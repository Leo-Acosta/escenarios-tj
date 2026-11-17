"""Validación y persistencia de redes creadas por el analista."""
import json
import sqlite3
from contextlib import closing


def validate_graph(payload):
    if not isinstance(payload,dict):raise ValueError('Red inválida.')
    if payload.get('schema') not in (None,2):raise ValueError('Versión de red no compatible.')
    if payload.get('schema')==2:
        from .visual_graph import validate
        return validate(payload)
    nodes, edges = payload['nodes'], payload['edges']
    if not isinstance(nodes,list) or not isinstance(edges,list) or not 1 <= len(nodes) <= 200 or len(edges)>1000:
        raise ValueError('Se permiten de 1 a 200 nodos y hasta 1000 relaciones.')
    clean=[]
    for index,node in enumerate(nodes):
        if not isinstance(node,dict) or not isinstance(node.get('name'),str):raise ValueError('Nombre inválido.')
        name=node['name'].strip()
        if not 1<=len(name)<=80 or type(node['type']) is not int or node['type'] not in (0,1,2) or type(node['id']) is not int or node['id'] != index:
            raise ValueError('Nombre, tipo o identificador inválido.')
        clean.append(dict(id=index,name=name,type=node['type']))
    links=[]
    for index,edge in enumerate(edges):
        if not isinstance(edge,dict):raise ValueError('Relación inválida.')
        if type(edge['a']) is not int or type(edge['b']) is not int or not 0<=edge['a']<len(clean) or not 0<=edge['b']<len(clean) or edge['a']==edge['b'] or edge['type'] not in ('Influencia','Cooperación','Participación'):
            raise ValueError('Relación inválida.')
        link=dict(id=index,a=edge['a'],b=edge['b'],type=edge['type'])
        if 'evidence' in edge:
            evidence=edge['evidence']
            if not isinstance(evidence,dict):raise ValueError('Evidencia inválida.')
            clean_evidence={}
            for key,limit in (('source',160),('reference',500),('note',1200)):
                value=evidence.get(key)
                if not isinstance(value,str) or not 1<=len(value.strip())<=limit:
                    raise ValueError('Completá fuente, referencia y nota de la evidencia.')
                clean_evidence[key]=value.strip()
            link['evidence']=clean_evidence
        links.append(link)
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



def save_version(path, payload):
    from uuid import uuid4
    from datetime import datetime, timezone
    if not isinstance(payload, dict) or payload.get('reviewed') is not True:
        raise ValueError('Revisá la red y los supuestos antes de conservarla.')
    title, assumptions = payload.get('title'), payload.get('assumptions')
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 100:
        raise ValueError('Ingresá un título de hasta 100 caracteres.')
    if not isinstance(assumptions, str) or not 1 <= len(assumptions.strip()) <= 6000:
        raise ValueError('Registrá el fundamento y los supuestos de la red.')
    graph = validate_graph(payload['graph'])
    record = dict(id=str(uuid4()), created_at=datetime.now(timezone.utc).isoformat(),
                  title=title.strip(), assumptions=assumptions.strip(), graph=graph)
    parent=payload.get('parent_id')
    if parent:
        previous=get_version(path,parent)
        if previous.get('workflow',{}).get('id','')!=payload.get('workflow_id',''):raise ValueError('Red de otro expediente.')
        record['parent_id']=parent
    identity = payload.get('workflow_id')
    if identity is not None and not isinstance(identity, str):
        raise ValueError('Referencia de expediente inválida.')
    if identity:
        from .workflow import get_workflow
        case = get_workflow(path, identity)
        record['workflow'] = {key: case[key] for key in ('id', 'title', 'revision')}
    if graph.get('schema')==2:
        from .decision_agents import fingerprint
        record['sha256']=fingerprint(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS graph_versions (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        db.execute('INSERT INTO graph_versions VALUES (?,?)', (record['id'], json.dumps(record, ensure_ascii=False)))
    return record


def version_history(path, workflow_id=''):
    if workflow_id:
        from .workflow import get_workflow
        get_workflow(path, workflow_id)
    if not path.exists():return []
    with closing(sqlite3.connect(path)) as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='graph_versions'").fetchone():return []
        sql = 'SELECT payload FROM graph_versions'
        args = ()
        if workflow_id:
            sql += " WHERE json_extract(payload,'$.workflow.id')=?"
            args = (workflow_id,)
        return [json.loads(row[0]) for row in db.execute(sql+' ORDER BY rowid DESC LIMIT 30', args)]


def verify_version(record):
    from .decision_agents import fingerprint
    if record['graph'].get('schema')==2 and not record.get('sha256'):raise ValueError('Falta la huella de la red visual.')
    if record.get('sha256') and fingerprint({k:v for k,v in record.items() if k!='sha256'})!=record['sha256']:
        raise ValueError('Versión de red alterada.')
    if validate_graph(record['graph'])!=record['graph']:raise ValueError('Red conservada incompatible.')
    return record

def get_version(path,identity):
    from .workflow import NotFound
    with closing(sqlite3.connect(path)) as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='graph_versions'").fetchone():raise NotFound('Red inexistente.')
        row=db.execute('SELECT payload FROM graph_versions WHERE id=?',(identity,)).fetchone()
    if not row:raise NotFound('Red inexistente.')
    return verify_version(json.loads(row[0]))
