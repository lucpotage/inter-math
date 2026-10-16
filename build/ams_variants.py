"""
The designs KaTeX's AMS font has at the code points it shares with Main
(\\varnothing \\hslash \\centerdot \\smallsetminus \\thicksim \\thickapprox
\\varpropto \\shortmid \\shortparallel \\vartriangle \\triangledown
\\smallfrown \\smallsmile: KaTeX sets them from its AMS font, at the code
points of Main's ∅ ℏ ⋅ ∖ ∼ ≈ ∝ ∣ ∥ △ ▽ ⌢ ⌣), with \\nshortmid \\nshortparallel
(its U+E006 U+E007) and \\Bbbk: a font of their own, InterMath-AMS, where
the "Inter Math AMS" face sends them (the upright font has Main's designs at
those code points: src/inter-math.css). \\vDash is the upright font's ⊨
(SHARED: TeX's is its ⊢ with two bars, as Inter Math's ⊨ is). With the
minus sign's side bearings unless said:

- ∅ (\\varnothing): Inter's own, a ring crossed (TeX's \\varnothing is round,
  its \\emptyset its 0 crossed, as Inter Math's is), as Inter draws and
  spaces it: about as large against the capitals as TeX's;
- ℏ (\\hslash): Inter's italic h with ł's stroke across its ascender, sloped
  as Inter's ₺ slopes its upper stroke (flatter at Black, where ₺'s strokes
  clear its bottom arm as this one clears the h's arch), its middle in the
  middle of the stem above the arch (TeX's \\hslash is its \\hbar with a slash
  for the bar); with h's spacing, as Inter Math's \\hbar is Inter's italic ħ;
- ⋅ (\\centerdot): Inter's ▪, CENTERDOT times as wide as Inter Math's ⋅
  (TeX's square against its round dot), on the axis, in ⋅'s advance (KaTeX's
  font has it on the baseline, its box up to 0.55 em: TeX centres it, as its
  name says);
- ∖ (\\smallsetminus): a stroke as thick across as Inter's \\, from the
  baseline to the x-height (TeX's), as wide against its height as TeX's
  (SMALLSETMINUS), its ends level as ╲'s are (build/misc_glyphs.py);
- ∼ ≈ (\\thicksim \\thickapprox): Inter Math's, their waves at the weight
  that makes them THICK times as heavy (TeX's), where Inter Math's are (past
  Black the weight is drawn on: a little less heavy there, the gap open);
- ∝ (\\varpropto): two of Inter's ○ as tall and heavy as Inter Math's ∝,
  side by side and crossing by a third of a stroke, the right one its left
  half only (TeX's \\varpropto is a ring and a C; its \\propto, Inter Math's,
  is ∞ opened);
- ∣ ∥ (\\shortmid \\shortparallel): Inter Math's cut to the baseline and the
  x-height (TeX's), with their spacing; \\nshortmid \\nshortparallel crossed
  as ∤ ∦ are (build/negated_glyphs.py), across the bars' middle;
- △ ▽ (\\vartriangle \\triangledown): Inter's △ in ▲'s box (TeX's are ▲ ▼
  white: build/misc_glyphs.py), as heavy as the small triangles ◃ ▹
  (build/binary_glyphs.py); ▽ the same turned;
- ⌢ ⌣ (\\smallfrown \\smallsmile): Inter Math's, as wide as = (TeX's), at
  the stroke Inter gives its ties (build/equality_glyphs.py);
- k (\\Bbbk): the blackboard k (build/blackboard.py), added by build.py.
"""

from equality_glyphs import infinity_opened, ring, tie, triangle_around
from geometry_glyphs import DOT, SOURCES as GEOMETRY_SOURCES, bars_to, subsets, vertical_bars
from misc_glyphs import SMALL_TRIANGLE, stroke_across
from negated_glyphs import stroked
from operators import OFFSET, column, even_bars, sign
from symbol_glyphs import ring_light
from variable import Masters, NewGlyph, Shape

SOURCES = list(dict.fromkeys([
    *GEOMETRY_SOURCES, "emptyset", "uni25AA", "circlewhite", "uni25EF", "infinity", "uni25B3", "uni203F", "uni2040",
    "slash", "x", "l", "lslash", "one", "uni20BA", "H",
]))
# TeX's: \\centerdot's square against \\cdot's dot (167 to 121 wide); \\smallsetminus's width against its height (595
# to 453); \\thicksim's and \\thickapprox's waves against \\sim's (75 to 56 thick)
CENTERDOT = 167 / 121
SMALLSETMINUS = 595 / 453
THICK = 4 / 3
# the AMS symbols whose design Inter Math's Main glyph already is (\\vDash: ⊢ with two bars, Inter Math's ⊨): the
# upright font's (build.py's AMS_DRAWN)
SHARED = {0x22A8}
# the code points InterMath-AMS holds (with \\Bbbk's k, from build/blackboard.py)
VARIANTS = {0x2205, 0x210F, 0x22C5, 0x2216, 0x223C, 0x2248, 0x221D, 0x2223, 0x2225, 0xE006, 0xE007, 0x25B3, 0x25BD, 0x2322, 0x2323}
# what each of InterMath-AMS's glyphs is drawn from (the workbench shows it): code point → (how, Inter's glyphs);
# build.py looks these up for that font (the same code points in the upright font are Main's designs)
DRAWN_FROM = {
    0x2205: ("Inter's own ∅, a ring crossed (\\varnothing)", "emptyset"),
    0x210F: ("Inter's italic h with ł's stroke across its ascender, sloped as ₺'s, across the middle of the stem above the arch (\\hslash)", "italic:h italic:lslash uni20BA"),
    0x22C5: ("Inter's ▪, larger than ⋅, on the axis (\\centerdot)", "uni25AA periodcentered"),
    0x2216: ("a stroke as thick as \\, from the baseline to the x-height (\\smallsetminus)", "backslash"),
    0x223C: ("∼, its wave heavier (\\thicksim)", "approxequal"),
    0x2248: ("≈, its waves heavier (\\thickapprox)", "approxequal"),
    0x221D: ("○ and its left half, side by side (\\varpropto)", "circlewhite"),
    0x2223: ("∣ from the baseline to the x-height (\\shortmid)", "bar"),
    0x2225: ("∥ from the baseline to the x-height (\\shortparallel)", "bar"),
    0xE006: ("the short ∣ crossed by ł's stroke (\\nshortmid)", "bar lslash"),
    0xE007: ("the short ∥ crossed by ł's stroke (\\nshortparallel)", "bar lslash"),
    0x25B3: ("△ in ▲'s box (\\vartriangle)", "uni25B3"),
    0x25BD: ("△ turned, in ▼'s box (\\triangledown)", "uni25B3"),
    0x2322: ("⌢, as wide as = (\\smallfrown)", "uni2040"),
    0x2323: ("⌣, as wide as = (\\smallsmile)", "uni203F"),
    0x006B: ("the blackboard k: K's hollow stem and leg on Inter's k (\\Bbbk)", "k"),
}


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def width(shape: Shape) -> float:
    x0, _, x1, _ = shape.bounds()
    return x1 - x0


def centre(shape: Shape) -> tuple[float, float]:
    x0, y0, x1, y1 = shape.bounds()
    return (x0 + x1) / 2, (y0 + y1) / 2


def lira_stroke(lira: Shape, cap: float) -> tuple[float, float]:
    """₺'s upper stroke (a four-point contour wider than tall): its slope, and how far under the cap height its top is."""
    strokes = [c for c in lira.contours() if len(c.points) == 4 and width(c) > height(c)]
    upper = max(strokes, key=lambda c: c.bounds()[3])
    left = sorted(upper.points)[:2]
    right = sorted(upper.points)[2:]
    (lx, ly), (rx, ry) = [(sum(x for x, _ in e) / 2, sum(y for _, y in e) / 2) for e in (left, right)]
    return (ry - ly) / (rx - lx), cap - upper.bounds()[3]


def sloped(stroke: Shape, slope: float, letter: Shape, top: float) -> Shape:
    """
    A four-point stroke (its ends two pairs of points) with its middle line at
    `slope`, its ends cut as they were, its top at `top`, across the stem of
    `letter` there.
    """
    pts = list(stroke.points)
    order = sorted(range(4), key=lambda i: pts[i][0])
    left, right = order[:2], order[2:]
    m0 = (sum(pts[i][0] for i in left) / 2, sum(pts[i][1] for i in left) / 2)
    m1 = (sum(pts[i][0] for i in right) / 2, sum(pts[i][1] for i in right) / 2)
    span = m1[0] - m0[0]
    rise = slope * span
    moved = [(m0[0] + x - m0[0], m0[1] + y - m0[1]) if i in left else (m0[0] + span + x - m1[0], m0[1] + rise + y - m1[1]) for i, (x, y) in enumerate(pts)]
    out = Shape(moved, list(stroke.on), list(stroke.ends), stroke.advance)
    _, _, _, y1 = out.bounds()
    out = out.moved(0, top - y1)
    cx, cy = centre(out)
    (a0, a1), *_ = letter.runs(cy)
    return out.moved((a0 + a1) / 2 - cx, 0)


def variant_shapes(m: Masters, mi: Masters, design: dict, italic: dict, master: dict, upem: int) -> dict[int, Shape]:
    """The family at a master (`italic`: the italic font's same master): code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    stem = width(max(even_bars(m, "plus", master).contours(), key=height))
    x_height = m.shape("x", design).bounds()[3]

    # ∅: Inter's own
    shapes[0x2205] = m.shape("emptyset", design)

    # ℏ: the italic h, ł's stroke across its ascender (its length, its thickness, its ends along the italic slant),
    # sloped as Inter's ₺ slopes its upper stroke at the weight (flatter at Black: ₺'s strokes flatten to clear its
    # bottom arm, as this one the h's arch), its middle in the middle of the stem above the arch (placed as ₺'s, as
    # far under the cap height, it crossed the stem's top at light weights)
    h = mi.shape("h", italic)
    letter, cross = sorted(mi.shape("lslash", italic).contours(), key=height, reverse=True)
    cap = m.shape("H", design).bounds()[3]
    slope, _ = lira_stroke(m.shape("uni20BA", design), cap)
    _, _, _, top = h.bounds()
    # where the arch leaves the stem: the lowest height above the x-height where the stem stands alone
    x_top = mi.shape("x", italic).bounds()[3]
    arch = next(y for y in range(int(x_top * 0.9), int(top)) if len(h.runs(y)) == 1)
    probe = sloped(cross, slope, h, top)
    shapes[0x210F] = Shape.join([h, sloped(cross, slope, h, (arch + top) / 2 + height(probe) / 2)], h.advance)

    # ⋅: Inter's ▪, larger than Inter Math's ⋅, on the axis, in ⋅'s advance
    dot = sign(m, "periodcentered", master, DOT)
    square = m.shape("uni25AA", master)
    square = square.scaled(CENTERDOT * width(dot) / width(square))
    (dx, _), (qx, qy) = centre(dot), centre(square)
    square = square.moved(dx - qx, axis - qy)
    square.advance = dot.advance
    shapes[0x22C5] = square

    # ∖: a backslash from the baseline to the x-height
    back = stroke_across(m, master, 0, x_height, SMALLSETMINUS * x_height)
    back.advance = width(back)
    shapes[0x2216] = back.mirrored().spaced(side)

    # ∼ ≈: their waves heavier, where Inter Math's are (≈: two waves at ='s pitch; ∼: ≈'s upper one, on the axis)
    def wave_at(wght: float) -> Shape:
        return max(sign(m, "approxequal", {**master, "wght": wght}).contours(), key=lambda c: c.bounds()[3])

    def thickness(wght: float) -> float:
        wave = wave_at(wght)
        ys = column(wave, centre(wave)[0])
        return ys[-1] - ys[0]

    heavy = wave_at(m.weight_for(thickness, THICK * thickness(master["wght"])))
    hx, hy = centre(heavy)

    def instead(c: Shape) -> Shape:
        x, y = centre(c)
        return heavy.moved(x - hx, y - hy)

    approx = even_bars(m, "approxequal", master)
    shapes[0x2248] = Shape.join([instead(c) for c in approx.contours()], approx.advance)
    sim = sign(m, "approxequal", master)
    tilde = max(sim.contours(), key=lambda c: c.bounds()[3]).centred(axis)
    shapes[0x223C] = Shape.join([instead(tilde)], sim.advance)

    # ∝: a ring and the left half of another, as tall and heavy as Inter Math's ∝, crossing by a third of a stroke
    d = height(infinity_opened(m, master, stem))
    circle = m.shape("circlewhite", master)
    r = d / 2
    second = (r + d - stem / 3, axis)
    shapes[0x221D] = Shape.join([ring(circle, (r, axis), r, r - stem), ring(circle, second, r, r - stem, "upper").turned(90, second)], 0).spaced(side)

    # ∣ ∥: Inter Math's, from the baseline to the x-height; crossed as ∤ ∦ are, at their middle
    bar, parallel = vertical_bars(m, design, master, upem)
    short_bar, short_parallel = bars_to(bar, 0, x_height), bars_to(parallel, 0, x_height)
    shapes[0x2223] = short_bar
    shapes[0x2225] = short_parallel
    shapes[0xE006] = stroked(m, master, short_bar, stem, x_height / 2).spaced(side)
    shapes[0xE007] = stroked(m, master, short_parallel, stem, x_height / 2).spaced(side)

    # △ ▽: Inter's △ in ▲'s box (build/misc_glyphs.py), as heavy as ◃ ▹
    _, subset, _ = subsets(m, master)
    tri = m.shape("uni25B3", master)
    unit = height(triangle_around(tri, (0, 0), 1000, 0))
    white = triangle_around(tri, (0, 0), 1000 * SMALL_TRIANGLE * height(subset) / unit, stem * ring_light(m, master))
    white = white.moved(0, -white.bounds()[1]).spaced(side)
    shapes[0x25B3] = white
    shapes[0x25BD] = white.rotated()

    # ⌢ ⌣: as wide as =, on the axis
    eq = even_bars(m, "equal", master)
    ex, _ = centre(eq)
    for cp, name in {0x2322: "uni2040", 0x2323: "uni203F"}.items():
        arc = tie(m, master, name, width(eq))
        ax, ay = centre(arc)
        shapes[cp] = arc.moved(ex - ax, axis - ay).spaced(side)
    return shapes


def variant_glyphs(path, italic_path, upem: int) -> list[NewGlyph]:
    m = Masters(path, [*SOURCES, *(f"{n}.case" for n in ("minus", "plus", "equal", "approxequal", "periodcentered"))])
    mi = Masters(italic_path, ["h", "lslash", "one", "x"])
    shapes: dict[int, list[Shape]] = {}
    for design, italic in zip(m.masters, mi.masters):
        for cp, s in variant_shapes(m, mi, design, italic, m.lighter(design, OFFSET), upem).items():
            shapes.setdefault(cp, []).append(s)
    return [m.glyph(f"uni{cp:04X}.ams", s, cp) for cp, s in shapes.items()]
