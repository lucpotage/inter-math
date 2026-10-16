"""
The shapes and symbols KaTeX sets from its AMS font that school maths uses
(\\therefore \\because \\measuredangle \\sphericalangle \\square \\Box
\\blacksquare \\checkmark):

- □ ■ ✓: Inter's own, as it draws them (KEPT): its □ ■ are squares as tall
  as the capitals on the baseline, as TeX's are, and as heavy as its △;
- ∴ ∵: three of Inter Math's ⋅ (as ⋯ has them) in an equilateral triangle
  from the baseline to the x-height, as TeX's: the lower dots sit as Inter's
  period does, the upper one as far over the x-height; the dots grow inward
  with the weight, the triangle keeps its height (as letters keep theirs);
- ∡: Inter Math's ∠ with an arc of Inter's ○ (its circle, as heavy as Inter
  draws ○: lighter than the operators at Black, as its rings are) centred
  where the bar's and the diagonal's middle lines meet, ARC of the bar's
  length out (TeX's), across both strokes and ending flush with their outer
  edges (cut level under the bar, along the diagonal): TeX's ends half a
  stroke past them, stubs at Inter's weights;
- ∢: Inter Math's < with such an arc centred at its point, SPHERICAL of its
  arms' length out (TeX's), across both arms, flush with their outer edges.
"""

import math

from geometry_glyphs import DOT, angle
from operators import OFFSET, sign
from variable import Masters, NewGlyph, Shape

CASED = ["minus", "plus", "less"]
SOURCES = [*CASED, *(f"{n}.case" for n in CASED), "periodcentered", "period", "x", "circlewhite", "one"]
# Inter's own glyphs these are, kept as Inter draws them (AMS symbols the build keeps from Inter: build.py)
KEPT = {0x25A1, 0x25A0, 0x2713}
# the arcs: their middle line's radius against ∠'s bar and <'s arms (TeX's ∡ and ∢); how many quadratic arcs
# they are drawn with (the same at every master: their span changes with the weight, their points can't)
ARC = 0.59
SPHERICAL = 0.8
ARCS = 4
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x2234: ("three of ⋅'s dots, from the baseline to the x-height", "periodcentered"),
    0x2235: ("∴ upside down", "periodcentered"),
    0x2221: ("∠ with an arc of ○", "minus less circlewhite"),
    0x2222: ("< with an arc of ○", "less circlewhite"),
}


Line = tuple[tuple[float, float], tuple[float, float]]


def meets(centre: tuple[float, float], r: float, line: Line, near: float) -> float:
    """The angle (degrees) at which a circle about `centre` meets a line (through two points), the crossing nearest `near`."""
    (x0, y0), (x1, y1) = line
    n = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    px, py = x0 - centre[0], y0 - centre[1]
    b = ux * px + uy * py
    root = math.sqrt(max(0.0, b * b - (px * px + py * py - r * r)))
    angles = [math.degrees(math.atan2(py + t * uy, px + t * ux)) for t in (-b - root, -b + root)]
    return min(angles, key=lambda a: abs((a - near + 180) % 360 - 180))


def arc(centre: tuple[float, float], radius: float, stroke: float, start: Line, stop: Line, near: tuple[float, float], steps: int = ARCS) -> Shape:
    """
    A stroke along a circle (`radius` its middle line's) from the line
    `start` to the line `stop`, anticlockwise, each end cut along its line
    (the crossings nearest the angles `near`): drawn as Inter's ○ is,
    `steps` quadratic arcs (Inter's are 22.5°), their off-curve points on the
    bisector, 1/cos(half the arc) out.
    """
    cx, cy = centre

    def side(r: float, reverse: bool) -> tuple[list, list]:
        a0, a1 = meets(centre, r, start, near[0]), meets(centre, r, stop, near[1])
        assert 0 < (a1 - a0) / steps <= 25, f"an arc of {a1 - a0:.0f}° in {steps} quadratic arcs"
        half = math.radians((a1 - a0) / steps / 2)
        pts, on = [], []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            on.append(True)
            if i < steps:
                b = a + half
                pts.append((cx + r / math.cos(half) * math.cos(b), cy + r / math.cos(half) * math.sin(b)))
                on.append(False)
        return (pts[::-1], on[::-1]) if reverse else (pts, on)

    # clockwise: the outer side back from `stop` to `start`, the inner one from `start` to `stop`
    outer, inner = side(radius + stroke / 2, True), side(radius - stroke / 2, False)
    return Shape(outer[0] + inner[0], outer[1] + inner[1], [len(outer[0]) + len(inner[0]) - 1], 0)


def shape_shapes(m: Masters, design: dict, master: dict) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2

    # ∴ ∵: ⋅'s dots, the lower ones as low as Inter's period, the upper one as far over the x-height
    dot = sign(m, "periodcentered", master, DOT)
    dx0, dy0, dx1, dy1 = dot.bounds()
    d = dx1 - dx0
    under = -m.shape("period", design).bounds()[1]
    x_height = m.shape("x", design).bounds()[3]
    low, high = -under + d / 2, x_height + under - d / 2
    reach = (high - low) / math.sqrt(3)

    def at(x: float, y: float) -> Shape:
        return dot.moved(x - (dx0 + dx1) / 2, y - (dy0 + dy1) / 2)

    shapes[0x2234] = Shape.join([at(-reach, low), at(reach, low), at(0, high)], 0).spaced(side)
    shapes[0x2235] = Shape.join([at(-reach, high), at(reach, high), at(0, low)], 0).spaced(side)

    # the arcs' stroke: Inter's ○'s
    ring_outer, ring_inner = sorted(m.shape("circlewhite", master).contours(), key=lambda c: c.bounds()[0])
    ring = ring_inner.bounds()[0] - ring_outer.bounds()[0]

    # ∡: ∠ with an arc centred where its bar's and diagonal's middle lines meet
    angle_ = angle(m, master)
    bar, diagonal = sorted(angle_.contours(), key=lambda c: c.bounds()[3])
    bx0, by0, bx1, by1 = bar.bounds()
    # the diagonal's middle line, from its foot (on the bar) to its top
    (f0, fy), (f1, _) = sorted(((x, y) for x, y in diagonal.points if abs(y - by1) < 0.5))
    (t0, ty), (t1, _) = sorted(((x, y) for x, y in diagonal.points if abs(y - by1) >= 0.5))
    foot, top = ((f0 + f1) / 2, fy), ((t0 + t1) / 2, ty)
    lean = (top[0] - foot[0]) / (top[1] - foot[1])
    vertex = (foot[0] - (fy - (by0 + by1) / 2) * lean, (by0 + by1) / 2)
    rise = math.degrees(math.atan2(top[1] - foot[1], top[0] - foot[0]))
    r = ARC * (bx1 - bx0)
    # from the bar's lower edge to the diagonal's outer edge (its left one: through its foot's and top's left points)
    under, outside = ((bx0, by0), (bx1, by0)), ((f0, fy), (t0, ty))
    shapes[0x2221] = Shape.join([angle_, arc(vertex, r, ring, under, outside, (0, rise))], angle_.advance)

    # ∢: < with an arc centred at its point, across both arms
    less = sign(m, "less", master)
    lx0, _, lx1, _ = less.bounds()
    point = (lx0, axis)
    r = SPHERICAL * (lx1 - lx0)
    # from the lower arm's outer edge to the upper one's: from the point's corners to the arms' ends
    corner = sorted(y for x, y in less.points if abs(x - lx0) < 0.5)
    lowest, highest = min(less.points, key=lambda p: p[1]), max(less.points, key=lambda p: p[1])
    lower, upper = ((lx0, corner[0]), lowest), ((lx0, corner[-1]), highest)
    spread = math.degrees(math.atan2(highest[1] - axis, highest[0] - lx0))
    shapes[0x2222] = Shape.join([less, arc(point, r, ring, lower, upper, (-spread, spread))], less.advance)
    return shapes


def shape_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, SOURCES)
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in shape_shapes(m, design, m.lighter(design, OFFSET)).items():
            shapes.setdefault(cp, []).append(s)
    return [m.glyph(f"uni{cp:04X}", s, cp) for cp, s in shapes.items()]
