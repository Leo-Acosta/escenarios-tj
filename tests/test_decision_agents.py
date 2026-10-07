import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import closing
from escenarios import agents,decision_agents as d,local_ai
from test_agents import MODEL,payload


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'decisions.sqlite3'
        self.config={'model':copy.deepcopy(MODEL),'options':{'actor':0,'rounds':4,'seeds':[42,43],'baseline':'random','opponent':'mirror','noise':.3},'assumptions':'Caso sintético de prueba; no predicción real.','reviewed':True}

    def response(self,action=1):return {'done':True,'message':{'content':json.dumps({'action':action,'reason':'Alternativa permitida en la matriz.'})}}

    def test_invalid_action_never_executes_and_failed_request_is_logged(self):
        with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value=self.response(True)):
            with self.assertRaises(local_ai.AIError):d.choose(self.path,0,MODEL,[],42)
        with closing(d.connect(self.path)) as db:record=json.loads(db.execute('SELECT payload FROM decision_audits').fetchone()[0])
        self.assertEqual(record['state'],'rejected');self.assertTrue(record['error'])

    def test_interrupted_generation_is_not_recorded_as_accepted(self):
        with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):d.choose(self.path,0,MODEL,[],42)
        with closing(d.connect(self.path)) as db:record=json.loads(db.execute('SELECT payload FROM decision_audits').fetchone()[0])
        self.assertEqual(record['state'],'interrupted')
        self.assertNotIn('decision',record)

    def test_same_execution_perturbations_replay_without_ollama(self):
        with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value=self.response()) as request:
            record=d.compare(self.path,self.config)
        self.assertEqual(request.call_count,8)
        for trial in record['payload']['trials']:
            c=trial['candidate']['rounds'];b=trial['baseline']['rounds']
            self.assertEqual([[x!=y for x,y in zip(r['intended'],r['actions'])] for r in c],[[x!=y for x,y in zip(r['intended'],r['actions'])] for r in b])
            for index,trace in enumerate(trial['decisions']):
                self.assertEqual(trace['input']['completed_rounds'],index)
                self.assertEqual(trace['input']['round'],index+1)
                self.assertEqual(len(trace['input']['last_completed_rounds']),index)
        with patch('escenarios.local_ai.request',side_effect=AssertionError('No consultar IA al reproducir')):
            self.assertTrue(d.replay(self.path,record['id'])['reproduced'])
        self.assertFalse(record['payload']['promotion_allowed'])

    def test_provider_cannot_mutate_payoffs_or_simulation_history(self):
        p=payload(['fixed0','fixed1']);p['options']['policies'][0]='local_ai'
        def malicious(i,m,h):
            m['a'][0][1]=9999;h.clear();return 0,'Decisión válida.'
        result=agents.run(p,decision_provider=malicious)
        self.assertEqual(result['totals'][0],0)
        self.assertEqual(len(result['rounds']),3)
        self.assertEqual(p['model'],MODEL)

    def test_tampered_trace_or_recomputed_hash_does_not_replay(self):
        with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value=self.response()):record=d.compare(self.path,self.config)
        record['payload']['trials'][0]['decisions'][0]['input']['completed_rounds']=999
        record['sha256']=d.fingerprint(record['payload'])
        with closing(d.connect(self.path)) as db:db.execute('UPDATE decision_comparisons SET payload=? WHERE id=?',(json.dumps(record),record['id']));db.commit()
        with self.assertRaises(ValueError):d.replay(self.path,record['id'])

    def test_actor_b_utility_calculation_uses_own_columns(self):
        m=copy.deepcopy(MODEL);m['b']=[[0,5],[0,5]]
        self.assertEqual(d.context(1,m,[])['python_expected_utilities'],[0,5])

    def test_unreviewed_case_never_calls_ollama(self):
        with patch('escenarios.local_ai.request',side_effect=AssertionError('No generar')):
            with self.assertRaises(ValueError):d.compare(self.path,{**self.config,'reviewed':False})

    def test_optimizer_can_only_propose_unreviewed_experiment(self):
        state={'ready':True,'config':{'model':'mistral:latest'}}
        with patch('escenarios.local_ai.status',return_value=state),patch('escenarios.local_ai.request',return_value=self.response()):record=d.compare(self.path,self.config)
        recommendation={'next_step':'stress_test','opponent':'adaptive','reason':'Probar sensibilidad ante un rival diferente.'}
        with patch('escenarios.local_ai.status',return_value=state),patch('escenarios.local_ai.request',return_value={'done':True,'message':{'content':json.dumps(recommendation)}}):advice=d.optimize_process(self.path,record['id'])
        self.assertFalse(advice['auto_execution']);self.assertFalse(advice['promotion_allowed'])
        self.assertFalse(advice['experiment_draft']['reviewed'])
        self.assertFalse(set(advice['experiment_draft']['options']['seeds'])&set(self.config['options']['seeds']))
        with self.assertRaises(ValueError):d.compare(self.path,advice['experiment_draft'])

    def test_optimizer_rejects_unearned_promotion(self):
        state={'ready':True,'config':{'model':'mistral:latest'}}
        with patch('escenarios.local_ai.status',return_value=state),patch('escenarios.local_ai.request',return_value=self.response()):record=d.compare(self.path,self.config)
        with patch('escenarios.local_ai.status',return_value=state),patch('escenarios.local_ai.request',return_value={'done':True,'message':{'content':'{"next_step":"promote","opponent":"fixed0","reason":"Supuesto éxito"}'}}):
            with self.assertRaises(local_ai.AIError):d.optimize_process(self.path,record['id'])
