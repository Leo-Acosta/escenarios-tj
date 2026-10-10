"""Complete local acceptance run with synthetic data only; requires installed R."""
import argparse
import io
import json
import sys
import time
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from escenarios import scientific_runtime as science,laboratories,executive,executive_view,executive_pdf,continuity
from escenarios.workflow import operate,QUESTIONS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('tmp/scientific-acceptance'));args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);db=args.output/'case.sqlite3'
    if db.exists():raise ValueError('Usá una carpeta nueva: no se sobrescribe una aceptación anterior.')
    runtime=science.status()
    if not runtime['ready']:raise ValueError('Entorno R incompleto: '+json.dumps(runtime))
    model={'title':'Negociación sintética · aceptación R','actors':['Actor A','Actor B'],'strategies':[['Cooperar','Competir'],['Cooperar','Competir']],'a':[[3,0],[5,1]],'b':[[3,5],[0,1]],'p':.5,'q':.6}
    case=operate(db,{'action':'create','title':model['title'],'description':'Caso sintético, sin datos ni documentos privados.'})
    for _ in QUESTIONS:case=operate(db,{'action':'message','id':case['id'],'revision':case['revision'],'text':'Supuesto sintético de verificación.'})
    case=operate(db,{'action':'calculate','id':case['id'],'revision':case['revision'],'model':model,'evidence':[],'assumptions':'Pagos hipotéticos en puntos.','reviewed':True})
    for seed in [7,42,99]:
        for policies in [['mirror','adaptive'],['random','fixed0']]:
            laboratories.save_from_version(db,{'kind':'agents','workflow_id':case['id'],'version':1,'reviewed':True,'assumptions':'Corrida sintética','options':{'rounds':30,'seed':seed,'noise':.1,'policies':policies}})
    job=science.start(db,{'workflow_id':case['id'],'version':1,'mode':'synthetic','deep':True,'reviewed':True})
    deadline=time.monotonic()+900
    while time.monotonic()<deadline:
        record=science.read(db,job['id'])
        if record['state']!='running':break
        time.sleep(2)
    if record['state']!='ready':raise ValueError('Laboratorio fallido: '+str(record.get('error')))
    replay=science.verify(record)
    archive=science.base64.b64decode(record['archive']);(args.output/'resultados.zip').write_bytes(archive)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for file in ['resultados/espacio_resultados.png','resultados/distribuciones.png','resultados/sensibilidad-3d.html','resultados/eventos-sinteticos.csv','resultados/asociaciones.csv','evaluacion-final/red-profunda.keras','evaluacion-final/reproduccion-modelo.json']:
            assert file in z.namelist(),file
        verification=json.loads(z.read('evaluacion-final/reproduccion-modelo.json'));assert verification['reproducido']
        for name in z.namelist():
            if name.endswith(('.png','.pdf')):
                target=args.output/Path(name).name;target.write_bytes(z.read(name))
    report=executive.create(db,{'workflow_id':case['id'],'version':1,'sections':['matrix'],'references':[],'title':'Aceptación científica · ejemplo sintético','evidence_mode':'synthetic','reviewed':True})
    assert executive.replay(db,report['id'])['new_inference'] is False
    (args.output/'informe.html').write_text(science.report(record),encoding='utf-8')
    content,metadata=continuity.snapshot(db);assert 'scientific_jobs' in metadata['tables']
    (args.output/'respaldo.sqlite3').write_bytes(content)
    acceptance={'classification':'synthetic_only','runtime':runtime,'result':record['result'],'replay':replay,'saved_model_replay':verification,'workflow_id':case['id'],'job_id':job['id'],'executive_id':report['id'],'artifacts':len(record['assets']),'backup_integrity':metadata['integrity']}
    (args.output/'acceptance.json').write_text(json.dumps(acceptance,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(acceptance,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
