import copy
import unittest
from test_comparisons import MODEL
from escenarios.payoff_sweep import run

def payload():return {'model':copy.deepcopy(MODEL),'options':{'actor':'a','row':0,'column':1,'minimum':0,'maximum':2}}

class SweepTests(unittest.TestCase):
    def test_equilibrium_changes_and_tie_are_preserved(self):
        p=payload();before=copy.deepcopy(p);r=run(p)
        self.assertEqual(p,before);self.assertEqual(len(r['points']),101)
        self.assertEqual(r['points'][0]['pure'],[[1,1]])
        self.assertEqual(r['points'][50]['pure'],[[0,1],[1,1]])
        self.assertEqual(r['points'][-1]['pure'],[[0,1]])
        self.assertEqual(len(r['changes']),2)
    def test_b_utility_uses_correct_column(self):
        p=payload();p['options'].update(actor='b',row=1,column=0)
        r=run(p);self.assertEqual(r['points'][0]['values_b'][0],1.5)
        self.assertEqual(r['points'][-1]['values_b'][0],2.5)
    def test_invalid_bounds_and_indices(self):
        for key,value in [('minimum',float('nan')),('maximum',0),('row',True),('actor','other'),('column',2),('maximum',1000001)]:
            p=payload();p['options'][key]=value
            with self.assertRaises(ValueError):run(p)
