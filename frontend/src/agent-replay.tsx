import React,{useEffect,useState} from 'react';

export default function AgentReplay({index,count,onChange}:{index:number;count:number;onChange:(index:number)=>void}){
 const [playing,setPlaying]=useState(false),[delay,setDelay]=useState(1000);
 useEffect(()=>{
  const pause=()=>setPlaying(false);
  const visibility=()=>{if(document.hidden)pause();};
  document.addEventListener('visibilitychange',visibility);
  window.addEventListener('beforeprint',pause);
  return()=>{document.removeEventListener('visibilitychange',visibility);window.removeEventListener('beforeprint',pause);};
 },[]);
 useEffect(()=>{
  if(!playing)return;
  if(index>=count-1){setPlaying(false);return;}
  const timer=window.setTimeout(()=>onChange(index+1),delay);
  return()=>window.clearTimeout(timer);
 },[playing,index,count,delay,onChange]);
 function seek(next:number){setPlaying(false);onChange(next);}
 return <section className="agent-replay" aria-label="Reproducción de agentes">
  <div className="title-row"><h3>Reproducir la interacción</h3><span className="badge">Ronda {index+1} / {count}</span></div>
  <p className="muted">Recorrido de las decisiones conservadas. La reproducción no ejecuta una nueva simulación.</p>
  <div className="replay-controls">
   <button className="secondary" onClick={()=>seek(0)} disabled={index===0&&!playing}>Volver al inicio</button>
   <button className="secondary" onClick={()=>seek(index-1)} disabled={index===0}>Ronda anterior</button>
   <button disabled={count<2} aria-pressed={playing} onClick={()=>{if(playing)setPlaying(false);else{if(index===count-1)onChange(0);setPlaying(true);}}}>{playing?'Pausar':'Reproducir'}</button>
   <button className="secondary" onClick={()=>seek(index+1)} disabled={index===count-1}>Ronda siguiente</button>
   <label>Velocidad<select value={delay} onChange={e=>setDelay(Number(e.target.value))}><option value={2000}>Lenta · 2 segundos</option><option value={1000}>Normal · 1 segundo</option><option value={500}>Rápida · 0,5 segundos</option></select></label>
  </div>
  <label>Ronda seleccionada<input type="range" min={0} max={count-1} value={index} aria-valuetext={`Ronda ${index+1} de ${count}`} onChange={e=>seek(Number(e.target.value))}/></label>
  <p role="status">{playing?'Reproducción en curso':index===count-1?'Última ronda · reproducción finalizada':'Reproducción en pausa'}</p>
 </section>;
}
