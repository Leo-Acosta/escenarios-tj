/* Gráficos de resultados Python: no estiman probabilidades nuevas. */
let selectedOutcome = 0;
let treeZoom = 1, treePan = {x:0,y:0};
const collapsedBranches = new Set();
const graphColors = ['#6dd7b8','#a3acff','#f0ba77','#ec90ba'];
const graphNames = ['A coopera / B coopera','A coopera / B compite','A compite / B coopera','A compite / B compite'];
const svgText = (x,y,text,extra='')=>`<text x="${x}" y="${y}" ${extra} fill="#e9edf5" font-family="Segoe UI,Arial,sans-serif" font-size="13">${text}</text>`;
function drawGraphs(){
  if(!result)return;
  const p=result.parameters;
  $('visual-q').value=p.cooperation*100; $('visual-cost').value=p.cost;
  $('visual-q-value').textContent=format(p.cooperation*100)+' %'; $('visual-cost-value').textContent=format(p.cost)+' puntos';
  const outcomes=result.matrix_a.flatMap((row,i)=>row.map((a,j)=>({a,b:result.matrix_b[i][j],i,j,prob:j===0?p.cooperation:1-p.cooperation,eq:result.equilibria.some(e=>e[0]===i&&e[1]===j)})));
  let tree='<rect width="740" height="380" fill="#171e2a"/><title>Árbol de consecuencias: cuatro pagos (A, B)</title><defs><linearGradient id="node-surface" x2="0" y2="1"><stop stop-color="#2a3d50"/><stop offset="1" stop-color="#1c2b3b"/></linearGradient></defs>';
  tree+='<rect x="284" y="12" width="172" height="42" rx="6" fill="#263247"/>'+svgText(370,38,'Institución A','text-anchor="middle"');
  for(let i=0;i<2;i++){
    const x=i===0?186:554;
    tree+=`<path d="M370 54 C370 80 ${x} 72 ${x} 98" stroke="${Math.floor(selectedOutcome/2)===i?'#6dd7b8':'#64768e'}" stroke-width="2" fill="none"/><g class="graph-action" data-branch="${i}" role="button" tabindex="0" aria-label="${collapsedBranches.has(i)?'Expandir':'Contraer'} rama ${i===0?'cooperar':'competir'}" aria-expanded="${!collapsedBranches.has(i)}"><rect x="${x-88}" y="98" width="176" height="46" rx="10" fill="url(#node-surface)" stroke="#5c748a"/>`+svgText(x-8,126,i===0?'A coopera':'A compite','text-anchor="middle"')+svgText(x+68,126,collapsedBranches.has(i)?'+':'−','text-anchor="middle"')+'</g>';
    tree+=svgText(x,171,'Utilidad esperada A: '+format(result.values[i]),'text-anchor="middle"');
    for(let j=0;j<2;j++){
      if(collapsedBranches.has(i))continue;
      const index=i*2+j,o=outcomes[index],leaf=x+(j===0?-89:89),active=index===selectedOutcome;
      tree+=`<path d="M${x} 182 C${x} 204 ${leaf} 204 ${leaf} 230" stroke="${active?graphColors[index]:'#64768e'}" stroke-width="${active?3:1}" fill="none"/>`;
      tree+=svgText(leaf,213,format(o.prob*100)+' %','text-anchor="middle"');
      tree+=`<g class="graph-action" data-outcome="${index}" role="button" tabindex="0" aria-label="Seleccionar resultado ${index+1}: ${graphNames[index]}, pagos ${format(o.a)} y ${format(o.b)}" aria-pressed="${active}"><title>${graphNames[index]} · A: ${format(o.a)} · B: ${format(o.b)} · supuesto ${format(o.prob*100)} %</title><rect x="${leaf-80}" y="230" width="160" height="106" rx="12" fill="${active?'#253b40':'#202a39'}" stroke="${active?graphColors[index]:'#3a465a'}" stroke-width="${active?2:1}"/>`;
      tree+=svgText(leaf,254,j===0?'B coopera':'B compite','text-anchor="middle"');
      tree+=svgText(leaf,282,`A: ${format(o.a)} · B: ${format(o.b)}`,'text-anchor="middle"');
      tree+=svgText(leaf,309,o.eq?'Equilibrio puro':'Resultado '+(index+1),'text-anchor="middle"');
      tree+='</g>';
    }
  }
  $('decision-graph').innerHTML=tree;
  applyTreeViewport();
  const width=Math.max(280,$('utility-graph').clientWidth||560),height=450,left=58,right=32,top=32,bottom=58;
  const lo=Math.floor(Math.min(0,...outcomes.map(o=>o.a),...outcomes.map(o=>o.b)))-2;
  const hi=Math.ceil(Math.max(0,...outcomes.map(o=>o.a),...outcomes.map(o=>o.b)))+2;
  const size=Math.min(width-left-right,height-top-bottom),startX=left+(width-left-right-size)/2,startY=top+(height-top-bottom-size)/2;
  const X=a=>startX+(a-lo)/(hi-lo)*size,Y=b=>startY+size-(b-lo)/(hi-lo)*size;
  let vector=`<title>Vectores de pagos de los dos actores</title><rect width="${width}" height="${height}" fill="#171e2a"/><defs>`+graphColors.map((c,i)=>`<marker id="vector-arrow-${i}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="${c}"/></marker>`).join('')+'</defs>';
  vector+=`<rect x="${X(0)}" y="${Y(hi)}" width="${X(hi)-X(0)}" height="${Y(0)-Y(hi)}" fill="#6dd7b8" opacity=".035"/><rect x="${X(lo)}" y="${Y(0)}" width="${X(0)-X(lo)}" height="${Y(lo)-Y(0)}" fill="#ec90ba" opacity=".035"/>`;
  for(let t=lo;t<=hi;t+=2){vector+=`<path d="M${X(t)} ${startY} V${startY+size} M${startX} ${Y(t)} H${startX+size}" stroke="#2b3444" fill="none"/>`+svgText(X(t),startY+size+22,String(t),'text-anchor="middle"')+svgText(startX-12,Y(t)+4,String(t),'text-anchor="end"');}
  vector+=`<path d="M${X(0)} ${startY} V${startY+size} M${startX} ${Y(0)} H${startX+size}" stroke="#8c9bb1" fill="none"/>`;
  outcomes.forEach((o,index)=>{vector+=`<g class="graph-action" data-outcome="${index}" role="button" tabindex="0" aria-label="Seleccionar vector ${index+1}: utilidad A ${format(o.a)}, utilidad B ${format(o.b)}" aria-pressed="${index===selectedOutcome}"><title>${graphNames[index]} · (${format(o.a)}, ${format(o.b)})${o.eq?' · equilibrio puro':''}</title><line x1="${X(0)}" y1="${Y(0)}" x2="${X(o.a)}" y2="${Y(o.b)}" stroke="${graphColors[index]}" stroke-width="${index===selectedOutcome?3:1.5}" opacity="${index===selectedOutcome?1:.4}" marker-end="url(#vector-arrow-${index})"/>`;
    if(o.eq)vector+=`<circle cx="${X(o.a)}" cy="${Y(o.b)}" r="13" fill="none" stroke="#e9edf5"/>`;
    vector+=`<line x1="${X(0)}" y1="${Y(0)}" x2="${X(o.a)}" y2="${Y(o.b)}" stroke="transparent" stroke-width="16"/><circle cx="${X(o.a)}" cy="${Y(o.b)}" r="20" fill="transparent"/><circle cx="${X(o.a)}" cy="${Y(o.b)}" r="6" fill="${graphColors[index]}"/>`+svgText(X(o.a)+12,Y(o.b)-12,String(index+1))+'</g>';});
  vector+=svgText(startX+size/2,height-10,'Utilidad de A (puntos)','text-anchor="middle"')+svgText(startX-42,height/2,'Utilidad de B (puntos)',`text-anchor="middle" transform="rotate(-90 ${startX-42} ${height/2})"`);
  $('utility-graph').setAttribute('viewBox',`0 0 ${width} ${height}`);$('utility-graph').innerHTML=vector;
  $('outcome-buttons').innerHTML=graphNames.map((name,index)=>`<button class="secondary outcome-button" data-outcome="${index}" aria-pressed="${index===selectedOutcome}"><span style="color:${graphColors[index]}">● ${index+1}</span> ${name}</button>`).join('');
  const chosen=outcomes[selectedOutcome];
  $('outcome-detail').innerHTML=`<div class="selected-route">RUTA ${selectedOutcome+1} / ${graphNames[selectedOutcome]}</div><div class="vector-values"><div>Utilidad A<strong>${format(chosen.a)}</strong></div><div>Utilidad B<strong>${format(chosen.b)}</strong></div></div><p>Respuesta supuesta de B: ${format(chosen.prob*100)} %.</p><p>${chosen.eq?'Este resultado es un equilibrio puro de la matriz.':'Este resultado no es un equilibrio puro de la matriz.'}</p><div class="route-reading">${chosen.a>=0&&chosen.b>=0?'Ambos actores obtienen utilidad no negativa.':chosen.a<0&&chosen.b<0?'Ambos actores obtienen utilidad negativa.':'Los beneficios y pérdidas se distribuyen de forma desigual.'}</div>`;
}
document.addEventListener('click',event=>{const button=event.target.closest('[data-outcome]');if(button){selectedOutcome=Number(button.dataset.outcome);const container=button.closest('svg')?.id;drawGraphs();const replacement=container?$(container).querySelector(`[data-outcome="${selectedOutcome}"]`):$('outcome-buttons').querySelector(`[data-outcome="${selectedOutcome}"]`);replacement?.focus({preventScroll:true});}const branch=event.target.closest('[data-branch]');if(branch){const index=Number(branch.dataset.branch);collapsedBranches.has(index)?collapsedBranches.delete(index):collapsedBranches.add(index);drawGraphs();$('decision-graph').querySelector(`[data-branch="${index}"]`)?.focus({preventScroll:true});}const exportButton=event.target.closest('[data-export]');if(exportButton){const original=$(exportButton.dataset.export);const svg=original.cloneNode(true);svg.setAttribute('xmlns','http://www.w3.org/2000/svg');if(original.id==='decision-graph')svg.setAttribute('viewBox','0 0 740 380');const url=URL.createObjectURL(new Blob([svg.outerHTML],{type:'image/svg+xml;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=exportButton.dataset.export+'.svg';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}});
document.addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&event.target.matches('svg [role="button"]')){event.preventDefault();event.target.dispatchEvent(new MouseEvent('click',{bubbles:true}));}});
function applyTreeViewport(){const w=740/treeZoom,h=380/treeZoom;$('decision-graph').setAttribute('viewBox',`${(740-w)/2+treePan.x} ${(380-h)/2+treePan.y} ${w} ${h}`);if($('tree-zoom-label'))$('tree-zoom-label').textContent=Math.round(treeZoom*100)+' %';}
let treeDrag;
$('decision-graph').addEventListener('pointerdown',event=>{if(event.target.closest('[role="button"]'))return;const box=$('decision-graph').getBoundingClientRect();treeDrag={x:event.clientX,y:event.clientY,pan:{...treePan},scale:Math.max(740/treeZoom/box.width,380/treeZoom/box.height)};$('decision-graph').setPointerCapture(event.pointerId);});
$('decision-graph').addEventListener('pointermove',event=>{if(!treeDrag)return;treePan={x:treeDrag.pan.x-(event.clientX-treeDrag.x)*treeDrag.scale,y:treeDrag.pan.y-(event.clientY-treeDrag.y)*treeDrag.scale};applyTreeViewport();});
for(const event of ['pointerup','pointercancel'])$('decision-graph').addEventListener(event,()=>{treeDrag=null;});
document.addEventListener('click',event=>{const control=event.target.closest('[data-tree-zoom]');if(!control)return;const action=control.dataset.treeZoom;if(action==='reset'){treeZoom=1;treePan={x:0,y:0};}else treeZoom=Math.min(2.5,Math.max(.75,treeZoom+(action==='in'?.25:-.25)));applyTreeViewport();});
for(const [id,target] of [['visual-q','cooperation'],['visual-cost','cost']])$(id).addEventListener('input',()=>{$(target).value=$(id).value;recalculate();});
new ResizeObserver(()=>{if(activeView==='visual')drawGraphs();}).observe($('utility-graph').parentElement);
