import tempfile
import unittest
from pathlib import Path
from escenarios import variables
from escenarios.workflow import get_version
from test_laboratories import prepare_case


class VariablesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'variables.sqlite3';self.case=prepare_case(self.path)
        self.item={'name':'Presencia supuesta de estrategia B','type':'number','value':.6,'unit':'proporción',
                   'source':'Ejemplo sintético','uncertainty':'Intervalo exploratorio','interval':[.4,.8],
                   'target':'q','evidence':'synthetic'}
        self.payload={'workflow_id':self.case['id'],'version':1,'variables':[self.item],'reviewed':True}
    def test_frozen_dictionary_does_not_change_matrix(self):
        before=get_version(self.path,self.case['id'],1);r=variables.save(self.path,self.payload)
        self.assertEqual(variables.read(self.path,r['id']),r)
        self.assertEqual(get_version(self.path,self.case['id'],1),before)
    def test_invalid_or_incompatible_value_and_uncertainty_rejected(self):
        for update in [{'value':float('nan')},{'value':True},{'value':.7},{'interval':[.8,.4]},
                       {'interval':[-.1,.8]},{'type':'category','value':'Alta'},{'evidence':'verified'}]:
            with self.assertRaises(ValueError):variables.save(self.path,{**self.payload,'variables':[{**self.item,**update}]})
    def test_duplicate_names_targets_and_missing_review_rejected(self):
        for payload in [{**self.payload,'reviewed':False},{**self.payload,'variables':[self.item,self.item]},
                        {**self.payload,'variables':[self.item,{**self.item,'name':'Otra variable'}]}]:
            with self.assertRaises(ValueError):variables.save(self.path,payload)
    def test_context_variable_retains_declared_unit_without_conversion(self):
        r=variables.save(self.path,{**self.payload,'variables':[{**self.item,'name':'Contexto','target':'context',
                                   'type':'category','value':'Hipotético','unit':'categoría','interval':None}]})
        self.assertEqual(r['payload']['variables'][0]['value'],'Hipotético')
