import React from 'react';
export default class RecoveryBoundary extends React.Component<{children:React.ReactNode},{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 render(){return this.state.failed?<main className="panel session-recovery" role="alert"><p className="eyebrow">CONTINUIDAD DE LA SESIÓN</p><h1>Volvé a abrir el espacio de análisis</h1><p>Un módulo no pudo cargarse o la interfaz se actualizó. Los registros de SQLite y las copias locales conservadas permanecen disponibles.</p><p>Al volver a abrir, seleccioná tu expediente y recuperá el borrador ofrecido. Si antes apareció un error de almacenamiento, esa copia puede no estar disponible.</p><button onClick={()=>window.location.reload()}>Volver a abrir la aplicación</button><a className="button secondary" href="/app/?view=data">Abrir respaldo y recuperación</a></main>:this.props.children;}
}
