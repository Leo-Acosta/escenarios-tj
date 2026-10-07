"""Agentes con políticas explícitas y memoria de rondas terminadas."""
import json
import math
import random
import sqlite3
from contextlib import closing
from uuid import uuid4
from copy import deepcopy
from .case_model import validate
from .workflow import now

POLICIES={'fixed0':'Siempre alternativa 1','fixed1':'Siempre alternativa 2',
          'mirror':'Copiar última alternativa rival','trigger':'Cambiar tras la primera alternativa 2 rival',
          'adaptive':'Mejor respuesta a frecuencias observadas','random':'Aleatorio 50 / 50'}


def choose(policy,actor,model,history,rng):
    opponent=[row['actions'][1-actor] for row in history]
    if policy=='fixed0':return 0,'Política fija: alternativa 1.'
    if policy=='fixed1':return 1,'Política fija: alternativa 2.'
    if policy=='mirror':return (opponent[-1] if opponent else 0),'Copia la alternativa rival de la ronda anterior; inicia con 1.'
    if policy=='trigger':return (1 if 1 in opponent else 0),'Usa alternativa 2 si el rival la usó alguna vez; inicia con 1.'
    if policy=='random':return rng.randrange(2),'Sorteo independiente 50 / 50.'
    frequency=(opponent.count(0)+1)/(len(opponent)+2)
    if actor==0:values=[row[0]*frequency+row[1]*(1-frequency) for row in model['a']]
    else:values=[model['b'][0][j]*frequency+model['b'][1][j]*(1-frequency) for j in range(2)]
    return (0 if values[0]>=values[1] else 1),f'Mejor respuesta a frecuencia rival de alternativa 1: {frequency:.4f}; prior 1/1. Empates: alternativa 1.'


def run(payload,*,decision_provider=None,execution_seed=None):
    if not isinstance(payload,dict):raise ValueError('Configuración inválida.')
    model=validate(payload['model']);options=payload['options']
    if not isinstance(options,dict):raise ValueError('Configuración inválida.')
    n=options.get('rounds');seed=options.get('seed');noise=options.get('noise');policies=options.get('policies')
    if type(n) is not int or not 1<=n<=500:raise ValueError('Usá entre 1 y 500 rondas.')
    if type(seed) is not int or not 0<=seed<=4294967295:raise ValueError('Semilla entera válida requerida.')
    if execution_seed is not None and (type(execution_seed) is not int or not 0<=execution_seed<=4294967295):raise ValueError('Semilla de ejecución inválida.')
    if type(noise) not in (int,float) or not math.isfinite(noise) or not 0<=noise<=1:raise ValueError('Error de ejecución entre 0 y 1.')
    allowed=set(POLICIES)|({'local_ai'} if decision_provider is not None else set())
    if not isinstance(policies,list) or len(policies)!=2 or any(p not in allowed for p in policies):raise ValueError('Elegí una política válida para cada actor.')
    rationale=payload.get('assumptions')
    if not isinstance(rationale,str) or not rationale.strip() or len(rationale)>6000:raise ValueError('Registrá el fundamento de las políticas y supuestos.')
    rng=[random.Random(seed*2),random.Random(seed*2+1)];rounds=[];totals=[0,0];counts=[[0,0],[0,0]]
    execution_rng=([random.Random(execution_seed*2+i+8589934592) for i in range(2)] if execution_seed is not None else rng)
    for index in range(n):
        decisions=[decision_provider(i,deepcopy(model),deepcopy(rounds)) if policies[i]=='local_ai' else choose(policies[i],i,model,rounds,rng[i]) for i in range(2)]
        if any(not isinstance(d,(tuple,list)) or len(d)!=2 or type(d[0]) is not int or d[0] not in (0,1) or not isinstance(d[1],str) or not d[1].strip() for d in decisions):raise ValueError('El agente devolvió una decisión incompatible; corrida rechazada.')
        intended=[d[0] for d in decisions]
        actual=[1-intended[i] if noise and execution_rng[i].random()<noise else intended[i] for i in range(2)]
        a,b=actual;payments=[model['a'][a][b],model['b'][a][b]]
        memory=[{'observed_rounds':len(rounds),'opponent_counts':list(counts[1-i])} for i in range(2)]
        totals=[totals[i]+payments[i] for i in range(2)]
        rounds.append({'round':index+1,'intended':intended,'actions':actual,'payments':payments,'totals':list(totals),'memory':memory,'reasons':[d[1] for d in decisions]})
        for i in range(2):counts[i][actual[i]]+=1
    result={'id':None,'created_at':now(),'engine':'repeated-agents-v1','model':model,
        'options':{'rounds':n,'seed':seed,'noise':noise,'policies':policies},'assumptions':rationale.strip(),
        'rounds':rounds,'totals':totals,'means':[v/n for v in totals],'action_counts':counts,
        'limits':['Decisiones simultáneas: cada agente usa solo rondas ya terminadas.',
            'Los pagos y políticas son supuestos del analista; no hay aprendizaje validado con datos.',
            'Copiar y activar cambio usan índices de alternativas, no interpretan el significado de sus nombres.',
            'Error de ejecución independiente por actor y ronda: invierte su alternativa. Se observa la acción ejecutada.',
            'La política adaptativa usa frecuencias con prior 1/1 y elige alternativa 1 en empates.',
            'Memoria reiniciada en cada corrida. No se usan LLM ni herramientas externas para decidir.',
            'p y q del caso base no se usan: las conductas las generan las políticas. Sin descuento temporal.']}
    if decision_provider is not None:
        result['engine']='repeated-local-ai-v1'
        result['limits']=[s for s in result['limits'] if 'No se usan LLM' not in s]
        result['limits'].append('IA local elige una alternativa permitida; no acredita optimalidad ni predicción real.')
    if execution_seed is not None:
        result['options']['execution_seed']=execution_seed
        if decision_provider is None:result['engine']='repeated-paired-noise-v1'
        result['limits'].append('Perturbaciones de ejecución en flujo separado de las decisiones, con semilla conservada.')
    return result


def connection(path):
    path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS agent_runs (id TEXT PRIMARY KEY, payload TEXT)');db.commit();return db


def save(path,result):
    record={**result,'id':str(uuid4())}
    with closing(connection(path)) as db,db:db.execute('INSERT INTO agent_runs VALUES (?,?)',(record['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record


def history(path):
    with closing(connection(path)) as db:return [json.loads(row[0]) for row in db.execute('SELECT payload FROM agent_runs ORDER BY rowid DESC LIMIT 20')]


def get_run(path,identity):
    with closing(connection(path)) as db:
        row=db.execute('SELECT payload FROM agent_runs WHERE id=?',(identity,)).fetchone()
    if row is None:raise KeyError('Corrida inexistente.')
    return json.loads(row[0])


def build_csv(record):
    import csv
    from io import StringIO
    out=StringIO(newline='');writer=csv.writer(out,delimiter=';')
    writer.writerow(['version','motor','caso','semilla','error_ejecucion','ronda','actor','politica','intencion_indice','intencion','accion_indice','accion','pago','acumulado','rondas_observadas','rival_alternativa_1','rival_alternativa_2','motivo'])
    def cell(value):
        if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')):return "'"+value
        return value
    for row in record['rounds']:
        for i in range(2):
            memory=row['memory'][i];m=record['model'];o=record['options']
            cells=[record['id'],record['engine'],m['title'],o['seed'],o['noise'],row['round'],m['actors'][i],o['policies'][i],
                row['intended'][i]+1,m['strategies'][i][row['intended'][i]],row['actions'][i]+1,m['strategies'][i][row['actions'][i]],
                row['payments'][i],row['totals'][i],memory['observed_rounds'],*memory['opponent_counts'],row['reasons'][i]]
            writer.writerow([cell(v) for v in cells])
    return out.getvalue().encode('utf-8-sig')
