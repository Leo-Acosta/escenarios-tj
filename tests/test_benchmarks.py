import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from escenarios import decision_agents as d,ai_jobs,local_ai
from test_laboratories import prepare_case,MODEL
from test_decision_jobs import ImmediateThread

class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'bench.sqlite3';self.case=prepare_case(self.path)
        self.options={'actor':0,'rounds':1,'seeds':[42],'baseline':'fixed0','opponent':'fixed0','noise':0}
        self.payload={'model':MODEL,'conditions':[self.options,{**self.options,'baseline':'fixed1'},self.options|{'opponent':'fixed1'},self.options|{'baseline':'mirror'}],'assumptions':'Prueba sintética.','reviewed':True}
    def test_all_wins_ties_losses_and_failures_conserved_and_replayed(self):
        responses=[{'done':True,'message':{'content':'{"action":1,"reason":"Ensayo."}'}},
            {'done':True,'message':{'content':'{"action":1,"reason":"Ensayo."}'}},
            {'done':True,'message':{'content':'{"action":0,"reason":"Ensayo."}'}},
            {'done':True,'message':{'content':'{"action":99,"reason":"Inválida."}'}}]
        source={'id':self.case['id'],'version':1,'title':MODEL['title']}
        with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',side_effect=responses):record=d.benchmark(self.path,self.payload,source)
        # Bajo rival fijo 1, A coopera: ambos pagos 0; introducir referencia fija 2 produce pérdida.
        self.assertEqual(record['payload']['summary'],{'win':1,'tie':2,'loss':0,'failure':1})
        self.assertEqual(record['payload']['trials'][-1]['failure_trace']['state'],'rejected')
        with patch('escenarios.local_ai.request',side_effect=AssertionError('Sin inferencia')):self.assertTrue(d.benchmark_record(self.path,record['id'],True)['reproduced'])
    def test_loss_is_not_hidden_and_jobs_bind_frozen_matrix(self):
        payload={**self.payload,'conditions':[{**self.options,'baseline':'fixed1'}]}
        with patch('escenarios.ai_jobs.threading.Thread',ImmediateThread),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value={'done':True,'message':{'content':'{"action":0,"reason":"Decisión de prueba."}'}}):
            job=ai_jobs.start_benchmark(self.path,{**payload,'workflow_id':self.case['id'],'version':1,'model':{**MODEL,'a':[[999,999],[999,999]]}})
        self.assertEqual(job['result']['payload']['summary']['loss'],1)
        self.assertEqual(job['result']['payload']['model'],MODEL);self.assertEqual(job['workflow_id'],'benchmarks:'+self.case['id'])
    def test_bounded_plan_rejects_duplicate_conditions_and_excess_cost(self):
        with self.assertRaises(ValueError):d.benchmark_prepare({**self.payload,'conditions':[self.options,self.options]})
        with self.assertRaises(ValueError):d.benchmark_prepare({**self.payload,'conditions':[{**self.options,'rounds':20,'seeds':[1,2,3,4,5]},{**self.options,'rounds':20,'seeds':[1,2,3,4,5],'noise':.1}]})
