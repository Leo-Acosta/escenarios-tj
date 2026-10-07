import React,{useState} from 'react';
import DiscardDialog from './discard-dialog';
export function useDiscard(){
 const [pending,setPending]=useState<{run:()=>void;description?:string;action?:string}|null>(null);
 function request(dirty:boolean,run:()=>void,options?:{description:string;action:string}){if(dirty)setPending({run,...options});else run();}
 const dialog=pending?<DiscardDialog description={pending.description} action={pending.action} onStay={()=>setPending(null)} onDiscard={()=>{setPending(null);pending.run();}}/>:null;
 return {request,dialog};
}
