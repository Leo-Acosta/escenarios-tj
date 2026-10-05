"""Coordinador guiado y persistente. No interpreta texto ni llama a una IA."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from uuid import uuid4
from .case_model import analyze_case


QUESTIONS = [
    ('objective', '¿Qué decisión querés evaluar y qué objetivo buscás alcanzar?'),
    ('horizon', '¿En qué plazo y contexto se toma la decisión?'),
    ('facts', '¿Qué datos conocés? Diferenciá hechos aportados y datos que todavía faltan.'),
    ('payoff_basis', '¿Cómo vas a asignar los pagos de cada resultado? Indicá la escala y su fundamento, o declaralos hipotéticos.'),
    ('probability_basis', '¿Qué respalda las probabilidades de conducta? Si no hay evidencia, declaralas como supuestos exploratorios.'),
]


class Conflict(ValueError):
    pass


class NotFound(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def text(value, maximum, required=True):
    if not isinstance(value, str) or len(value.strip()) > maximum or (required and not value.strip()):
        raise ValueError('Revisá los textos obligatorios y su longitud.')
    return value.strip()


def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS workflows (id TEXT PRIMARY KEY, updated_at TEXT, revision INTEGER, payload TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS workflow_versions (workflow_id TEXT, version INTEGER, created_at TEXT, payload TEXT, PRIMARY KEY(workflow_id,version))')
    db.commit()
    return db


def encoded(data):
    return json.dumps(data, ensure_ascii=False, allow_nan=False)


def question(data):
    return next(({'key': key, 'text': value} for key, value in QUESTIONS if key not in data['answers']), None)


def view(db, data):
    data['question'] = question(data)
    data['versions'] = [{'version': row[0], 'created_at': row[1]} for row in db.execute(
        'SELECT version,created_at FROM workflow_versions WHERE workflow_id=? ORDER BY version DESC', (data['id'],))]
    return data


def read(db, identity):
    row = db.execute('SELECT payload FROM workflows WHERE id=?', (text(identity, 40),)).fetchone()
    if not row:
        raise NotFound('El expediente no existe.')
    return json.loads(row[0])


def get_workflow(path, identity):
    with closing(connect(path)) as db:
        return view(db, read(db, identity))


def list_workflows(path):
    if not path.exists():
        return []
    with closing(connect(path)) as db:
        items=[]
        for row in db.execute('SELECT payload FROM workflows ORDER BY updated_at DESC LIMIT 30'):
            d=json.loads(row[0])
            items.append({k:d[k] for k in ('id','title','stage','revision','updated_at')})
        return items


def draft(value):
    """Permite campos sin completar, sin almacenar formas arbitrarias."""
    if not isinstance(value, dict):
        raise ValueError('Modelo inválido.')
    m={'title':text(value['title'],100,False)}
    if not isinstance(value['actors'],list) or len(value['actors'])!=2:
        raise ValueError('Se necesitan dos actores.')
    m['actors']=[text(v,100,False) for v in value['actors']]
    rows=value['strategies']
    if not isinstance(rows,list) or len(rows)!=2 or any(not isinstance(r,list) or len(r)!=2 for r in rows):
        raise ValueError('Se necesitan dos estrategias por actor.')
    m['strategies']=[[text(v,100,False) for v in r] for r in rows]
    for key in ('a','b'):
        rows=value[key]
        if not isinstance(rows,list) or len(rows)!=2 or any(not isinstance(r,list) or len(r)!=2 for r in rows):
            raise ValueError('Matriz inválida.')
        for r in rows:
            for v in r:
                if v is not None and (type(v) not in (int,float) or not -1000000<=v<=1000000):
                    raise ValueError('Pago inválido.')
        m[key]=rows
    for key in ('p','q'):
        v=value[key]
        if v is not None and (type(v) not in (int,float) or not 0<=v<=1):
            raise ValueError('Probabilidad inválida.')
        m[key]=v
    return m


def evidence(value):
    if not isinstance(value,list) or len(value)>20:
        raise ValueError('Máximo veinte fuentes por expediente.')
    return [{'title':text(v['title'],200), 'reference':text(v['reference'],1000),
             'claim':text(v['claim'],2000), 'origin':'analyst', 'verified':False} for v in value]


def operate(path, payload):
    if not isinstance(payload,dict):
        raise ValueError('Solicitud inválida.')
    action=payload.get('action')
    proposal_job=None
    if action=='accept_ai':
        from .ai_jobs import get_job
        proposal_job=get_job(path,text(payload['job_id'],40))
    with closing(connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        if action=='create':
            description=text(payload['description'],12000)
            if len(description)<10:raise ValueError('Describí el caso con al menos diez caracteres.')
            identity=str(uuid4());stamp=now()
            d={'id':identity,'title':text(payload['title'],100),'description':description,'stage':'collecting',
               'revision':1,'updated_at':stamp,'answers':{},'evidence':[],'assumptions':'', 'model':None,
               'result':None,'messages':[{'role':'user','text':description,'source':'analyst','at':stamp},
               {'role':'assistant','text':QUESTIONS[0][1],'source':'guided','at':stamp}]}
            db.execute('INSERT INTO workflows VALUES (?,?,?,?)',(identity,stamp,1,encoded(d)))
            return view(db,d)
        d=read(db,payload['id'])
        if type(payload.get('revision')) is not int or payload['revision']!=d['revision']:
            raise Conflict('El expediente cambió en otra pestaña. Recargá la versión antes de guardar.')
        if action=='message':
            if len(d['messages'])>=100:raise ValueError('La conversación alcanzó el límite de cien mensajes.')
            q=question(d)
            if q is None:raise ValueError('Las preguntas están completas. Editá los datos del modelo y revisá los supuestos.')
            answer=text(payload['text'],4000);stamp=now()
            d['answers'][q['key']]=answer
            d['messages'].append({'role':'user','text':answer,'source':'analyst','at':stamp})
            next_q=question(d)
            reply=next_q['text'] if next_q else 'La preparación está completa. Definí los dos actores, sus estrategias y pagos. Registrá las fuentes y revisá los supuestos antes de calcular. Sin IA, el texto no se interpreta automáticamente.'
            d['messages'].append({'role':'assistant','text':reply,'source':'guided','at':stamp})
            d['stage']='collecting' if next_q else 'modeling'
            d['result']=None
        elif action=='accept_ai':
            if proposal_job['workflow_id']!=d['id'] or proposal_job['state']!='ready':
                raise ValueError('La propuesta no corresponde a este expediente o no está lista.')
            if proposal_job['base_revision']!=d['revision']:
                raise Conflict('El expediente cambió después de solicitar la propuesta. Generá una nueva antes de aplicarla.')
            from .local_ai import validate_proposal
            proposal=validate_proposal(proposal_job['result']['proposal'])
            if len(d.get('ai_proposals',[]))>=10 or len(d['messages'])>=100:
                raise ValueError('El expediente alcanzó el límite de propuestas o mensajes.')
            m=d['model'] or {'title':d['title'],'actors':['',''],'strategies':[['',''],['','']],
                            'a':[[None,None],[None,None]],'b':[[None,None],[None,None]],'p':.5,'q':.5}
            m['actors']=proposal['actors'];m['strategies']=proposal['strategies']
            d['model']=draft(m)
            record={'job_id':proposal_job['id'],'accepted_at':now(),**proposal_job['result']}
            d.setdefault('ai_proposals',[]).append(record)
            d['messages'].append({'role':'assistant','text':proposal['summary'],'source':'ai-draft',
                                  'at':now(),'model':record['metadata']['model'],'job_id':proposal_job['id']})
            d['result']=None;d['stage']='collecting' if question(d) else 'modeling'
        elif action in ('draft','calculate'):
            d['model']=draft(payload['model']);d['title']=text(d['model']['title'],100)
            d['evidence']=evidence(payload.get('evidence',[]))
            d['assumptions']=text(payload.get('assumptions',''),6000,False)
            d['result']=None;d['stage']='collecting' if question(d) else 'modeling'
            if action=='calculate':
                if question(d):raise ValueError('Completá primero las preguntas de preparación.')
                if payload.get('reviewed') is not True:raise ValueError('Confirmá la revisión de pagos y supuestos antes de calcular.')
                if not d['assumptions']:raise ValueError('Registrá los supuestos del modelo.')
                result=analyze_case(d['model'])
                version=db.execute('SELECT COALESCE(MAX(version),0)+1 FROM workflow_versions WHERE workflow_id=?',(d['id'],)).fetchone()[0]
                result['context']={'workflow_id':d['id'],'version':version,'description':d['description'],
                    'answers':d['answers'],'evidence':d['evidence'],'assumptions':d['assumptions'],
                    'conversation':d['messages'],'reviewed_at':now(),
                    'ai_proposals':d.get('ai_proposals',[]),
                    'mode':'ai-assisted' if d.get('ai_proposals') else 'guided'}
                db.execute('INSERT INTO workflow_versions VALUES (?,?,?,?)',(d['id'],version,now(),encoded(result)))
                d['result']=result;d['stage']='calculated'
        else:
            raise ValueError('Acción inexistente.')
        d['revision']+=1;d['updated_at']=now()
        db.execute('UPDATE workflows SET updated_at=?,revision=?,payload=? WHERE id=?',(d['updated_at'],d['revision'],encoded(d),d['id']))
        return view(db,d)


def get_version(path, identity, version):
    with closing(connect(path)) as db:
        read(db,identity)
        row=db.execute('SELECT payload FROM workflow_versions WHERE workflow_id=? AND version=?',(identity,int(version))).fetchone()
        if not row:raise NotFound('La versión no existe.')
        return json.loads(row[0])
