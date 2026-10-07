import tempfile
import unittest
import copy
import sqlite3
from contextlib import closing
from pathlib import Path
from escenarios import variables,executive,executive_view,executive_pdf
from escenarios.decision_agents import fingerprint
from escenarios.workflow import get_version,operate
from test_laboratories import prepare_case,MODEL


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
    def test_history_filters_versions_and_frozen_report_survives_source_deletion(self):
        r=variables.save(self.path,self.payload)
        self.assertEqual(variables.history(self.path,self.case['id'],1)[0]['id'],r['id'])
        report=executive.create(self.path,{'workflow_id':self.case['id'],'version':1,'title':'Variables sintéticas',
            'sections':['matrix','variables'],'references':[{'kind':'variables','id':r['id']}],
            'evidence_mode':'synthetic','reviewed':True})
        self.assertIn('Ejemplo sintético',executive_view.html(report))
        self.assertTrue(executive_pdf.build_pdf(report).startswith(b'%PDF'))
        with closing(sqlite3.connect(self.path)) as db,db:db.execute('DELETE FROM variable_versions')
        self.assertTrue(executive.replay(self.path,report['id'])['reproduced'])
    def test_semantic_mismatch_detected_even_with_new_hash(self):
        r=variables.save(self.path,self.payload);bad=copy.deepcopy(r)
        bad['payload']['variables'][0]['value']=.7;bad['sha256']=fingerprint(bad['payload'])
        with self.assertRaises(ValueError):variables.verify(bad)
        bad=copy.deepcopy(r);bad['payload']['matrix']['values_a'][0]+=1;bad['sha256']=fingerprint(bad['payload'])
        with self.assertRaises(ValueError):variables.verify(bad)
    def test_units_invalid_types_and_foreign_sources_are_not_silently_accepted(self):
        for update in [{'unit':'%'},{'target':[]},{'type':[]},{'interval':[0,float('inf')]},{'source':''}]:
            with self.assertRaises(ValueError):variables.save(self.path,{**self.payload,'variables':[{**self.item,**update}]})
        r=variables.save(self.path,self.payload);foreign=prepare_case(self.path)
        with self.assertRaises(ValueError):executive.create(self.path,{'workflow_id':foreign['id'],'version':1,
             'title':'Fuentes ajenas','sections':['variables'],'references':[{'kind':'variables','id':r['id']}],
             'evidence_mode':'synthetic','reviewed':True})
    def test_versions_are_filtered_before_history_limit_and_old_dictionary_remains_frozen(self):
        old=variables.save(self.path,self.payload)
        operate(self.path,{'action':'calculate','id':self.case['id'],'revision':self.case['revision'],
                          'model':{**MODEL,'q':.7},'evidence':[],'assumptions':'Otra versión sintética','reviewed':True})
        new=variables.save(self.path,{**self.payload,'version':2,'variables':[{**self.item,'value':.7}]})
        self.assertEqual([r['id'] for r in variables.history(self.path,self.case['id'],1)],[old['id']])
        self.assertEqual([r['id'] for r in variables.history(self.path,self.case['id'],2)],[new['id']])
        self.assertEqual(variables.read(self.path,old['id'])['payload']['matrix']['model']['q'],.6)
    def test_multiline_sources_split_across_pdf_pages_without_loss(self):
        from io import BytesIO
        from pypdf import PdfReader
        r=variables.save(self.path,{**self.payload,'variables':[{**self.item,'source':'dato\n'*190}]})
        report=executive.create(self.path,{'workflow_id':self.case['id'],'version':1,'title':'Fuente extensa',
            'sections':['variables'],'references':[{'kind':'variables','id':r['id']}],
            'evidence_mode':'synthetic','reviewed':True})
        pdf=executive_pdf.build_pdf(report);reader=PdfReader(BytesIO(pdf))
        self.assertEqual(' '.join(p.extract_text() for p in reader.pages).split().count('dato'),190)
