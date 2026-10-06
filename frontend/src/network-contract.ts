import {object} from './contracts.ts';
export const entityTypes=['Institución','Actor','Escenario'];
export type Network={nodes:{id:number;name:string;type:number}[];edges:{id:number;a:number;b:number;type:string}[]};
export function network(value:unknown):Network|null{
 const raw=object(value).graph;if(raw===null)return null;const g=object(raw);
 const fail=():never=>{throw new Error('Red guardada incompatible.');};
 if(!Array.isArray(g.nodes)||!Array.isArray(g.edges)||!g.nodes.length||g.nodes.length>200||g.edges.length>1000)return fail();
 const nodes=g.nodes.map((v,i)=>{const n=object(v);if(n.id!==i||typeof n.name!=='string'||!n.name.trim()||n.name.length>80||![0,1,2].includes(n.type as number))return fail();return {id:i,name:n.name,type:n.type as number};});
 const edges=g.edges.map((v,i)=>{const e=object(v);if(e.id!==i||!Number.isInteger(e.a)||!Number.isInteger(e.b)||(e.a as number)<0||(e.b as number)<0||(e.a as number)>=nodes.length||(e.b as number)>=nodes.length||e.a===e.b||!['Influencia','Cooperación','Participación'].includes(e.type as string))return fail();return {id:i,a:e.a as number,b:e.b as number,type:e.type as string};});
 return {nodes,edges};
}

export type NetworkVersion={id:string;created_at:string;title:string;assumptions:string;graph:Network;workflow?:{id:string;title:string;revision:number}};
export function networkVersion(value:unknown):NetworkVersion{
 const o=object(value),graph=network(o);
 if(!graph||typeof o.id!=='string'||typeof o.created_at!=='string'||typeof o.title!=='string'||typeof o.assumptions!=='string')throw new Error('Versión de red incompatible.');
 const r:NetworkVersion={id:o.id,created_at:o.created_at,title:o.title,assumptions:o.assumptions,graph};
 if(o.workflow!==undefined){const w=object(o.workflow);if(typeof w.id!=='string'||typeof w.title!=='string'||!Number.isSafeInteger(w.revision)||(w.revision as number)<1)throw new Error('Referencia histórica de red incompatible.');r.workflow={id:w.id,title:w.title,revision:w.revision as number};}
 return r;
}
export function networkVersions(value:unknown){if(!Array.isArray(value))throw new Error('Historial de redes incompatible.');return value.map(networkVersion);}
