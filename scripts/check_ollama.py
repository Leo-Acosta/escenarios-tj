"""Comprueba la integración del proyecto sin modificar expedientes ni descargar modelos."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from escenarios import local_ai


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate',action='store_true',help='Verificar además una propuesta real con un caso hipotético aislado.')
    args=parser.parse_args()
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    state=local_ai.status(ROOT/'data'/'escenarios.sqlite3')
    print(json.dumps(state,ensure_ascii=False,indent=2),flush=True)
    if not state['ready']:return 1
    if not args.generate:return 0
    print('Generando una propuesta real de prueba; puede tardar varios minutos.',flush=True)
    started=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='escenarios-ollama-') as directory:
        database=Path(directory)/'check.sqlite3'
        local_ai.save_config(database,state['config'])
        workflow={'description':'El municipio y una empresa negocian una plaza. Ambos pueden aceptar o rechazar un acuerdo.',
                  'answers':{},'model':None,'assumptions':'Caso hipotético de verificación técnica.','evidence':[]}
        try:result=local_ai.propose(database,workflow)
        except local_ai.AIError as error:
            print(json.dumps({'success':False,'error':str(error)},ensure_ascii=False),flush=True)
            return 1
    print(json.dumps({'success':True,'elapsed_seconds':round(time.monotonic()-started,2),'result':result},ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
