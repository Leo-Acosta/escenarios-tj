import math
import tempfile
import unittest
from pathlib import Path
from escenarios.core import Parameters, analyze
from escenarios.storage import save_snapshot, list_snapshots


class CoreTests(unittest.TestCase):
    def test_known_game_and_transition(self):
        r = analyze(Parameters(.6, 3))
        self.assertAlmostEqual(r['values'][0], 2)
        self.assertAlmostEqual(r['values'][1], 1)
        self.assertEqual(r['equilibria'], [(0, 1)])
        self.assertEqual(analyze(Parameters(.6, 0))['equilibria'], [(1, 1)])
        self.assertEqual(analyze(Parameters(.6, 2))['recommendation'], 'Indiferente')
        self.assertEqual(len(analyze(Parameters(.6, 2))['equilibria']), 2)

    def test_invalid_and_endpoints(self):
        for q,c in [(math.nan,3),(.6,math.inf),(-1,0),(1,7)]:
            with self.assertRaises(ValueError): Parameters(q,c)
        self.assertEqual(analyze(Parameters(0,3))['values'],[-4,-5])
        self.assertEqual(analyze(Parameters(1,3))['values'],[6,5])

    def test_snapshot_survives_connection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'demo.sqlite3'
            result = analyze(Parameters())
            ident = save_snapshot(path,result)
            self.assertEqual(list_snapshots(path)[0]['id'], ident)
            self.assertEqual(list_snapshots(path)[0]['result']['parameters'],result['parameters'])


if __name__ == '__main__': unittest.main()
