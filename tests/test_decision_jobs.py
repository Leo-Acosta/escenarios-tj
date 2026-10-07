import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from escenarios import ai_jobs,decision_agents,local_ai
from escenarios.workflow import get_workflow,NotFound,Conflict
from test_laboratories import prepare_case,MODEL

class ImmediateThread:
    def __init__(self,target,args,daemon):self.target=target;self.args=args
    def start(self):self.target(*self.args)

class DecisionJobTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'case.sqlite3';self.case=prepare_case(self.path)
        self.payload={'workflow_id':self.case['id'],'version':1,'options':{'actor':0,'rounds':1,'seeds':[42],'baseline':'fixed0','opponent':'fixed0','noise':0},'assumptions':'Ensayo sintético.','reviewed':True}
        ai_jobs.RUNNING=False
        self.addCleanup(setattr,ai_jobs,'RUNNING',False)

    def start(self):
        response={'done':True,'message':{'content':'{"action":1,"reason":"Alternativa de prueba."}'}}
        with patch('escenarios.ai_jobs.threading.Thread',ImmediateThread),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value=response):
            return ai_jobs.start_decision(self.path,{**self.payload,'model':{**MODEL,'a':[[999,999],[999,999]]}})

    def test_frozen_source_registered_and_replayed_without_model_request(self):
        job=self.start();saved=ai_jobs.get_job(self.path,job['id'])
        self.assertEqual(saved['state'],'ready');self.assertEqual(saved['result']['payload']['model'],MODEL)
        self.assertEqual(saved['base_version'],1);self.assertEqual(saved['workflow_id'],'decisions:'+self.case['id'])
        self.assertEqual(ai_jobs.list_jobs(self.path,saved['workflow_id']),[saved])
        self.assertEqual(get_workflow(self.path,self.case['id']),self.case)
        with patch('escenarios.local_ai.request',side_effect=AssertionError('No consultar IA')):
            self.assertTrue(decision_agents.replay(self.path,saved['result']['id'])['reproduced'])
        self.assertEqual(decision_agents.get_record(self.path,saved['result']['id']),saved['result'])

    def test_review_and_version_required_before_generation(self):
        with patch('escenarios.local_ai.request',side_effect=AssertionError('No consultar IA')):
            with self.assertRaises(ValueError):ai_jobs.start_decision(self.path,{**self.payload,'reviewed':False})
            with self.assertRaises(NotFound):ai_jobs.start_decision(self.path,{**self.payload,'version':2})
            with self.assertRaises(ValueError):ai_jobs.start_decision(self.path,{**self.payload,'version':True})
        self.assertFalse(ai_jobs.RUNNING)

    def test_optimizer_requires_finished_comparison_and_preserves_source(self):
        job=self.start()
        response={'done':True,'message':{'content':json.dumps({'next_step':'stress_test','opponent':'mirror','reason':'Evaluar otra memoria.'})}}
        with patch('escenarios.ai_jobs.threading.Thread',ImmediateThread),patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value=response):
            advice=ai_jobs.start_decision_optimizer(self.path,{'job_id':job['id']})
        saved=ai_jobs.get_job(self.path,advice['id']);self.assertEqual(saved['state'],'ready')
        self.assertEqual(saved['input_snapshot']['source_job_id'],job['id'])
        self.assertEqual(saved['result']['source_comparison'],job['result']['id'])
        self.assertFalse(saved['result']['experiment_draft']['reviewed'])
        with self.assertRaises(ValueError):ai_jobs.start_decision_optimizer(self.path,{'job_id':advice['id']})
        self.assertEqual(get_workflow(self.path,self.case['id']),self.case)

    def test_failed_decision_persists_and_releases_shared_lock(self):
        with patch('escenarios.ai_jobs.threading.Thread',ImmediateThread),patch('escenarios.decision_agents.choose',side_effect=local_ai.AIError('Respuesta inválida.')):
            job=ai_jobs.start_decision(self.path,self.payload)
        self.assertEqual(ai_jobs.get_job(self.path,job['id'])['state'],'failed');self.assertFalse(ai_jobs.RUNNING)
        self.assertEqual(get_workflow(self.path,self.case['id']),self.case)
        ai_jobs.RUNNING=True
        with self.assertRaises(Conflict):ai_jobs.start_decision(self.path,self.payload)
