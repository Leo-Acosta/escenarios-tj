import {object} from './contracts.ts';
import {laboratory,type LabRecord,type Cell} from './laboratory-contract.ts';
export function comparisonReplay(value:unknown,record:LabRecord,cell:Cell,trial:number):LabRecord{
 const o=object(value),source=object(o.comparison_source),options=object(o.options);
 if(o.engine!=='repeated-agents-v1'||source.id!==record.id||source.i!==cell.i||source.j!==cell.j||source.trial!==trial||options.seed!==record.seeds?.[trial]||options.rounds!==record.options.rounds||options.noise!==record.options.noise||JSON.stringify(options.policies)!==JSON.stringify(cell.policies))throw new Error('La reproducción no corresponde a la combinación solicitada.');
 const result=laboratory({...o,id:record.id},'agents');
 if(JSON.stringify(result.model)!==JSON.stringify(record.model)||result.rounds!.length!==record.options.rounds||result.rounds!.some((r,i)=>r.round!==i+1))throw new Error('La reproducción no conserva la matriz o las rondas originales.');
 return result;
}
