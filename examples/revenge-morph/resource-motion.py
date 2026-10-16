"""Satirical resource-consumption beat inserted before the final flood."""
from motion import *

class ResourcePromo(Promo):
    def proof(self):
        tri=playmark(1,R).move_to([0,1.5,0]);ring=Circle(1.5,color=W,stroke_width=5).move_to([0,1.5,0])
        self.add(tri,ring)
        self.at(self.cue('made'))
        loop=Arc(radius=2.4,start_angle=-PI*.15,angle=PI*1.8,color=W,stroke_width=5).move_to([0,1.5,0]).add_tip(tip_length=.2)
        self.play(Transform(ring,loop),run_time=.5)
        dot=node(ring.get_start(),.14,R);self.add(dot)
        self.play(MoveAlongPath(dot,ring),run_time=.7);self.remove(dot)
        self.at(self.cue('Burn'))
        bolt=Polygon([.1,4.5,0],[-1.2,2.3,0],[-.2,2.3,0],[-.7,.9,0],[1.2,3.1,0],[.25,3.1,0],color=R,fill_opacity=1,stroke_width=0)
        bars=VGroup(*[Rectangle(width=.65,height=.35,color=W,fill_opacity=1,stroke_width=0).move_to([-1.6+i*.8,-.2,0]) for i in range(5)])
        self.play(ReplacementTransform(ring,bolt),tri.animate.scale(.45).move_to([0,-1.3,0]),FadeIn(bars),run_time=.35)
        self.play(LaggedStart(*[b.animate.move_to(tri.get_center()).scale(.05).set_opacity(0) for b in bars],lag_ratio=.12),Indicate(bolt,color=W,scale_factor=1.08),run_time=.65)
        self.at(self.cue('Waste'))
        tank=RoundedRectangle(width=3.6,height=3.0,corner_radius=.2,color=W,stroke_width=5).move_to([0,2.7,0])
        water=Rectangle(width=3.35,height=2.65,stroke_width=0,fill_color=R,fill_opacity=.85).move_to([0,2.6,0])
        self.play(ReplacementTransform(bolt,tank),FadeIn(water),run_time=.3)
        self.at(self.cue('cooling'))
        drops=VGroup(*[Dot([-.7+i*.35,1.1,0],radius=.10,color=R) for i in range(5)])
        self.add(drops)
        self.play(water.animate.stretch(.04,1,about_edge=DOWN),LaggedStart(*[d.animate.move_to(tri.get_center()).set_opacity(0) for d in drops],lag_ratio=.12),run_time=.7,rate_func=rate_functions.ease_in_cubic)
        self.at(self.cue('Fight'))
        self.play(FadeOut(tank),FadeOut(water),tri.animate.scale(1/.45).move_to([0,1.5,0]),run_time=.3)
        self.at(self.cue('flood'))
        tiles=VGroup(*[playmark(.42,R if i%3==0 else W).move_to([(i%5-2)*1.2,4.5-(i//5)*1.15,0]) for i in range(25)])
        self.play(tri.animate.scale(.42).move_to(tiles[12].get_center()),run_time=.45)
        self.at(self.cue('adding'))
        end=self.shot['captions'][-1]['end']
        self.play(LaggedStart(*[TransformFromCopy(tri,t) for i,t in enumerate(tiles) if i!=12],lag_ratio=.025),run_time=max(.4,min(1.15,end-self.time)))
