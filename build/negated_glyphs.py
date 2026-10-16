"""
The negated relations KaTeX sets from its AMS font (\\nless, \\nleq,
\\nleqslant, \\nleqq, \\lneq, \\lneqq, \\lvertneqq, \\lnsim, \\lnapprox,
\\nsim, \\ncong, \\nmid, \\nparallel, \\nsubseteq, \\subsetneq,
\\varsubsetneq, \\subsetneqq, \\varsubsetneqq, \\nsubseteqq, \\nvdash,
\\nvDash, \\nVdash, \\nVDash, \\nprec, \\npreceq, \\precneqq, \\precnsim,
\\precnapprox, \\ntriangleleft, \\ntrianglelefteq, and their mirrors): Inter Math's own relations crossed by the
slash of Inter's ≠, the one Inter Math's ∉ ∄ and \\not have
(build/geometry_glyphs.py), drawn out or cut along its slant, its ends cut
level as Inter's:

- across the whole relation (≮ ≯ ≰ ≱, \\nleqslant \\ngeqslant \\nleqq
  \\ngeqq, ≁ ≆ ⊈ ⊉ ⊬ ⊭ ⊮ ⊯ ⊀ ⊁ ⋠ ⋡ ⋪ ⋫ ⋬ ⋭, \\nsubseteqq \\nsupseteqq): centred on it,
  passing it above and below as far as ≠'s slash passes its bars, as ∉'s
  and ∄'s do (build/geometry_glyphs.py's slash(): a slash ending where the
  relation ends is missed at a glance; TeX's pass theirs by a quarter of
  the cap height);
- across the bars or waves under a chevron or a bowl only, as TeX's (⪇ ⪈
  ≨ ≩ ⋦ ⋧ ⪉ ⪊ ⊊ ⊋ ⫋ ⫌, and ⪵ ⪶ ⋨ ⋩ ⪹ ⪺ under ≺ ≻'s curved chevron,
  build/precedence_glyphs.py): passing them below as far as ≠'s passes its bars,
  above by half ='s gap, so that it stops halfway to what is above;
  \\lvertneqq \\gvertneqq cross them with plus's vertical bar instead, as
  long; \\varsubsetneq \\varsupsetneq \\varsubsetneqq \\varsupsetneqq carry
  the slash on up to ⊂'s lower arm, joining it (TeX's);
- across vertical bars (∤ ∦): not ≠'s slash, which is steep enough to run
  along them (and fill in at Black), but the stroke of Inter's ł, Inter's
  own across a stem: at the weight that gives l the bars' stroke, on the
  axis, drawn out along its slant to pass the outer bars by as much as it
  passes ł's stem;
- ⫅ ⫆ (\\subseteqq, \\supseteqq, which ⫋ ⫌ cross): ⊆ ⊇ with a second
  bar, ='s gap under their own, as ≦ is drawn (build/order_glyphs.py).

A slash leans one way: the ≥ forms are never the ≤ ones mirrored once
crossed, but their mirrored relation crossed.
"""

from geometry_glyphs import SOURCES as GEOMETRY_SOURCES, drawn_slash, equalities, slash as negation_slash, subsets, vertical_bars
from operators import OFFSET, column, even_bars, gap, sign
from order_glyphs import CASED as ORDER_CASED, SOURCES as ORDER_SOURCES, order_shapes
from precedence_glyphs import precedence_shapes
from binary_glyphs import triangles
from set_glyphs import forces
from symbol_glyphs import turnstiles
from variable import Masters, NewGlyph, Shape

SOURCES = list(dict.fromkeys([*GEOMETRY_SOURCES, *ORDER_SOURCES, *(f"{n}.case" for n in ORDER_CASED), "l", "lslash", "uni25B7", "uni25EF", "multiply", "multiply.case"]))
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x226E: ("< crossed by ≠'s slash", "less notequal"),
    0x226F: ("> crossed by ≠'s slash", "greater notequal"),
    0x2270: ("≤ crossed by ≠'s slash", "lessequal notequal"),
    0x2271: ("≥ crossed by ≠'s slash", "greaterequal notequal"),
    0xE010: ("⩽ crossed by ≠'s slash", "lessequal notequal"),
    0xE00F: ("⩾ crossed by ≠'s slash", "greaterequal notequal"),
    0xE011: ("≦ crossed by ≠'s slash", "lessequal equal notequal"),
    0xE00E: ("≧ crossed by ≠'s slash", "greaterequal equal notequal"),
    0x2241: ("∼ crossed by ≠'s slash", "approxequal notequal"),
    0x2246: ("≅ crossed by ≠'s slash", "approxequal equal notequal"),
    0x2288: ("⊆ crossed by ≠'s slash", "U lessequal notequal"),
    0x2289: ("⊇ crossed by ≠'s slash", "U lessequal notequal"),
    0xE016: ("⫅ crossed by ≠'s slash", "U lessequal notequal"),
    0xE018: ("⫆ crossed by ≠'s slash", "U lessequal notequal"),
    0x22AC: ("⊢ crossed by ≠'s slash", "plus minus notequal"),
    0x22AD: ("⊨ crossed by ≠'s slash", "plus equal notequal"),
    0x2280: ("≺ crossed by ≠'s slash", "less circlewhite notequal"),
    0x2281: ("≻ crossed by ≠'s slash", "less circlewhite notequal"),
    0x22E0: ("⪯ crossed by ≠'s slash", "lessequal circlewhite notequal"),
    0x22E1: ("⪰ crossed by ≠'s slash", "lessequal circlewhite notequal"),
    0x2AB5: ("≺ over two bars, ≠'s slash across them", "lessequal circlewhite equal notequal"),
    0x2AB6: ("≻ over two bars, ≠'s slash across them", "lessequal circlewhite equal notequal"),
    0x22E8: ("≾ with ≠'s slash across its ∼", "lessequal circlewhite approxequal notequal"),
    0x22E9: ("≿ with ≠'s slash across its ∼", "lessequal circlewhite approxequal notequal"),
    0x2AB9: ("⪷ with ≠'s slash across its ≈", "lessequal circlewhite approxequal notequal"),
    0x2ABA: ("⪸ with ≠'s slash across its ≈", "lessequal circlewhite approxequal notequal"),
    0x22EA: ("⊲ crossed by ≠'s slash", "uni25B7 notequal"),
    0x22EB: ("⊳ crossed by ≠'s slash", "uni25B7 notequal"),
    0x22EC: ("⊴ crossed by ≠'s slash", "uni25B7 lessequal notequal"),
    0x22ED: ("⊵ crossed by ≠'s slash", "uni25B7 lessequal notequal"),
    0x22AE: ("⊩ crossed by ≠'s slash", "plus minus notequal"),
    0x22AF: ("⊫ crossed by ≠'s slash", "plus equal notequal"),
    0x2A87: ("≤ with ≠'s slash across its bar", "lessequal notequal"),
    0x2A88: ("≥ with ≠'s slash across its bar", "greaterequal notequal"),
    0x2268: ("≦ with ≠'s slash across its bars", "lessequal equal notequal"),
    0x2269: ("≧ with ≠'s slash across its bars", "greaterequal equal notequal"),
    0xE00C: ("≦ with plus's bar across its bars", "lessequal equal plus"),
    0xE00D: ("≧ with plus's bar across its bars", "greaterequal equal plus"),
    0x22E6: ("≲ with ≠'s slash across its ∼", "lessequal approxequal notequal"),
    0x22E7: ("≳ with ≠'s slash across its ∼", "greaterequal approxequal notequal"),
    0x2A89: ("⪅ with ≠'s slash across its ≈", "lessequal approxequal notequal"),
    0x2A8A: ("⪆ with ≠'s slash across its ≈", "greaterequal approxequal notequal"),
    0x228A: ("⊆ with ≠'s slash across its bar", "U lessequal notequal"),
    0x228B: ("⊇ with ≠'s slash across its bar", "U lessequal notequal"),
    0x2ACB: ("⫅ with ≠'s slash across its bars", "U lessequal notequal"),
    0x2ACC: ("⫆ with ≠'s slash across its bars", "U lessequal notequal"),
    0xE01A: ("⊆ with ≠'s slash from under its bar to the bowl", "U lessequal notequal"),
    0xE01B: ("⊇ with ≠'s slash from under its bar to the bowl", "U lessequal notequal"),
    0xE017: ("⫅ with ≠'s slash from under its bars to the bowl", "U lessequal notequal"),
    0xE019: ("⫆ with ≠'s slash from under its bars to the bowl", "U lessequal notequal"),
    0x2224: ("∣ crossed by ł's stroke", "bar lslash"),
    0x2226: ("∥ crossed by ł's stroke, drawn out", "bar lslash"),
    0x2AC5: ("⊆ over a second bar, ='s gap under its own", "U lessequal"),
    0x2AC6: ("⫅ mirrored", "U lessequal"),
}


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def centre(shape: Shape) -> tuple[float, float]:
    x0, y0, x1, y1 = shape.bounds()
    return (x0 + x1) / 2, (y0 + y1) / 2


def lean(slash: Shape) -> float:
    """How far a slash goes right as it goes up (its middle line's dx/dy)."""
    ys = sorted({y for _, y in slash.points})
    mid = lambda y: sum(x for x, py in slash.points if py == y) / sum(1 for _, py in slash.points if py == y)  # noqa: E731
    return (mid(ys[-1]) - mid(ys[0])) / (ys[-1] - ys[0])


def crossed(base: Shape, slash: Shape, length: float, through: tuple[float, float] | None = None) -> Shape:
    """`base` with the slash, `length` tall, across it: centred on `through` (the base's ink centre by default)."""
    s = drawn_slash(slash, length)
    cx, cy = through or centre(base)
    sx, sy = centre(s)
    return Shape.join([base, s.moved(cx - sx, cy - sy)], base.advance)


def split(relation: Shape) -> tuple[Shape, Shape]:
    """A relation's top part (the chevron or bowl: its highest contour) and what is under it (bars, waves)."""
    contours = sorted(relation.contours(), key=lambda c: c.bounds()[3])
    return contours[-1], Shape.join(contours[:-1], relation.advance)


def stroked(m: Masters, master: dict, bars: Shape, stem: float, axis: float) -> Shape:
    """
    Vertical bars crossed by Inter's ł's stroke (at the weight that gives l a
    `stem` thick stem), on the axis, drawn out along its slant to pass the
    outer bars by as much as it passes ł's stem.
    """
    w = m.weight_for(lambda w: m.shape("l", master, w).bounds()[2] - m.shape("l", master, w).bounds()[0], stem)
    lslash = m.shape("lslash", master, w)
    letter, stroke = sorted(lslash.contours(), key=height, reverse=True)
    lx0, _, lx1, _ = letter.bounds()
    sx0, _, sx1, _ = stroke.bounds()
    left = sorted(y for x, y in stroke.points if abs(x - sx0) < 0.5)
    right = sorted(y for x, y in stroke.points if abs(x - sx1) < 0.5)
    slope, thick = (right[0] - left[0]) / (sx1 - sx0), left[1] - left[0]
    beyond = (lx0 - sx0 + sx1 - lx1) / 2
    bx0, _, bx1, _ = bars.bounds()
    cx = (bx0 + bx1) / 2
    x0, x1 = bx0 - beyond, bx1 + beyond
    y0, y1 = axis - thick / 2 + (x0 - cx) * slope, axis - thick / 2 + (x1 - cx) * slope
    return Shape.join([bars, Shape.polygon([(x0, y0), (x0, y0 + thick), (x1, y1 + thick), (x1, y1)])], bars.advance)


def negated_shapes(m: Masters, design: dict, master: dict, upem: int) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    space = gap(m, master)
    # ≠'s slash, how far it passes its bars, how it leans
    slash, past = negation_slash(m, master)
    k = lean(slash)

    def whole(base: Shape) -> Shape:
        """Across all of it, passing it as far as ≠'s slash passes its bars."""
        return crossed(base, slash, height(base) + 2 * past)

    def reach(low: Shape) -> tuple[float, float]:
        """How far a slash across bars alone goes: as far under them as ≠'s passes its bars, half ='s gap over them."""
        _, y0, _, y1 = low.bounds()
        return y0 - past, y1 + space / 2

    def under(base: Shape, low: Shape | None = None) -> Shape:
        """Across the bars or waves under its chevron or bowl (`low`, if not its contours under the highest), its middle line through theirs."""
        low = low or split(base)[1]
        cx, cy = centre(low)
        bottom, top = reach(low)
        mid = (bottom + top) / 2
        return crossed(base, slash, top - bottom, (cx + (mid - cy) * k, mid))

    def upright(base: Shape) -> Shape:
        """Plus's vertical bar across the bars under its chevron, as far as `under`'s slash goes."""
        _, low = split(base)
        cx, _ = centre(low)
        half, (bottom, top) = stem / 2, reach(low)
        bar = Shape.polygon([(cx - half, bottom), (cx - half, top), (cx + half, top), (cx + half, bottom)])
        return Shape.join([base, bar], base.advance)

    def joined(base: Shape) -> Shape:
        """The slash from as far under the bars as `under`'s up to the bowl's lower arm, its end level with the arm's top."""
        bowl, low = split(base)
        cx, cy = centre(low)
        bottom = reach(low)[0]
        top = bowl.bounds()[1]
        for _ in range(3):  # where it meets the arm depends on how high it goes (its middle line leans by k)
            top = column(bowl, cx + (top - cy) * k)[1]
        mid = (bottom + top) / 2
        return crossed(base, slash, top - bottom, (cx + (mid - cy) * k, mid))

    def relation(parts: list[Shape]) -> Shape:
        return Shape.join(parts, 0).centred(axis).spaced(side)

    plus = even_bars(m, "plus", master)
    vertical = max(plus.contours(), key=height)
    stem = vertical.bounds()[2] - vertical.bounds()[0]
    order = order_shapes(m, master)
    _, _, subseteq = subsets(m, master)
    _, congruent, _, sim = equalities(m, master)
    tack, models = turnstiles(m, design, master)
    forces_, _, forces_models = forces(m, design, master)
    bar, parallel = vertical_bars(m, design, master, upem)

    # ⫅ ⫆: ⊆ with ='s second bar under its own (as ≦ has)
    bowl, low = split(subseteq)
    subseteqq = relation([bowl, low, low.moved(0, -height(low) - space)])
    shapes[0x2AC5] = subseteqq
    shapes[0x2AC6] = subseteqq.mirrored()

    bases = {
        "less": sign(m, "less", master), "greater": sign(m, "greater", master),
        "le": even_bars(m, "lessequal", master), "ge": even_bars(m, "greaterequal", master),
        "subseteq": subseteq, "supseteq": subseteq.mirrored(),
        "subseteqq": subseteqq, "supseteqq": subseteqq.mirrored(),
    }
    for cp, base in {
        0x226E: bases["less"], 0x226F: bases["greater"], 0x2270: bases["le"], 0x2271: bases["ge"],
        0xE010: order[0x2A7D], 0xE00F: order[0x2A7E], 0xE011: order[0x2266], 0xE00E: order[0x2267],
        0x2241: sim, 0x2246: congruent, 0x2288: bases["subseteq"], 0x2289: bases["supseteq"],
        0xE016: bases["subseteqq"], 0xE018: bases["supseteqq"], 0x22AC: tack, 0x22AD: models,
        0x22AE: forces_, 0x22AF: forces_models,
    }.items():
        shapes[cp] = whole(base)
    # the precedence relations: their curved chevron is two contours (the arms), the bars or waves under them the rest
    prec = precedence_shapes(m, master)
    *_, bar_ = sorted(prec[0x2AAF].contours(), key=lambda c: c.bounds()[3], reverse=True)
    precneqq = Shape.join([*prec[0x2AAF].contours(), bar_.moved(0, -height(bar_) - space)], 0).centred(axis).spaced(side)
    tri = triangles(m, master)
    for cp, base in {
        0x2280: prec[0x227A], 0x2281: prec[0x227B], 0x22E0: prec[0x2AAF], 0x22E1: prec[0x2AB0],
        0x22EA: tri[0x22B2], 0x22EB: tri[0x22B3], 0x22EC: tri[0x22B4], 0x22ED: tri[0x22B5],
    }.items():
        shapes[cp] = whole(base)
    for cp, base in {
        0x2AB5: precneqq, 0x2AB6: precneqq.mirrored(), 0x22E8: prec[0x227E], 0x22E9: prec[0x227F], 0x2AB9: prec[0x2AB7], 0x2ABA: prec[0x2AB8],
    }.items():
        shapes[cp] = under(base, Shape.join(sorted(base.contours(), key=lambda c: c.bounds()[3])[:-2], base.advance))
    for cp, base in {
        0x2A87: bases["le"], 0x2A88: bases["ge"], 0x2268: order[0x2266], 0x2269: order[0x2267],
        0x22E6: order[0x2272], 0x22E7: order[0x2273], 0x2A89: order[0x2A85], 0x2A8A: order[0x2A86],
        0x228A: bases["subseteq"], 0x228B: bases["supseteq"], 0x2ACB: bases["subseteqq"], 0x2ACC: bases["supseteqq"],
    }.items():
        shapes[cp] = under(base)
    shapes[0xE00C] = upright(order[0x2266])
    shapes[0xE00D] = upright(order[0x2267])
    for cp, base in {0xE01A: bases["subseteq"], 0xE01B: bases["supseteq"], 0xE017: bases["subseteqq"], 0xE019: bases["supseteqq"]}.items():
        shapes[cp] = joined(base)

    # ∤ ∦: the stroke sticks out of the bars' advance: the minus sign's side bearings around it all
    shapes[0x2224] = stroked(m, master, bar, stem, axis).spaced(side)
    shapes[0x2226] = stroked(m, master, parallel, stem, axis).spaced(side)
    return shapes


def negated_glyphs(path, upem: int) -> list[NewGlyph]:
    m = Masters(path, SOURCES)
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in negated_shapes(m, design, m.lighter(design, OFFSET), upem).items():
            shapes.setdefault(cp, []).append(s)
    taken = set(m.font.getGlyphOrder())
    return [m.glyph(f"uni{cp:04X}" + (".math" if f"uni{cp:04X}" in taken else ""), s, cp) for cp, s in shapes.items()]
