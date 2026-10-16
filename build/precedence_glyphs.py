"""
The precedence relations: \\prec \\succ \\preceq \\succeq, which KaTeX sets
from Main, and \\preccurlyeq \\curlyeqprec \\precsim \\precapprox and their
mirrors, from its AMS font (their negations: build/negated_glyphs.py).
Inter has none: they are Inter Math's < and ≤ (build/operators.py) with
curved arms, and the order relations' parts (build/order_glyphs.py), as heavy
as them, centred on the math axis, with the minus sign's side bearings.

- ≺: TeX's is a cusp, two arcs leaving the point level with the axis and
  curving out to steep ends; here, arcs of Inter's ○ (drawn as ○ is: quadratic
  arcs, build/shape_glyphs.py), as thick as <'s arms, in <'s box: the point
  cut upright as <'s is, the ends cut level as Inter cuts its curves' ends;
- ⪯: that chevron in ≤'s box (smaller and flatter than <'s) over ≤'s bar, as
  far from it as ≤'s is;
- ≼ ⋞: the ≤-sized chevron with a second lower arm, the curly bar: a
  concentric arc ='s gap under the arm, across, from under the point to a
  stroke and a gap under the arm's end, as ⩽'s bar runs along its lower arm;
  ⋞ upside down (TeX's are);
- ≾ ⪷: the ≤-sized chevron over ∼ or ≈, hanging from where ≤'s bar's top is
  (as ≲ ⪅).

The ≻ forms are the ≺ ones mirrored, their ∼ and ≈ kept as they are.
"""

import math

from arrow_glyphs import flipped
from operators import OFFSET, arm_stroke, even_bars, gap, sign
from shape_glyphs import arc
from variable import Masters, NewGlyph, Shape

CASED = ["minus", "less", "lessequal", "equal", "approxequal"]
SOURCES = [*CASED, "circlewhite", "one"]
# the ones KaTeX sets from Main (the rest come from its AMS font)
MAIN = {0x227A, 0x227B, 0x2AAF, 0x2AB0}
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x227A: ("arcs of ○ in <'s box, as thick as its arms", "less circlewhite"),
    0x227B: ("≺ mirrored", "less circlewhite"),
    0x2AAF: ("≤'s chevron curved, over its bar", "lessequal circlewhite"),
    0x2AB0: ("⪯ mirrored", "lessequal circlewhite"),
    0x227C: ("≤'s chevron curved, with a curved bar along its lower arm", "lessequal circlewhite"),
    0x227D: ("≼ mirrored", "lessequal circlewhite"),
    0x22DE: ("≼ upside down", "lessequal circlewhite"),
    0x22DF: ("≽ upside down", "lessequal circlewhite"),
    0x227E: ("≤'s chevron curved, over ∼", "lessequal circlewhite approxequal"),
    0x227F: ("≾ mirrored", "lessequal circlewhite approxequal"),
    0x2AB7: ("≤'s chevron curved, over ≈", "lessequal circlewhite approxequal"),
    0x2AB8: ("⪷ mirrored", "lessequal circlewhite approxequal"),
}

Box = tuple[float, float, float, float]


def across(shape: Shape) -> float:
    """A chevron's arm stroke across the arm (operators.arm_stroke measures it upright, halfway along)."""
    x0, y0, x1, y1 = max(shape.contours(), key=lambda c: len(c.points)).bounds()
    return arm_stroke(shape) * math.cos(math.atan2((y1 - y0) / 2, x1 - x0))


def radius(width: float, half: float, stroke: float) -> float:
    """
    The radius of an arm's middle line, tangent to the axis at the point, for
    the arm's outer edge to end `width` from the point and `half` from the
    axis (its end cut level there): (R + t/2)² = width² + (R − half)².
    """
    return (width * width + half * half - stroke * stroke / 4) / (stroke + 2 * half)


def upper_arm(box: Box, stroke: float) -> tuple[Shape, tuple[float, float], float]:
    """A curved chevron's upper arm in a box (the point at its left on its middle height): the arm, its circle's centre, and radius."""
    x0, y0, x1, y1 = box
    axis, half = (y0 + y1) / 2, (y1 - y0) / 2
    r = radius(x1 - x0, half, stroke)
    centre = (x0, axis + r)
    # from the point (the bottom of the circle), cut upright, anticlockwise to the end, cut level at the box's top
    end = math.degrees(math.asin((half - r) / (r + stroke / 2)))
    return arc(centre, r, stroke, ((x0, axis), (x0, axis + 1)), ((x0, y1), (x1, y1)), (-90, end)), centre, r


def chevron(box: Box, stroke: float) -> Shape:
    """≺ in a box: its two arms, the lower one the upper one upside down."""
    arm, _, _ = upper_arm(box, stroke)
    axis = (box[1] + box[3]) / 2
    return Shape.join([arm, flipped(arm, axis)], 0)


def curly_bar(box: Box, stroke: float, space: float) -> Shape:
    """
    ≼'s second lower arm: concentric with the lower arm, `space` under it
    across, from under the point (cut upright) to a stroke and `space` under
    the arm's end (cut level).
    """
    x0, y0, _, y1 = box
    axis = (y0 + y1) / 2
    arm, (cx, cy), r = upper_arm(box, stroke)
    # drawn as the upper arm's (on the circle above the axis), then turned upside down
    bottom_cut = y1 + stroke + space
    inner = r - stroke - space
    end = math.degrees(math.asin((bottom_cut - cy) / (inner + stroke / 2)))
    bar = arc((cx, cy), inner, stroke, ((x0, axis), (x0, axis + 1)), ((x0, bottom_cut), (x0 + 1, bottom_cut)), (-90, end))
    return flipped(bar, axis)


def precedence_shapes(m: Masters, master: dict) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    space = gap(m, master)

    def relation(parts: list[Shape]) -> Shape:
        return Shape.join(parts, 0).centred(axis).spaced(side)

    def both(cp: int, s: Shape) -> None:
        """A ≺ form and its ≻ mirror (the next code point)."""
        shapes[cp], shapes[cp + 1] = s, s.mirrored()

    # ≺ ≻: in <'s box, as thick as its arms
    less = sign(m, "less", master)
    both(0x227A, relation([chevron(less.bounds(), across(less))]))

    # the ≤-sized chevron (≤'s box and arms), ≤'s bar and how far under it
    bar, le = sorted(even_bars(m, "lessequal", master).contours(), key=lambda c: len(c.points))
    box, thick = le.bounds(), across(le)
    small = chevron(box, thick)
    _, _, _, b1 = bar.bounds()

    # ⪯ ⪰
    both(0x2AAF, relation([small, bar]))

    # ≼ ≽, and ⋞ ⋟ upside down
    curly = relation([small, curly_bar(box, thick, space)])
    both(0x227C, curly)
    shapes[0x22DE], shapes[0x22DF] = flipped(curly, axis), flipped(curly.mirrored(), axis)

    # ≾ ≿ ⪷ ⪸: ∼ and ≈ hanging from where ≤'s bar's top is, centred under the chevron (≻'s where ≺'s is)
    tilde = max(sign(m, "approxequal", master).contours(), key=lambda c: c.bounds()[3])
    x0, _, x1, _ = box
    succ = small.mirrored()
    succ = succ.moved(x0 - succ.bounds()[0], 0)
    for cp, waves in ((0x227E, tilde), (0x2AB7, even_bars(m, "approxequal", master))):
        wx0, _, wx1, wy1 = waves.bounds()
        hung = waves.moved((x0 + x1 - wx0 - wx1) / 2, b1 - wy1)
        shapes[cp] = relation([small, hung])
        shapes[cp + 1] = relation([succ, hung])
    return shapes


def precedence_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, [*SOURCES, *(f"{n}.case" for n in CASED)])
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in precedence_shapes(m, m.lighter(design, OFFSET)).items():
            shapes.setdefault(cp, []).append(s)
    return [m.glyph(f"uni{cp:04X}", s, cp) for cp, s in shapes.items()]
