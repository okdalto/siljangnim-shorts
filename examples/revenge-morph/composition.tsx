import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, staticFile} from 'remotion';
import {CONTENT} from 'agent-layout';
// Replaced with content-addressed asset names by prepare.py.
const clips:Record<string,string>=__CLIPS__;
const labels:Record<string,string>={flood:'계속 쏟아지는 쇼츠',revenge:'보는 쪽에서, 만드는 쪽으로',production:'스킬을 따라 에이전트가 제작합니다',edit:'같은 대화에서, 보고 고칩니다',proof:'이 광고도 같은 과정으로'};
export default function Visual({shot}:{shot:{id:string}}){return <AbsoluteFill>
 <OffthreadVideo src={staticFile(clips[shot.id])} muted style={{width:1080,height:1920}}/>
 </AbsoluteFill>}
export function Cover(){return <AbsoluteFill style={{background:'#111214',color:'#f4f4f1'}}>
 <div style={{position:'absolute',left:CONTENT.left,top:CONTENT.top,fontSize:82,lineHeight:1.12,letterSpacing:-3}}>당신도 만들어서<br/><span style={{color:'#ff4b32'}}>복수하세요.</span></div>
 <svg width="1080" height="1920" viewBox="0 0 1080 1920" style={{position:'absolute',inset:0}}>
  <path d="M270 700C270 980 810 660 810 980" stroke="#62676c" strokeWidth="5" fill="none"/>
  <path d="M810 1070C810 1370 270 1370 270 1080" stroke="#f4f4f1" strokeWidth="7" fill="none"/>
  <path d="M240 1110L270 1070L300 1110" stroke="#ff4b32" strokeWidth="8" fill="none"/>
  <circle cx="270" cy="680" r="27" fill="#ff4b32"/>
  {Array.from({length:19},(_,i)=>{const h=25+105*Math.exp(-Math.pow((i-9)/6,2))*Math.abs(Math.sin(i*.8));return <line key={i} x1={350+i*20} x2={350+i*20} y1={880-h} y2={880+h} stroke={i<9?'#f4f4f1':'#ff4b32'} strokeWidth="7" strokeLinecap="round"/>})}
  <circle cx="810" cy="1040" r="80" fill="none" stroke="#f4f4f1" strokeWidth="6"/>
  <path d="M785 997L850 1040L785 1083Z" fill="#ff4b32"/>
  <circle cx="270" cy="1040" r="18" fill="#ff4b32"/>
 </svg>
 <div style={{position:'absolute',left:144,top:1430,fontSize:38,color:'#b8b9b8'}}>에이전트에 붙이는 쇼츠 제작 스킬</div>
 <div style={{position:'absolute',left:144,top:CONTENT.bottom-88,display:'flex',alignItems:'center',gap:20}}><Img src={staticFile('logo.svg')} style={{width:88,height:88}}/><span style={{fontSize:43}}>실장님 Shorts</span></div>
 </AbsoluteFill>}
