"""Juego de información perfecta: A decide, B observa y responde."""
import json
import math
import sqlite3
from contextlib import closing
from uuid import uuid4
from .workflow import now


def analyze(value):
    if not isinstance(value,dict):raise ValueError('Modelo inválido.')
    def label(v):
        if not isinstance(v,str) or not v.strip() or len(v)>100:raise ValueError('Completá nombres de hasta 100 caracteres.')
        return v.strip()
    title=label(value.get('title'))
    actors=value.get('actors');actions=value.get('actions');payoffs=value.get('payoffs')
    if not isinstance(actors,list) or len(actors)!=2:raise ValueError('Se requieren dos actores.')
    actors=[label(x) for x in actors]
    if not isinstance(actions,list) or len(actions)!=3 or any(not isinstance(r,list) or len(r)!=2 for r in actions):raise ValueError('Definí dos decisiones por nodo.')
    actions=[[label(x) for x in r] for r in actions]
    if any(r[0]==r[1] for r in actions):raise ValueError('Las alternativas de cada nodo deben ser distintas.')
    if not isinstance(payoffs,list) or len(payoffs)!=2 or any(not isinstance(r,list) or len(r)!=2 for r in payoffs):raise ValueError('Se requieren cuatro resultados.')
    for row in payoffs:
        for pair in row:
            if not isinstance(pair,list) or len(pair)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>1e6 for x in pair):raise ValueError('Ingresá pagos finitos entre -1000000 y 1000000.')
    assumptions=value.get('assumptions')
    if not isinstance(assumptions,str) or not assumptions.strip() or len(assumptions)>6000:raise ValueError('Registrá los supuestos y fundamento de los pagos.')
    # Todas las respuestas óptimas, incluidos empates y planes fuera de la ruta.
    responses=[]
    for row in payoffs:
        best=max(p[1] for p in row)
        responses.append([j for j,p in enumerate(row) if p[1]==best])
    equilibria=[]
    for left in responses[0]:
        for right in responses[1]:
            plan=[left,right];utilities=[payoffs[i][plan[i]][0] for i in range(2)]
            for first in range(2):
                if utilities[first]==max(utilities):
                    equilibria.append({'first':first,'responses':plan,'outcome':[first,plan[first]],'payoffs':payoffs[first][plan[first]]})
    return {'model':{'title':title,'actors':actors,'actions':actions,'payoffs':payoffs,'assumptions':assumptions.strip()},
        'responses':responses,'equilibria':equilibria,'method':'Inducción hacia atrás',
        'limits':['Información perfecta: B observa la decisión de A.','Pagos hipotéticos aportados por el analista; sin calibración predictiva.','Dos etapas, dos actores y dos alternativas por nodo. Sin azar ni información oculta.'], 'calculated_at':now()}


def connect(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS sequential_versions (id TEXT PRIMARY KEY, payload TEXT)');db.commit()
    return db


def save(path,result):
    record={**result,'id':str(uuid4())}
    with closing(connect(path)) as db,db:
        db.execute('INSERT INTO sequential_versions VALUES (?,?)',(record['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record


def history(path):
    with closing(connect(path)) as db:
        return [json.loads(row[0]) for row in db.execute('SELECT payload FROM sequential_versions ORDER BY rowid DESC LIMIT 30')]
