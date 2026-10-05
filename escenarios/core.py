"""Cálculos verificables para el caso ilustrativo de dos actores."""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Parameters:
    cooperation: float = 0.60
    cost: float = 3.0

    def __post_init__(self):
        if not isfinite(self.cooperation) or not 0 <= self.cooperation <= 1:
            raise ValueError('La cooperación debe estar entre 0 y 1.')
        if not isfinite(self.cost) or not 0 <= self.cost <= 6:
            raise ValueError('El costo debe estar entre 0 y 6.')


def analyze(p: Parameters) -> dict:
    a = [[6, -4], [8 - p.cost, -2 - p.cost]]
    b = [[6, 8], [-4, -2]]
    equilibria = [(i, j) for i in range(2) for j in range(2)
                  if a[i][j] >= max(a[r][j] for r in range(2))
                  and b[i][j] >= max(b[i][s] for s in range(2))]
    values = [row[0] * p.cooperation + row[1] * (1 - p.cooperation) for row in a]
    recommendation = 'Indiferente' if abs(values[0] - values[1]) < 1e-9 else ('Cooperar' if values[0] > values[1] else 'Competir')
    alternatives = []
    for name, q, cost in [('Base', p.cooperation, p.cost),
                         ('Mayor cooperación', min(1, p.cooperation + .2), p.cost),
                         ('Menor costo', p.cooperation, max(0, p.cost - 2))]:
        v = [10 * q - 4, 10 * q - 2 - cost]
        alternatives.append(dict(name=name, cooperation=q, cost=cost, values=v))
    return dict(parameters=dict(cooperation=p.cooperation, cost=p.cost), matrix_a=a, matrix_b=b,
                values=values, recommendation=recommendation, equilibria=equilibria,
                scenarios=alternatives, status='Ejemplo ilustrativo; no validado',
                assumptions=['Pagos hipotéticos en unidades de utilidad.',
                             'Cooperación de B fijada por el analista; no estimada con datos.',
                             'Dos estrategias por actor; una interacción simultánea.',
                             'La comparación supone el mismo comportamiento de B ante ambas estrategias de A.'])
