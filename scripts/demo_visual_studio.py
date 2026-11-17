"""End-to-end visual study showcase. Only a new, synthetic database is accepted."""
import argparse
import json
from pathlib import Path
from .demo_aurora import build as seed
from escenarios import graph,studio,visual_graph,workflow,sequential,executive,continuity


def build(path):
    seed(path)
    metadata=json.loads(path.with_suffix('.demo.json').read_text(encoding='utf-8'));scope=metadata['workflow_id']
    original=graph.version_history(path,scope)[0];g=visual_graph.upgrade(original['graph'],original['id'])
    g['settings']={'layout':'groups','labels':False}
    for n in g['nodes']:
        n['group']='Decisores' if n['id'] in (0,1,4,5) else 'Servicios esenciales' if n['id'] in (2,3) else 'Infraestructura' if n['id'] in (6,7,8) else 'Evidencia y escenarios'
        column=['Decisores','Servicios esenciales','Infraestructura','Evidencia y escenarios'].index(n['group'])
        rank=sum(1 for other in g['nodes'][:n['id']] if other.get('group')==n['group'])
        n['position']={'x':column*300,'y':rank*135}
        n['profile'].update(organization='Puerto Aurora ficticio',role='Coordinación municipal' if n['id']==0 else 'Entidad del escenario',description='Ficha de demostración sintética, sin datos personales reales.',source='Guion de Puerto Aurora')
    g['nodes'][0]['profile']['email']='coordinacion@aurora.invalid'
    for e in g['edges']:
        e['directed']=e['type']=='Influencia';e['label']='Prioridad sanitaria' if e['b']==2 else e['type'];e['start']='2026-11-01';e['end']='2027-01-30'
    g['edges'][0]['weight']={'value':3,'unit':'puntos declarados','meaning':'Intensidad cualitativa de coordinación','scale':'0 a 5, escala ordinal; no probabilidad'}
    net=graph.save_version(path,{'workflow_id':scope,'title':'Puerto Aurora · actores y dependencias','assumptions':'Red ficticia. Flechas y pesos declarados, sin causalidad validada. Ningún vínculo modifica automáticamente los cálculos.','graph':g,'parent_id':original['id'],'reviewed':True})
    trees=sequential.history(path,scope);base=next(t for t in trees if 'Escenario base' in t['model']['title']);crisis=next(t for t in trees if 'Crisis de costos' in t['model']['title'])
    links=[{'node_uid':g['nodes'][i]['uid'],'kind':kind,'actor':i,'strategies':[0,1]} for i in (0,1) for kind in ('matrix','tree')]
    config={'workflow_id':scope,'network_id':net['id'],'matrix_version':1,'tree_id':base['id'],'title':'Acuerdo coordinado · escenario base','assumptions':'DATOS SINTÉTICOS. Inversión compartida y auditoría. Pagos cardinales hipotéticos por actor.','evidence_mode':'synthetic','payoff_units':['puntos propios del municipio','puntos propios del operador'],'comparable':True,'links':links,'variables':[{'name':'Prioridad de continuidad','value':'alta','unit':'categoría declarada','source':'Guion ficticio','target':'context','transformation':'Se usa para interpretar el caso, no para alterar pagos.','status':'assumed'}],'constraints':['Proteger hospital y puerto en 90 días','No modificar pagos sin revisión del analista'],'reviewed':True}
    left=studio.save(path,config)
    current=workflow.get_workflow(path,scope);matrix=workflow.get_version(path,scope,1)['model']
    variant={**matrix,'title':'Puerto Aurora · crisis de costos · FICTICIO','a':[[2,-3],[1,-5]],'b':[[1,4],[2,-2]]}
    workflow.operate(path,{'action':'calculate','id':scope,'revision':current['revision'],'model':variant,'evidence':[],'assumptions':'Costos adversos sintéticos; cambios revisados manualmente, sin inferencia desde la red.','reviewed':True})
    right=studio.save(path,{**config,'clone_of':left['id'],'title':'Crisis de costos · variante revisada','matrix_version':2,'tree_id':crisis['id'],'assumptions':'DATOS SINTÉTICOS. Presión de costos y rechazo del acuerdo; matriz y árbol definidos explícitamente.','constraints':['Proteger hospital y puerto en 90 días','Presupuesto reducido en hipótesis'],'variables':[{'name':'Costo supuesto','value':'adverso','unit':'categoría','source':'Guion de crisis ficticia','target':'a00','transformation':'El analista asignó manualmente 2 puntos al acuerdo coordinado bajo costos adversos; sin fórmula automática.','status':'assumed'}]})
    comparison=studio.compare(left,right);assert comparison['comparable']
    report=studio.report(path,[left['id'],right['id']]);assert executive.replay(path,report['id'])['reproduced']
    content,info=continuity.snapshot(path);folder=path.parent/'demo-visual-recovery';restored,_=continuity.recover(content,folder)
    assert studio.read(restored,left['id'])==left;assert executive.replay(restored,report['id'])['reproduced']
    metadata.update(visual_network=net['id'],scenarios=[left['id'],right['id']],visual_report=report['id'],restoration_verified=True,comparison=comparison)
    path.with_suffix('.demo.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in metadata.items() if k!='comparison'},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('database',type=Path);build(p.parse_args().database.resolve())
