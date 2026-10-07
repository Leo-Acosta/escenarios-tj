import {copies,preserve,variantKey,removeExact,type Copy} from './draft-journal.ts';
import {object,workflow,type DraftModel,type Evidence} from './contracts.ts';
export type LocalDraft={format:1;identity:string;revision:number|null;saved_at:string;model:DraftModel;assumptions:string;evidence:Evidence[];title:string;description:string;answer:string};
export const draftKey=(identity:string)=>'escenarios-tj:editor:v1:'+encodeURIComponent(identity||'new');
export function parseDraft(raw:string,identity:string):LocalDraft{
 if(raw.length>1000000)throw new Error('Borrador local demasiado grande.');
 const o=object(JSON.parse(raw));
 if(o.format!==1||o.identity!==identity||!(o.revision===null||typeof o.revision==='number'&&Number.isSafeInteger(o.revision)&&o.revision>0)||typeof o.saved_at!=='string'||!Number.isFinite(Date.parse(o.saved_at)))throw new Error('Borrador local de otra versión o expediente.');
 const text=(key:string,max:number)=>{const v=o[key];if(typeof v!=='string'||v.length>max)throw new Error('Campo local incompatible: '+key);return v;};
 const parsed=workflow({id:identity,title:text('title',100),description:text('description',12000),revision:o.revision||1,assumptions:text('assumptions',6000),model:o.model,evidence:o.evidence,answers:{},question:null,versions:[]});
 if(!parsed.model||parsed.evidence.length>20)throw new Error('Modelo local incompatible.');
 return {format:1,identity,revision:o.revision as number|null,saved_at:o.saved_at,model:parsed.model,evidence:parsed.evidence,assumptions:parsed.assumptions,title:parsed.title,description:parsed.description,answer:text('answer',4000)};
}
export function draftCopies(storage:Pick<Storage,'getItem'> & Partial<Pick<Storage,'length'|'key'>>,identity:string){const valid:Array<Copy & {draft:LocalDraft}>=[];let rejected=0;for(const c of copies(storage,draftKey(identity))){try{valid.push({...c,draft:parseDraft(c.raw,identity)});}catch{rejected++;}}return Object.assign(valid.sort((a,b)=>b.draft.saved_at.localeCompare(a.draft.saved_at)),{rejected});}
export function readDraft(storage:Pick<Storage,'getItem'> & Partial<Pick<Storage,'length'|'key'>>,identity:string):LocalDraft|null{return draftCopies(storage,identity)[0]?.draft||null;}
export function writeDraft(storage:Pick<Storage,'setItem'>,draft:LocalDraft){const raw=JSON.stringify(draft);parseDraft(raw,draft.identity);preserve(storage,draftKey(draft.identity),raw);storage.setItem(draftKey(draft.identity),raw);}
export function clearDraft(storage:Pick<Storage,'removeItem'> & Partial<Pick<Storage,'getItem'>>,identity:string,selected?:Copy,clearOwn=true){if(clearOwn)storage.removeItem(variantKey(draftKey(identity)));if(selected&&storage.getItem){removeExact(storage as Pick<Storage,'getItem'|'removeItem'>,selected);if(storage.getItem(draftKey(identity))===selected.raw)storage.removeItem(draftKey(identity));}else storage.removeItem(draftKey(identity));}
