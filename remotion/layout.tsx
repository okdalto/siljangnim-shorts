import React from 'react';
// Symmetric composition bounds are separate from platform caption safety.
export const FRAME={width:1080,height:1920,paddingY:270,paddingX:144};
export const CONTENT={top:FRAME.paddingY,bottom:FRAME.height-FRAME.paddingY,left:FRAME.paddingX,right:FRAME.width-FRAME.paddingX,width:FRAME.width-2*FRAME.paddingX};
export const CAPTIONS={bottom:1550,maxHeight:258,left:144,width:792};
export const GRAPHICS={top:292,bottom:1260,gap:32};
export function LayoutGuides(){return <div style={{position:'absolute',inset:0,pointerEvents:'none',fontFamily:'monospace',fontSize:27,color:'#00f0b0'}}>
 <div style={{position:'absolute',left:0,top:0,width:'100%',height:FRAME.paddingY,background:'#00f0b018',borderBottom:'3px solid #00f0b0',display:'grid',placeItems:'center'}}>TOP · 270 px</div>
 <div style={{position:'absolute',left:0,bottom:0,width:'100%',height:FRAME.paddingY,background:'#00f0b018',borderTop:'3px solid #00f0b0',display:'grid',placeItems:'center'}}>BOTTOM · 270 px</div>
 <div style={{position:'absolute',left:0,top:CAPTIONS.bottom,width:'100%',height:FRAME.height-CAPTIONS.bottom,background:'#ff604022',borderTop:'3px solid #ff6040'}}>CAPTION SAFE · y1550</div>
 <div style={{position:'absolute',left:144,top:GRAPHICS.bottom,width:792,borderTop:'2px dashed #ffcc66'}}>GRAPHICS · y1260</div>
 <div style={{position:'absolute',left:CONTENT.left,top:CONTENT.top,width:CONTENT.width,height:CONTENT.bottom-CONTENT.top,border:'2px dashed #00f0b0'}}/>
 </div>}
