"""Diccionarios congelados de variables; no cambian pagos ni probabilidades."""
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4
from .workflow import get_version, get_workflow, now, text
from .case_model import analyze_case
from .decision_agents import fingerprint

TARGETS={'context','p','q',*[f'{a}.{i}.{j}' for a in ('a','b') for i in range(2) for j in range(2)]}


def validate(items,model):
    if not isinstance(items,list) or not 1<=len(items)<=100:
        raise ValueError('Definí entre una y cien variables.')
    clean=[];names=set();bound=set()
    for item in items:
        if not isinstance(item,dict):raise ValueError('Variable inválida.')
        name=text(item.get('name'),100)
        if name.casefold() in names:raise ValueError('Nombre de variable duplicado.')
        names.add(name.casefold())
        kind=item.get('type');value=item.get('value');target=item.get('target')
        if not isinstance(kind,str) or kind not in ('number','category','boolean'):raise ValueError('Tipo de variable inválido.')
        if not isinstance(target,str) or target not in TARGETS:raise ValueError('Vínculo con el modelo inválido.')
        numeric=kind=='number'
        if numeric and (type(value) not in (int,float) or not math.isfinite(value)):
            raise ValueError('Valor numérico finito requerido.')
        if kind=='category':value=text(value,200)
        if kind=='boolean' and type(value) is not bool:raise ValueError('Valor booleano requerido.')
        bounds=item.get('interval')
        if bounds is not None:
            if not numeric or not isinstance(bounds,list) or len(bounds)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in bounds) or not bounds[0]<=value<=bounds[1]:
                raise ValueError('Intervalo inválido o sin contener el valor.')
        if target!='context':
            if not numeric or target in bound:raise ValueError('Vínculo numérico único requerido.')
            bound.add(target)
            expected=model[target] if target in ('p','q') else model[target[0]][int(target[2])][int(target[4])]
            if value!=expected:raise ValueError('La variable no coincide con el valor congelado del modelo.')
            if target in ('p','q') and bounds and not 0<=bounds[0]<=bounds[1]<=1:
                raise ValueError('Intervalo de probabilidad fuera de 0–1.')
        evidence=item.get('evidence')
        if evidence not in ('synthetic','assumed','documented_declared','pending'):
            raise ValueError('Clasificá la evidencia de la variable.')
        unit=text(item.get('unit'),80)
        if target in ('p','q') and unit not in ('proporción','1'):
            raise ValueError('p/q se expresan en proporción (0–1), no en porcentajes.')
        clean.append({'name':name,'type':kind,'value':value,'unit':unit,
                      'source':text(item.get('source'),1000),'uncertainty':text(item.get('uncertainty'),1000),
                      'interval':bounds,'target':target,'evidence':evidence})
    return clean


def connect(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS variable_versions (id TEXT PRIMARY KEY,workflow_id TEXT,payload TEXT)')
    db.commit();return db


def save(path,payload):
    if payload.get('reviewed') is not True:raise ValueError('Revisá las variables antes de conservar.')
    version=payload.get('version')
    if type(version) is not int or version<1:raise ValueError('Versión calculada requerida.')
    matrix=get_version(path,payload.get('workflow_id'),version)
    body={'engine':'variables-v1','workflow':{'id':payload['workflow_id'],'version':version},
          'matrix':matrix,'variables':validate(payload.get('variables'),matrix['model']),
          'limits':['Las unidades y fuentes son declaradas; no se autentican ni convierten automáticamente.',
                    'Los intervalos son supuestos explícitos, no distribuciones ni confianza estadística.',
                    'Este diccionario describe una matriz congelada; no modifica pagos ni ejecuta inferencia.']}
    record={'id':str(uuid4()),'created_at':now(),'payload':body,'sha256':fingerprint(body)}
    verify(record)
    with closing(connect(path)) as db,db:
        db.execute('INSERT INTO variable_versions VALUES (?,?,?)',(record['id'],payload['workflow_id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record


def read(path,identity):
    with closing(connect(path)) as db:
        row=db.execute('SELECT payload FROM variable_versions WHERE id=?',(identity,)).fetchone()
    if not row:raise ValueError('Diccionario desconocido.')
    record=json.loads(row[0]);verify(record)
    return record


def verify(record):
    body=record['payload'];matrix=body['matrix'];scope=body['workflow']
    if body['engine']!='variables-v1' or record['sha256']!=fingerprint(body):raise ValueError('Diccionario alterado.')
    if matrix['context']['workflow_id']!=scope['id'] or matrix['context']['version']!=scope['version']:
        raise ValueError('Diccionario y matriz de versiones distintas.')
    if validate(body['variables'],matrix['model'])!=body['variables']:raise ValueError('Variables no normalizadas.')
    fresh=analyze_case(matrix['model'])
    if any(fresh[k]!=matrix[k] for k in fresh):raise ValueError('Los cálculos de matriz no se reproducen.')
    return {'id':record['id'],'sha256':record['sha256'],'reproduced':True,'new_inference':False}


def history(path,workflow_id,version=None):
    get_workflow(path,workflow_id)
    if version is not None:get_version(path,workflow_id,version)
    with closing(connect(path)) as db:
        query='SELECT payload FROM variable_versions WHERE workflow_id=?'
        args=[workflow_id]
        if version is not None:
            query+=" AND json_extract(payload,'$.payload.workflow.version')=?";args.append(version)
        rows=db.execute(query+' ORDER BY rowid DESC LIMIT 50',args)
        return [{'id':r['id'],'created_at':r['created_at'],'sha256':r['sha256'],
                 'version':r['payload']['workflow']['version'],'count':len(r['payload']['variables'])}
                for row in rows for r in [json.loads(row[0])]]
