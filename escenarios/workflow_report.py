"""Informe individual de una matriz calculada, usando solo su versión congelada."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer


def build_pdf(result):
    out=BytesIO();m=result['model'];c=result['context'];width=172*mm
    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=19*mm,rightMargin=19*mm,topMargin=22*mm,bottomMargin=22*mm,title=m['title'],author='Escenarios TJ')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TJTitle',fontSize=25,leading=30,textColor=colors.HexColor('#193140'),spaceAfter=18))
    styles.add(ParagraphStyle(name='TJSection',fontSize=13,leading=18,spaceBefore=15,spaceAfter=8,keepWithNext=True,textColor=colors.HexColor('#087f78')))
    styles.add(ParagraphStyle(name='TJBody',fontSize=10,leading=15,spaceAfter=8,splitLongWords=True))
    styles.add(ParagraphStyle(name='TJSmall',fontSize=8,leading=12,spaceAfter=6,splitLongWords=True))
    def p(text,style='TJBody'):return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
    def number(v):return format(v,'.3f').rstrip('0').rstrip('.').replace('.',',')
    def table(rows,widths):
        t=Table([[p(v,'TJSmall') for v in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf5f2')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#d6e3e8'))]))
        return t
    flow=[p('ESCENARIOS TJ / INFORME INDIVIDUAL DE MATRIZ','TJSmall'),p(m['title'],'TJTitle'),p(f"Versión conservada {c['version']} · expediente {c['workflow_id']}",'TJSmall'),p('Análisis exploratorio condicionado a los pagos y probabilidades del analista. No constituye una predicción calibrada.'),p('01 / Actores y matriz','TJSection'),p(f"A: {m['actors'][0]} · B: {m['actors'][1]}"),p(f"Probabilidades de primera estrategia: p = {number(m['p'])}; q = {number(m['q'])}."),table([['A / B',*m['strategies'][1]],*[[m['strategies'][0][i],*[f"{number(m['a'][i][j])} / {number(m['b'][i][j])}" for j in range(2)]] for i in range(2)]],[60*mm,56*mm,56*mm]),p('02 / Utilidades y equilibrios','TJSection'),table([['Actor','Alternativa','Utilidad esperada'],*[[m['actors'][a],m['strategies'][a][i],number(result['values_a' if a==0 else 'values_b'][i])] for a in range(2) for i in range(2)]],[42*mm,90*mm,40*mm])]
    flow.append(p('Equilibrios puros: '+(' / '.join(f"{m['strategies'][0][i]} <-> {m['strategies'][1][j]}" for i,j in result['pure']) or 'Ninguno.')))
    mixed=result['mixed'];flow.append(p(f"Equilibrio mixto interior: p = {number(mixed['p'])}; q = {number(mixed['q'])}." if mixed else 'No se identifica un equilibrio mixto interior aislado.'))
    flow.extend([PageBreak(),p('03 / Contexto y fundamentos','TJSection'),p(c['description']),p('Supuestos conservados','TJSection'),p(c['assumptions'])])
    labels={'objective':'Objetivo','horizon':'Horizonte','facts':'Hechos y datos pendientes','payoff_basis':'Fundamento de pagos','probability_basis':'Fundamento de probabilidades'}
    for key,value in c.get('answers',{}).items():flow.extend([p(labels.get(key,key),'TJSection'),p(value)])
    flow.append(p('Fuentes aportadas por el analista','TJSection'))
    for evidence in c.get('evidence',[]):flow.extend([p(evidence['title']),p(evidence['reference'],'TJSmall'),p(evidence['claim']),p('Contenido aportado por el analista; no verificado automáticamente.','TJSmall')])
    if not c.get('evidence'):flow.append(p('No se aportaron fuentes para esta versión.'))
    flow.append(p('04 / Alcance y trazabilidad','TJSection'))
    flow.extend(p(v) for v in result['limitations'])
    flow.append(p(f"Revisión del análisis: {c.get('reviewed_at','No registrada')}. Modo: {c.get('mode','guided')}.",'TJSmall'))
    def footer(canvas,document):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#526574'));canvas.drawString(19*mm,12*mm,f"Escenarios TJ - matriz - versión {c['version']}");canvas.drawRightString(191*mm,12*mm,f'Página {document.page}');canvas.restoreState()
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
