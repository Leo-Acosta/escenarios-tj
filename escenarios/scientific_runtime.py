"""Bounded R jobs, frozen inputs and replay from stored predictions, never arbitrary code."""
import base64
import csv
import hashlib
import io
import json
import math
import os
import random
import re
import shutil
import sqlite3
import subprocess
import threading
import zipfile
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from . import scientific
from .workflow import get_version, get_workflow, now, NotFound, Conflict
from .decision_agents import fingerprint

ROOT=Path(__file__).resolve().parent.parent
SOURCE_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
LOCK=threading.Lock()
MAX_ARCHIVE=10*1024*1024
PACKAGES=['ggplot2','plotly','htmlwidgets','igraph','simmer','arules','caret','nnet','keras3','jsonlite']

def executable():
    configured=os.getenv('SCENARIOS_RSCRIPT')
    if configured:return configured if Path(configured).is_file() else None
    local=ROOT/'.tools/R/bin/x64/Rscript.exe'
    return str(local) if local.is_file() else shutil.which('Rscript')

def environment():
    env=os.environ.copy();library=ROOT/'.tools/R-library'
    for key in list(env):
        if key.startswith('LC_') or key=='LANG':env.pop(key,None)
    if library.is_dir():env['R_LIBS_USER']=str(library)
    python=ROOT/'.tools/keras-python/Scripts/python.exe'
    if python.is_file():env['RETICULATE_PYTHON']=str(python)
    env.update(KERAS_BACKEND='torch',CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='42')
    return env

def status():
    r=executable()
    if not r:return {'r_available':False,'ready':False,'packages':{},'error':'Rscript no está instalado o configurado.'}
    try:
        script="p<-c("+','.join("'"+p+"'" for p in PACKAGES)+");cat(R.version.string,'\\n');for(x in p)cat(x,if(requireNamespace(x,quietly=TRUE))as.character(packageVersion(x))else 'MISSING','\\n')"
        value=subprocess.run([r,'--vanilla','-e',script],env=environment(),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60,check=True)
        lines=value.stdout.strip().splitlines();packages={row.split()[0]:row.split()[1] for row in lines[1:] if len(row.split())==2}
        return {'r_available':True,'ready':all(packages.get(p) not in (None,'MISSING') for p in PACKAGES),'version':lines[0],'packages':packages,'error':None}
    except (subprocess.SubprocessError,OSError) as e:return {'r_available':True,'ready':False,'packages':{},'error':str(e)[:1000]}

def connect(path):
    db=sqlite3.connect(path,timeout=15)
    db.execute('CREATE TABLE IF NOT EXISTS scientific_jobs (id TEXT PRIMARY KEY,workflow_id TEXT,payload TEXT)');db.commit();return db

def process_alive(pid):
    if type(pid) is not int or pid<=0:return False
    if os.name=='nt':
        import ctypes
        api=ctypes.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.restype=ctypes.c_void_p
        api.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
        api.CloseHandle.argtypes=[ctypes.c_void_p]
        handle=api.OpenProcess(0x100000,False,pid)
        if not handle:return False
        try:return api.WaitForSingleObject(handle,0)==258
        finally:api.CloseHandle(handle)
    try:os.kill(pid,0);return True
    except OSError:return False

def store(path,record,new=False):
    with closing(connect(path)) as db,db:
        db.execute('BEGIN IMMEDIATE')
        if new:
            for row in db.execute('SELECT payload FROM scientific_jobs').fetchall():
                other=json.loads(row[0])
                if other['state']=='running' and process_alive(other.get('owner_pid')):raise Conflict('Hay un laboratorio R activo en otra instancia de esta base.')
        db.execute('INSERT OR REPLACE INTO scientific_jobs VALUES (?,?,?)',(record['id'],record['workflow']['id'],json.dumps(record,ensure_ascii=False,allow_nan=False)))

def read(path,identity):
    with closing(connect(path)) as db:row=db.execute('SELECT payload FROM scientific_jobs WHERE id=?',(identity,)).fetchone()
    if not row:raise NotFound('Laboratorio científico desconocido.')
    record=json.loads(row[0])
    if record['state']=='ready':verify(record)
    return record

def public(record):return {k:v for k,v in record.items() if k not in ('archive','input_csv','bundle')}

def history(path,identity,version):
    get_version(path,identity,version)
    with closing(connect(path)) as db:records=[json.loads(x[0]) for x in db.execute('SELECT payload FROM scientific_jobs WHERE workflow_id=? ORDER BY rowid DESC LIMIT 20',(identity,))]
    return [public(r) for r in records if r['workflow']['version']==version]

def date(value):
    if not isinstance(value,str):raise ValueError('Fecha UTC requerida.')
    try:d=datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except ValueError:raise ValueError('Usá fecha ISO UTC: AAAA-MM-DDTHH:MM:SSZ.') from None
    return d

def validate_data(content,cutoffs):
    if not isinstance(content,str) or len(content.encode('utf-8'))>1000000:raise ValueError('CSV máximo de 1 MB.')
    reader=csv.DictReader(io.StringIO(content));headers=reader.fieldnames or []
    required=['unidad','disponible','observado','resultado'];xs=[x for x in headers if x.startswith('x') and x[1:].isdigit()]
    if len(set(headers))!=len(headers) or set(headers)!=set(required+xs) or 'x1' not in xs or not set(xs)<=set('x'+str(i) for i in range(1,21)):raise ValueError('Columnas: unidad, disponible, observado, resultado y x1…x20; x1 es obligatoria.')
    cuts=[date(x) for x in cutoffs]
    if len(cuts)!=2 or not cuts[0]<cuts[1]<datetime.now(timezone.utc):raise ValueError('Dos cortes temporales pasados y crecientes requeridos.')
    rows=list(reader)
    if not 90<=len(rows)<=2000:raise ValueError('Entre 90 y 2000 unidades independientes requeridas.')
    seen=set();counts=[0,0,0];development=[]
    for row in rows:
        unit=row['unidad']
        if not unit or len(unit)>100 or unit in seen:raise ValueError('Unidades únicas y no vacías requeridas.')
        seen.add(unit);available=date(row['disponible']);observed=date(row['observado'])
        if not available<observed<=datetime.now(timezone.utc):raise ValueError('Observación futura o información posterior al resultado.')
        if row['resultado'] not in ('0','1'):raise ValueError('Resultados binarios 0/1 requeridos.')
        for x in xs:
            try:n=float(row[x])
            except (TypeError,ValueError):raise ValueError('Características numéricas requeridas.') from None
            if not math.isfinite(n) or abs(n)>1e9:raise ValueError('Características finitas y acotadas requeridas.')
        part=0 if observed<=cuts[0] else 1 if available>cuts[0] and observed<=cuts[1] else 2 if available>cuts[1] else None
        if part is None:raise ValueError('Una unidad cruza el corte temporal; corregí el protocolo, no omitas silenciosamente casos.')
        counts[part]+=1
        if part==0:development.append(row['resultado'])
    if min(counts)<30 or len(set(development))<2:raise ValueError('Mínimo 30 unidades por partición y ambas clases en desarrollo.')
    return counts

def synthetic():
    rng=random.Random(42);out=io.StringIO();writer=csv.writer(out);writer.writerow(['unidad','disponible','observado','resultado','x1','x2'])
    start=datetime(2020,1,1,tzinfo=timezone.utc)
    for i in range(360):
        x=rng.uniform(-2,2);z=rng.uniform(-2,2);y=int(rng.random()<1/(1+math.exp(-(1.2*x-.5*z))))
        t=start+timedelta(days=i)
        writer.writerow([f'sintetica-{i:04}',t.strftime('%Y-%m-%dT%H:%M:%SZ'),(t+timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%SZ'),y,x,z])
    return out.getvalue(),['2020-04-29T23:59:59Z','2020-08-27T23:59:59Z']

def start(path,payload):
    if not isinstance(payload,dict):raise ValueError('Configuración científica inválida.')
    if payload.get('reviewed') is not True:raise ValueError('Confirmá versión, datos y límites antes de ejecutar.')
    version=payload.get('version')
    if type(version) is not int or version<1:raise ValueError('Versión calculada requerida.')
    source=get_version(path,payload.get('workflow_id'),version)
    mode=payload.get('mode')
    if mode not in ('graphics','synthetic','observed'):raise ValueError('Modo científico inválido.')
    if not executable():raise ValueError('Instalá o configurá R antes de ejecutar.')
    if type(payload.get('deep',False)) is not bool:raise ValueError('Selección de red profunda inválida.')
    content=None;cuts=None
    if mode=='synthetic':content,cuts=synthetic()
    if mode=='observed':
        content=payload.get('csv');cuts=payload.get('cutoffs')
        if not isinstance(cuts,list) or len(cuts)!=2:raise ValueError('Dos cortes requeridos.')
        if not isinstance(payload.get('source'),str) or not 1<=len(payload['source'].strip())<=2000:raise ValueError('Fuente y revisión de independencia requeridas.')
    counts=validate_data(content,cuts) if content else None
    bundle=base64.b64encode(scientific.bundle(path,payload['workflow_id'],version)).decode()
    if not LOCK.acquire(blocking=False):raise Conflict('Ya hay un laboratorio R en ejecución.')
    record={'id':str(uuid4()),'created_at':now(),'owner_pid':os.getpid(),'workflow':{'id':payload['workflow_id'],'version':version},'state':'running','mode':mode,'deep':payload.get('deep',False),'engine':'scientific-r-v2','python_engine_sha256':SOURCE_SHA256,
            'matrix':source,'input_csv':content,'cutoffs':cuts,'partition_counts':counts,'source':payload.get('source','Ejemplo sintético generado por el sistema' if mode=='synthetic' else 'Matriz y corridas conservadas'),
            'bundle':bundle,'seed':42,'result':None,'error':None,
            'limits':['Evaluación retrospectiva; no sustituye el protocolo prospectivo de la aplicación.','Fechas, independencia y autenticidad de datos observados declaradas por el analista.','No hay promoción automática, cambios de pagos ni garantía de precisión futura.']}
    try:
        store(path,record,new=True);threading.Thread(target=worker,args=(path,record),daemon=True).start()
    except BaseException:LOCK.release();raise
    return public(record)

def execute(script,folder,extra=None,deep=False):
    env=environment();env['ESCENARIOS_KERAS']='1' if deep else '0'
    run=subprocess.run([executable(),'--vanilla','--encoding=UTF-8',str(folder/script),*(extra or [])],cwd=folder,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600)
    (folder/(script+'.log')).write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
    if run.returncode:raise ValueError(f'{script}: '+run.stderr[-2500:])

def worker(path,record):
    folder=(Path(path).parent/'scientific-work'/record['id']).resolve()
    try:
        folder.mkdir(parents=True,exist_ok=False)
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(record['bundle']))) as z:z.extractall(folder)
        record['environment']=status();store(path,record)
        if record['input_csv']:
            rows=list(csv.DictReader(io.StringIO(record['input_csv'])));cut=date(record['cutoffs'][0])
            stream=io.StringIO();w=csv.writer(stream);w.writerow(['variable_x1_positiva','variable_x2_positiva','resultado_positivo'])
            for r in rows:
                if date(r['observado'])<=cut:w.writerow([int(float(r['x1'])>0),int(float(r.get('x2','0'))>0),int(r['resultado'])])
            (folder/'transacciones.csv').write_text(stream.getvalue(),encoding='utf-8')
        execute('graficos.R',folder);execute('exploracion.R',folder)
        if record['input_csv']:
            (folder/'datos.csv').write_text(record['input_csv'],encoding='utf-8')
            execute('aprendizaje.R',folder,['datos.csv',*record['cutoffs']],record['deep'])
            execute('reproducir.R',folder,deep=record['deep'])
        archive=io.BytesIO();assets=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for file in sorted(folder.rglob('*')):
                if file.is_file():
                    name=file.relative_to(folder).as_posix();z.write(file,name)
                    if name.startswith(('resultados/','evaluacion-final/')):assets.append({'name':name,'size':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
        content=archive.getvalue()
        if len(content)>MAX_ARCHIVE:raise ValueError('Resultados demasiado grandes para conservación local (máximo 10 MB comprimidos).')
        if Path(path).stat().st_size+len(content)*4/3>18*1024*1024:raise ValueError('La base se acerca al límite de respaldo de 20 MB. Usá un expediente en una base nueva.')
        record['archive']=base64.b64encode(content).decode();record['archive_sha256']=hashlib.sha256(content).hexdigest()
        record['assets']=assets;record['result']=recalculate(record);record['state']='ready';record['finished_at']=now()
        record['sha256']=fingerprint({k:v for k,v in record.items() if k not in ('sha256','archive')});store(path,record)
    except Exception as error:
        record['state']='failed';record['error']=str(error)[:3000];record['finished_at']=now();store(path,record)
    finally:LOCK.release()

def asset(record,name):
    if record['state']!='ready' or not any(x['name']==name for x in record['assets']):raise NotFound('Archivo científico desconocido.')
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(record['archive']))) as z:return z.read(name)

def recalculate(record,saved=None):
    if not record['input_csv']:return {'classification':'model_assumptions','metrics':None,'new_inference':False}
    if saved is None:
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(record['archive']))) as z:
            saved={name:list(csv.DictReader(io.StringIO(z.read('evaluacion-final/'+name+'.csv').decode('utf-8')))) for name in ('pronosticos','validacion','pronosticos-validacion')}
    predictions=saved['pronosticos'];validation=saved['validacion'];validation_predictions=saved['pronosticos-validacion']
    counts=validate_data(record['input_csv'],record['cutoffs']);rows=list(csv.DictReader(io.StringIO(record['input_csv'])))
    cuts=[date(x) for x in record['cutoffs']];test={r['unidad']:r for r in rows if date(r['disponible'])>cuts[1]}
    baseline=sum(int(r['resultado']) for r in rows if date(r['observado'])<=cuts[0])/counts[0]
    validation_units={r['unidad']:r for r in rows if date(r['disponible'])>cuts[0] and date(r['observado'])<=cuts[1]}
    if len(validation_predictions)!=counts[1] or {r['unidad'] for r in validation_predictions}!=set(validation_units):raise ValueError('La validación no conserva todas las unidades.')
    if len(predictions)!=counts[2] or {r['unidad'] for r in predictions}!=set(test):raise ValueError('La prueba no conserva todas las unidades reservadas.')
    differences=[];candidate=[];reference=[]
    for r in predictions:
        y=int(r['resultado']);p=float(r['pronostico']);b=float(r['referencia'])
        if y!=int(test[r['unidad']]['resultado']) or not math.isfinite(p) or not 0<=p<=1 or not math.isclose(b,baseline,abs_tol=1e-12):raise ValueError('Pronósticos, observaciones o referencia incompatibles.')
        candidate.append((p-y)**2);reference.append((b-y)**2);differences.append(candidate[-1]-reference[-1])
    for r in validation:
        errors=[]
        for v in validation_predictions:
            y=int(v['resultado']);p=float(v[r['metodo']])
            if y!=int(validation_units[v['unidad']]['resultado']) or not math.isfinite(p) or not 0<=p<=1:raise ValueError('Pronóstico de validación inválido.')
            if r['metodo']=='referencia' and not math.isclose(p,baseline,abs_tol=1e-12):raise ValueError('Referencia de validación incompatible.')
            errors.append((p-y)**2)
        if not math.isclose(sum(errors)/len(errors),float(r['brier_validacion']),abs_tol=1e-12):raise ValueError('Brier de validación no se reproduce.')
    selected=min(validation,key=lambda r:float(r['brier_validacion']))['metodo']
    delta=sum(differences)/len(differences);rng=random.Random(record['seed'])
    boot=sorted(sum(rng.choices(differences,k=len(differences)))/len(differences) for _ in range(1000))
    return {'classification':'synthetic_only' if record['mode']=='synthetic' else 'observed_retrospective','new_inference':False,
            'validation':validation,'selected':selected,'metrics':{'n':len(predictions),'candidate_brier':sum(candidate)/len(candidate),'baseline_brier':sum(reference)/len(reference),'delta':delta,'paired_bootstrap_95':[boot[24],boot[974]],
            'wins':sum(x < -1e-12 for x in differences),'ties':sum(abs(x)<=1e-12 for x in differences),'losses':sum(x>1e-12 for x in differences)},'promotion_allowed':False}

def verify(record):
    if record.get('state')!='ready':raise ValueError('La ejecución todavía no terminó correctamente.')
    if fingerprint({k:v for k,v in record.items() if k not in ('sha256','archive')})!=record['sha256']:raise ValueError('Registro científico alterado.')
    content=base64.b64decode(record['archive'],validate=True)
    if hashlib.sha256(content).hexdigest()!=record['archive_sha256']:raise ValueError('Archivo científico alterado.')
    if recalculate(record)!=record['result']:raise ValueError('La evaluación científica no se reproduce.')
    return {'reproduced':True,'new_inference':False,'result':record['result']}

def recover(path):
    with closing(connect(path)) as db,db:
        for row in db.execute('SELECT payload FROM scientific_jobs').fetchall():
            r=json.loads(row[0])
            if r['state']=='running' and not process_alive(r.get('owner_pid')):
                r['state']='failed';r['error']='La aplicación se reinició durante la ejecución R.'
                db.execute('UPDATE scientific_jobs SET payload=? WHERE id=?',(json.dumps(r,ensure_ascii=False),r['id']))

def frozen_context(path,identity,version):
    results=[]
    for item in history(path,identity,version):
        if item['state']!='ready':continue
        record=read(path,item['id']);snapshot=public(record)
        if record['input_csv']:
            with zipfile.ZipFile(io.BytesIO(base64.b64decode(record['archive']))) as z:
                saved={name:list(csv.DictReader(io.StringIO(z.read('evaluacion-final/'+name+'.csv').decode('utf-8')))) for name in ('pronosticos','validacion','pronosticos-validacion')}
            snapshot['replay_inputs']={'input_csv':record['input_csv'],'cutoffs':record['cutoffs'],'mode':record['mode'],'seed':record['seed'],'saved':saved}
        results.append(snapshot)
        if len(results)==3:break
    return results

def verify_summary(snapshot):
    inputs=snapshot.get('replay_inputs')
    if inputs and recalculate(inputs,inputs['saved'])!=snapshot['result']:raise ValueError('El resumen científico congelado no se reproduce.')

def widget(record):
    name='resultados/sensibilidad-3d.html'
    content=asset(record,name).decode('utf-8')
    def replace(match):
        relative=match.group(2)
        if relative.startswith(('http:','https:','//')):raise ValueError('Dependencia externa no admitida.')
        target=(Path('resultados')/relative).as_posix()
        data=asset(record,target);mime='application/javascript' if target.endswith('.js') else 'text/css'
        return match.group(1)+'data:'+mime+';base64,'+base64.b64encode(data).decode()+match.group(3)
    content=re.sub(r'((?:src|href)=")(sensibilidad-3d_files/[^\"]+)(")',replace,content)
    policy="<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; script-src 'unsafe-inline' data:; style-src 'unsafe-inline' data:; img-src data: blob:; font-src data:; connect-src 'none'\">"
    return content.replace('<head>','<head>'+policy,1)

def report(record):
    from html import escape
    verify(record);result=record['result'];metric=result['metrics']
    label='DATOS SINTÉTICOS · prueba funcional' if record['mode']=='synthetic' else 'Observaciones declaradas · evaluación retrospectiva' if record['mode']=='observed' else 'Supuestos del modelo · exploración'
    paragraphs=[label,'Fuente: '+record['source'],*record['limits']]
    if metric:
        method={'referencia':'Referencia','logistica':'Regresión logística','red':'Red neuronal pequeña','profunda':'Red neuronal profunda'}[result['selected']]
        paragraphs.extend([f"Método seleccionado: {method}. {metric['n']} unidades de prueba.",f"Brier candidato: {metric['candidate_brier']:.5f}; referencia: {metric['baseline_brier']:.5f}; diferencia: {metric['delta']:.5f}. Menor es mejor.",f"{metric['wins']} mejoras; {metric['ties']} empates; {metric['losses']} pérdidas por unidad. Intervalo pareado aproximado: {metric['paired_bootstrap_95']}."])
    body=''.join('<p>'+escape(s)+'</p>' for s in paragraphs)
    for a in record['assets']:
        if a['name'].endswith('.png'):
            body+='<figure><img alt="Gráfico científico" src="data:image/png;base64,'+base64.b64encode(asset(record,a['name'])).decode()+'"><figcaption>'+escape(a['name'].split('/')[-1])+'</figcaption></figure>'
    return '<!doctype html><html lang="es"><meta charset="utf-8"><title>Informe científico · Escenarios TJ</title><style>@page{size:A4;margin:18mm}body{font:15px Arial;color:#19365a;max-width:850px;margin:30px auto;line-height:1.5}h1{font-size:32px}figure{margin:22px 0;break-inside:avoid}img{width:100%}figcaption{font-size:12px;color:#53667d}@media print{button{display:none}body{margin:0}}</style><button onclick="window.print()">Imprimir / guardar PDF</button><h1>Informe científico</h1><p>Escenarios TJ · versión '+str(record['workflow']['version'])+'</p>'+body+'</html>'
