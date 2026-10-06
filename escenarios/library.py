"""Consulta unificada de versiones locales sin modificar los modelos."""
import json
import sqlite3
from contextlib import closing

TABLES={'case':'cases','workflow':'workflow_versions','tree':'sequential_versions',
        'agents':'agent_runs','comparison':'agent_comparisons','sweep':'payoff_sweeps'}
LABELS={'case':'Matriz libre','workflow':'Versión de expediente','tree':'Árbol secuencial',
        'agents':'Corrida de agentes','comparison':'Comparación de políticas','sweep':'Exploración de incentivos'}

def rows(path):
    if not path.exists():return []
    output=[]
    with closing(sqlite3.connect(path)) as db:
        available={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for kind,table in TABLES.items():
            if table not in available:continue
            columns='workflow_id,version,created_at,payload' if kind=='workflow' else ('id,created_at,payload' if kind=='case' else 'id,payload')
            for row in db.execute(f'SELECT {columns} FROM {table}'):
                record=json.loads(row[-1]);identity=f'{row[0]}:{row[1]}' if kind=='workflow' else str(row[0])
                date=row[2] if kind=='workflow' else row[1] if kind=='case' else record.get('created_at',record.get('calculated_at',''))
                m=record['model'];output.append({'type':kind,'label':LABELS[kind],'id':identity,'title':m['title'],
                    'actors':m['actors'],'created_at':date,'record':record})
    return output

def search(path,query='',kind='',offset=0):
    if kind and kind not in TABLES:raise ValueError('Tipo de análisis inválido.')
    if type(offset) is not int or offset<0:raise ValueError('Página inválida.')
    if not isinstance(query,str) or len(query)>200:raise ValueError('Búsqueda inválida.')
    query=query.strip().casefold()
    found=[r for r in rows(path) if (not kind or r['type']==kind) and
           (not query or query in ' '.join([r['title'],*r['actors'],r['id'],r['label']]).casefold())]
    found.sort(key=lambda r:(r['created_at'],r['type'],r['id']),reverse=True)
    return {'total':len(found),'offset':offset,'items':[{k:v for k,v in r.items() if k!='record'} for r in found[offset:offset+30]]}

def get_record(path,kind,identity):
    if kind not in TABLES:raise ValueError('Tipo de análisis inválido.')
    for row in rows(path):
        if row['type']==kind and row['id']==identity:return row
    raise KeyError('Versión inexistente.')
