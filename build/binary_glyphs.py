"""
The binary operators KaTeX sets from Main (\\triangleleft \\triangleright
\\diamond \\wr) and from its AMS font (\\lhd \\rhd \\unlhd \\unrhd, the same
glyphs as \\vartriangleleft … \\trianglerighteq; \\ltimes \\rtimes
\\leftthreetimes \\rightthreetimes; \\circledast \\circledcirc \\circleddash;
\\boxplus \\boxminus \\boxtimes \\boxdot; \\barwedge \\veebar \\doublebarwedge;
\\curlywedge \\curlyvee; \\divideontimes \\dotplus \\intercal), drawn from
Inter Math's operators and Inter's ▷ ◇ □ ○ (their negations ⋪ ⋫ ⋬ ⋭:
build/negated_glyphs.py), with the minus sign's side bearings unless said:

- ◃ ▹: ⋈'s triangles (Inter's ▷ at TeX's ▹ size, build/set_glyphs.py);
  ⊲ ⊳: ▷ as tall as ⊂ (TeX's are in <'s box); all as heavy as the
  operators and lighter past Regular, as the rings, so that they stay open
  (build/symbol_glyphs.py's ring_light); ⊴ ⊵: ≤ ≥'s chevron outlined as ▹
  is (its outer triangle, the corners mitered, as light), over ≤ ≥'s bar as
  much lighter: TeX's are in ≤ ≥'s box (≤ ≥'s chevron closed by an upright
  read as an angle and a bar at heavy weights; ◃ ▹ themselves over the bar
  stood narrow);
- ⋉ ⋊: in ×'s box, as TeX's are, a triangle outlined as ▹ is, its sides
  drawn on through the crossing in the same lines (⋈ with one triangle
  open), their ends cut square as Inter cuts ×'s (× closed by plus's bar
  clogged at heavy weights; ▹ itself drawn on stood too large);
  ⋈'s triangles likewise: their sides one line through the crossing
  (build/set_glyphs.py's crossed_triangles); ⋋ ⋌:
  ×'s strokes as a λ, one from the baseline to the cap height (TeX's sit
  there), the other from its middle down to the baseline, ends cut level;
- ⊛ ⊚ ⊝: ⊕'s ring (ring_for) around Inter Math's ∗, a smaller ring or a
  dash, as large against it as TeX's (ASTERISK, INNER, DASH), as heavy;
- ⊞ ⊟ ⊠ ⊡: Inter's □ (a cap-height square on the baseline, as TeX's
  boxes are) with +, −, × or ⋅ in it, the bars meeting the box, as heavy
  as it (the horizontal ones lighter by the operators' contrast);
- ⊼ ⊻ ⩞: ∧ ∨ shortened as ≤'s chevron is from < (as ⊆ is), with the minus
  sign's bar over (under) the point at ≤'s distance, ⩞ with a second one
  ='s gap over it; on the axis;
- ⋏ ⋎: the precedence relations' curved chevron (build/precedence_glyphs.py)
  turned up (down), in ∧'s box, as thick as ∧;
- ⋇: × with ÷ over it, as TeX's: ÷'s bar across the crossing, its dots
  where ÷ has them, or further out in the arms' V where they must be to
  keep ≤'s distance from the arms (as ⋖'s dot, build/order_glyphs.py: at
  Black the V is narrow); ∔: + with ⋅ over it at ≤'s distance;
- ⊺: ⊤'s bars from the descender to the x-height, its bar INTERCAL of ⊤'s
  (TeX's);
- ≀: the wide tilde's wave (Inter's ͠, as \\widetilde draws it) turned a quarter
  clockwise (TeX's ≀ is its ∼ turned, flatter), as long as ∼ is wide, grown
  until its stroke is ∼'s (an operator), on the axis: grown, not drawn
  heavier, so that it keeps ͠'s wave against its stroke at each weight;
- ⋄: Inter's ◇ DIAMOND times as tall as + (TeX's), its sides as heavy as
  the triangles'.
"""

import math

from equality_glyphs import ring
from geometry_glyphs import DOT, rect, subsets
from operators import OFFSET, case, even_bars, gap, sign, wave_stroke
from precedence_glyphs import chevron
from set_glyphs import BOWTIE, crossed_triangles, outlined, pointer
from symbol_glyphs import RING, ring_for, ring_light
from variable import Masters, NewGlyph, Shape

CASED = ["minus", "plus", "equal", "less", "lessequal", "greaterequal", "multiply", "divide", "approxequal", "asterisk"]
SOURCES = [*CASED, "uni03F5", "U", "Lambda", "periodcentered", "circlewhite", "uni25EF", "uni25B7", "uni25A1", "diamondwhite", "one", "x", "p",
           "uni0436", "uni0360"]
# TeX's: ⊛'s asterisk, ⊚'s inner ring and ⊝'s dash against the ring; ⊺'s bar against ⊤'s; ⋄ against +
ASTERISK = 430 / 664
INNER = 278 / 664
DASH = 332 / 664
INTERCAL = 443 / 668
DIAMOND = 480 / 666
# the ones KaTeX sets from Main (the rest come from its AMS font)
MAIN = {0x25C3, 0x25B9, 0x22C4, 0x2240}
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x25B9: ("▷, as ⋈'s", "uni25B7"),
    0x25C3: ("▷ mirrored, as ⋈'s", "uni25B7"),
    0x22B3: ("▷ as tall as ⊂", "uni25B7 uni03F5"),
    0x22B2: ("⊳ mirrored", "uni25B7 uni03F5"),
    0x22B5: ("≥'s chevron outlined as ▹ is, over ≥'s bar", "greaterequal uni25B7"),
    0x22B4: ("⊵ mirrored: ≤'s chevron outlined", "lessequal uni25B7"),
    0x22C9: ("▹'s outline in ×'s box, its sides drawn on through the crossing, as ⋈ with one triangle open", "uni25B7 multiply"),
    0x22CA: ("⋉ mirrored", "uni25B7"),
    0x22CB: ("×'s strokes as a λ, from the baseline to the cap height", "multiply"),
    0x22CC: ("⋋ mirrored", "multiply"),
    0x229B: ("⊕'s ring around the asterisk", "circlewhite asterisk"),
    0x229A: ("⊕'s ring around a smaller ring", "circlewhite"),
    0x229D: ("⊕'s ring around a dash", "circlewhite minus"),
    0x229E: ("□ with + in it", "uni25A1 plus"),
    0x229F: ("□ with − in it", "uni25A1 minus"),
    0x22A0: ("□ with × in it, corner to corner", "uni25A1 multiply"),
    0x22A1: ("□ with ⋅ in it", "uni25A1 periodcentered"),
    0x22BC: ("∧ shortened, under minus's bar", "Lambda minus"),
    0x22BB: ("∨ shortened, over minus's bar", "Lambda minus"),
    0x2A5E: ("∧ shortened, under two of minus's bars", "Lambda minus"),
    0x22CF: ("the curved chevron of ≺ turned up", "less circlewhite"),
    0x22CE: ("the curved chevron of ≺ turned down", "less circlewhite"),
    0x22C7: ("× with ÷ over it: its bar across the crossing, its dots", "multiply divide"),
    0x2214: ("+ with ⋅ over it", "plus periodcentered"),
    0x22BA: ("⊤'s bars, from the descender to the x-height", "minus plus"),
    0x2240: ("the wide tilde (Inter's ͠) turned a quarter, as long as ∼ is wide, grown to its stroke", "uni0360 approxequal"),
    0x22C4: ("◇, as heavy as the triangles", "diamondwhite"),
}


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def width(shape: Shape) -> float:
    x0, _, x1, _ = shape.bounds()
    return x1 - x0


def lambda_strokes(cap: float, thick: float) -> Shape:
    """⋋ at the origin: a stroke from the cap height down right to the baseline, another from its middle down left, `thick` across at 45°, cut level."""
    w = thick * math.sqrt(2)
    middle = w / 2 + cap / 2
    long = Shape.polygon([(0, cap), (w, cap), (cap + w, 0), (cap, 0)])
    short = Shape.polygon([(middle - w / 2, cap / 2), (middle + w / 2, cap / 2), (middle + w / 2 - cap / 2, 0), (middle - w / 2 - cap / 2, 0)])
    # both clockwise: the long one from its top left corner along the top, the short one the same
    return Shape.join([long, short], 0)


def diagonal(a: tuple[float, float], b: tuple[float, float], thick: float) -> Shape:
    """A stroke from a to b, `thick` across, its ends cut square."""
    (ax, ay), (bx, by) = a, b
    n = math.hypot(bx - ax, by - ay)
    nx, ny = -(by - ay) / n * thick / 2, (bx - ax) / n * thick / 2
    pts = [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)]
    # clockwise
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return Shape.polygon(pts if area < 0 else pts[::-1])


def triangles(m: Masters, master: dict) -> dict[int, Shape]:
    """▹ ◃ ⊳ ⊲ ⊵ ⊴ at a master (their negations cross them: build/negated_glyphs.py)."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    stem = width(max(even_bars(m, "plus", master).contours(), key=height))
    thin = stem * ring_light(m, master)
    _, subset, _ = subsets(m, master)
    bar, le = sorted(even_bars(m, "lessequal", master).contours(), key=lambda c: len(c.points))
    _, b0, _, b1 = bar.bounds()
    cx0, c0, _, c1 = le.bounds()

    def both(cp: int, s: Shape, mirror: int) -> None:
        shapes[cp], shapes[mirror] = s, s.mirrored()

    both(0x25B9, pointer(m, master, BOWTIE * height(subset), thin, axis).spaced(side), 0x25C3)
    both(0x22B3, pointer(m, master, height(subset), thin, axis).spaced(side), 0x22B2)
    # ⊵: ≥'s chevron outlined as ▹ is (its outer triangle, mitered, its sides `thin`, as lighter past Regular), over
    # ≥'s bar as much lighter: in ≥'s box, as TeX's is; ⊴ the mirror
    ge = even_bars(m, "greaterequal", master)
    ge_bar, arms = sorted(ge.contours(), key=lambda c: len(c.points))
    gx0, g0, gx1, g1 = arms.bounds()
    point = max(arms.points, key=lambda p: p[0])
    top, bottom = max(arms.points, key=lambda p: p[1]), min(arms.points, key=lambda p: p[1])

    def back(corner: tuple[float, float]) -> tuple[float, float]:
        """Where the arm's outer edge (from the point through its end's outer corner) meets the back, at gx0."""
        return gx0, point[1] + (corner[1] - point[1]) * (point[0] - gx0) / (point[0] - corner[0])

    _, gb0, _, gb1 = ge_bar.bounds()
    thick = (gb1 - gb0) * ring_light(m, master)
    triangle = outlined([back(top), point, back(bottom)], thin)
    both(0x22B5, Shape.join([triangle, rect(gx0, gb1 - thick, gx1, gb1)], ge.advance), 0x22B4)
    # ⋉: in ×'s box, as TeX's is, a triangle outlined as ▹ is from its left side, its sides drawn on through the
    # crossing (the same lines) to the right side, their ends cut square as Inter cuts ×'s; ⋊ the mirror
    times = sign(m, "multiply", master)
    both(0x22C9, crossed_triangles(times.bounds(), thin, closed=False).spaced(side), 0x22CA)
    return shapes


def binary_shapes(m: Masters, design: dict, master: dict) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis, rule = (my0 + my1) / 2, my1 - my0
    side = (mx0 + minus.advance - mx1) / 2
    plus = even_bars(m, "plus", master)
    stem = width(max(plus.contours(), key=height))
    light = ring_light(m, master)
    space = gap(m, master)
    cap = m.section("one", design["wght"], design["opsz"])[2]
    _, subset, _ = subsets(m, master)
    bar, le = sorted(even_bars(m, "lessequal", master).contours(), key=lambda c: len(c.points))
    _, b0, _, b1 = bar.bounds()
    cx0, c0, cx1, c1 = le.bounds()
    tight = c0 - b1

    def relation(parts: list[Shape]) -> Shape:
        return Shape.join(parts, 0).centred(axis).spaced(side)

    def both(cp: int, s: Shape, mirror: int) -> None:
        shapes[cp], shapes[mirror] = s, s.mirrored()

    # ◃ ▹ ⊲ ⊳ ⊴ ⊵: Inter's ▷, as heavy as the operators, lighter past Regular
    thin = stem * light
    shapes.update(triangles(m, master))

    # ⋋ ⋌: ×'s bars (as thick across as one of them is)
    times = sign(m, "multiply", master)
    tx0, ty0, tx1, ty1 = times.bounds()
    one = times.contours()[0]
    _, oy0, _, oy1 = one.bounds()
    (r0, r1), *_ = one.runs((oy0 + oy1) / 2)
    both(0x22CB, lambda_strokes(cap, (r1 - r0) / math.sqrt(2)).spaced(side), 0x22CC)

    # ⊛ ⊚ ⊝: ⊕'s ring
    _, p0, _, p1 = plus.bounds()
    ring_, (rx, ry), _ = ring_for(m, master, RING * (p1 - p0), thin, axis)
    across = height(ring_)
    star = m.shape(case(m, "asterisk"), master)
    star = m.fitted(case(m, "asterisk"), master, ASTERISK * across / height(star), thin, lambda s: s.side(0.9))
    sx0, sy0, sx1, sy1 = star.bounds()
    star = star.moved(rx - (sx0 + sx1) / 2, ry - (sy0 + sy1) / 2)
    small_ring = ring(m.shape("circlewhite", master), (rx, ry), INNER * across / 2, INNER * across / 2 - thin)
    dash = rect(rx - DASH * across / 2, ry - rule * light / 2, rx + DASH * across / 2, ry + rule * light / 2)
    for cp, inside in {0x229B: star, 0x229A: small_ring, 0x229D: dash}.items():
        shapes[cp] = Shape.join([ring_, inside], 0).spaced(side)

    # ⊞ ⊟ ⊠ ⊡: Inter's □ as it draws it, the signs as heavy, meeting it
    box = m.shape("uni25A1", design)
    hollow = min(box.contours(), key=width)
    ix0, iy0, ix1, iy1 = hollow.bounds()
    s = ix0 - box.bounds()[0]
    mid_x, mid_y = (ix0 + ix1) / 2, (iy0 + iy1) / 2
    flat = s * rule / stem
    across_box = rect(ix0 - s / 2, mid_y - flat / 2, ix1 + s / 2, mid_y + flat / 2)
    upward = rect(mid_x - s / 2, iy0 - s / 2, mid_x + s / 2, iy1 + s / 2)
    # the diagonals run on to the middle of the box's corners (s√2/2 past the inner ones), their square ends inside them
    reach = s / 2
    crosses = [diagonal((ix0 - reach, iy0 - reach), (ix1 + reach, iy1 + reach), s), diagonal((ix0 - reach, iy1 + reach), (ix1 + reach, iy0 - reach), s)]
    dot = sign(m, "periodcentered", master, DOT)
    dx0, dy0, dx1, dy1 = dot.bounds()
    dot = dot.moved(mid_x - (dx0 + dx1) / 2, mid_y - (dy0 + dy1) / 2)
    for cp, parts in {0x229E: [across_box, upward], 0x229F: [across_box], 0x22A0: crosses, 0x22A1: [dot]}.items():
        shapes[cp] = Shape.join([box, *parts], box.advance)

    # ⊼ ⊻ ⩞: ∧ (Λ at the operators' stroke across) shortened as ≤'s chevron is from <
    less = sign(m, "less", master)
    short = height(subset) * (c1 - c0) / height(less)
    wedge = m.fitted("Lambda", master, short / height(m.shape("Lambda", master)), stem, Shape.across)
    wx0, wy0, wx1, wy1 = wedge.bounds()
    first = rect(wx0, wy1 + tight, wx1, wy1 + tight + rule)
    second = first.moved(0, rule + space)
    shapes[0x22BC] = relation([wedge, first])
    shapes[0x2A5E] = relation([wedge, first, second])
    vee = wedge.rotated()
    shapes[0x22BB] = relation([vee, rect(wx0, wy0 - tight - rule, wx1, wy0 - tight)])

    # ⋏ ⋎: ≺'s curved chevron, turned up, in ∧'s box (Λ as tall as ⊂, as geometry_glyphs draws ∧)
    full = m.fitted("Lambda", master, height(subset) / height(m.shape("Lambda", master)), stem, Shape.across)
    fx0, fy0, fx1, fy1 = full.bounds()
    cusp = chevron((0, -(fx1 - fx0) / 2, fy1 - fy0, (fx1 - fx0) / 2), stem).turned(-90, (0, 0))
    shapes[0x22CF] = relation([cusp])
    shapes[0x22CE] = relation([cusp.rotated()])

    # ⋇: × with ÷ over it (TeX's: ÷'s bar across the crossing), its dots where ÷ has them, or further out in the V to
    # keep ≤'s distance from the arms' inner edges (at 45°, meeting a bar's run over two above and below the
    # crossing); ∔: + with ⋅ over it at ≤'s distance
    divide = even_bars(m, "divide", master)
    dots = [c for c in divide.contours() if width(c) < width(divide) / 2]
    divide_bar = max(divide.contours(), key=width)
    middle_x, middle_y = (tx0 + tx1) / 2, (ty0 + ty1) / 2
    placed = []
    for d in dots:
        dx0, dy0, dx1, dy1 = d.bounds()
        r, y = (dx1 - dx0) / 2, (dy0 + dy1) / 2
        out = max(abs(y - middle_y), (r1 - r0) / 2 + (tight + r) * math.sqrt(2))
        placed.append(d.moved(middle_x - (dx0 + dx1) / 2, middle_y + math.copysign(out, y - middle_y) - y))
    dbx0, dby0, dbx1, dby1 = divide_bar.bounds()
    across_ = divide_bar.moved(middle_x - (dbx0 + dbx1) / 2, middle_y - (dby0 + dby1) / 2)
    shapes[0x22C7] = Shape.join([times, across_, *placed], times.advance)
    px0, _, px1, py1 = plus.bounds()
    cdot = sign(m, "periodcentered", master, DOT)
    ex0, ey0, ex1, _ = cdot.bounds()
    shapes[0x2214] = Shape.join([plus, cdot.moved((px0 + px1 - ex0 - ex1) / 2, py1 + tight - ey0)], plus.advance)

    # ⊺: ⊤'s bars from the descender to the x-height
    x_height = m.shape("x", design).bounds()[3]
    descender = m.shape("p", design).bounds()[1]
    centre, half = (mx0 + mx1) / 2, INTERCAL * (mx1 - mx0) / 2
    shapes[0x22BA] = Shape.join([rect(centre - half, x_height - rule, centre + half, x_height), rect(centre - stem / 2, descender, centre + stem / 2, x_height)], 0).spaced(side)

    # ≀: \\widetilde's wave (Inter's ͠) turned a quarter clockwise, as long as ∼ is wide, and as heavy as ∼ (an operator:
    # the accent's stroke is lighter). ͠ at the weight, drawn out to that length, then grown about its middle until its
    # stroke across is ∼'s: grown, it keeps its wave against its stroke (2.6 at Thin, 0.95 at Regular, 0.6 at Black:
    # close to TeX's ≀ against its ∼, 0.6 of ∼'s); drawn heavier instead, its wave sank to a third of its stroke at
    # Black (a bar)
    approx = sign(m, "approxequal", master)
    tilde = max(approx.contours(), key=lambda c: c.bounds()[3])
    target = wave_stroke(approx)
    wave = m.shape("uni0360", master)
    wx0, wy0, wx1, wy1 = wave.bounds()
    middle = (wy0 + wy1) / 2
    wave = wave.map(lambda x, y: (wx0 + (x - wx0) * width(tilde) / (wx1 - wx0), y))
    grow = 1.0
    for _ in range(6):  # its stroke across grows a little slower than its height: its slopes steepen
        grow *= target / wave_stroke(wave.map(lambda x, y: (x, middle + (y - middle) * grow)))
    wave = wave.map(lambda x, y: (x, middle + (y - middle) * grow))
    shapes[0x2240] = wave.turned(-90).centred(axis).spaced(side)

    # ⋄: Inter's ◇ (its outer square) DIAMOND times as tall as +, its sides as heavy as the triangles'
    outer = max(m.shape("diamondwhite", master).contours(), key=width)
    qx0, qy0, qx1, qy1 = outer.bounds()
    k = DIAMOND * (p1 - p0) / (qy1 - qy0)
    qcx, qcy = (qx0 + qx1) / 2, (qy0 + qy1) / 2
    half = (qy1 - qy0) * k / 2
    inner = (half - thin * math.sqrt(2)) / half

    def scaled(f: float, points: list) -> Shape:
        return Shape.polygon([(qcx + (x - qcx) * k * f, qcy + (y - qcy) * k * f) for x, y in points])

    shapes[0x22C4] = Shape.join([scaled(1, outer.points), scaled(inner, outer.points[::-1])], 0).centred(axis).spaced(side)
    return shapes


def binary_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, [*SOURCES, *(f"{n}.case" for n in CASED)])
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in binary_shapes(m, design, m.lighter(design, OFFSET)).items():
            shapes.setdefault(cp, []).append(s)
    taken = set(m.font.getGlyphOrder())
    return [m.glyph(f"uni{cp:04X}" + (".math" if f"uni{cp:04X}" in taken else ""), s, cp) for cp, s in shapes.items()]
