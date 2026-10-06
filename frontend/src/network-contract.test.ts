import {test} from 'node:test';
import assert from 'node:assert/strict';
import {network,networkVersion,networkVersions} from './network-contract.ts';
const graph={nodes:[{id:0,name:'Municipio',type:0},{id:1,name:'Vecinos',type:1}],edges:[{id:0,a:0,b:1,type:'Cooperación'}]};
test('conserva nombres y relaciones sin atribuir expediente ni dirección',()=>{assert.deepEqual(network({graph}),graph);assert.equal(network({graph:null}),null);});
test('rechaza referencias rotas, tipos inválidos e identificadores repetidos',()=>{assert.throws(()=>network({graph:{...graph,edges:[{id:0,a:0,b:2,type:'Influencia'}]}}));assert.throws(()=>network({graph:{...graph,nodes:[graph.nodes[0],{...graph.nodes[1],id:0}]}}));assert.throws(()=>network({graph:{...graph,edges:[{id:0,a:0,b:1,type:'Predicción'}]}}));assert.throws(()=>network({graph:{nodes:[],edges:[]}}));});

test('conserva revisión histórica e historial independiente',()=>{const record={id:'v1',created_at:'2026-10-06',title:'Mapa',assumptions:'Hipótesis',graph,workflow:{id:'case',title:'Título histórico',revision:3}};assert.deepEqual(networkVersion(record),record);assert.deepEqual(networkVersions([]),[]);assert.throws(()=>networkVersion({...record,workflow:{...record.workflow,revision:0}}));assert.throws(()=>networkVersion({...record,graph:null}));});
