"""Portable scientific export; never executes user R code or changes the matrix."""
import csv
import io
import json
import hashlib
import shutil
import zipfile
from pathlib import Path
from .workflow import get_version
from .case_model import analyze_case
from . import laboratories

RECIPES = Path(__file__).parent / 'r'

def status():
    return {'r_available': bool(shutil.which('Rscript')), 'execution': 'external_reviewed',
            'limits': ['R se ejecuta fuera del servidor local.', 'Simulaciones no demuestran mejora predictiva real.']}

def csv_bytes(headers, rows):
    stream=io.StringIO(newline='');writer=csv.writer(stream);writer.writerow(headers);writer.writerows(rows)
    return stream.getvalue().encode('utf-8')

def bundle(path, identity, version):
    if type(version) is not int or version < 1: raise ValueError('Versión calculada requerida.')
    source=get_version(path,identity,version);model=source['model'];result=analyze_case(model)
    files={'version.json':json.dumps(source,ensure_ascii=False,allow_nan=False,sort_keys=True).encode('utf-8')}
    files['pagos.csv']=csv_bytes(['resultado','estrategia_a','estrategia_b','actor_a','actor_b','pago_a','pago_b'],
        [(f'R{i*2+j+1}',model['strategies'][0][i],model['strategies'][1][j],*model['actors'],model['a'][i][j],model['b'][i][j]) for i in range(2) for j in range(2)])
    files['sensibilidad.csv']=csv_bytes(['q','estrategia','utilidad'],[(p['q'],model['strategies'][0][i],p['values'][i]) for p in result['sensitivity']['points'] for i in range(2)])
    runs=[r for r in laboratories.history(path,'agents',identity) if r['workflow']['version']==version]
    files['rondas.csv']=csv_bytes(['corrida','semilla','ronda','actor','politica','pago'],
        [(r['id'],r['options']['seed'],row['round'],model['actors'][i],r['options']['policies'][i],row['payments'][i]) for r in runs for row in r['rounds'] for i in range(2)])
    files['corridas.json']=json.dumps(runs,ensure_ascii=False,allow_nan=False).encode('utf-8')
    for name in ['graficos.R','aprendizaje.R','exploracion.R','LEEME.txt']:
        files[name]=(RECIPES/name).read_bytes()
    manifest={'schema':'scientific-bundle-v1','workflow_id':identity,'version':version,'seed':42,
              'classification':'supuestos del modelo; no observaciones empíricas',
              'files':{name:hashlib.sha256(content).hexdigest() for name,content in files.items()}}
    files['manifest.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,content in files.items():
            info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,content)
    return stream.getvalue()
