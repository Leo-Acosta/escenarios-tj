import {useState} from 'react';
export default function ScientificPanel({identity,version}:{identity:string;version:string}) {
 const [busy,setBusy]=useState(false),[error,setError]=useState('');
 async function download(){setBusy(true);setError('');try{
  const response=await fetch('/api/scientific/bundle?'+new URLSearchParams({workflow_id:identity,version}));
  if(!response.ok)throw new Error('No se pudo preparar la versión científica.');
  const url=URL.createObjectURL(await response.blob()),a=document.createElement('a');a.href=url;a.download=`laboratorio-cientifico-v${version}.zip`;a.click();URL.revokeObjectURL(url);
 }catch(e){setError(e instanceof Error?e.message:'Error de exportación.');}finally{setBusy(false);}}
 return <aside className="scientific-panel"><div><p className="eyebrow">LABORATORIO CIENTÍFICO / R</p><h3>De la exploración al gráfico publicable</h3><p>Conservá esta matriz y sus corridas en un paquete con gráficos de puntos, sensibilidad, barras y distribuciones. PDF vectorial y PNG de alta resolución, con títulos en español.</p><p className="muted">Incluye recetas de optimización, redes, simulación por eventos y evaluación temporal. Se ejecutan en un entorno R externo. El aprendizaje requiere datos observados revisados; las simulaciones no acreditan mejora predictiva.</p></div><div><button className="secondary" disabled={busy||!identity||!version} onClick={download}>{busy?'Preparando…':'Descargar laboratorio R'}</button><p className="muted">CSV · scripts R · versión congelada · manifiesto de integridad</p>{error&&<p role="alert">{error}</p>}</div></aside>;
}
