"""Comparación local auditada. --demo no modifica expedientes reales."""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from escenarios import decision_agents,local_ai


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo',action='store_true')
    group.add_argument('--config',type=Path,help='JSON con model, options, assumptions y reviewed')
    group.add_argument('--replay',help='ID de comparación conservada; no requiere Ollama')
    group.add_argument('--optimize',help='ID de comparación para solicitar el siguiente paso, sin ejecutarlo')
    parser.add_argument('--db',type=Path,default=ROOT/'data'/'local-agent-demo.sqlite3')
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    try:
        if args.replay:result=decision_agents.replay(args.db,args.replay)
        elif args.optimize:result=decision_agents.optimize_process(args.db,args.optimize)
        else:
            if args.demo:
                local_ai.save_config(args.db,{'enabled':True,'model':'mistral:latest'})
                config={'model':{'title':'Demostración sintética de políticas','actors':['A','B'],
                    'strategies':[['Cooperar','Competir'],['Cooperar','Competir']],
                    'a':[[3,0],[5,1]],'b':[[3,5],[0,1]],'p':.5,'q':.5},
                    'options':{'actor':0,'rounds':1,'seeds':[42],'baseline':'fixed0','opponent':'fixed0','noise':0},
                    'assumptions':'Pagos hipotéticos. Prueba técnica, no datos de EDESUR ni predicción real.','reviewed':True}
            else:config=json.loads(args.config.read_text(encoding='utf-8-sig'))
            print('Generando decisiones locales; puede tardar varios minutos.',file=sys.stderr,flush=True)
            result=decision_agents.compare(args.db,config)
            decision_agents.replay(args.db,result['id'])
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        if 'payload' in result:
            print(json.dumps({'id':result['id'],'reproduced':True,'mean_utility_delta':result['payload']['mean_utility_delta'],
                'evidence':result['payload']['evidence'],'promotion_allowed':False},ensure_ascii=False))
        elif 'suggestion' in result:
            print(json.dumps({'id':result['id'],'suggestion':result['suggestion'],'auto_execution':False,'promotion_allowed':False},ensure_ascii=False))
        else:print(json.dumps(result,ensure_ascii=False))
        return 0
    except (ValueError,KeyError,OSError,TypeError) as error:
        print(str(error),file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
