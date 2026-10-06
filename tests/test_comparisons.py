import copy
import tempfile
import unittest
from pathlib import Path
from escenarios import comparisons, agents

MODEL={'title':'Prueba','actors':['A','B'],'strategies':[['Cooperar','Competir'],['Cooperar','Competir']],
       'a':[[3,0],[5,1]],'b':[[3,5],[0,1]],'p':.5,'q':.5}

def payload():
    return {'model':copy.deepcopy(MODEL),'options':{'rounds':5,'repetitions':3,'seed':42,'noise':.2},'assumptions':'Pagos hipotéticos'}

class ComparisonTests(unittest.TestCase):
    def test_all_pairs_match_individual_runs(self):
        p=payload();original=copy.deepcopy(p);r=comparisons.compare(p)
        self.assertEqual(len(r['cells']),36);self.assertEqual(p,original)
        for c in r['cells']:
            for t,seed in enumerate(r['seeds']):
                expected=agents.run({'model':p['model'],'options':{'rounds':5,'seed':seed,'noise':.2,'policies':c['policies']},'assumptions':p['assumptions']})
                self.assertEqual(c['trial_means'][t],expected['means'])

    def test_fixed_payoffs_and_single_trial_dispersion(self):
        p=payload();p['options'].update(noise=0,repetitions=1);r=comparisons.compare(p)
        self.assertEqual(r['cells'][1]['trial_means'],[[0,5]])
        self.assertEqual(r['cells'][1]['statistics'][1],{'mean':5,'std':0,'min':5,'max':5})

    def test_invalid_bounds(self):
        for key,value in [('rounds',101),('repetitions',0),('repetitions',True),('seed',4294967295),('noise',float('nan'))]:
            p=payload();p['options'][key]=value
            with self.assertRaises(ValueError):comparisons.compare(p)

    def test_saved_replay_uses_original_matrix(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'db.sqlite3';r=comparisons.compare(payload());saved=comparisons.save(path,r)
            r['model']['a'][0][0]=999
            replay=comparisons.replay(path,{'id':saved['id'],'i':5,'j':4,'trial':2})
            self.assertEqual(replay['means'],saved['cells'][34]['trial_means'][2])
            self.assertEqual(replay['model']['a'][0][0],3)
            self.assertEqual(comparisons.history(path)[0]['id'],saved['id'])
            with self.assertRaises(ValueError):comparisons.replay(path,{'id':saved['id'],'i':True,'j':0,'trial':0})
            with self.assertRaises(KeyError):comparisons.replay(path,{'id':'missing','i':0,'j':0,'trial':0})
