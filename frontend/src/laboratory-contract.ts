import {object,type Model} from './contracts.ts';
export type Kind='agents'|'comparison'|'sweep';
export const labels:Record<Kind,string>={agents:'Agentes con memoria',comparison:'Comparación de políticas',sweep:'Exploración de incentivos'};
export const policies:Record<string,string>={fixed0:'Siempre alternativa 1',fixed1:'Siempre alternativa 2',mirror:'Copiar última alternativa rival',trigger:'Cambiar tras alternativa 2 rival',adaptive:'Respuesta a frecuencias observadas',random:'Aleatorio 50 / 50'};
export type Round={round:number;actions:number[];payments:number[];totals:number[];reasons:string[]};
export type Cell={i:number;j:number;policies:string[];statistics:{mean:number;std:number;min:number;max:number}[]};
export type Point={value:number;values_a:number[];values_b:number[];pure:number[][]};
export type LabRecord={id:string;created_at:string;model:Model;assumptions:string;limits:string[];workflow?:{id:string;title:string;version:number};rounds?:Round[];cells?:Cell[];points?:Point[];options:Record<string,unknown>;seeds?:number[]};
const fail=():never=>{throw new Error('Respuesta incompatible del laboratorio.');};
const str=(v:unknown):string=>typeof v==='string'?v:fail();
const num=(v:unknown):number=>typeof v==='number'&&Number.isFinite(v)?v:fail();
const idx=(v:unknown)=>v===0||v===1?v:fail();
const integer=(v:unknown)=>typeof v==='number'&&Number.isSafeInteger(v)&&v>=0?v:fail();
function list<T>(v:unknown,p:(x:unknown)=>T):T[]{return Array.isArray(v)?v.map(p):fail();}
function pair<T>(v:unknown,p:(x:unknown)=>T){const a=list(v,p);return a.length===2?a:fail();}
export function laboratory(v:unknown,kind:Kind):LabRecord{const o=object(v),m=object(o.model);const model={title:str(m.title),actors:pair(m.actors,str),strategies:pair(m.strategies,x=>pair(x,str)),a:pair(m.a,x=>pair(x,num)),b:pair(m.b,x=>pair(x,num)),p:num(m.p),q:num(m.q)};if(model.p<0||model.p>1||model.q<0||model.q>1)fail();const r:LabRecord={id:str(o.id),created_at:str(o.created_at),model,assumptions:str(o.assumptions),limits:list(o.limits,str),options:object(o.options)};if(o.workflow){const w=object(o.workflow);r.workflow={id:str(w.id),title:str(w.title),version:integer(w.version)};if(!r.workflow.version)fail();}
 if(kind==='agents')r.rounds=list(o.rounds,x=>{const a=object(x);return {round:integer(a.round),actions:pair(a.actions,idx),payments:pair(a.payments,num),totals:pair(a.totals,num),reasons:pair(a.reasons,str)};});
 if(kind==='comparison'&&o.seeds!==undefined){r.seeds=list(o.seeds,integer);if(!r.seeds.length||r.seeds.some(s=>s>4294967295))fail();}
 if(kind==='comparison')r.cells=list(o.cells,x=>{const a=object(x);return {i:integer(a.i),j:integer(a.j),policies:pair(a.policies,str),statistics:pair(a.statistics,x=>{const s=object(x);return {mean:num(s.mean),std:num(s.std),min:num(s.min),max:num(s.max)};})};});
 if(kind==='sweep')r.points=list(o.points,x=>{const p=object(x);return {value:num(p.value),values_a:pair(p.values_a,num),values_b:pair(p.values_b,num),pure:list(p.pure,x=>pair(x,idx))};});
 if(!(r.rounds||r.cells||r.points)?.length)fail();return r;
}
export function records(v:unknown,kind:Kind){return list(v,x=>laboratory(x,kind));}
