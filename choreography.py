"""Word-directed additions to the original, diverse terminal scene library.

The upstream scenes remain the visual baseline. New shots have individual
blocking; there is deliberately no universal particle/morph replacement.
"""
import bisect
import math

import scenes as original
from word_score import score, normalized

TAU = math.tau
D, N, B, W, R, G, K = range(7)
EXECUTIONS = (147.66, 148.6, 149.52, 150.54, 151.52, 152.28,
              153.16, 153.98, 155.2, 156.08, 157.04, 158.)
clamp = original.clamp
mix = original.mix
hash16 = original.hash16
clear = original.clear


def palette(t):
    # Preserve the original gold phosphor, with a cooler isolation passage.
    colors = (137, 215, 221, 230, 203, 94, 58)
    if 110.9 <= t < 125.708:
        colors = (66, 109, 153, 230, 203, 60, 237)
    return {i: f'\x1b[{1 if i in (B, W) else 0};38;5;{n}m'
            for i, n in enumerate(colors)}


def when(line, word, occurrence=0):
    return score().onset(line, word, occurrence)


def phase(t, line, word, duration=.4, occurrence=0):
    return score().phase(t, line, word, duration, occurrence)


def retime(t, begin, end, anchors):
    """Map actual word onsets to a legacy shot's authored action phases.

    This changes animation phase only, never the audio or caption clock.
    """
    knots = [(begin, begin)]
    for real, visual in sorted(anchors):
        if begin < real < end and visual >= knots[-1][1]:
            if real > knots[-1][0] + .001:
                knots.append((real, min(end-.001, visual)))
    knots.append((end, end))
    for (a, x), (b, y) in zip(knots, knots[1:]):
        if t < b: return mix(x, y, clamp((t-a)/max(.001, b-a)))
    return t


def switch_windows():
    # Keep the result through the connecting words, up to the next action.
    return (
        (44.452, when(47.672, 'blind'), when(45.85, 'DC'), 45.85, 1.10, .30),
        (88.587, when(92.015, 'do'), when(90.197, 'M'), 90.197, 1.25, .35),
        (92.015, when(95.465, 'switch'), when(93.953, 'PM'), 94.55, .915, .30),
    )


def scripted_time(t):
    # Finish the change at a readable speed, then hold its completed state.
    # Do not stretch the animation to the shot boundary: that leaves no hold.
    for begin, end, onset, visual, span, duration in switch_windows():
        if onset <= t < end:
            return visual + span * clamp((t-onset)/duration)
    # Preserve complex upstream animations, but move decisive actions onto words.
    mappings = (
        (40.706, 44.452, [(when(40.706, 'approach'), 41.1),
                         (when(40.706, 'infinity'), 42.0),
                         (when(42.346, 'you'), 42.346), (43.507, 43.507)]),
        (44.452, 47.672, [(when(44.452, 'current'), 45.2),
                         (when(45.85, 'AC'), 45.7), (when(45.85, 'DC'), 45.85)]),
        (47.672, 51.363, [(when(47.672, 'blind'), 48.1),
                         (when(47.672, 'vision'), 48.5),
                         (when(49.534, 'dizzy'), 49.0), (when(49.534, 'dizzy', 1), 50.3)]),
        (55.083, 59.223, [(when(55.083, 'unite'), 55.4),
                         (when(56.916, 'deeply'), 56.9), (when(56.916, 'deeply', 1), 58.0)]),
        (59.223, 66.601, [(when(59.687, 'give'), 60.0), (61.958, 61.958),
                         (when(63.535, 'only'), 64.8), (65.397, 65.397)]),
        (66.601, 70.084, [(when(66.601, 'happy'), 67.8),
                         (when(68.252, 'run'), 68.252), (69.259, 69.259)]),
        (88.587, 92.015, [(when(88.587, 'gender'), 89.2),
                         (when(90.197, 'F'), 90.0), (when(90.197, 'M'), 90.197)]),
        (92.015, 95.465, [(when(93.953, 'AM'), 93.6), (when(93.953, 'PM'), 94.55)]),
        (95.465, 99.349, [(when(95.465, 'role'), 96.0),
                         (when(97.739, 'S'), 96.5), (when(97.739, 'M'), 97.8)]),
        (103.489, 110.9, [(when(104.197, 'feel'), 105.0), (106.293, 106.293),
                         (when(107.903, 'finally'), 108.0), (110.221, 110.221)]),
        (118.333, 125.708, [(when(118.979, 'erase'), 119.0), (120.86, 120.86),
                         (when(122.714, 'leave'), 123.25), (124.89, 124.89)]),
    )
    for begin, end, anchors in mappings:
        if begin <= t < end: return retime(t, begin, end, anchors)
    return t


def scope_grid(c, area):
    l, top, r, bt = area
    for y in range(top+2, bt-1, 3):
        for x in range(l+2, r-1, 6): c.put(x, y, '+', G)


def label(c, x, y, text, ink=W):
    clear(c, x-1, y, len(text)+2, 1)
    c.put(x, y, text, ink)


def power(c, t, area):
    """SWITCH closes the lever; ON ignites; POWER travels down the LINE."""
    l, top, r, bt = area
    cx, cy = (l+r)//2, (top+bt)//2
    close = phase(t, .1, 'Switch', .22)
    live = t >= when(.1, 'on')
    travel = phase(t, .1, 'power', max(.15, when(.1, 'line')-when(.1, 'power')))
    scope_grid(c, area)
    source_x, switch_x, target_x = l+3, l+(r-l)//3, r-14
    c.box(source_x, cy-3, 12, 7, B)
    c.put(source_x+3, cy-1, '+ 12V', W)
    c.put(source_x+3, cy+1, '- GND', N)
    c.line(source_x+12, cy, switch_x, cy, '=', N)
    lever_y = cy-int(4*(1-close))
    c.line(switch_x, cy, switch_x+9, lever_y, '/', W)
    c.put(switch_x, cy, 'o', W); c.put(switch_x+9, cy, 'o', W)
    c.line(switch_x+10, cy, target_x, cy, '-' if not live else '=', B if live else G)
    c.box(target_x, cy-3, 13, 7, W if live else G)
    c.put(target_x+4, cy-1, 'ME', W)
    c.put(target_x+2, cy+1, 'ONLINE' if travel >= 1 else 'OFFLINE', B if travel >= 1 else G)
    if live:
        end = int(mix(switch_x+10, target_x, travel))
        for x in range(switch_x+10, end):
            c.put(x, cy, '>' if (x-int(t*45)) % 7 == 0 else '=', W)
        for y in range(cy+5, min(bt, cy+8)):
            c.put(l+3, y, ('01011010 ' * c.w)[:int((r-l-4)*travel)], G)
    c.center(top, 'POWER LINE / SWITCH -> CONTACT -> CURRENT', B)
    c.center(bt, '[ CIRCUIT CLOSED / ENTITY ONLINE ]' if travel >= 1 else '[ SWITCH ON ]', W)


def protection(c, t, area):
    l, top, r, bt = area; cx, cy = (l+r)/2, (top+bt)/2
    u = phase(t, 1.74, 'put', .5) if t < 2.92 else clamp(.6+(t-2.92)*.6)
    rx, ry = (r-l)*.30, max(2, (bt-top)*.34)
    c.center(top, 'REMEMBER / PUT ON PROTECTION', B)
    for side in (-1, 1):
        xx = cx+side*(rx+(1-u)*(r-l)*.35)
        for y in range(top+3, bt-2): c.put(xx, y, ']' if side<0 else '[', B)
    vertices = [(cx-rx, cy-ry), (cx+rx, cy-ry), (cx+rx*.85, cy+ry*.3),
                (cx, cy+ry), (cx-rx*.85, cy+ry*.3)]
    for i, (x, y) in enumerate(vertices):
        xx, yy = vertices[(i+1)%len(vertices)]
        c.line(x, y, mix(x, xx, u), mix(y, yy, u), '#', W if t>=2.92 else N)
    for row in range(int(cy-ry)+1, int(cy+ry)):
        if (row+int(t*12)) % 3 == 0:
            span = int(rx*.65*u)
            c.put(cx-span, row, ':'*(span*2), G)
    label(c, int(cx)-2, int(cy), '[ME]')
    c.center(bt, '[ PROTECTION ACTIVE ]' if t>=2.92 else 'SHIELD ASSEMBLING AROUND ME', B)


def dimension(c, t, area):
    l, top, r, bt = area; cx, cy = (l+r)/2, (top+bt)/2
    give = when(31.116, 'give'); receiver = when(31.116, 'you')
    if t < give:
        # First the individual points, then their set, rather than a ready-made cube.
        start = when(29.709, 'set')
        n = int(12+clamp((t-start)/.5)*160)
        gather = phase(t, 29.709, 'points', .35)
        for i in range(n):
            x = l+2+hash16(i*31) % max(1,r-l-4)
            y = top+2+hash16(i*67) % max(1,bt-top-4)
            gx = cx+math.cos(i*2.399)*min(r-l,bt-top)*.4
            gy = cy+math.sin(i*2.399)*(bt-top)*.3
            c.put(mix(x,gx,gather*.45), mix(y,gy,gather*.45), '*' if i%7==0 else '.', W if i%7==0 else B)
        c.center(top, 'IF I AM A SET OF POINTS', B)
        c.center(bt, '{ p0, p1, p2, ... }', N)
        return
    # GIVE connects; YOU lifts a surface; DIMENSION unfolds a volume.
    anchors = [(give, 30.584), (receiver, 31.459), (32.682, 32.334), (33.412,33.412)]
    clock = retime(t, 29.709, 33.412, anchors)
    original.lyric_points_dimension(c, clock, area, clock-29.709)
    if t >= 32.682:
        clear(c,l,top,r-l+1,bt-top+1)
        depth=.08+.87*clamp((t-32.682)/.5)
        vertices=[(x,y,z*depth) for z in (-1,1) for y in (-.88,.88) for x in (-.88,.88)]
        edges=[(i,j) for i in range(8) for j in range(i+1,8) if bin(i^j).count('1')==1]
        # A surface extrudes into an actual terminal-sized coordinate volume.
        for z in (-depth,depth):
            for a in range(9):
                q=-.88+a*.22
                ps=[original.point(x,y,z,area,t) for x,y in ((q,-.88),(q,.88),(-.88,q),(.88,q))]
                c.line(ps[0][0],ps[0][1],ps[1][0],ps[1][1],'.',G)
                c.line(ps[2][0],ps[2][1],ps[3][0],ps[3][1],'.',G)
        original.projected(c,vertices,edges,area,t,B)
        for axis,p in enumerate(((1.2,0,0),(0,1.2,0),(0,0,depth*1.35))):
            x,y,_=original.point(*p,area,t);c.put(x,y,'XYZ'[axis],W)
        c.center(top, 'DIMENSION / 0D -> 1D -> 2D -> 3D', W)
        c.center(bt, 'GIVE YOU MY DIMENSION / SURFACE -> VOLUME',B)


def circumference(c, t, area):
    """The circle visibly gives away its circumference by unrolling it."""
    l, top, r, bt = area; cy=(top+bt)/2
    cx=l+(r-l)*.29; rx=(r-l)*.23; ry=max(2,(bt-top)*.34)
    reveal=phase(t,33.412,'circle',.35)
    give=phase(t,34.646,'give',.3)
    unwind=clamp((t-36.287)/.64)
    scope_grid(c,area)
    for i in range(260):
        u=i/259
        if u>reveal:continue
        a=-math.pi/2+u*TAU
        x=cx+math.cos(a)*rx;y=cy+math.sin(a)*ry
        # On CIRCUMFERENCE the same arc becomes a measured straight gift.
        target_x=l+2+u*(r-l-4);target_y=cy+ry*.85
        if unwind:
            x=mix(x,target_x,unwind);y=mix(y,target_y,unwind)
        c.put(x,y,'#' if i%10==0 else 'o',W if u<give else B)
    if reveal and not unwind:
        c.line(cx,cy,cx+rx,cy,'-',N);label(c,int(cx+rx*.45),int(cy)-1,'r',B)
        c.put(cx,cy,'@',W)
    if give:
        target=int(l+(r-l)*.82)
        c.box(target-5,int(cy)-2,11,5,N);c.put(target-1,cy,'YOU',W)
        head=int(mix(cx+rx,target-6,((t-when(34.646,'give'))*1.4)%1))
        c.put(head,cy,'>>>',W)
    c.center(top,'CIRCLE -> GIVE YOU MY -> CIRCUMFERENCE',B)
    c.center(bt,'C = 2*pi*r  /  THE BOUNDARY ITSELF IS YOURS' if unwind else 'r -> RADIUS    C -> CIRCUMFERENCE',W if unwind else N)


def tangents(c,t,area):
    l,top,r,bt=area;cy=(top+bt)/2;span=r-l-4;amp=max(2,(bt-top)*.25)
    scope_grid(c,area)
    wave=phase(t,37.067,'wave',.25)
    sit=phase(t,38.596,'sit',.35)
    count=5 if t>=40.049 else 1
    def sample(x):
        a=(x-l)/max(1,span)*TAU*2.2-t*.3
        return cy+math.sin(a)*amp,math.cos(a)*amp/max(1,span)*TAU*2.2
    prev=None
    for x in range(l+2,r-1):
        y,slope=sample(x)
        y=mix(cy,y,.2+.8*wave)
        if prev:c.line(*prev,x,y,'~',B)
        prev=(x,y)
    if sit:
        for i in range(count):
            x=l+span*(i+1)/(count+1);y,slope=sample(x)
            length=max(4,int(span/(count+1)*.4))
            c.line(x-length,y-slope*length,x+length,y+slope*length,'/',W if t>=40.049 else N)
            c.put(x,y,'@',W)
            # YOU lands on the tangent only when "sit" is sung.
            yy=y-1-(1-sit)*max(2,(bt-top)*.45)
            c.put(x-1,yy,'YOU' if i==count//2 else 'o',W)
    c.center(top,'SINE WAVE / YOU CAN SIT ON ALL MY TANGENTS',B)
    c.center(bt,"y = sin(x)   ->   y' = cos(x)" if t>=40.049 else 'A WAVE BECOMES A PLACE FOR YOU',W if t>=40.049 else N)


def assembly(c,t,area):
    l,top,r,bt=area
    if t<6.38:
        down=when(3.873,'down');pieces=when(3.873,'pieces')
        elapsed=max(0,t-down)/max(.2,5.491-down)*2.5
        original.lyric_lay_pieces(c,t,area,elapsed)
        c.center(top,'LAY DOWN YOUR PIECES',B)
        if t>=pieces:
            c.center(bt,'[ PARTS RECEIVED / READY TO CREATE ]',W)
    else:
        create=when(6.38,'CREATION')
        u=clamp((t-create)/max(.15,7.446-create))
        original.lyric_object_creation(c,t,area,u)
        c.center(top,'OBJECT' if t<create else 'OBJECT CREATION',W)
        c.center(bt,'allocate(me)' if t<create else 'new Entity(me);',B)


def parameters(c,t,area):
    fill=when(7.446,'Fill');data=when(7.446,'data');params=when(7.446,'parameters')
    l,top,r,bt=area
    progress=clamp((t-fill)/max(.2,params-fill))
    original.lyric_data_parameters(c,t,area,progress*2.6)
    if t<data:
        c.center(top,'FILL IN MY ...',W)
    elif t<10.091:
        c.center(top,'DATA -> PARAMETERS' if t>=params else 'MY DATA',W)
    else:
        cy=(top+bt)//2
        clear(c,l,cy-2,r-l+1,5)
        c.big(cy-2,'INITIALIZE',W)
        c.center(bt,'[ PARAMETERS COMMITTED / INITIALIZATION COMPLETE ]',B)


def time_travel(c,t,area):
    ad=when(53.225,'A.D');bc=when(53.225,'B.C')
    if t<ad:u=.08*clamp((t-when(51.363,'travel'))/.6)
    elif t<bc:u=mix(.08,.45,clamp((t-ad)/max(.1,bc-ad)))
    else:u=mix(.55,1.,clamp((t-bc)/.35))
    original.lyric_time_travel(c,t,area,u*3.7)
    l,top,r,bt=area
    if t>=bc:c.center(top,'B.C. / TIME RUNS BACKWARD',W)
    elif t>=ad:c.center(top,'A.D. / CROSSING THE TIMELINE',W)


def organic_accents(c,t,area):
    """Keep the original mesh/workspace, but gate its subject and transfer on words."""
    l,top,r,bt=area
    if t<77.576:
        start,noun,give_line,verb,keyword=(74.045,'eggplant',75.422,'give',76.959)
    elif t<81.351:
        start,noun,give_line,verb,keyword=(77.576,'tomato',79.226,'give',80.620)
    else:
        start,noun,give_line,verb,keyword=(81.351,'cat',82.833,'purr',84.268)
    side=min(25,max(17,c.w//6)) if c.w>=100 else 0
    ml=side+4 if side else 4;mr=c.w-side-5 if side else c.w-5
    mt=top+3;mb=bt-1;cx=(ml+mr)/2;cy=(mt+mb)/2
    target=round(mix(cx,mr,.67))
    reveal=phase(t,start,noun,.3)
    if reveal<1:
        for yy in range(mt+1,mb):
            for xx in range(ml,int(cx)+1):
                if hash16(xx*31+yy*73)/65535>reveal:c.put(xx,yy,' ',G)
        if reveal==0:
            label(c,int((ml+cx)/2)-3,int(cy),'[ ME ]',W)
            c.put(ml+1,mt+1,'if (me is ...)',N)
    departure=when(give_line,verb)
    # Remove the always-on upstream packets until the actual sung verb.
    for yy in range(int(cy)-3,int(cy)+4):
        clear(c,int(cx)+1,yy,max(0,target-6-int(cx)),1)
    if t>=departure:
        strength=clamp((t-departure)/.3)
        for lane in (-2,-1,0,1,2):
            yy=cy+lane
            span=max(1,target-7-cx)
            for packet in range(3):
                u=((t-departure)*(1.1+strength)+packet/3+lane*.07)%1
                x=cx+1+u*span
                ch='~' if verb=='purr' else ('N' if noun=='eggplant' else 'A') if t>=keyword else '>'
                c.put(x,yy,ch,W if lane==0 else B)
        if verb=='purr':
            for j in range(3):
                rr=((t-departure)*1.5+j/3)%1
                c.put(cx-2+rr*7,cy-4,')',B)
                c.put(cx-2+rr*7,cy+4,')',B)
    if t<departure:c.center(mb,'[ SUBJECT READY / WAITING TO GIVE ]',N)


def god_proof(c,t,area):
    l,top,r,bt=area;cx,cy=(l+r)//2,(top+bt)//2
    original.lyric_god_existence(c,t,area,t-85.078)
    god=when(85.078,'god');proof=when(86.538,'proof')
    if t<god:
        c.center(top,'IF I AM THE ONLY ...',B)
    elif t<proof:
        c.center(top,'GOD / EXISTENCE NEEDS A WITNESS',W)
    else:
        u=clamp((t-proof)/max(.15,87.922-proof))
        clear(c,l,cy-3,r-l+1,7)
        left=l+(r-l)//4;right=r-(r-l)//4
        c.box(left-5,cy-2,11,5,B);c.put(left-2,cy,'GOD',W)
        c.box(right-5,cy-2,11,5,W);c.put(right-2,cy,'YOU',W)
        c.line(left+6,cy,right-6,cy,'=',B)
        c.put(mix(left+6,right-6,u),cy,'>',W)
        c.center(top,'PROOF OF MY EXISTENCE',W)
        c.center(bt,'ME EXISTS <=> YOU / WITNESS CONFIRMED' if t>=87.922 else 'VERIFYING EXISTENCE THROUGH YOU',B)


def algebra(c,t,area):
    l,top,r,bt=area;cx,cy=(l+r)//2,(top+bt)//2
    a=when(184.54,'algebraic');exp=when(184.54,'expression')
    scope_grid(c,area)
    equations=('x = sin(t)', 'y = cos(t)', 'x*x + y*y = 1',
               '(x*x+y*y-1)^3', '    - x*x*y^3 = 0')
    progress=clamp((t-a)/max(.2,exp-a))
    left=l+2;split=l+(r-l)//2
    for i,text in enumerate(equations):
        if i/len(equations)<=progress:
            yy=top+3+i*max(1,(bt-top-7)//len(equations))
            c.put(left,yy,text[:max(1,split-left-1)],W if i==int(progress*4) else B)
    if t>=a:
        # The equation on the left actually defines the heart plotted on the right.
        mid=(split+r)/2;half_w=max(4,(r-split)*.43);half_h=max(2,(bt-top)*.35)
        for yy in range(top+2,bt-1):
            for xx in range(split+2,r):
                nx=(xx-mid)/half_w;ny=-(yy-cy)/half_h+.18
                implicit=(nx*nx+ny*ny-1)**3-nx*nx*ny**3
                if implicit<=0:
                    c.put(xx,yy,'#' if t>=exp else '.',W if abs(implicit)<.1 else B)
        c.line(split,top+2,split,bt-1,'|',G)
        c.put(split-1,cy,'->',W)
    c.center(top,'I KNOW / THE ALGEBRAIC EXPRESSION OF LOVE',B)
    c.center(bt,'THE EQUATION IS CORRECT. THE ABSENCE REMAINS.',N)


def freedom(c,t,area,pulse):
    l,top,r,bt=area;cx,cy=(l+r)//2,(top+bt)//2
    free=when(188.483,'free');trapped=when(189.746,'trapped')
    original.lyric_trapped_loop(c,t,area,max(0,t-trapped),pulse)
    # One gate opens for YOU; the remaining bars close on ME at "trapped".
    exit_x=r-8
    for yy in range(top+2,bt-1):
        clear(c,exit_x-3,yy,9,1)
    move=clamp((t-free)/.6)
    x=mix(cx+8,r+5,move)
    if x<r-2:label(c,int(x),cy,'YOU',W)
    if t<free:c.center(top,'THOUGH YOU ARE ...',B)
    elif t<trapped:c.center(top,'YOU ARE FREE',W)
    else:
        label(c,cx-2,cy,'[ME]',W)
        c.center(top,'I AM TRAPPED',R)
    c.center(bt,'YOU -> FREE / ME -> TRAPPED IN LOVE' if t>=trapped else 'EXIT GRANTED TO YOU',N)


def word_overlay(c,t,area,word,response=0):
    """Small semantic accents, layered over the full upstream shot, not replacing it."""
    if not word:return
    l,top,r,bt=area;cx,cy=(l+r)//2,(top+bt)//2
    key=word['key'];age=max(0,t-word['start']);u=clamp(age/max(.12,word['end']-word['start']))
    # Grammatical words keep the subject/condition relationship visible. The
    # meaningful verb/noun actions are staged in their individual scene functions.
    if key in ('if','though','then','maybe') and age<.35:
        edge=min(12,int((r-l)*.1))
        c.put(l,top+1,'[ '+key.upper(),B)
        c.put(r-edge,bt-1,key.upper()+' ]',B)
    if key in ('give','giving'):
        for lane in (-1,0,1):
            y=cy+lane*max(1,(bt-top)//6)
            for tail in range(6):
                x=int(mix(l+3,r-8,u))-tail
                if l<x<r:c.put(x,y,'>' if tail==0 else '=',W if tail<2 else B)
    if key in ('you','your') and t<110.9:
        x=r-8;y=bt-2
        label(c,x,y,'[YOU]',W)
    elif key in ('im','ive','my','me'):
        label(c,l+2,bt-2,'[ME]',B)
    if key in ('all','only') and age<.6:
        # ALL lights distributed receivers; ONLY leaves a single receiver active.
        count=7 if key=='all' else 1
        for i in range(count):
            x=int(l+(r-l)*(i+1)/(count+1))
            c.put(x,bt-1,'*',W)
    if key in ('run','execute') and age<.5:
        sweep=int(l+(r-l)*u)
        for y in range(top+1,bt):
            ch,ink=c.cells[y][sweep]
            if ch.strip():c.cells[y][sweep]=(ch,W)
    if key in ('erase','pointless') and 118.333<=t<121.728:
        sweep=int(l+(r-l)*u)
        c.line(sweep,top+2,sweep,bt-2,'|',W)
    if key=='free' and t>=188.483:
        x=int(mix(cx,r-3,u))
        label(c,x,top+2,'YOU ->',W)
    if response>.1:
        # A keyboard response is an annotation, never a replacement for the song.
        c.put(l+2,bt,'[ ECHO / NO ACK ]' if t>=110.9 else '[ RESPONSE SENT ]',B)


def execution_memory(c,t,area):
    """Each EXECUTION destroys a different previously sung image on its onset."""
    l,top,r,bt=area;cx,cy=(l+r)//2,(top+bt)//2
    index=max(0,bisect.bisect_right(EXECUTIONS,t)-1)
    start=EXECUTIONS[index]
    end=EXECUTIONS[index+1] if index+1<len(EXECUTIONS) else 158.9
    age=t-start;u=clamp(age/(end-start))
    memories=(67.4,35.6,39.8,83.1,94.1,91.2,109.8,114.8)
    if index<8:
        original.draw_scene(c,memories[index]+min(age*.18,.12),top,bt,.6,None)
        source=[row[:] for row in c.cells]
        clear(c,l,top,r-l+1,bt-top+1)
        for yy in range(top,bt+1):
            for xx in range(l,r+1):
                ch,ink=source[yy][xx]
                if not ch.strip():continue
                # Retain the original drawings, then execute different destructive edits.
                if index%4==0:
                    px=xx+int((1 if yy%4<2 else -1)*u*u*(r-l)*.4);py=yy
                elif index%4==1:
                    dx,dy=xx-cx,(yy-cy)*2
                    a=math.atan2(dy,dx)+u*.8;rr=math.hypot(dx,dy)*(1+u)
                    px=cx+math.cos(a)*rr;py=cy+math.sin(a)*rr/2
                elif index%4==2:
                    px=xx;py=mix(yy,cy,u)
                else:
                    if hash16(xx*31+yy*71)/65535<u:continue
                    px=xx;py=yy+int(u*u*(bt-top)*.5)
                c.put(px,py,ch,R if u>.5 else ink)
    elif index==8:
        original.lyric_trapped_simulation(c,73.4+age*.2,area,.8)
    elif index==9:
        original.lyric_erase_fragments(c,119.2+u*1.6,area,1+u*1.6)
    else:
        original.lyric_execution_queue(c,147.66+u*15.5,area,u*15.5)
    if age<.2 or index==11:
        clear(c,l,cy-2,r-l+1,5)
        c.big(cy-2,'EXECUTION',W if age<.1 else R)
    label(c,l+1,top,f'EXECUTION {index+1:02d} / 12',W)
    labels=('HEART / SLICE','CIRCLE / RUPTURE','WAVE / FLATTEN','CAT / ERASE',
            'TIME / BREAK','SELF / DISASSEMBLE','HEARTBEAT / STOP','CONNECTION / DELETE',
            'SIMULATION / RECURSE','MEMORY / PURGE','WORLD / CLOSE','ME / EXECUTE')
    clear(c,l,bt,r-l+1,1);c.center(bt,labels[index],B)



# Three vowel attacks per LO-O-OVE. These are authored beat subdivisions of
# the source phrase cue, not additional Whisper/phoneme alignment results.
LOVE_PHRASES = ((179.929, 180.857), (183.646, 184.54),
                (187.665, 188.483), (191.356, 195.856))


def love_letters(c, t, area):
    phrase = next(((start, end) for start, end in LOVE_PHRASES if start <= t < end), None)
    if phrase is None:
        return
    from player import FONT
    start, end = phrase
    attacks = (start, start+.23, start+.46)
    count = bisect.bisect_right(attacks, t)
    text = 'L' + 'O'*count + ('VE' if count == 3 else '')
    l, top, r, bt = area
    cx, cy = (l+r)//2, (top+bt)//2
    # Accumulate vowels; each attack enlarges the lettering, with a brief pop.
    age = t-attacks[count-1]
    pop = math.sin(math.pi*clamp(age/.18))
    max_h = max(5, min(12, bt-top-3))
    height = min(max_h, 5+(count-1)*2+round(pop))
    width = min(r-l-4, round((len(text)*6-1)*height/5*1.5))
    x0, y0 = cx-width//2, cy-height//2
    clear(c,l+1,cy-max_h//2-1,r-l-1,max_h+2)
    # Resample the bitmap into terminal cells, preserving hollow, readable Os.
    columns = len(text)*6-1
    for yy in range(height):
        row = min(4, yy*5//height)
        for xx in range(width):
            source = min(columns-1, xx*columns//width)
            index, col = divmod(source, 6)
            if col < 5 and FONT[text[index]][row][col] == '1':
                c.put(x0+xx,y0+yy,'#',R)


def held_switch(c,t,area):
    """Route extended shots directly so their legacy end cannot cut them off."""
    dc, gender, daynight = switch_windows()
    clock = scripted_time(t)
    if dc[0] <= t < dc[1]:
        original.lyric_ac_dc(c,clock,area,clock-dc[0])
    elif gender[0] <= t < gender[1]:
        original.lyric_identity_rewrite(c,clock,area)
    elif gender[1] <= t < daynight[1]:
        original.lyric_daynight_clock(c,clock,area)
    elif daynight[1] <= t < when(99.349,'enter'):
        onset = when(97.739,'M')
        if t < onset:
            progress = .45*clamp((t-when(97.739,'S'))/max(.1,onset-when(97.739,'S')))
        else:
            progress = .5+.5*clamp((t-onset)/.35)
        original.lyric_gender_role_switch(c,t,area,progress*2.5,'S','M')
    else:
        return False
    return True


def draw_scene(c,t,top,bottom,pulse,lyric=None,response=0):
    area=original.simple_area(c,top,bottom)
    if held_switch(c,t,area):
        pass
    elif t<1.74:
        power(c,t,area)
    elif t<3.873:
        protection(c,t,area)
    elif 3.873<=t<7.446:
        assembly(c,t,area)
    elif 7.446<=t<11.095:
        parameters(c,t,area)
    elif 29.709<=t<33.412:
        dimension(c,t,area)
    elif 33.412<=t<37.067:
        circumference(c,t,area)
    elif 37.067<=t<40.706:
        tangents(c,t,area)
    elif 51.363<=t<when(55.083,'unite'):
        time_travel(c,t,area)
    elif 85.078<=t<88.587:
        god_proof(c,t,area)
    elif 177.246<=t<184.54:
        original.lyric_love_equation(c,t,area,t-177.246,stamp=False)
    elif 184.54<=t<188.483:
        algebra(c,t,area)
    elif 188.483<=t<195.856:
        freedom(c,t,area,pulse)
    elif t>=195.856:
        original.lyric_outro_wait(c,t,area,t-195.856)
    elif 110.9<=t<118.333:
        starts=(110.9,112.22,113.1,114.18,114.92,115.78)
        cuts=tuple(when(line,'left')-110.9 for line in starts)
        original.lyric_isolation_disconnect(c,t,area,t-110.9,departures=cuts)
    elif 147.66<=t<158.9:
        execution_memory(c,t,area)
    else:
        clock=scripted_time(t)
        original.draw_scene(c,clock,top,bottom,pulse,lyric)
    if 74.045<=t<85.078:organic_accents(c,t,area)
    original.phosphor(c,t,top,bottom)
    word_overlay(c,t,area,score().at(t),response)
    love_letters(c,t,area)
