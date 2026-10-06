import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {parseComparison} from './comparison-contract.ts';
const value={model_before:{actors:['A','B'],strategies:[['Acuerdo','Competir'],['Acuerdo','Competir']]},effects:[{actor:0,strategy:0,before:1.5,after:0,delta:-1.5,payment_effect:0,probability_effect:-1.5}],cells:[],probabilities:[{key:'q',before:.5,after:0,delta:-.5}],pure_before:[[1,1]],pure_after:[[1,1]],assumptions_before:'Base',assumptions_after:'Contraste',limits:['No causal']};
test('Conserva diferencias y atribuciones calculadas por Python',()=>assert.deepEqual(parseComparison(value),value));
test('Rechaza índices y dimensiones incompatibles',()=>{assert.throws(()=>parseComparison({...value,effects:[{...value.effects[0],actor:2}]}));assert.throws(()=>parseComparison({...value,pure_before:[[0,2]]}));assert.throws(()=>parseComparison({...value,model_before:{actors:['A'],strategies:[['X','Y'],['X','Y']]}}));});
