"""
The order relations KaTeX sets from its AMS font (\\leqslant, \\leqq,
\\lesssim, \\lessapprox, \\lessgtr, \\lesseqgtr, \\lesseqqgtr, \\lll,
\\lessdot, \\eqslantless, and their mirrors), drawn from Inter Math's
< > ≤ ≥ = ∼ ≈ ⋅ (build/operators.py, build/geometry_glyphs.py,
build/symbol_glyphs.py): as heavy as them, centred on the math axis, with the
minus sign's side bearings, as relations have.

A chevron with something under it is ≤'s, which Inter draws smaller and
flatter than <, to stand over a bar. The parts keep Inter Math's two
distances: ≤'s, from a chevron's point (an arm's end) to the bar under it,
and ='s gap between parallel strokes (build/operators.py: gap()):

- ⩽ ⩾: ≤ with its bar slanted along the lower arm, as heavy as the arm and
  ='s gap from it, across; its ends cut upright, as the arm's end is;
- ⪕ ⪖: ⩽ ⩾ upside down about the axis (TeX's are);
- ≦ ≧: ≤ with a second bar under its own, ='s gap apart (parallels);
- ≲ ≳ ⪅ ⪆: ≤'s chevron over ∼ or ≈, hanging from where ≤'s bar's top is;
- ≶ ≷: ≤'s chevron over ≥'s, their parallel arms ='s gap apart, across;
- ⋚ ⋛ ⪋ ⪌: ≤ over ≥ upside down, sharing ≤'s bar (⋚) or ≦'s two bars (⪋),
  each chevron as far from the bar next to it as ≤'s;
- ⋘ ⋙: three < or >, nested as ≪ ≫'s two (build/symbol_glyphs.py);
- ⋖ ⋗: < > with ⋅ in their mouth, on the axis: where TeX puts it (MOUTH)
  or further out, as far from the arms as ≤'s bar from its chevron, and
  smaller where the mouth can't hold it so (heavy weights).

The ≥ forms are the ≤ ones mirrored (Inter's ≥ is its ≤ mirrored), their ∼
and ≈ kept as they are.
"""

import math

from arrow_glyphs import flipped
from geometry_glyphs import DOT
from operators import OFFSET, arm_stroke, column, even_bars, gap, sign
from symbol_glyphs import nested
from variable import Masters, NewGlyph, Shape

CASED = ["minus", "less", "greater", "lessequal", "greaterequal", "equal", "approxequal"]
SOURCES = [*CASED, "periodcentered", "one"]
# ⋖'s dot, as TeX places it: its centre this share of the way from the chevron's point to its arms' ends
MOUTH = 0.73
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x2A7D: ("≤ with its bar slanted along the lower arm", "lessequal"),
    0x2A7E: ("⩽ mirrored", "greaterequal"),
    0x2A95: ("⩽ upside down", "lessequal"),
    0x2A96: ("⩾ upside down", "greaterequal"),
    0x2266: ("≤ over a second bar, ='s gap under its own", "lessequal equal"),
    0x2267: ("≦ mirrored", "greaterequal equal"),
    0x2272: ("≤'s chevron over ∼", "lessequal approxequal"),
    0x2273: ("≥'s chevron over ∼", "greaterequal approxequal"),
    0x2A85: ("≤'s chevron over ≈", "lessequal approxequal"),
    0x2A86: ("≥'s chevron over ≈", "greaterequal approxequal"),
    0x2276: ("≤'s chevron over ≥'s, their arms ='s gap apart", "lessequal greaterequal"),
    0x2277: ("≶ mirrored", "greaterequal lessequal"),
    0x22DA: ("≤ over ≥ upside down, sharing the bar", "lessequal greaterequal"),
    0x22DB: ("⋚ mirrored", "greaterequal lessequal"),
    0x2A8B: ("≤ over ≥ upside down, with ≦'s two bars", "lessequal greaterequal equal"),
    0x2A8C: ("⪋ mirrored", "greaterequal lessequal equal"),
    0x22D8: ("three <, nested", "less"),
    0x22D9: ("three >, nested", "greater"),
    0x22D6: ("< with the middle dot in its mouth, no larger than at Regular, as ͽ's", "less periodcentered uni037D"),
    0x22D7: ("⋖ mirrored", "greater periodcentered"),
}


def lower_arm(chevron: Shape) -> tuple[float, float, float]:
    """A < chevron's lower arm, its outer edge: its height at the point (the cut's lower corner), at the arm's end, and its slope."""
    x0, y0, x1, _ = chevron.bounds()
    at_point = min(y for x, y in chevron.points if abs(x - x0) < 0.5)
    return at_point, y0, (y0 - at_point) / (x1 - x0)


def with_dot(chevron: Shape, dot: Shape, axis: float, space: float) -> Shape:
    """
    A < with a dot in its mouth, on the axis: MOUTH of the way to the arms'
    ends, or further out to keep `space` from the arms' inner edges; its
    right edge no further than their ends, the dot smaller where it must be.
    """
    x0, _, x1, _ = chevron.bounds()
    dx0, _, dx1, _ = dot.bounds()
    r = (dx1 - dx0) / 2
    # the upper arm's inner edge, through two points in the mouth (the third crossing up a vertical: lower arm, then upper)
    xa, xb = x0 + (x1 - x0) * 0.6, x1 - 1
    ya, yb = column(chevron, xa)[2], column(chevron, xb)[2]
    n = math.hypot(xb - xa, yb - ya)
    ux, uy = (xb - xa) / n, (yb - ya) / n

    def clear(x: float) -> float:
        """From a dot's centre at (x, axis) to the arm's inner edge, across."""
        return ux * (ya - axis) + uy * (x - xa)

    centre = max(x0 + MOUTH * (x1 - x0), xa + (space + r - ux * (ya - axis)) / uy)
    if centre + r > x1:
        # as large as fits between the arms, its right edge at their ends
        r_fit = (clear(x1) - space) / (1 + uy)
        dot = dot.scaled(r_fit / r)
        r, centre = r_fit, x1 - r_fit
    dx0, dy0, dx1, dy1 = dot.bounds()
    return Shape.join([chevron, dot.moved(centre - (dx0 + dx1) / 2, axis - (dy0 + dy1) / 2)], chevron.advance)


def order_shapes(m: Masters, master: dict) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    space = gap(m, master)

    def relation(parts: list[Shape]) -> Shape:
        return Shape.join(parts, 0).centred(axis).spaced(side)

    # ≤'s chevron and bar, how far apart; ≥'s chevron where ≤'s is
    bar, chevron = sorted(even_bars(m, "lessequal", master).contours(), key=lambda c: len(c.points))
    x0, c0, x1, _ = chevron.bounds()
    _, b0, _, b1 = bar.bounds()
    tight = c0 - b1
    greater = chevron.mirrored()
    greater = greater.moved(x0 - greater.bounds()[0], 0)
    _, _, _, g1 = greater.bounds()

    # ⩽ ⩾ ⪕ ⪖: the bar along the lower arm, as heavy as it (upright, halfway), ='s gap under it across
    at_point, at_end, slope = lower_arm(chevron)
    drop = space * math.hypot(1, slope)
    thick = arm_stroke(chevron)
    top0, top1 = at_point - drop, at_end - drop
    leqslant = relation([chevron, Shape.polygon([(x0, top0 - thick), (x0, top0), (x1, top1), (x1, top1 - thick)])])
    shapes[0x2A7D] = leqslant
    shapes[0x2A7E] = leqslant.mirrored()
    shapes[0x2A95] = flipped(leqslant, axis)
    shapes[0x2A96] = flipped(leqslant.mirrored(), axis)

    # ≦ ≧: ='s two bars under the chevron
    second = bar.moved(0, -(b1 - b0) - space)
    leqq = relation([chevron, bar, second])
    shapes[0x2266] = leqq
    shapes[0x2267] = leqq.mirrored()

    # ≲ ≳ ⪅ ⪆: ∼ and ≈ hanging from where ≤'s bar's top is, centred under the chevron
    tilde = max(sign(m, "approxequal", master).contours(), key=lambda c: c.bounds()[3])
    for cp, waves in ((0x2272, tilde), (0x2A85, even_bars(m, "approxequal", master))):
        wx0, _, wx1, wy1 = waves.bounds()
        hung = waves.moved((x0 + x1 - wx0 - wx1) / 2, b1 - wy1)
        shapes[cp] = relation([chevron, hung])
        shapes[cp + 1] = relation([greater, hung])

    # ≶ ≷: ≥'s chevron under ≤'s, its upper arm ='s gap under the other's lower arm, across (they are parallel)
    lessgtr = relation([chevron, greater.moved(0, at_point - drop - g1)])
    shapes[0x2276] = lessgtr
    shapes[0x2277] = lessgtr.mirrored()

    # ⋚ ⋛ ⪋ ⪌: ≥ upside down under ≤, its chevron as far under the last bar as ≤'s is over its own
    _, s0, _, _ = second.bounds()
    lesseqgtr = relation([chevron, bar, greater.moved(0, b0 - tight - g1)])
    lesseqqgtr = relation([chevron, bar, second, greater.moved(0, s0 - tight - g1)])
    shapes[0x22DA] = lesseqgtr
    shapes[0x22DB] = lesseqgtr.mirrored()
    shapes[0x2A8B] = lesseqqgtr
    shapes[0x2A8C] = lesseqqgtr.mirrored()

    # ⋘ ⋙
    shapes[0x22D8] = nested(m, master, "less", 3)
    shapes[0x22D9] = nested(m, master, "greater", 3)

    # ⋖ ⋗: Inter Math's ⋅ in the mouth of its <, no larger than at Regular: Inter's ͽ (a dot inside a stroke) grows its
    # dot to Regular and holds it there, its stroke thickening around it
    dot = sign(m, "periodcentered", master, DOT)
    regular = sign(m, "periodcentered", {**master, "wght": m.axes["wght"].defaultValue}, DOT)
    grown = (dot.bounds()[2] - dot.bounds()[0]) / (regular.bounds()[2] - regular.bounds()[0])
    if grown > 1:
        dot = dot.scaled(1 / grown)
    lessdot = with_dot(sign(m, "less", master), dot, axis, tight)
    shapes[0x22D6] = lessdot
    shapes[0x22D7] = lessdot.mirrored()
    return shapes


def order_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, [*SOURCES, *(f"{n}.case" for n in CASED)])
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in order_shapes(m, m.lighter(design, OFFSET)).items():
            shapes.setdefault(cp, []).append(s)
    return [m.glyph(f"uni{cp:04X}", s, cp) for cp, s in shapes.items()]
