"""Sensibilidad Monte Carlo de pagos, sin selección arbitraria de empates."""
import random
import math
from .sequential import analyze


def simulate(model,options):
    base=analyze(model)['model']
    if not isinstance(options,dict):raise ValueError('Configuración de simulación inválida.')
    n=options.get('iterations');seed=options.get('seed');radius=options.get('radius')
    if type(n) is not int or not 100<=n<=5000:raise ValueError('Usá entre 100 y 5000 repeticiones.')
    if type(seed) is not int or not 0<=seed<=4294967295:raise ValueError('Semilla entera entre 0 y 4294967295.')
    if type(radius) not in (int,float) or not math.isfinite(radius) or radius<0 or any(abs(p)+radius>1e6 for row in base['payoffs'] for pair in row for p in pair):raise ValueError('Revisá la amplitud: los intervalos deben estar dentro de ±1000000.')
    rng=random.Random(seed);counts=[0,0,0];routes=[[0,0],[0,0]];lower=[];upper=[];preview=[]
    for index in range(n):
        matrix=[[[rng.uniform(p-radius,p+radius) if radius else p for p in pair] for pair in row] for row in base['payoffs']]
        equilibria=analyze({**base,'payoffs':matrix})['equilibria']
        choices={e['first'] for e in equilibria};counts[next(iter(choices)) if len(choices)==1 else 2]+=1
        for i,j in {tuple(e['outcome']) for e in equilibria}:routes[i][j]+=1
        utilities=[e['payoffs'][0] for e in equilibria];lower.append(min(utilities));upper.append(max(utilities))
        if index<20:preview.append({'iteration':index+1,'payoffs':matrix,'outcomes':[list(x) for x in sorted({tuple(e['outcome']) for e in equilibria})]})
    def quantile(values,q):
        values=sorted(values);position=(len(values)-1)*q;left=int(position);fraction=position-left
        return values[left]*(1-fraction)+values[min(left+1,len(values)-1)]*fraction
    return {'version':'uniform-independent-v1','options':{'iterations':n,'seed':seed,'radius':radius},
        'decision_counts':counts,'decision_frequencies':[c/n for c in counts],
        'route_counts':routes,'utility_a':{'lower_p05':quantile(lower,.05),'upper_p95':quantile(upper,.95),
            'lower_mean':sum(lower)/n,'upper_mean':sum(upper)/n},'preview':preview,
        'assumptions':['Cada uno de los ocho pagos varía independientemente con distribución uniforme, valor base ± amplitud.',
          'Los actores conocen los pagos de cada escenario antes de decidir; se vuelve a resolver el árbol completo.',
          'Los empates conservan todos los equilibrios; una repetición cuenta como ambigua si permite ambas decisiones de A.',
          'Frecuencias condicionadas a supuestos exploratorios. No son probabilidades empíricas ni predicciones validadas.',
          'P5/P95 resumen utilidades de equilibrio simuladas, no intervalos de confianza ni pagos de una política fija.']}
