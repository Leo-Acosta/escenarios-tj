"""Vector exports and readable report tiles from frozen networks."""
from html import escape
import math
from .visual_graph import upgrade

STATUS={'documented_declared':'Documentación declarada','declared':'Declarado','assumed':'Hipótesis','pending':'Pendiente'}

def svg(record):
    from .graph import verify_version
    verify_version(record);g=upgrade(record['graph'],record['id']);nodes=g['nodes'];pos={n['id']:n['position'] for n in nodes}
    lo_x=min(p['x'] for p in pos.values());lo_y=min(p['y'] for p in pos.values());span_x=max(p['x'] for p in pos.values())-lo_x+220;span_y=max(p['y'] for p in pos.values())-lo_y+100
    width=max(900,span_x+80);height=max(500,span_y+160)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Red conservada"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#224b76"/></marker></defs>',f'<rect width="100%" height="100%" fill="white"/><text x="40" y="35" font-size="22" font-family="Arial" fill="#163451">{escape(record["title"])}</text>']
    def point(i):p=pos[i];return p['x']-lo_x+135,p['y']-lo_y+145
    for e in g['edges']:
        a,b=point(e['a']),point(e['b']);arrow=' marker-end="url(#arrow)"' if e['directed'] else ''
        parts.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#8098b0" stroke-width="2"{arrow}/>')
        if g['settings']['labels']:parts.append(f'<text x="{(a[0]+b[0])/2}" y="{(a[1]+b[1])/2-8}" font-size="12" font-family="Arial" fill="#355374">{escape(e["label"] or e["type"])}</text>')
    for n in nodes:
        x,y=point(n['id']);parts.append(f'<rect x="{x-95}" y="{y-25}" width="190" height="50" rx="9" fill="#f0f5fa" stroke="#163451"/><text x="{x}" y="{y+4}" text-anchor="middle" font-size="13" font-family="Arial" fill="#163451">N{n["id"]+1} {escape(n["name"][:27])}</text>')
    parts.append(f'<text x="40" y="{height-20}" font-size="12" font-family="Arial" fill="#53677b">Flechas: dirección declarada. Sin causalidad ni probabilidad inferida. Etiquetas completas en JSON.</text></svg>')
    return ''.join(parts)

def chapters(record):
    g=record['graph'];nodes=g['nodes'];tables=[]
    rows=[]
    for n in nodes:
        profile=n.get('profile',{});rows.append([f'N{n["id"]+1}',n['name'],n.get('group','') or 'Sin grupo',profile.get('organization',''),profile.get('role','')])
    tables.append({'headers':['Nodo','Entidad','Grupo','Organización','Función'],'rows':rows})
    links=[]
    for e in g['edges']:
        w=e.get('weight');ev=e.get('evidence',{})
        links.append([f'N{e["a"]+1} '+('→' if e.get('directed') else '↔')+f' N{e["b"]+1}',e.get('label') or e['type'],
                      STATUS.get(e.get('status'),'Hipótesis')+(' · '+ev['reference'] if ev.get('reference') else ''),
                      (f'{w["value"]} {w["unit"]}' if w else 'Sin peso')+'; '+(' a '.join(x for x in [e.get('start'),e.get('end')] if x) or 'Sin fechas')])
    tables.append({'headers':['Conexión','Etiqueta','Evidencia y referencia','Peso y fechas'],'rows':links})
    charts=[{'type':'network','title':f'Mapa de relaciones · lámina {i//12+1}','nodes':nodes[i:i+12],'edges':g['edges'],'unit':'Números remiten al inventario. Distribución adaptada para impresión.'} for i in range(0,len(nodes),12)]
    return {'tables':tables,'charts':charts,'paragraphs':[record['title'],'Supuestos: '+record['assumptions'],
        'Red congelada. Flechas indican dirección declarada, no causalidad estimada. Un peso no es una probabilidad.',
        'Mapas divididos en láminas de hasta doce nodos para mantener legibilidad. Los vínculos entre láminas figuran en la tabla completa; no se omiten del registro.',
        'La distribución del PDF se adapta a la página; el SVG y JSON conservan las posiciones del lienzo. Tipos: institución, actor y escenario.',
        'Fuentes de vínculos declaradas: '+'; '.join(sorted({e['evidence']['source'] for e in g['edges'] if e.get('evidence')}))+'. Notas completas y fichas en JSON.',
        *[f"Peso de N{e['a']+1} a N{e['b']+1}: {e['weight']['meaning']}. Escala: {e['weight']['scale']}." for e in g['edges'] if e.get('weight')]]}
