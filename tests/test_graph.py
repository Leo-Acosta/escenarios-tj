import tempfile
import unittest
from pathlib import Path
from escenarios.graph import save_graph,load_graph,validate_graph


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
