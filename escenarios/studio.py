"""Reviewed links between existing frozen analytical models. No inference or causal propagation."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4
from . import graph,sequential,variables,continuity
from .workflow import get_workflow,get_version,now,text,NotFound,Conflict
from .decision_agents import fingerprint
from .visual_graph import STATUSES

LIMITS=['Matrices de dos actores y dos estrategias; árboles de dos etapas con información perfecta.',
        'Una conexión gráfica no demuestra causalidad ni modifica pagos o probabilidades.',
        'Variables y transformaciones declaradas se registran para revisión; no se ejecutan fórmulas de texto.',
        'Comparación exploratoria; no acredita mejora predictiva ni autenticidad de fuentes.']

def connect(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path,timeout=10)) as probe:
        exists=probe.execute("SELECT 1 FROM sqlite_master WHERE name='studio_scenarios'").fetchone()
    if not exists and path.stat().st_size:
        content,info=continuity.snapshot(path)
        directory=path.parent/'migration-backups';directory.mkdir(exist_ok=True)
        target=directory/('visual-'+str(uuid4())+'.sqlite3');target.write_bytes(content)
        if fingerprint_bytes(target.read_bytes())!=info['sha256']:raise ValueError('Respaldo visual no verificado.')
        target.with_suffix('.json').write_text(json.dumps(info),encoding='utf-8')
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS studio_scenarios (id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, payload TEXT NOT NULL)');db.commit()
    return db

def fingerprint_bytes(value):
    import hashlib
    return hashlib.sha256(value).hexdigest()

def read(path,identity):
    with closing(connect(path)) as db:row=db.execute('SELECT payload FROM studio_scenarios WHERE id=?',(identity,)).fetchone()
    if not row:raise NotFound('Escenario inexistente.')
    return verify(json.loads(row[0]))

def history(path,scope):
    get_workflow(path,scope)
    with closing(connect(path)) as db:
        return [verify(json.loads(r[0])) for r in db.execute('SELECT payload FROM studio_scenarios WHERE workflow_id=? ORDER BY rowid DESC LIMIT 100',(scope,))]

def verify(record):
    from .executive import verify_source
    p=record['payload']
    if p.get('engine')!='visual-study-v1' or fingerprint(p)!=record['sha256']:raise ValueError('Escenario alterado.')
    graph.verify_version(p['network']);verify_source('matrix',p['matrix'])
    if p['tree']:verify_source('tree',p['tree'])
    if p.get('dictionary'):variables.verify(p['dictionary'])
    validate_links(p,p['links'])
    return record

def validate_links(body,links):
    if not isinstance(links,list) or len(links)>400:raise ValueError('Hasta 400 referencias analíticas.')
    from .visual_graph import upgrade
    nodes={n['uid']:n for n in upgrade(body['network']['graph'],body['network']['id'])['nodes']};seen=set();clean=[]
    for link in links:
        if not isinstance(link,dict):raise ValueError('Referencia analítica inválida.')
        node=link.get('node_uid');kind=link.get('kind');actor=link.get('actor')
        if node not in nodes or kind not in ('matrix','tree') or type(actor) is not int or actor not in (0,1):raise ValueError('Referencia de actor inválida.')
        source=body['matrix'] if kind=='matrix' else body['tree']
        if not source:raise ValueError('Árbol requerido para esta referencia.')
        strategies=link.get('strategies',[])
        if not isinstance(strategies,list) or any(type(i) is not int or i not in (0,1) for i in strategies) or len(set(strategies))!=len(strategies):raise ValueError('Estrategia referenciada inválida.')
        key=(node,kind,actor)
        if key in seen:raise ValueError('Referencia analítica duplicada.')
        seen.add(key)
        clean.append({'node_uid':node,'kind':kind,'actor':actor,'strategies':strategies})
    return clean

def save(path,value):
    if not isinstance(value,dict):raise ValueError('Escenario inválido.')
    if value.get('reviewed') is not True:raise ValueError('Revisá enlaces, fuentes y supuestos antes de guardar.')
    scope=value.get('workflow_id');get_workflow(path,scope)
    version=value.get('matrix_version')
    if type(version) is not int or version<1:raise ValueError('Versión de matriz requerida.')
    matrix=get_version(path,scope,version);network=graph.get_version(path,value.get('network_id'))
    if network.get('workflow',{}).get('id')!=scope:raise ValueError('Red de otro expediente.')
    tree=None
    if value.get('tree_id'):
        try:tree=sequential.get_version(path,value['tree_id'])
        except KeyError:raise NotFound('Árbol inexistente.')
        if tree.get('workflow',{}).get('id')!=scope:raise ValueError('Árbol de otro expediente.')
    dictionary=None
    if value.get('dictionary_id'):
        dictionary=variables.read(path,value['dictionary_id']);w=dictionary['payload']['workflow']
        if w.get('id')!=scope or w.get('version')!=version:raise ValueError('Diccionario de otra matriz.')
    mode=value.get('evidence_mode')
    if mode not in ('synthetic','declared','pending'):raise ValueError('Clasificá la evidencia del escenario.')
    units=value.get('payoff_units')
    if not isinstance(units,list) or len(units)!=2:raise ValueError('Definí las escalas de pagos de ambos actores.')
    units=[text(x,160) for x in units]
    if type(value.get('comparable')) is not bool:raise ValueError('Revisá la comparabilidad de escalas.')
    rows=value.get('variables',[])
    if not isinstance(rows,list) or len(rows)>100:raise ValueError('Hasta cien variables declaradas.')
    clean=[];seen=set()
    for row in rows:
        if not isinstance(row,dict):raise ValueError('Variable inválida.')
        item={k:text(row.get(k,''),1200 if k=='transformation' else 250,k not in ('transformation',)) for k in ('name','value','unit','source','target','transformation')}
        if item['name'].casefold() in seen:raise ValueError('Variable duplicada.')
        seen.add(item['name'].casefold());item['status']=row.get('status')
        if item['status'] not in STATUSES:raise ValueError('Evidencia de variable inválida.')
        target=item['target'];m=matrix['model']
        if target=='context':item['model_value']=None
        elif target in ('p','q'):item['model_value']=m[target]
        elif len(target)==3 and target[0] in ('a','b') and target[1:] in ('00','01','10','11'):item['model_value']=m[target[0]][int(target[1])][int(target[2])]
        else:raise ValueError('Destino de transformación inválido.')
        if target!='context' and not item['transformation']:raise ValueError('Describí y revisá la transformación a parámetros del modelo.')
        clean.append(item)
    constraints=value.get('constraints',[])
    if not isinstance(constraints,list) or len(constraints)>50:raise ValueError('Hasta cincuenta restricciones declaradas.')
    body={'engine':'visual-study-v1','workflow':{'id':scope,'version':version},'title':text(value.get('title'),160),
          'assumptions':text(value.get('assumptions'),6000),'evidence_mode':mode,'payoff_units':units,'comparable':value['comparable'],
          'network':network,'matrix':matrix,'tree':tree,'dictionary':dictionary,'variables':clean,
          'constraints':[text(x,1000) for x in constraints],'links':[], 'limits':LIMITS,
          'review':{'confirmed':True,'at':now(),'transformations':'Declaradas y revisadas; sin ejecución automática.'}}
    body['links']=validate_links(body,value.get('links',[]))
    parent=value.get('parent_id');clone=value.get('clone_of');lineage=str(uuid4());number=1
    if parent:
        previous=read(path,parent)
        if previous['payload']['workflow']['id']!=scope:raise ValueError('Escenario de otro expediente.')
        lineage=previous['payload']['lineage'];number=previous['payload']['revision']+1
        body['parent_id']=parent
    if clone:
        original=read(path,clone)
        if original['payload']['workflow']['id']!=scope:raise ValueError('No se puede duplicar un escenario de otro expediente.')
        body['clone_of']=clone
    body.update(lineage=lineage,revision=number)
    record={'id':str(uuid4()),'created_at':now(),'payload':body,'sha256':fingerprint(body)};verify(record)
    with closing(connect(path)) as db,db:
        db.execute('BEGIN IMMEDIATE')
        if parent and db.execute("SELECT 1 FROM studio_scenarios WHERE json_extract(payload,'$.payload.parent_id')=?",(parent,)).fetchone():raise Conflict('Hay una revisión más reciente; recargá antes de guardar.')
        db.execute('INSERT INTO studio_scenarios VALUES (?,?,?)',(record['id'],scope,json.dumps(record,ensure_ascii=False,allow_nan=False)))
    return record

def status(path,record):
    p=record['payload'];scope=p['workflow']['id'];warnings=[]
    case=get_workflow(path,scope)
    if case['versions'] and case['versions'][0]['version']!=p['workflow']['version']:warnings.append('Hay una matriz posterior; este escenario conserva la versión original.')
    nets=graph.version_history(path,scope)
    if nets and nets[0]['id']!=p['network']['id']:warnings.append('Hay otra red más reciente en el expediente; no se sustituyó la conservada.')
    if not any(n['id']==p['network']['id'] for n in nets):warnings.append('Red original fuera del historial visible o no disponible; se utiliza la copia congelada.')
    trees=sequential.history(path,scope)
    if p['tree'] and trees and trees[0]['id']!=p['tree']['id']:warnings.append('Hay otro árbol posterior; revisá si es una variante o una actualización.')
    return warnings

def compare(left,right):
    verify(left);verify(right);a=left['payload'];b=right['payload']
    if a['workflow']['id']!=b['workflow']['id']:raise ValueError('Compará escenarios del mismo expediente.')
    comparable=a['comparable'] and b['comparable'] and a['payoff_units']==b['payoff_units'] and a['matrix']['model']['actors']==b['matrix']['model']['actors'] and a['matrix']['model']['strategies']==b['matrix']['model']['strategies']
    fields=['assumptions','evidence_mode','payoff_units','constraints','variables','links']
    differences=[{'field':k,'left':a[k],'right':b[k]} for k in fields if a[k]!=b[k]]
    for kind in ('network','matrix','tree','dictionary'):
        if a[kind]!=b[kind]:differences.append({'field':kind,'left':a[kind].get('id',a['workflow']['version']) if a[kind] else None,'right':b[kind].get('id',b['workflow']['version']) if b[kind] else None})
    return {'left':left['id'],'right':right['id'],'comparable':comparable,'differences':differences,
            'expected_a_delta':[b['matrix']['values_a'][i]-a['matrix']['values_a'][i] for i in range(2)] if comparable else None,
            'expected_b_delta':[b['matrix']['values_b'][i]-a['matrix']['values_b'][i] for i in range(2)] if comparable else None,
            'left_pure':a['matrix']['pure'],'right_pure':b['matrix']['pure'],
            'left_tree':a['tree']['equilibria'] if a['tree'] else None,'right_tree':b['tree']['equilibria'] if b['tree'] else None,
            'limits':LIMITS+['Las diferencias de utilidad solo se muestran con etiquetas y escalas coincidentes y confirmación del analista. No son diferencias de precisión.']}

def catalog(path,scope):
    case=get_workflow(path,scope)
    return {'workflow_id':scope,'matrices':[{'version':v['version'],'title':get_version(path,scope,v['version'])['model']['title']} for v in case['versions'][:100]],
            'networks':[graph.verify_version(r) for r in graph.version_history(path,scope)],'trees':sequential.history(path,scope),
            'scenarios':[{**r,'warnings':status(path,r)} for r in history(path,scope)],'limits':LIMITS}


def report(path,identities):
    from . import executive
    if not isinstance(identities,list) or not 1<=len(identities)<=2:raise ValueError('Seleccioná uno o dos escenarios.')
    records=[read(path,i) for i in identities];scope=records[0]['payload']['workflow']['id']
    if any(r['payload']['workflow']['id']!=scope for r in records):raise ValueError('Escenarios de distintos expedientes.')
    refs=[]
    for r in records:
        p=r['payload']
        for kind,identity in [('scenario',r['id']),('graph',p['network']['id'])]+([('tree',p['tree']['id'])] if p['tree'] else []):
            ref={'kind':kind,'id':identity}
            if ref not in refs:refs.append(ref)
    return executive.create(path,{'workflow_id':scope,'version':records[0]['payload']['workflow']['version'],
        'title':'Estudio visual · '+records[0]['payload']['title'],'sections':['matrix','graph','scenario','tree','simulation'],
        'references':refs,'evidence_mode':'synthetic' if all(r['payload']['evidence_mode']=='synthetic' for r in records) else 'declared',
        'executive_note':'Escenarios independientes conservados; cada uno identifica su matriz y escalas. '+(('Comparación con escalas declaradas compatibles. ' if compare(*records)['comparable'] else 'Escalas no comparables; no se informa diferencia de utilidad. ')+str(len(compare(*records)['differences']))+' diferencias de configuración conservadas en el registro.' if len(records)==2 else ''),
        'pending':'Verificar externamente fuentes, interpretación y comparabilidad. Sin acreditación predictiva real.','reviewed':True})
