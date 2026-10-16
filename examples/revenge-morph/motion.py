"""Speech-aligned explanatory geometry. Manim 0.19, native 60fps."""
import json, os
from pathlib import Path
import numpy as np
from manim import *
config.background_color='#111214'
config.frame_width=9
config.frame_height=16
W='#F4F4F1'; R='#FF4B32'; M='#62676C'

def playmark(size=.5,color=W):
    return Polygon([-size*.45,-size*.6,0],[-size*.45,size*.6,0],[size*.65,0,0],color=color,fill_opacity=1,stroke_width=0)

def node(p,r=.14,color=W):return Dot(p,radius=r,color=color)

def line(a,b,color=M,width=4):return Line(a,b,color=color,stroke_width=width)

class Promo(Scene):
    def at(self,t):
        if t>self.time:self.wait(t-self.time)
    def cue(self,word):
        for c in self.shot['captions']:
            for w in c['words']:
                if w['word'].strip(' .,!?').lower()==word.lower():return w['start']+.25
        raise ValueError(word)
    def construct(self):
        self.shot=json.loads(Path(os.environ['SHORTS_GEOMETRY_TIMELINE']).read_text())
        getattr(self,self.shot['id'])()
        self.at(self.shot['frames']/60)
    def flood(self):
        # Each triangle is one incoming Short; the receiver visibly compresses.
        marks=VGroup(*[playmark(.36,M).move_to([(i%7-3)*.85,4.9-(i//7)*.74,0]) for i in range(35)])
        receiver=Circle(1.05,color=W,stroke_width=5).move_to([0,-.9,0])
        core=node([0,-.9,0],.2,R)
        self.add(receiver,core)
        self.play(LaggedStart(*[GrowFromCenter(m) for m in marks],lag_ratio=.035),run_time=.8)
        self.play(LaggedStart(*[m.animate.move_to([(i%5-2)*.17,-.65+(i//5)*.12,0]).scale(.6).set_color(R) for i,m in enumerate(marks)],lag_ratio=.016),receiver.animate.stretch(.78,1),run_time=1.35,rate_func=rate_functions.ease_in_cubic)
        rings=VGroup(*[Arc(radius=1.3+i*.24,start_angle=.12,angle=PI-.24,color=R,stroke_width=4).move_to([0,.4+i*.24,0]) for i in range(3)])
        self.play(Create(rings),run_time=.5)
        self.at(self.cue('sit'))
        self.play(receiver.animate.stretch(1.28,1),marks.animate.shift(DOWN*.23),run_time=.35,rate_func=rate_functions.ease_out_back)
        self.at(self.cue('take'))
        self.play(Indicate(core,color=R,scale_factor=1.8),run_time=.55)
    def revenge(self):
        circle=Circle(1.05,color=W,stroke_width=5).move_to([0,-.9,0]);core=node([0,-.9,0],.2,R)
        self.add(circle,core)
        self.at(self.cue('Make'))
        ports=VGroup(*[node(p,.13) for p in [[-1.8,1,0],[0,2.8,0],[1.8,1,0]]])
        spokes=VGroup(*[line(core.get_center(),p.get_center(),W,4) for p in ports])
        self.play(Transform(circle,spokes),LaggedStart(*[GrowFromCenter(n) for n in ports],lag_ratio=.12),run_time=.85)
        self.at(self.cue('revenge'))
        outputs=VGroup(*[playmark(.5,R).move_to([x,4.7,0]) for x in [-2.2,0,2.2]])
        paths=VGroup(*[CubicBezier(core.get_center(),[x*1.5,-.2,0],[x*1.5,4.7,0],o.get_center(),color=M,stroke_width=3) for x,o in zip([-2.2,0,2.2],outputs)])
        self.play(Create(paths),run_time=.4)
        signals=VGroup(*[node(core.get_center(),.13,R) for _ in paths]);self.add(signals)
        self.play(*[MoveAlongPath(s,p) for s,p in zip(signals,paths)],run_time=.7)
        self.play(*[ReplacementTransform(s,o) for s,o in zip(signals,outputs)],run_time=.3)
        self.at(self.cue('Naturally'))
        self.play(Indicate(ports,color=R,scale_factor=1.18),run_time=.5)
    def production(self):
        seed=node([0,1.4,0],.3,R);self.add(seed)
        self.at(self.cue('guides'))
        script=VGroup(*[line([-2.4,2.7-i*.65,0],[2.4-(i%2)*.9,2.7-i*.65,0],W,9) for i in range(5)])
        self.play(ReplacementTransform(seed,script),run_time=.65,rate_func=rate_functions.ease_out_cubic)
        self.at(self.cue('voice'))
        wave=VGroup(*[line([x,1.2-h,0],[x,1.2+h,0],R,8) for x,h in [(x,.2+1.1*np.exp(-x*x/3)*abs(np.sin(x*2.5+.5))) for x in np.linspace(-2.7,2.7,25)]])
        self.play(ReplacementTransform(script,wave),run_time=.55)
        self.at(self.cue('Captions'))
        captions=VGroup(*[line([-1.75,-.8-i*.4,0],[1.75-i*.5,-.8-i*.4,0],W,7) for i in range(2)])
        self.play(TransformFromCopy(wave,captions),run_time=.55)
        self.at(self.cue('Moving'))
        ring=Circle(.7,color=W,stroke_width=5).move_to([0,3.5,0]);triangle=playmark(.7,R).move_to([0,3.5,0])
        self.play(TransformFromCopy(wave,ring),run_time=.35)
        self.play(ReplacementTransform(ring,triangle),wave.animate.stretch(.55,1),run_time=.4,rate_func=rate_functions.ease_out_back)
        self.at(self.cue('video'))
        frame=RoundedRectangle(width=3.5,height=5.1,corner_radius=.18,color=W,stroke_width=5).move_to([0,1.3,0])
        self.play(Create(frame),triangle.animate.move_to([0,2.4,0]).scale(1.3),wave.animate.scale(.45).move_to([0,.8,0]),captions.animate.scale(.65).move_to([0,-.2,0]),run_time=.65)
    def edit(self):
        pts=[[-2.8,3.8,0],[0,3.8,0],[2.8,3.8,0]]
        inputs=VGroup(*[node(p,.17) for p in pts]);junction=node([0,1.2,0],.23)
        paths=VGroup(*[line(p,junction.get_center()) for p in pts]);outpath=line([0,1,0],[0,-.7,0]);out=playmark(.9).move_to([0,-1.5,0])
        self.add(inputs,paths,junction,outpath,out)
        self.at(self.cue('skill'))
        self.play(inputs[1].animate.shift(UP*.7).set_color(R),paths[1].animate.put_start_and_end_on([0,4.5,0],junction.get_center()).set_color(R),run_time=.5,rate_func=rate_functions.ease_out_back)
        self.at(self.cue('creating'))
        signal=node(inputs[1].get_center(),.12,R);self.add(signal)
        self.play(MoveAlongPath(signal,paths[1]),run_time=.35)
        self.play(junction.animate.set_color(R),run_time=.15)
        self.play(signal.animate.move_to(out.get_center()),outpath.animate.set_color(R),run_time=.35)
        newout=VGroup(playmark(.9,R).move_to(out.get_center()),Circle(1.25,color=R,stroke_width=4).move_to(out.get_center()))
        self.remove(signal);self.play(ReplacementTransform(out,newout),run_time=.35)
        self.at(self.cue('app'))
        self.play(Indicate(newout,color=R,scale_factor=1.1),run_time=.4)
    def proof(self):
        tri=playmark(1,R).move_to([0,1.5,0]);ring=Circle(1.5,color=W,stroke_width=5).move_to([0,1.5,0])
        self.add(tri,ring)
        self.at(self.cue('made'))
        loop=Arc(radius=2.4,start_angle=-PI*.15,angle=PI*1.8,color=W,stroke_width=5).move_to([0,1.5,0]).add_tip(tip_length=.2)
        self.play(Transform(ring,loop),run_time=.5)
        dot=node(ring.get_start(),.14,R);self.add(dot)
        self.play(MoveAlongPath(dot,ring),run_time=.7);self.remove(dot)
        self.at(self.cue('flood'))
        tiles=VGroup(*[playmark(.42,R if i%3==0 else W).move_to([(i%5-2)*1.2,4.5-(i//5)*1.15,0]) for i in range(25)])
        self.play(tri.animate.scale(.42).move_to(tiles[12].get_center()),Uncreate(ring),run_time=.55)
        self.at(self.cue('adding'))
        self.play(LaggedStart(*[TransformFromCopy(tri,t) for i,t in enumerate(tiles) if i!=12],lag_ratio=.025),run_time=min(1.15,max(.4,self.shot['frames']/60-self.time-.1)))
