"""Run the installed application and scientific stack with no Python/R on PATH."""
import argparse
import json
import os
import socket
import subprocess
import time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError

def run(executable,source,output):
    output.mkdir(parents=True,exist_ok=False)
    import shutil
    shutil.copy2(source,output/'escenarios.sqlite3')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    env={k:v for k,v in os.environ.items() if k not in ('SCENARIOS_RSCRIPT','R_LIBS_USER','RETICULATE_PYTHON','PYTHONPATH','PYTHONHOME')}
    env['PATH']=''
    def get(route):
        with urlopen(base+route,timeout=90) as r:return json.load(r)
    with (output/'installed-server.log').open('ab') as log:
        process=subprocess.Popen([str(executable),'--no-browser','--port',str(port),'--data-dir',str(output)],cwd=output,env=env,stdout=log,stderr=log)
        try:
            deadline=time.monotonic()+60
            while True:
                try:get('/api/continuity/status');break
                except (URLError,TimeoutError):
                    if process.poll() is not None or time.monotonic()>deadline:raise RuntimeError('No inició el ejecutable instalado.')
                    time.sleep(.2)
            runtime=get('/api/scientific/status');assert runtime['ready'],runtime
            cases=get('/api/workflows');identity=cases[0]['id']
            payload={'workflow_id':identity,'version':1,'mode':'synthetic','deep':True,'source':'Aceptación sintética del instalador','reviewed':True}
            request=Request(base+'/api/scientific/run',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Origin':base},method='POST')
            with urlopen(request,timeout=90) as r:job=json.load(r)
            deadline=time.monotonic()+1200
            while job['state']=='running':
                if time.monotonic()>deadline:raise TimeoutError('Laboratorio instalado excedió tiempo.')
                time.sleep(2);job=get('/api/scientific/job?id='+job['id'])
            assert job['state']=='ready',job.get('error')
            replay=get('/api/scientific/replay?id='+job['id']);assert replay['reproduced'] and not replay['new_inference']
            result={'synthetic':True,'python_r_on_path':False,'runtime':runtime,'job':job['id'],'assets':len(job['assets']),'result':job['result'],'replayed':True}
            (output/'installed-scientific-verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
            print(json.dumps(result,ensure_ascii=False))
        finally:process.terminate();process.wait(timeout=15)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--exe',type=Path,required=True);a.add_argument('--database',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    o=a.parse_args();run(o.exe.resolve(),o.database.resolve(),o.output.resolve())
