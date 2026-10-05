/* Red sintética explícita. No representa actores extraídos ni predicciones. */
(()=>{
const svg=document.getElementById('relationship-graph'),get=id=>document.getElementById('network-'+id);
const types=['Institución','Actor','Escenario'],colors=['#fa7855','#4192bb','#8974a7'];
const nodes=Array.from({length:90},(_,id)=>{
 const type=id%3,cluster=Math.floor(id/30),angle=id*2.399963,r=30+Math.sqrt(id%30)*30;
 return {id,type,name:types[type]+' '+String(id+1).padStart(2,'0'),x:290+cluster*155+Math.cos(angle)*r,y:280+(cluster%2)*80+Math.sin(angle)*r};
});
const relations=['Influencia','Cooperación','Participación'];
const edges=[];const keys=new Set();
nodes.forEach(n=>{for(const delta of [1,3,11]){const target=(n.id+delta)%nodes.length,key=[n.id,target].sort((a,b)=>a-b).join('-');if(!keys.has(key)){keys.add(key);edges.push({id:edges.length,a:n.id,b:target,type:relations[(n.id+delta)%3]});}}});
let selected=0,selectedEdge=null,zoom=1,pan={x:0,y:0},drag=null;
function visible(){const type=get('type').value,query=get('search').value.trim().toLocaleLowerCase('es');return nodes.filter(n=>(type==='all'||String(n.type)===type)&&(!query||n.name.toLocaleLowerCase('es').includes(query)));}
function viewport(){const w=900/zoom,h=620/zoom;svg.setAttribute('viewBox',`${(900-w)/2+pan.x} ${(620-h)/2+pan.y} ${w} ${h}`);get('zoom').textContent=Math.round(zoom*100)+' %';}
function render(){
 const shown=visible(),ids=new Set(shown.map(n=>n.id)),neighbors=new Set(edges.filter(e=>e.a===selected||e.b===selected).flatMap(e=>[e.a,e.b]));
 let content='<title>Red demostrativa: 90 entidades y relaciones sintéticas</title><defs><pattern id="network-dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#d8e2ea"/></pattern></defs><rect x="-3000" y="-3000" width="6900" height="6620" fill="#fafcfe"/><rect x="-3000" y="-3000" width="6900" height="6620" fill="url(#network-dots)"/>';
 edges.filter(e=>ids.has(e.a)&&ids.has(e.b)).forEach(e=>{const a=nodes[e.a],b=nodes[e.b],active=e.a===selected||e.b===selected||selectedEdge===e.id;content+=`<g data-edge="${e.id}" role="button" tabindex="0" aria-label="${e.type}: ${a.name} y ${b.name}" class="relationship-action"><title>${e.type}: ${a.name} / ${b.name}</title><line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="${active?'#ea795b':'#b7c4d1'}" stroke-width="${active?1.5:.7}" opacity="${active?.85:.28}"/><line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="transparent" stroke-width="8"/></g>`;});
 shown.forEach(n=>{const active=n.id===selected;content+=`<g data-node="${n.id}" role="button" tabindex="0" aria-label="Seleccionar ${n.name}" aria-pressed="${active}" class="relationship-action"><title>${n.name} · ${types[n.type]}</title>${active?`<circle cx="${n.x}" cy="${n.y}" r="15" fill="${colors[n.type]}" opacity=".12"/><circle cx="${n.x}" cy="${n.y}" r="9" fill="none" stroke="${colors[n.type]}"/>`:''}<circle cx="${n.x}" cy="${n.y}" r="12" fill="transparent"/><circle cx="${n.x}" cy="${n.y}" r="${active?5:3}" fill="${colors[n.type]}"/><text x="${n.x+8}" y="${n.y+3}" font-family="Segoe UI,Arial,sans-serif" font-size="${active?11:8}" fill="${active?'#203547':'#718496'}">${n.name}</text></g>`;});
 svg.innerHTML=content;viewport();
 const detail=get('detail');detail.replaceChildren();
 function line(label,value){const p=document.createElement('p');const b=document.createElement('strong');b.textContent=label+' ';p.append(b,document.createTextNode(value));detail.append(p);}
 if(selectedEdge!==null){const e=edges[selectedEdge];line('Relación:',e.type);line('Origen:',nodes[e.a].name);line('Destino:',nodes[e.b].name);line('Evidencia:','Vínculo generado para esta demostración, sin respaldo documental.');}
 else {const n=nodes[selected];line('Nombre:',n.name);line('Tipo:',types[n.type]);line('Identificador:','DEM-'+String(n.id+1).padStart(3,'0'));line('Conexiones:',String(edges.filter(e=>e.a===n.id||e.b===n.id).length));line('Descripción:','Entidad sintética para explorar la navegación de una red estratégica.');if(!ids.has(selected))line('Estado:','Este nodo está oculto por el filtro actual.');}
 const results=get('results');results.replaceChildren();const count=document.createElement('p');count.textContent=`${shown.length} de ${nodes.length} entidades`;results.append(count);
 shown.slice(0,10).forEach(n=>{const button=document.createElement('button');button.textContent=n.name;button.addEventListener('click',()=>selectNode(n.id,true));results.append(button);});
 if(shown.length>10){const p=document.createElement('p');p.textContent='Usá la búsqueda para encontrar otros nodos.';results.append(p);}
}
function selectNode(id,center=false){selected=id;selectedEdge=null;if(center){pan={x:nodes[id].x-450,y:nodes[id].y-310};zoom=1.6;}render();}
svg.addEventListener('click',event=>{if(drag?.moved)return;const node=event.target.closest('[data-node]'),edge=event.target.closest('[data-edge]');if(node)selectNode(Number(node.dataset.node));else if(edge){selectedEdge=Number(edge.dataset.edge);render();}});
svg.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){const group=event.target.closest('[data-node],[data-edge]');if(group){event.preventDefault();group.dispatchEvent(new MouseEvent('click',{bubbles:true}));svg.querySelector(group.dataset.node!==undefined?`[data-node="${group.dataset.node}"]`:`[data-edge="${group.dataset.edge}"]`)?.focus();}}});
svg.addEventListener('pointerdown',event=>{if(event.target.closest('[data-node],[data-edge]'))return;const rect=svg.getBoundingClientRect();drag={x:event.clientX,y:event.clientY,pan:{...pan},scale:Math.max(900/zoom/rect.width,620/zoom/rect.height),moved:false};svg.setPointerCapture(event.pointerId);});
svg.addEventListener('pointermove',event=>{if(!drag)return;drag.moved=Math.abs(event.clientX-drag.x)+Math.abs(event.clientY-drag.y)>4;pan={x:drag.pan.x-(event.clientX-drag.x)*drag.scale,y:drag.pan.y-(event.clientY-drag.y)*drag.scale};viewport();});
svg.addEventListener('pointerup',()=>setTimeout(()=>{drag=null;},0));svg.addEventListener('pointercancel',()=>{drag=null;});
get('search').addEventListener('input',render);get('type').addEventListener('change',render);
get('plus').addEventListener('click',()=>{zoom=Math.min(4,zoom+.25);viewport();});get('minus').addEventListener('click',()=>{zoom=Math.max(.5,zoom-.25);viewport();});get('reset').addEventListener('click',()=>{zoom=1;pan={x:0,y:0};viewport();});
get('fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.getElementById('relationship-panel').requestFullscreen();}catch{get('fullscreen').textContent='Pantalla completa no disponible';}});
document.addEventListener('fullscreenchange',()=>{get('fullscreen').textContent=document.fullscreenElement?'Salir de pantalla completa':'Pantalla completa';});
get('export').addEventListener('click',()=>{const clone=svg.cloneNode(true);clone.setAttribute('xmlns','http://www.w3.org/2000/svg');clone.setAttribute('viewBox','0 0 900 620');clone.setAttribute('width','900');clone.setAttribute('height','620');const url=URL.createObjectURL(new Blob([clone.outerHTML],{type:'image/svg+xml'}));const link=document.createElement('a');link.href=url;link.download='red-relaciones-demostrativa.svg';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
render();
})();
