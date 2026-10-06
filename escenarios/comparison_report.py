"""Informe vectorial de una comparación guardada, con escalas por actor."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from .agents import POLICIES
from .sequential_report import number, INK, MUTED, GREEN, PALE

LABELS=['Fija 1','Fija 2','Copiar','Cambio','Frecuencia','Azar']

def summaries(record, actor):
    """Rango de medias por rival; no representa probabilidades de conducta."""
    rows=[]
    for policy in range(6):
        values=[c['statistics'][actor]['mean'] for c in record['cells']
                if (c['i'] if actor==0 else c['j'])==policy]
        rows.append({'policy':policy,'minimum':min(values),'maximum':max(values)})
    return rows

def build_pdf(r):
    out=BytesIO();m=r['model'];o=r['options'];width=172*mm
    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=19*mm,rightMargin=19*mm,topMargin=20*mm,bottomMargin=20*mm,title=m['title'],author='Escenarios TJ')
    styles={key:ParagraphStyle(key,fontName=font,fontSize=size,leading=leading,textColor=INK if key in ('title','section') else MUTED,spaceAfter=8,keepWithNext=key=='section')
            for key,font,size,leading in [('title','Helvetica-Bold',23,28),('section','Helvetica-Bold',13,18),('body','Helvetica',9,13),('small','Helvetica',7.5,10)]}
    def p(text,style='body'):return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
    def table(rows,widths):
        t=Table([[p(v,'small') for v in row] for row in rows],colWidths=widths,repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#d6e3e8'))]));return t
    flow=[p('ESCENARIOS TJ / COMPARACIÓN DE CONDUCTAS','small'),p(m['title'],'title'),p('Informe ejecutivo de 36 enfrentamientos. Simulación exploratoria condicionada a pagos y políticas; sin validación predictiva.'),p('01 / Configuración y trazabilidad','section'),p(f"{o['rounds']} rondas por repetición / {o['repetitions']} repeticiones por combinación / semillas {r['seeds'][0]} a {r['seeds'][-1]} / error {number(o['noise']*100)} %."),p('Versión: '+r['id']+'\nMotor: '+r['engine']+' / '+r['agents_engine']+'\nCalculada: '+r['created_at'],'small'),p('Matriz de incentivos conservada','section')]
    rows=[['Alternativa A','Alternativa B','Pago A','Pago B']]
    for i in range(2):
        for j in range(2):rows.append([m['strategies'][0][i],m['strategies'][1][j],number(m['a'][i][j]),number(m['b'][i][j])])
    flow.extend([table(rows,[62*mm,62*mm,24*mm,24*mm]),Spacer(1,4*mm),p('Lectura ejecutiva','section'),p('Las páginas siguientes separan las utilidades de cada actor. El rango por política muestra cómo cambia su media al enfrentar las seis conductas rivales; no supone que esas conductas sean igualmente probables. No permite clasificar A contra B.'),p('Las matrices, semillas y supuestos provienen de la versión guardada. Cambios posteriores en el formulario no alteran este informe.')])
    for actor in range(2):
        flow.extend([PageBreak(),p(f"0{actor+2} / Utilidad de {m['actors'][actor]}",'title'),p('Filas: política de A. Columnas: política de B. Celda: utilidad media por ronda; DE: desviación poblacional entre las semillas ensayadas.','small')])
        vals=[c['statistics'][actor]['mean'] for c in r['cells']];lo=min(vals);hi=max(vals)
        rows=[['A / B']+LABELS]
        for i in range(6):rows.append([LABELS[i]]+[f"{number(r['cells'][i*6+j]['statistics'][actor]['mean'])}\nDE {number(r['cells'][i*6+j]['statistics'][actor]['std'])}" for j in range(6)])
        heat=table(rows,[28*mm]+[24*mm]*6)
        for i in range(6):
            for j in range(6):
                value=r['cells'][i*6+j]['statistics'][actor]['mean'];ratio=(value-lo)/(hi-lo) if hi!=lo else .5
                fill=colors.linearlyInterpolatedColor(colors.HexColor('#eef7f3'),colors.HexColor('#88c9b5'),0,1,ratio)
                heat.setStyle(TableStyle([('BACKGROUND',(j+1,i+1),(j+1,i+1),fill)]))
        flow.extend([heat,p(f"Escala de color propia de este actor: {number(lo)} a {number(hi)} puntos. Los colores de las dos páginas no se comparan entre sí.",'small'),p('Rango frente a las seis políticas rivales','section'),table([['Política propia','Menor media','Mayor media']]+[[LABELS[s['policy']],number(s['minimum']),number(s['maximum'])] for s in summaries(r,actor)],[84*mm,44*mm,44*mm]),p('Este rango describe medias de combinaciones ensayadas. No es un intervalo de confianza, una garantía ni una recomendación automática.','small')])
    flow.extend([PageBreak(),p('04 / Supuestos y alcance','title'),p('Supuestos aportados','section'),p(r['assumptions']),p('Conductas del motor','section'),table([['Código visual','Regla de decisión']]+[[LABELS[i],POLICIES[key]] for i,key in enumerate(r['policies'])],[35*mm,137*mm]),p('Frecuencia utiliza un prior 1/1 y elige la primera alternativa en empates. Copiar comienza por la primera alternativa. Cambio adopta permanentemente la segunda al observarla en el rival.','small'),p('Límites de interpretación','section')])
    for limit in r['limits']:flow.append(p('- '+limit,'small'))
    flow.extend([p('Siguiente decisión del analista','section'),p('Revisar la evidencia de pagos y conductas; abrir combinaciones relevantes para inspeccionar memoria, acciones y errores; contrastar el modelo con datos antes de presentar capacidad predictiva.')])
    def footer(canvas,document):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED);canvas.drawString(19*mm,11*mm,'ESCENARIOS TJ / Comparación guardada');canvas.drawRightString(191*mm,11*mm,str(document.page));canvas.restoreState()
    doc.build(flow,onFirstPage=footer,onLaterPages=footer);return out.getvalue()
