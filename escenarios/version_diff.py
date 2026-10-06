"""Contraste de dos matrices conservadas con identidad de estrategias."""
import copy
from . import library
from .case_model import analyze_case

def compare(path,payload):
    refs=[payload['baseline'],payload['candidate']]
    if any(r['type'] not in ('case','workflow') for r in refs):raise ValueError('Elegí matrices libres o versiones de expediente.')
    if refs[0]==refs[1]:raise ValueError('Seleccioná dos versiones distintas.')
    if payload.get('comparable_scales') is not True:raise ValueError('Confirmá que las escalas de pagos son comparables entre versiones.')
    records=[library.get_record(path,r['type'],r['id']) for r in refs]
    models=[r['record']['model'] for r in records];old,new=models
    if old['actors']!=new['actors'] or old['strategies']!=new['strategies']:
        raise ValueError('Los actores y estrategias deben coincidir en nombre y posición para comparar pagos.')
    analyses=[analyze_case(m) for m in models]
    frozen=copy.deepcopy(new);frozen['p']=old['p'];frozen['q']=old['q'];middle=analyze_case(frozen)
    cells=[{'actor':key,'row':i,'column':j,'before':old[key][i][j],'after':new[key][i][j],'delta':new[key][i][j]-old[key][i][j]}
           for key in ('a','b') for i in range(2) for j in range(2) if old[key][i][j]!=new[key][i][j]]
    effects=[]
    for actor,key in enumerate(('values_a','values_b')):
        for strategy in range(2):
            before=analyses[0][key][strategy];after=analyses[1][key][strategy];intermediate=middle[key][strategy]
            effects.append({'actor':actor,'strategy':strategy,'before':before,'after':after,'delta':after-before,
                           'payment_effect':intermediate-before,'probability_effect':after-intermediate})
    before_pure=analyses[0]['pure'];after_pure=analyses[1]['pure']
    def assumptions(row):return row['record'].get('context',{}).get('assumptions','')
    return {'baseline':{k:v for k,v in records[0].items() if k!='record'},'candidate':{k:v for k,v in records[1].items() if k!='record'},
            'model_before':old,'model_after':new,'cells':cells,'effects':effects,
            'probabilities':[{'key':k,'before':old[k],'after':new[k],'delta':new[k]-old[k]} for k in ('p','q')],
            'pure_before':before_pure,'pure_after':after_pure,'gained':[e for e in after_pure if e not in before_pure],
            'lost':[e for e in before_pure if e not in after_pure],'mixed_before':analyses[0]['mixed'],'mixed_after':analyses[1]['mixed'],
            'assumptions_before':assumptions(records[0]),'assumptions_after':assumptions(records[1]),
            'limits':['Comparación condicionada a nombres, posiciones y escalas equivalentes, confirmadas por el analista.',
                      'La descomposición cambia primero pagos con p/q iniciales y después p/q con pagos nuevos; otro orden puede cambiar la atribución.',
                      'Las diferencias son aritméticas del modelo, no efectos causales ni predicciones validadas.',
                      'El contraste se calcula al consultar y no crea una nueva versión guardada.']}
