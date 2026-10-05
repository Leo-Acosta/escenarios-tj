"""Juegos bimatriciales 2x2 definidos por el analista."""
import json
import math
import sqlite3
from contextlib import closing
from datetime import datetime, timezone


def validate(payload):
    def text(value):
        if not isinstance(value,str) or not 1<=len(value.strip())<=100:raise ValueError('Texto inválido.')
        return value.strip()
    model={'title':text(payload['title']), 'actors':[text(v) for v in payload['actors']],
           'strategies':[[text(v) for v in row] for row in payload['strategies']]}
    if len(model['actors'])!=2 or model['actors'][0]==model['actors'][1] or len(model['strategies'])!=2 or any(len(row)!=2 or row[0]==row[1] for row in model['strategies']):raise ValueError('Se necesitan dos actores y dos estrategias distintas por actor.')
    for key in ('a','b'):
        matrix=payload[key]
        if not isinstance(matrix,list) or len(matrix)!=2 or any(not isinstance(row,list) or len(row)!=2 for row in matrix):raise ValueError('Matriz inválida.')
        model[key]=[]
        for row in matrix:
            if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1000000 for v in row):raise ValueError('Pagos inválidos.')
            model[key].append(list(row))
    for key in ('p','q'):
        value=payload[key]
        if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1:raise ValueError('Probabilidad inválida.')
        model[key]=value
    return model


def analyze_case(payload):
    m=validate(payload);a,b=m['a'],m['b'];p,q=m['p'],m['q']
    pure=[[i,j] for i in range(2) for j in range(2) if a[i][j]>=max(a[r][j] for r in range(2)) and b[i][j]>=max(b[i][s] for s in range(2))]
    da=a[0][0]-a[0][1]-a[1][0]+a[1][1];db=b[0][0]-b[0][1]-b[1][0]+b[1][1]
    mixed=None
    if abs(da)>1e-12 and abs(db)>1e-12:
        qm=(a[1][1]-a[0][1])/da;pm=(b[1][1]-b[1][0])/db
        if 0<pm<1 and 0<qm<1:mixed={'p':pm,'q':qm}
    va=[row[0]*q+row[1]*(1-q) for row in a]
    vb=[p*b[0][j]+(1-p)*b[1][j] for j in range(2)]
    best=[i for i,v in enumerate(va) if math.isclose(v,max(va),rel_tol=1e-12,abs_tol=1e-9)]
    scenarios=[]
    for name,qq in [('Base',q),('Menor presencia de la primera estrategia de B',max(0,q-.2)),('Mayor presencia de la primera estrategia de B',min(1,q+.2))]:
        scenarios.append({'name':name,'q':qq,'values':[row[0]*qq+row[1]*(1-qq) for row in a]})
    intercept=a[0][1]-a[1][1]
    slope=(a[0][0]-a[0][1])-(a[1][0]-a[1][1])
    threshold=None
    if slope!=0:
        candidate=-intercept/slope
        if 0<=candidate<=1:threshold=candidate
    sensitivity={'threshold':threshold,'always_tied':slope==0 and intercept==0,'points':[]}
    for k in range(101):
        qq=k/100
        values=[row[0]*qq+row[1]*(1-qq) for row in a]
        sensitivity['points'].append({'q':qq,'values':values,'best':[i for i,v in enumerate(values) if math.isclose(v,max(values),rel_tol=1e-12,abs_tol=1e-9)]})
    return {'model':m,'pure':pure,'mixed':mixed,'values_a':va,'values_b':vb,'best_a':best,'scenarios':scenarios,
            'sensitivity':sensitivity,
            'limitations':['Pagos y probabilidades definidos por el analista; no calibrados con datos.',
                            'Juego simultáneo de dos actores y dos estrategias. No es un juego secuencial.',
                            'En juegos degenerados puede haber familias de equilibrios mixtos; no se enumeran aquí.']}


def save_case(path,result):
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db,db:
        db.execute('CREATE TABLE IF NOT EXISTS cases (id INTEGER PRIMARY KEY,created_at TEXT,payload TEXT)')
        return db.execute('INSERT INTO cases(created_at,payload) VALUES (?,?)',(datetime.now(timezone.utc).isoformat(),json.dumps(result,ensure_ascii=False,allow_nan=False))).lastrowid


def list_cases(path):
    if not path.exists():return []
    with closing(sqlite3.connect(path)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS cases (id INTEGER PRIMARY KEY,created_at TEXT,payload TEXT)')
        return [{'id':r[0],'created_at':r[1],'result':json.loads(r[2])} for r in db.execute('SELECT id,created_at,payload FROM cases ORDER BY id DESC LIMIT 20')]
