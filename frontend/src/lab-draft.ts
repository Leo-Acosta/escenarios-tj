export type Envelope<T>={format:1;scope:string;saved_at:string;value:T};
export const labKey=(scope:string)=>'escenarios-tj:labs:v1:'+encodeURIComponent(scope);
export function safeDraft(value:unknown,depth=0):void {
 if(depth>12)throw new Error('Borrador demasiado complejo.');
 if(typeof value==='string'){if(value.length>12000)throw new Error('Campo demasiado extenso.');return;}
 if(typeof value==='number'&&Number.isFinite(value)||typeof value==='boolean'||value===null)return;
 if(Array.isArray(value)){if(value.length>1000)throw new Error('Demasiados elementos.');value.forEach(v=>safeDraft(v,depth+1));return;}
 if(value&&typeof value==='object'){const entries=Object.entries(value);if(entries.length>200)throw new Error('Demasiados campos.');for(const [k,v]of entries){if(/reviewed|__proto__|constructor|prototype|ai_job_id/i.test(k))throw new Error('El borrador no puede conservar autorizaciones.');safeDraft(v,depth+1);}return;}
 throw new Error('Tipo de borrador incompatible.');
}
export function shape<T>(sample:T): (v:unknown)=>T {
 function check(v:unknown,s:unknown):void{if(Array.isArray(s)){if(!Array.isArray(v))throw new Error('Lista incompatible.');if(s.length)v.forEach(x=>check(x,s[0]));return;}if(s&&typeof s==='object'){if(!v||typeof v!=='object'||Array.isArray(v))throw new Error('Formulario incompatible.');const keys=Object.keys(s);if(Object.keys(v).some(k=>!keys.includes(k))||keys.some(k=>!(k in v)))throw new Error('Campos incompatibles.');for(const k of keys)check((v as Record<string,unknown>)[k],(s as Record<string,unknown>)[k]);return;}if(typeof v!==typeof s)throw new Error('Campo incompatible.');}
 return v=>{safeDraft(v);check(v,sample);return v as T;};
}
export function decodeDraft<T>(raw:string,scope:string,parse:(v:unknown)=>T):Envelope<T>{
 if(raw.length>1000000)throw new Error('Copia local demasiado grande.');const e=JSON.parse(raw);
 if(!e||e.format!==1||e.scope!==scope||typeof e.saved_at!=='string'||!Number.isFinite(Date.parse(e.saved_at)))throw new Error('Copia de otro contexto o formato.');
 return {format:1,scope,saved_at:e.saved_at,value:parse(e.value)};
}
