"""Informes ejecutivos inmutables: fuentes seleccionadas y cálculos existentes."""
import json
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path
from uuid import uuid4
from . import agents, comparisons, payoff_sweep, sequential, simulation, research, variables, decision_agents as decisions
from .case_model import analyze_case
from .workflow import get_version, get_workflow, now

LABELS = {'matrix':'Matriz estratégica', 'tree':'Árbol decisorio', 'simulation':'Monte Carlo',
          'agents':'Agentes con memoria', 'comparison':'Comparación de políticas',
          'sweep':'Sensibilidad de incentivos', 'decision':'Decisiones de IA local', 'benchmark':'Batería de agentes IA', 'evaluation':'Evaluación predictiva', 'variables':'Variables y unidades'}
TABLES = {'tree':'sequential_versions', 'agents':'agent_runs', 'comparison':'agent_comparisons',
          'sweep':'payoff_sweeps', 'decision':'decision_comparisons', 'benchmark':'decision_benchmarks', 'evaluation':'research_records', 'variables':'variable_versions'}
LIMITS = ['Documento exploratorio condicionado a modelos y supuestos; no garantiza predicciones ni éxito judicial.',
          'Los documentos y hechos son declarados por el analista; su autenticidad exige revisión externa.',
          'SHA-256 identifica contenido, no es una firma ni acredita veracidad.',
          'Utilidades de modelos o actores con escalas diferentes no se agregan ni comparan entre sí.',
          'La reproducción verifica cálculos y registros; no garantiza toda la coherencia semántica.',
          'No se ejecuta inferencia nueva ni se modifican políticas, pagos o evidencias al exportar.']

def text(value, limit, optional=False):
    if not isinstance(value,str) or len(value)>limit or (not optional and not value.strip()):
        raise ValueError('Texto requerido o demasiado extenso para el informe.')
    return value.strip()

def connect(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS executive_reports (id TEXT PRIMARY KEY, workflow_id TEXT, payload TEXT)')
    db.commit();return db

def _sources(path,kind):
    with closing(sqlite3.connect(path)) as db:
        table=TABLES[kind]
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name=? AND type='table'",(table,)).fetchone():return []
        query=f'SELECT payload FROM {table}'
        if kind=='evaluation':query+=" WHERE kind='evaluation'"
        return [json.loads(r[0]) for r in db.execute(query+' ORDER BY rowid DESC')]

def scope(kind,record):
    if kind=='evaluation':return record['payload']['protocol']['payload']['workflow']
    if kind in ('decision','benchmark','variables'):return record['payload'].get('workflow',{})
    return record.get('workflow',{})

def compatible(kind,record,workflow_id,version):
    source=scope(kind,record)
    return source.get('id')==workflow_id and (kind=='tree' or source.get('version')==version)

def catalog(path,workflow_id,version):
    matrix=get_version(path,workflow_id,version)
    items=[]
    for kind in TABLES:
        for record in _sources(path,kind):
            if not compatible(kind,record,workflow_id,version):continue
            body=record.get('payload',record)
            title=body.get('model',{}).get('title') or (body['candidate']['payload']['name'] if kind=='evaluation' else 'Diccionario de '+str(len(body['variables']))+' variables' if kind=='variables' else kind)
            items.append({'kind':kind,'id':record['id'],'title':title,'created_at':record.get('created_at',record.get('calculated_at','')),
                          'label':LABELS[kind],'simulation':bool(record.get('simulation')),
                          'evidence':body['result']['evidence'] if kind=='evaluation' else 'variables_declared' if kind=='variables' else 'simulation_only'})
    return {'workflow_id':workflow_id,'version':version,'matrix':matrix,'items':items[:200],
            'total':len(items),'limits':LIMITS}

def verify_source(kind,record):
    """Recalcular con motores originales; las decisiones IA se leen de sus trazas."""
    if kind=='variables':
        variables.verify(record);return
    elif kind=='matrix':
        fresh=analyze_case(record['model']);keys=('model','pure','mixed','values_a','values_b','best_a')
    elif kind=='tree':
        fresh=sequential.analyze(record['model']);keys=('model','responses','equilibria','method','limits')
        if record.get('simulation') and simulation.simulate(record['model'],record['simulation']['options'])!=record['simulation']:
            raise ValueError('La simulación del árbol no se reproduce.')
    elif kind in ('agents','comparison','sweep'):
        fn={'agents':agents.run,'comparison':comparisons.compare,'sweep':payoff_sweep.run}[kind]
        fresh=fn({'model':record['model'],'options':record['options'],'assumptions':record['assumptions']})
        keys={'agents':('engine','model','options','rounds','totals','means','action_counts'),
              'comparison':('engine','model','options','seeds','policies','cells'),
              'sweep':('engine','model','options','points','changes')}[kind]
    elif kind in ('decision','benchmark','evaluation'):
        # Base efímera con copias congeladas: ninguna dependencia de fuentes actuales.
        with tempfile.TemporaryDirectory(prefix='tj-report-') as directory:
            path=Path(directory)/'replay.sqlite3'
            if kind in ('decision','benchmark'):
                with closing(decisions.connect(path)) as db,db:
                    if kind=='decision':db.execute('INSERT INTO decision_comparisons VALUES (?,?)',(record['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
                    else:
                        db.execute('CREATE TABLE decision_benchmarks (id TEXT PRIMARY KEY,payload TEXT)')
                        db.execute('INSERT INTO decision_benchmarks VALUES (?,?)',(record['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))
                        for t in record['payload']['trials']:
                            if t['comparison']:db.execute('INSERT INTO decision_comparisons VALUES (?,?)',(t['comparison']['id'],json.dumps(t['comparison'],ensure_ascii=False,allow_nan=False)))
                if kind=='decision':decisions.replay(path,record['id'])
                else:decisions.benchmark_record(path,record['id'],True)
            else:
                with closing(research.connect(path)) as db,db:
                    db.execute('INSERT INTO research_records VALUES (?,?,?)',(record['id'],'evaluation',json.dumps(record,ensure_ascii=False,allow_nan=False)))
                research.replay(path,record['id'])
        return
    else:raise ValueError('Fuente de informe desconocida.')
    if any(fresh[k]!=record[k] for k in keys):raise ValueError('Los cálculos de '+LABELS[kind]+' no se reproducen.')

def create(path,payload):
    if payload.get('reviewed') is not True:raise ValueError('Revisá fuentes, secciones y clasificación antes de conservar.')
    workflow_id=payload.get('workflow_id');version=payload.get('version')
    if type(version) is not int or version<1:raise ValueError('Seleccioná una versión calculada.')
    matrix=get_version(path,workflow_id,version)
    sections=payload.get('sections')
    if not isinstance(sections,list) or not sections or any(k not in LABELS for k in sections) or len(set(sections))!=len(sections):
        raise ValueError('Seleccioná secciones distintas y válidas.')
    if 'simulation' in sections and 'tree' not in sections:raise ValueError('Monte Carlo necesita incluir el árbol de origen.')
    refs=payload.get('references',[])
    if not isinstance(refs,list) or len(refs)>16:raise ValueError('Hasta dieciséis fuentes complementarias por informe.')
    picked=[];seen=set()
    for ref in refs:
        if not isinstance(ref,dict) or set(ref)!={'kind','id'} or ref['kind'] not in TABLES:raise ValueError('Referencia de fuente inválida.')
        key=(ref['kind'],text(ref['id'],200))
        if key in seen:raise ValueError('Fuente duplicada.')
        seen.add(key)
        record=next((r for r in _sources(path,key[0]) if r['id']==key[1]),None)
        if record is None:raise ValueError('Fuente conservada inexistente.')
        if not compatible(key[0],record,workflow_id,version):raise ValueError('Fuente de otro expediente o versión de matriz.')
        if key[0] not in sections:raise ValueError('Una fuente pertenece a una sección desactivada.')
        if key[0] in ('agents','comparison','sweep') and record['model']!=matrix['model']:raise ValueError('La matriz del laboratorio no coincide con la versión seleccionada.')
        if key[0] in ('decision','benchmark') and record['payload']['model']!=matrix['model']:raise ValueError('La matriz de la IA no coincide con la versión seleccionada.')
        if key[0]=='evaluation' and record['payload']['protocol']['payload']['snapshot']['model']!=matrix['model']:raise ValueError('La matriz del protocolo no coincide con la seleccionada.')
        if key[0]=='variables' and record['payload']['matrix']!=matrix:raise ValueError('La matriz del diccionario no coincide con la seleccionada.')
        verify_source(key[0],record)
        picked.append({'kind':key[0],'id':key[1],'sha256':decisions.fingerprint(record),'record':record})
    verify_source('matrix',matrix)
    mode=payload.get('evidence_mode')
    if mode not in ('synthetic','declared'):raise ValueError('Clasificá explícitamente el informe como sintético o fuentes declaradas.')
    body={'engine':'unified-executive-v1','workflow':{'id':workflow_id,'version':version},
          'title':text(payload.get('title'),200),'executive_note':text(payload.get('executive_note',''),4000,True),
          'pending':text(payload.get('pending',''),4000,True),'evidence_mode':mode,'sections':sections,
          'matrix':matrix,'matrix_sha256':decisions.fingerprint(matrix),'sources':picked,'limits':LIMITS}
    record={'id':str(uuid4()),'created_at':now(),'payload':body,'sha256':decisions.fingerprint(body)}
    with closing(connect(path)) as db,db:db.execute('INSERT INTO executive_reports VALUES (?,?,?)',(record['id'],workflow_id,json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record

def read(path,identity):
    with closing(connect(path)) as db:
        row=db.execute('SELECT payload FROM executive_reports WHERE id=?',(identity,)).fetchone()
    if not row:raise ValueError('Informe conservado desconocido.')
    record=json.loads(row[0]);verify(record,calculations=False);return record

def history(path,workflow_id):
    get_workflow(path,workflow_id)
    with closing(connect(path)) as db:
        return [{'id':r['id'],'created_at':r['created_at'],'title':r['payload']['title'],'version':r['payload']['workflow']['version'],
                 'evidence_mode':r['payload']['evidence_mode'],'sha256':r['sha256']}
                for row in db.execute('SELECT payload FROM executive_reports WHERE workflow_id=? ORDER BY rowid DESC LIMIT 50',(workflow_id,))
                for r in [json.loads(row[0])]]

def verify(record,calculations=True):
    body=record['payload']
    if body['engine']!='unified-executive-v1' or decisions.fingerprint(body)!=record['sha256'] or decisions.fingerprint(body['matrix'])!=body['matrix_sha256']:
        raise ValueError('El manifiesto o la matriz no coincide con su huella.')
    for source in body['sources']:
        if decisions.fingerprint(source['record'])!=source['sha256'] or not compatible(source['kind'],source['record'],body['workflow']['id'],body['workflow']['version']):
            raise ValueError('Una fuente congelada fue alterada o es incompatible.')
        if calculations:verify_source(source['kind'],source['record'])
    if calculations:verify_source('matrix',body['matrix'])
    return {'id':record['id'],'sha256':record['sha256'],'reproduced':True,'sources':len(body['sources'])+1,'new_inference':False}

def replay(path,identity):return verify(read(path,identity))
