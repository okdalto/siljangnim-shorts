"""Measured, balanced bilingual caption wrapping."""
import math, re
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
@lru_cache(maxsize=100)
def font(size,weight='Bold'):return ImageFont.truetype(str(ROOT/'assets/fonts'/f'Pretendard-{weight}.otf'),size)
def wrap(value,size=64,width=920):
 """Balance complete words across lines; never split Korean endings into fragments."""
 d=ImageDraw.Draw(Image.new('RGB',(1,1)));result=[]
 for paragraph in value.split('\n'):
  tokens=re.findall(r'(?:Texture Warping|Vertex Jitter|Depth buffer|Gouraud Shading|Perspective correction|affine texture mapping|texture warping|vertex jitter|depth buffer|Gouraud shading|physics engine|neural network|velocity field|Growing NCA|WebGL Fluid|cell erasure|dye injection)\S*|\S+',paragraph)
  if not tokens:continue
  measure=lambda v:d.textlength(v,font=font(size))
  if any(measure(w)>width for w in tokens):raise ValueError('A caption word is too wide; shorten the caption')
  # Minimize raggedness at the smallest possible line count. Penalize short final lines.
  from functools import lru_cache
  @lru_cache(None)
  def layout(start,remaining):
   if remaining==0:return (0,[]) if start==len(tokens) else (float('inf'),[])
   best=(float('inf'),[])
   for end in range(start+1,len(tokens)+1):
    line=' '.join(tokens[start:end]);length=measure(line)
    if length>width:break
    cost,tail=layout(end,remaining-1)
    penalty=(width-length)**2
    if remaining==1 and start>0 and len(line.replace(' ',''))<5:penalty+=width**2*4
    if cost+penalty<best[0]:best=(cost+penalty,[line,*tail])
   return best
  for count in range(1,5):
   score,lines=layout(0,count)
   if math.isfinite(score):result.extend(lines);break
  else:raise ValueError('Caption exceeds four lines; shorten the narration sentence')
 return result
