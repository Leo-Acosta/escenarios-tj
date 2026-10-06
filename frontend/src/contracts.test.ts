import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {result,workflows,workflow,library} from './contracts.ts';
const valid={model:{title:'Caso',actors:['A','B'],strategies:[['Sí','No'],['Sí','No']],a:[[3,0],[5,1]],b:[[3,5],[0,1]],p:.5,q:.5},pure:[[1,1]],mixed:null,values_a:[1.5,3],values_b:[1.5,3],best_a:[1],limitations:['Hipotético']};
test('Conserva los pagos y resultados recibidos, sin recalcular',()=>assert.deepEqual(result(valid),{...valid,context:undefined}));
test('Rechaza dimensiones, probabilidades y resultados inválidos',()=>{for(const value of [{...valid,model:{...valid.model,a:[[1,2,3],[4,5,6]]}},{...valid,model:{...valid.model,p:1.1}},{...valid,values_a:[Infinity,1]},{...valid,pure:[[2,0]]}])assert.throws(()=>result(value));});
test('Rechaza contratos incompatibles y permite estados vacíos',()=>{assert.deepEqual(workflows([]),[]);assert.throws(()=>workflows({items:[]}));assert.throws(()=>workflow({id:'x',title:'x',description:'x',versions:[{version:'1',created_at:'x'}]}));assert.deepEqual(library({total:0,items:[]}),{total:0,items:[]});});
