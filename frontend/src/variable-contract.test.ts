import test from 'node:test';
import assert from 'node:assert/strict';
import {blank,draftValue,dictionary,variable} from './variable-contract.ts';
const model={title:'Sintético',actors:['A','B'],strategies:[['a','b'],['c','d']],a:[[1,2],[3,4]],b:[[4,3],[2,1]],p:.5,q:.6};
const item={name:'Proporción B',type:'number',value:.6,unit:'proporción',source:'Sintético',uncertainty:'Exploratoria',interval:[.4,.8],target:'q',evidence:'synthetic'};
test('conserva vínculo y rechaza porcentajes, valor incompatible e intervalo incompleto',()=>{
 assert.equal(variable(item,model).value,.6);
 for(const update of [{unit:'%'},{value:.7},{interval:[.8,.4]},{interval:[0,Infinity]},{target:'a.2.0'}])assert.throws(()=>variable({...item,...update},model));
 assert.throws(()=>draftValue({...blank(),name:'Valor vacío',source:'Supuesto',unit:'puntos',uncertainty:'Pendiente'},model));
 assert.throws(()=>draftValue({...blank(),name:'Intervalo',source:'Supuesto',unit:'puntos',uncertainty:'Pendiente',value:'0',lower:'',upper:'1'},model));
});
test('booleanos falsos y categorías conservan su tipo',()=>{
 assert.equal(variable({...item,type:'boolean',value:false,unit:'indicador',target:'context',interval:null},model).value,false);
 assert.equal(variable({...item,type:'category',value:'No disponible',unit:'categoría',target:'context',interval:null,evidence:'pending'},model).evidence,'pending');
});
test('rechaza diccionarios de otra matriz y vínculos repetidos',()=>{
 const r={id:'test',created_at:'2026-10-07T12:00:00Z',sha256:'a'.repeat(64),payload:{engine:'variables-v1',workflow:{id:'wf',version:1},matrix:{model,pure:[],mixed:null,values_a:[1,2],values_b:[1,2],best_a:[1],limitations:[],context:{workflow_id:'wf',version:1,assumptions:'Sintético',description:'Prueba'}},variables:[item],limits:['Declarado']}};
 assert.equal(dictionary(r).payload.variables.length,1);
 assert.throws(()=>dictionary({...r,payload:{...r.payload,workflow:{id:'otro',version:1}}}));
 assert.throws(()=>dictionary({...r,payload:{...r.payload,variables:[item,{...item,name:'Otra'}]}}));
});
