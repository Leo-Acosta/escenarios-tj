import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {graphResult} from './graph-contract.ts';
const sample={model:{title:'Sintético',actors:['A','B'],strategies:[['Sí','No'],['Sí','No']],a:[[3,0],[5,1]],b:[[3,5],[0,1]],p:.5,q:.5},pure:[[1,1]],mixed:null,values_a:[1.5,3],values_b:[1.5,3],best_a:[1],limitations:['Sintético'],sensitivity:{threshold:null,always_tied:false,points:Array.from({length:101},(_,k)=>({q:k/100,values:[3*k/100,1+4*k/100],best:[1]}))}};
test('conserva las 101 muestras Python y los empates sin nueva inferencia',()=>{assert.deepEqual(graphResult(sample).sensitivity,sample.sensitivity);const tie=structuredClone(sample);tie.sensitivity.points[20].best=[0,1];assert.deepEqual(graphResult(tie).sensitivity.points[20].best,[0,1]);});
test('rechaza muestras incompletas, desordenadas, no finitas y elecciones inválidas',()=>{for(const mutate of [(s:typeof sample)=>s.sensitivity.points.pop(),(s:typeof sample)=>{s.sensitivity.points[3].q=.9;},(s:typeof sample)=>{s.sensitivity.points[3].values[0]=Infinity;},(s:typeof sample)=>{s.sensitivity.points[3].best=[2];}]){const s=structuredClone(sample);mutate(s);assert.throws(()=>graphResult(s));}});
