"""Informe vectorial A4 basado en el mismo análisis de la interfaz."""
from io import BytesIO
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, String
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from .core import Parameters, analyze

INK = colors.HexColor('#172d3b')
MUTED = colors.HexColor('#526574')
GREEN = colors.HexColor('#20745b')
PURPLE = colors.HexColor('#656da7')
PALE = colors.HexColor('#eef5f2')


def f(value):
    return f'{value:.1f}'.rstrip('0').rstrip('.').replace('.', ',')


def build_pdf(result: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=19*mm, leftMargin=19*mm,
                            topMargin=19*mm, bottomMargin=19*mm, title='Escenarios TJ - Informe ejecutivo', author='Escenarios TJ')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleTJ', fontName='Helvetica-Bold', fontSize=27, leading=31, textColor=INK, spaceAfter=16))
    styles.add(ParagraphStyle(name='SectionTJ', fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=INK, spaceBefore=18, spaceAfter=9))
    styles.add(ParagraphStyle(name='BodyTJ', fontName='Helvetica', fontSize=10, leading=15, textColor=MUTED, spaceAfter=10))
    styles.add(ParagraphStyle(name='SmallTJ', fontName='Helvetica', fontSize=8, leading=12, textColor=MUTED, spaceAfter=7))
    def para(text, name='BodyTJ'):
        return Paragraph(text, styles[name])
    def table(rows, widths):
        t = Table([[para(str(cell),'SmallTJ') for cell in row] for row in rows], colWidths=widths, hAlign='LEFT', repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),
                               ('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),
                               ('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#d8e2e7'))]))
        return t
    p=result['parameters']; q=p['cooperation']; cost=p['cost']; v=result['values']
    flow=[para('LABORATORIO ESTRATÉGICO / CASO 001','SmallTJ'),Spacer(1,8*mm),
          para('Negociación institucional:<br/>incentivos y futuros posibles.','TitleTJ'),
          para('Dos instituciones evalúan cooperar o competir. Análisis ilustrativo con pagos hipotéticos; no constituye una predicción validada.')]
    summary=Table([[para('RESULTADO CONDICIONAL PARA A','SmallTJ')],
                   [para(result['recommendation'],'SectionTJ')],
                   [para(f'Utilidad esperada: cooperar <b>{f(v[0])}</b> puntos; competir <b>{f(v[1])}</b> puntos. La conclusión depende de los supuestos del analista.')]],colWidths=[172*mm])
    summary.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),('TOPPADDING',(0,0),(-1,0),12),('BOTTOMPADDING',(0,-1),(-1,-1),12)]))
    flow.extend([Spacer(1,4*mm),summary,para('01 / Actores y supuestos','SectionTJ')])
    d=Drawing(480,92)
    d.add(Line(100,50,380,50,strokeColor=colors.HexColor('#bbcbd3'),strokeWidth=1))
    for x,name,label,col in [(100,'A','Institución A / decisor',GREEN),(380,'B','Institución B / contraparte',PURPLE)]:
        d.add(Circle(x,50,23,fillColor=col,strokeColor=None));d.add(String(x,43,name,fontName='Helvetica-Bold',fontSize=20,fillColor=colors.white,textAnchor='middle'));d.add(String(x,8,label,fontName='Helvetica',fontSize=9,fillColor=INK,textAnchor='middle'))
    d.add(String(240,65,'Cooperación / competencia',fontSize=9,fillColor=MUTED,textAnchor='middle'))
    flow.extend([d,para(f'Cooperación supuesta de B: <b>{f(q*100)} %</b>. Costo de competir para A: <b>{f(cost)} puntos</b>. La misma conducta de B se supone ante ambas alternativas de A.'),para('02 / Matriz de incentivos','SectionTJ')])
    rows=[['Pagos (A, B)','B coopera','B compite']]
    strategies=['Cooperar','Competir']
    for i,row in enumerate(result['matrix_a']):
        rows.append([f'A: {strategies[i]}']+[f'({f(value)}, {f(result["matrix_b"][i][j])})' for j,value in enumerate(row)])
    flow.append(table(rows,[60*mm,56*mm,56*mm]))
    eq='; '.join(f'A: {strategies[i].lower()}, B: {strategies[j].lower()}' for i,j in result['equilibria'])
    flow.append(para(f'Equilibrio(s) puro(s): {eq}. El equilibrio representa mejores respuestas mutuas; no es la probabilidad observada de ese resultado.','SmallTJ'))
    flow.extend([PageBreak(),para('CONSECUENCIAS / COMPARACIÓN / ALCANCE','SmallTJ'),para('Qué cambia entre escenarios.','TitleTJ'),para('03 / Árbol de consecuencias','SectionTJ')])
    d=Drawing(480,158)
    d.add(Rect(177,128,126,25,fillColor=PALE,strokeColor=GREEN,strokeWidth=.6));d.add(String(240,136,'Institución A',fontSize=10,fillColor=INK,textAnchor='middle'))
    for x,i in [(118,0),(362,1)]:
        d.add(Line(240,128,x,103,strokeColor=colors.HexColor('#98adb8'),strokeWidth=.7))
        d.add(String(x,87,strategies[i],fontName='Helvetica-Bold',fontSize=11,fillColor=GREEN,textAnchor='middle'))
        for y,j in [(55,0),(22,1)]:
            prob=q if j==0 else 1-q
            d.add(Rect(x-112,y-5,224,27,fillColor=colors.HexColor('#f5f7f8'),strokeColor=None))
            d.add(String(x-100,y+5,f'B {strategies[j].lower()} ({f(prob*100)} %)',fontSize=9,fillColor=MUTED))
            d.add(String(x+100,y+5,f'{f(result["matrix_a"][i][j])} pts',fontSize=9,fillColor=INK,textAnchor='end'))
    flow.extend([d,para('04 / Comparación de escenarios','SectionTJ')])
    d=Drawing(480,145); values=[v for s in result['scenarios'] for v in s['values']]; lo=min(0,*values)-1;hi=max(0,*values)+1
    def x(value):return 150+(value-lo)/(hi-lo)*265
    for row,s in enumerate(result['scenarios']):
        y=112-row*39;d.add(String(0,y+3,s['name'],fontSize=9,fillColor=INK))
        d.add(Line(x(0),y-13,x(0),y+20,strokeColor=colors.HexColor('#a8b8c3'),strokeWidth=.5))
        for i,value in enumerate(s['values']):
            yy=y+8-i*15;d.add(Rect(min(x(0),x(value)),yy,max(.5,abs(x(value)-x(0))),8,fillColor=GREEN if i==0 else PURPLE,strokeColor=None));d.add(String(465,yy,f(value),fontSize=9,fillColor=INK,textAnchor='end'))
    for xx,col,label in [(0,GREEN,'Cooperar'),(120,PURPLE,'Competir')]:
        d.add(Rect(xx,0,7,7,fillColor=col,strokeColor=None));d.add(String(xx+13,0,label,fontSize=8,fillColor=MUTED))
    d.add(String(270,0,'Utilidad esperada de A / puntos',fontSize=8,fillColor=MUTED))
    flow.append(d)
    flow.append(table([['Escenario','B coopera','Costo A','Cooperar','Competir']]+[[s['name'],f(s['cooperation']*100)+' %',f(s['cost']),f(s['values'][0]),f(s['values'][1])] for s in result['scenarios']],[62*mm,29*mm,25*mm,28*mm,28*mm]))
    flow.append(para('05 / Evidencia y alcance','SectionTJ'))
    for text in result['assumptions']:flow.append(para('- '+text,'SmallTJ'))
    flow.append(para('El costo cambia la alternativa conveniente en 2 puntos; allí A es indiferente. Validar pagos y conducta con evidencia antes de aplicar el modelo. No se incorporaron datos históricos ni agentes generativos.','SmallTJ'))
    def footer(canvas, document):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#cad7de'));canvas.line(19*mm,15*mm,191*mm,15*mm);canvas.setFont('Helvetica',8);canvas.setFillColor(MUTED);canvas.drawString(19*mm,10*mm,'ESCENARIOS TJ / Modelo 0.1 / Ejemplo sin calibración');canvas.drawRightString(191*mm,10*mm,f'{document.page}');canvas.restoreState()
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)
    return buffer.getvalue()


if __name__ == '__main__':
    destination=Path('output/pdf/informe-ejecutivo-demo.pdf')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(build_pdf(analyze(Parameters())))
    print(destination.resolve())
