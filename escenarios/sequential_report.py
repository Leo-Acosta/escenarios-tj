"""PDF vectorial del árbol guardado y su sensibilidad Monte Carlo."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

INK=colors.HexColor('#193140');MUTED=colors.HexColor('#526574');GREEN=colors.HexColor('#207b61');PURPLE=colors.HexColor('#6977b8');PALE=colors.HexColor('#edf5f2')


def number(v):return format(v,'.3f').rstrip('0').rstrip('.').replace('.',',')


def build_pdf(record):
    m=record['model'];out=BytesIO();width=172*mm
    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=19*mm,rightMargin=19*mm,topMargin=22*mm,bottomMargin=22*mm,title=m['title'],author='Escenarios TJ')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TJTitle',fontName='Helvetica-Bold',fontSize=26,leading=31,textColor=INK,spaceAfter=16))
    styles.add(ParagraphStyle(name='TJSection',fontName='Helvetica-Bold',fontSize=14,leading=19,textColor=INK,spaceBefore=16,spaceAfter=10,keepWithNext=True))
    styles.add(ParagraphStyle(name='TJBody',fontName='Helvetica',fontSize=10,leading=15,textColor=MUTED,spaceAfter=10))
    styles.add(ParagraphStyle(name='TJSmall',fontName='Helvetica',fontSize=8,leading=12,textColor=MUTED,spaceAfter=6))
    def p(text,style='TJBody'):return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
    def table(rows,widths):
        t=Table([[p(x,'TJSmall') for x in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#d6e3e8'))]))
        return t
    flow=[p('ESCENARIOS TJ / INFORME EJECUTIVO','TJSmall'),Spacer(1,8*mm),p(m['title'],'TJTitle'),p('Decisiones secuenciales e incertidumbre en los incentivos.'),p('Modelo exploratorio con información perfecta. Los resultados dependen de los pagos y supuestos del analista; no constituyen una predicción validada.'),p('01 / Lectura ejecutiva','TJSection')]
    eq=record['equilibria'];firsts=sorted({e['first'] for e in eq})
    summary='Decisión de A compatible con la solución: '+ ' / '.join(m['actions'][0][i] for i in firsts)+'.'
    t=Table([[p(summary)],[p(f'{len(eq)} soluciones puras perfectas en subjuegos. Se conservan los empates y los planes de respuesta fuera de la ruta.')]],colWidths=[width]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)]));flow.append(t)
    flow.extend([p('Actores y orden de decisión','TJSection'),p('A: '+m['actors'][0]+'. Decide primero.'),p('B: '+m['actors'][1]+'. Observa la decisión de A y responde.'),p('Planes completos de equilibrio','TJSection')])
    rows=[['Solución','Decisión A','B después de A1','B después de A2','Pagos en ruta']]
    for i,e in enumerate(eq):rows.append([str(i+1),m['actions'][0][e['first']],m['actions'][1][e['responses'][0]],m['actions'][2][e['responses'][1]],' / '.join(number(v) for v in e['payoffs'])])
    flow.extend([table(rows,[16*mm,42*mm,42*mm,42*mm,30*mm]),p('Inducción hacia atrás: B maximiza su utilidad en cada nodo; A compara las consecuencias de esos planes completos.','TJSmall')])
    flow.extend([p('Trazabilidad y próximos pasos','TJSection'),p('Versión guardada: '+record.get('id','sin identificador')+'\nCalculado: '+record['calculated_at'],'TJSmall'),p('Verificar los pagos con evidencia, revisar los supuestos de información y contrastar alternativas antes de aplicar el modelo a una decisión real. Las referencias y la validación predictiva deben documentarse por separado.','TJSmall')])
    flow.extend([PageBreak(),p('02 / Árbol y consecuencias','TJTitle')])
    d=Drawing(width,235)
    def box(x,y,w,h,label,col=PALE):
        d.add(Rect(x-w/2,y,w,h,rx=7,ry=7,fillColor=col,strokeColor=colors.HexColor('#8aa5ad')))
        d.add(String(x,y+h/2-3,label,fontSize=9,fontName='Helvetica',fillColor=INK,textAnchor='middle'))
    e=eq[0]
    box(width/2,195,150,32,'A decide primero')
    for i in range(2):
        x=width*(.25+.5*i);d.add(Line(width/2,195,x,152,strokeColor=GREEN if e['first']==i else MUTED,strokeWidth=2 if e['first']==i else .7));box(x,122,190,30,'A'+str(i+1)+' / B observa')
        for j in range(2):
            xx=width*(.125+.5*i+.25*j);active=e['first']==i and e['responses'][i]==j
            d.add(Line(x,122,xx,75,strokeColor=GREEN if active else MUTED,strokeWidth=2 if active else .7))
            box(xx,34,110,40,' / '.join(number(v) for v in m['payoffs'][i][j]))
            d.add(String(xx,16,'A'+str(i+1)+' - B'+str(j+1),fontSize=9,fillColor=MUTED,textAnchor='middle'))
    flow.extend([d,p('Ruta resaltada: solución 1. Los códigos A1/A2 y B1/B2 remiten a las alternativas completas de la tabla.','TJSmall')])
    rows=[['Decisión de A','Respuesta observada de B','Pago A','Pago B']]
    for i in range(2):
        for j in range(2):rows.append(['A'+str(i+1)+': '+m['actions'][0][i],'B'+str(j+1)+': '+m['actions'][i+1][j],number(m['payoffs'][i][j][0]),number(m['payoffs'][i][j][1])])
    flow.extend([table(rows,[65*mm,65*mm,21*mm,21*mm]),p('Supuestos aportados por el analista','TJSection'),p(m['assumptions'])])
    for limitation in record['limits']:flow.append(p('- '+limitation,'TJSmall'))
    if record.get('simulation'):
        s=record['simulation'];options=s['options']
        flow.extend([PageBreak(),p('03 / Robustez de la decisión','TJTitle'),p(f"{options['iterations']} repeticiones / semilla {options['seed']} / amplitud +/- {number(options['radius'])} puntos."),p('Distribuciones uniformes e independientes. Los actores conocen los pagos de cada escenario antes de decidir. Se resuelve nuevamente el árbol en cada repetición.')])
        chart=Drawing(width,170)
        labels=['A1: '+m['actions'][0][0],'A2: '+m['actions'][0][1],'Ambas decisiones compatibles']
        for i,c in enumerate(s['decision_counts']):
            y=140-i*53;label=labels[i] if len(labels[i])<=65 else labels[i][:62]+'...'
            chart.add(String(0,y,label,fontSize=9,fontName='Helvetica',fillColor=INK));chart.add(Rect(0,y-25,390*c/options['iterations'],12,rx=4,ry=4,fillColor=[GREEN,PURPLE,colors.HexColor('#b98b44')][i],strokeColor=None)) if c else None;chart.add(String(width,y-23,number(c/options['iterations']*100)+' %',fontSize=10,fontName='Helvetica',fillColor=INK,textAnchor='end'))
        flow.extend([chart,p('Frecuencias de soluciones condicionadas a los intervalos del analista. No representan probabilidades empíricas de conducta.','TJSmall')])
        u=s['utility_a'];flow.append(table([['Utilidad simulada de A','Puntos'],['P5 del mínimo entre equilibrios',number(u['lower_p05'])],['P95 del máximo entre equilibrios',number(u['upper_p95'])]],[132*mm,40*mm]))
        rows=[['Ruta compatible','Repeticiones']]
        for i in range(2):
            for j in range(2):rows.append([m['actions'][0][i]+' / '+m['actions'][i+1][j],f"{s['route_counts'][i][j]} / {options['iterations']}"])
        flow.extend([p('Rutas compatibles','TJSection'),table(rows,[132*mm,40*mm]),p('En empates pueden coincidir varias rutas en la misma repetición; los conteos de rutas no deben sumarse.','TJSmall')])
        for assumption in s['assumptions']:flow.append(p('- '+assumption,'TJSmall'))
    if record.get('ai_proposal'):
        source=record['ai_proposal'];proposal=source['proposal'];meta=source['metadata']
        flow.extend([PageBreak(),p('Asistencia local de IA','TJTitle'),p('Propuesta incorporada como borrador; no constituye evidencia. Los actores, decisiones y pagos finales son los revisados por el analista.'),p('Modelo: '+meta['model']+' / '+meta.get('publisher','')+' / '+meta.get('license',''),'TJSmall'),p('Digest: '+meta['digest'],'TJSmall'),p('Trabajo: '+source['job_id'],'TJSmall'),p(proposal['summary'])])
        flow.append(table([['Nodo','Alternativas propuestas']]+[[['A decide','B después de A1','B después de A2'][i],' / '.join(row)] for i,row in enumerate(proposal['actions'])],[55*mm,117*mm]))
        flow.append(p('Variables propuestas','TJSection'))
        for variable in proposal['variables']:flow.append(p(variable['name']+': '+variable['reason'],'TJSmall'))
        for key,title in [('questions','Preguntas pendientes'),('assumptions','Hipótesis de la propuesta'),('limitations','Límites declarados por la IA')]:
            flow.append(p(title,'TJSection'))
            for text in proposal[key]:flow.append(p('- '+text,'TJSmall'))
    def footer(canvas,document):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d2dfe5'));canvas.line(19*mm,16*mm,191*mm,16*mm);canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED);canvas.drawString(19*mm,11*mm,'ESCENARIOS TJ / Análisis exploratorio / Versión guardada');canvas.drawRightString(191*mm,11*mm,str(document.page));canvas.restoreState()
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
