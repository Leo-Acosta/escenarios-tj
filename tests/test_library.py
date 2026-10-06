import tempfile
import unittest
from pathlib import Path
from escenarios import library,payoff_sweep,agents,comparisons,sequential
from escenarios.case_model import analyze_case,save_case
from test_payoff_sweep import payload
from test_agents import payload as agent_payload
from test_comparisons import payload as comparison_payload

class LibraryTests(unittest.TestCase):
    def test_missing_database_is_empty_without_creating_file(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'absent.db';self.assertEqual(library.search(path)['total'],0);self.assertFalse(path.exists())
    def test_types_search_details_and_immutable_models(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'db.sqlite3'
            case=analyze_case(payload()['model']);save_case(path,case)
            sweep=payoff_sweep.save(path,payoff_sweep.run(payload()))
            agents.save(path,agents.run(agent_payload()));comparisons.save(path,comparisons.compare(comparison_payload()))
            self.assertEqual(library.search(path)['total'],4)
            found=library.search(path,query=sweep['id'],kind='sweep')
            self.assertEqual(found['total'],1);self.assertNotIn('record',found['items'][0])
            retrieved=library.get_record(path,'sweep',sweep['id']);retrieved['record']['model']['title']='Cambio'
            self.assertEqual(library.get_record(path,'sweep',sweep['id'])['title'],'Prueba')
            self.assertEqual(library.search(path,'prUEba')['total'],4)
            with self.assertRaises(KeyError):library.get_record(path,'sweep','missing')
    def test_pagination_reaches_older_records(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'db.sqlite3';r=payoff_sweep.run(payload())
            for i in range(32):payoff_sweep.save(path,r)
            self.assertEqual(library.search(path)['total'],32)
            self.assertEqual(len(library.search(path)['items']),30)
            self.assertEqual(len(library.search(path,offset=30)['items']),2)
    def test_invalid_queries(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'db.sqlite3'
            for args in [{'kind':'invalid'},{'offset':-1},{'offset':True},{'query':'x'*201}]:
                with self.assertRaises(ValueError):library.search(path,**args)
