import React from 'react';
import {AbsoluteFill,Img,OffthreadVideo,staticFile} from 'remotion';
import Opening from './opening';
export default function Visual(props:React.ComponentProps<typeof Opening>){
 if(['flood','revenge'].includes(props.shot.id))return <Opening {...props}/>;
 return <AbsoluteFill><OffthreadVideo src={staticFile(props.shot.id+'.mp4')} muted style={{width:1080,height:1920}}/></AbsoluteFill>;
}
export function Cover(){return <AbsoluteFill style={{background:'#111214',color:'#f4f4f1'}}>
 <div style={{position:'absolute',top:270,left:144,fontSize:100,lineHeight:1.1,letterSpacing:-5}}>쇼츠에 당했나요?<br/><span style={{color:'#ff4b32'}}>복수하세요.</span></div>
 <svg width="1080" height="1920" viewBox="0 0 1080 1920" style={{position:'absolute',inset:0}}>
 <defs><linearGradient id="red" x2="1" y2="1"><stop stopColor="#ff8769"/><stop offset=".5" stopColor="#ff4b32"/><stop offset="1" stopColor="#c52216"/></linearGradient><filter id="shadow"><feDropShadow dx="0" dy="20" stdDeviation="20" floodOpacity=".6"/></filter></defs>
 {Array.from({length:12},(_,i)=>{const a=i*Math.PI/6;return <g key={i} transform={`translate(${540+290*Math.cos(a)},${1000+270*Math.sin(a)}) rotate(${i*30+10})`}><rect x="-67" y="-112" width="134" height="224" rx="18" fill="#25282d" stroke="#646a73" strokeWidth="3"/><path d="M-19-28L29 0L-19 28Z" fill="#979da6"/></g>})}
 <g transform="translate(540 1000) rotate(-9)" filter="url(#shadow)"><rect x="-160" y="-263" width="320" height="526" rx="35" fill="url(#red)" stroke="#ffac8d" strokeWidth="4"/><circle r="80" fill="none" stroke="#fff6ed" strokeWidth="5"/><path d="M-24-43L49 0L-24 43Z" fill="#fff6ed"/></g>
 </svg>
 <div style={{position:'absolute',left:144,top:1430,fontSize:38}}>에이전트에 붙이는 쇼츠 제작 스킬</div>
 <div style={{position:'absolute',left:144,bottom:270,display:'flex',alignItems:'center',gap:20}}><Img src={staticFile('logo.svg')} style={{width:88,height:88}}/><span style={{fontSize:43}}>실장님 Shorts</span></div>
 </AbsoluteFill>}
