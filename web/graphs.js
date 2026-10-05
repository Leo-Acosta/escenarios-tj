/* Gráficos de resultados Python: no estiman probabilidades nuevas. */
let selectedOutcome = 0;
const graphColors = ['#6dd7b8','#a3acff','#f0ba77','#ec90ba'];
const graphNames = ['A coopera / B coopera','A coopera / B compite','A compite / B coopera','A compite / B compite'];
const svgText = (x,y,text,extra='')=>`<text x="${x}" y="${y}" ${extra} fill="#e9edf5" font-family="Segoe UI,Arial,sans-serif" font-size="13">${text}</text>`;
function drawGraphs(){
  if(!result)return;
  const p=result.parameters;
  $('visual-q').value=p.cooperation*100; $('visual-cost').value=p.cost;
  $('visual-q-value').textContent=format(p.cooperation*100)+' %'; $('visual-cost-value').textContent=format(p.cost)+' puntos';
  const outcomes=result.matrix_a.flatMap((row,i)=>row.map((a,j)=>({a,b:result.matrix_b[i][j],i,j,prob:j===0?p.cooperation:1-p.cooperation,eq:result.equilibria.some(e=>e[0]===i&&e[1]===j)})));
  let tree='<rect width="740" height="380" fill="#171e2a"/><title>Árbol de consecuencias: cuatro pagos (A, B)</title>';
  tree+='<rect x="284" y="12" width="172" height="42" rx="6" fill="#263247"/>'+svgText(370,38,'Institución A','text-anchor="middle"');
  for(let i=0;i<2;i++){
    const x=i===0?186:554;
    tree+=`<path d="M370 54 L${x} 98" stroke="#64768e" fill="none"/><rect x="${x-88}" y="98" width="176" height="46" rx="6" fill="#263247"/>`+svgText(x,126,i===0?'A coopera':'A compite','text-anchor="middle"');
    tree+=svgText(x,171,'Utilidad esperada A: '+format(result.values[i]),'text-anchor="middle"');
    for(let j=0;j<2;j++){
      const index=i*2+j,o=outcomes[index],leaf=x+(j===0?-89:89),active=index===selectedOutcome;
      tree+=`<path d="M${x} 182 L${leaf} 226" stroke="${active?graphColors[index]:'#64768e'}" stroke-width="${active?3:1}" fill="none"/>`;
      tree+=svgText(leaf,213,format(o.prob*100)+' %','text-anchor="middle"');
      tree+=`<rect x="${leaf-80}" y="230" width="160" height="106" rx="7" fill="#202a39" stroke="${active?graphColors[index]:'#3a465a'}" stroke-width="${active?2:1}"/>`;
      tree+=svgText(leaf,254,j===0?'B coopera':'B compite','text-anchor="middle"');
      tree+=svgText(leaf,282,`A: ${format(o.a)} · B: ${format(o.b)}`,'text-anchor="middle"');
      tree+=svgText(leaf,309,o.eq?'Equilibrio puro':'Resultado '+(index+1),'text-anchor="middle"');
    }
  }
  $('decision-graph').innerHTML=tree;
  const width=Math.max(280,$('utility-graph').clientWidth||560),height=390,left=58,right=30,top=34,bottom=58;
  const lo=Math.floor(Math.min(0,...outcomes.map(o=>o.a),...outcomes.map(o=>o.b)))-2;
  const hi=Math.ceil(Math.max(0,...outcomes.map(o=>o.a),...outcomes.map(o=>o.b)))+2;
  const X=a=>left+(a-lo)/(hi-lo)*(width-left-right),Y=b=>height-bottom-(b-lo)/(hi-lo)*(height-top-bottom);
  let vector=`<title>Vectores de pagos de los dos actores</title><rect width="${width}" height="${height}" fill="#171e2a"/><defs>`+graphColors.map((c,i)=>`<marker id="vector-arrow-${i}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="${c}"/></marker>`).join('')+'</defs>';
  for(let t=lo;t<=hi;t+=2){vector+=`<path d="M${X(t)} ${top} V${height-bottom} M${left} ${Y(t)} H${width-right}" stroke="#2b3444" fill="none"/>`+svgText(X(t),height-bottom+22,String(t),'text-anchor="middle"')+svgText(left-12,Y(t)+4,String(t),'text-anchor="end"');}
  vector+=`<path d="M${X(0)} ${top} V${height-bottom} M${left} ${Y(0)} H${width-right}" stroke="#8c9bb1" fill="none"/>`;
  outcomes.forEach((o,index)=>{vector+=`<line x1="${X(0)}" y1="${Y(0)}" x2="${X(o.a)}" y2="${Y(o.b)}" stroke="${graphColors[index]}" stroke-width="${index===selectedOutcome?3:1.5}" opacity="${index===selectedOutcome?1:.55}" marker-end="url(#vector-arrow-${index})"/>`;
    if(o.eq)vector+=`<circle cx="${X(o.a)}" cy="${Y(o.b)}" r="13" fill="none" stroke="#e9edf5"/>`;
    vector+=`<circle cx="${X(o.a)}" cy="${Y(o.b)}" r="5" fill="${graphColors[index]}"/>`+svgText(X(o.a)+9,Y(o.b)-9,String(index+1));});
  vector+=svgText((left+width-right)/2,height-10,'Utilidad de A (puntos)','text-anchor="middle"')+svgText(18,height/2,'Utilidad de B (puntos)',`text-anchor="middle" transform="rotate(-90 18 ${height/2})"`);
  $('utility-graph').setAttribute('viewBox',`0 0 ${width} ${height}`);$('utility-graph').innerHTML=vector;
  $('outcome-buttons').innerHTML=graphNames.map((name,index)=>`<button class="secondary outcome-button" data-outcome="${index}" aria-pressed="${index===selectedOutcome}"><span style="color:${graphColors[index]}">● ${index+1}</span> ${name}</button>`).join('');
  const chosen=outcomes[selectedOutcome];
  $('outcome-detail').innerHTML=`<div class="vector-values"><div>Utilidad A<strong>${format(chosen.a)}</strong></div><div>Utilidad B<strong>${format(chosen.b)}</strong></div></div><p>${chosen.eq?'Este resultado es un equilibrio puro de la matriz.':'Este resultado no es un equilibrio puro de la matriz.'}</p>`;
}
document.addEventListener('click',event=>{const button=event.target.closest('[data-outcome]');if(button){selectedOutcome=Number(button.dataset.outcome);drawGraphs();}const exportButton=event.target.closest('[data-export]');if(exportButton){const original=$(exportButton.dataset.export);const svg=original.cloneNode(true);svg.setAttribute('xmlns','http://www.w3.org/2000/svg');const url=URL.createObjectURL(new Blob([svg.outerHTML],{type:'image/svg+xml;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=exportButton.dataset.export+'.svg';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}});
for(const [id,target] of [['visual-q','cooperation'],['visual-cost','cost']])$(id).addEventListener('input',()=>{$(target).value=$(id).value;recalculate();});
new ResizeObserver(()=>{if(activeView==='visual')drawGraphs();}).observe($('utility-graph').parentElement);
