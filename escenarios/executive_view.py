"""Contenido compartido por la vista A4 y el PDF, sin inferencias ni fuentes vivas."""
from html import escape
from datetime import datetime, timedelta, timezone
from .executive import LABELS, verify
from .dossier import LABELS as DOCUMENTARY_LABELS

POLICIES={'fixed0':'Siempre 1','fixed1':'Siempre 2','mirror':'Copiar rival','trigger':'Cambio permanente','adaptive':'Adaptativa','random':'Aleatoria','local_ai':'IA local'}
EVIDENCE={'synthetic_only':'DATOS SINTÉTICOS - sin evidencia predictiva real',
          'development_only':'DESARROLLO - sin acreditación independiente',
          'validation_only':'VALIDACIÓN - prueba final pendiente',
          'provisional_improvement':'MEJORA PROVISIONAL - requiere validación externa',
          'insufficient_evidence':'EVIDENCIA INSUFICIENTE'}
PARTITIONS={'development':'Desarrollo','validation':'Validación','test':'Prueba reservada'}
NUMERIC=lambda x:format(x,'.6g').replace('.',',') if isinstance(x,(int,float)) else str(x)

def display_date(value):
    """Presentation only; preserve the original timestamp in the frozen record."""
    instant=datetime.fromisoformat(value.replace('Z','+00:00'))
    if instant.tzinfo is None:instant=instant.replace(tzinfo=timezone.utc)
    return instant.astimezone(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y · %H:%M (hora argentina)')

def content(record):
    verify(record,calculations=False)
    p=record['payload'];m=p['matrix'];model=m['model'];sections=p['sections'];sources=p['sources']
    chapters=[]
    def chapter(title,paras=None,tables=None,charts=None):
        c={'title':title,'paragraphs':paras or [],'tables':tables or [],'charts':charts or []};chapters.append(c);return c
    def table(headers,rows):return {'headers':headers,'rows':[[NUMERIC(x) for x in r] for r in rows]}
    def bar(title,labels,values,unit):return {'type':'bars','title':title,'labels':labels,'values':values,'unit':unit}
    def lines(title,series,unit):return {'type':'lines','title':title,'series':series,'unit':unit}
    def source_note(s):return f"Fuente {sources.index(s)+1}: {LABELS[s['kind']]}. Versión conservada; registro técnico disponible en la exportación JSON."
    selected={s['kind'] for s in sources}
    absent=[LABELS[k] for k in sections if k not in ('matrix','simulation') and k not in selected]
    note='DATOS SINTÉTICOS - prueba funcional' if p['evidence_mode']=='synthetic' else 'FUENTES DECLARADAS - verificación documental externa requerida'
    summary=[note,'Objetivo y contexto conservados: '+m['context']['description'],
             f"Base: versión {p['workflow']['version']}; {len(sources)} fuentes complementarias seleccionadas.",
             f"Matriz: {len(m['pure'])} equilibrios puros. Son soluciones del modelo, no pronósticos de conducta real."]
    if p['executive_note']:summary.append('Síntesis del analista (declarada): '+p['executive_note'])
    if absent:summary.append('Secciones solicitadas sin fuente: '+', '.join(absent)+'. No se completan con valores inventados.')
    if 'simulation' in sections and not any(s['kind']=='tree' and s['record'].get('simulation') for s in sources):summary.append('Monte Carlo pendiente: no hay simulación conservada seleccionada.')
    for s in sources:
        if s['kind']=='evaluation':
            r=s['record']['payload']['result'];summary.append(f"Evaluación {PARTITIONS[r['partition']]}: {EVIDENCE[r['evidence']]}. Brier candidato {NUMERIC(r['candidate_brier'])}; referencia {NUMERIC(r['baseline_brier'])}; diferencia {NUMERIC(r['delta'])}; n={r['n']}. Menor Brier es mejor.")
        if s['kind']=='benchmark':
            c=s['record']['payload']['summary'];summary.append(f"Batería simulada: {c['win']} victorias, {c['tie']} empates, {c['loss']} pérdidas y {c['failure']} fallos; sin acreditación predictiva real.")
    if not any(s['kind']=='evaluation' for s in sources):summary.append('Evaluación predictiva pendiente o no seleccionada; no se acredita mejora real.')
    chapter('Resumen ejecutivo',summary)
    if p.get('dossier'):
        d=p['dossier']
        chapter('Expediente documental y seguimiento',[
            'Copia congelada de documentación declarada. Los originales están en el expediente documental; este informe incorpora datos y referencias sin autenticar fuentes.',
            *[f"Original: {r['name']}. {r['note']}" for r in d['documents']],
            *[f"{r['payload']['title']}: {r['payload']['value']} {r['payload']['unit']} · {r['payload']['date']}. Evidencia: {DOCUMENTARY_LABELS[r['payload']['evidence']]}. Fuente: {r['payload']['locator']}. Límites: {r['payload']['uncertainty']}" for r in d['facts']],
            *[f"{r['payload']['date']} · {r['payload']['actor']} · {DOCUMENTARY_LABELS[r['payload']['status']]}: {r['payload']['title']}. {r['payload']['detail']}" for r in d['events']],
            *[f"Cálculo conservado: {r['payload']['result']['difference_kwh']} kWh en {r['payload']['result']['days']} días; {r['payload']['result']['daily_kwh']} kWh diarios. {' '.join(r['payload']['result']['limits'])}" for r in d.get('calculations',[])]])
    if 'matrix' in sections:
        c=chapter('Matriz estratégica',[
            f"Actores: {model['actors'][0]} / {model['actors'][1]}. p={NUMERIC(model['p'])}, q={NUMERIC(model['q'])}: supuestos, no probabilidades aprendidas.",
            'Supuestos conservados: '+m['context']['assumptions'],
            'Equilibrios puros: '+('; '.join(model['strategies'][0][i]+' / '+model['strategies'][1][j] for i,j in m['pure']) or 'Ninguno.'),
            'Equilibrio mixto interior: '+(f"p={NUMERIC(m['mixed']['p'])}; q={NUMERIC(m['mixed']['q'])}." if m['mixed'] else 'No se identifica uno aislado.')],
            [table([model['actors'][0]+' / '+model['actors'][1],*model['strategies'][1]],
                   [[model['strategies'][0][i],*[f"{NUMERIC(model['a'][i][j])} / {NUMERIC(model['b'][i][j])}" for j in range(2)]] for i in range(2)])])
        for actor,key in enumerate(('values_a','values_b')):
            c['charts'].append(bar('Utilidad esperada - '+model['actors'][actor],model['strategies'][actor],m[key],'Escala del actor'))
        c['paragraphs']+=m['limitations']
    for s in sources:
        k=s['kind'];r=s['record'];body=r.get('payload',r)
        title=LABELS[k]
        c=chapter(title,[source_note(s)])
        if k=='variables':
            evidence_labels={'synthetic':'Sintético','assumed':'Supuesto','documented_declared':'Documentación declarada','pending':'Pendiente'}
            type_labels={'number':'Número','category':'Categoría','boolean':'Booleano'}
            def target_label(target):
                model=body['matrix']['model']
                if target=='context':return 'Contexto'
                if target in ('p','q'):return 'Proporción de estrategia 1 de '+model['actors'][0 if target=='p' else 1]
                return 'Pago '+model['actors'][0 if target[0]=='a' else 1]+': '+model['strategies'][0][int(target[2])]+' / '+model['strategies'][1][int(target[4])]
            c['paragraphs']+=body['limits']
            c['tables'].append(table(['Variable / tipo','Valor / unidad','Vínculo / intervalo','Evidencia'],
                [[v['name']+' / '+type_labels[v['type']],('Sí' if v['value'] is True else 'No' if v['value'] is False else NUMERIC(v['value']))+' / '+v['unit'],
                  target_label(v['target'])+' / '+(' a '.join(NUMERIC(x) for x in v['interval']) if v['interval'] is not None else 'Sin intervalo'),evidence_labels[v['evidence']]] for v in body['variables']]))
            c['tables'].append(table(['Variable','Fuente declarada','Incertidumbre'],[[v['name'],v['source'],v['uncertainty']] for v in body['variables']]))
        elif k=='tree':
            t=r['model'];c['paragraphs']+=['Modelo secuencial independiente, vinculado al expediente; no hereda automáticamente la matriz simultánea.',
                                         'Información perfecta: B observa la decisión de A. Supuestos: '+t['assumptions']]
            c['charts'].append({'type':'tree','title':'Árbol y pagos por desenlace','model':t})
            c['tables'].append(table(['Decisión A','Respuesta B','Pago A','Pago B'],[[t['actions'][0][i],t['actions'][i+1][j],*t['payoffs'][i][j]] for i in range(2) for j in range(2)]))
            c['tables'].append(table(['Primer movimiento','Plan completo de B','Desenlace','Pagos A / B'],
                [[t['actions'][0][e['first']],'; '.join(t['actions'][i+1][e['responses'][i]] for i in range(2)),
                  t['actions'][e['first']+1][e['outcome'][1]],' / '.join(NUMERIC(x) for x in e['payoffs'])] for e in r['equilibria']]))
            c['paragraphs']+=r['limits']
            if 'simulation' in sections and r.get('simulation'):
                v=r['simulation'];o=v['options'];mc=chapter('Monte Carlo',[
                    f"{o['iterations']} repeticiones; semilla {o['seed']}; amplitud {NUMERIC(o['radius'])}. Frecuencias simuladas, no probabilidades empíricas.",
                    'P5/P95 de utilidad A: '+NUMERIC(v['utility_a']['lower_p05'])+' / '+NUMERIC(v['utility_a']['upper_p95'])+'.']+v['assumptions'])
                mc['charts'].append(bar('Frecuencia de decisiones compatibles',[t['actions'][0][0],t['actions'][0][1],'Ambas / empate'],v['decision_frequencies'],'Frecuencia simulada 0-1'))
        elif k=='agents':
            o=r['options'];c['paragraphs']+=[f"{o['rounds']} rondas; semilla {o['seed']}; error {NUMERIC(o['noise'])}. Políticas: {' / '.join(POLICIES[x] for x in o['policies'])}.",'Supuestos: '+r['assumptions']]+r['limits']
            for actor in range(2):c['charts'].append(lines('Utilidad acumulada - '+r['model']['actors'][actor],[{'name':POLICIES[o['policies'][actor]],'values':[v['totals'][actor] for v in r['rounds']]}],'Pago acumulado en escala del actor'))
            c['tables'].append(table(['Actor','Total','Media por ronda'],[[r['model']['actors'][i],r['totals'][i],r['means'][i]] for i in range(2)]))
            samples=r['rounds'] if len(r['rounds'])<=10 else r['rounds'][:5]+r['rounds'][-5:]
            c['paragraphs'].append('Trazas: primeras y últimas cinco rondas, sin duplicar. JSON conserva todas.')
            c['tables'].append(table(['Ronda','Acciones ejecutadas A / B','Pagos A / B'],[[v['round'],' / '.join(r['model']['strategies'][i][v['actions'][i]] for i in range(2)),' / '.join(NUMERIC(x) for x in v['payments'])] for v in samples]))
        elif k=='comparison':
            o=r['options'];c['paragraphs']+=['Semillas: '+', '.join(map(str,r['seeds']))+f"; {o['rounds']} rondas; error {NUMERIC(o['noise'])}.",'Supuestos: '+r['assumptions']]+r['limits']
            c['paragraphs'].append('Los gráficos muestran medias. La dispersión y las trazas completas se conservan en el JSON exportable.')
            labels=[POLICIES[x] for x in r['policies']]
            for actor in range(2):
                values=[[next(x['statistics'][actor]['mean'] for x in r['cells'] if x['i']==i and x['j']==j) for j in range(len(labels))] for i in range(len(labels))]
                c['charts'].append({'type':'heatmap','title':'Utilidad media - '+r['model']['actors'][actor],'labels':labels,'values':values,'unit':'Filas: A; columnas: B. Escala del actor.'})
        elif k=='sweep':
            o=r['options'];c['paragraphs']+=[f"Pago {o['actor'].upper()}, fila {o['row']+1}, columna {o['column']+1}: {NUMERIC(o['minimum'])} a {NUMERIC(o['maximum'])}. 101 muestras.",'Supuestos: '+r['assumptions']]+r['limits']
            actor=0 if o['actor']=='a' else 1;key='values_a' if actor==0 else 'values_b'
            c['charts'].append(lines('Sensibilidad - '+r['model']['actors'][actor],[{'name':r['model']['strategies'][actor][i],'values':[v[key][i] for v in r['points']]} for i in range(2)],'Utilidad; eje horizontal: muestras del pago'))
            c['tables'].append(table(['Cambios entre muestras','Desde','Hasta'],[[i+1,x['from'],x['to']] for i,x in enumerate(r['changes'])]))
        elif k=='decision':
            o=body['options'];actor=o['actor'];c['paragraphs']+=[f"Actor {body['model']['actors'][actor]}; referencia {POLICIES[o['baseline']]}; rival {POLICIES[o['opponent']]}; error {NUMERIC(o['noise'])}.",'Supuestos: '+body['assumptions'],f"Diferencia media de utilidad: {NUMERIC(body['mean_utility_delta'])}. Simulación, no precisión predictiva."]+body['limits']
            c['tables'].append(table(['Semilla','Utilidad IA','Utilidad referencia','Diferencia'],[[t['seed'],t['candidate']['means'][actor],t['baseline']['means'][actor],t['utility_delta']] for t in body['trials']]))
            for t in body['trials']:
                trace=t['decisions'][0];c['paragraphs'].append(f"Modelo {trace['model']}; semilla {t['seed']}; versión técnica del modelo, respuestas y decisiones completas en JSON.")
                c['charts'].append(lines('IA y referencia - semilla '+str(t['seed']),[{'name':name,'values':[v['totals'][actor] for v in t[key]['rounds']]} for name,key in [('IA local','candidate'),('Referencia','baseline')]],'Utilidad acumulada del actor evaluado'))
        elif k=='benchmark':
            counts=body['summary'];c['paragraphs']+=['Supuestos: '+body['assumptions']]+body['limits']
            c['charts'].append(bar('Resultados de la batería',['Victorias','Empates','Pérdidas','Fallos'],[counts[x] for x in ('win','tie','loss','failure')],'Número de condiciones / semillas'))
            c['tables'].append(table(['Semilla','Referencia / rival','Error','Resultado','Diferencia o fallo'],
                [[t['config']['options']['seeds'][0],POLICIES[t['config']['options']['baseline']]+' / '+POLICIES[t['config']['options']['opponent']],t['config']['options']['noise'],
                  {'win':'Victoria','tie':'Empate','loss':'Pérdida','failure':'Fallo'}[t['outcome']],t['comparison']['payload']['mean_utility_delta'] if t['comparison'] else t['error']] for t in body['trials']]))
        elif k=='evaluation':
            metric=body['result'];proto=body['protocol']['payload'];candidate=body['candidate']['payload']
            c['paragraphs']+=[EVIDENCE[metric['evidence']],f"Partición: {PARTITIONS[metric['partition']]}; objetivo: {proto['target']}",
                             'Método candidato: '+candidate['method'],'Referencia: '+proto['baseline_method'],
                             f"n={metric['n']}; pendientes={metric['pending']}; diferencia Brier={NUMERIC(metric['delta'])}. Menor es mejor.",
                             'Intervalo pareado aproximado: '+' a '.join(NUMERIC(x) for x in metric['paired_bootstrap_95'])+'. Semilla '+str(metric['seed'])+'.',
                             'Cierre de desarrollo: '+display_date(proto['development_end'])+'; validación: '+display_date(proto['validation_end'])+'; prueba reservada: '+display_date(proto['test_end']),
                             'Fuentes: '+proto['sources']+'; independencia: '+proto['independence'],'Supuestos: '+proto['assumptions']]+metric['limits']
            c['charts'].append(bar('Brier candidato y referencia',['Candidato','Referencia'],[metric['candidate_brier'],metric['baseline_brier']],'Error Brier 0-1; menor es mejor'))
            c['tables'].append(table(['Unidad','Prob. candidato','Prob. referencia','Resultado'],[[x['research']['unit_id'],x['candidate_probability'],x['baseline_probability'],x['observation']['outcome'] if x['observation'] else 'Pendiente'] for x in body['dataset'][:20]]))
            c['paragraphs'].append(f"Se muestran hasta veinte eventos; JSON conserva {len(body['dataset'])}. No se omiten pérdidas del cálculo.")
    evidence=m['context'].get('evidence',[])
    c=chapter('Fuentes, hechos declarados y pendientes',[
        'DOCUMENTACIÓN DECLARADA: los elementos siguientes contienen referencias aportadas, no verificación automática.',
        'Los pagos, políticas y simulaciones se interpretan como supuestos del modelo, aun cuando exista documentación contextual.'],
        [table(['Documento','Referencia','Afirmación declarada'],[[v['title'],v['reference'],v['claim']] for v in evidence])] if evidence else [])
    if not evidence:c['paragraphs'].append('DOCUMENTACIÓN PENDIENTE: la versión base no incluye documentos de respaldo.')
    for key,label in [('facts','Hechos / datos declarados'),('payoff_basis','Fundamento de pagos'),('probability_basis','Fundamento de probabilidades')]:
        value=m['context'].get('answers',{}).get(key)
        if value:c['paragraphs'].append(label+': '+value)
    c['paragraphs'].append('PENDIENTES DECLARADOS: '+(p['pending'] or 'Sin detalle adicional aportado. Esto no acredita completitud.'))
    chapter('Trazabilidad y límites',p['limits']+[
        'Emisión: '+display_date(record['created_at']),
        'Los capítulos proceden de versiones conservadas. La exportación JSON mantiene identificadores, huellas de integridad y copias completas de las fuentes para auditoría.'],
        [table(['Fuente','Referencia de lectura'],[['Matriz estratégica','Versión '+str(p['workflow']['version'])],*[[LABELS[s['kind']],'Fuente '+str(index+1)] for index,s in enumerate(sources)]])])
    return {'title':p['title'],'badge':note,'id':record['id'],'date':display_date(record['created_at']),'chapters':chapters}

def primitives(chart):
    """Coordenadas compartidas: 720x290, y hacia abajo, PDF y SVG idénticos."""
    output=[]
    def line(x1,y1,x2,y2,color='#cedbe2',width=1):output.append(('line',x1,y1,x2,y2,color,width))
    def rect(x,y,w,h,color):output.append(('rect',x,y,w,h,color))
    def label(x,y,value,size=12,color='#213846'):output.append(('text',x,y,str(value),size,color))
    palette=['#137f84','#c37445','#7d65a5','#82969f']
    typ=chart['type'];label(20,20,chart['title'] if len(chart['title'])<=45 else chart['title'][:42]+'...',14)
    if typ not in ('lines','tree'):label(20,282,chart.get('unit',''),10,'#536a78')
    if typ=='tree':
        m=chart['model'];nodes=[(360,55),(185,130),(535,130),(90,225),(270,225),(450,225),(630,225)]
        for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]:line(*nodes[a],*nodes[b],'#9dbbc1',2)
        for i,(x,y) in enumerate(nodes):rect(x-58,y-18,116,36,'#edf5f5');label(x-49,y+4,('A' if i==0 else 'B' if i<3 else ' / '.join(NUMERIC(v) for v in m['payoffs'][(i-3)//2][(i-3)%2])),12)
        for i,x in enumerate((185,535)):label(x-70,102,m['actions'][0][i][:22],11)
        for i,x in enumerate((90,270,450,630)):label(x-75,194,m['actions'][i//2+1][i%2][:23],10)
        label(20,282,'Etiquetas completas y pagos en la tabla del capítulo.',10,'#536a78')
    elif typ=='bars':
        vals=chart['values'];lo=min(0,*vals);hi=max(0,*vals);span=hi-lo or 1
        zero=240-(0-lo)/span*175;line(65,zero,695,zero)
        width=570/len(vals)
        for i,(name,value) in enumerate(zip(chart['labels'],vals)):
            x=85+i*width;y=240-(value-lo)/span*175
            rect(x,min(y,zero),width*.55,max(1,abs(y-zero)),palette[i%4]);label(x,y-8 if value>=0 else y+16,NUMERIC(value),13)
            label(x,260,name[:min(22,int(width/9))],9)
        label(22,65,NUMERIC(hi),10);label(22,240,NUMERIC(lo),10)
    elif typ=='lines':
        series=chart['series'];vals=[v for s in series for v in s['values']];lo=min(vals);hi=max(vals);span=hi-lo or 1
        line(65,60,65,230);line(65,230,695,230)
        for i,s in enumerate(series):
            v=s['values'];n=len(v);indices=sorted(set([round(j*(n-1)/79) for j in range(80)])) if n>80 else list(range(n))
            pts=[(65+(j/(n-1) if n>1 else .5)*630,230-(v[j]-lo)/span*170) for j in indices]
            if len(pts)==1:rect(pts[0][0]-3,pts[0][1]-3,6,6,palette[i%4])
            for a,b in zip(pts,pts[1:]):line(*a,*b,palette[i%4],2)
            label(70+i*300,45,s['name'][:28],11,palette[i%4])
        label(15,65,NUMERIC(hi),10);label(15,233,NUMERIC(lo),10)
        label(65,255,'1',10);label(650,255,str(len(series[0]['values'])),10)
        label(20,282,chart.get('unit','')+'; trazo de hasta 80 puntos, datos completos en JSON.',9,'#536a78')
    elif typ=='heatmap':
        n=len(chart['labels']);allvalues=[v for row in chart['values'] for v in row];lo=min(allvalues);hi=max(allvalues);span=hi-lo or 1
        for i,name in enumerate(chart['labels']):label(15,82+i*28,name[:14],10);label(180+i*85,48,str(i+1),11)
        for i,row in enumerate(chart['values']):
            for j,v in enumerate(row):
                strength=(v-lo)/span;color='#{:02x}{:02x}{:02x}'.format(int(235-strength*160),int(247-strength*110),int(246-strength*110))
                rect(155+j*85,60+i*28,81,25,color);label(166+j*85,78+i*28,NUMERIC(v),10)
        label(20,258,'Columnas 1-'+str(n)+': mismas políticas que las filas, en ese orden.',10)
    return output

def svg(chart):
    pieces=[]
    for item in primitives(chart):
        k,*v=item
        if k=='line':pieces.append(f'<line x1="{v[0]}" y1="{v[1]}" x2="{v[2]}" y2="{v[3]}" stroke="{v[4]}" stroke-width="{v[5]}"/>')
        if k=='rect':pieces.append(f'<rect x="{v[0]}" y="{v[1]}" width="{v[2]}" height="{v[3]}" fill="{v[4]}"/>')
        if k=='text':pieces.append(f'<text x="{v[0]}" y="{v[1]}" font-size="{v[3]}" fill="{v[4]}">{escape(v[2])}</text>')
    return '<svg viewBox="0 0 720 290" role="img" aria-label="'+escape(chart['title'],quote=True)+'" xmlns="http://www.w3.org/2000/svg">'+''.join(pieces)+'</svg>'

def html(record):
    view=content(record);e=lambda x:escape(str(x),quote=True)
    chapters=[]
    for i,c in enumerate(view['chapters']):
        tables=[]
        for t in c['tables']:
            tables.append('<table><thead><tr>'+''.join('<th>'+e(v)+'</th>' for v in t['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(v)+'</td>' for v in row)+'</tr>' for row in t['rows'])+'</tbody></table>')
        chapters.append(f'<section class="chapter" id="chapter-{i}"><p class="kicker">ESCENARIOS TJ / {i+1:02d}</p><h2>'+e(c['title'])+'</h2>'+''.join('<p>'+e(v)+'</p>' for v in c['paragraphs'])+''.join(tables)+''.join('<figure>'+svg(v)+'</figure>' for v in c['charts'])+'</section>')
    links=''.join(f'<a href="#chapter-{i}">{e(c["title"])}</a>' for i,c in enumerate(view['chapters']))
    return '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+e(view['title'])+'''</title><style>
    :root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#e9eff2;color:#213846;font:14px/1.65 Arial,sans-serif}.toolbar{background:#112b38;color:white;padding:16px;position:sticky;top:0;z-index:2;display:flex;gap:16px;align-items:center}.toolbar a,.toolbar button{color:white;background:#137f84;border:0;padding:10px;text-decoration:none;cursor:pointer}.document{max-width:210mm;margin:28px auto;background:white;box-shadow:0 8px 32px #132b3820}.cover,.chapter{padding:18mm}.cover{background:#112b38;color:white;min-height:220mm;display:flex;flex-direction:column;justify-content:center;border-bottom:7px solid #137f84}.cover h1{font-size:38px;line-height:1.18;overflow-wrap:anywhere}.kicker{font-size:10px;letter-spacing:2px;color:#137f84;font-weight:bold}.cover .kicker{color:#70d0c4}.badge{padding:12px;border:1px solid #78bfb8;font-size:12px}.chapter{border-bottom:1px solid #d4e0e6}h2{font-size:26px;line-height:1.25;color:#163c4a;break-after:avoid}p,td,th{overflow-wrap:anywhere}p{white-space:pre-line}figure{margin:22px 0;padding:12px;border:1px solid #d4e0e6;background:#f8fbfc;break-inside:avoid}svg{width:100%;display:block;font-family:Arial,sans-serif}table{width:100%;table-layout:fixed;border-collapse:collapse;margin:18px 0;font-size:11px}th{text-align:left;background:#edf5f5}td,th{padding:9px;border-bottom:1px solid #d4e0e6;vertical-align:top}tr{break-inside:avoid}thead{display:table-header-group}.contents a{display:block;color:#137f84;padding:4px}small{overflow-wrap:anywhere}@page{size:A4;margin:16mm}@media print{body{background:white}.toolbar{display:none}.document{margin:0;max-width:none;box-shadow:none}.cover{min-height:240mm;break-after:page;padding:16mm;print-color-adjust:exact;-webkit-print-color-adjust:exact}.chapter{padding:0;break-before:page;border:0}figure,th{print-color-adjust:exact;-webkit-print-color-adjust:exact}h2{break-after:avoid}}@media screen and (max-width:700px){.cover,.chapter{padding:24px}.cover h1{font-size:30px}.toolbar{position:static;flex-wrap:wrap}}
    </style></head><body><div class="toolbar"><strong>Vista A4 · versión congelada</strong><button onclick="window.print()">Imprimir / guardar PDF</button><a href="/api/executive/pdf?id='''+e(view['id'])+'">Descargar PDF vectorial</a></div><main class="document"><header class="cover"><p class="kicker">ESCENARIOS TJ / INFORME EJECUTIVO</p><h1>'+e(view['title'])+'</h1><p class="badge">'+e(view['badge'])+'</p><p>Modelos, escenarios y evidencia reunidos desde versiones conservadas.</p><small>Emisión '+e(view['date'])+'</small></header><section class="chapter contents"><h2>Contenido del informe</h2>'+links+'</section>'+''.join(chapters)+'</main></body></html>'
