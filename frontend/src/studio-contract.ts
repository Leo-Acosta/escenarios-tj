import {object,type Result} from './contracts.ts';
export type Evidence='documented_declared'|'declared'|'assumed'|'pending';
export const evidenceLabels:Record<Evidence,string>={documented_declared:'Documentación declarada',declared:'Declarado',assumed:'Hipótesis',pending:'Pendiente'};
export type Contact={organization:string;role:string;description:string;email:string;phone:string;url:string;source:string;notes:string};
export type VisualNode={id:number;uid:string;name:string;type:number;position:{x:number;y:number};group:string;profile:Contact};
export type VisualEdge={id:number;uid:string;a:number;b:number;type:string;directed:boolean;label:string;status:Evidence;start:string;end:string;weight:null|{value:number;unit:string;meaning:string;scale:string};evidence?:{source:string;reference:string;note:string}};
export type VisualGraph={schema:2;nodes:VisualNode[];edges:VisualEdge[];settings:{layout:'manual'|'grid'|'circle'|'groups';labels:boolean;viewport?:{x:number;y:number;zoom:number}}};
export type NetworkRecord={id:string;title:string;created_at:string;assumptions:string;graph:VisualGraph|LegacyGraph;parent_id?:string;sha256?:string;workflow?:{id:string;title:string;revision:number}};
type LegacyGraph={schema?:undefined;nodes:{id:number;name:string;type:number}[];edges:{id:number;a:number;b:number;type:string;evidence?:{source:string;reference:string;note:string}}[]};
export type Tree={id:string;model:{title:string;actors:string[];actions:string[][];payoffs:number[][][];assumptions:string};equilibria:{first:number;responses:number[];outcome:number[];payoffs:number[]}[];simulation?:{decision_counts:number[];options:{iterations:number;seed:number;radius:number}}};
export type Binding={node_uid:string;kind:'matrix'|'tree';actor:number;strategies:number[]};
export type ScenarioVariable={name:string;value:string;unit:string;source:string;status:Evidence;target:string;transformation:string;model_value?:number|null};
export type Scenario={id:string;created_at:string;sha256:string;warnings?:string[];payload:{engine:string;title:string;workflow:{id:string;version:number};lineage:string;revision:number;parent_id?:string;clone_of?:string;network:NetworkRecord;matrix:Result;tree:Tree|null;dictionary?:unknown;variables:ScenarioVariable[];constraints:string[];links:Binding[];assumptions:string;evidence_mode:'synthetic'|'declared'|'pending';payoff_units:string[];comparable:boolean;limits:string[]}};
export type Catalog={workflow_id:string;matrices:{version:number;title:string}[];networks:NetworkRecord[];trees:Tree[];scenarios:Scenario[];limits:string[]};
export type Comparison={left:string;right:string;comparable:boolean;differences:{field:string;left:unknown;right:unknown}[];expected_a_delta:number[]|null;expected_b_delta:number[]|null;left_pure:number[][];right_pure:number[][];left_tree:unknown;right_tree:unknown;limits:string[]};
const bad=():never=>{throw new Error('Estudio visual incompatible o incompleto.');};
const str=(v:unknown):string=>typeof v==='string'?v:bad();
const finite=(v:unknown)=>typeof v==='number'&&Number.isFinite(v)?v:bad();
const arr=(v:unknown):unknown[]=>Array.isArray(v)?v:bad();
export function parseGraph(v:unknown):VisualGraph{
 const g=object(v);if(g.schema!==2)bad();const ns=arr(g.nodes),es=arr(g.edges);if(!ns.length||ns.length>200||es.length>1000)bad();
 const keys=new Set<string>();for(const [i,x] of ns.entries()){const n=object(x),p=object(n.position),profile=object(n.profile);if(n.id!==i||![0,1,2].includes(finite(n.type)))bad();const id=str(n.uid);if(!id||keys.has(id))bad();keys.add(id);str(n.name);str(n.group);finite(p.x);finite(p.y);for(const k of Object.keys(emptyContact()))str(profile[k]);}
 for(const [i,x] of es.entries()){const e=object(x);if(e.id!==i||typeof e.directed!=='boolean'||!(str(e.status) in evidenceLabels)||!['Influencia','Cooperación','Participación'].includes(str(e.type)))bad();for(const k of ['a','b']){const n=finite(e[k]);if(!Number.isInteger(n)||n<0||n>=ns.length)bad();}if(e.a===e.b)bad();for(const k of ['uid','label','start','end'])str(e[k]);if(e.weight){const w=object(e.weight);finite(w.value);for(const k of ['unit','meaning','scale'])str(w[k]);}if(e.evidence){const ev=object(e.evidence);for(const k of ['source','reference','note'])str(ev[k]);}}
 const s=object(g.settings);if(!['manual','grid','circle','groups'].includes(str(s.layout))||typeof s.labels!=='boolean')bad();if(s.viewport){const camera=object(s.viewport);finite(camera.x);finite(camera.y);const z=finite(camera.zoom);if(z<.08||z>2)bad();}return v as VisualGraph;
}
export const emptyContact=():Contact=>({organization:'',role:'',description:'',email:'',phone:'',url:'',source:'',notes:''});
export const clone=<T,>(v:T):T=>JSON.parse(JSON.stringify(v)) as T;
export function upgrade(r:NetworkRecord):VisualGraph{
 if(r.graph.schema===2)return clone(parseGraph(r.graph));
 return {schema:2,settings:{layout:'grid',labels:true},nodes:r.graph.nodes.map((n,i)=>({...n,uid:`${r.id}-${n.id}`,position:{x:(i%4)*240,y:Math.floor(i/4)*145},group:'',profile:emptyContact()})),edges:r.graph.edges.map(e=>({...e,uid:crypto.randomUUID(),directed:false,label:'',status:'assumed',start:'',end:'',weight:null}))};
}
export function parseScenario(v:unknown):Scenario{const r=object(v),p=object(r.payload);str(r.id);if(!/^[a-f0-9]{64}$/.test(str(r.sha256)))bad();if(p.engine!=='visual-study-v1')bad();str(p.title);const n=object(p.network);if(object(n.graph).schema===2)parseGraph(n.graph);arr(p.links);arr(p.variables);arr(p.constraints);object(p.matrix);return v as Scenario;}
export function parseCatalog(v:unknown):Catalog{const c=object(v);str(c.workflow_id);for(const n of arr(c.networks)){const r=object(n);str(r.id);str(r.title);if(object(r.graph).schema===2)parseGraph(r.graph);}arr(c.matrices);arr(c.trees);arr(c.scenarios).forEach(parseScenario);arr(c.limits);return v as Catalog;}
export function parseComparison(v:unknown):Comparison{const c=object(v);str(c.left);str(c.right);if(typeof c.comparable!=='boolean')bad();arr(c.differences);arr(c.limits);return v as Comparison;}
export function removeNode(g:VisualGraph,key:string):VisualGraph{const node=g.nodes.find(n=>n.uid===key);if(!node)return g;const ids=new Map<number,number>();const nodes=g.nodes.filter(n=>n.uid!==key).map((n,i)=>{ids.set(n.id,i);return {...n,id:i};});return {...g,nodes,edges:g.edges.filter(e=>e.a!==node.id&&e.b!==node.id).map((e,i)=>({...e,id:i,a:ids.get(e.a)!,b:ids.get(e.b)!}))};}
export function layout(g:VisualGraph,kind:'grid'|'circle'|'groups'):VisualGraph{const groups=[...new Set(g.nodes.map(n=>n.group))];const count=new Map<string,number>();return {...g,settings:{...g.settings,layout:kind},nodes:g.nodes.map((n,i)=>{let position={x:(i%4)*260,y:Math.floor(i/4)*150};if(kind==='circle')position={x:Math.cos(i/g.nodes.length*Math.PI*2)*Math.max(240,g.nodes.length*23)+400,y:Math.sin(i/g.nodes.length*Math.PI*2)*Math.max(240,g.nodes.length*23)+350};if(kind==='groups'){const j=count.get(n.group)||0;count.set(n.group,j+1);position={x:groups.indexOf(n.group)*320,y:j*145};}return {...n,position};})};}
export type Journal<T>={past:T[];present:T;future:T[]};
export function commit<T>(j:Journal<T>,next:T):Journal<T>{return {past:[...j.past,j.present].slice(-80),present:next,future:[]};}
export function undo<T>(j:Journal<T>):Journal<T>{if(!j.past.length)return j;return {past:j.past.slice(0,-1),present:j.past[j.past.length-1],future:[j.present,...j.future]};}
export function redo<T>(j:Journal<T>):Journal<T>{if(!j.future.length)return j;return {past:[...j.past,j.present],present:j.future[0],future:j.future.slice(1)};}

// Persist completed pointer/keyboard moves, never selection or intermediate drag frames.
export function finishedNodeMoves(graph:VisualGraph,changes:readonly {type:string;id?:string;position?:{x:number;y:number};dragging?:boolean}[]):{id:string;position:{x:number;y:number}}[]{
 const last=new Map<string,{x:number;y:number}>();
 for(const change of changes){if(change.type!=='position'||!change.id||!change.position||change.dragging===true)continue;const {x,y}=change.position;if(!Number.isFinite(x)||!Number.isFinite(y)||Math.abs(x)>100000||Math.abs(y)>100000)continue;last.set(change.id,{x,y});}
 return [...last].flatMap(([id,position])=>{const node=graph.nodes.find(n=>n.uid===id);return node&&(node.position.x!==position.x||node.position.y!==position.y)?[{id,position}]:[];});
}
