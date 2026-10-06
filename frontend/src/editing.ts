import type {DraftModel} from './contracts';
export function emptyModel(title:string):DraftModel{return {title,actors:['',''],strategies:[['',''],['','']],a:[[null,null],[null,null]],b:[[null,null],[null,null]],p:.5,q:.5};}
export function validateCalculation(model:DraftModel,assumptions:string,reviewed:boolean):string|null{
 if(!model.title.trim()||model.actors.some(x=>!x.trim())||model.strategies.some(row=>row.some(x=>!x.trim())))return 'Completá el título, los actores y las estrategias.';
 if(model.actors[0].trim()===model.actors[1].trim()||model.strategies.some(row=>row[0].trim()===row[1].trim()))return 'Los actores y las estrategias de cada actor deben ser distintos.';
 if([...model.a.flat(),...model.b.flat()].some(x=>x===null||!Number.isFinite(x)||Math.abs(x)>1000000))return 'Completá los ocho pagos con números entre −1.000.000 y 1.000.000.';
 if([model.p,model.q].some(x=>x===null||!Number.isFinite(x)||x<0||x>1))return 'Las probabilidades deben estar entre 0 y 1.';
 if(!assumptions.trim())return 'Registrá los supuestos antes de calcular.';
 if(!reviewed)return 'Confirmá la revisión de pagos, probabilidades y supuestos.';
 return null;
}
