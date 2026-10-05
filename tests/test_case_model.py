import unittest
from escenarios.case_model import analyze_case


def model(a,b):
    return {'title':'Caso','actors':['A','B'],'strategies':[['C','D'],['C','D']],'a':a,'b':b,'p':.5,'q':.6}


class CaseModelTests(unittest.TestCase):
    def test_prisoners_dilemma(self):
        r=analyze_case(model([[3,0],[5,1]],[[3,5],[0,1]]))
        self.assertEqual(r['pure'],[[1,1]])
        self.assertIsNone(r['mixed'])
        self.assertEqual(r['best_a'],[1])

    def test_matching_pennies(self):
        r=analyze_case(model([[1,-1],[-1,1]],[[-1,1],[1,-1]]))
        self.assertEqual(r['pure'],[])
        self.assertEqual(r['mixed'],{'p':.5,'q':.5})

    def test_coordination(self):
        r=analyze_case(model([[2,0],[0,2]],[[2,0],[0,2]]))
        self.assertEqual(r['pure'],[[0,0],[1,1]])
        self.assertEqual(r['mixed'],{'p':.5,'q':.5})

    def test_invalid_inputs(self):
        m=model([[2,0],[0,2]],[[2,0],[0,2]])
        for key,value in [('q',float('nan')),('a',[[1,2,3],[1,2]]),('actors',['A','A'])]:
            invalid={**m,key:value}
            with self.assertRaises(ValueError):analyze_case(invalid)

    def test_sensitivity_transition(self):
        r=analyze_case(model([[4,0],[0,2]],[[2,0],[0,2]]))
        s=r['sensitivity']
        self.assertAlmostEqual(s['threshold'],1/3)
        self.assertEqual(s['points'][0]['best'],[1])
        self.assertEqual(s['points'][-1]['best'],[0])
        self.assertEqual(len(s['points']),101)

    def test_sensitivity_tie_and_dominance(self):
        tied=analyze_case(model([[2,3],[2,3]],[[2,0],[0,2]]))['sensitivity']
        self.assertTrue(tied['always_tied'])
        self.assertEqual(tied['points'][50]['best'],[0,1])
        dominated=analyze_case(model([[3,4],[1,2]],[[2,0],[0,2]]))['sensitivity']
        self.assertIsNone(dominated['threshold'])
        self.assertFalse(dominated['always_tied'])

    def test_sensitivity_boundary(self):
        r=analyze_case(model([[4,2],[0,2]],[[2,0],[0,2]]))
        self.assertEqual(r['sensitivity']['threshold'],0)
        self.assertEqual(r['sensitivity']['points'][0]['best'],[0,1])
