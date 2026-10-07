import React from 'react';
const number=(n:number)=>n.toLocaleString('es-AR',{maximumFractionDigits:3});
export default function Plot({series,index,title}:{series:{name:string;color:string;values:number[]}[];index:number;title:string}){
 const all=series.flatMap(s=>s.values),lo=Math.min(...all),hi=Math.max(...all),span=hi-lo||1;
 const x=(i:number)=>45+i*700/Math.max(1,series[0].values.length-1),y=(v:number)=>235-(v-lo)*190/span;
 return <div className="lab-plot"><h3>{title}</h3><svg viewBox="0 0 800 280" role="img" aria-label={title}><line x1="45" y1="235" x2="745" y2="235" stroke="#bbcbd4"/><text x="5" y="48">{number(hi)}</text><text x="5" y="235">{number(lo)}</text>{series.map(s=><g key={s.name}><polyline fill="none" stroke={s.color} strokeWidth="3" points={s.values.map((v,i)=>`${x(i)},${y(v)}`).join(' ')}/><circle cx={x(index)} cy={y(s.values[index])} r="6" fill={s.color}/></g>)}<text x="45" y="267">Primera muestra</text><text x="630" y="267">Última muestra</text></svg><p>{series.map(s=><span key={s.name} style={{color:s.color,marginRight:20}}>● {s.name}</span>)}</p></div>;
}
