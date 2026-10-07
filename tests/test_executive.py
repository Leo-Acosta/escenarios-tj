import copy
import json
import tempfile
import unittest
from contextlib import closing
from datetime import datetime,timezone,timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
from escenarios import executive as e,executive_view,executive_pdf,laboratories,sequential,simulation,research,decision_agents
from test_laboratories import prepare_case,OPTIONS
from test_sequential import MODEL as TREE

def prepared(path):
    case=prepare_case(path);refs=[]
    for kind in OPTIONS:
        record=laboratories.save_from_version(path,{'kind':kind,'workflow_id':case['id'],'version':1,'options':OPTIONS[kind],'assumptions':'Prueba sintética de integración.','reviewed':True})
        refs.append({'kind':kind,'id':record['id']})
    tree=sequential.analyze(TREE);tree['simulation']=simulation.simulate(tree['model'],{'iterations':100,'seed':42,'radius':.1})
    tree=sequential.save(path,tree,case['id']);refs.append({'kind':'tree','id':tree['id']})
    t=datetime(2027,1,1,tzinfo=timezone.utc)
    with patch('escenarios.research.clock',return_value=t):
        p=research.protocol(path,{'workflow_id':case['id'],'version':1,'title':'Protocolo sintético','target':'Resultado binario hipotético','horizon_hours':24,'sources':'Fuentes sintéticas','independence':'Unidades de prueba','baseline_method':'Fija 0.5','baseline_probability':.5,'assumptions':'No evidencia real','synthetic':True,'development_end':(t+timedelta(days=2)).isoformat(),'validation_end':(t+timedelta(days=4)).isoformat(),'test_end':(t+timedelta(days=6)).isoformat(),'reviewed':True})
        c=research.candidate(path,{'protocol_id':p['id'],'name':'Candidato sintético','method':'Probabilidad manual','trained_through':t.isoformat(),'reviewed':True})
        event=research.forecast(path,{'protocol_id':p['id'],'candidate_id':c['id'],'unit_id':'unidad-sintética','deadline':(t+timedelta(hours=1)).isoformat(),'candidate_probability':.8,'baseline_probability':.5,'feature_cutoff':t.isoformat(),'features':[{'reference':'Prueba','available_at':t.isoformat()}]})
    with patch('escenarios.research.clock',return_value=t+timedelta(hours=1)):
        research.observe(path,{'event':event['event'],'outcome':0,'source':'Resultado sintético','observed_at':(t+timedelta(hours=1)).isoformat()})
        evaluation=research.evaluate(path,{'protocol_id':p['id'],'candidate_id':c['id'],'partition':'development'})
    refs.append({'kind':'evaluation','id':evaluation['id']})
    matrix=e.catalog(path,case['id'],1)['matrix']['model']
    config={'model':matrix,'options':{'actor':0,'rounds':2,'seeds':[42,43],'baseline':'fixed0','opponent':'mirror','noise':.1},'assumptions':'Simulación sintética de IA.','reviewed':True}
    response={'done':True,'message':{'content':'{"action":1,"reason":"Decisión sintética."}'}}
    source={'id':case['id'],'version':1,'title':matrix['title']}
    with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',return_value=response):
        decision=decision_agents.compare(path,config,workflow_source=source)
    refs.append({'kind':'decision','id':decision['id']})
    conditions=[{**config['options'],'rounds':1,'seeds':[42]},{**config['options'],'rounds':1,'seeds':[43],'baseline':'fixed1'}]
    with patch('escenarios.local_ai.status',return_value={'ready':True,'config':{'model':'mistral:latest'}}),patch('escenarios.local_ai.request',side_effect=[response,{'done':True,'message':{'content':'{"action":99,"reason":"Rechazada."}'}}]):
        benchmark=decision_agents.benchmark(path,{**config,'conditions':conditions},source)
    refs.append({'kind':'benchmark','id':benchmark['id']})
    return case,refs

class ExecutiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'report.sqlite3'
        self.case,self.refs=prepared(self.path)
        self.payload={'workflow_id':self.case['id'],'version':1,'title':'Informe <script> & síntesis','executive_note':'Conclusión del analista, no validada.','pending':'Documentación real pendiente.','evidence_mode':'synthetic','sections':list(e.LABELS),'references':self.refs,'reviewed':True}
    def test_full_report_pdf_html_and_replay_use_same_frozen_sources_without_inference(self):
        report=e.create(self.path,self.payload);view=executive_view.content(report)
        self.assertEqual(len(report['payload']['sources']),7)
        with patch('escenarios.local_ai.request',side_effect=AssertionError('Sin inferencia')):
            self.assertTrue(e.replay(self.path,report['id'])['reproduced']);pdf=executive_pdf.build_pdf(report)
        self.assertEqual(pdf,executive_pdf.build_pdf(report))
        reader=PdfReader(BytesIO(pdf));text=' '.join(p.extract_text() for p in reader.pages)
        for label in ['Matriz estratégica','Árbol decisorio','Monte Carlo','Agentes con memoria','Comparación de políticas','Evaluación predictiva','Fallos','Documentación real pendiente.']:
            self.assertIn(label,text)
        self.assertTrue(all(abs(float(p.mediabox.width)-595.2756)<.1 for p in reader.pages))
        html=executive_view.html(report);self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>',html)
        self.assertIn('DATOS SINTÉTICOS',text);self.assertIn('sin evidencia predictiva real',text)
        self.assertEqual(e.read(self.path,report['id']),report)
    def test_sources_survive_original_deletion_and_workflow_changes(self):
        report=e.create(self.path,self.payload)
        with closing(e.connect(self.path)) as db,db:
            db.execute('DELETE FROM agent_runs');db.execute('DELETE FROM research_records');db.execute('DELETE FROM decision_comparisons')
        self.assertTrue(e.replay(self.path,report['id'])['reproduced'])
        self.assertEqual(e.read(self.path,report['id']),report)
    def test_foreign_duplicate_unreviewed_and_unselected_sources_rejected(self):
        foreign=prepare_case(self.path)
        for payload in [{**self.payload,'workflow_id':foreign['id']},{**self.payload,'references':self.refs+[self.refs[0]]},{**self.payload,'reviewed':False},{**self.payload,'sections':['matrix']},{**self.payload,'sections':['simulation']}]:
            with self.assertRaises(ValueError):e.create(self.path,payload)
        self.assertEqual(e.history(self.path,self.case['id']),[])
    def test_tampered_calculation_detected_even_with_recomputed_hashes(self):
        report=e.create(self.path,self.payload);r=copy.deepcopy(report)
        source=next(s for s in r['payload']['sources'] if s['kind']=='agents');source['record']['totals'][0]+=1
        source['sha256']=decision_agents.fingerprint(source['record']);r['sha256']=decision_agents.fingerprint(r['payload'])
        with self.assertRaises(ValueError):e.verify(r)
    def test_missing_sections_are_pending_and_cannot_claim_documentary_authenticity(self):
        r=e.create(self.path,{**self.payload,'references':[],'evidence_mode':'declared'})
        html=executive_view.html(r);self.assertIn('Secciones solicitadas sin fuente',html);self.assertIn('DOCUMENTACIÓN PENDIENTE',html)
        self.assertIn('verificación documental externa',html)
    def test_long_content_and_negative_utilities_paginate_without_losing_literal_text(self):
        r=e.create(self.path,{**self.payload,'executive_note':'Supuesto declarado. '*200,'pending':'PENDIENTE-LARGO-'+('dato '*700)})
        pdf=executive_pdf.build_pdf(r);reader=PdfReader(BytesIO(pdf));text=' '.join(p.extract_text() for p in reader.pages)
        self.assertIn('PENDIENTE-LARGO-',text);self.assertIn('<script>',text);self.assertGreater(len(reader.pages),10)
