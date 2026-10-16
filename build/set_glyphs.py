"""
The set symbols, turnstiles and joins KaTeX sets from its AMS font
(\\complement \\sqsubset \\sqsupset \\Subset \\Supset \\backepsilon
\\pitchfork \\Cup \\Cap \\Vdash \\Vvdash \\multimap) and from Main
(\\bowtie \\Join, and \\origof \\imageof, which its fonts lack), drawn from
Inter Math's ⊂ ∪ ∩ ⊢ ⊨ and minus sign (build/geometry_glyphs.py,
build/symbol_glyphs.py) and Inter's U ϶ ○ ▷, as heavy as the operators
and on the math axis unless said otherwise:

- ∁: Inter's U, its bowl below and turned above, joined along its left
  stem, its right stem cut level into stubs that leave OPENING of its
  height open between them: TeX's ∁ is ∪ over ∩, opened. It stands on the
  baseline, COMPLEMENT times the cap height tall, WIDE times as wide as
  tall at the regular weight (TeX's), wider with the weight as U grows,
  its stems as thick as plus's vertical bar (as ∪'s);
- ⊏ ⊐: ⊂ square, in ⊂'s box: plus's vertical bar and the minus sign's
  bars (as ⊑ ⊒ are, build/symbol_glyphs.py);
- ⋐ ⋑ ⋓ ⋒: ⊂ or ∪ with a smaller one inside, in its box (TeX's), the
  inner one's arms or stems ending where the outer one's do, the white
  across them shared as TeX's: each gap NESTED of it, the inner counter the
  rest (at ='s gap the inner sign closes: Inter's strokes take twice TeX's
  share of the box); past the regular weight both are lighter than the
  operators, as Inter's rings are (ring_light, build/symbol_glyphs.py), so
  that they stay open;
- ∍: Inter's ϶ on the baseline, as heavy as the letters: TeX's
  \\backepsilon is the letter, smaller than ∋;
- ⋔: ∩ with plus's vertical bar up its middle, from its feet to PITCHFORK
  of its height above it (TeX's);
- ⊩ ⊪: ⊢ with one or two more uprights before it, ='s gap apart (as ∥'s
  bars), its bar FORCES as long (TeX's); ⊫, which ⊯ crosses, is ⊨ drawn
  the same (build/negated_glyphs.py);
- ⊸: the minus sign's bar running into a ring, Inter's ○ drawn apart
  (build/equality_glyphs.py), MULTIMAP times as tall as = (TeX's), as
  thick as the bar; ⊷ ⊶: ⊸ with a disc (the ring's outer circle) at the
  bar's other end, ⊶ ⊷ mirrored (Unicode's: STIX's ⊶ has its ring left);
- ⋈: two of Inter's ▷ pointing at each other, their points crossing by a
  stroke, BOWTIE times as tall as ⊂ (TeX's ▹ ◃), as heavy as the
  operators and lighter past the regular weight, as the rings: smaller
  than Inter's ▷, its triangles would close at Black.
"""

import math

from equality_glyphs import ring, triangle_around
from geometry_glyphs import SOURCES as GEOMETRY_SOURCES, cups, rect, stems_to, subsets, turned_u
from operators import OFFSET, column, even_bars, gap, pipe_bars, sign
from symbol_glyphs import ring_light, turnstiles
from variable import Masters, NewGlyph, Shape

SOURCES = [*GEOMETRY_SOURCES, "circlewhite", "uni25EF", "uni25B7", "uni03F6", "pipedbl"]
# ∁ (TeX's): its height against the cap height, its width against its height, the opening between its stubs
COMPLEMENT = 825 / 683
WIDE = 388 / 867
OPENING = 0.35
# ⋐ ⋓: each gap between the outer and the inner sign, a share of the white across them (TeX's: 114 of 420, of 396)
NESTED = 0.28
# ⋔: how far its bar rises above ∩, a share of ∩'s height (TeX's: 138 of 620)
PITCHFORK = 138 / 620
# ⊩ ⊪: their bar against ⊢'s (TeX's: 417 to 500)
FORCES = 417 / 500
# ⊸: its ring against ='s height (TeX's: 316 to 234)
MULTIMAP = 316 / 234
# ⋈: its triangles' height against ⊂'s (TeX's ▹: 510 to 580)
BOWTIE = 510 / 580
# the ones KaTeX sets from its AMS font; those its fonts lack (\\origof \\imageof: Inter Math gives KaTeX their metrics)
AMS = {0x2201, 0x228F, 0x2290, 0x22D0, 0x22D1, 0x220D, 0x22D4, 0x22D3, 0x22D2, 0x22A9, 0x22AA, 0x22B8}
UNSET = {0x22B6, 0x22B7}
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x2201: ("U's bowl below and turned above, opened on the right", "U"),
    0x228F: ("plus's vertical bar and minus's bars in ⊂'s box", "plus minus"),
    0x2290: ("⊏ mirrored", "plus minus"),
    0x22D0: ("⊂ with a smaller ⊂ inside, its strokes no heavier than ǁ's bars", "U pipedbl"),
    0x22D1: ("⋐ mirrored", "U"),
    0x220D: ("the reversed lunate epsilon", "uni03F6"),
    0x22D4: ("∩ with plus's vertical bar up its middle", "U plus"),
    0x22D3: ("∪ with a smaller ∪ inside, its strokes no heavier than ǁ's bars", "U pipedbl"),
    0x22D2: ("⋓ turned", "U"),
    0x22A9: ("⊢ with another upright before it", "plus minus"),
    0x22AA: ("⊢ with two more uprights before it", "plus minus"),
    0x22B8: ("minus's bar into a ring of ○", "minus circlewhite"),
    0x22B7: ("⊸ with a disc of ○ at the bar's other end", "minus circlewhite"),
    0x22B6: ("⊷ mirrored", "minus circlewhite"),
    0x22C8: ("two ▷ pointing at each other", "uni25B7"),
}


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def width(shape: Shape) -> float:
    x0, _, x1, _ = shape.bounds()
    return x1 - x0


def u_fitted(m: Masters, master: dict, wide: float, stroke: float) -> Shape:
    """Inter's U, `wide` wide, its stems `stroke` thick (drawn at the weight that makes them so)."""
    k = wide / width(m.shape("U", master))
    for _ in range(3):  # the weight it is drawn at changes its width
        k *= wide / width(m.fitted("U", master, k, stroke))
    return m.fitted("U", master, k, stroke)


def complement(m: Masters, design: dict, master: dict, stroke: float) -> Shape:
    """
    ∁ at a master: Inter's U (its stems `stroke` thick), and the U turned,
    joined along their left stems into one outline, their right stems cut
    level, OPENING of its height apart.
    """
    cap = m.section("one", design["wght"], design["opsz"])[2]
    tall = COMPLEMENT * cap
    regular = {**design, "wght": m.axes["wght"].defaultValue}
    u = u_fitted(m, master, WIDE * tall * width(m.shape("U", design)) / width(m.shape("U", regular)), stroke)
    n = len(u.points)
    _, y0, _, y1 = u.bounds()
    # the stems' tops, in the outline's order: left outer, left inner, … right inner, right outer
    lo, li, ri, ro = sorted((i for i, (_, y) in enumerate(u.points) if abs(y - y1) < 0.5), key=lambda i: u.points[i][0])
    assert (li - lo) % n == 1 and (ro - ri) % n == 1, "U's stems end in two points each"
    low, high = tall * (1 - OPENING) / 2, tall * (1 + OPENING) / 2
    # the U turned, its flat top (where the U's baseline goes) at the full height
    above = list(u.rotated().moved(0, tall - (y0 + y1)).points)
    below = list(u.points)
    # its right stems cut level: the U's down to the opening, the turned one's up to it, both on their straight part
    for i in (ri, ro):
        below[i] = (below[i][0], low)
    for i in (lo, li):
        above[i] = (above[i][0], high)
    assert low > max(below[(ri - 1) % n][1], below[(ro + 1) % n][1]), "∁'s lower stub ends on the bowl"
    assert high < min(above[(li + 1) % n][1], above[(lo - 1) % n][1]), "∁'s upper stub ends on the bowl"

    def span(a: int, b: int) -> list[int]:
        return [(a + i) % n for i in range((b - a) % n + 1)]

    # clockwise: the lower stub's cut, the U's outer side up to its left stem, the turned U's outer side over to its
    # stub, that stub's cut, its inner side back to the left stem, the U's inner side round to the start
    order = (
        [("below", i) for i in [ri, *span(ro, lo)[:-1]]] + [("above", i) for i in span(ro, lo)[1:]]
        + [("above", i) for i in span(li, ri)[:-1]] + [("below", i) for i in span(li, ri)[1:-1]]
    )
    points = {"below": below, "above": above}
    return Shape([points[part][i] for part, i in order], [u.on[i] for _, i in order], [len(order) - 1], u.advance)


def squared(subset: Shape, stem: float, rule: float) -> Shape:
    """⊏ in ⊂'s box: plus's vertical bar (`stem` wide) and the minus sign's bars (`rule` thick)."""
    x0, y0, x1, y1 = subset.bounds()
    return Shape.join([rect(x0, y0, x0 + stem, y1), rect(x0, y1 - rule, x1, y1), rect(x0, y0, x1, y0 + rule)], subset.advance)


def nested_subset(m: Masters, master: dict, subset: Shape, stroke: float, arm_: float) -> Shape:
    """
    ⋐ at a master, in ⊂'s box (`subset`): ⊂ (Inter's U turned: turned_u) with
    a smaller one inside, as ⋓ is ∪ with a smaller ∪ in it, their sides
    `stroke` thick and their arms `arm_`, both running to ⊂'s end.
    """
    x0, y0, x1, y1 = subset.bounds()
    axis = (y0 + y1) / 2
    outer = turned_u(m, master, y1 - y0, x1 - x0, stroke, arm_)
    outer = outer.moved(x0 - outer.bounds()[0], 0).centred(axis)
    space = NESTED * (y1 - y0 - 4 * arm_)
    inner = turned_u(m, master, y1 - y0 - 2 * (arm_ + space), x1 - x0 - (stroke + space), stroke, arm_)
    inner = inner.moved(x0 + stroke + space - inner.bounds()[0], 0).centred(axis)
    return Shape.join([outer, inner], subset.advance)


def nested_cup(m: Masters, master: dict, cup: Shape, stroke: float) -> Shape:
    """⋓ at a master, in ∪'s box (`cup`): ∪ with a smaller one inside, its stems up to the outer one's tops, `stroke` thick."""
    x0, y0, x1, y1 = cup.bounds()
    outer = u_fitted(m, master, x1 - x0, stroke)
    outer = stems_to(outer, outer.bounds()[1] + y1 - y0)
    outer = outer.moved(x0 - outer.bounds()[0], y0 - outer.bounds()[1])
    middle = (x0 + x1) / 2
    ys = column(outer, middle)
    space = NESTED * (x1 - x0 - 4 * stroke)
    inner = u_fitted(m, master, x1 - x0 - 2 * (stroke + space), stroke)
    ix0, iy0, ix1, _ = inner.bounds()
    inner = stems_to(inner.moved(middle - (ix0 + ix1) / 2, ys[1] + space - iy0), y1)
    return Shape.join([outer, inner], cup.advance)


def forces(m: Masters, design: dict, master: dict) -> tuple[Shape, Shape, Shape]:
    """⊩ ⊪ ⊫ at a master: ⊢ (⊫: ⊨) with one or two more uprights before it, ='s gap apart, its bars FORCES as long."""
    minus = sign(m, "minus", master)
    mx0, _, mx1, _ = minus.bounds()
    side = (mx0 + minus.advance - mx1) / 2
    tack, models = turnstiles(m, design, master)
    upright = max(tack.contours(), key=height)
    pitch = width(upright) + gap(m, master)
    end = mx0 + FORCES * (mx1 - mx0)

    def after(base: Shape, count: int) -> Shape:
        return Shape.join([upright.moved(i * pitch, 0) for i in range(count)] + [base.bars_to(mx0, end).moved(count * pitch, 0)], 0).spaced(side)

    return after(tack, 1), after(tack, 2), after(models, 1)


def ringed(m: Masters, master: dict) -> tuple[Shape, Shape]:
    """⊸ and ⊷ at a master: the minus sign's bar into a ring, and with a disc at its other end."""
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis, rule = (my0 + my1) / 2, my1 - my0
    side = (mx0 + minus.advance - mx1) / 2
    radius = MULTIMAP * height(even_bars(m, "equal", master)) / 2
    circle = m.shape("circlewhite", master)
    # the bar runs half a stroke into the ring (and the disc): its corners inside the ring's stroke
    ring_ = ring(circle, (mx1 + radius, axis), radius, radius - rule)
    disc = ring(circle, (mx0 - radius, axis), radius, radius - rule).contours()[0]
    multimap = Shape.join([rect(mx0, axis - rule / 2, mx1 + rule / 2, axis + rule / 2), ring_], 0).spaced(side)
    image = Shape.join([disc, rect(mx0 - rule / 2, axis - rule / 2, mx1 + rule / 2, axis + rule / 2), ring_], 0).spaced(side)
    return multimap, image


def pointer(m: Masters, master: dict, tall: float, stroke: float, axis: float) -> Shape:
    """Inter's ▷ (its outer triangle) `tall` tall, centred on `axis`, its sides `stroke` thick (the inner triangle drawn in from them)."""
    tri = m.shape("uni25B7", master)
    # triangle_around draws it around a circle: the circle that makes it as tall
    unit = height(triangle_around(tri, (0, 0), 1000, 0))
    return triangle_around(tri, (0, axis), 1000 * tall / unit, stroke)


def outlined(corners: list[tuple[float, float]], stroke: float) -> Shape:
    """
    A triangle's outline, its sides `stroke` thick and its corners mitered,
    as Inter draws ▷: the outer triangle and the inner one, its sides
    `stroke` in (the outer one scaled about its incentre).
    """
    a, b, c = corners
    la, lb, lc = math.dist(b, c), math.dist(a, c), math.dist(a, b)
    s = (la + lb + lc) / 2
    area = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2
    r = area / s
    ix, iy = (la * a[0] + lb * b[0] + lc * c[0]) / (2 * s), (la * a[1] + lb * b[1] + lc * c[1]) / (2 * s)
    outer = Shape.polygon(corners)
    # clockwise outside, the other way inside (as Inter's contours run)
    if sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(corners, corners[1:] + corners[:1])) > 0:
        outer = Shape.polygon(corners[::-1])
    k = (r - stroke) / r
    inner = Shape.polygon([(ix + (x - ix) * k, iy + (y - iy) * k) for x, y in reversed(outer.points)])
    return Shape.join([outer, inner], 0)


def crossed_triangles(box: tuple[float, float, float, float], stroke: float, closed: bool) -> Shape:
    """
    ⋈ (`closed`) or ⋉ in a box: a triangle pointing right from the box's left
    side (its outer corners the box's left ones), its sides `stroke` thick
    and their middle lines crossing in the box's middle; then the same sides
    drawn on through the crossing (in the same line, its turn about it): the
    other triangle, or (⋉) only its sides, their ends cut square as Inter
    cuts ×'s.
    """
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = x1 - x0, y1 - y0
    # the sides' slope: the outer edge, half a stroke off the middle line through the crossing, passes the corner
    phi = math.atan2(w / 2, h / 2)
    theta = math.acos(stroke / 2 / math.hypot(w / 2, h / 2)) - phi
    tip = (x0 + (y1 - cy) / math.sin(theta) * math.cos(theta), cy)
    left = outlined([(x0, y1), tip, (x0, y0)], stroke)
    if closed:
        return Shape.join([left, left.map(lambda x, y: (2 * cx - x, 2 * cy - y))], 0)
    # the sides' middle lines, from the crossing to the far side's middle line (its turn of the back side's)
    reach = (cx - x0 - stroke / 2) / math.cos(theta)
    ends = [(cx + reach * math.cos(theta), cy + way * reach * math.sin(theta)) for way in (1, -1)]
    return Shape.join([left, *(diagonal((cx, cy), end, stroke) for end in ends)], 0)


def diagonal(a: tuple[float, float], b: tuple[float, float], thick: float) -> Shape:
    """A straight stroke from a to b, `thick` across, its ends cut square."""
    (ax, ay), (bx, by) = a, b
    n = math.hypot(bx - ax, by - ay)
    nx, ny = -(by - ay) / n * thick / 2, (bx - ax) / n * thick / 2
    pts = [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)]
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return Shape.polygon(pts if area < 0 else pts[::-1])


def bowtie(m: Masters, master: dict, subset: Shape, stroke: float) -> Shape:
    """
    ⋈ at a master: two of Inter's ▷ (`stroke` thick), BOWTIE times as tall as
    ⊂, as wide as two of them, pointing at each other, their sides in the
    same line through the crossing (set apart by a stroke, they broke there).
    """
    x0, y0, x1, y1 = subset.bounds()
    point = pointer(m, master, BOWTIE * (y1 - y0), stroke, (y0 + y1) / 2)
    px0, py0, px1, py1 = point.bounds()
    return crossed_triangles((0, py0, 2 * (px1 - px0) - stroke, py1), stroke, closed=True)


def set_shapes(m: Masters, design: dict, master: dict) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    rule = my1 - my0
    side = (mx0 + minus.advance - mx1) / 2
    vertical = max(sign(m, "plus", master).contours(), key=height)
    stem = width(vertical)
    light = ring_light(m, master)
    _, subset, _ = subsets(m, master)
    cup, cap = cups(m, master)

    shapes[0x2201] = complement(m, design, master, stem)
    shapes[0x228F] = squared(subset, stem, rule)
    shapes[0x2290] = shapes[0x228F].mirrored()
    # nested signs: two strokes side by side, no heavier than Inter's ǁ's bars (they keep their white open)
    pipe, _ = pipe_bars(m, master)
    nested = min(subset.side() * light, pipe)
    # its arms lighter by ⊂'s contrast (minus's bar to plus's vertical bar)
    shapes[0x22D0] = nested_subset(m, master, subset, nested, nested * rule / stem)
    shapes[0x22D1] = shapes[0x22D0].mirrored()
    shapes[0x220D] = m.shape("uni03F6", design).spaced(side)
    cx0, cy0, cx1, cy1 = cap.bounds()
    middle = (cx0 + cx1) / 2
    shapes[0x22D4] = Shape.join([cap, rect(middle - stem / 2, cy0, middle + stem / 2, cy1 + PITCHFORK * (cy1 - cy0))], cap.advance)
    shapes[0x22D3] = nested_cup(m, master, cup, min(stem * light, pipe))
    shapes[0x22D2] = shapes[0x22D3].rotated()
    shapes[0x22A9], shapes[0x22AA], _ = forces(m, design, master)
    shapes[0x22B8], shapes[0x22B7] = ringed(m, master)
    shapes[0x22B6] = shapes[0x22B7].mirrored()
    shapes[0x22C8] = bowtie(m, master, subset, stem * light).spaced(side)
    return shapes


def set_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, SOURCES)
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in set_shapes(m, design, m.lighter(design, OFFSET)).items():
            shapes.setdefault(cp, []).append(s)
    taken = set(m.font.getGlyphOrder())
    return [m.glyph(f"uni{cp:04X}" + (".math" if f"uni{cp:04X}" in taken else ""), s, cp) for cp, s in shapes.items()]
