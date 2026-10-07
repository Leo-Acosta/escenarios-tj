import {object,result,type Result} from './contracts.ts';
export const sections={matrix:'Matriz estratégica',tree:'Árbol decisorio',simulation:'Monte Carlo',agents:'Agentes con memoria',comparison:'Comparación de políticas',sweep:'Sensibilidad de incentivos',decision:'Decisiones de IA local',benchmark:'Batería de agentes IA',evaluation:'Evaluación predictiva'};
export type Kind=keyof typeof sections;
export type Mode='synthetic'|'declared';
export type Source={kind:Exclude<Kind,'matrix'|'simulation'>;id:string;title:string;created_at:string;label:string;simulation:boolean;evidence:string};
export type Catalog={workflow_id:string;version:number;matrix:Result;items:Source[];total:number;limits:string[]};
export type SavedReport={id:string;created_at:string;sha256:string;payload:{engine:string;workflow:{id:string;version:number};title:string;executive_note:string;pending:string;evidence_mode:Mode;sections:Kind[];matrix:Result;matrix_sha256:string;sources:{kind:Source['kind'];id:string;sha256:string;record:Record<string,unknown>}[];limits:string[]}};
export type ReportSummary={id:string;created_at:string;sha256:string;title:string;version:number;evidence_mode:Mode};
const bad=():never=>{throw new Error('Informe recibido incompatible con el contrato.');};
const str=(v:unknown):string=>typeof v==='string'&&v.length>0?v:bad();
const opt=(v:unknown):string=>typeof v==='string'?v:bad();
const integer=(v:unknown):number=>typeof v==='number'&&Number.isSafeInteger(v)&&v>=0?v:bad();
const sha=(v:unknown):string=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v)?v:bad();
const date=(v:unknown):string=>{const s=str(v);return /(?:Z|[+-]\d\d:\d\d)$/.test(s)&&Number.isFinite(Date.parse(s))?s:bad();};
const mode=(v:unknown):Mode=>v==='synthetic'||v==='declared'?v:bad();
const kind=(v:unknown):Kind=>typeof v==='string'&&Object.hasOwn(sections,v)?v as Kind:bad();
const sourceKind=(v:unknown):Source['kind']=>{const k=kind(v);return k==='matrix'||k==='simulation'?bad():k;};
const list=<T,>(v:unknown,parse:(x:unknown)=>T):T[]=>Array.isArray(v)?v.map(parse):bad();
export function catalog(v:unknown):Catalog{const o=object(v);return {workflow_id:str(o.workflow_id),version:integer(o.version),matrix:result(o.matrix),total:integer(o.total),limits:list(o.limits,str),items:list(o.items,x=>{const s=object(x);if(typeof s.simulation!=='boolean')bad();return {kind:sourceKind(s.kind),id:str(s.id),title:str(s.title),created_at:date(s.created_at),label:str(s.label),simulation:s.simulation as boolean,evidence:str(s.evidence)};})};}
export function report(v:unknown):SavedReport{const o=object(v),p=object(o.payload),w=object(p.workflow),selected=list(p.sections,kind);if(p.engine!=='unified-executive-v1'||!selected.length||new Set(selected).size!==selected.length||selected.includes('simulation')&&!selected.includes('tree'))bad();const sources=list(p.sources,x=>{const s=object(x),k=sourceKind(s.kind);if(!selected.includes(k))bad();return {kind:k,id:str(s.id),sha256:sha(s.sha256),record:object(s.record)};});if(new Set(sources.map(s=>s.kind+':'+s.id)).size!==sources.length)bad();return {id:str(o.id),created_at:date(o.created_at),sha256:sha(o.sha256),payload:{engine:str(p.engine),workflow:{id:str(w.id),version:integer(w.version)},title:str(p.title),executive_note:opt(p.executive_note),pending:opt(p.pending),evidence_mode:mode(p.evidence_mode),sections:selected,matrix:result(p.matrix),matrix_sha256:sha(p.matrix_sha256),sources,limits:list(p.limits,str)}};}
export function history(v:unknown):ReportSummary[]{return list(v,x=>{const s=object(x);return {id:str(s.id),created_at:date(s.created_at),sha256:sha(s.sha256),title:str(s.title),version:integer(s.version),evidence_mode:mode(s.evidence_mode)};});}
