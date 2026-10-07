"""Registro prospectivo y evaluación pareada binaria. No fabrica observaciones."""
import hashlib
import json
import math
import random
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from uuid import uuid4
from .workflow import now


def connect(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS prediction_events (id TEXT PRIMARY KEY, payload TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS prediction_evaluations (id TEXT PRIMARY KEY, payload TEXT)')
    db.commit();return db


def probability(v):
    if type(v) not in (float,int) or not math.isfinite(v) or not 0<=v<=1:raise ValueError('Probabilidad finita entre 0 y 1 requerida.')
    return v


def text(v,limit):
    if not isinstance(v,str) or not v.strip() or len(v)>limit:raise ValueError('Texto de contexto o procedencia requerido.')
    return v.strip()


def forecast(path,payload):
    if not isinstance(payload,dict):raise ValueError('Pronóstico inválido.')
    identity=text(payload.get('event'),100);deadline=text(payload.get('deadline'),60)
    try:date=datetime.fromisoformat(deadline)
    except ValueError:raise ValueError('Plazo ISO con zona horaria requerido.') from None
    if date.tzinfo is None or date<=datetime.now(timezone.utc):raise ValueError('El plazo debe ser futuro y tener zona horaria.')
    value={'event':identity,'target':text(payload.get('target'),1000),'deadline':deadline,
        'candidate_probability':probability(payload.get('candidate_probability')),
        'baseline_probability':probability(payload.get('baseline_probability')),
        'candidate_ref':text(payload.get('candidate_ref'),500),'baseline_ref':text(payload.get('baseline_ref'),500),
        'created_at':now(),'observation':None}
    with closing(connect(path)) as db,db:
        try:db.execute('INSERT INTO prediction_events VALUES (?,?)',(identity,json.dumps(value,ensure_ascii=False,allow_nan=False)))
        except sqlite3.IntegrityError:raise ValueError('El evento ya fue registrado; los pronósticos no se sobrescriben.') from None
    return value


def observe(path,payload):
    if not isinstance(payload,dict) or type(payload.get('outcome')) is not int or payload['outcome'] not in (0,1):raise ValueError('Resultado observado binario 0 o 1 requerido.')
    source=text(payload.get('source'),2000)
    with closing(connect(path)) as db,db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT payload FROM prediction_events WHERE id=?',(payload.get('event'),)).fetchone()
        if not row:raise ValueError('Registrá el pronóstico antes de observar el resultado.')
        record=json.loads(row[0])
        if record.get('research'):raise ValueError('Usá el protocolo para observar este evento reservado.')
        if record['observation'] is not None:raise ValueError('El resultado ya está conservado; no se sobrescribe.')
        if datetime.fromisoformat(record['deadline'])>datetime.now(timezone.utc):raise ValueError('Esperá al plazo predefinido para registrar la observación.')
        record['observation']={'outcome':payload['outcome'],'source':source,'recorded_at':now(),'verification':'analyst_supplied'}
        db.execute('UPDATE prediction_events SET payload=? WHERE id=?',(json.dumps(record,ensure_ascii=False,allow_nan=False),record['event']))
    return record


def history(path):
    with closing(connect(path)) as db:return [v for r in db.execute('SELECT payload FROM prediction_events ORDER BY rowid DESC') if not (v:=json.loads(r[0])).get('research')][:200]


def evaluate_rows(rows,seed=42):
    if type(seed) is not int or not 0<=seed<=4294967295:raise ValueError('Semilla entera válida requerida.')
    pairs=[]
    for r in rows:
        if r['observation'] is None:continue
        y=r['observation']['outcome']
        if type(y) is not int or y not in (0,1):raise ValueError('Observación binaria inválida.')
        a=probability(r['candidate_probability']);b=probability(r['baseline_probability'])
        pairs.append(((a-y)**2,(b-y)**2))
    if not pairs:raise ValueError('No hay resultados observados. No puede demostrarse mejora sin datos.')
    n=len(pairs);candidate=sum(a for a,b in pairs)/n;baseline=sum(b for a,b in pairs)/n
    differences=[a-b for a,b in pairs];rng=random.Random(seed)
    samples=sorted(sum(rng.choice(differences) for _ in range(n))/n for _ in range(1000))
    interval=[samples[24],samples[974]]
    return {'metric':'brier-binary-v1','n':n,'candidate_brier':candidate,'baseline_brier':baseline,
        'delta':candidate-baseline,'paired_bootstrap_95':interval,'seed':seed,'resamples':1000,
        'evidence':'provisional_improvement' if n>=30 and interval[1]<0 else 'insufficient_evidence',
        'limits':['Menor Brier es mejor; se comparan pronósticos del mismo evento.',
            'Observaciones aportadas por el analista; el sistema no acredita autenticidad ni ausencia de filtración previa.',
            'Intervalo bootstrap aproximado bajo independencia de eventos; series correlacionadas requieren otro diseño.',
            'Treinta eventos es un mínimo operativo, no un cálculo de potencia ni garantía de generalización.',
            'Una mejora provisional no autoriza promoción automática ni garantiza predicciones futuras.']}


def evaluate(path,payload):
    if not isinstance(payload,dict):raise ValueError('Configuración de evaluación inválida.')
    candidate=text(payload.get('candidate_ref'),500);baseline=text(payload.get('baseline_ref'),500)
    with closing(connect(path)) as db,db:
        rows=sorted([json.loads(r[0]) for r in db.execute('SELECT payload FROM prediction_events')],key=lambda r:r['event'])
        rows=[r for r in rows if not r.get('research') and r['candidate_ref']==candidate and r['baseline_ref']==baseline and r['observation'] is not None]
        if len(rows)>2000:raise ValueError('Máximo 2000 observaciones por evaluación.')
        result=evaluate_rows(rows,payload.get('seed',42))
        dataset=json.dumps(rows,sort_keys=True,ensure_ascii=False,allow_nan=False)
        record={**result,'id':str(uuid4()),'created_at':now(),'candidate_ref':candidate,'baseline_ref':baseline,
            'dataset_sha256':hashlib.sha256(dataset.encode()).hexdigest(),'dataset':rows,
            'optimizer_action':'collect_more_or_review_design' if result['evidence']=='insufficient_evidence' else 'independent_validation_required'}
        db.execute('INSERT INTO prediction_evaluations VALUES (?,?)',(record['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record


def evaluations(path):
    with closing(connect(path)) as db:
        return [{k:v for k,v in json.loads(r[0]).items() if k!='dataset'} for r in db.execute('SELECT payload FROM prediction_evaluations ORDER BY rowid DESC LIMIT 10')]


def replay(path,identity):
    with closing(connect(path)) as db:
        row=db.execute('SELECT payload FROM prediction_evaluations WHERE id=?',(identity,)).fetchone()
    if not row:raise ValueError('Evaluación desconocida.')
    saved=json.loads(row[0])
    digest=hashlib.sha256(json.dumps(saved['dataset'],sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    if digest!=saved['dataset_sha256']:raise ValueError('El conjunto conservado no coincide con su huella.')
    result=evaluate_rows(saved['dataset'],saved['seed'])
    if any(saved[k]!=v for k,v in result.items()):raise ValueError('La evaluación no se reproduce con esta versión.')
    return {'id':identity,'reproduced':True,'dataset_sha256':digest,'result':result}
