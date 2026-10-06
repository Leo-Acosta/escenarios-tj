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
