import React,{useEffect,useRef,useState} from 'react';

function Viewer({url,title,onClose}:{url:string;title:string;onClose:()=>void}){
 const ref=useRef<HTMLDialogElement>(null);
 useEffect(()=>{const dialog=ref.current!;dialog.showModal();return()=>dialog.close();},[]);
 return <dialog ref={ref} className="report-preview" aria-labelledby="report-preview-title" onCancel={e=>{e.preventDefault();onClose();}}>
  <div className="report-preview-toolbar"><div><p className="eyebrow">INFORME INDIVIDUAL CONSERVADO</p><h2 id="report-preview-title">{title}</h2></div><div><a className="button" href={url} download>Descargar PDF</a><button type="button" autoFocus className="secondary" onClick={onClose}>Cerrar vista previa</button></div></div>
  <p className="muted">Documento generado desde esta versión guardada. Podés imprimirlo con los controles del visor PDF. Si tu navegador no muestra el visor, descargá el archivo para abrirlo.</p>
  <iframe title={`PDF individual: ${title}`} src={url} className="report-preview-frame"/>
 </dialog>;
}

export default function ReportPreview({url,title}:{url:string;title:string}){
 const [open,setOpen]=useState(false);
 return <><button type="button" className="secondary" onClick={()=>setOpen(true)}>Vista previa PDF</button>{open&&<Viewer url={url} title={title} onClose={()=>setOpen(false)}/>}</>;
}
