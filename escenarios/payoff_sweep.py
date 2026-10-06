"""Barrido determinista de un pago, conservando los demás supuestos."""
import copy
import math
import json
import sqlite3
import csv
from io import StringIO
from contextlib import closing
from uuid import uuid4
from .workflow import now
from .case_model import validate, analyze_case

def run(payload):
    model=validate(payload['model']);o=payload['options']
    key=o.get('actor');i=o.get('row');j=o.get('column');lo=o.get('minimum');hi=o.get('maximum')
    if key not in ('a','b') or type(i) is not int or type(j) is not int or i not in (0,1) or j not in (0,1):
        raise ValueError('Seleccioná un pago válido.')
    if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1000000 for v in (lo,hi)) or lo>=hi:
        raise ValueError('El rango debe ser finito y creciente, dentro de ±1.000.000.')
    points=[];changes=[];previous=None
    for index in range(101):
        value=lo+(hi-lo)*index/100;candidate=copy.deepcopy(model);candidate[key][i][j]=value
        r=analyze_case(candidate)
        best_b=[k for k,v in enumerate(r['values_b']) if math.isclose(v,max(r['values_b']),rel_tol=1e-12,abs_tol=1e-9)]
        point={'value':value,'pure':r['pure'],'mixed':r['mixed'],'best_a':r['best_a'],'best_b':best_b,'values_a':r['values_a'],'values_b':r['values_b']}
        signature=(r['pure'],r['best_a'],best_b,r['mixed'] is not None)
        if previous is not None and signature!=previous:
            changes.append({'from':points[-1]['value'],'to':value,'index':index})
        previous=signature;points.append(point)
    assumptions=payload.get('assumptions','Exploración hipotética sin fundamento adicional registrado.')
    if not isinstance(assumptions,str) or not 1<=len(assumptions.strip())<=10000:raise ValueError('Registrá supuestos de hasta 10.000 caracteres.')
    return {'id':None,'created_at':now(),'engine':'payoff-sweep-v1','assumptions':assumptions.strip(),'model':model,'options':{'actor':key,'row':i,'column':j,'minimum':lo,'maximum':hi},'points':points,'changes':changes,
            'limits':['Se varía un único pago; los demás pagos y p/q permanecen constantes.',
                      'Los cambios se localizan entre muestras consecutivas: no son umbrales exactos y pueden existir cambios dentro del intervalo.',
                      'Los equilibrios son soluciones del modelo; p/q son supuestos del analista, no probabilidades pronosticadas.',
                      'No se enumeran familias de equilibrios mixtos degenerados.']}


def connection(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS payoff_sweeps (id TEXT PRIMARY KEY,payload TEXT)');db.commit()
    return db


def save(path,result):
    record={**result,'id':str(uuid4())}
    with closing(connection(path)) as db,db:
        db.execute('INSERT INTO payoff_sweeps VALUES (?,?)',(record['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record


def history(path):
    with closing(connection(path)) as db:
        return [json.loads(row[0]) for row in db.execute('SELECT payload FROM payoff_sweeps ORDER BY rowid DESC LIMIT 20')]


def get_record(path,identity):
    with closing(connection(path)) as db:row=db.execute('SELECT payload FROM payoff_sweeps WHERE id=?',(identity,)).fetchone()
    if row is None:raise KeyError('Exploración inexistente.')
    return json.loads(row[0])


def build_csv(r):
    out=StringIO();writer=csv.writer(out,delimiter=';');o=r['options']
    # Neutralize spreadsheet formulas only in text; preserve numeric negatives.
    def safe(value):
        return "'"+value if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')) else value
    writer.writerow(['version','motor','caso','supuestos','actor_pago','fila_A','columna_B','p','q','muestra','pago','utilidad_A1','utilidad_A2','utilidad_B1','utilidad_B2','mejor_A','mejor_B','equilibrios_puros','mixto_p','mixto_q'])
    for index,p in enumerate(r['points']):
        writer.writerow([safe(v) for v in [r['id'],r['engine'],r['model']['title'],r['assumptions'],o['actor'],o['row']+1,o['column']+1,r['model']['p'],r['model']['q'],index+1,p['value'],*p['values_a'],*p['values_b'],','.join(str(v+1) for v in p['best_a']),','.join(str(v+1) for v in p['best_b']),'; '.join(f'{i+1}/{j+1}' for i,j in p['pure']),p['mixed']['p'] if p['mixed'] else '',p['mixed']['q'] if p['mixed'] else '']])
    return out.getvalue().encode('utf-8-sig')
