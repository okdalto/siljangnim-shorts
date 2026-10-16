import React from 'react';
import {AbsoluteFill,spring} from 'remotion';
const W='#f4f4f1',R='#ff4b32',BG='#111214';
type Shot={id:string;frames:number;captions:{start:number;words?:{word:string;start:number}[]}[]};
function Card({x,y,scale=1,red=false,angle=0}:{x:number;y:number;scale?:number;red?:boolean;angle?:number}){
 return <div style={{position:'absolute',left:x-174,top:y-282,width:348,height:564,transform:`rotate(${angle}deg) scale(${scale})`,background:red?R:'#24272b',border:`3px solid ${red?'#ff826a':'#747a80'}`,borderRadius:30,boxShadow:'0 20px 35px #0007',display:'grid',placeItems:'center'}}>
 <svg width="142" height="142" viewBox="0 0 142 142"><circle cx="71" cy="71" r="68" fill="none" stroke={W} strokeWidth="4"/><path d="M53 35L106 71L53 107Z" fill={W}/></svg>
 <div style={{position:'absolute',left:28,right:28,bottom:30,height:5,borderRadius:3,background:'#ffffff35'}}><div style={{width:'38%',height:5,background:W}}/></div>
 </div>
}
const pop=(f:number)=>spring({frame:Math.max(0,f),fps:60,config:{damping:18,stiffness:180,mass:.8}});
// Integrate a short acceleration ramp followed by steadily declining velocity.
// Starts and finishes at rest; most of the journey is a gradual deceleration.
const decelerate=(t:number)=>{
 t=Math.max(0,Math.min(1,t));const r=.04;
 const ramp=(x:number)=>(x*x/2-2*x*x*x/3+x*x*x*x/4)/r;
 const cruise=(x:number)=>x-x*x+x*x*x/3;
 return (t<r?ramp(t):ramp(r)+cruise(t)-cruise(r))/(ramp(r)+1/3-cruise(r));
};
function Radial({frame,shift=0}:{frame:number;shift?:number}){
 const cards=[];
 // The same card multiplies around its centre; each copy travels outward.
 for(let ring=1;ring>=0;ring--){
  const count=ring?12:8;
  for(let i=0;i<count;i++){
   const born=44+ring*40+i*4;
   if(frame<born)continue;
   const p=pop(frame-born),a=(i/count)*Math.PI*2-Math.PI/2;
   const rx=ring?445:270,ry=ring?350:235;
   cards.push(<Card key={`${ring}-${i}`} x={540+Math.cos(a)*rx*p-shift} y={815+Math.sin(a)*ry*p} scale={(ring?.32:.4)*p} angle={Math.cos(a)*8*p}/>);
  }
 }
 return <>{cards}<Card x={540-shift} y={815} scale={.82*pop(frame)}/></>;
}
export default function Visual({shot,frame}:{shot:Shot;frame:number}){
 const answer=shot.id==='revenge';
 // Enter from the right. Existing cards only move after the leading card touches them.
 const count=48,pitch=322,lastGap=1000;
 const offset=(i:number)=>i===count-1?(count-2)*pitch+lastGap:i*pitch;
 const travel=1370+offset(count-1)-540;
 // Word timestamps are audio-relative; narration begins at frame 15.
 const naturally=shot.captions.flatMap(c=>c.words??[]).find(w=>w.word.trim().toLowerCase().replace(/[^a-z]/g,'')==='naturally');
 const stopFrame=naturally?Math.round((naturally.start+.25)*60):shot.frames-54;
 const move=decelerate((frame-18)/Math.max(1,stopFrame-18));
 const lead=1370-travel*move;
 const outerEdge=540+445+348*.32/2;
 const frontEdge=lead-348*.88/2;
 const push=answer?Math.max(0,outerEdge-frontEdge):0;
 return <AbsoluteFill style={{background:BG,overflow:'hidden'}}>
 {push<1600&&<Radial frame={answer?200:frame} shift={push}/>}
 {answer&&Array.from({length:count},(_,i)=>{const x=lead+offset(i);return x> -220&&x<1300?<Card key={i} x={x} y={815} scale={.88} red/>:null})}
 <div style={{position:'absolute',left:0,right:0,top:1270,height:120,background:`linear-gradient(transparent,${BG})`}}/>
 </AbsoluteFill>
}
export function Cover(){return <AbsoluteFill style={{background:BG}}><Radial frame={200}/></AbsoluteFill>}
