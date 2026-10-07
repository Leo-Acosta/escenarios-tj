import {object,result,type Result} from './contracts.ts';
export type GraphResult=Result&{sensitivity:{threshold:number|null;always_tied:boolean;points:{q:number;values:number[];best:number[]}[]}};
export function graphResult(v:unknown):GraphResult{
 const base=result(v),s=object(object(v).sensitivity);
 const fail=():never=>{throw new Error('Sensibilidad incompatible con la matriz conservada.');};
 if(typeof s.always_tied!=='boolean'||!(s.threshold===null||typeof s.threshold==='number'&&Number.isFinite(s.threshold)&&s.threshold>=0&&s.threshold<=1)||!Array.isArray(s.points)||s.points.length!==101)fail();
 const points=(s.points as unknown[]).map((v,k)=>{const p=object(v);if(p.q!==k/100||!Array.isArray(p.values)||p.values.length!==2||!p.values.every(x=>typeof x==='number'&&Number.isFinite(x))||!Array.isArray(p.best)||!p.best.length||!p.best.every(x=>x===0||x===1)||new Set(p.best).size!==p.best.length)fail();return {q:p.q as number,values:p.values as number[],best:p.best as number[]};});
 return {...base,sensitivity:{threshold:s.threshold as number|null,always_tied:s.always_tied as boolean,points}};
}
