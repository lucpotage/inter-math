"""
Geometry and set symbols Inter lacks, drawn from Inter's own glyphs.

- ∈ ∋ ⊂ ⊃: the bowl of Inter's lunate epsilon (ϵ), its straight arms drawn
  out to the width of Inter's relations (<), its bar (∈) run to their ends,
  both as much larger than Inter's as the relations (RELATION_SCALE,
  build/operators.py);
- ⊆ ⊇: as Inter draws ≤ from <: a shorter ⊂ (taken at a heavier weight so its
  stroke doesn't thin, arms drawn out again) over the bar of ≤, as far below
  its lower arm as ='s bars are apart (build/operators.py: parallel strokes
  are; ≤'s own bar is closer, a point over a bar);
- ∪ ∩: Inter's U at the width of ⊂, its stems shortened to ⊂'s height: the
  box of ⊂, the size of Inter's u (a turned ⊂ would put Inter's thick
  verticals on the bowl and its thin horizontals on the stems), its stems as
  thick as plus's vertical bar (a letter's stems are heavier);
- ∉: ∈ crossed by the slash of Inter's ≠, drawn out along its slant to pass
  it as far as ≠'s passes its bars (slash());
- ⊥ ∠: bars as thick as Inter's minus and plus, the angle's diagonal as thick
  across as plus's vertical bar and its point cut flat, like the point of <;
- ∘ ⋅ ∙: Inter's degree sign, middle dot and bullet, on the math axis, as
  much larger as the relations (the dot less, DOT: TeX's is a period's size);
- | ∣ ∥: Inter's | and ‖ cut to the height of Inter Math's parentheses
  (build/delimiters.py; Inter's bars are taller; TeX's match the parentheses,
  and (AB) ∥ (CD) reads better), as thick as plus's vertical bar (Inter's
  grow heavier than it towards Black); ∥ two of them as far apart as ='s bars
  (Inter's ‖ is tighter).

- the slash of \\not (KaTeX sets ≠ as \\not=, ∉ the same way in Computer
  Modern): the one of Inter's ≠, on no advance, over the next relation;
- logic: ∀ ∃ are Inter's A turned and E mirrored, their stems as thick as
  plus's vertical bar (TeX draws them as its other symbols, not as letters);
  ∇ is Inter's Δ turned, at the letters' weight (TeX's is heavy too); ∄ is ∃
  crossed by ≠'s slash, drawn out along its slant to pass it as ≠'s passes
  its bars; ∧ ∨ are
  Inter's Λ in ⊂'s box and turned (the pair of ∪ ∩); ∓ is ± turned;
- ≡ ≅ ≃ ∼: ='s bars and the upper tilde of ≈, at ='s pitch: ≡ three bars,
  ≅ ≃ the tilde over two bars or one, ∼ the tilde alone (as in ≈).

Relations get the minus sign's side bearings. Everything is drawn as light,
and centred as high, as the operators (build/operators.py: Inter's case forms,
centred on the digits), at each of Inter's masters (build/variable.py), so it
follows the weight and optical size.
"""

import math

from delimiters import NORMAL
from operators import OFFSET, RELATION_SCALE, SCALE, axis_drop, case, column, even_bars, gap, sign
from variable import Masters, NewGlyph, Shape

# the operators and brackets these follow come in their case forms (see build/operators.py)
CASED = ["notequal", "lessequal", "less", "minus", "plus", "parenleft", "plusminus", "equal", "approxequal"]
SOURCES = [
    "uni03F5", "U", "degree", "periodcentered", "bullet", "bar", "verticalbardbl", "one",
    "A", "E", "uni0394", "Lambda",
    *CASED, *(f"{n}.case" for n in CASED),
]
# dots grow less than the signs (TeX's · is as large as a period)
DOT = SCALE ** 0.5
# ∣ (\mid) is the math | : code point → the glyph drawn for another
ALIASES = {0x2223: "bar.math"}
# what each is drawn from (the workbench shows it, /dev/symbols): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x2208: ("⊂ with minus's bar across it, from inside its side to its arms' ends", "U minus"),
    0x220B: ("∈ mirrored", "U minus"),
    0x2209: ("∈ crossed by ≠'s slash", "U notequal"),
    0x220C: ("∋ crossed by ∉'s slash", "U notequal"),
    0x2282: ("Inter's U turned, as tall as ϵ and as wide as < (its side plus's vertical bar, its arms minus's bar)", "U uni03F5 less"),
    0x2283: ("⊂ mirrored", "U"),
    0x2286: ("⊂ shortened as ≤ shortens <, over minus's bar ='s gap under it", "U lessequal"),
    0x2287: ("⊆ mirrored", "U lessequal"),
    0x222A: ("U in ⊂'s box", "U"),
    0x2229: ("∪ turned", "U"),
    0x22A5: ("plus's vertical bar on minus's bar", "plus minus"),
    0x2220: ("minus's bar and a diagonal, its point cut as <'s", "minus less"),
    0x2218: ("the degree sign on the axis", "degree"),
    0x22C5: ("the middle dot on the axis", "periodcentered"),
    0x2219: ("the bullet on the axis", "bullet"),
    0xE020: ("≠'s slash (\\not)", "notequal"),
    0x2200: ("A turned", "A"),
    0x2203: ("E mirrored", "E"),
    0x2204: ("∃ crossed by ≠'s slash", "E notequal"),
    0x2207: ("Δ turned", "uni0394"),
    0x2227: ("Λ in ⊂'s box", "Lambda"),
    0x2228: ("∧ turned", "Lambda"),
    0x2213: ("± turned", "plusminus"),
    0x2261: ("three of ='s bars", "equal"),
    0x2245: ("≈'s upper tilde over ='s bars, ='s gap between", "approxequal equal"),
    0x2243: ("≈'s upper tilde over a bar, ='s gap between", "approxequal equal"),
    0x223C: ("≈'s upper tilde", "approxequal"),
    0x007C: ("cut to the parentheses' height", "bar"),
    0x2223: ("| (\\mid)", "bar"),
    0x2225: ("two |, as far apart as ='s bars", "bar"),
}


def stems_to(shape: Shape, y: float) -> Shape:
    """A U with its stems cut down to y (their tops are its highest points)."""
    y1 = shape.bounds()[3]
    return shape.map(lambda px, py: (px, y if abs(py - y1) < 0.5 else py))


def bars_to(shape: Shape, bottom: float, top: float) -> Shape:
    """Vertical bars cut to a bottom and a top (their ends are its lowest and highest points)."""
    _, y0, _, y1 = shape.bounds()
    return shape.map(lambda px, py: (px, bottom if abs(py - y0) < 0.5 else top if abs(py - y1) < 0.5 else py))


def rect(x0: float, y0: float, x1: float, y1: float) -> Shape:
    return Shape.polygon([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])


def slash(m: Masters, master: dict) -> tuple[Shape, float]:
    """
    ≠'s slash at a master, and how far it passes ='s bars (Inter Math's =, the
    one it crosses for KaTeX): every slash of a negation passes what it crosses
    as far (a shorter one, ending where the relation does, is missed at a
    glance; TeX's pass theirs by a quarter of the cap height).
    """
    ne = sign(m, "notequal", master)
    s = max(ne.contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
    _, e0, _, e1 = even_bars(m, "equal", master).bounds()
    _, s0, _, s1 = s.bounds()
    return s, ((s1 - s0) - (e1 - e0)) / 2


def drawn_slash(slash: Shape, height: float) -> Shape:
    """≠'s slash drawn out (or cut) along its slant to `height`, about its middle, its ends still cut level."""
    ys = sorted({y for _, y in slash.points})
    low_y, high_y = ys[0], ys[-1]
    mid = lambda y: sum(x for x, py in slash.points if py == y) / sum(1 for _, py in slash.points if py == y)  # noqa: E731
    lean = (mid(high_y) - mid(low_y)) / (high_y - low_y)
    reach = (height - (high_y - low_y)) / 2
    return slash.map(lambda x, y: (x + lean * reach, y + reach) if y == high_y else (x - lean * reach, y - reach))


def turned_u(m: Masters, master: dict, tall: float, wide: float, side: float, arm: float) -> Shape:
    """
    ⊂ from Inter's U turned a quarter (as ∪ is that U upright), `tall` tall
    and `wide` wide: the U at the weight that gives its bowl, turned the
    upright side, a `side` thick stroke at that size; its counter widened
    until its stems, turned the arms, are `arm` thick (horizontals, lighter
    by the operators' contrast: turned as they are, the bowl stood lighter
    than the arms); cut down to `wide`, and turned (opening right).
    """
    def bowl(s: Shape) -> float:
        x0, _, x1, _ = s.bounds()
        ys = sorted(column(s, (x0 + x1) / 2))
        return ys[1] - ys[0]

    u = m.shape("U", master)
    ux0, _, ux1, _ = u.bounds()
    u = m.fitted("U", master, tall / (ux1 - ux0), side, bowl)
    x0, y0, x1, y1 = u.bounds()
    (a0, a1), _ = u.runs(y0 + 0.75 * (y1 - y0))[:2]
    stem = a1 - a0
    # the counter: the outline from the right stem's inner top round the bowl to the left stem's inner top
    pts, n = list(u.points), len(u.points)
    tops = sorted((i for i in range(n) if abs(pts[i][1] - y1) < 0.5), key=lambda i: pts[i][0])
    outer, inner_left, inner_right = {tops[0], tops[-1]}, tops[1], tops[-2]
    run = [(inner_right + k) % n for k in range((inner_left - inner_right) % n + 1)]
    if outer & set(run):
        run = [(inner_left + k) % n for k in range((inner_right - inner_left) % n + 1)]
    cx, counter = (x0 + x1) / 2, (x1 - x0) - 2 * stem
    k = (counter + 2 * (stem - arm)) / counter
    for i in run:
        pts[i] = (cx + (pts[i][0] - cx) * k, pts[i][1])
    u = stems_to(Shape(pts, list(u.on), list(u.ends), u.advance), y0 + wide)
    return u.turned(-90, (cx, y0))


def subsets(m: Masters, master: dict) -> tuple[Shape, Shape, Shape]:
    """
    ∈, ⊂ and ⊆ at a master, as the glyphs are: centred on the axis, with the
    minus sign's side bearings. ⊂ is Inter's U turned (turned_u), in the box
    ϵ gave it (as tall as Inter's ϵ at the relations' size, as wide as <),
    its upright side plus's vertical bar, its arms the minus sign's bar; ∈
    the minus sign's bar across it; ⊆ ⊂ shortened as ≤ shortens <, its
    strokes kept, over the minus sign's bar ='s gap under it.
    """
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis, rule = (my0 + my1) / 2, my1 - my0
    side = (mx0 + minus.advance - mx1) / 2
    less = sign(m, "less", master)
    width = less.bounds()[2] - less.bounds()[0]
    vertical = max(sign(m, "plus", master).contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
    stem = vertical.bounds()[2] - vertical.bounds()[0]
    epsilon = sign(m, "uni03F5", master, RELATION_SCALE)
    _, ey0, _, ey1 = max(epsilon.contours(), key=lambda c: len(c.points)).bounds()

    bowl = turned_u(m, master, ey1 - ey0, width, stem, rule)
    subset = bowl.centred(axis).spaced(side)
    # ∈: the bar from inside the upright side out to the arms' ends
    bx0, by0, bx1, by1 = bowl.bounds()
    mid = (by0 + by1) / 2
    element = (bowl + rect(bx0 + stem / 2, mid - rule / 2, bx1, mid + rule / 2)).centred(axis).spaced(side)

    # ⊆ ⊇: Inter's ≤ is < shortened over a bar; ⊂ shortened the same, its strokes kept
    le = sign(m, "lessequal", master)
    le_bar, le_chevron = sorted(le.contours(), key=lambda c: len(c.points))
    _, cy0, _, cy1 = le_chevron.bounds()
    lx0, ly0, lx1, ly1 = less.bounds()
    small = turned_u(m, master, (ey1 - ey0) * (cy1 - cy0) / (ly1 - ly0), width, stem, rule).centred((cy0 + cy1) / 2)
    sx0, bowl_bottom, sx1, _ = small.bounds()
    # the bar under it, as far from its lower arm as ='s bars are apart (≤'s own is closer: a point over a bar)
    _, b0, _, b1 = le_bar.bounds()
    under = rect(sx0, bowl_bottom - gap(m, master) - (b1 - b0), sx1, bowl_bottom - gap(m, master))
    subseteq = (small + under).centred(axis).spaced(side)
    return element, subset, subseteq


def cups(m: Masters, master: dict) -> tuple[Shape, Shape]:
    """∪ and ∩ at a master: Inter's U as wide as ⊂, its stems as thick as plus's vertical bar, cut down to ⊂'s height, on the axis."""
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    vertical = max(sign(m, "plus", master).contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
    stem = vertical.bounds()[2] - vertical.bounds()[0]
    _, subset, _ = subsets(m, master)
    sub_x0, sub_y0, sub_x1, sub_y1 = subset.bounds()
    u = m.shape("U", master)
    ux0, uy0, ux1, _ = u.bounds()
    u = m.fitted("U", master, (sub_x1 - sub_x0) / (ux1 - ux0), stem)
    ux0, uy0, ux1, _ = u.bounds()
    cup = stems_to(u, uy0 + (sub_y1 - sub_y0)).centred(axis).spaced(side)
    return cup, cup.rotated()


def vertical_bars(m: Masters, design: dict, master: dict, upem: int) -> tuple[Shape, Shape]:
    """| and ∥ at a master: Inter's bars as tall as Inter Math's parentheses, centred like them; ∥ two, ='s gap apart."""
    plus = sign(m, "plus", master)
    vertical = max(plus.contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
    vx0, _, vx1, _ = vertical.bounds()
    stem = vx1 - vx0
    _, p0, _, p1 = m.shape(case(m, "parenleft"), design).bounds()
    p0, p1 = (p0 + p1 - NORMAL * upem) / 2 - axis_drop(m, design), (p0 + p1 + NORMAL * upem) / 2 - axis_drop(m, design)
    bar = bars_to(m.fitted("bar", master, 1, stem), p0, p1)
    # ∥: two of them, as far apart as ='s bars (Inter's ‖ is tighter)
    bw = bar.bounds()[2] - bar.bounds()[0]
    parallel = Shape.join([bar, bar.moved(bw + gap(m, master), 0)], bar.advance + bw + gap(m, master))
    return bar, parallel


def angle(m: Masters, master: dict) -> Shape:
    """∠ at a master: minus's bar on the baseline and a diagonal as thick across as plus's vertical bar, its point cut flat like <'s."""
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    rule = my1 - my0
    vertical = max(sign(m, "plus", master).contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
    thickness = vertical.bounds()[2] - vertical.bounds()[0]
    cap_height = m.section("one", master["wght"], master["opsz"])[2]
    # the diagonal rises from the bar's top left to cap height, its outer edge ending over the bar's end
    run = mx1 - mx0
    for _ in range(4):  # its width depends on its slant
        slope = run / (cap_height - rule)
        across = thickness * math.hypot(1, slope)
        run = (mx1 - mx0) - across
    diagonal = Shape.polygon([(mx0, rule), (mx0 + run, cap_height), (mx0 + run + across, cap_height), (mx0 + across, rule)])
    return Shape.join([rect(mx0, 0, mx1, rule), diagonal], minus.advance)


def stacked(parts: list[Shape], white: float, axis: float, advance: float) -> Shape:
    """
    Parts one over the other, the first lowest, `white` apart from ink to ink,
    the whole centred on the axis.
    """
    out: list[Shape] = []
    for p in parts:
        if out:
            p = p.moved(0, out[-1].bounds()[3] + white - p.bounds()[1])
        out.append(p)
    return Shape.join(out, advance).centred(axis)


def equalities(m: Masters, master: dict) -> tuple[Shape, Shape, Shape, Shape]:
    """
    ≡ ≅ ≃ ∼ at a master: ='s bars and ≈'s upper tilde, on the axis, ='s gap
    between each of them and the next, ink to ink. (Set at ='s pitch, middle to
    middle, the tilde's ends came down on the bar as it grew with the weight:
    a third of ='s gap at Black.)
    """
    _, my0, _, my1 = sign(m, "minus", master).bounds()
    axis = (my0 + my1) / 2
    eq = even_bars(m, "equal", master)
    low, high = sorted(eq.contours(), key=lambda c: c.bounds()[1])
    centre_of = lambda c: (c.bounds()[1] + c.bounds()[3]) / 2  # noqa: E731
    pitch = centre_of(high) - centre_of(low)
    approx = sign(m, "approxequal", master)
    tilde = max(approx.contours(), key=lambda c: c.bounds()[3])
    identical = Shape.join([low.centred(axis - pitch), low.centred(axis), low.centred(axis + pitch)], eq.advance)
    white = gap(m, master)
    congruent = stacked([low, low, tilde], white, axis, eq.advance)
    simeq = stacked([low, tilde], white, axis, eq.advance)
    sim = Shape.join([tilde.centred(axis)], approx.advance)
    return identical, congruent, simeq, sim


def geometry_glyphs(path, upem: int) -> list[NewGlyph]:
    m = Masters(path, SOURCES)
    shapes: dict[tuple[str, int], list[Shape]] = {}

    for design in m.masters:
        # every part at the operators' weight
        master = m.lighter(design, OFFSET)
        minus = sign(m, "minus", master)
        mx0, my0, mx1, my1 = minus.bounds()
        axis = (my0 + my1) / 2
        side = (mx0 + minus.advance - mx1) / 2
        rule = my1 - my0
        plus = sign(m, "plus", master)
        vertical = max(plus.contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
        vx0, _, vx1, _ = vertical.bounds()
        # the operators' stroke: what a scaled part is drawn to
        stem = vx1 - vx0

        # ∈ ∋ ⊂ ⊃ ⊆ ⊇
        element, subset, subseteq = subsets(m, master)

        # ∪ ∩: U as wide as ⊂, its stems down to ⊂'s height
        sub_x0, sub_y0, sub_x1, sub_y1 = subset.bounds()
        cup, cap = cups(m, master)

        # ∉: ∈ crossed by ≠'s slash, drawn out to pass it as far as ≠'s passes its bars, centred on it
        cap_height = m.section("one", master["wght"], master["opsz"])[2]
        not_slash, past = slash(m, master)
        # \not: Inter's ≠ is = and this slash, and all of Inter's relations are as wide as =
        not_slash = Shape(not_slash.points, not_slash.on, not_slash.ends, 0)
        ex0, ey0, ex1, ey1 = element.bounds()
        crossing = drawn_slash(not_slash, ey1 - ey0 + 2 * past)
        sx0_, sy0_, sx1_, sy1_ = crossing.bounds()
        notin = element + crossing.moved((ex0 + ex1 - sx0_ - sx1_) / 2, (ey0 + ey1 - sy0_ - sy1_) / 2)
        # ∌ (\\notni): ∋ crossed by the same slash, not mirrored (a slash leans one way), the longer of KaTeX's two
        # (it builds \\notni from \\not, ≠'s slash as long as =)
        mirror = element.mirrored()
        mx0_, my0_, mx1_, my1_ = mirror.bounds()
        notni = mirror + crossing.moved((mx0_ + mx1_ - sx0_ - sx1_) / 2, (my0_ + my1_ - sy0_ - sy1_) / 2)

        # ⊥: plus's vertical bar up to cap height, standing on minus's bar
        centre = (mx0 + mx1) / 2
        perp = Shape.join(
            [rect(mx0, 0, mx1, rule), rect(centre - (vx1 - vx0) / 2, 0, centre + (vx1 - vx0) / 2, cap_height)], minus.advance
        )

        # ∠: minus's bar on the baseline and a diagonal as thick across as the operators' stroke, its point cut flat like <'s
        angle_ = angle(m, master)

        # | ∥: Inter's bars, as tall as Inter Math's parentheses, centred like them
        bar, parallel = vertical_bars(m, design, master, upem)

        # ∀ ∃: turned letters, their stroke the operators' (as TeX's); ∇: at the letters' weight (as TeX's, heavy)
        forall = m.fitted("A", master, 1, stem, Shape.across).rotated()
        exists = m.fitted("E", master, 1, stem, lambda e: e.side(0.25)).mirrored()
        nabla = m.shape("uni0394", design).rotated()
        # ∄: ∃ crossed by ≠'s slash, drawn out along its slant to pass it as far as ≠'s passes its bars
        qx0, qy0, qx1, qy1 = exists.bounds()
        long_slash = drawn_slash(not_slash, qy1 - qy0 + 2 * past)
        lx0, ly0, lx1, ly1 = long_slash.bounds()
        nexists = exists + long_slash.moved((qx0 + qx1 - lx0 - lx1) / 2, (qy0 + qy1 - ly0 - ly1) / 2)

        # ∧ ∨: Λ as tall as ⊂, as heavy as the operators; ∨ turned (the pair of ∪ ∩)
        _, l0, _, l1 = m.shape("Lambda", master).bounds()
        k = (sub_y1 - sub_y0) / (l1 - l0)
        wedge = m.fitted("Lambda", master, k, stem, Shape.across).centred(axis).spaced(side)
        vee = wedge.rotated()
        # ∓: ± (its bars as wide as the minus sign) turned
        minusplus = even_bars(m, "plusminus", master).rotated()

        # ≡ ≅ ≃ ∼: ='s bars and ≈'s upper tilde, at ='s pitch
        identical, congruent, simeq, sim = equalities(m, master)

        # ∘ ⋅ ∙: on the axis
        ring = sign(m, "degree", master, RELATION_SCALE).centred(axis)
        dot = sign(m, "periodcentered", master, DOT).centred(axis)
        bullet = sign(m, "bullet", master, RELATION_SCALE).centred(axis)

        for cp, s in {
            0x2208: element, 0x220B: element.mirrored(), 0x2209: notin, 0x220C: notni,
            0x2282: subset, 0x2283: subset.mirrored(), 0x2286: subseteq, 0x2287: subseteq.mirrored(),
            0x222A: cup, 0x2229: cap, 0x22A5: perp, 0x2220: angle_,
            0x2218: ring, 0x22C5: dot, 0x2219: bullet, 0xE020: not_slash,
            0x2200: forall, 0x2203: exists, 0x2204: nexists, 0x2207: nabla,
            0x2227: wedge, 0x2228: vee, 0x2213: minusplus,
            0x2261: identical, 0x2245: congruent, 0x2243: simeq, 0x223C: sim,
        }.items():
            shapes.setdefault((f"uni{cp:04X}", cp), []).append(s)

        shapes.setdefault(("bar.math", 0x007C), []).append(bar)
        shapes.setdefault(("uni2225", 0x2225), []).append(parallel)

    return [m.glyph(name, s, cp) for (name, cp), s in shapes.items()]
