import React,{useEffect,useState} from 'react';
import {policies,type LabRecord,type Cell} from './laboratory-contract';
import {comparisonReplay} from './comparison-replay-contract';
import AgentReplay from './agent-replay';
import Plot from './lab-plot';
const number=(n:number)=>n.toLocaleString('es-AR',{maximumFractionDigits:3});
export default function ComparisonReplay({record,cell,actor}:{record:LabRecord;cell:Cell;actor:number}){
 const [trial,setTrial]=useState(0),[index,setIndex]=useState(0),[result,setResult]=useState<LabRecord>(),[error,setError]=useState(''),[retry,setRetry]=useState(0);
 useEffect(()=>{
  if(!record.seeds)return;
  const controller=new AbortController();setResult(undefined);setError('');setIndex(0);
  async function load(){try{
   const response=await fetch('/api/agent-comparisons/replay',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({id:record.id,i:cell.i,j:cell.j,trial})});
   const value=await response.json();if(!response.ok)throw new Error(value.error||'No se pudo reconstruir la repetición.');
   const parsed=comparisonReplay(value,record,cell,trial);if(!controller.signal.aborted)setResult(parsed);
  }catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Error de conexión.');}}
  void load();return()=>controller.abort();
 },[record,cell,trial,retry]);
 if(!record.seeds)return <p className="notice">Este análisis histórico no conserva las semillas necesarias para reconstruir sus repeticiones.</p>;
 const row=result?.rounds?.[index];
 return <section className="comparison-replay" aria-label="Detalle de la combinación">
  <h3>Explorar una repetición</h3><p>Python reconstruye las rondas con la matriz, las políticas y la semilla conservadas. No crea otra versión del análisis.</p>
  <p className="muted">Comparación de origen: {record.id} · {cell.policies.map(p=>policies[p]||p).join(' / ')}</p>
  <label>Repetición y semilla<select value={trial} onChange={e=>setTrial(Number(e.target.value))}>{record.seeds.map((seed,i)=><option key={i} value={i}>Repetición {i+1} · semilla {seed}</option>)}</select></label>
  {error?<div role="alert" className="error">{error} <button className="secondary" onClick={()=>setRetry(n=>n+1)}>Reintentar reproducción</button></div>:!result?<p role="status">Reconstruyendo las rondas conservadas…</p>:<>
   <Plot index={index} title={`Utilidad acumulada de esta repetición · ${record.model.actors[actor]}`} series={[{name:record.model.actors[actor],color:'#087f70',values:result.rounds!.map(r=>r.totals[actor])}]}/>
   <AgentReplay key={trial} index={index} count={result.rounds!.length} onChange={setIndex} description="Recorrido de las rondas reconstruidas por Python. Estos controles recorren el resultado recibido sin volver a calcular."/>
   {row&&<div className="lab-detail" aria-live="polite"><h3>Decisiones de la ronda {row.round}</h3><div className="tree-form-grid">{record.model.actors.map((name,i)=><div key={i}><strong>{name}</strong><p>{record.model.strategies[i][row.actions[i]]}</p><p>Pago: {number(row.payments[i])} · acumulado: {number(row.totals[i])}</p><p>{row.reasons[i]}</p></div>)}</div></div>}
  </>}
 </section>;
}
