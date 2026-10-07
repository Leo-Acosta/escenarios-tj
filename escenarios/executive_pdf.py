"""PDF A4 vectorial del mismo contenido que la previsualización HTML."""
from io import BytesIO
from pathlib import Path
from datetime import datetime,timezone
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer, Flowable, KeepTogether
from .executive_view import content, primitives

INK='#213846';TEAL='#137f84';PALE='#edf5f5'

def fonts():
    candidates=[(Path('C:/Windows/Fonts/arial.ttf'),Path('C:/Windows/Fonts/arialbd.ttf')),
                (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))]
    for regular,bold in candidates:
        if regular.exists() and bold.exists():
            if 'TJ-Regular' not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont('TJ-Regular',str(regular)));pdfmetrics.registerFont(TTFont('TJ-Bold',str(bold)))
                pdfmetrics.registerFontFamily('TJ-Regular',normal='TJ-Regular',bold='TJ-Bold',italic='TJ-Regular',boldItalic='TJ-Bold')
            return 'TJ-Regular','TJ-Bold'
    return 'Helvetica','Helvetica-Bold'

class VectorChart(Flowable):
    def __init__(self,chart,width,font):
        super().__init__();self.chart=chart;self.width=width;self.height=width*290/720;self.font=font
    def draw(self):
        c=self.canv;c.saveState();c.scale(self.width/720,self.width/720)
        c.setFillColor(colors.HexColor('#f8fbfc'));c.rect(0,0,720,290,fill=1,stroke=0)
        for item in primitives(self.chart):
            kind,*v=item
            if kind=='line':
                c.setStrokeColor(colors.HexColor(v[4]));c.setLineWidth(v[5]);c.line(v[0],290-v[1],v[2],290-v[3])
            elif kind=='rect':
                c.setFillColor(colors.HexColor(v[4]));c.rect(v[0],290-v[1]-v[3],v[2],v[3],fill=1,stroke=0)
            else:
                c.setFillColor(colors.HexColor(v[4]));c.setFont(self.font,v[3]);c.drawString(v[0],290-v[1],v[2])
        c.restoreState()

def build_pdf(record):
    view=content(record);regular,bold=fonts();width=174*mm;out=BytesIO()
    styles={
        'title':ParagraphStyle('CoverTitle',fontName=bold,fontSize=29,leading=35,textColor=colors.white,spaceAfter=18,splitLongWords=True),
        'cover':ParagraphStyle('CoverBody',fontName=regular,fontSize=11,leading=17,textColor=colors.HexColor('#dcf2f0'),spaceAfter=12,splitLongWords=True),
        'section':ParagraphStyle('Section',fontName=bold,fontSize=20,leading=25,textColor=colors.HexColor(INK),spaceAfter=16,keepWithNext=True),
        'body':ParagraphStyle('Body',fontName=regular,fontSize=9.5,leading=14.5,textColor=colors.HexColor(INK),spaceAfter=9,splitLongWords=True),
        'small':ParagraphStyle('Small',fontName=regular,fontSize=7.5,leading=10.5,textColor=colors.HexColor(INK),spaceAfter=4,splitLongWords=True),
        'kicker':ParagraphStyle('Kicker',fontName=bold,fontSize=8,leading=11,textColor=colors.HexColor(TEAL),spaceAfter=9,keepWithNext=True)}
    def p(value,style='body'):return Paragraph(escape(str(value)).replace('\n','<br/>'),styles[style])
    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=22*mm,bottomMargin=20*mm,
                         title=view['title'],author='Escenarios TJ',pageCompression=1,invariant=1)
    flow=[Spacer(1,40*mm),p('ESCENARIOS TJ / INFORME EJECUTIVO','cover'),p(view['title'],'title'),p(view['badge'],'cover'),
          p('Modelos, escenarios y evidencia reunidos desde versiones conservadas.','cover'),Spacer(1,15*mm),
          p('Informe '+view['id'],'cover'),p('Emisión '+view['date'],'cover'),PageBreak(),p('Contenido del informe','section')]
    for i,c in enumerate(view['chapters']):flow.append(p(f"{i+1:02d} / {c['title']}"))
    for i,c in enumerate(view['chapters']):
        flow.extend([PageBreak(),p(f'ESCENARIOS TJ / {i+1:02d}','kicker'),p(c['title'],'section')])
        flow.extend(p(v) for v in c['paragraphs'])
        for t in c['tables']:
            rows=[[p(v,'small') for v in t['headers']]]+[[p(v,'small') for v in row] for row in t['rows']]
            n=len(t['headers']);sizes=[width/n]*n
            if c['title']=='Trazabilidad y límites' and n==3:sizes=[width*.2,width*.32,width*.48]
            table=Table(rows,colWidths=sizes,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(PALE)),('VALIGN',(0,0),(-1,-1),'TOP'),
                                      ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
                                      ('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#cbdce3'))]))
            flow.extend([Spacer(1,4*mm),table])
        for chart in c['charts']:flow.extend([Spacer(1,5*mm),VectorChart(chart,width,regular),Spacer(1,5*mm)])
    def footer(canvas,document):
        canvas.saveState()
        if document.page==1:
            canvas.setFillColor(colors.HexColor('#112b38'));canvas.rect(0,0,*A4,fill=1,stroke=0)
            canvas.setFillColor(colors.HexColor(TEAL));canvas.rect(0,0,8*mm,A4[1],fill=1,stroke=0)
            canvas.setFillColor(colors.HexColor('#dcf2f0'))
        else:
            canvas.setStrokeColor(colors.HexColor('#cbdce3'));canvas.line(18*mm,17*mm,192*mm,17*mm)
            canvas.setFillColor(colors.HexColor('#536a78'))
        canvas.setFont(regular,7.5);canvas.drawString(18*mm,11*mm,'Escenarios TJ / '+view['id'][:8])
        canvas.drawRightString(192*mm,11*mm,'Página '+str(document.page));canvas.restoreState()
    emitted=datetime.fromisoformat(record['created_at']).astimezone(timezone.utc)
    def canvasmaker(*args,**kwargs):
        canvas=Canvas(*args,**kwargs)
        canvas.setDateFormatter(lambda *_:'D:'+emitted.strftime('%Y%m%d%H%M%S')+"+00'00'")
        return canvas
    doc.build(flow,onFirstPage=footer,onLaterPages=footer,canvasmaker=canvasmaker)
    return out.getvalue()
