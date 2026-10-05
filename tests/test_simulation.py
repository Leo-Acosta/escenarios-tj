import copy
import unittest
from test_sequential import MODEL
from escenarios.simulation import simulate

class SimulationTests(unittest.TestCase):
    def test_zero_uncertainty_matches_base_solution(self):
        r=simulate(MODEL,{'iterations':100,'seed':42,'radius':0})
        self.assertEqual(r['decision_counts'],[100,0,0]);self.assertEqual(r['route_counts'],[[0,100],[0,0]])
        self.assertEqual(r['utility_a']['lower_p05'],2)
    def test_seed_reproduces_every_result(self):
        options={'iterations':100,'seed':9,'radius':3}
        r=simulate(MODEL,options)
        self.assertEqual(r,simulate(MODEL,options));self.assertEqual(sum(r['decision_counts']),100)
        self.assertEqual(len(r['preview']),20)
        self.assertNotEqual(r['preview'],simulate(MODEL,{**options,'seed':10})['preview'])
        for sample in r['preview']:
            for i in range(2):
                for j in range(2):
                    for k in range(2):self.assertLessEqual(abs(sample['payoffs'][i][j][k]-MODEL['payoffs'][i][j][k]),3)
    def test_ties_are_ambiguous_without_arbitrary_selection(self):
        m=copy.deepcopy(MODEL);m['payoffs']=[[[0,0],[0,0]],[[0,0],[0,0]]]
        r=simulate(m,{'iterations':100,'seed':0,'radius':0})
        self.assertEqual(r['decision_counts'],[0,0,100]);self.assertEqual(r['route_counts'],[[100,100],[100,100]])
    def test_invalid_configuration_is_rejected(self):
        base={'iterations':100,'seed':42,'radius':2}
        for key,value in [('iterations',99),('iterations',5001),('iterations',True),('seed',-1),('radius',float('nan')),('radius',-1),('radius',1000000)]:
            with self.assertRaises(ValueError):simulate(MODEL,{**base,key:value})
