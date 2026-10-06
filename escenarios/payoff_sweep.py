"""Barrido determinista de un pago, conservando los demás supuestos."""
import copy
import math
from .case_model import validate, analyze_case

def run(payload):
    model=validate(payload['model']);o=payload['options']
    key=o.get('actor');i=o.get('row');j=o.get('column');lo=o.get('minimum');hi=o.get('maximum')
    if key not in ('a','b') or type(i) is not int or type(j) is not int or i not in (0,1) or j not in (0,1):
        raise ValueError('Seleccioná un pago válido.')
    if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1000000 for v in (lo,hi)) or lo>=hi:
        raise ValueError('El rango debe ser finito y creciente, dentro de ±1.000.000.')
    points=[];changes=[];previous=None
    for index in range(101):
        value=lo+(hi-lo)*index/100;candidate=copy.deepcopy(model);candidate[key][i][j]=value
        r=analyze_case(candidate)
        best_b=[k for k,v in enumerate(r['values_b']) if math.isclose(v,max(r['values_b']),rel_tol=1e-12,abs_tol=1e-9)]
        point={'value':value,'pure':r['pure'],'mixed':r['mixed'],'best_a':r['best_a'],'best_b':best_b,'values_a':r['values_a'],'values_b':r['values_b']}
        signature=(r['pure'],r['best_a'],best_b,r['mixed'] is not None)
        if previous is not None and signature!=previous:
            changes.append({'from':points[-1]['value'],'to':value,'index':index})
        previous=signature;points.append(point)
    return {'model':model,'options':{'actor':key,'row':i,'column':j,'minimum':lo,'maximum':hi},'points':points,'changes':changes,
            'limits':['Se varía un único pago; los demás pagos y p/q permanecen constantes.',
                      'Los cambios se localizan entre muestras consecutivas: no son umbrales exactos y pueden existir cambios dentro del intervalo.',
                      'Los equilibrios son soluciones del modelo; p/q son supuestos del analista, no probabilidades pronosticadas.',
                      'No se enumeran familias de equilibrios mixtos degenerados.']}
