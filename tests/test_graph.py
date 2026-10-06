import tempfile
import unittest
from pathlib import Path
from escenarios.graph import save_graph,load_graph,validate_graph,save_version,version_history


class GraphTests(unittest.TestCase):
    def test_persistence_and_untrusted_names(self):
        graph={'nodes':[{'id':0,'name':'<Actor>','type':1},{'id':1,'name':'Municipalidad','type':0}],
               'edges':[{'a':0,'b':1,'type':'Cooperación'}]}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'graph.db'
            saved=save_graph(path,graph)
            self.assertEqual(load_graph(path),saved)
            self.assertEqual(saved['nodes'][0]['name'],'<Actor>')

    def test_invalid_edges_and_names(self):
        for graph in [{'nodes':[],'edges':[]},
                      {'nodes':[{'id':0,'name':42,'type':1}],'edges':[]},
                      {'nodes':[{'id':0,'name':'A','type':1}],'edges':[{'a':0,'b':4,'type':'Influencia'}]}]:
            with self.assertRaises(ValueError):validate_graph(graph)

    def test_versions_keep_full_graph_and_frozen_case(self):
        from escenarios.workflow import operate
        graph={'nodes':[{'id':0,'name':'Actor','type':1}],'edges':[]}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'versions.db'
            case=operate(path,{'action':'create','title':'Caso inicial','description':'Contexto histórico de prueba.'})
            payload={'title':'Red inicial','assumptions':'Relaciones hipotéticas.','reviewed':True,'graph':graph,'workflow_id':case['id']}
            first=save_version(path,payload)
            second=save_version(path,{**payload,'title':'Red posterior','graph':{'nodes':[{'id':0,'name':'Otro actor','type':1}],'edges':[]}})
            save_graph(path,second['graph'])
            self.assertEqual(version_history(path,case['id']),[second,first])
            self.assertEqual(first['graph'],graph)
            self.assertEqual(first['workflow']['revision'],case['revision'])
            independent=save_version(path,{**payload,'workflow_id':''})
            self.assertNotIn('workflow',independent)
            self.assertNotIn(independent,version_history(path,case['id']))

    def test_versions_require_review_and_valid_context(self):
        from escenarios.workflow import NotFound
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'versions.db'
            payload={'title':'Red','assumptions':'Supuestos','reviewed':True,'graph':{'nodes':[{'id':0,'name':'A','type':1}],'edges':[]}}
            self.assertEqual(version_history(path),[])
            for patch in ({'reviewed':False},{'title':''},{'assumptions':''}):
                with self.assertRaises(ValueError):save_version(path,{**payload,**patch})
            with self.assertRaises(NotFound):save_version(path,{**payload,'workflow_id':'missing'})
            self.assertEqual(version_history(path),[])

    def test_evidence_is_preserved_and_invalid_evidence_rejected(self):
        graph={'nodes':[{'id':0,'name':'A','type':1},{'id':1,'name':'B','type':0}], 'edges':[{'a':0,'b':1,'type':'Cooperación','evidence':{'source':' Acta ','reference':' Folio 12 ','note':' Acuerdo hipotético. '}}]}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'evidence.db'
            first=save_version(path,{'title':'Red','assumptions':'Hipótesis','reviewed':True,'graph':graph})
            self.assertEqual(first['graph']['edges'][0]['evidence']['source'],'Acta')
            graph['edges'][0]['evidence']['source']='Nueva fuente'
            save_version(path,{'title':'Otra red','assumptions':'Hipótesis','reviewed':True,'graph':graph})
            self.assertEqual(version_history(path)[1],first)
            for invalid in (None,{}, {'source':'Acta','reference':'','note':'Nota'}, {'source':'A'*161,'reference':'R','note':'N'}):
                graph['edges'][0]['evidence']=invalid
                with self.assertRaises(ValueError):validate_graph(graph)
