import {trees,type TreeRecord} from './tree-contract.ts';
export type TreeDraft={title:string;actors:string[];actions:string[][];payoffs:string[][][];assumptions:string};
export function draftTree(source?:TreeRecord):TreeDraft{return source?{...source.model,actors:[...source.model.actors],actions:source.model.actions.map(r=>[...r]),payoffs:source.model.payoffs.map(r=>r.map(p=>p.map(String)))}:{title:'',actors:['',''],actions:[['',''],['',''],['','']],payoffs:Array.from({length:2},()=>Array.from({length:2},()=>['',''])),assumptions:''};}
export function treePayload(d:TreeDraft,reviewed:boolean){
 if(!reviewed)throw new Error('Confirmá la revisión del modelo antes de guardar.');
 const labels=[d.title,...d.actors,...d.actions.flat()];if(labels.some(s=>!s.trim()||s.length>100))throw new Error('Completá el título, los actores y las decisiones (hasta 100 caracteres).');
 if(d.actions.some(r=>r[0].trim()===r[1].trim()))throw new Error('Las alternativas de cada nodo deben ser distintas.');
 if(!d.assumptions.trim()||d.assumptions.length>6000)throw new Error('Registrá los supuestos y el fundamento de los pagos (hasta 6000 caracteres).');
 const payoffs=d.payoffs.map(r=>r.map(p=>p.map(s=>{const n=Number(s);if(!s.trim()||!Number.isFinite(n)||Math.abs(n)>1e6)throw new Error('Completá los ocho pagos con valores entre -1000000 y 1000000.');return n;})));
 return {...d,payoffs,save:true,reviewed:true};
}
export async function saveTree(d:TreeDraft,reviewed:boolean):Promise<TreeRecord>{const payload=treePayload(d,reviewed);const response=await fetch('/api/sequential',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const value=await response.json();if(!response.ok)throw new Error(typeof value.error==='string'?value.error:'No se pudo guardar el árbol.');return trees([value])[0];}
