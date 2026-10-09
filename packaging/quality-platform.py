"""Repeatable, synthetic platform acceptance. Never opens the user's database."""
import argparse
import concurrent.futures
import hashlib
import json
import platform
import socket
import statistics
import subprocess
import sys
import time
import tracemalloc
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from test_executive import prepared
from test_sequential import MODEL
from escenarios import executive, executive_pdf, executive_view, simulation
from pypdf import PdfReader


def measure(operation, count, budget):
    operation()  # warm-up is excluded, never silently counted as a sample
    values = []
    for _ in range(count):
        start = time.perf_counter()
        operation()
        values.append((time.perf_counter() - start) * 1000)
    ordered = sorted(values)
    p95 = ordered[max(0, __import__('math').ceil(.95 * count) - 1)]
    return {'samples': count, 'durations_ms': values,
            'p50_ms': statistics.median(values), 'p95_ms': p95,
            'budget_p95_ms': budget, 'passed': p95 <= budget}


def run(directory, samples=10):
    directory.mkdir(parents=True, exist_ok=False)
    database = directory / 'escenarios.sqlite3'
    case, refs = prepared(database)
    record = executive.create(database, {'workflow_id': case['id'], 'version': 1,
        'title': 'Calidad de plataforma · ejemplo sintético',
        'executive_note': 'Prueba reproducible; no acredita mejora predictiva real.',
        'pending': 'Observaciones independientes pendientes.',
        'sections': list(executive.LABELS), 'references': refs,
        'evidence_mode': 'synthetic', 'reviewed': True})
    frozen = executive_pdf.build_pdf(record)
    (directory / 'informe-vectorial.pdf').write_bytes(frozen)
    (directory / 'informe-a4.html').write_text(executive_view.html(record), encoding='utf-8')
    reader = PdfReader(BytesIO(frozen))
    assert all(abs(float(p.mediabox.width) - 595.276) < .1 and
               abs(float(p.mediabox.height) - 841.89) < .1 for p in reader.pages)
    text = ' '.join(p.extract_text() for p in reader.pages)
    for label in ['Matriz estratégica', 'Monte Carlo', 'Evaluación predictiva', 'DATOS SINTÉTICOS']:
        assert label in text, label
    metrics = {}
    for iterations in (100, 1000, 5000):
        options = {'iterations': iterations, 'seed': 42, 'radius': .1}
        first = simulation.simulate(MODEL, options)
        assert first == simulation.simulate(MODEL, options)
        metrics[f'monte_carlo_{iterations}'] = measure(
            lambda: simulation.simulate(MODEL, options), samples, 3000)
    tracemalloc.start()
    simulation.simulate(MODEL, {'iterations': 5000, 'seed': 43, 'radius': .1})
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    metrics['simulation_memory'] = {'peak_python_bytes': peak,
        'budget_bytes': 32 * 1024 * 1024, 'passed': peak < 32 * 1024 * 1024}
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    command = [sys.executable, '-m', 'escenarios.server', '--port', str(port), '--database', str(database)]
    with (directory / 'server.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=log)
        try:
            base = f'http://127.0.0.1:{port}'
            def get(path):
                with urlopen(base + path, timeout=15) as response:
                    assert response.status == 200
                    return response.read()
            deadline = time.monotonic() + 30
            while True:
                try:
                    get('/api/continuity/status')
                    break
                except OSError:
                    if process.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError('Server failed to start; inspect server.log')
                    time.sleep(.1)
            for name, endpoint in [('workflows', '/api/workflows'),
                    ('replay', '/api/executive/replay?id=' + record['id']),
                    ('html', '/api/executive/html?id=' + record['id']),
                    ('pdf', '/api/executive/pdf?id=' + record['id'])]:
                metrics['http_' + name] = measure(lambda: get(endpoint), samples, 3000)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                copies = list(pool.map(lambda _: get('/api/executive/pdf?id=' + record['id']), range(12)))
            assert all(copy == frozen for copy in copies)
            replay = json.loads(get('/api/executive/replay?id=' + record['id']))
            assert replay['reproduced']
        finally:
            process.terminate()
            process.wait(timeout=10)
    result = {'synthetic': True, 'environment': {'os': platform.platform(),
        'python': platform.python_version(), 'machine': platform.machine()},
        'samples': samples, 'warmup_excluded': True, 'metrics': metrics,
        'parallel_readers': 4, 'parallel_pdf_requests': 12,
        'parallel_pdf_identical': True, 'reproduced_without_inference': True,
        'pdf_pages': len(reader.pages), 'pdf_a4': True,
        'pdf_sha256': hashlib.sha256(frozen).hexdigest(),
        'report_id': record['id'], 'workflow_id': case['id'],
        'passed': all(value['passed'] for value in metrics.values()),
        'limits': ['Budgets apply to this fixture and environment; not an Ollama SLA.',
                   'Python allocation peak is not total process RSS.',
                   'Digital A4 verification does not verify a physical printer.']}
    (directory / 'acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=10)
    args = parser.parse_args()
    if not 5 <= args.samples <= 100:
        parser.error('Use 5–100 samples.')
    result = run(args.output.resolve(), args.samples)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
