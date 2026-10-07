import {object,result,type Result} from './contracts.ts';

export const evidenceLabels={synthetic:'Sintético',assumed:'Supuesto',documented_declared:'Documentación declarada',pending:'Pendiente'};
export const typeLabels={number:'Número',category:'Categoría',boolean:'Booleano'};
export const targets=['context','p','q','a.0.0','a.0.1','a.1.0','a.1.1','b.0.0','b.0.1','b.1.0','b.1.1'];
export type Variable={name:string;type:keyof typeof typeLabels;value:number|string|boolean;unit:string;source:string;uncertainty:string;interval:[number,number]|null;target:string;evidence:keyof typeof evidenceLabels};
export type DraftVariable=Omit<Variable,'value'|'interval'> & {value:string;lower:string;upper:string};
export type Dictionary={id:string;created_at:string;sha256:string;payload:{engine:string;workflow:{id:string;version:number};matrix:Result;variables:Variable[];limits:string[]}};
export type VariableSummary={id:string;created_at:string;sha256:string;version:number;count:number};
const bad=():never=>{throw new Error('Diccionario de variables incompatible.');};
const text=(v:unknown):string=>typeof v==='string'&&v.trim().length>0?v:bad();
const number=(v:unknown):number=>typeof v==='number'&&Number.isFinite(v)?v:bad();
const positive=(v:unknown):number=>{const n=number(v);return Number.isSafeInteger(n)&&n>0?n:bad();};
const sha=(v:unknown):string=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v)?v:bad();
const date=(v:unknown):string=>{const s=text(v);return /(?:Z|[+-]\d\d:\d\d)$/.test(s)&&Number.isFinite(Date.parse(s))?s:bad();};
export function expected(model:Result['model'],target:string):number {return target==='p'||target==='q'?model[target]:model[target[0] as 'a'|'b'][Number(target[2])][Number(target[4])];}
export function variable(v:unknown,model:Result['model']):Variable {
 const o=object(v),kind=text(o.type) as Variable['type'],target=text(o.target),evidence=text(o.evidence) as Variable['evidence'];
 if(!Object.hasOwn(typeLabels,kind)||!targets.includes(target)||!Object.hasOwn(evidenceLabels,evidence))bad();
 const value=kind==='number'?number(o.value):kind==='category'?text(o.value):typeof o.value==='boolean'?o.value:bad();
 let interval:Variable['interval']=null;
 if(o.interval!==null){if(kind!=='number'||!Array.isArray(o.interval)||o.interval.length!==2)bad();const b=o.interval as unknown[];interval=[number(b[0]),number(b[1])];if(interval[0]>Number(value)||Number(value)>interval[1])bad();}
 const unit=text(o.unit);
 if(target!=='context'&&(kind!=='number'||value!==expected(model,target)))bad();
 if(['p','q'].includes(target)&&(!['proporción','1'].includes(unit)||interval&&(interval[0]<0||interval[1]>1)))bad();
 return {name:text(o.name),type:kind,value,unit,source:text(o.source),uncertainty:text(o.uncertainty),interval,target,evidence};
}
export function dictionary(v:unknown):Dictionary {
 const o=object(v),p=object(o.payload),w=object(p.workflow),matrix=result(p.matrix),ctx=object(object(p.matrix).context);
 if(p.engine!=='variables-v1'||ctx.workflow_id!==w.id||ctx.version!==w.version||!Array.isArray(p.variables)||!p.variables.length||p.variables.length>100||!Array.isArray(p.limits))bad();
 const items=(p.variables as unknown[]).map(x=>variable(x,matrix.model));
 if(new Set(items.map(x=>x.name.toLocaleLowerCase('es'))).size!==items.length)bad();
 const links=items.filter(x=>x.target!=='context').map(x=>x.target);if(new Set(links).size!==links.length)bad();
 return {id:text(o.id),created_at:date(o.created_at),sha256:sha(o.sha256),payload:{engine:String(p.engine),workflow:{id:text(w.id),version:positive(w.version)},matrix,variables:items,limits:(p.limits as unknown[]).map(text)}};
}
export function history(v:unknown):VariableSummary[]{if(!Array.isArray(v))bad();return (v as unknown[]).map(x=>{const s=object(x);return {id:text(s.id),created_at:date(s.created_at),sha256:sha(s.sha256),version:positive(s.version),count:positive(s.count)};});}
export function blank():DraftVariable{return {name:'',type:'number',value:'',unit:'',source:'',uncertainty:'',lower:'',upper:'',target:'context',evidence:'assumed'};}
export function draftValue(d:DraftVariable,model:Result['model']):Variable {
 if(['p','q'].includes(d.target)&&!['proporción','1'].includes(d.unit.trim()))throw new Error('Para p/q usá proporción (0–1), no porcentajes.');
 if((d.lower.trim()&&!d.upper.trim())||(!d.lower.trim()&&d.upper.trim()))throw new Error('Completá ambos límites del intervalo o dejá ambos vacíos.');
 const numeric=(s:string)=>s.trim()?number(Number(s)):bad();
 const value=d.type==='number'?numeric(d.value):d.type==='boolean'?d.value==='true'?true:d.value==='false'?false:bad():d.value;
 const interval=d.lower.trim()||d.upper.trim()?[numeric(d.lower),numeric(d.upper)]:null;
 return variable({...d,value,interval},model);
}
