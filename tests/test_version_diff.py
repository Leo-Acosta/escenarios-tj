import copy
import tempfile
import unittest
from pathlib import Path
from escenarios.case_model import analyze_case,save_case
from escenarios.version_diff import compare
from test_comparisons import MODEL

class VersionDiffTests(unittest.TestCase):
    def prepare(self,path):
        a=save_case(path,analyze_case(MODEL));m=copy.deepcopy(MODEL);m['a'][0][1]=2;m['q']=.1
        b=save_case(path,analyze_case(m))
        return {'baseline':{'type':'case','id':str(a)},'candidate':{'type':'case','id':str(b)},'comparable_scales':True}
    def test_deltas_equilibria_and_decomposition(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'db';p=self.prepare(path);r=compare(path,p)
            self.assertEqual(r['cells'][0]['delta'],2)
            self.assertEqual(r['gained'],[[0,1]]);self.assertEqual(r['lost'],[[1,1]])
            for effect in r['effects']:self.assertAlmostEqual(effect['delta'],effect['payment_effect']+effect['probability_effect'])
            self.assertAlmostEqual(r['effects'][0]['payment_effect'],1)
            self.assertAlmostEqual(r['effects'][0]['probability_effect'],-.4)
    def test_scales_and_same_version_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'db';p=self.prepare(path);p['comparable_scales']=False
            with self.assertRaises(ValueError):compare(path,p)
            p['comparable_scales']=True;p['candidate']=p['baseline']
            with self.assertRaises(ValueError):compare(path,p)
    def test_incompatible_labels_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'db';p=self.prepare(path);m=copy.deepcopy(MODEL);m['actors'][0]='Otro actor'
            p['candidate']['id']=str(save_case(path,analyze_case(m)))
            with self.assertRaises(ValueError):compare(path,p)
