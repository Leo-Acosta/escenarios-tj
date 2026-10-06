import {network,type Network} from './network-contract.ts';
export function copyNetwork(graph:Network):Network{return {nodes:graph.nodes.map(n=>({...n})),edges:graph.edges.map(e=>({...e}))};}
export function removeEntity(graph:Network,id:number):Network{
 if(graph.nodes.length<2)throw new Error('La red debe conservar al menos una entidad.');
 if(!graph.nodes.some(n=>n.id===id))throw new Error('Entidad inexistente.');
 return {nodes:graph.nodes.filter(n=>n.id!==id).map((n,i)=>({...n,id:i})),edges:graph.edges.filter(e=>e.a!==id&&e.b!==id).map((e,i)=>({...e,id:i,a:e.a>id?e.a-1:e.a,b:e.b>id?e.b-1:e.b}))};
}
export function addRelation(graph:Network,a:number,b:number,type:string):Network{
 if(graph.edges.length>=1000)throw new Error('Se permiten hasta 1000 relaciones.');
 if(graph.edges.some(e=>e.type===type&&((e.a===a&&e.b===b)||(e.a===b&&e.b===a))))throw new Error('Esta relación ya existe entre las entidades.');
 const result={nodes:graph.nodes,edges:[...graph.edges,{id:graph.edges.length,a,b,type}]};
 network({graph:result});return result;
}
export function reviewedNetwork(graph:Network,title:string,assumptions:string,reviewed:boolean){
 if(!reviewed)throw new Error('Revisá entidades, relaciones y supuestos antes de guardar.');
 if(!title.trim()||title.trim().length>100||!assumptions.trim()||assumptions.trim().length>6000)throw new Error('Completá título y fundamento dentro de los límites.');
 return {graph:network({graph}),title:title.trim(),assumptions:assumptions.trim(),reviewed:true};
}
