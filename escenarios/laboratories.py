"""Laboratorios basados en versiones congeladas de expedientes."""
import json
import sqlite3
from contextlib import closing
from . import agents,comparisons,payoff_sweep
from .workflow import get_version,get_workflow

MODULES={'agents':(agents,agents.run,'agent_runs'),'comparison':(comparisons,comparisons.compare,'agent_comparisons'),'sweep':(payoff_sweep,payoff_sweep.run,'payoff_sweeps')}

def module(kind):
    if not isinstance(kind,str) or kind not in MODULES:raise ValueError('Laboratorio inválido.')
    return MODULES[kind]

def history(path,kind,workflow_id=''):
    _,_,table=module(kind)
    if workflow_id:get_workflow(path,workflow_id)
    if not path.exists():return []
    with closing(sqlite3.connect(path)) as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():return []
        query=f'SELECT payload FROM {table}'
        params=()
        if workflow_id:query+=" WHERE json_extract(payload,'$.workflow.id')=?";params=(workflow_id,)
        return [json.loads(r[0]) for r in db.execute(query+' ORDER BY rowid DESC LIMIT 20',params)]

def save_from_version(path,payload):
    if not isinstance(payload,dict):raise ValueError('Configuración inválida del laboratorio.')
    mod,run,_=module(payload.get('kind'))
    if payload.get('reviewed') is not True:raise ValueError('Confirmá la revisión del laboratorio antes de guardar.')
    version=payload.get('version')
    if type(version) is not int or not 1<=version<=2147483647:raise ValueError('Seleccioná una versión calculada del expediente.')
    if not isinstance(payload.get('options'),dict):raise ValueError('Configuración incompleta del laboratorio.')
    source=get_version(path,payload.get('workflow_id'),version)
    # Never accept a client-supplied matrix in place of the frozen source.
    result=run({'model':source['model'],'options':payload.get('options'),'assumptions':payload.get('assumptions')})
    result['workflow']={'id':payload['workflow_id'],'title':source['model']['title'],'version':version}
    return mod.save(path,result)
