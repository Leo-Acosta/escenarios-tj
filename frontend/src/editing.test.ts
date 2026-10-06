import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {emptyModel,validateCalculation} from './editing.ts';
const model={title:'Negociación',actors:['Municipio','Vecinos'],strategies:[['Acuerdo','Competir'],['Acuerdo','Competir']],a:[[3,0],[5,1]],b:[[3,5],[0,1]],p:.5,q:.5};
test('Un modelo vacío no se presenta como calculable',()=>{const m=emptyModel('Caso');assert.equal(m.a[0][0],null);assert.ok(validateCalculation(m,'Hipotéticos',true));});
test('Exige pagos completos y revisión explícita',()=>{assert.equal(validateCalculation(model,'Hipotéticos',true),null);assert.ok(validateCalculation(model,'Hipotéticos',false));assert.ok(validateCalculation({...model,a:[[null,0],[5,1]]},'Hipotéticos',true));assert.ok(validateCalculation({...model,q:2},'Hipotéticos',true));assert.ok(validateCalculation({...model,actors:['A',' A ']},'Hipotéticos',true));assert.ok(validateCalculation(model,' ',true));});
