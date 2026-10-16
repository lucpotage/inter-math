"""
The equalities with marks KaTeX sets (\\doteqdot \\fallingdotseq
\\risingdotseq \\eqcirc \\circeq \\triangleq \\bumpeq \\Bumpeq \\eqsim
\\backsim \\backsimeq \\approxeq \\between from its AMS font; \\asymp \\frown
\\smile \\propto from Main), drawn from Inter Math's = ∼ ≈ ⋅ ( )
(build/operators.py, build/geometry_glyphs.py, build/delimiters.py) and
Inter's ○ △ ( ∞, as heavy as ='s bars, = where = is (on the math axis):

- ≑ ≒ ≓: ≐'s dot (Inter Math's ⋅, its centre a pitch of ='s bars from the
  nearest bar's) above and below, or at the bars' ends, flush with them;
- the ring: Inter's ○, its two circles drawn apart so that the counter is
  as wide as ='s gap and the ring as tall as =: ≖ holds it between the bars
  (its counter fits the gap, its outer edge merges with the bars), ≗ sets
  it on =, ='s gap over it, ≏ ≎ take its upper (and lower) half as the
  bars' bumps, the bars broken under them;
- ≜: Inter's △ drawn around that ring (its counter holds the ring's), its
  base where the ring's foot is, as heavy as the bars: it grows with = as
  the ring does, and stays open at Black;
- ≂: ≃ upside down (the bar over ∼); ∽: ∼ mirrored; ⋍: ≃ with ∽; ≊: ≈
  over a bar, all three at ='s pitch (as ≅ is a tilde over two bars);
- ⌢ ⌣: Inter's ⁀ ‿ (its character tie and undertie, its own arcs: they
  thin to their ends as a slur does; its ( turned flat curves half as much
  as TeX's ⌢), as much wider than = as TeX's (FROWN), drawn at the weight
  that keeps the stroke Inter gives its ties (lighter than the operators'
  at Black: drawn as heavy, they flatten into dashes); ≍: ‿ over ⁀ as Inter
  draws them, ='s gap apart at their middles (squeezed to ='s width, they
  read as = at Black);
- ≬: Inter Math's ( and ) (build/delimiters.py) at the weight that gives
  them the operators' stroke (a relation's, not the delimiters' heavier
  one), past Regular as much lighter as Inter's rings (crowded, at the
  operators' stroke its crossings filled in from 600 up and it read as an
  ellipse), their curves drawn out sideways, their strokes kept
  (BETWEEN_WIDE: ≬ then as wide against its height as TeX's at the regular
  weight, its ends crossing steeper; the whole paren stretched, its stroke
  thickened past what Inter's Thin can lighten), drawn together until their
  inner edges meet BETWEEN of their height from their ends, where TeX's ≬
  closes (it opens over two thirds of its height);
- ∝: Inter's ∞ at the operators' stroke, its right loop cut open at its
  top and bottom, as TeX's ∝ is its ∞ opened.

\\varpropto \\smallfrown \\smallsmile are ∝ ⌢ ⌣ in KaTeX's AMS font, its own
designs: build/ams_variants.py draws them (a font of their own).
"""

import math

from delimiters import NORMAL, drawn
from geometry_glyphs import DOT, equalities, stacked
from operators import OFFSET, column, even_bars, gap, sign
from symbol_glyphs import ring_light
from variable import Masters, NewGlyph, Shape

CASED = ["minus", "plus", "equal", "approxequal", "parenleft", "parenright"]
SOURCES = [*CASED, *(f"{n}.case" for n in CASED), "periodcentered", "circlewhite", "uni25B3", "infinity", "uni203F", "uni2040", "one",
           "uni25EF"]
# ⌢ ⌣ against ='s width (TeX's: 889 against 666)
FROWN = 4 / 3
# ≬: where the inner edges of its ( and ) meet, a share of their height from their ends (TeX's)
BETWEEN = 0.156
# ≬: its ( and )'s curves drawn out sideways this much, so that it is as wide against its height as TeX's at the
# regular weight (351 to 1000; Inter's curves made it 268)
BETWEEN_WIDE = 1.68
# the ones KaTeX sets from its AMS font (≍ ⌢ ⌣ ∝ are Main's)
AMS = {0x2251, 0x2252, 0x2253, 0x2256, 0x2257, 0x225C, 0x224F, 0x224E, 0x2242, 0x223D, 0x22CD, 0x224A, 0x226C}
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x2251: ("= with ≐'s dot above and below", "equal periodcentered"),
    0x2252: ("= with ≐'s dots over its left end and under its right end", "equal periodcentered"),
    0x2253: ("= with ≐'s dots under its left end and over its right end", "equal periodcentered"),
    0x2256: ("○ between ='s bars, its counter the gap", "equal circlewhite"),
    0x2257: ("≖'s ring on =", "equal circlewhite"),
    0x225C: ("△ drawn around ≖'s ring, on =", "equal uni25B3"),
    0x224F: ("= with half of ≖'s ring as a bump", "equal circlewhite"),
    0x224E: ("= with halves of ≖'s ring as bumps", "equal circlewhite"),
    0x2242: ("≃ upside down", "approxequal equal"),
    0x223D: ("∼ mirrored", "approxequal"),
    0x22CD: ("≃ with ∽", "approxequal equal"),
    0x224A: ("≈ over a bar, at ='s pitch", "approxequal equal"),
    0x2322: ("Inter's character tie, wider", "uni2040"),
    0x2323: ("Inter's undertie, wider", "uni203F"),
    0x224D: ("‿ over ⁀, ='s gap apart", "uni203F uni2040"),
    0x226C: ("( and ), their curves drawn out sideways, their ends crossing, past Regular as light as ◯", "parenleft parenright uni25EF"),
    0x221D: ("∞, its right loop cut open", "infinity"),
}


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def rect(x0: float, y0: float, x1: float, y1: float) -> Shape:
    return Shape.polygon([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])


def extremes(contour: Shape) -> tuple[int, int, int, int]:
    """A circle's on-curve points at its left, right, bottom and top (their indices)."""
    on = [i for i in range(len(contour.points)) if contour.on[i]]
    x, y = (lambda i: contour.points[i][0]), (lambda i: contour.points[i][1])
    return min(on, key=x), max(on, key=x), min(on, key=y), max(on, key=y)


def run(contour: Shape, start: int, stop: int) -> tuple[list, list]:
    """A contour's points from `start` to `stop` (both kept), on in its own order."""
    n = len(contour.points)
    idx = [(start + k) % n for k in range((stop - start) % n + 1)]
    return [contour.points[i] for i in idx], [contour.on[i] for i in idx]


def ring(circle: Shape, centre: tuple[float, float], outer: float, inner: float, half: str = "") -> Shape:
    """
    Inter's ○ (`circle`: its outer and inner circles) drawn apart: radii
    `outer` and `inner`, about `centre`; with `half` ("upper", "lower") only
    that half, cut along its horizontal diameter (at the circles' on-curve
    extremes).
    """
    big, small = sorted(circle.contours(), key=lambda c: c.bounds()[2] - c.bounds()[0], reverse=True)

    def placed(c: Shape, r: float) -> Shape:
        x0, y0, x1, y1 = c.bounds()
        k = 2 * r / (x1 - x0)
        return c.map(lambda x, y: (centre[0] + (x - (x0 + x1) / 2) * k, centre[1] + (y - (y0 + y1) / 2) * k))

    big, small = placed(big, outer), placed(small, inner)
    if not half:
        return Shape.join([big, small], 0)
    # the outer circle runs clockwise, the inner one the other way: over the top, outer left → right, inner right → left
    bl, br, _, _ = extremes(big)
    sl, sr, _, _ = extremes(small)
    outer_run = run(big, bl, br) if half == "upper" else run(big, br, bl)
    inner_run = run(small, sr, sl) if half == "upper" else run(small, sl, sr)
    points, on = outer_run[0] + inner_run[0], outer_run[1] + inner_run[1]
    return Shape(points, on, [len(points) - 1], 0)


def triangle_around(tri: Shape, centre: tuple[float, float], radius: float, stroke: float) -> Shape:
    """
    Inter's △ (`tri`: its outer and inner triangles) drawn around a circle
    of `radius` about `centre`: its outer sides touching the circle, its
    base under it, its inner sides `stroke` in from the outer ones.
    """
    outer, _ = sorted(tri.contours(), key=height, reverse=True)
    (ax, ay), (bx, by), (cx, cy) = outer.points
    # the outer triangle's incircle: how much it must be scaled for its inradius to be `radius`
    a, b, c = math.dist((bx, by), (cx, cy)), math.dist((ax, ay), (cx, cy)), math.dist((ax, ay), (bx, by))
    s = (a + b + c) / 2
    area = abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2
    rho = area / s
    ix, iy = (a * ax + b * bx + c * cx) / (2 * s), (a * ay + b * by + c * cy) / (2 * s)

    def scaled(k: float, order: list[tuple[float, float]]) -> Shape:
        return Shape.polygon([(centre[0] + (x - ix) * k, centre[1] + (y - iy) * k) for x, y in order])

    # the outer triangle in Inter's order (clockwise), the inner one the other way, as Inter's inner contour runs
    return Shape.join([scaled(radius / rho, [(ax, ay), (bx, by), (cx, cy)]), scaled((radius - stroke) / rho, [(ax, ay), (cx, cy), (bx, by)])], 0)


def tie(m: Masters, master: dict, name: str, width: float) -> Shape:
    """Inter's ‿ or ⁀ (`name`), `width` wide, as thick in its middle as Inter's at the master (drawn at the weight that keeps it)."""
    own = m.shape(name, master)
    x0, _, x1, _ = own.bounds()

    def middle(s: Shape) -> float:
        sx0, _, sx1, _ = s.bounds()
        ys = column(s, (sx0 + sx1) / 2)
        return ys[1] - ys[0]

    return m.fitted(name, master, width / (x1 - x0), middle(own), middle)


def infinity_opened(m: Masters, master: dict, stroke: float) -> Shape:
    """
    Inter's ∞ at the weight whose loops are `stroke` thick at their sides,
    its right loop cut open along the vertical through its top and bottom
    (on-curve points of the outline and of the right counter there).
    """
    inf = m.fitted("infinity", master, 1, stroke)
    outer, *holes = sorted(inf.contours(), key=lambda c: len(c.points), reverse=True)
    left_hole, right_hole = sorted(holes, key=lambda c: c.bounds()[0])
    waist = (left_hole.bounds()[2] + right_hole.bounds()[0]) / 2
    right_on = [i for i in range(len(outer.points)) if outer.on[i] and outer.points[i][0] > waist]
    top = max(right_on, key=lambda i: outer.points[i][1])
    bottom = min(right_on, key=lambda i: outer.points[i][1])
    _, _, h_bottom, h_top = extremes(right_hole)
    # the outline (clockwise) from the right loop's bottom round the left loop to its top, then down the cut to the
    # counter's top, along the counter's left side (the crossing's inside) to its bottom, and down the cut again
    pts, on = run(outer, bottom, top)
    hpts, hon = run(right_hole, h_top, h_bottom)
    arms = Shape(pts + hpts, on + hon, [len(pts) + len(hpts) - 1], inf.advance)
    return Shape.join([arms, left_hole], inf.advance)


def equality_shapes(m: Masters, design: dict, master: dict, upem: int) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    space = gap(m, master)
    plus = even_bars(m, "plus", master)
    stem = max(plus.contours(), key=height).bounds()
    stem = stem[2] - stem[0]

    eq = even_bars(m, "equal", master)
    low, high = sorted(eq.contours(), key=lambda c: c.bounds()[1])
    x0, b0, x1, _ = low.bounds()
    _, t0, _, t1 = high.bounds()
    bar = t1 - t0
    centre = (x0 + x1) / 2
    pitch = t0 - b0
    whole = t1 - b0
    _, _, _, sim = equalities(m, master)

    def relation(parts: list[Shape]) -> Shape:
        return Shape.join(parts, 0).spaced(side)

    def at(shape: Shape, x: float, y: float) -> Shape:
        sx0, sy0, sx1, sy1 = shape.bounds()
        return shape.moved(x - (sx0 + sx1) / 2, y - (sy0 + sy1) / 2)

    # ≑ ≒ ≓: ≐'s dot, a pitch from the nearest bar
    dot = sign(m, "periodcentered", master, DOT)
    r_dot = (dot.bounds()[2] - dot.bounds()[0]) / 2
    above, below = (t0 + t1) / 2 + pitch, (b0 + low.bounds()[3]) / 2 - pitch
    shapes[0x2251] = relation([eq, at(dot, centre, above), at(dot, centre, below)])
    shapes[0x2252] = relation([eq, at(dot, x0 + r_dot, above), at(dot, x1 - r_dot, below)])
    shapes[0x2253] = relation([eq, at(dot, x0 + r_dot, below), at(dot, x1 - r_dot, above)])

    # the ring: its counter ='s gap, its outer edge as tall as =
    circle = m.shape("circlewhite", master)
    outer_r, inner_r = whole / 2, space / 2
    shapes[0x2256] = relation([eq, ring(circle, (centre, axis), outer_r, inner_r)])
    ring_centre = (centre, t1 + space + outer_r)
    shapes[0x2257] = relation([eq, ring(circle, ring_centre, outer_r, inner_r)])
    shapes[0x225C] = relation([eq, triangle_around(m.shape("uni25B3", master), ring_centre, outer_r, bar)])

    # ≏ ≎: the bars broken under half rings, centred on them
    def bumped(b: Shape, half: str) -> list[Shape]:
        _, y0, _, y1 = b.bounds()
        mid = (y0 + y1) / 2
        return [rect(x0, y0, centre - inner_r, y1), rect(centre + inner_r, y0, x1, y1), ring(circle, (centre, mid), outer_r, inner_r, half)]

    shapes[0x224F] = relation([low, *bumped(high, "upper")])
    shapes[0x224E] = relation([*bumped(low, "lower"), *bumped(high, "upper")])

    # ≂ ∽ ⋍ ≊: ∼ centred over the bars, ='s gap between a tilde and a bar ink to ink (as ≃), on the axis; ≊'s two
    # tildes as ≈ has them
    tilde = at(sim, centre, axis)
    backtilde = at(tilde.mirrored(), centre, axis)
    shapes[0x2242] = relation([stacked([tilde, low], space, axis, 0)])
    shapes[0x223D] = relation([backtilde])
    shapes[0x22CD] = relation([stacked([low, backtilde], space, axis, 0)])
    lower = stacked([low, tilde], space, axis, 0)
    shapes[0x224A] = relation([Shape.join([lower, max(lower.contours(), key=lambda c: c.bounds()[3]).moved(0, pitch)], 0).centred(axis)])

    # ⌢ ⌣ ≍: Inter's ties
    shapes[0x2322] = relation([at(tie(m, master, "uni2040", FROWN * (x1 - x0)), centre, axis)])
    shapes[0x2323] = relation([at(tie(m, master, "uni203F", FROWN * (x1 - x0)), centre, axis)])
    smile, frown = m.shape("uni203F", master), m.shape("uni2040", master)
    sh = height(smile)
    shapes[0x224D] = relation([at(smile, centre, axis + space / 2 + sh / 2), at(frown, centre, axis - space / 2 - sh / 2)])

    # ≬: ( and ), past Regular as light as Inter's rings, their curves drawn out sideways (BETWEEN_WIDE), their inner
    # edges meeting BETWEEN of their height from their ends (the lens twice the curve's run)
    def paren(name: str, cp: int, w: float) -> Shape:
        return drawn(m, name, cp, {**master, "wght": w}, NORMAL * upem, False)

    def wider(p: Shape) -> Shape:
        """Its curve drawn out sideways about its middle, its stroke kept: each point moved with its stroke's middle line."""
        _, py0, _, py1 = p.bounds()
        a, b = p.span((py0 + py1) / 2)

        def centre(y: float) -> float:
            r = max(p.runs(min(max(y, py0 + 0.5), py1 - 0.5)), key=lambda r: r[1] - r[0])
            return (r[0] + r[1]) / 2

        return p.map(lambda x, y: (x + (BETWEEN_WIDE - 1) * (centre(y) - (a + b) / 2), y))

    def thick(w: float) -> float:
        _, py0, _, py1 = (p := paren("parenleft", 0x28, w)).bounds()
        a, b = p.span((py0 + py1) / 2)
        return b - a

    w = m.weight_for(thick, stem * ring_light(m, master))
    left, right = wider(paren("parenleft", 0x28, w)), wider(paren("parenright", 0x29, w))
    _, ly0, _, ly1 = left.bounds()
    mid, meet = (ly0 + ly1) / 2, ly1 - BETWEEN * (ly1 - ly0)
    lens = 2 * (left.runs(meet)[-1][1] - left.runs(mid)[-1][1])
    right = right.moved(left.span(mid)[1] + lens - right.span(mid)[0], 0)
    shapes[0x226C] = relation([left, right])

    # ∝
    propto = infinity_opened(m, master, stem)
    shapes[0x221D] = relation([at(propto, centre, axis)])
    return shapes


def equality_glyphs(path, upem: int) -> list[NewGlyph]:
    m = Masters(path, SOURCES)
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in equality_shapes(m, design, m.lighter(design, OFFSET), upem).items():
            shapes.setdefault(cp, []).append(s)
    taken = set(m.font.getGlyphOrder())
    return [m.glyph(f"uni{cp:04X}" + (".math" if f"uni{cp:04X}" in taken else ""), s, cp) for cp, s in shapes.items()]
