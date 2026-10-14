"""Demostración ficticia reproducible; crea una base separada y nunca usa EDESUR."""
import argparse,json
from pathlib import Path
from escenarios import workflow,laboratories,sequential,simulation,graph,executive,agents,comparisons

TITLE='Puerto Aurora · resiliencia energética · CASO FICTICIO'
ASSUMPTIONS='DATOS SINTÉTICOS. Utilidades cardinales hipotéticas en la escala propia de cada actor, no pesos ni pérdidas monetarias. Horizonte 90 días. Sin evidencia real ni inferencia IA. Matriz simultánea y árbol secuencial representan decisiones distintas.'
MODEL={'title':TITLE,'actors':['Municipio Aurora','Operador Delta'],'strategies':[['Cofinanciar reserva','Postergar inversión'],['Invertir con auditoría','Operar al mínimo']],'a':[[8,-2],[5,1]],'b':[[7,4],[2,3]],'p':.6,'q':.55}

def build(path):
    if path.exists():raise ValueError('La base de destino ya existe; elegí una nueva para conservar todas las versiones.')
    case=workflow.operate(path,{'action':'create','title':TITLE,'description':'Ciudad ficticia con puerto, hospital y reserva energética. Comparar inversión coordinada frente a una crisis de suministro.'})
    answers=['Evaluar un acuerdo de inversión y continuidad de servicios esenciales.','90 días; una negociación inicial y 60 rondas hipotéticas de ejecución.','Todos los actores, incidentes, pagos y relaciones son ficticios. No se utilizan datos EDESUR.',ASSUMPTIONS,'Probabilidades 60% y 55% son supuestos exploratorios, no frecuencias observadas.']
    for answer in answers:case=workflow.operate(path,{'action':'message','id':case['id'],'revision':case['revision'],'text':answer})
    case=workflow.operate(path,{'action':'calculate','id':case['id'],'revision':case['revision'],'model':MODEL,'evidence':[],'assumptions':ASSUMPTIONS,'reviewed':True})
    options={'agents':{'rounds':60,'seed':20261014,'noise':.12,'policies':['mirror','adaptive']},'comparison':{'rounds':60,'seed':20261014,'noise':.12,'repetitions':8},'sweep':{'actor':'a','row':0,'column':0,'minimum':-6,'maximum':12}}
    refs=[]
    for kind,config in options.items():
        record=laboratories.save_from_version(path,{'kind':kind,'workflow_id':case['id'],'version':1,'options':config,'assumptions':ASSUMPTIONS,'reviewed':True})
        refs.append({'kind':kind,'id':record['id']})
        if kind=='agents':assert agents.run({'model':MODEL,'options':config,'assumptions':ASSUMPTIONS})['totals']==record['totals']
        if kind=='comparison':assert comparisons.compare({'model':MODEL,'options':config,'assumptions':ASSUMPTIONS})['cells']==record['cells']
    trees=[]
    for label,payoffs in [('Crisis de costos',[[[2,1],[-3,4]],[[1,2],[-5,-2]]]),('Acuerdo protegido',[[[9,8],[2,3]],[[3,2],[-4,-3]]]),('Escenario base',[[[8,7],[1,5]],[[3,1],[-4,-3]]])]:
        model={'title':'Aurora · '+label+' · FICTICIO','actors':MODEL['actors'],'actions':[['Proponer acuerdo','Postergar'],['Aceptar con auditoría','Rechazar acuerdo'],['Invertir por cuenta propia','Operar al mínimo']],'payoffs':payoffs,'assumptions':ASSUMPTIONS+' Variante: '+label+'. Información perfecta; cada actor conoce los pagos.'}
        tree=sequential.analyze(model);tree['simulation']=simulation.simulate(model,{'iterations':2500,'seed':20261014,'radius':3})
        assert tree['simulation']==simulation.simulate(model,tree['simulation']['options'])
        trees.append(sequential.save(path,tree,case['id']))
    refs.extend({'kind':'tree','id':t['id']} for t in trees)
    names=[('Municipio Aurora',0),('Operador Delta',0),('Hospital Central',1),('Puerto comercial',1),('Cooperativa vecinal',0),('Consejo de control',0),('Reserva de baterías',1),('Red de distribución',1),('Fondo de inversión',1),('Informe de auditoría',2),('Indicador de cortes',2),('Registro de demanda',2),('Plan de contingencia',2),('Escenario base',2),('Crisis de costos',2),('Acuerdo protegido',2),('Prioridad sanitaria',2),('Restricción presupuestaria',2)]
    links=[(0,1,'Cooperación'),(0,8,'Participación'),(1,7,'Participación'),(8,6,'Influencia'),(6,7,'Influencia'),(7,2,'Influencia'),(7,3,'Influencia'),(4,0,'Influencia'),(5,9,'Participación'),(9,1,'Influencia'),(10,5,'Influencia'),(11,6,'Influencia'),(12,2,'Influencia'),(12,3,'Influencia'),(2,16,'Participación'),(16,0,'Influencia'),(17,8,'Influencia'),(8,0,'Influencia'),(13,10,'Participación'),(14,17,'Participación'),(15,9,'Participación'),(4,11,'Participación'),(1,12,'Cooperación'),(0,5,'Cooperación'),(6,15,'Participación'),(7,14,'Participación')]
    network=graph.save_version(path,{'title':'Aurora · mapa analítico ficticio','assumptions':ASSUMPTIONS+' Conexiones cualitativas declaradas; no causalidad estimada ni dinámica física.','workflow_id':case['id'],'reviewed':True,'graph':{'nodes':[{'id':i,'name':name,'type':kind} for i,(name,kind) in enumerate(names)],'edges':[{'a':a,'b':b,'type':kind,'evidence':{'source':'Diseño sintético de la demostración','reference':'Relación conceptual '+str(i+1),'note':'Vínculo hipotético para explorar dependencias; sin documento real ni peso causal.'}} for i,(a,b,kind) in enumerate(links)]}})
    report=executive.create(path,{'workflow_id':case['id'],'version':1,'title':'Puerto Aurora · demostración estratégica','sections':['matrix','agents','comparison','sweep','tree','simulation'],'references':refs,'executive_note':'Explorar cómo cambian las decisiones cuando varían costos, incentivos y respuestas. El acuerdo protegido y la crisis no son pronósticos: son alternativas sintéticas. La red es cualitativa y no ejecuta automáticamente el modelo.','pending':'No hay observaciones reales ni evaluación predictiva. Agentes de políticas Python, sin Ollama. Árbol de dos etapas y matriz 2×2.','evidence_mode':'synthetic','reviewed':True})
    assert executive.replay(path,report['id'])['reproduced']
    result={'synthetic':True,'title':TITLE,'workflow_id':case['id'],'matrix_version':1,'trees':len(trees),'iterations_per_tree':2500,'comparison_seeds':8,'network_nodes':len(names),'network_edges':len(links),'report_id':report['id'],'reproducibility_verified':True,'llm_inference':False}
    path.with_suffix('.demo.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('database',type=Path);build(parser.parse_args().database.resolve())

