"""Generación local en segundo plano sin bloquear transacciones del expediente."""
import json
import sqlite3
import threading
from contextlib import closing
from uuid import uuid4
from . import local_ai
from .workflow import get_workflow,now,Conflict,NotFound

LOCK=threading.Lock()
RUNNING=False


def connect(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS ai_jobs (id TEXT PRIMARY KEY, workflow_id TEXT, payload TEXT)')
    db.commit()
    return db


def get_job(path,identity):
    with closing(connect(path)) as db:
        row=db.execute('SELECT payload FROM ai_jobs WHERE id=?',(identity,)).fetchone()
    if not row:raise NotFound('La propuesta no existe.')
    return json.loads(row[0])


def list_jobs(path,workflow_id):
    with closing(connect(path)) as db:
        return [json.loads(row[0]) for row in db.execute('SELECT payload FROM ai_jobs WHERE workflow_id=? ORDER BY rowid DESC LIMIT 5',(workflow_id,))]


def store(path,value):
    with closing(connect(path)) as db,db:
        db.execute('INSERT OR REPLACE INTO ai_jobs VALUES (?,?,?)',(value['id'],value['workflow_id'],json.dumps(value,ensure_ascii=False,allow_nan=False)))


def recover_interrupted(path):
    with closing(connect(path)) as db,db:
        for row in db.execute('SELECT payload FROM ai_jobs').fetchall():
            value=json.loads(row[0])
            if value['state']=='running':
                value['state']='failed';value['error']='La aplicación se reinició durante la generación. Podés reintentar.'
                db.execute('UPDATE ai_jobs SET payload=? WHERE id=?',(json.dumps(value,ensure_ascii=False),value['id']))


def start(path,payload):
    global RUNNING
    workflow=get_workflow(path,payload['id'])
    if type(payload.get('revision')) is not int or workflow['revision']!=payload['revision']:
        raise Conflict('El expediente cambió. Recargalo antes de solicitar una propuesta.')
    with LOCK:
        if RUNNING:raise Conflict('Ya hay una generación local en curso. Esperá a que termine.')
        RUNNING=True
    value={'id':str(uuid4()),'workflow_id':workflow['id'],'base_revision':workflow['revision'],
           'created_at':now(),'state':'running','result':None,'error':None}
    try:
        store(path,value)
        threading.Thread(target=worker,args=(path,workflow,value),daemon=True).start()
    except Exception:
        with LOCK:RUNNING=False
        raise
    return value


def worker(path,workflow,value):
    global RUNNING
    try:
        value['result']=local_ai.propose(path,workflow);value['state']='ready'
    except local_ai.AIError as error:
        value['state']='failed';value['error']=str(error)
    except Exception:
        value['state']='failed';value['error']='No se pudo generar la propuesta. El modo guiado sigue disponible.'
    finally:
        value['finished_at']=now()
        try:store(path,value)
        finally:
            with LOCK:RUNNING=False
