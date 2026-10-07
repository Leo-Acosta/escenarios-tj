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
export function readDraft(storage:Pick<Storage,'getItem'>,identity:string):LocalDraft|null{const raw=storage.getItem(draftKey(identity));return raw?parseDraft(raw,identity):null;}
export function writeDraft(storage:Pick<Storage,'setItem'>,draft:LocalDraft){const raw=JSON.stringify(draft);parseDraft(raw,draft.identity);storage.setItem(draftKey(draft.identity),raw);}
export function clearDraft(storage:Pick<Storage,'removeItem'>,identity:string){storage.removeItem(draftKey(identity));}
