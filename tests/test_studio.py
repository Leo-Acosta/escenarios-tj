import base64
import copy
import json
import sqlite3
import tempfile
import threading
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from escenarios import graph,visual_graph,studio,continuity,executive,executive_view,executive_pdf,server,sequential
from escenarios.workflow import operate,Conflict
from test_laboratories import prepare_case
from test_sequential import MODEL as TREE

class StudioTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'db.sqlite3';self.case=prepare_case(self.path);self.scope=self.case['id']
        self.legacy=graph.save_version(self.path,{'title':'Red sintética','graph':{'nodes':[{'id':0,'name':'Municipio','type':0},{'id':1,'name':'Vecinos','type':1}],'edges':[{'a':0,'b':1,'type':'Cooperación'}]},'assumptions':'Hipótesis sintética sin causalidad','workflow_id':self.scope,'reviewed':True})
        self.draft=visual_graph.upgrade(self.legacy['graph'],self.legacy['id'])
        self.network=graph.save_version(self.path,{'title':'Red visual','graph':self.draft,'assumptions':'Hipótesis sintética','workflow_id':self.scope,'parent_id':self.legacy['id'],'reviewed':True})
        self.tree=sequential.save(self.path,sequential.analyze(TREE),self.scope)
        self.value={'workflow_id':self.scope,'title':'Escenario sintético','matrix_version':1,'network_id':self.network['id'],'tree_id':self.tree['id'],'variables':[{'name':'Costo supuesto','value':'10','unit':'puntos','source':'Hipótesis','target':'a00','transformation':'Se asigna manualmente el pago de la matriz conservada; no se ejecuta esta nota.','status':'assumed'}],'constraints':['Presupuesto hipotético'], 'assumptions':'Datos sintéticos sin validación empírica','evidence_mode':'synthetic','payoff_units':['puntos de A','puntos de B'],'comparable':True,'links':[{'node_uid':self.draft['nodes'][0]['uid'],'kind':'matrix','actor':0,'strategies':[0,1]}],'reviewed':True}
    def test_legacy_positions_profiles_stable_ids_and_invalid_contacts(self):
        self.assertEqual(graph.get_version(self.path,self.legacy['id']),self.legacy)
        n=self.draft['nodes'][0];n['position']={'x':-50,'y':400};n['profile']['organization']='Organización ficticia'
        clean=visual_graph.validate(self.draft);self.assertEqual(clean['nodes'][0]['uid'],self.network['graph']['nodes'][0]['uid']);self.assertEqual(clean['nodes'][0]['position']['x'],-50)
        for change in [lambda g:g['nodes'][0]['position'].update(x=float('nan')),lambda g:g['nodes'][0]['profile'].update(email='incorrecto'),lambda g:g['nodes'][1].update(uid=g['nodes'][0]['uid'])]:
            g=copy.deepcopy(self.draft);change(g)
            with self.assertRaises(ValueError):visual_graph.validate(g)
    def test_links_direction_evidence_dates_weights_duplicates(self):
        g=copy.deepcopy(self.draft);e=g['edges'][0];e.update(directed=True,label='Entrega',start='2026-01-01',end='2026-12-01',weight={'value':3,'unit':'puntos','meaning':'Intensidad declarada','scale':'0 a 5 ordinal'})
        self.assertTrue(visual_graph.validate(g)['edges'][0]['directed'])
        for change in [lambda e:e.update(end='2025-01-01'),lambda e:e.update(status='documented_declared'),lambda e:e['weight'].update(unit='')]:
            bad=copy.deepcopy(g);change(bad['edges'][0])
            with self.assertRaises(ValueError):visual_graph.validate(bad)
        bad=copy.deepcopy(g);bad['edges'].append({**bad['edges'][0],'uid':'otra'})
        with self.assertRaises(ValueError):visual_graph.validate(bad)
    def test_backup_migration_recovery_and_frozen_versions(self):
        r=studio.save(self.path,self.value)
        backups=list((self.path.parent/'migration-backups').glob('visual-*.sqlite3'));self.assertTrue(backups)
        self.assertNotIn('studio_scenarios',continuity.inspect(backups[0])['tables'])
        content,_=continuity.snapshot(self.path);recovered,_=continuity.recover(content,self.path.parent/'recovered')
        self.assertEqual(studio.read(recovered,r['id']),r);self.assertEqual(graph.get_version(recovered,self.network['id']),self.network)
    def test_scenarios_revision_clone_comparison_and_stale_references(self):
        a=studio.save(self.path,self.value);b=studio.save(self.path,{**self.value,'title':'Revisión','parent_id':a['id'],'constraints':['Otra restricción']})
        with self.assertRaises(Conflict):studio.save(self.path,{**self.value,'parent_id':a['id']})
        clone=studio.save(self.path,{**self.value,'clone_of':a['id'],'title':'Variante'})
        self.assertNotEqual(clone['payload']['lineage'],a['payload']['lineage']);self.assertEqual(b['payload']['revision'],2)
        comparison=studio.compare(a,b);self.assertTrue(comparison['comparable']);self.assertEqual(comparison['expected_a_delta'],[0,0]);self.assertTrue(comparison['differences'])
        other=studio.save(self.path,{**self.value,'payoff_units':['otras','puntos B']});self.assertIsNone(studio.compare(a,other)['expected_a_delta'])
        graph.save_version(self.path,{'title':'Más nueva','graph':self.draft,'assumptions':'Hipótesis','workflow_id':self.scope,'reviewed':True})
        self.assertTrue(studio.status(self.path,a));self.assertEqual(studio.read(self.path,a['id']),a)
    def test_invalid_reference_cross_case_unreviewed_and_transform(self):
        for extra in [{'reviewed':False},{'network_id':'ausente'},{'matrix_version':99},{'links':[{'node_uid':'ausente','kind':'matrix','actor':0}]},{'tree_id':'ausente'}]:
            with self.assertRaises(ValueError):studio.save(self.path,{**self.value,**extra})
        other=prepare_case(self.path)
        with self.assertRaises(ValueError):studio.save(self.path,{**self.value,'workflow_id':other['id']})
        bad=copy.deepcopy(self.value);bad['variables'][0]['transformation']=''
        with self.assertRaises(ValueError):studio.save(self.path,bad)
    def test_frozen_report_map_svg_and_no_inference_reproduction(self):
        a=studio.save(self.path,self.value);report=studio.report(self.path,[a['id']]);view=executive_view.content(report)
        self.assertTrue(any(c['title']=='Red de relaciones' for c in view['chapters']))
        with patch('escenarios.local_ai.request',side_effect=AssertionError('Sin inferencia')):
            self.assertTrue(executive.replay(self.path,report['id'])['reproduced']);pdf=executive_pdf.build_pdf(report)
            self.assertEqual(pdf,executive_pdf.build_pdf(report))
        with closing(sqlite3.connect(self.path)) as db,db:
            db.execute('DELETE FROM graph_versions');db.execute('DELETE FROM studio_scenarios')
        self.assertTrue(executive.replay(self.path,report['id'])['reproduced'])
        from escenarios.visual_report import svg
        markup=svg(self.network);self.assertIn('<svg',markup);self.assertNotIn('<script',markup)
    def test_tampering_detected(self):
        r=studio.save(self.path,self.value);bad=copy.deepcopy(r);bad['payload']['network']['graph']['nodes'][0]['name']='Alterado'
        with self.assertRaises(ValueError):studio.verify(bad)
        no_hash=copy.deepcopy(self.network);no_hash.pop('sha256')
        with self.assertRaises(ValueError):graph.verify_version(no_hash)
        n=copy.deepcopy(self.network);n['graph']['nodes'][0]['name']='Alterado'
        with self.assertRaises(ValueError):graph.verify_version(n)
    def test_http_journey_origin_and_export(self):
        previous=server.DB;server.DB=self.path;self.addCleanup(setattr,server,'DB',previous)
        http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
        try:
            base=f'http://127.0.0.1:{http.server_port}'
            with urlopen(Request(base+'/api/studio',data=json.dumps({'action':'scenario',**self.value}).encode(),headers={'Origin':base,'Content-Type':'application/json'})) as res:r=json.load(res)
            for route in ['/api/studio/export?id='+r['id'],'/api/studio/replay?id='+r['id'],'/api/studio/catalog?workflow_id='+self.scope,'/api/studio/svg?id='+self.network['id']]:
                with urlopen(base+route) as res:self.assertEqual(res.status,200)
            with self.assertRaises(HTTPError) as error:urlopen(Request(base+'/api/studio',data=b'{}',headers={'Origin':'https://invalid.example'}))
            self.assertEqual(error.exception.code,403)
        finally:http.shutdown();http.server_close();thread.join()

    def test_invalid_structures_are_rejected_without_server_errors(self):
        for value in (None,[],True,'texto'):
            with self.assertRaises(ValueError):studio.save(self.path,value)
            with self.assertRaises(ValueError):graph.validate_graph(value)
        for key,value in [('links',['incorrecto']),('variables',['incorrecto'])]:
            with self.assertRaises(ValueError):studio.save(self.path,{**self.value,key:value})
        bad=copy.deepcopy(self.draft);bad['edges'][0]['weight']=True
        with self.assertRaises(ValueError):visual_graph.validate(bad)
    def test_large_map_tiles_and_printable_pdf_do_not_drop_entities(self):
        from escenarios.visual_report import chapters
        g=visual_graph.upgrade({'nodes':[{'id':i,'name':'Entidad sintética '+str(i),'type':1} for i in range(25)],'edges':[{'a':i,'b':i+1,'type':'Influencia'} for i in range(24)]},'test')
        net=graph.save_version(self.path,{'title':'Red amplia sintética','graph':g,'assumptions':'Sin evidencia real','workflow_id':self.scope,'reviewed':True})
        view=chapters(net);self.assertEqual(len(view['charts']),3);self.assertEqual(sum(len(c['nodes']) for c in view['charts']),25);self.assertEqual(len(view['tables'][1]['rows']),24)
        r=studio.save(self.path,{**self.value,'network_id':net['id'],'links':[]});report=studio.report(self.path,[r['id']]);pdf=executive_pdf.build_pdf(report)
        from io import BytesIO
        from pypdf import PdfReader
        reader=PdfReader(BytesIO(pdf));text=' '.join(p.extract_text() for p in reader.pages)
        self.assertIn('Entidad sintética 24',text);self.assertIn('lámina 3',text)
        self.assertTrue(all(abs(float(p.mediabox.width)-595.2756)<.1 for p in reader.pages))

    def test_report_freezes_and_reproduces_paired_scenario_comparison(self):
        a=studio.save(self.path,self.value);b=studio.save(self.path,{**self.value,'title':'Otra variante','constraints':['Otra restricción'],'clone_of':a['id']})
        report=studio.report(self.path,[a['id'],b['id']]);self.assertEqual(report['payload']['scenario_comparison'],studio.compare(a,b))
        self.assertTrue(any(c['title']=='Comparación de escenarios' for c in executive_view.content(report)['chapters']))
        bad=copy.deepcopy(report);bad['payload']['scenario_comparison']['expected_a_delta'][0]=99
        from escenarios.decision_agents import fingerprint
        bad['sha256']=fingerprint(bad['payload'])
        with self.assertRaises(ValueError):executive.verify(bad)
