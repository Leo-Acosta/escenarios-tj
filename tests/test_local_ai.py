import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from escenarios import local_ai,ai_jobs
from escenarios.workflow import operate,Conflict,QUESTIONS


def proposal():
    return {'summary':'Borrador de negociación para revisar.','actors':['Municipio','Vecinos'],
        'strategies':[['Acordar','Postergar'],['Apoyar','Objetar']],
        'variables':[{'name':'Presupuesto','reason':'Dato pendiente de confirmar.'}],
        'questions':['¿Qué presupuesto existe?'],'assumptions':['Hipótesis pendiente de revisión.'],
        'limitations':['No hay predicción validada.']}


class LocalAITests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'local.sqlite3'

    def test_configuration_allows_only_reviewed_model(self):
        self.assertFalse(local_ai.config(self.path)['enabled'])
        saved=local_ai.save_config(self.path,{'enabled':True,'model':'mistral:latest'})
        self.assertEqual(saved,local_ai.config(self.path))
        for name in ['qwen3:8b','unknown','mistral:cloud']:
            with self.assertRaises(local_ai.AIError):local_ai.save_config(self.path,{'enabled':True,'model':name})

    def test_unavailable_engine_preserves_guided_mode(self):
        with patch('escenarios.local_ai.request',side_effect=local_ai.AIError('Desconectado')):
            state=local_ai.status(self.path)
        self.assertFalse(state['ready']);self.assertFalse(state['connected'])

    def test_digest_change_requires_review(self):
        local_ai.save_config(self.path,{'enabled':True,'model':'mistral:latest'})
        with patch('escenarios.local_ai.request',return_value={'models':[{'name':'mistral:latest','digest':'changed'}]}):
            self.assertFalse(local_ai.status(self.path)['ready'])

    def test_proposal_rejects_numbers_as_new_fields(self):
        self.assertEqual(local_ai.validate_proposal(proposal()),proposal())
        for key in ['payments','probability','code']:
            with self.assertRaises(local_ai.AIError):local_ai.validate_proposal({**proposal(),key:123})
        bad=proposal();bad['actors']=['Only one']
        with self.assertRaises(local_ai.AIError):local_ai.validate_proposal(bad)

    def create(self):
        return operate(self.path,{'action':'create','title':'Prueba IA','description':'El Municipio negocia con los Vecinos.'})

    def job(self,d):
        value={'id':'job-test','workflow_id':d['id'],'base_revision':d['revision'],'state':'ready','created_at':'2026-10-05',
               'result':{'proposal':proposal(),'metadata':{'model':'mistral:latest','digest':local_ai.CATALOG['mistral:latest']['digest'],
                       'publisher':'Mistral AI','license':'Apache-2.0'}},'error':None}
        ai_jobs.store(self.path,value)
        return value

    def test_acceptance_preserves_numbers_and_never_calculates(self):
        d=self.create()
        m={'title':'Prueba IA','actors':['A','B'],'strategies':[['S1','S2'],['T1','T2']],
           'a':[[3,0],[5,1]],'b':[[3,5],[0,1]],'p':.5,'q':.6}
        d=operate(self.path,{'action':'draft','id':d['id'],'revision':d['revision'],'model':m,'assumptions':'Hipotético'})
        self.job(d)
        applied=operate(self.path,{'action':'accept_ai','id':d['id'],'revision':d['revision'],'job_id':'job-test'})
        self.assertEqual(applied['model']['a'],m['a']);self.assertEqual(applied['model']['q'],.6)
        self.assertEqual(applied['model']['actors'],['Municipio','Vecinos'])
        self.assertIsNone(applied['result']);self.assertEqual(applied['versions'],[])
        self.assertEqual(applied['messages'][-1]['source'],'ai-draft')
        for key,_ in QUESTIONS:
            applied=operate(self.path,{'action':'message','id':applied['id'],'revision':applied['revision'],'text':'Respuesta '+key})
        calculated=operate(self.path,{'action':'calculate','id':applied['id'],'revision':applied['revision'],
            'model':applied['model'],'evidence':[],'assumptions':'Hipotéticos','reviewed':True})
        self.assertEqual(calculated['result']['context']['mode'],'ai-assisted')
        self.assertEqual(len(calculated['result']['context']['ai_proposals']),1)

    def test_stale_proposal_cannot_overwrite_case(self):
        d=self.create();self.job(d)
        d=operate(self.path,{'action':'message','id':d['id'],'revision':d['revision'],'text':'Otro contexto.'})
        with self.assertRaises(Conflict):operate(self.path,{'action':'accept_ai','id':d['id'],'revision':d['revision'],'job_id':'job-test'})

    def test_failed_generation_is_persisted(self):
        d=self.create();job=self.job(d);job['state']='running';job['result']=None;ai_jobs.store(self.path,job)
        with patch('escenarios.local_ai.propose',side_effect=local_ai.AIError('Modelo desconectado')):
            ai_jobs.worker(self.path,d,job)
        saved=ai_jobs.get_job(self.path,job['id'])
        self.assertEqual(saved['state'],'failed');self.assertEqual(saved['error'],'Modelo desconectado')

    def test_restart_recovers_interrupted_job(self):
        d=self.create();job=self.job(d);job['state']='running';ai_jobs.store(self.path,job)
        ai_jobs.recover_interrupted(self.path)
        self.assertEqual(ai_jobs.get_job(self.path,job['id'])['state'],'failed')

    def test_generation_uses_schema_and_records_limited_context(self):
        local_ai.save_config(self.path,{'enabled':True,'model':'mistral:latest'})
        d=self.create();d['description']='a'*5000
        d['model']={'q':0};d['assumptions']='Hipotético'
        responses=[{'models':[{'name':'mistral:latest','digest':local_ai.CATALOG['mistral:latest']['digest'],'size':4372824384}]},
                   {'done':True,'message':{'content':json.dumps(proposal())},'eval_count':100,'total_duration':2000000000}]
        with patch('escenarios.local_ai.request',side_effect=responses) as call:
            generated=local_ai.propose(self.path,d)
        body=call.call_args_list[1].args[1]
        self.assertFalse(body['stream'])
        self.assertEqual(body['format'],local_ai.SCHEMA)
        self.assertTrue(generated['metadata']['context_limited'])
        self.assertEqual(generated['metadata']['duration_seconds'],2)
        self.assertEqual(generated['input_context']['current_model']['q'],0)
        self.assertEqual(generated['input_context']['analyst_assumptions'],'Hipotético')
        self.assertEqual(generated['metadata']['options']['num_ctx'],4096)

    def test_incomplete_or_malformed_generation_is_not_accepted(self):
        local_ai.save_config(self.path,{'enabled':True,'model':'mistral:latest'})
        ready={'models':[{'name':'mistral:latest','digest':local_ai.CATALOG['mistral:latest']['digest']}]}
        for response in [{'done':True,'message':{'content':'not JSON'}},
                         {'done':True,'done_reason':'length','message':{'content':json.dumps(proposal())}}]:
            with patch('escenarios.local_ai.request',side_effect=[ready,response]):
                with self.assertRaises(local_ai.AIError):local_ai.propose(self.path,self.create())
