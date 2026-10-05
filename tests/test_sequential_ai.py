import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_sequential import MODEL
from escenarios import local_ai,ai_jobs
from escenarios.workflow import Conflict


def proposal():
    return {'summary':'Borrador secuencial para revisar.','actors':['Entrante','Instalada'],
        'actions':[['Entrar','Esperar'],['Competir','Acomodar'],['Mantener','Expandir']],
        'variables':[{'name':'Demanda','reason':'Dato pendiente.'}], 'questions':['¿B observa A?'],
        'assumptions':['Información perfecta.'],'limitations':['Pagos hipotéticos.']}

class SequentialAITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'db.sqlite3'
        self.payload={'model':copy.deepcopy(MODEL),'description':'La entrante decide antes que la instalada.','simulation':None}
    def job(self):
        j={'id':'tree-job','workflow_id':'sequential','kind':'sequential','state':'ready',
            'base_fingerprint':ai_jobs.fingerprint(ai_jobs.tree_snapshot(self.payload)),
            'result':{'proposal':proposal(),'metadata':{'model':'mistral:latest','digest':'test'}},'error':None}
        ai_jobs.store(self.path,j);return j
    def test_tree_contract_rejects_wrong_topology_and_new_numbers(self):
        self.assertEqual(local_ai.validate_tree_proposal(proposal()),proposal())
        for key,val in [('payoffs',[[1,2]]),('actions',[['A','B'],['C','D']])]:
            p=proposal();p[key]=val
            with self.assertRaises(local_ai.AIError):local_ai.validate_tree_proposal(p)
        p=proposal();p['actions'][2]=['Same','Same']
        with self.assertRaises(local_ai.AIError):local_ai.validate_tree_proposal(p)
    def test_application_preserves_payoffs_and_requires_fresh_snapshot(self):
        self.job();r=ai_jobs.apply_tree(self.path,{**self.payload,'job_id':'tree-job'})
        self.assertEqual(r['model']['payoffs'],MODEL['payoffs']);self.assertEqual(r['model']['assumptions'],'Hipotético')
        self.assertEqual(r['model']['actions'][0][1],'Esperar')
        for key,value in [('description','Otra descripción del árbol.'),('simulation',{'iterations':100,'seed':42,'radius':2})]:
            with self.assertRaises(Conflict):ai_jobs.apply_tree(self.path,{**self.payload,key:value,'job_id':'tree-job'})
    def test_worker_dispatches_tree_to_distinct_generator(self):
        j=self.job();j['state']='running'
        with patch('escenarios.local_ai.propose_tree',return_value=j['result']) as call:
            ai_jobs.worker(self.path,ai_jobs.tree_snapshot(self.payload),j)
        call.assert_called_once();self.assertEqual(ai_jobs.get_job(self.path,j['id'])['state'],'ready')
    def test_tree_generation_records_schema_context_and_provenance(self):
        local_ai.save_config(self.path,{'enabled':True,'model':'mistral:latest'})
        ready={'models':[{'name':'mistral:latest','digest':local_ai.CATALOG['mistral:latest']['digest']}]}
        answer={'done':True,'message':{'content':json.dumps(proposal())},'total_duration':1000000000}
        with patch('escenarios.local_ai.request',side_effect=[ready,answer]) as request:
            r=local_ai.propose_tree(self.path,ai_jobs.tree_snapshot(self.payload))
        self.assertEqual(request.call_args.args[1]['format'],local_ai.TREE_SCHEMA)
        self.assertEqual(r['metadata']['schema'],'proposal-sequential-v1')
        self.assertEqual(r['input_context']['current_model']['payoffs'],MODEL['payoffs'])

