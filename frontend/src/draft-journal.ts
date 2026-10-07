// Each browser document owns a separate slot. Concurrent tabs never replace that slot.
export const draftWriter=crypto.randomUUID();
export type Store=Pick<Storage,'getItem'|'setItem'|'removeItem'|'key'|'length'>;
export type Copy={key:string;raw:string};
export const variantKey=(base:string,writer=draftWriter)=>base+':tab:'+writer;
export function copies(storage:Pick<Store,'getItem'> & Partial<Pick<Store,'length'|'key'>>,base:string):Copy[]{
 const result:Copy[]=[];const old=storage.getItem(base);if(old!==null)result.push({key:base,raw:old});
 if(storage.key)for(let i=0;i<(storage.length||0);i++){const key=storage.key(i);if(key?.startsWith(base+':tab:')){const raw=storage.getItem(key);if(raw!==null)result.push({key,raw});}}
 return result;
}
export function preserve(storage:Pick<Store,'setItem'>,base:string,raw:string,writer=draftWriter){if(raw.length>1000000)throw new Error('Copia local demasiado grande.');storage.setItem(variantKey(base,writer),raw);}
export function removeExact(storage:Pick<Store,'getItem'|'removeItem'>,copy:Copy):boolean{if(storage.getItem(copy.key)!==copy.raw)return false;storage.removeItem(copy.key);return true;}
