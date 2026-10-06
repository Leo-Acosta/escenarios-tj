export type WorkflowSummary={id:string;title:string;stage:string;revision:number;updated_at:string};
export type Workflow={id:string;title:string;description:string;versions:{version:number;created_at:string}[]};
export type Model={title:string;actors:string[];strategies:string[][];a:number[][];b:number[][];p:number;q:number};
export type Result={model:Model;pure:number[][];mixed:{p:number;q:number}|null;values_a:number[];values_b:number[];best_a:number[];limitations:string[];context?:{assumptions:string;description:string;version:number}};
export type LibraryItem={type:string;label:string;id:string;title:string;actors:string[];created_at:string};
const fail=()=>{throw new Error('La respuesta del servidor no coincide con el contrato esperado.');};
export function object(v:unknown):Record<string,unknown>{return v!==null&&typeof v==='object'&&!Array.isArray(v)?v as Record<string,unknown>:fail();}
const str=(v:unknown):string=>typeof v==='string'?v:fail();
const num=(v:unknown):number=>typeof v==='number'&&Number.isFinite(v)?v:fail();
function list<T>(v:unknown,parse:(x:unknown)=>T):T[]{return Array.isArray(v)?v.map(parse):fail();}
function pair<T>(v:unknown,parse:(x:unknown)=>T):T[]{const a=list(v,parse);return a.length===2?a:fail();}
export function workflows(v:unknown):WorkflowSummary[]{return list(v,x=>{const o=object(x);return {id:str(o.id),title:str(o.title),stage:str(o.stage),revision:num(o.revision),updated_at:str(o.updated_at)};});}
export function workflow(v:unknown):Workflow{const o=object(v);return {id:str(o.id),title:str(o.title),description:str(o.description),versions:list(o.versions,x=>{const z=object(x);return {version:num(z.version),created_at:str(z.created_at)};})};}
export function result(v:unknown):Result{
 const o=object(v),m=object(o.model);const probability=(x:unknown)=>{const n=num(x);return n>=0&&n<=1?n:fail();};
 const index=(x:unknown)=>{const n=num(x);return n===0||n===1?n:fail();};
 const model={title:str(m.title),actors:pair(m.actors,str),strategies:pair(m.strategies,x=>pair(x,str)),a:pair(m.a,x=>pair(x,num)),b:pair(m.b,x=>pair(x,num)),p:probability(m.p),q:probability(m.q)};
 let context:Result['context'];if(o.context){const c=object(o.context);context={assumptions:str(c.assumptions),description:str(c.description),version:num(c.version)};}
 const mixed=o.mixed===null?null:object(o.mixed);
 return {model,pure:list(o.pure,x=>pair(x,index)),mixed:mixed?{p:probability(mixed.p),q:probability(mixed.q)}:null,values_a:pair(o.values_a,num),values_b:pair(o.values_b,num),best_a:list(o.best_a,index),limitations:list(o.limitations,str),context};
}
export function library(v:unknown):{total:number;items:LibraryItem[]}{const o=object(v);return {total:num(o.total),items:list(o.items,x=>{const r=object(x);return {type:str(r.type),label:str(r.label),id:str(r.id),title:str(r.title),actors:pair(r.actors,str),created_at:str(r.created_at)};})};}
export async function get<T>(url:string,parse:(x:unknown)=>T,signal:AbortSignal):Promise<T>{const response=await fetch(url,{signal});const data:unknown=await response.json();if(!response.ok){const o=object(data);throw new Error(typeof o.error==='string'?o.error:'No se pudo completar la consulta.');}return parse(data);}
