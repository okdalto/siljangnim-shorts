import React from 'react';
import {AbsoluteFill, Audio, Composition, Img, Sequence, cancelRender, continueRender, delayRender, registerRoot, staticFile, useCurrentFrame} from 'remotion';
import Visual, {Cover} from 'agent-design';
import {CONTENT, LayoutGuides} from './layout';

type Caption={start:number;end:number;ko_lines:string[];en_lines:string[];words:{word:string;start:number;end:number}[]};
type Shot={id:string;frames:number;captions:Caption[]};
type Props={plan:Shot[];guides?:boolean};
function Font({children}:{children:React.ReactNode}){
 const [handle]=React.useState(()=>delayRender('Load font'));
 React.useEffect(()=>{new FontFace('Pretendard',`url(${staticFile('font.otf')})`).load().then(font=>{document.fonts.add(font);continueRender(handle)}).catch(cancelRender)},[handle]);
 return <AbsoluteFill style={{fontFamily:'Pretendard',fontWeight:700,color:'#f7f7f5',background:'#101112'}}>{children}</AbsoluteFill>;
}
function ShotView({shot}:{shot:Shot}){
 const frame=useCurrentFrame(),t=frame/60,c=shot.captions.filter(c=>c.start<=t).at(-1)??shot.captions[0];
 const height=c.ko_lines.length*64.8+18+c.en_lines.length*55.2;
 return <AbsoluteFill>
  {shot.id==='brand'?<><Img src={staticFile('logo.svg')} style={{position:'absolute',left:340,top:470,width:400,height:400}}/><div style={{position:'absolute',top:920,width:'100%',textAlign:'center',fontSize:100}}>siljangnim</div></>:<Visual shot={shot} frame={frame}/>}
  <div style={{position:'absolute',left:144,width:792,top:CONTENT.bottom-height,textAlign:'center',color:'#fff',textShadow:'0 2px 5px #000,0 1px 15px #000'}}>
   <div style={{fontSize:54,lineHeight:'64.8px'}}>{c.ko_lines.map((s,i)=><div key={i}>{s}</div>)}</div>
   <div style={{fontSize:46,lineHeight:'55.2px',marginTop:18}}>{c.en_lines.map((s,i)=><div key={i}>{s}</div>)}</div>
  </div>
  <Sequence from={15}><Audio src={staticFile(shot.id+'.wav')}/></Sequence>
 </AbsoluteFill>;
}
function Film({plan,guides}:Props){let cursor=0;return <Font>{plan.map(shot=>{const from=cursor;cursor+=shot.frames;return <Sequence key={shot.id} from={from} durationInFrames={shot.frames}><ShotView shot={shot}/></Sequence>})}{guides&&<LayoutGuides/>}</Font>}
function Thumbnail({guides=false}:{guides?:boolean}){return <Font><Cover/>{guides&&<LayoutGuides/>}</Font>}
registerRoot(()=> <><Composition id="Film" component={Film} width={1080} height={1920} fps={60} durationInFrames={60} defaultProps={{plan:[]} as Props} calculateMetadata={({props})=>({durationInFrames:Math.max(1,props.plan.reduce((n,s)=>n+s.frames,0))})}/><Composition id="Thumbnail" component={Thumbnail} defaultProps={{guides:false}} width={1080} height={1920} fps={60} durationInFrames={1}/></>);
