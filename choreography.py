"""ASCII cinematography for the original terminal/audio framework.

Every cue is anchored to lyrics.json. Geometry is deterministic at song time,
so seeking, snapshots and normal playback use the same composition.
"""
import bisect
import functools
import math

from scenes import hash16

TAU = math.tau
D, N, B, W, R, G, K = range(7)
CUES = (
    (0., 'seed', 'POWER LINE'), (2.92, 'shield', 'PROTECTION'),
    (3.873, 'cube', 'OBJECT CREATION'), (7.446, 'lattice', 'PARAMETERS'),
    (11.095, 'sphere', 'SIMULATION'), (16., 'title', 'WORLD.EXECUTE(ME);'),
    (29.709, 'lattice', 'DIMENSION'), (33.412, 'circle', 'CIRCUMFERENCE'),
    (37.067, 'wave', 'TANGENTS'), (40.706, 'infinity', 'LIMITATIONS'),
    (44.452, 'current', 'AC / DC'), (47.672, 'vortex', 'BLIND MY VISION'),
    (51.363, 'hourglass', 'A.D. / B.C.'), (55.083, 'helix', 'UNITE'),
    (59.223, 'neural', 'STIMULATIONS'), (62.589, 'heart', 'SATISFACTION'),
    (66.601, 'bloom', 'EXECUTION'), (70.084, 'cage', 'SIMULATION'),
    (74.045, 'eggplant', 'NUTRIENTS'), (77.576, 'tomato', 'ANTIOXIDANTS'),
    (81.351, 'cat', 'ENJOYMENT'), (85.078, 'solar', 'EXISTENCE'),
    (88.587, 'mirror', 'F / M'), (92.015, 'clock', 'AM / PM'),
    (95.465, 'helix', 'S / M'), (99.349, 'vortex', 'TRANCE'),
    (103.489, 'resonance', 'VIBRATIONS'), (110.9, 'isolation', 'ISOLATION'),
    (118.333, 'fragments', 'FRAGMENTS'), (125.708, 'error', 'ILLEGAL ARGUMENTS'),
    (147.66, 'execution', 'EXECUTION'), (158.9, 'count', 'EXECUTION'),
    (162.632, 'collapse', 'EXECUTION'), (173.643, 'cage', 'TRAPPED'),
    (177.246, 'heart', 'LO-O-OVE'), (180.857, 'formula', 'LO-O-OVE'),
    (184.54, 'infinity', 'LO-O-OVE'), (188.483, 'prison', 'TRAPPED IN LOVE'),
    (205.811, 'last', 'EXECUTION'), (208., 'seed', 'THE LOOP REMAINS'),
)
CUE_TIMES = tuple(c[0] for c in CUES)
EXECUTIONS = (147.66, 148.6, 149.52, 150.54, 151.52, 152.28,
              153.16, 153.98, 155.2, 156.08, 157.04, 158.)
COUNTS = ((158.9, 'EIN'), (159.321, 'DOS'), (159.657, 'TROIS'),
          (160.244, 'NE'), (160.693, 'FEM'), (161.124, 'LIU'))


def cue_at(t):
    return max(0, bisect.bisect_right(CUE_TIMES, t) - 1)


def clamp(v, a=0., b=1.):
    return min(b, max(a, v))


def palette(t):
    """ANSI 256-color light, no background flashes or non-ASCII art glyphs."""
    colors = (66, 109, 157, 230, 203, 60, 237)
    if 110.9 <= t < 125.708:
        colors = (60, 67, 110, 153, 203, 60, 237)
    elif 125.708 <= t < 177.246:
        colors = (95, 173, 209, 230, 203, 52, 235)
    elif t >= 177.246:
        colors = (66, 109, 151, 230, 203, 60, 235)
    return {i: f'\x1b[{1 if i in (B, W) else 0};38;5;{n}m'
            for i, n in enumerate(colors)}


@functools.lru_cache(maxsize=160)
def form(name, count):
    """Stable particle identities make one object change form all song long."""
    points = []
    for i in range(count):
        u = (i + .5) / count
        a = i * 2.399963229728653
        q, v = hash16(i * 7) / 65535, hash16(i * 13 + 9) / 65535
        s = hash16(i * 31 + 5) / 65535
        angle = q * TAU
        y = 1 - 2 * u
        rr = math.sqrt(max(0, 1 - y * y))
        x, z = rr * math.cos(a), rr * math.sin(a)
        if name == 'seed':
            x, y, z = x * .13, y * .13, z * .13
        elif name in ('cube', 'lattice', 'shield', 'error'):
            x, y, z = (q - .5) * 1.8, (v - .5) * 1.8, (s - .5) * 1.8
            face = i % 3
            if face == 0: x = .9 if i % 2 else -.9
            if face == 1: y = .9 if i % 2 else -.9
            if face == 2: z = .9 if i % 2 else -.9
            if name == 'lattice':
                x, y, z = (round(n * 4) / 4 for n in (x, y, z))
            if name == 'error':
                k = 1 + s ** 9 * 1.2
                x, y, z = x * k, y * k, z * k
        elif name in ('circle', 'isolation'):
            tube = .16 if name == 'circle' else .025
            x = (1 + tube * math.cos(a)) * math.cos(angle)
            y = (1 + tube * math.cos(a)) * math.sin(angle)
            z = tube * math.sin(a)
        elif name in ('infinity', 'formula'):
            den = 1 + math.cos(angle) ** 2
            x = 1.5 * math.sin(angle) / den
            y = 1.5 * math.sin(angle) * math.cos(angle) / den
            z = (v - .5) * .14
            x += math.cos(a) * .025
            y += math.sin(a) * .025
        elif name in ('wave', 'current', 'resonance'):
            x = (u - .5) * 3.6
            side = 1 if i % 2 else -1
            y = math.sin(x * (4 if name == 'current' else 2.8)) * .48
            if name == 'resonance': y = y * .6 + side * .32
            elif name == 'current' and i % 3 == 0: y = .45
            z = (q - .5) * .16
            y += (v - .5) * .03
        elif name == 'hourglass':
            y = (u - .5) * 2.2
            r = abs(y) * .85 + .035
            x, z = r * math.cos(a), r * math.sin(a)
        elif name == 'heart':
            k = .78 + v * .22
            x = 16 * math.sin(angle) ** 3 / 17 * k
            y = (13 * math.cos(angle) - 5 * math.cos(2 * angle)
                 - 2 * math.cos(3 * angle) - math.cos(4 * angle)) / 17 * k
            z = (s - .5) * .3
            y += .12
        elif name in ('helix', 'mirror'):
            angle = u * TAU * 3 + (math.pi if i % 2 else 0)
            x, y, z = .65 * math.cos(angle), (u - .5) * 2.3, .65 * math.sin(angle)
            if name == 'mirror':
                x = x * .5 + (.48 if i % 2 else -.48)
        elif name in ('cage', 'prison'):
            lane = i % 13
            x, z = .95 * math.cos(angle), .95 * math.sin(angle)
            y = (lane / 12 - .5) * 2.4
            if i % 4 == 0:
                angle = i % 24 / 24 * TAU
                x, z = .95 * math.cos(angle), .95 * math.sin(angle)
                y = (q - .5) * 2.4
        elif name == 'eggplant':
            y = (u - .5) * 2.1
            r = .58 * math.sin(math.pi * u) ** .7 * (1.4 - u)
            x, z = r * math.cos(a) + y * .15, r * math.sin(a)
        elif name == 'tomato':
            y *= .75
            ripple = 1 + .045 * math.cos(math.atan2(z, x) * 7)
            x, z = x * ripple, z * ripple
        elif name == 'cat':
            if q < .58:
                r = .5 * math.sqrt(v)
                x, y, z = r * math.cos(s * TAU), .25 + r * math.sin(s * TAU), 0
            elif q < .78:
                side = 1 if i % 2 else -1
                x = side * (.22 + v * .3)
                y = .55 + .44 * (1 - abs(v - .66) * 1.4) * s
                z = 0
            elif q < .94:
                r = math.sqrt(v)
                x, y, z = .42 * r * math.cos(s * TAU), -.45 + .43 * r * math.sin(s * TAU), 0
            else:
                x, y, z = .48 + .4 * math.sin(v * math.pi), -.6 + .4 * math.cos(v * math.pi), 0
        elif name in ('vortex', 'solar', 'bloom', 'clock', 'title'):
            radius = .4 + (i % 6) * .17
            tilt = (i % 6 - 2.5) * .23
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) * math.cos(tilt)
            z = radius * math.sin(angle) * math.sin(tilt)
        elif name == 'fragments':
            k = .6 + q * q * 2
            x, y, z = (round(n * k * 8) / 8 for n in (x, y, z))
        elif name == 'last':
            x, y, z = 0, (u - .5) * 2.2, 0
        points.append((x, y, z))
    return tuple(points)


class Stage:
    def __init__(self, canvas, t, top, bottom, pulse, response=0):
        self.c = canvas
        self.t = t
        self.top, self.bottom = top, bottom
        self.w, self.h = canvas.w, bottom - top + 1
        self.cx, self.cy = (canvas.w - 1) / 2, (top + bottom) / 2
        self.sx, self.sy = min(canvas.w * .28, self.h * 1.3), self.h * .34
        self.pulse, self.response = pulse, response
        self.zbuffer = {}
        self.flat = False
        self.turn = t * .19
        self.tilt = .23

    def project(self, p):
        x, y, z = p
        turn = math.sin(self.t * .2) * .12 if self.flat else self.turn
        cy, sy = math.cos(turn), math.sin(turn)
        x, z = x * cy + z * sy, -x * sy + z * cy
        cx, sx = math.cos(self.tilt), math.sin(self.tilt)
        y, z = y * cx - z * sx, y * sx + z * cx
        perspective = 4.6 / max(.5, 4.6 + z)
        return round(self.cx + x * self.sx * perspective), round(self.cy - y * self.sy * perspective), z

    def dot(self, p, ch=None, style=None):
        x, y, z = self.project(p)
        if not (2 <= x < self.w - 2 and self.top < y < self.bottom): return
        if z > self.zbuffer.get((x, y), 999): return
        self.zbuffer[x, y] = z
        lum = clamp((1.45 - z) / 2.8)
        if ch is None: ch = '.,:;+=*#@'[min(8, int(lum * 9))]
        if style is None: style = G if lum < .27 else D if lum < .43 else N if lum < .65 else B if lum < .88 else W
        self.c.put(x, y, ch, style)

    def line(self, p, q, ch='.', style=D):
        x, y, _ = self.project(p)
        xx, yy, _ = self.project(q)
        self.c.line(x, y, xx, yy, ch, style)

    def ring(self, radius=1., y=0., style=D, tilt=0., segments=100):
        for j in range(segments):
            a = j / segments * TAU
            self.dot((radius * math.cos(a), y + radius * math.sin(a) * math.sin(tilt),
                      radius * math.sin(a) * math.cos(tilt)), '.', style)

    def backdrop(self, intense=False):
        for i in range(min(100, self.w)):
            x = 2 + hash16(i * 73) % max(1, self.w - 4)
            y = self.top + 1 + hash16(i * 71) % max(1, self.h - 2)
            if hash16(i + int(self.t * 2)) % 7 == 0:
                self.c.put(x, y, '+' if i % 13 == 0 else '.', G)
        if intense:
            self.tunnel(.28, G)

    def tunnel(self, motion=1., style=D):
        # Perspective frames pass the viewer, always on the audio clock.
        for i in range(11):
            d = ((i / 11 + self.t * motion * .09) % 1.) ** 2
            rx, ry = self.w * .72 * d, self.h * .8 * d
            if rx < 3 or ry < 1: continue
            left, right = self.cx - rx, self.cx + rx
            top, bottom = self.cy - ry, self.cy + ry
            for x in range(max(2, int(left)), min(self.w - 2, int(right))):
                self.c.put(x, top, '-' if i % 2 else '.', style)
                self.c.put(x, bottom, '-' if i % 2 else '.', style)
            for y in range(max(self.top, int(top)), min(self.bottom + 1, int(bottom))):
                self.c.put(left, y, '|', style)
                self.c.put(right, y, '|', style)

    def object(self, name, previous=None, morph=1., scale=1.):
        count = min(4200, max(900, self.w * self.h))
        pts = form(name, count)
        old = form(previous, count) if previous and morph < 1 else pts
        m = morph * morph * (3 - 2 * morph)
        flat = ('circle', 'wave', 'current', 'infinity', 'formula', 'heart',
                'eggplant', 'tomato', 'cat', 'resonance', 'isolation', 'last')
        self.flat = name in flat
        self.tilt = .06 if self.flat else .23
        breath = scale * (1 + self.pulse * .08 + math.sin(self.t * 2) * .018)
        for i, (p, q) in enumerate(zip(old, pts)):
            x, y, z = ((a + (b - a) * m) * breath for a, b in zip(p, q))
            if name == 'vortex':
                turn = math.hypot(x, y) * .8 + self.t
                x, y = x * math.cos(turn) - y * math.sin(turn), x * math.sin(turn) + y * math.cos(turn)
            if name == 'fragments':
                k = clamp((self.t - 118.333) / 7.375)
                if hash16(i) / 65535 < k * .9: continue
                x *= 1 + k; y *= 1 + k
            if name == 'neural' and i % 120 == 0:
                self.line((x, y, z), (x * -.5, y * .5, z * -.5), '.', G)
            if name == 'cat':
                fur = clamp(.5 + .25 * math.sin(y * 32 + abs(x) * 9) + .2 * hash16(i) / 65535)
                ch = '.,:;+*#@'[min(7, int(fur * 8))]
                self.dot((x, y, z), ch, N if fur < .7 else B)
            else:
                self.dot((x, y, z))

    def core(self, absent=False):
        x = self.cx - self.sx * .55 if absent else self.cx
        self.c.put(round(x) - 1, round(self.cy), '(@)', W)
        if self.response > .05:
            r = (1 - self.response) * 1.4 + .2
            self.ring(r, style=B)

    def caption(self, text, lower=''):
        self.c.center(self.top, text, N)
        if lower: self.c.center(self.bottom, lower, D)


def draw_title(c, t, top, bottom, pulse):
    s = Stage(c, t, top, bottom, pulse)
    s.tunnel(1.5)
    s.object('title', scale=1.1)
    elapsed = t - 16
    if elapsed < 1.4:
        c.big(int(s.cy) - 2, 'WORLD', W)
    else:
        # A full terminal-width cut, with ordinary printable ASCII only.
        for y in range(int(s.cy) - 3, int(s.cy) + 4):
            c.put(2, y, ' ' * (c.w - 4), K)
        c.big(int(s.cy) - 2, 'EXECUTE(ME);', W)
    c.center(top + 1, 'W O R L D .', B)
    c.center(bottom - 1, 'TWO OBJECTS. ONE SIMULATION.', N)


def isolation(s, t):
    elapsed = t - 110.9
    cuts = (0, 1.32, 2.2, 3.28, 4.02, 4.88, 6.374)
    lost = bisect.bisect_right(cuts, elapsed)
    left, right = int(s.w * .27), int(s.w * .73)
    cy = int(s.cy)
    s.flat = True
    for j in range(140):
        a = j / 140 * TAU
        x = left + math.cos(a) * s.sx * .55
        y = cy + math.sin(a) * s.sy * .67
        s.c.put(x, y, '.:o'[j % 3], N if j % 3 else B)
    s.c.put(left - 1, cy, '(@)', W)
    s.c.put(right - 3, cy, '[   ]', G)
    s.c.put(left - 1, cy + int(s.sy * .8), 'ME', B)
    s.c.put(right - 5, cy + int(s.sy * .8), 'YOU / NULL', D)
    span = right - left - 5
    for i in range(max(0, span)):
        x = left + 3 + i
        y = cy + math.sin(i * .25 - t * 4) * (1.3 + s.pulse)
        if hash16(i * 37) % 9 >= lost:
            s.c.put(x, y, '~', N)
    # Sending a response now creates only a local echo, never reverses the lyric.
    if s.response > .1: s.c.center(s.bottom - 2, 'ECHO RECEIVED. CONNECTION NOT FOUND.', D)
    s.caption('YOU HAVE LEFT' + ' .' * min(lost, 6), 'SEND -> [             ] -> NO RESPONSE')


def execution(s, t):
    idx = max(0, bisect.bisect_right(EXECUTIONS, t) - 1)
    elapsed = t - EXECUTIONS[idx]
    flash = math.exp(-elapsed * 7)
    s.tunnel(1.6, G)
    cols, rows = (4, 3) if s.w >= 100 else (3, 4)
    cellw, cellh = (s.w - 8) / cols, max(2, (s.h - 4) / rows)
    for j in range(12):
        x = int(4 + j % cols * cellw)
        y = int(s.top + 2 + j // cols * cellh)
        ww, hh = max(5, int(cellw) - 3), max(3, int(cellh) - 1)
        if j < idx:
            s.c.put(x + ww // 2, y + hh // 2, '.', G)
            continue
        if j == idx:
            for k in range(28):
                angle = k / 28 * TAU
                radius = elapsed * 18
                s.c.put(x + ww / 2 + math.cos(angle) * radius,
                        y + hh / 2 + math.sin(angle) * radius * .4,
                        '/:;*'[k % 4], R if elapsed < .35 else G)
            continue
        s.c.box(x, y, ww, hh, D)
        s.c.put(x + 2, y, f' {j + 1:02d} ', N)
        for k in range(22):
            angle = k / 22 * TAU
            s.c.put(x + ww / 2 + math.cos(angle + t * .3) * ww * .25,
                    y + hh / 2 + math.sin(angle) * max(1, hh * .3), '.', N)
        s.c.put(x + ww // 2, y + hh // 2, '@', B)
        if ww > 15 and hh > 4: s.c.put(x + 2, y + hh - 2, 'you = null', G)
    if flash > .12:
        mid = int(s.cy) - 2
        for y in range(mid - 1, mid + 6): s.c.put(2, y, ' ' * (s.w - 4), K)
        s.c.big(mid, 'EXECUTION', W if flash > .5 else R)
    s.caption(f'EXECUTION {idx + 1:02d} / 12', f'{max(0, 11 - idx):02d} WORLDS REMAIN  /  YOU = NULL')


def prison(s, t):
    s.object('prison')
    # The same circle that offered its circumference now encloses its author.
    s.ring(.65, style=B)
    phase = (t - 188.483) * .8
    s.dot((.65 * math.cos(phase), 0, .65 * math.sin(phase)), '@', W)
    s.c.put(s.w - 18, int(s.cy), 'YOU -> FREE', B)
    s.caption('I AM TRAPPED', 'while (love) { me.wait(); }')


def draw_scene(c, t, top, bottom, pulse, lyric=None, response=0):
    """Compose a full ASCII stage, leaving subtitle and transport rows intact."""
    s = Stage(c, t, top, bottom, pulse, response)
    index = cue_at(t)
    start, name, word = CUES[index]
    previous = CUES[max(0, index - 1)][1]
    s.backdrop(name in ('error', 'collapse', 'vortex'))
    if name == 'title':
        draw_title(c, t, top, bottom, pulse)
        return
    if name == 'isolation':
        isolation(s, t)
        return
    if name == 'execution':
        execution(s, t)
        return
    if name == 'count':
        count = max((entry for entry in COUNTS if entry[0] <= t), default=COUNTS[0])
        s.tunnel(2)
        c.big(int(s.cy) - 2, count[1] if t < 161.584 else 'EXECUTION', W)
        s.caption('EIN / DOS / TROIS / NE / FEM / LIU', 'THE SAME COMMAND, IN EVERY LANGUAGE')
        return
    if name == 'prison':
        prison(s, t)
        return
    if name == 'collapse':
        k = clamp((t - 162.632) / (173.643 - 162.632))
        s.tunnel(2.2, R if pulse > .55 else D)
        s.object('heart', scale=1.3 - k)
        s.core()
        s.caption('IF I CAN HAVE YOU BACK', 'world.execute(me);')
        return
    if name == 'last':
        elapsed = t - start
        if elapsed < .6:
            c.big(int(s.cy) - 2, 'EXECUTION', W)
        else:
            c.put(s.cx, s.cy, '@' if elapsed < 1.2 else '.', B)
        s.caption('', 'world.execute(me);')
        return
    if t >= 208:
        s.core()
        s.caption('YOU ARE FREE. I AM TRAPPED.', 'while (love) { wait(); }')
        return
    s.object(name, previous, clamp((t - start) / .7))
    if name in ('cube', 'lattice', 'shield', 'error'):
        for axis in range(3):
            for a in (-.9, .9):
                for b in (-.9, .9):
                    p, q = [a, b], [a, b]
                    p.insert(axis, -.9); q.insert(axis, .9)
                    s.line(p, q, ':', G if name == 'error' else N)
    if name in ('sphere', 'solar', 'bloom', 'neural'):
        for i in range(3): s.ring(1.12 + i * .14, style=D, tilt=(i - 1) * .45)
    if name == 'wave':
        x = math.sin(t * .8) * .75
        y = math.sin(x * 2.8) * .48
        slope = math.cos(x * 2.8) * 1.344
        s.line((x - .55, y - slope * .55, -.1), (x + .55, y + slope * .55, -.1), '-', B)
        s.dot((x, y, -.11), '@', W)
    if name == 'cat':
        for sign in (-1, 1):
            s.dot((sign * .2, .33, -.05), '^', W)
            for j in range(3):
                s.line((sign * .22, .1, -.05), (sign * .8, .12 + (j - 1) * .12, -.05), '-', N)
    if name == 'eggplant':
        s.line((.12, .95, 0), (.3, 1.3, 0), '/', B)
    if name == 'tomato':
        for i in range(5):
            a = i / 5 * TAU
            s.line((0, .77, 0), (.35 * math.cos(a), .9, .35 * math.sin(a)), '*', B)
    if name == 'clock':
        a = t * 1.2
        s.line((0, 0, -.1), (.8 * math.cos(a), .8 * math.sin(a), -.1), '-', W)
        s.line((0, 0, -.1), (.45 * math.cos(a / 12), .45 * math.sin(a / 12), -.1), ':', B)
    if name == 'error':
        depth = 1 + int((t - start) * 1.7)
        for i in range(min(7, depth)):
            y = top + 2 + i * max(1, (s.h - 5) // 7)
            x = 3 if i % 2 else max(3, c.w - 27)
            c.put(x, y, ('  ' * (i % 3)) + 'love(you)', D)
        c.center(int(s.cy) - 1, '[ ILLEGAL ARGUMENTS ]', R)
        c.center(int(s.cy) + 1, 'expected: YOU  /  got: NULL', W)
    if name == 'formula':
        c.put(3, top + 3, 'd(love) / dt = ?', N)
        c.put(max(3, c.w - 24), bottom - 3, 'lim me -> you', B)
    if name not in ('error', 'fragments'):
        s.core()
    lower = {
        'seed': 'power.connect(me)', 'shield': 'protection.enable()',
        'cube': 'object.create(me, you)', 'lattice': 'me.dimension -> you',
        'sphere': 'world.add(me); world.add(you);', 'circle': 'C = 2*pi*r  ->  YOU',
        'wave': 'y = sin(x)  /  y\' = cos(x)', 'infinity': 'me -> infinity  /  you = my limit',
        'current': 'AC ~~~~~~  <->  DC ------', 'vortex': 'vision.clear() -> dizzy',
        'hourglass': 'A.D. <--------- 0 ---------> B.C.', 'helix': 'me.change(for=you)',
        'heart': 'if (you.happy) { me.give(all); }', 'neural': 'me.stimulations -> you',
        'bloom': 'if (you.happy) { me.execute(); }', 'cage': '[ me, you ] inside simulation',
        'eggplant': 'me.nutrients -> you', 'tomato': 'me.antioxidants -> you',
        'cat': 'me.purr(for=you)', 'solar': 'proof(me.exists) = you',
        'mirror': 'me.gender.switch(F, M)', 'clock': 'AM -------------> PM',
        'resonance': 'phase(me) = phase(you)', 'fragments': 'erase(memory); absence remains.',
        'error': 'love(you) -> INVALID ARGUMENT: absence', 'formula': 'EVERY ANSWER. NO YOU.',
    }.get(name, '')
    if name == 'helix' and t >= 95.465: lower = 'me.role.switch(S, M)'
    if name == 'heart' and t >= 177.246: lower = 'I HAVE STUDIED HOW TO LOVE.'
    s.caption(word, lower)
