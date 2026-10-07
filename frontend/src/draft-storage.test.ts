import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {emptyModel} from './editing.ts';
import {writeDraft,readDraft,parseDraft,clearDraft,draftCopies,draftKey,type LocalDraft} from './draft-storage.ts';
const draft:LocalDraft={format:1,identity:'synthetic',revision:4,saved_at:'2026-10-07T00:00:00Z',model:emptyModel('Parcial'),assumptions:'Pendiente',evidence:[],title:'',description:'',answer:'Respuesta sin enviar'};
test('recupera pagos incompletos y respuesta sin inferir ni confirmar revisión',()=>{const data=new Map<string,string>();const storage={getItem:(k:string)=>data.get(k)||null,setItem:(k:string,v:string)=>{data.set(k,v);},removeItem:(k:string)=>{data.delete(k);}};writeDraft(storage,draft);assert.deepEqual(readDraft(storage,'synthetic'),draft);assert.equal(readDraft(storage,'other'),null);clearDraft(storage,'synthetic');assert.equal(readDraft(storage,'synthetic'),null);});
test('rechaza corrupción, expediente cruzado, formato futuro y dimensiones inválidas',()=>{for(const raw of ['broken',JSON.stringify({...draft,identity:'other'}),JSON.stringify({...draft,format:2}),JSON.stringify({...draft,model:{...draft.model,a:[[null]]}})])assert.throws(()=>parseDraft(raw,'synthetic'));});
test('expone cuota agotada para no atribuir persistencia a un intento fallido',()=>{assert.throws(()=>writeDraft({setItem:()=>{throw new Error('QuotaExceeded');}},draft),/QuotaExceeded/);});

test('una copia corrupta no bloquea otras válidas y no se borra silenciosamente',()=>{const data=new Map([[draftKey('synthetic'), 'broken'],[draftKey('synthetic')+':tab:other',JSON.stringify(draft)]]);const storage={getItem:(k:string)=>data.get(k)||null,length:data.size,key:(i:number)=>[...data.keys()][i]||null};const found=draftCopies(storage,'synthetic');assert.equal(found.length,1);assert.equal(found.rejected,1);assert.deepEqual(found[0].draft,draft);assert.equal(data.get(draftKey('synthetic')),'broken');});
