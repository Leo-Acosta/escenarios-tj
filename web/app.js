const $ = id => document.getElementById(id);
const format = n => Number(n).toLocaleString('es-AR', {maximumFractionDigits: 1});
const strategies = ['Cooperar', 'Competir'];
let result, activeView = 'analysis', generation = 0;
function show(view) {
  activeView = view;
  for (const name of ['analysis','report','history','visual']) $(`${name}-view`).hidden = name !== view;
  if(view === 'visual') drawGraphs();
  document.querySelectorAll('[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === view));
  if(view === 'report' && result) renderReport();
  if(view === 'history') loadHistory();
  window.scrollTo({top:0, behavior:'instant'});
}
async function recalculate() {
  const current = ++generation;
  $('save').disabled = true; $('report-open').disabled = true;
  try {
    const response = await fetch(`/api/analysis?q=${Number($('cooperation').value)/100}&cost=${$('cost').value}`);
    if(!response.ok) throw new Error('No se pudo calcular el análisis.');
    const data = await response.json();
    if(current !== generation) return;
    result = data; render(); $('status').textContent = '';
  } catch(e) {if(current === generation) {result = null; $('status').textContent = e.message; $('download-pdf').removeAttribute('href');}}
  finally {if(current === generation) {$('save').disabled = !result; $('report-open').disabled = !result;}}
}
function render() {
  const p = result.parameters;
  $('q-label').textContent = format(p.cooperation*100)+' %'; $('cost-label').textContent = format(p.cost);
  $('recommendation').textContent = result.recommendation;
  $('expected-coop').textContent = format(result.values[0])+' pts'; $('expected-comp').textContent = format(result.values[1])+' pts';
  $('matrix').innerHTML = result.matrix_a.map((row,i)=>`<tr><th>A ${i===0?'coopera':'compite'}</th>${row.map((v,j)=>`<td class="${result.equilibria.some(e=>e[0]===i&&e[1]===j)?'equilibrium':''}">(${format(v)}, ${format(result.matrix_b[i][j])})</td>`).join('')}</tr>`).join('');
  $('equilibrium-label').textContent = result.equilibria.map(e=>`A: ${strategies[e[0]].toLowerCase()} · B: ${strategies[e[1]].toLowerCase()}`).join(' / ');
  for(const id of ['tree-q1','tree-q2']) $(id).textContent = format(p.cooperation*100)+' %';
  for(const id of ['tree-p1','tree-p2']) $(id).textContent = format((1-p.cooperation)*100)+' %';
  $('leaf-a').textContent = format(result.matrix_a[1][0])+' puntos'; $('leaf-b').textContent = format(result.matrix_a[1][1])+' puntos';
  const vals = result.scenarios.flatMap(s=>s.values), min=Math.min(0,...vals)-1,max=Math.max(0,...vals)+1,position=v=>(v-min)/(max-min)*100;
  $('scenario-chart').innerHTML = result.scenarios.map(s=>`<div class="scenario-row"><div class="scenario-title"><strong>${s.name}</strong><small>B: ${format(s.cooperation*100)} % · costo ${format(s.cost)}</small></div><div class="bars" role="img" aria-label="${s.name}: cooperar ${format(s.values[0])}, competir ${format(s.values[1])} puntos"><div class="zero-line" style="left:${position(0)}%"></div>${s.values.map((v,i)=>`<div class="bar ${i===0?'coop':'comp'}" style="left:${Math.min(position(v),position(0))}%;width:${Math.abs(position(v)-position(0))}%"></div>`).join('')}</div><div class="bar-labels">${s.values.map(format).join('<br>')}</div></div>`).join('');
  renderReport();
  drawGraphs();
}
function renderReport() {
  if(window.renderOwnReport?.()) return;
  $('download-pdf').hidden=false;
  const p=result.parameters;
  $('download-pdf').href = `/api/report.pdf?q=${p.cooperation}&cost=${p.cost}`;
  $('executive-report').innerHTML = `<div class="report-brand"><strong>ESCENARIOS TJ</strong><span>INFORME EJECUTIVO · CASO 001</span></div><p class="eyebrow" style="margin-top:30px">EXPLORACIÓN ESTRATÉGICA</p><h1>Negociación institucional:<br>incentivos y futuros posibles.</h1><p>Dos instituciones evalúan cooperar o competir. Este documento compara alternativas bajo pagos hipotéticos y supuestos explícitos.</p><div class="report-summary"><div class="eyebrow">RESULTADO CONDICIONAL PARA A</div><p><strong>${result.recommendation}</strong></p><p>Utilidad esperada: cooperar ${format(result.values[0])} puntos; competir ${format(result.values[1])} puntos. Resultado condicionado al modelo; no es una predicción validada.</p></div><h2>01 / Actores y supuestos</h2><p><b>A:</b> actor decisor; asume el costo de competir. <b>B:</b> contraparte con dos estrategias. Cooperación supuesta de B: ${format(p.cooperation*100)} %. Costo de competir para A: ${format(p.cost)} puntos.</p><h2>02 / Matriz estratégica</h2><table class="report-table"><thead><tr><th>Pagos (A, B)</th><th>B coopera</th><th>B compite</th></tr></thead><tbody>${result.matrix_a.map((row,i)=>`<tr><td>A ${strategies[i].toLowerCase()}</td>${row.map((v,j)=>`<td>(${format(v)}, ${format(result.matrix_b[i][j])})</td>`).join('')}</tr>`).join('')}</tbody></table><p>Equilibrio(s) puro(s): ${$('equilibrium-label').textContent}. El equilibrio y el valor esperado bajo una conducta supuesta de B son análisis diferentes.</p><h2>03 / Árbol de consecuencias</h2><div class="report-tree"><div><b>A coopera</b><br>B coopera (${format(p.cooperation*100)} %): 6 puntos<br>B compite (${format((1-p.cooperation)*100)} %): -4 puntos</div><div><b>A compite</b><br>B coopera (${format(p.cooperation*100)} %): ${format(result.matrix_a[1][0])} puntos<br>B compite (${format((1-p.cooperation)*100)} %): ${format(result.matrix_a[1][1])} puntos</div></div><h2>04 / Comparación de escenarios</h2><table class="report-table"><thead><tr><th>Escenario</th><th>B coopera</th><th>Costo A</th><th>Cooperar</th><th>Competir</th></tr></thead><tbody>${result.scenarios.map(s=>`<tr><td>${s.name}</td><td>${format(s.cooperation*100)} %</td><td>${format(s.cost)}</td><td>${format(s.values[0])}</td><td>${format(s.values[1])}</td></tr>`).join('')}</tbody></table><h2>05 / Evidencia y alcance</h2><ul>${result.assumptions.map(s=>`<li>${s}</li>`).join('')}</ul><p>El costo de competir cambia la alternativa conveniente en 2 puntos; allí A es indiferente. Validar pagos y conducta con evidencia antes de aplicar este modelo a una decisión real.</p><div class="report-footer"><span>Modelo 0.1 · Datos ilustrativos · Elaboración local</span><span>Escenarios TJ</span></div>`;
}
async function loadHistory(){
  try {
    const response = await fetch('/api/history'); if(!response.ok)throw Error(); const history=await response.json();
    $('history-list').replaceChildren();
    if(!history.length){$('history-list').textContent='Todavía no hay análisis guardados.';return;}
    for(const item of history){const section=document.createElement('section');section.className='panel history-item';const text=document.createElement('div');const heading=document.createElement('h2');heading.textContent=`Análisis #${item.id}`;const p=document.createElement('p');p.textContent=`${new Date(item.created_at).toLocaleString('es-AR', {timeZone:'America/Buenos_Aires'})} · cooperación ${format(item.result.parameters.cooperation*100)} % · costo ${format(item.result.parameters.cost)}`;text.append(heading,p);const button=document.createElement('button');button.className='secondary';button.textContent='Abrir análisis';button.addEventListener('click',()=>{$('cooperation').value=item.result.parameters.cooperation*100;$('cost').value=item.result.parameters.cost;recalculate();show('analysis');});section.append(text,button);$('history-list').append(section);}
  }catch{$('history-list').textContent='No se pudo leer el historial.';}
}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>show(b.dataset.view)));
$('report-open').addEventListener('click',()=>{$('report-source').value='demo';show('report');});
$('print').addEventListener('click',()=>window.print());
for(const id of ['cooperation','cost'])$(id).addEventListener('input',recalculate);
for(const actor of ['a','b'])$(`actor-${actor}`).addEventListener('click',()=>{for(const name of ['a','b']){$(`actor-${name}`).classList.toggle('selected',name===actor);$(`actor-${name}`).setAttribute('aria-pressed',String(name===actor));}$('actor-detail').textContent=actor==='a'?'A · Busca maximizar su utilidad. El costo de competir se aplica a este actor.':'B · Busca maximizar su utilidad. Su cooperación se modela como supuesto; competir es su mejor respuesta en esta matriz.';});
$('save').addEventListener('click',async()=>{if(!result)return;$('save').disabled=true;try{const response=await fetch('/api/snapshots',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(result.parameters)});if(!response.ok)throw Error('No se pudo guardar.');const saved=await response.json();$('status').textContent=`Análisis #${saved.id} guardado en este equipo.`;}catch(e){$('status').textContent=e.message;}finally{$('save').disabled=false;}});
recalculate();
