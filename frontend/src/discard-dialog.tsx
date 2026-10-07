import React,{useEffect,useRef} from 'react';

export default function DiscardDialog({onStay,onDiscard}:{onStay:()=>void;onDiscard:()=>void}){
 const dialog=useRef<HTMLDialogElement>(null);
 useEffect(()=>{const element=dialog.current!;element.showModal();return()=>element.close();},[]);
 return <dialog ref={dialog} className="discard-dialog" aria-labelledby="discard-title" aria-describedby="discard-description" onCancel={e=>{e.preventDefault();onStay();}}>
  <h2 id="discard-title">Cambios sin guardar</h2>
  <p id="discard-description">Si salís de esta sección, se descartará el borrador local. Las versiones guardadas permanecen disponibles.</p>
  <div className="tree-actions"><button type="button" autoFocus onClick={onStay}>Seguir editando</button><button type="button" className="secondary" onClick={onDiscard}>Descartar y continuar</button></div>
 </dialog>;
}
