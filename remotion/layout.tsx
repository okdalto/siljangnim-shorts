import React from 'react';
// User preference: equal top and bottom padding. Shared by film and cover.
export const FRAME={width:1080,height:1920,paddingY:270,paddingX:144};
export const CONTENT={top:FRAME.paddingY,bottom:FRAME.height-FRAME.paddingY,left:FRAME.paddingX,right:FRAME.width-FRAME.paddingX,width:FRAME.width-2*FRAME.paddingX};
export function LayoutGuides(){return <div style={{position:'absolute',inset:0,pointerEvents:'none',fontFamily:'monospace',fontSize:27,color:'#00f0b0'}}>
 <div style={{position:'absolute',left:0,top:0,width:'100%',height:FRAME.paddingY,background:'#00f0b018',borderBottom:'3px solid #00f0b0',display:'grid',placeItems:'center'}}>TOP · 270 px</div>
 <div style={{position:'absolute',left:0,bottom:0,width:'100%',height:FRAME.paddingY,background:'#00f0b018',borderTop:'3px solid #00f0b0',display:'grid',placeItems:'center'}}>BOTTOM · 270 px</div>
 <div style={{position:'absolute',left:CONTENT.left,top:CONTENT.top,width:CONTENT.width,height:CONTENT.bottom-CONTENT.top,border:'2px dashed #00f0b0'}}/>
 </div>}
