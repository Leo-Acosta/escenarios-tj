"""Optional visual schema. Legacy graphs retain their original interpretation."""
import math
import re
from datetime import date
from uuid import uuid4
from .workflow import text

STATUSES=('documented_declared','declared','assumed','pending')
PROFILE=('organization','role','description','email','phone','url','source','notes')

def finite(value,limit=100000):
    if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>limit:
        raise ValueError('Coordenada o peso no finito o fuera de rango.')
    return value

def uid(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',value):
        raise ValueError('Identificador estable inválido.')
    return value

def validate(value):
    if not isinstance(value,dict):raise ValueError('Red visual inválida.')
    from .graph import validate_graph
    base=validate_graph({'nodes':[{'id':n['id'],'name':n['name'],'type':n['type']} for n in value['nodes']],
                         'edges':[{k:e[k] for k in ('a','b','type','evidence') if k in e} for e in value['edges']]})
    if value.get('schema')!=2:raise ValueError('Esquema visual incompatible.')
    keys=set();duplicates=set()
    for node,raw in zip(base['nodes'],value['nodes']):
        node['uid']=uid(raw.get('uid'))
        if node['uid'] in keys:raise ValueError('Identificador de entidad duplicado.')
        keys.add(node['uid']);pos=raw.get('position',{})
        node['position']={k:finite(pos.get(k)) for k in ('x','y')}
        node['group']=text(raw.get('group',''),80,False)
        profile=raw.get('profile',{})
        if not isinstance(profile,dict):raise ValueError('Ficha de contacto inválida.')
        node['profile']={k:text(profile.get(k,''),1200 if k in ('description','notes') else 250,False) for k in PROFILE}
        signature=(node['name'].casefold(),node['profile']['organization'].casefold(),node['profile']['role'].casefold())
        if signature in duplicates:raise ValueError('Entidad duplicada: revisá nombre, organización y función.')
        duplicates.add(signature)
        if node['profile']['email'] and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',node['profile']['email']):raise ValueError('Correo de contacto inválido.')
        if node['profile']['url'] and not node['profile']['url'].startswith(('https://','http://')):raise ValueError('El enlace de contacto debe usar http o https.')
    edges=set()
    for edge,raw in zip(base['edges'],value['edges']):
        edge['uid']=uid(raw.get('uid'))
        if edge['uid'] in edges:raise ValueError('Identificador de vínculo duplicado.')
        edges.add(edge['uid'])
        if type(raw.get('directed')) is not bool:raise ValueError('Definí la dirección del vínculo.')
        edge['directed']=raw['directed'];edge['label']=text(raw.get('label',''),120,False)
        edge['status']=raw.get('status')
        if edge['status'] not in STATUSES:raise ValueError('Clasificación de vínculo inválida.')
        if edge['status']=='documented_declared' and not edge.get('evidence'):raise ValueError('El vínculo documentado requiere una referencia de evidencia.')
        for k in ('start','end'):
            edge[k]=text(raw.get(k,''),10,False)
            if edge[k]:date.fromisoformat(edge[k])
        if edge['start'] and edge['end'] and edge['end']<edge['start']:raise ValueError('Fechas de vínculo invertidas.')
        edge['weight']=None
        if raw.get('weight') is not None:
            w=raw['weight']
            if not isinstance(w,dict):raise ValueError('Peso inválido.')
            edge['weight']={'value':finite(w.get('value'),1e6),'unit':text(w.get('unit'),80),'meaning':text(w.get('meaning'),500),'scale':text(w.get('scale'),250)}
        signature=(edge['a'],edge['b'],edge['type'],edge['directed'],edge['label'])
        reverse=(edge['b'],edge['a'],edge['type'],False,edge['label'])
        if any((e['a'],e['b'],e['type'],e['directed'],e['label']) in (signature,reverse if not edge['directed'] else signature) for e in base['edges'][:edge['id']]):raise ValueError('Vínculo duplicado.')
    settings=value.get('settings',{})
    if not isinstance(settings,dict):raise ValueError('Configuración visual inválida.')
    if settings.get('layout') not in ('manual','grid','circle','groups') or type(settings.get('labels')) is not bool:raise ValueError('Configuración visual inválida.')
    clean_settings={'layout':settings['layout'],'labels':settings['labels']}
    if 'viewport' in settings:
        camera=settings['viewport']
        if not isinstance(camera,dict):raise ValueError('Vista del lienzo inválida.')
        clean_settings['viewport']={k:finite(camera.get(k),1e6) for k in ('x','y','zoom')}
        if not .08<=camera['zoom']<=2:raise ValueError('Zoom fuera de rango.')
    return {**base,'schema':2,'settings':clean_settings}

def upgrade(value,identity='legacy'):
    """A new draft, never a mutation of the original. Stable deterministic legacy keys."""
    if value.get('schema')==2:return validate(value)
    from .graph import validate_graph
    g=validate_graph(value)
    for n in g['nodes']:
        n.update(uid=f'{identity}-{n["id"]}'[:80],position={'x':(n['id']%4)*240,'y':(n['id']//4)*145},group='',profile={k:'' for k in PROFILE})
    for e in g['edges']:e.update(uid=str(uuid4()),directed=False,label='',status='assumed',start='',end='',weight=None)
    return {**g,'schema':2,'settings':{'layout':'grid','labels':True}}
