import {object} from './contracts.ts';
export type SimulationRecord={version:string;options:{iterations:number;seed:number;radius:number};decision_counts:number[];decision_frequencies:number[];route_counts:number[][];utility_a:{lower_p05:number;upper_p95:number;lower_mean:number;upper_mean:number};preview:{iteration:number;payoffs:number[][][];outcomes:number[][]}[];assumptions:string[]};
export type TreeRecord={simulation?:SimulationRecord;workflow?:{id:string;title:string;revision:number};id:string;calculated_at:string;method:string;limits:string[];model:{title:string;actors:string[];actions:string[][];payoffs:number[][][];assumptions:string};responses:number[][];equilibria:{first:number;responses:number[];outcome:number[];payoffs:number[]}[]};
const fail=():never=>{throw new Error('El árbol recibido no cumple el contrato esperado.');};
const str=(v:unknown):string=>typeof v==='string'?v:fail();
const num=(v:unknown):number=>typeof v==='number'&&Number.isFinite(v)?v:fail();
const index=(v:unknown):number=>v===0||v===1?v:fail();
function list<T>(v:unknown,p:(x:unknown)=>T):T[]{return Array.isArray(v)?v.map(p):fail();}
function sized<T>(v:unknown,n:number,p:(x:unknown)=>T):T[]{const a=list(v,p);return a.length===n?a:fail();}
export function simulationRecord(v:unknown):SimulationRecord{
 const s=object(v),o=object(s.options),u=object(s.utility_a);
 const integer=(v:unknown,min:number,max:number)=>{const n=num(v);return Number.isInteger(n)&&n>=min&&n<=max?n:fail();};
 const iterations=integer(o.iterations,100,5000),seed=integer(o.seed,0,4294967295),radius=num(o.radius);if(radius<0||radius>1e6||s.version!=='uniform-independent-v1')fail();
 const counts=sized(s.decision_counts,3,v=>integer(v,0,iterations)),frequencies=sized(s.decision_frequencies,3,num);if(counts.reduce((a,b)=>a+b,0)!==iterations||frequencies.some((f,i)=>Math.abs(f-counts[i]/iterations)>1e-9))fail();
 const preview=list(s.preview,x=>{const p=object(x);const outcomes=list(p.outcomes,x=>sized(x,2,index));if(!outcomes.length||outcomes.length>4)fail();return {iteration:integer(p.iteration,1,iterations),payoffs:sized(p.payoffs,2,x=>sized(x,2,y=>sized(y,2,num))),outcomes};});if(preview.length>20)fail();
 return {version:str(s.version),options:{iterations,seed,radius},decision_counts:counts,decision_frequencies:frequencies,route_counts:sized(s.route_counts,2,x=>sized(x,2,v=>integer(v,0,iterations))),utility_a:{lower_p05:num(u.lower_p05),upper_p95:num(u.upper_p95),lower_mean:num(u.lower_mean),upper_mean:num(u.upper_mean)},preview,assumptions:list(s.assumptions,str)};
}
export function trees(v:unknown):TreeRecord[]{return list(v,x=>{const o=object(x),m=object(o.model);const equilibria=list(o.equilibria,x=>{const e=object(x);return {first:index(e.first),responses:sized(e.responses,2,index),outcome:sized(e.outcome,2,index),payoffs:sized(e.payoffs,2,num)};});if(!equilibria.length)fail();return {...(o.simulation!==undefined?{simulation:simulationRecord(o.simulation)}:{}),...(o.workflow?{workflow:(()=>{const w=object(o.workflow);return {id:str(w.id),title:str(w.title),revision:num(w.revision)};})()}:{}),id:str(o.id),calculated_at:str(o.calculated_at),method:str(o.method),limits:list(o.limits,str),model:{title:str(m.title),actors:sized(m.actors,2,str),actions:sized(m.actions,3,x=>sized(x,2,str)),payoffs:sized(m.payoffs,2,x=>sized(x,2,y=>sized(y,2,num))),assumptions:str(m.assumptions)},responses:sized(o.responses,2,x=>list(x,index)),equilibria};});}
// This adapter displays saved Python results; it never solves the game.
export function treeGraph(t:TreeRecord,choice:number|null,preview?:SimulationRecord['preview'][number]){
 const paths=preview?preview.outcomes.map(outcome=>({first:outcome[0],outcome})):choice===null?t.equilibria:[t.equilibria[choice]];
 const payoffs=preview?.payoffs||t.model.payoffs;
 const nodes=[{id:'root',position:{x:420,y:0},data:{label:t.model.actors[0]}}];
 const edges:{id:string;source:string;target:string;label:string;style:{stroke:string;strokeWidth:number}}[]=[];
 for(let i=0;i<2;i++){nodes.push({id:`b${i}`,position:{x:120+i*600,y:180},data:{label:t.model.actors[1]}});const active=paths.some(e=>e.first===i);edges.push({id:`a${i}`,source:'root',target:`b${i}`,label:t.model.actions[0][i],style:{stroke:active?'#087f70':'#a5b2bd',strokeWidth:active?3:1}});
 for(let j=0;j<2;j++){const active=paths.some(e=>e.outcome[0]===i&&e.outcome[1]===j);nodes.push({id:`leaf${i}${j}`,position:{x:i*600+j*260,y:370},data:{label:`${t.model.actions[i+1][j]} · Pagos (${payoffs[i][j].map(n=>n.toLocaleString('es-AR',{maximumFractionDigits:3})).join(' / ')})`}});edges.push({id:`e${i}${j}`,source:`b${i}`,target:`leaf${i}${j}`,label:t.model.actions[i+1][j],style:{stroke:active?'#087f70':'#a5b2bd',strokeWidth:active?3:1}});}}
 return {nodes,edges};
}
