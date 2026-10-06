"""PDF vectorial de una exploración de incentivos guardada."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,PageBreak
from reportlab.graphics.shapes import Drawing,Line,PolyLine,String
from .sequential_report import number,INK,MUTED,GREEN,PURPLE,PALE

def chart(r,actor):
    width=172*mm;d=Drawing(width,235);points=r['points'];key='values_a' if actor==0 else 'values_b'
    values=[v for p in points for v in p[key]];lo=min(values);hi=max(values);span=hi-lo or 1
    x=lambda k:45+(width-60)*k/100
    y=lambda v:40+160*(v-lo)/span
    d.add(Line(x(0),40,x(100),40,strokeColor=MUTED))
    for strategy,color in [(0,GREEN),(1,PURPLE)]:
        coords=[]
        for k,p in enumerate(points):coords.extend([x(k),y(p[key][strategy])])
        d.add(PolyLine(coords,strokeColor=color,strokeWidth=2,fillColor=None))
    for yy,value in [(200,hi),(40,lo)]:d.add(String(0,yy,number(value),fontSize=8,fillColor=MUTED))
    d.add(String(x(0),23,number(points[0]['value']),fontSize=8,fillColor=MUTED))
    d.add(String(x(100),23,number(points[-1]['value']),fontSize=8,textAnchor='end',fillColor=MUTED))
    d.add(String(width/2,5,'Pago explorado',fontSize=9,textAnchor='middle',fillColor=MUTED))
    return d

def build_pdf(r):
    m=r['model'];o=r['options'];out=BytesIO()
    styles={name:ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,textColor=INK if name in ('title','section') else MUTED,spaceAfter=9,keepWithNext=name=='section')
            for name,font,size,leading in [('title','Helvetica-Bold',23,28),('section','Helvetica-Bold',13,18),('body','Helvetica',9,13),('small','Helvetica',7.5,10)]}
    def p(text,style='body'):return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
    def pair(indices):return ' / '.join(m['strategies'][k][v] for k,v in enumerate(indices))
    def table(rows,widths):
        t=Table([[p(v,'small') for v in row] for row in rows],colWidths=widths,repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#d6e3e8'))]));return t
    flow=[p('ESCENARIOS TJ / INCENTIVOS','small'),p(m['title'],'title'),p('Informe ejecutivo de sensibilidad de un pago. 101 escenarios del modelo; sin validación predictiva.'),p('01 / Configuración y trazabilidad','section'),p(f"Pago de {m['actors'][0 if o['actor']=='a' else 1]} en {pair([o['row'],o['column']])}. Rango: {number(o['minimum'])} a {number(o['maximum'])}."),p(f"Supuestos constantes: p = {number(m['p']*100)} % / q = {number(m['q']*100)} %. Los otros siete pagos permanecen fijos."),p('Versión: '+r['id']+'\nMotor: '+r['engine']+'\nCalculada: '+r['created_at'],'small'),p('Matriz original','section')]
    rows=[['Alternativa A','Alternativa B','Pago A','Pago B']]
    for i in range(2):
        for j in range(2):rows.append([m['strategies'][0][i],m['strategies'][1][j],number(m['a'][i][j]),number(m['b'][i][j])])
    flow.extend([table(rows,[62*mm,62*mm,24*mm,24*mm]),p('Lectura ejecutiva','section'),p(f"Se detectaron {len(r['changes'])} transiciones entre muestras en equilibrios puros, mejores respuestas o existencia de un mixto interior. Estos intervalos no son umbrales exactos; puede haber cambios entre muestras."),p('Los pagos describen preferencias del actor. Las utilidades de A y B se presentan por separado y no se suman ni se clasifican entre sí.')])
    for actor in range(2):
        key='values_a' if actor==0 else 'values_b';best='best_a' if actor==0 else 'best_b'
        flow.extend([PageBreak(),p(f"0{actor+2} / Utilidad de {m['actors'][actor]}",'title'),p('Utilidad esperada de cada estrategia frente a las probabilidades supuestas del rival. Cada gráfico utiliza su propia escala.'),chart(r,actor),p('Verde: '+m['strategies'][actor][0]+'\nVioleta: '+m['strategies'][actor][1],'small'),p('Extremos del rango','section')])
        rows=[['Pago explorado','Utilidad estrategia 1','Utilidad estrategia 2','Mejor respuesta']]
        for sample in [r['points'][0],r['points'][-1]]:
            rows.append([number(sample['value']),number(sample[key][0]),number(sample[key][1]),' o '.join(m['strategies'][actor][k] for k in sample[best])])
        flow.extend([table(rows,[32*mm,37*mm,37*mm,66*mm]),p('Equilibrios puros en los extremos','section')])
        for sample in [r['points'][0],r['points'][-1]]:flow.append(p(f"Pago {number(sample['value'])}: "+('; '.join(pair(v) for v in sample['pure']) or 'ninguno')+'.'))
        flow.append(p('Los porcentajes del equilibrio mixto no sustituyen p/q en estos gráficos. En los empates se conservan todas las mejores respuestas detectadas.','small'))
    flow.extend([PageBreak(),p('04 / Cambios y alcance','title'),p('Intervalos detectados','section')])
    rows=[['Desde','Hasta','Equilibrios puros en la muestra final','Mejor respuesta A / B']]
    for change in r['changes']:
        sample=r['points'][change['index']]
        rows.append([number(change['from']),number(change['to']),'; '.join(pair(v) for v in sample['pure']) or 'Ninguno',' / '.join(' o '.join(m['strategies'][k][v] for v in sample['best_a' if k==0 else 'best_b']) for k in range(2))])
    flow.append(table(rows,[21*mm,21*mm,65*mm,65*mm]) if r['changes'] else p('No se detectaron cambios en las 101 muestras. Esto no demuestra ausencia de cambios entre ellas.'))
    flow.extend([p('Supuestos registrados','section'),p(r['assumptions']),p('Límites de interpretación','section')])
    flow.extend(p('- '+limit,'small') for limit in r['limits'])
    flow.append(p('El CSV complementario conserva los 101 escenarios, incluyendo equilibrios puros y probabilidades del mixto interior cuando existe. Revisá datos y supuestos antes de trasladar resultados a una decisión real.','small'))
    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=19*mm,rightMargin=19*mm,topMargin=20*mm,bottomMargin=20*mm,title=m['title'],author='Escenarios TJ')
    def footer(canvas,document):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED);canvas.drawString(19*mm,11*mm,'ESCENARIOS TJ / Incentivos / Versión guardada');canvas.drawRightString(191*mm,11*mm,str(document.page));canvas.restoreState()
    doc.build(flow,onFirstPage=footer,onLaterPages=footer);return out.getvalue()
