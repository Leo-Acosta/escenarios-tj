"""Local documentary dossier. Append-only evidence, facts, events and snapshots."""
import base64
import copy
import hashlib
import io
import json
import sqlite3
import zipfile
from contextlib import closing
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path
from uuid import uuid4
from .workflow import get_workflow, now, text, NotFound

MAX_FILE = 5 * 1024 * 1024
MAX_TOTAL = 8 * 1024 * 1024
KINDS = ('document', 'fact', 'event', 'calculation', 'snapshot')
LABELS={'documented_declared':'Documentación declarada','declared':'Declarado','assumed':'Supuesto','pending':'Pendiente',
        'planned':'Planificado','submitted':'Presentado','response':'Respuesta recibida','resolved':'Resuelto','rejected':'Rechazado'}

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()

def connect(path):
    db=sqlite3.connect(path,timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS dossier_records (id TEXT PRIMARY KEY, workflow_id TEXT, kind TEXT, payload TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS dossier_blobs (sha256 TEXT PRIMARY KEY, content BLOB)')
    db.commit()
    return db

def packed(record,db):
    """Physical deduplication only: the analytical record and its hash stay intact."""
    record=copy.deepcopy(record)
    def visit(item):
        body=item['payload']
        if body['kind']=='document':
            raw=base64.b64decode(body.pop('content'),validate=True)
            key=hashlib.sha256(raw).hexdigest()
            if key!=body['file_sha256']:raise ValueError('Original alterado.')
            db.execute('INSERT OR IGNORE INTO dossier_blobs VALUES (?,?)',(key,raw))
            stored=db.execute('SELECT content FROM dossier_blobs WHERE sha256=?',(key,)).fetchone()[0]
            if not isinstance(stored,bytes) or hashlib.sha256(stored).hexdigest()!=key:raise ValueError('Archivo compartido alterado.')
            body['stored_content_sha256']=key
        for child in body.get('records',[]):visit(child)
        for child in body.get('inputs',[]):visit(child)
    visit(record)
    return record

def hydrated(record,db):
    def visit(item):
        body=item['payload']
        if body['kind']=='document' and 'stored_content_sha256' in body:
            key=body.pop('stored_content_sha256')
            row=db.execute('SELECT content FROM dossier_blobs WHERE sha256=?',(key,)).fetchone()
            if not row or not isinstance(row[0],bytes) or hashlib.sha256(row[0]).hexdigest()!=key:raise ValueError('Archivo documental ausente o alterado.')
            body['content']=base64.b64encode(row[0]).decode()
        for child in body.get('records',[]):visit(child)
        for child in body.get('inputs',[]):visit(child)
    visit(record)
    return verify(record)

def deduplicate_storage(path):
    """Explicit maintenance after a backup. Does not change IDs or logical hashes."""
    with closing(connect(path)) as db,db:
        db.execute('BEGIN IMMEDIATE')
        rows=db.execute('SELECT id,payload FROM dossier_records').fetchall()
        for identity,payload in rows:
            original=hydrated(json.loads(payload),db)
            stored=packed(original,db)
            db.execute('UPDATE dossier_records SET payload=? WHERE id=?',(json.dumps(stored,ensure_ascii=False,allow_nan=False),identity))
    return len(rows)

def verify(record):
    if digest(record['payload'])!=record['sha256']:raise ValueError('Registro documental alterado.')
    body=record['payload']
    if body['kind']=='document':
        raw=base64.b64decode(body['content'],validate=True)
        if hashlib.sha256(raw).hexdigest()!=body['file_sha256'] or len(raw)!=body['size']:raise ValueError('Original alterado.')
    if body['kind']=='snapshot':
        for item in body['records']:verify(item)
    if body['kind']=='calculation':
        for item in body['inputs']:verify(item)
        a,b=[r['payload'] for r in body['inputs']]
        days=(date.fromisoformat(b['date'])-date.fromisoformat(a['date'])).days
        difference=Decimal(b['value'].replace(',','.'))-Decimal(a['value'].replace(',','.'))
        result=body['result']
        if result['first_id']!=body['inputs'][0]['id'] or result['last_id']!=body['inputs'][1]['id'] or days<=0 or difference<0 or result['days']!=days or Decimal(result['difference_kwh'])!=difference or Decimal(result['daily_kwh'])!=difference/days:raise ValueError('Cálculo documental inconsistente.')
    return record

def read(path,identity):
    with closing(connect(path)) as db:
        row=db.execute('SELECT payload FROM dossier_records WHERE id=?',(identity,)).fetchone()
        if not row:raise NotFound('Registro documental inexistente.')
        return hydrated(json.loads(row[0]),db)

def records(path,workflow_id):
    get_workflow(path,workflow_id)
    with closing(connect(path)) as db:
        rows=db.execute('SELECT payload FROM dossier_records WHERE workflow_id=? ORDER BY rowid',(workflow_id,)).fetchall()
        return [hydrated(json.loads(r[0]),db) for r in rows]

def active(items,kind):
    superseded={r['payload'].get('supersedes') for r in items}
    return [r for r in items if r['payload']['kind']==kind and r['id'] not in superseded]

def save(path,value):
    if not isinstance(value,dict):raise ValueError('Objeto documental requerido.')
    scope=text(value.get('workflow_id'),40);get_workflow(path,scope)
    kind=value.get('kind')
    if kind not in KINDS:raise ValueError('Tipo documental inválido.')
    previous=records(path,scope)
    body={'kind':kind,'workflow_id':scope}
    if kind=='document':
        name=text(value.get('name'),160)
        if any(c in name for c in '/\\\x00') or name in ('.','..'):raise ValueError('Nombre de archivo inválido.')
        raw=base64.b64decode(value.get('content',''),validate=True)
        if not 0<len(raw)<=MAX_FILE:raise ValueError('Cada documento admite hasta 5 MiB.')
        if sum(r['payload']['size'] for r in previous if r['payload']['kind']=='document')+len(raw)>MAX_TOTAL:raise ValueError('El expediente admite hasta 8 MiB de originales.')
        suffix=Path(name).suffix.lower()
        signatures={'.pdf':(b'%PDF-', 'application/pdf'),'.png':(b'\x89PNG\r\n\x1a\n','image/png'),'.jpg':(b'\xff\xd8\xff','image/jpeg'),'.jpeg':(b'\xff\xd8\xff','image/jpeg')}
        if suffix not in signatures or not raw.startswith(signatures[suffix][0]):raise ValueError('Solo PDF, PNG y JPEG con formato compatible.')
        extracted='';status='manual_required'
        if suffix=='.pdf':
            try:
                from pypdf import PdfReader
                reader=PdfReader(io.BytesIO(raw))
                if len(reader.pages)<=50:
                    extracted='\n'.join((p.extract_text() or '')[:10000] for p in reader.pages)[:30000]
                    status='text_unreviewed' if extracted.strip() else 'scan_manual_required'
            except Exception:status='extraction_unavailable'
        body.update(name=name,mime=signatures[suffix][1],size=len(raw),content=base64.b64encode(raw).decode(),file_sha256=hashlib.sha256(raw).hexdigest(),extracted_text=extracted,extraction_status=status,
                    note=text(value.get('note',''),2000,False))
    elif kind in ('fact','event'):
        if value.get('reviewed') is not True:raise ValueError('Confirmá la revisión del registro.')
        source=value.get('document_id','')
        if source and not any(r['id']==source and r['payload']['kind']=='document' for r in previous):raise ValueError('Documento de otro expediente o inexistente.')
        supersedes=value.get('supersedes','')
        if supersedes and not any(r['id']==supersedes for r in active(previous,kind)):raise ValueError('La corrección debe referir al registro vigente del mismo tipo.')
        body.update(title=text(value.get('title'),200),document_id=source,locator=text(value.get('locator',''),200,False),supersedes=supersedes,reviewed=True)
        try:body['date']=date.fromisoformat(value.get('date','')).isoformat()
        except (ValueError,TypeError):raise ValueError('Fecha de documento/evento requerida en formato AAAA-MM-DD.')
        if kind=='fact':
            evidence=value.get('evidence')
            if evidence not in ('documented_declared','declared','assumed','pending'):raise ValueError('Clasificación de evidencia inválida.')
            if evidence=='documented_declared' and not source:raise ValueError('El dato documental requiere un original.')
            body.update(value=text(value.get('value'),1000),unit=text(value.get('unit'),80),evidence=evidence,uncertainty=text(value.get('uncertainty'),2000))
        else:
            if value.get('status') not in ('planned','submitted','response','resolved','rejected'):raise ValueError('Estado de seguimiento inválido.')
            body.update(actor=text(value.get('actor'),100),status=value['status'],detail=text(value.get('detail'),4000),reference=text(value.get('reference',''),200,False))
    elif kind=='calculation':
        if value.get('reviewed') is not True:raise ValueError('Revisá que ambas lecturas correspondan al mismo medidor.')
        result=consumption(path,scope,value.get('first_id'),value.get('last_id'))
        selected=[read(path,result[key]) for key in ('first_id','last_id')]
        body.update(title='Comparación de lecturas acumuladas',inputs=selected,result=result)
    else:
        if value.get('reviewed') is not True:raise ValueError('Revisá la composición del informe documental.')
        body.update(title=text(value.get('title'),200),records=[r for r in previous if r['payload']['kind']!='snapshot'])
    record={'id':str(uuid4()),'created_at':now(),'payload':body,'sha256':digest(body)}
    verify(record)
    # Serialize append/correction checks to reject concurrent stale corrections.
    with closing(connect(path)) as db,db:
        db.execute('BEGIN IMMEDIATE')
        if kind=='document':
            used=sum(json.loads(r[0])['payload']['size'] for r in db.execute("SELECT payload FROM dossier_records WHERE workflow_id=? AND kind='document'",(scope,)))
            if used+body['size']>MAX_TOTAL:raise ValueError('Límite de originales alcanzado.')
        if body.get('supersedes'):
            for (raw_record,) in db.execute('SELECT payload FROM dossier_records WHERE workflow_id=? AND kind=?',(scope,kind)):
                if json.loads(raw_record)['payload'].get('supersedes')==body['supersedes']:raise ValueError('Este registro ya tiene una corrección.')
        stored=packed(record,db)
        db.execute('INSERT INTO dossier_records VALUES (?,?,?,?)',(record['id'],scope,kind,json.dumps(stored,ensure_ascii=False,allow_nan=False)))
    return record

def summary(path,scope):
    items=records(path,scope)
    # Safe metadata for UI; originals obtained separately, never executable HTML.
    return [{**r,'payload':{k:v for k,v in r['payload'].items() if k not in ('content','records')}} for r in items]

def frozen_context(path,scope):
    items=records(path,scope)
    return {'documents':[{'id':r['id'],'created_at':r['created_at'],**{k:v for k,v in r['payload'].items() if k not in ('content','extracted_text')}} for r in items if r['payload']['kind']=='document'],
            'facts':active(items,'fact'),'events':active(items,'event'),
            'calculations':[r for r in items if r['payload']['kind']=='calculation']}

def consumption(path,scope,first_id,last_id):
    items=active(records(path,scope),'fact')
    def find(identity):
        r=next((r['payload'] for r in items if r['id']==identity),None)
        if not r or r['unit']!='kWh' or r['evidence'] not in ('documented_declared','declared'):raise ValueError('Elegí lecturas revisadas en kWh, no supuestos ni pendientes.')
        try:v=Decimal(r['value'].replace(',','.'))
        except InvalidOperation:raise ValueError('La lectura debe ser numérica, sin separador de miles.')
        if not v.is_finite() or v<0:raise ValueError('Lectura inválida.')
        return r,v
    a,x=find(first_id);b,y=find(last_id);days=(date.fromisoformat(b['date'])-date.fromisoformat(a['date'])).days
    if days<=0 or y<x:raise ValueError('Fechas o lecturas incompatibles; no se asume recambio ni reinicio de medidor.')
    return {'difference_kwh':str(y-x),'days':days,'daily_kwh':str((y-x)/days),'first_id':first_id,'last_id':last_id,
            'limits':['Requiere que ambas lecturas sean del mismo medidor y registro. Fechas declaradas; horas exactas no consideradas. No valida lecturas históricas ni facturación.']}

def report_html(record):
    verify(record)
    if record['payload']['kind']!='snapshot':raise ValueError('Seleccioná un informe congelado.')
    body=record['payload'];items=body['records'];e=lambda x:escape(str(x))
    parts=['<!doctype html><html lang="es"><meta charset="utf-8"><title>'+e(body['title'])+'</title><style>body{font:15px Arial;color:#163451;max-width:900px;margin:40px auto;padding:20px}article{break-inside:avoid;border-bottom:1px solid #ddd;padding:12px 0}img{max-width:100%;max-height:350px}p{white-space:pre-wrap}@page{size:A4;margin:18mm}@media print{button{display:none}body{margin:0;padding:0}}</style><button onclick="window.print()">Imprimir / guardar PDF</button><h1>'+e(body['title'])+'</h1><p>Documentación declarada y seguimiento real. No acredita autenticidad, éxito judicial ni mejora predictiva. Versión congelada: '+e(record['created_at'][:10])+'</p>']
    for kind,label in [('document','Documentos conservados'),('fact','Datos revisados vigentes'),('event','Seguimiento vigente'),('calculation','Cálculos conservados')]:
        parts.append('<h2>'+label+'</h2>')
        selected=[r for r in items if r['payload']['kind']==kind] if kind=='document' else active(items,kind)
        for r in selected:
            b=r['payload'];parts.append('<article><h3>'+e(b.get('title',b.get('name')))+'</h3>')
            if kind=='document':
                parts.append('<p>'+e(b['note'])+'</p>')
                if b['mime'].startswith('image/'):
                    parts.append('<img alt="Archivo conservado; procedencia descrita arriba" src="data:'+b['mime']+';base64,'+b['content']+'">')
            elif kind=='fact':parts.append('<p>'+e(b['date']+' · '+b['value']+' '+b['unit']+' · '+LABELS[b['evidence']])+'</p><p>Fuente: '+e(b['locator'])+'</p><p>Límites: '+e(b['uncertainty'])+'</p>')
            elif kind=='event':parts.append('<p>'+e(b['date']+' · '+b['actor']+' · '+LABELS[b['status']]+' · '+b['reference'])+'</p><p>'+e(b['detail'])+'</p>')
            else:
                result=b['result']
                parts.append('<p>'+e(f"{result['difference_kwh']} kWh en {result['days']} días; {result['daily_kwh']} kWh diarios")+'</p><p>'+e(' '.join(result['limits']))+'</p>')
            parts.append('</article>')
    return ''.join(parts)+'</html>'

def export_zip(record):
    verify(record)
    if record['payload']['kind']!='snapshot':raise ValueError('Informe congelado requerido.')
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('registro.json',json.dumps(record,ensure_ascii=False,indent=2))
        z.writestr('informe.html',report_html(record))
        for i,r in enumerate(record['payload']['records']):
            if r['payload']['kind']=='document':z.writestr(f'originales/{i+1}-{r["payload"]["name"]}',base64.b64decode(r['payload']['content']))
    return out.getvalue()
