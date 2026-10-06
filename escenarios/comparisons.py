"""Comparación de políticas con un conjunto común de semillas."""
import json
import sqlite3
from contextlib import closing
from uuid import uuid4
from statistics import fmean,pstdev
from . import agents
from .case_model import validate
from .workflow import now


def compare(payload):
    if not isinstance(payload,dict):raise ValueError('Configuración inválida.')
    model=validate(payload['model']);options=payload['options']
    if not isinstance(options,dict):raise ValueError('Configuración inválida.')
    n=options.get('rounds');repetitions=options.get('repetitions');seed=options.get('seed');noise=options.get('noise')
    if type(n) is not int or not 1<=n<=100 or type(repetitions) is not int or not 1<=repetitions<=10:raise ValueError('Usá 1–100 rondas y 1–10 repeticiones por combinación.')
    if type(seed) is not int or not 0<=seed<=4294967295-repetitions+1:raise ValueError('La semilla y sus repeticiones deben estar dentro del rango permitido.')
    seeds=list(range(seed,seed+repetitions));policies=list(agents.POLICIES);cells=[]
    for i,a in enumerate(policies):
        for j,b in enumerate(policies):
            trials=[]
            for current in seeds:
                result=agents.run({'model':model,'options':{'rounds':n,'seed':current,'noise':noise,'policies':[a,b]},'assumptions':payload.get('assumptions')})
                trials.append(result['means'])
            cells.append({'i':i,'j':j,'policies':[a,b],'trial_means':trials,
                'statistics':[{'mean':fmean(t[k] for t in trials),'std':pstdev(t[k] for t in trials),
                    'min':min(t[k] for t in trials),'max':max(t[k] for t in trials)} for k in range(2)]})
    return {'id':None,'created_at':now(),'engine':'policy-comparison-v1','agents_engine':'repeated-agents-v1',
        'model':model,'options':{'rounds':n,'repetitions':repetitions,'seed':seed,'noise':noise},'seeds':seeds,
        'policies':policies,'cells':cells,'assumptions':payload['assumptions'].strip(),
        'limits':['Cada combinación utiliza las mismas semillas; la memoria se reinicia en cada repetición.',
            'Las celdas muestran utilidad media por ronda y dispersión entre semillas, por actor.',
            'A y B tienen escalas propias: no se comparan sus pagos entre sí.',
            'La desviación es poblacional sobre las semillas ensayadas; no es un intervalo de confianza.',
            'Una repetición solo produce dispersión cero por construcción, no demuestra robustez.',
            'No se estima qué política utilizará un rival real. Resultados condicionados al modelo y conductas elegidas.']}


def connection(path):
    path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS agent_comparisons (id TEXT PRIMARY KEY,payload TEXT)');db.commit();return db


def save(path,result):
    record={**result,'id':str(uuid4())}
    with closing(connection(path)) as db,db:db.execute('INSERT INTO agent_comparisons VALUES (?,?)',(record['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record


def history(path):
    with closing(connection(path)) as db:return [json.loads(row[0]) for row in db.execute('SELECT payload FROM agent_comparisons ORDER BY rowid DESC LIMIT 20')]


def get_record(path, identity):
    with closing(connection(path)) as db:
        row=db.execute('SELECT payload FROM agent_comparisons WHERE id=?',(identity,)).fetchone()
    if row is None:raise KeyError('Comparación inexistente.')
    return json.loads(row[0])


def replay(path,payload):
    with closing(connection(path)) as db:row=db.execute('SELECT payload FROM agent_comparisons WHERE id=?',(payload['id'],)).fetchone()
    if row is None:raise KeyError('Comparación inexistente.')
    record=json.loads(row[0]);i=payload.get('i');j=payload.get('j');trial=payload.get('trial')
    if any(type(v) is not int for v in (i,j,trial)) or not 0<=i<len(record['policies']) or not 0<=j<len(record['policies']) or not 0<=trial<len(record['seeds']):raise ValueError('Combinación o repetición inválida.')
    if record['agents_engine']!='repeated-agents-v1':raise ValueError('La versión de motor requiere revisión antes de reproducir.')
    o=record['options']
    result=agents.run({'model':record['model'],'options':{'rounds':o['rounds'],'noise':o['noise'],'seed':record['seeds'][trial],
        'policies':[record['policies'][i],record['policies'][j]]},'assumptions':record['assumptions']})
    result['comparison_source']={'id':record['id'],'i':i,'j':j,'trial':trial}
    return result
