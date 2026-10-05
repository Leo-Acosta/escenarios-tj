import copy
import tempfile
import unittest
from pathlib import Path
from escenarios.agents import run,save,history

MODEL={'title':'Prueba','actors':['A','B'],'strategies':[['Cooperar','Competir'],['Cooperar','Competir']],
       'a':[[3,0],[5,1]],'b':[[3,5],[0,1]],'p':.5,'q':.5}

def payload(policies=None):return {'model':copy.deepcopy(MODEL),'options':{'rounds':3,'seed':42,'noise':0,'policies':policies or ['mirror','fixed1']},'assumptions':'Hipotéticos'}

class AgentTests(unittest.TestCase):
    def test_memory_uses_only_completed_rounds(self):
        r=run(payload())
        self.assertEqual([x['actions'] for x in r['rounds']],[[0,1],[1,1],[1,1]])
        self.assertEqual(r['rounds'][0]['memory'][0]['opponent_counts'],[0,0])
        self.assertEqual(r['rounds'][1]['memory'][0]['opponent_counts'],[0,1])
        self.assertEqual(r['totals'],[2,7]);self.assertEqual(r['action_counts'],[[1,2],[0,3]])
    def test_trigger_keeps_memory_after_rival_returns_to_first_action(self):
        from escenarios.agents import choose
        import random
        action,_=choose('trigger',0,MODEL,[{'actions':[0,1]},{'actions':[1,0]}],random.Random(0))
        self.assertEqual(action,1)
    def test_adaptive_b_uses_columns_of_own_payoff_matrix(self):
        p=payload(['adaptive','adaptive']);p['model']['b']=[[0,5],[0,5]]
        r=run(p);self.assertEqual(r['rounds'][0]['intended'],[1,1])
    def test_execution_error_is_observed_in_next_round(self):
        p=payload(['fixed0','mirror']);p['options']['noise']=1
        r=run(p);self.assertEqual(r['rounds'][0]['intended'],[0,0]);self.assertEqual(r['rounds'][0]['actions'],[1,1])
        self.assertEqual(r['rounds'][1]['intended'],[0,1])
    def test_random_seed_reproduces_trace_without_mutating_input(self):
        p=payload(['random','random']);p['options']['rounds']=30;p['options']['noise']=.2;original=copy.deepcopy(p)
        self.assertEqual(run(p)['rounds'],run(p)['rounds']);self.assertEqual(p,original)
        q=copy.deepcopy(p);q['options']['seed']=43;self.assertNotEqual(run(p)['rounds'],run(q)['rounds'])
    def test_invalid_options_are_rejected(self):
        for key,val in [('rounds',501),('rounds',True),('noise',float('nan')),('noise',-1),('seed',-1),('policies',['unknown','mirror'])]:
            p=payload();p['options'][key]=val
            with self.assertRaises(ValueError):run(p)
    def test_saved_run_is_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'db.sqlite3';r=run(payload());saved=save(path,r);r['model']['title']='Cambio'
            self.assertEqual(history(path)[0]['model']['title'],'Prueba');self.assertEqual(history(path)[0]['id'],saved['id'])
