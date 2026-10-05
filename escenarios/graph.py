"""Validación y persistencia de redes creadas por el analista."""
import json
import sqlite3
from contextlib import closing


def validate_graph(payload):
    nodes, edges = payload['nodes'], payload['edges']
    if not isinstance(nodes,list) or not isinstance(edges,list) or not 1 <= len(nodes) <= 200 or len(edges)>1000:
        raise ValueError('Se permiten de 1 a 200 nodos y hasta 1000 relaciones.')
    clean=[]
    for index,node in enumerate(nodes):
        if not isinstance(node,dict) or not isinstance(node.get('name'),str):raise ValueError('Nombre inválido.')
        name=node['name'].strip()
        if not 1<=len(name)<=80 or node['type'] not in (0,1,2) or node['id'] != index:
            raise ValueError('Nombre, tipo o identificador inválido.')
        clean.append(dict(id=index,name=name,type=node['type']))
    links=[]
    for index,edge in enumerate(edges):
        if not isinstance(edge,dict):raise ValueError('Relación inválida.')
        if type(edge['a']) is not int or type(edge['b']) is not int or not 0<=edge['a']<len(clean) or not 0<=edge['b']<len(clean) or edge['a']==edge['b'] or edge['type'] not in ('Influencia','Cooperación','Participación'):
            raise ValueError('Relación inválida.')
        links.append(dict(id=index,a=edge['a'],b=edge['b'],type=edge['type']))
    return dict(nodes=clean,edges=links)


def save_graph(path,payload):
    clean=validate_graph(payload)
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path)) as db,db:
        db.execute('CREATE TABLE IF NOT EXISTS graph (id INTEGER PRIMARY KEY,payload TEXT NOT NULL)')
        db.execute('INSERT OR REPLACE INTO graph VALUES (1,?)',(json.dumps(clean,ensure_ascii=False),))
    return clean


def load_graph(path):
    if not path.exists():return None
    with closing(sqlite3.connect(path)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS graph (id INTEGER PRIMARY KEY,payload TEXT NOT NULL)')
        row=db.execute('SELECT payload FROM graph WHERE id=1').fetchone()
        return json.loads(row[0]) if row else None
