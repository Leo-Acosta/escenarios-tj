"""Informe vectorial de una corrida inmutable de agentes."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.graphics.shapes import Drawing,Line,PolyLine,String,Rect
from .agents import POLICIES
from .sequential_report import number,INK,MUTED,GREEN,PURPLE,PALE


def build_pdf(r):
    out=BytesIO();width=172*mm;m=r['model'];o=r['options']
    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=19*mm,rightMargin=19*mm,topMargin=22*mm,bottomMargin=22*mm,title=m['title'],author='Escenarios TJ')
    styles=getSampleStyleSheet()
    for name,size,leading,font in [('Title',26,31,'Helvetica-Bold'),('Section',14,19,'Helvetica-Bold'),('Body',10,15,'Helvetica'),('Small',8,12,'Helvetica')]:
        styles.add(ParagraphStyle(name='Agent'+name,fontName=font,fontSize=size,leading=leading,textColor=INK if name in ('Title','Section') else MUTED,spaceAfter=10,spaceBefore=12 if name=='Section' else 0,keepWithNext=name=='Section'))
    def p(text,style='Body'):return Paragraph(escape(str(text)).replace('\n','<br/>'),styles['Agent'+style])
    def table(rows,widths):
        t=Table([[p(v,'Small') for v in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#d6e3e8'))]));return t
    flow=[p('ESCENARIOS TJ / AGENTES CON MEMORIA','Small'),Spacer(1,8*mm),p(m['title'],'Title'),p('Informe ejecutivo de juego repetido. Conductas configuradas por el analista; sin validación predictiva.'),p('01 / Resultado de la corrida','Section')]
    rows=[['Actor','Política','Total de puntos','Media por ronda']]
    for i in range(2):rows.append([m['actors'][i],POLICIES[o['policies'][i]],number(r['totals'][i]),number(r['means'][i])])
    flow.extend([table(rows,[50*mm,65*mm,29*mm,28*mm]),p(f"{o['rounds']} rondas / semilla {o['seed']} / error de ejecución {number(o['noise']*100)} %.",'Small'),p('Un pago mayor representa una preferencia mayor para ese actor. Los totales entre actores no se interpretan como una clasificación si sus escalas no son comparables.','Small'),p('Matriz de incentivos conservada','Section')])
    rows=[['Alternativa A','Alternativa B','Pago A','Pago B']]
    for i in range(2):
        for j in range(2):rows.append([m['strategies'][0][i],m['strategies'][1][j],number(m['a'][i][j]),number(m['b'][i][j])])
    flow.extend([table(rows,[65*mm,65*mm,21*mm,21*mm]),p('Trazabilidad','Section'),p('Corrida: '+r['id']+'\nMotor: '+r['engine']+'\nCalculada: '+r['created_at'],'Small'),p('Los datos de esta corrida guardada son independientes de cambios posteriores en el formulario. El CSV complementario conserva todas las rondas, motivos y memoria previa.','Small'),p('Próximos pasos','Section'),p('Contrastar pagos y políticas con observaciones, comparar varias semillas si hay azar y evaluar alternativas antes de aplicar el resultado a una decisión real. Una corrida aislada no estima probabilidades empíricas.','Small'),PageBreak(),p('02 / Evolución y alcance','Title')])
    d=Drawing(width,230);values=[0]+[v for row in r['rounds'] for v in row['totals']];lo=min(values);hi=max(values);span=hi-lo or 1
    def x(index):return 35+(width-50)*index/o['rounds']
    def y(value):return 35+160*(value-lo)/span
    d.add(Line(x(0),y(0),x(o['rounds']),y(0),strokeColor=colors.HexColor('#a0b6c0')))
    for i,color in [(0,GREEN),(1,PURPLE)]:
        points=[x(0),y(0)]
        for index,row in enumerate(r['rounds']):points.extend([x(index+1),y(row['totals'][i])])
        d.add(PolyLine(points,strokeColor=color,strokeWidth=2,fillColor=None))
    for yy,value in [(195,hi),(35,lo)]:d.add(String(0,yy,number(value),fontName='Helvetica',fontSize=8,fillColor=MUTED))
    d.add(String(35,15,'Inicio',fontName='Helvetica',fontSize=8,fillColor=MUTED));d.add(String(width-15,15,'Ronda '+str(o['rounds']),fontName='Helvetica',fontSize=8,fillColor=MUTED,textAnchor='end'))
    d.add(String(35,215,'A / línea verde',fontName='Helvetica',fontSize=9,fillColor=GREEN));d.add(String(200,215,'B / línea violeta',fontName='Helvetica',fontSize=9,fillColor=PURPLE))
    flow.extend([d,p('Pagos acumulados por ronda. El gráfico parte de cero; no aplica descuento temporal.','Small'),p('Frecuencia de acciones ejecutadas','Section'),table([['Actor','Alternativa 1','Alternativa 2']]+[[m['actors'][i],str(r['action_counts'][i][0]),str(r['action_counts'][i][1])] for i in range(2)],[72*mm,50*mm,50*mm]),p('Supuestos aportados','Section'),p(r['assumptions'])])
    for limit in r['limits']:flow.append(p('- '+limit,'Small'))
    flow.extend([PageBreak(),p('03 / Muestra de decisiones','Title'),p('Primeras diez y últimas diez rondas, sin duplicados. Los códigos 1/2 identifican alternativas de cada actor según la matriz. El CSV incluye la traza completa.','Small')])
    indices=sorted(set(range(min(10,len(r['rounds']))))|set(range(max(0,len(r['rounds'])-10),len(r['rounds']))))
    rows=[['Ronda','Intención A/B','Acción A/B','Pago A/B','Total A/B','Memoria previa']]
    for index in indices:
        row=r['rounds'][index]
        rows.append([str(row['round']),' / '.join(str(v+1) for v in row['intended']),' / '.join(str(v+1) for v in row['actions']),' / '.join(number(v) for v in row['payments']),' / '.join(number(v) for v in row['totals']),str(row['memory'][0]['observed_rounds'])+' rondas'])
    flow.extend([table(rows,[15*mm,28*mm,28*mm,31*mm,38*mm,32*mm]),p('Memoria previa = cantidad de rondas terminadas que los agentes podían observar antes de decidir. Una diferencia entre intención y acción indica error de ejecución.','Small')])
    def footer(canvas,document):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d2dfe5'));canvas.line(19*mm,16*mm,191*mm,16*mm);canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED);canvas.drawString(19*mm,11*mm,'ESCENARIOS TJ / Agentes / Corrida guardada');canvas.drawRightString(191*mm,11*mm,str(document.page));canvas.restoreState()
    doc.build(flow,onFirstPage=footer,onLaterPages=footer);return out.getvalue()
