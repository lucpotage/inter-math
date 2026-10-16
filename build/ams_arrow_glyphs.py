"""
The arrows KaTeX sets from its AMS font, drawn from Inter Math's own
(build/operators.py, build/arrow_glyphs.py: Inter's arrows on the axis, their
heads ARROW_HEAD as large, their shafts ARROW_LENGTH as long). The arrows TeX
draws only in its AMS font (↠ ↣ ⇢ ⇝ ↭ ↶ ↫ ↺ ↰ and their mirrors) have the
pairs' smaller heads, PAIR of an arrow's, as TeX's have its ⇉'s, and are as
light as the pairs past Regular (a head that small at the arrows' stroke
clogs). Inter has only ↺ ↻ ↰ ↱ of them, with filled triangles for heads:
redrawn with the pairs' angle heads (the triangles stood out among every
other arrow's), as large as Inter's (TeX's are as large against the
capitals; ↰ ↱ stand on the baseline as TeX's do).

- ↚ ↛ ↮ ⇍ ⇏ ⇎: ← → ↔ ⇐ ⇒ ⇔ crossed by ≠'s slash in their middle, passing
  the shafts as far as it passes ='s bars (the negations' rule:
  build/negated_glyphs.py): about as tall as the head, as TeX's; ↚ ↛ ↮ with
  the pairs' small heads, light (TeX's are 0.37 em tall to its →'s 0.52,
  its ⇍ ⇏ ⇎ as tall as ⇐ ⇒ ⇔), the slash as light;
- ↾ ↿ ⇂ ⇃: ⇀ ⇁ turned upright and down, their shaft where ↑'s is; ⇋: ⇌
  mirrored;
- ⇉ ⇇ ⇄ ⇆ ⇈ ⇊: two arrows, their heads PAIR as large as the arrows' (the
  pair as tall as TeX's), their inner barbs meeting between the shafts and
  cut level there into one joint, as TeX's merge, the lower arrow the upper
  one's mirror so that both cuts are one (⇄ ⇆ keep their barbs: each meets
  the other's tail, not its head). Crowded, they are as light as
  Inter's rings past Regular (symbol_glyphs.ring_light, as ⊕ ⋈): smaller
  heads at Black's stroke clog (and need weights far past Black);
- ⇛ ⇚: three shafts at ='s gap (as ≡'s bars) into a head large enough to
  hold them (as the double arrows' grow: build/operators.py): the arrow's
  head alone, drawn larger at the weight that keeps its stroke, the outer
  shafts ending in its barbs, the middle one in its point;
- ↠ ↞: → with its head again behind it, as far back as Inter's » sets its
  second chevron behind the first (for the heads' height);
- ↣ ↢: → with its head again at its tail, a chevron (the head's stub, where
  its shaft flared into the barbs, folded into the notch's point: kept, it
  stuck out into the notch), the shaft starting at its point as it ends in
  the head; a fletching, as TeX's;
- ⇢ ⇠: → drawn out as long as TeX's dashed arrow is against its arrow
  (DASHED), its shaft in DASHES dashes, their gaps GAP of a dash;
- ⇝ ↭: a zigzag at the shaft's stroke, its legs parallel to the head's
  barbs and its turns mitered, then straight into the head, as TeX's: ⇝ as
  long as →, three runs of zigzag (crest to trough) and SQUIG_STRAIGHT runs
  straight; ↭ SQUIG_BOTH times ↔, five runs between SQUIG_BOTH_STRAIGHT runs
  straight at each end;
- ↶ ↷: half a ring of Inter's ○ (its arcs, as ∡'s: build/shape_glyphs.py)
  at the shaft's stroke, the arrows' head at its end pointing down, as TeX's;
- ↫ ↬: ← run on into a loop, as TeX's: the shaft is the bottom of Inter's
  ρ's bowl (drawn straight from where it runs level back to the stem), which
  curls up round to the stem, down through the shaft; as tall against the
  x-height as TeX's loop (LOOP), at the shaft's stroke measured on its
  bowl's side (TeX's loop is a ρ);
- ↺ ↻: Inter's ring (as tall as the capitals) at the shaft's stroke, from its
  left end (cut level) round to its top, where the head goes on, centred on
  the curve it ends (its axis the chord of the stretch that leads into it);
- ↰ ↱: Inter's L, its stem on the baseline and its bar off the stem's top,
  at the shaft's stroke, into the head where Inter's triangle pointed.

The small-headed ones (SMALL_HEADED) have alternates with triangles for
heads, Inter's own small arrows' (↰ ↺: filled, a right angle at the tip),
reached through the `ss01` stylistic set (setMathFont's arrowHeads:
"triangle"; build.py adds the feature): each triangle as tall against the
angle head it stands for as Inter's ↰'s is against the pairs' heads
(TRIANGLE), its tip where the head's was, the shafts running into it a third
of the way to the tip (as Inter's ↰'s bar runs into its triangle); ↣'s
fletching stays a chevron (a tail, not a head).
"""

import math

from arrow_glyphs import flipped, harpoon, reversed_in_place, turned_up
from geometry_glyphs import slash as negation_slash
from negated_glyphs import crossed
from operators import (
    ARROW_HEAD, OFFSET, arrow, arrow_growth, bar_stroke, barb_reach, case, column, drawn_out, even_bars, gap,
    math_axis, sign,
)
from shape_glyphs import meets
from symbol_glyphs import ring_light
from variable import Masters, NewGlyph, Shape

CASED = ["arrowright", "arrowleft", "arrowboth", "arrowdblright", "arrowdblleft", "arrowdblboth", "arrowup", "arrowdown",
         "uni27F5", "uni27F6", "uni27F7", "uni27F8", "uni27F9", "uni27FA", "minus", "plus", "equal", "notequal",
         "less", "lessequal"]
# ⇝ ↭ as TeX's (KaTeX_AMS, measured on their strokes' middles, in runs: a crest to the next trough, across): ⇝'s
# straight shaft from its zigzag into its head's junction; ↭'s length over ↔'s (1274 to 889) and its straight shafts
SQUIG_STRAIGHT = 218 / 184
SQUIG_BOTH = 1274 / 889
SQUIG_BOTH_STRAIGHT = 133 / 163.5
SOURCES = [*CASED, "circlewhite", "uni25EF", "rho", "x", "guillemotright", "uni21BA", "uni21BB", "uni21B0", "uni21B1", "one"]
# Inter's own, as it draws them (AMS symbols the build keeps from Inter: build.py): none left
KEPT: set[int] = set()
# the triangle heads (ss01): as tall against the angle head they stand for as Inter's ↰'s triangle is against the
# pairs' heads at Regular (873 to 944)
TRIANGLE = 873 / 944
# the arrows with small heads, which have triangle alternates
SMALL_HEADED = [0x219A, 0x219B, 0x21AE, 0x21C9, 0x21C7, 0x21C4, 0x21C6, 0x21C8, 0x21CA, 0x21A0, 0x219E, 0x21A3, 0x21A2,
                0x21E2, 0x21E0, 0x21DD, 0x21AD, 0x21B6, 0x21B7, 0x21AB, 0x21AC, 0x21BA, 0x21BB, 0x21B0, 0x21B1]
# how far past the axis a joined pair's barbs reach into each other (units): cut on it, the joint showed a seam
JOINT = 2
# the paired arrows' heads against the arrows' (Inter's): TeX's ⇉'s are 0.64 of its →'s, and the pair is then as tall
# as TeX's, 0.67 em (0.8 of arrows' heads 0.8 of Inter's until review 1)
PAIR = 0.64
# TeX's dashed arrow against its arrow (⇢: 1.34 times as long as →), in DASHES dashes, their gaps GAP of a dash
DASHED = 1.34
DASHES = 3
GAP = 2 / 3
# TeX's loop (↫) against its x-height: 0.325 to 0.431
LOOP = 0.325 / 0.431
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x219A: ("← with ⇉'s head, crossed by ≠'s slash", "arrowleft notequal"),
    0x219B: ("→ with ⇉'s head, crossed by ≠'s slash", "arrowright notequal"),
    0x21AE: ("↔ with ⇉'s heads, crossed by ≠'s slash", "arrowboth notequal"),
    0x21CD: ("⇐ crossed by ≠'s slash", "arrowdblleft notequal"),
    0x21CF: ("⇒ crossed by ≠'s slash", "arrowdblright notequal"),
    0x21CE: ("⇔ crossed by ≠'s slash", "arrowdblboth notequal"),
    0x21BF: ("⇀ turned upright", "arrowright"),
    0x21BE: ("⇁ turned upright", "arrowright"),
    0x21C3: ("↿ upside down", "arrowright"),
    0x21C2: ("↾ upside down", "arrowright"),
    0x21CB: ("⇌ mirrored", "arrowright"),
    0x21C9: ("two →, their heads smaller, their inner barbs joined", "arrowright"),
    0x21C7: ("⇉ mirrored", "arrowright"),
    0x21C4: ("→ over ←, their heads smaller", "arrowright arrowleft"),
    0x21C6: ("← over →, their heads smaller", "arrowright arrowleft"),
    0x21C8: ("two ↑, their heads smaller, their inner barbs joined", "arrowup"),
    0x21CA: ("⇈ upside down", "arrowup"),
    0x21DB: ("⇒ with a third shaft", "arrowdblright"),
    0x21DA: ("⇛ mirrored", "arrowdblright"),
    0x21A0: ("→ with ⇉'s heads, the head again behind it, as » repeats ›", "arrowright guillemotright"),
    0x219E: ("↠ mirrored", "arrowright guillemotright"),
    0x21A3: ("→ with ⇉'s head, again at its tail", "arrowright"),
    0x21A2: ("↣ mirrored", "arrowright"),
    0x21E2: ("→ with ⇉'s head, drawn out, its shaft in dashes", "arrowright"),
    0x21E0: ("⇢ mirrored", "arrowright"),
    0x21DD: ("a zigzag, its legs parallel to ⇉'s head's barbs, then straight into that head", "arrowright"),
    0x21AD: ("⇝'s zigzag between ⇉'s heads, longer than ↔ as TeX's", "arrowright arrowboth"),
    0x21B6: ("half a ring of ○, ⇉'s head at its end", "circlewhite arrowright"),
    0x21B7: ("↶ mirrored", "circlewhite arrowright"),
    0x21AB: ("← with ⇉'s head, its shaft run on as ρ's bowl's bottom, up round the bowl to ρ's stem", "arrowleft rho"),
    0x21AC: ("↫ mirrored", "arrowleft rho"),
    0x21BA: ("Inter's ↺ with ⇉'s head, its ring at the shaft's stroke", "uni21BA arrowright circlewhite"),
    0x21BB: ("↺ mirrored", "uni21BB arrowright circlewhite"),
    0x21B0: ("Inter's ↰ with ⇉'s head, at the shaft's stroke", "uni21B0 arrowleft"),
    0x21B1: ("↰ mirrored", "uni21B1 arrowright"),
}


def ring_stroke(centre: tuple[float, float], radius: float, stroke: float, a0: float, a1: float,
                cut: tuple[tuple[float, float], tuple[float, float]] | None = None) -> Shape:
    """
    A stroke along a circle (`radius` its middle line's) from angle a0 to a1
    (degrees, anticlockwise), its ends cut along the radius, or the end at a1
    along the line `cut` (a head's neck): drawn as Inter's ○ is, in quadratic
    arcs of at most 22.5°, their off-curve points on the bisector, 1/cos(half
    the arc) out.
    """
    steps = math.ceil((a1 - a0) / 22.5 - 1e-9)
    cx, cy = centre

    def end(r: float) -> float:
        if cut is None:
            return a1
        a = meets(centre, r, cut, a1)
        return a + 360 * round((a1 - a) / 360)

    def side(r: float) -> tuple[list, list]:
        b1 = end(r)
        half = math.radians((b1 - a0) / steps / 2)
        pts, on = [], []
        for i in range(steps + 1):
            a = math.radians(a0 + (b1 - a0) * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            on.append(True)
            if i < steps:
                b = a + half
                pts.append((cx + r / math.cos(half) * math.cos(b), cy + r / math.cos(half) * math.sin(b)))
                on.append(False)
        return pts, on

    # clockwise: the outer side back from a1 to a0, the inner one from a0 to a1
    outer, inner = side(radius + stroke / 2), side(radius - stroke / 2)
    return Shape(outer[0][::-1] + inner[0], outer[1][::-1] + inner[1], [2 * len(outer[0]) - 1], 0)


def triangle(m: Masters, location: dict, height: float) -> Shape:
    """
    Inter's small arrows' head (↰'s filled triangle, its tip's angle as Inter
    draws it) pointing right, `height` tall, its tip at (0, 0); its base's
    corners doubled, so that it can be cut level (a pair's heads are).
    """
    x0, y0, x1, y1 = min(m.shape("uni21B0", location).contours(), key=lambda c: c.bounds()[0]).bounds()
    depth, h = (x1 - x0) / (y1 - y0) * height, height / 2
    return Shape([(0, 0), (-depth, -h), (-depth, -h), (-depth, h), (-depth, h)], [True] * 5, [4], 0)


def triangled(arrow_: Shape, tri: Shape) -> Shape:
    """
    A straight horizontal arrow (one head or two, its shafts straight) with
    triangles for heads: each triangle's tip where the head's was, each shaft
    (a band across the arrow just inside its tail, or across its middle when
    it has two heads: a short arrow's middle crosses its barbs) from the tail
    into the triangles, a third of the way to the tip, or as far back as
    keeps it inside.
    """
    x0, _, x1, _ = arrow_.bounds()
    depth = -min(x for x, _ in tri.points)
    half = max(y for _, y in tri.points)
    parts, heads = [], {}
    for way, end in ((1, x1), (-1, x0)):
        tips = [p for p in arrow_.points if abs(p[0] - end) < 0.5]
        if len(tips) == 1:
            t = tri if way > 0 else Shape([(-x, y) for x, y in reversed(tri.points)], list(reversed(tri.on)), list(tri.ends), 0)
            parts.append(t.moved(end, tips[0][1]))
            heads[way] = tips[0]
    across = (x0 + x1) / 2 if len(heads) == 2 else x0 + 1 if 1 in heads else x1 - 1
    ys = column(arrow_, across)
    bands = list(zip(ys[::2], ys[1::2]))
    for a, b in bands:
        ends = []
        for way, end in ((-1, x0), (1, x1)):
            if way in heads:
                reach = max(abs(a - heads[way][1]), abs(b - heads[way][1]))
                into = min(depth, max(depth * 2 / 3, depth * reach / half + 1))
                ends.append(end - way * into)
            else:
                ends.append(end)
        parts.append(Shape.polygon([(ends[0], a), (ends[0], b), (ends[1], b), (ends[1], a)]))
    return Shape.join(parts, arrow_.advance)


def polyline(points: list[tuple[float, float]], thick: float) -> Shape:
    """A stroke along straight segments through `points`, `thick` across, its turns mitered and its ends cut square."""
    h = thick / 2

    def normal(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        return -dy / n, dx / n

    left, right = [], []
    for i, p in enumerate(points):
        if 0 < i < len(points) - 1:
            n1, n2 = normal(points[i - 1], p), normal(p, points[i + 1])
            bx, by = n1[0] + n2[0], n1[1] + n2[1]
            b = math.hypot(bx, by)
            nx, ny = bx / b, by / b
            k = 1 / (nx * n1[0] + ny * n1[1])
        else:
            nx, ny = normal(points[0], points[1]) if i == 0 else normal(points[-2], points[-1])
            k = 1.0
        left.append((p[0] + nx * h * k, p[1] + ny * h * k))
        right.append((p[0] - nx * h * k, p[1] - ny * h * k))
    pts = left + right[::-1]
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return Shape.polygon(pts if area < 0 else pts[::-1])


def rho_parts(rho: Shape) -> tuple[Shape, Shape, int, int]:
    """
    ρ's outline (up its stem's left edge, over the bowl, down to its bottom,
    back to the stem and down its right edge) and its counter; on the outline,
    the bowl's lowest point and the stem's foot on its right.
    """
    outer, inner = sorted(rho.contours(), key=lambda c: c.bounds()[1])
    p, on = outer.points, outer.on
    foot_y = min(y for _, y in p)
    foot = max((i for i in range(len(p)) if on[i] and p[i][1] == foot_y), key=lambda i: p[i][0])
    bottom = min((i for i in range(len(p)) if on[i] and p[i][0] > p[foot][0] + 1), key=lambda i: p[i][1])
    assert bottom < foot, "ρ's outline runs otherwise"
    return outer, inner, bottom, foot


def bowl_floor(rho: Shape) -> tuple[float, float]:
    """Where ρ's bowl's bottom runs level: its outer edge's height and its counter's."""
    outer, inner, bottom, _ = rho_parts(rho)
    return outer.points[bottom][1], min(y for (_, y), on in zip(inner.points, inner.on) if on)


def looped(rho: Shape) -> Shape:
    """
    ρ with its bowl's bottom drawn straight from where it runs level (outside
    and in) back to its stem, instead of curving round to it: a loop for a
    shaft to run into, the shaft its bottom, as TeX's ↫'s (its counter square
    where the shaft meets the stem).
    """
    outer, inner, bottom, foot = rho_parts(rho)
    p, on = outer.points, outer.on
    out = Shape([*p[: bottom + 1], (p[foot][0], p[bottom][1]), *p[foot:]], [*on[: bottom + 1], True, *on[foot:]], [0], 0)
    out.ends = [len(out.points) - 1]
    # the counter from its lowest point round its right side and top to its leftmost, then straight down and back
    q, qon = inner.points, inner.on
    low = min((i for i in range(len(q)) if qon[i]), key=lambda i: q[i][1])
    q, qon = q[low:] + q[:low], qon[low:] + qon[:low]
    left = min((i for i in range(len(q)) if qon[i]), key=lambda i: q[i][0])
    counter = Shape([*q[: left + 1], (q[left][0], q[0][1])], [*qon[: left + 1], True], [left + 1], 0)
    return Shape.join([out, counter], rho.advance)


def on_ring(head_: Shape, neck: tuple[float, float], centre: tuple[float, float], radius: float, angle: float,
            tangent: bool = False) -> tuple[Shape, tuple]:
    """
    A right-pointing head (the middle of its neck at `neck`) at the end of a
    ring that runs anticlockwise to `angle` (degrees): centred on the curve it
    ends, its axis the chord of the stretch of ring that leads into it, as
    long as the head (off the tangent by half the arc it spans, outwards:
    along the tangent its tip left the curve, and turned inwards, the way the
    ring goes on, it looked turned the wrong way); or along the tangent (↶'s,
    TeX's pointing straight down). Also the line its neck lies on, for the
    ring's end to be cut along.
    """
    length = max(x for x, _ in head_.points) - neck[0]
    off = 0.0 if tangent else math.degrees(math.asin(min(1.0, length / (2 * radius))))
    way = math.radians(angle + 90 - off)
    ca, sa = math.cos(way), math.sin(way)
    a = math.radians(angle)
    ex, ey = centre[0] + radius * math.cos(a), centre[1] + radius * math.sin(a)
    placed = head_.map(lambda x, y: (ex + (x - neck[0]) * ca - (y - neck[1]) * sa, ey + (x - neck[0]) * sa + (y - neck[1]) * ca))
    return placed, ((ex, ey), (ex - sa, ey + ca))


def shaft_of(arrow_: Shape) -> tuple[float, float, float]:
    """A right-pointing arrow's tail x, and its shaft's edges (bottom, top)."""
    x0 = arrow_.bounds()[0]
    tail = sorted(y for x, y in arrow_.points if abs(x - x0) < 0.5)
    return x0, tail[0], tail[-1]


def junction(arrow_: Shape) -> float:
    """Where a right-pointing arrow's shaft runs straight to (its edges' last on-curve points before the head)."""
    _, s0, s1 = shaft_of(arrow_)
    return max(x for (x, y), on in zip(arrow_.points, arrow_.on) if on and (abs(y - s0) < 0.5 or abs(y - s1) < 0.5))


def tail_to(arrow_: Shape, x: float) -> Shape:
    """A right-pointing arrow with its tail moved to x (its shaft shortened, or folded into the head)."""
    x0 = arrow_.bounds()[0]
    return arrow_.map(lambda px, py: (x if abs(px - x0) < 0.5 else px, py))


def chevron(arrow_: Shape) -> Shape:
    """
    A right-pointing arrow's head alone, as a chevron: its shaft folded to
    where it runs straight to (tail_to), then what is left of it there (the
    stub where its edges flare into the barbs) folded into the notch's
    point, and the barbs' inner edges straight into that point, each along
    its barb.
    """
    joint = junction(arrow_)
    head_ = tail_to(arrow_, joint)
    _, s0, s1 = shaft_of(arrow_)
    tip_x, mid = arrow_.bounds()[2], (s0 + s1) / 2
    pts, n = list(head_.points), len(head_.points)
    inside = [i for i, (x, y) in enumerate(pts) if s0 < y < s1 and x < tip_x - 1]
    low = max((i for i in inside if pts[i][1] < mid), key=lambda i: pts[i][0])
    high = max((i for i in inside if pts[i][1] > mid), key=lambda i: pts[i][0])
    # the stub: the points between the notch's two corners, the way that passes the folded shaft
    forward = [(low + k) % n for k in range(1, (high - low) % n)]
    folded = {i for i, (x, _) in enumerate(pts) if abs(x - joint) < 0.5}
    run = forward if folded & set(forward) else [(high + k) % n for k in range(1, (low - high) % n)]
    # the barbs' inner edges straight into one point on the axis (Inter's curve them into the shaft: alone, they
    # bent the barbs): each from its end's inner corner, along the barb
    tip = max(range(n), key=lambda i: pts[i][0])
    by_height = sorted(range(n), key=lambda i: pts[i][1])
    lines = []
    for outer_i, inner_i, corner in ((by_height[0], by_height[1], low), (by_height[-1], by_height[-2], high)):
        (ox, oy), (ix, iy), (tx, ty) = pts[outer_i], pts[inner_i], pts[tip]
        slope = (tx - ox) / (ty - oy)
        ahead = [(inner_i + k) % n for k in range(1, (corner - inner_i) % n + 1)]
        edge = ahead if tip not in ahead else [(inner_i - k) % n for k in range(1, (inner_i - corner) % n + 1)]
        lines.append((ix, iy, slope, edge))
    point = (lines[0][0] + (mid - lines[0][1]) * lines[0][2], mid)
    for ix, iy, slope, edge in lines:
        for i in edge:
            pts[i] = (ix + (pts[i][1] - iy) * slope, pts[i][1])
    pts[low] = pts[high] = point
    for i in run:
        pts[i] = point
    return Shape(pts, list(head_.on), list(head_.ends), head_.advance)


def clipped(shape: Shape, cut: float, above: bool) -> Shape:
    """
    Its outline cut level at height `cut`, keeping what lies above it (or
    under): each run of points on the other side moved onto the cut where the
    outline leaves the kept side and where it comes back (straight edges:
    barbs), the first half of the run to one, the rest to the other.
    """
    out = []
    for c in shape.contours():
        pts, on, n = list(c.points), c.on, len(c.points)
        gone = [(y < cut) if above else (y > cut) for _, y in pts]
        if not any(gone) or all(gone):
            out.append(c)
            continue
        first = next(i for i in range(n) if not gone[i])
        k = (first + 1) % n
        while k != first:
            if not gone[k]:
                k = (k + 1) % n
                continue
            run = []
            while gone[k]:
                run.append(k)
                k = (k + 1) % n

            def meet(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
                t = (cut - a[1]) / (b[1] - a[1])
                return (a[0] + (b[0] - a[0]) * t, cut)

            before, after = pts[(run[0] - 1) % n], pts[k]
            enter, leave = meet(before, pts[run[0]]), meet(after, pts[run[-1]])
            # a neighbour on the cut already ends the cut there: the run all goes to the other end (one point
            # moved to its own end left the barb a wedge)
            on_before, on_after = abs(before[1] - cut) < 0.5, abs(after[1] - cut) < 0.5
            for j, i in enumerate(run):
                pts[i] = leave if on_before and not on_after else enter if on_after and not on_before else (
                    enter if j < (len(run) + 1) // 2 else leave)
        out.append(Shape(pts, list(on), list(c.ends), c.advance))
    return Shape.join(out, shape.advance)


def pair(top: Shape, bottom: Shape, pitch: float, axis: float, joined: bool) -> Shape:
    """
    Two horizontal arrows `pitch` apart about the axis. Joined (the same
    arrow twice, their inner barbs meeting there): the upper one's barb cut
    level a little under the axis (JOINT), the lower one its mirror in it,
    so that the two cuts are one and overlap (cut each on its own, the lower
    one's barb ended in a wedge).
    """
    upper, lower = top.moved(0, pitch / 2), bottom.moved(0, -pitch / 2)
    if joined:
        upper = clipped(upper, axis - JOINT, above=True)
        lower = flipped(upper, axis)
    return Shape.join([upper, lower], top.advance)


def respaced(shape: Shape, like: Shape) -> Shape:
    """Ink with `like`'s side bearings."""
    lx0, _, lx1, _ = like.bounds()
    x0, _, x1, _ = shape.bounds()
    out = shape.moved(lx0 - x0, 0)
    out.advance = (x1 - x0) + lx0 + like.advance - lx1
    return out


def lightened(m: Masters, master: dict, k: float) -> dict:
    """The location (the master's optical size) whose minus sign is k times as thick as at the master."""
    thick = lambda w: (lambda b: b[3] - b[1])(m.shape(case(m, "minus"), {**master, "wght": w}).bounds())  # noqa: E731
    return {**master, "wght": m.weight_for(thick, k * thick(master["wght"]))}


def ams_arrow_shapes(m: Masters, master: dict, triangles: bool = False) -> dict[int, Shape]:
    """The family at a master: code point → shape; with `triangles`, the small-headed ones with triangle heads."""
    shapes: dict[int, Shape] = {}
    axis = math_axis(m, master)
    right, left = even_bars(m, "arrowright", master), even_bars(m, "arrowleft", master)
    both = even_bars(m, "arrowboth", master)
    dright, dleft, dboth = (even_bars(m, n, master) for n in ("arrowdblright", "arrowdblleft", "arrowdblboth"))
    up = even_bars(m, "arrowup", master)
    x0, s0, s1 = shaft_of(right)
    t = s1 - s0
    # the arrows TeX draws only in its AMS font (↠ ↣ ⇢ ⇝ ↭ ↶ ↫) are drawn as the pairs are: their heads PAIR of an
    # arrow's (TeX's are 0.334 em tall to its →'s 0.522, as its ⇉'s), and as light as the rings past Regular (a head
    # that small at the arrows' stroke clogged from 600 up); their shafts, waves, rings and loops as light
    light = lightened(m, master, ring_light(m, master))
    small_right = arrow(m, "arrowright", light, ARROW_HEAD * PAIR)
    small_left = arrow(m, "arrowleft", light, ARROW_HEAD * PAIR)
    lx0, ls0, ls1 = shaft_of(small_right)
    lt = ls1 - ls0
    # the triangle heads (ss01), and an arrow with them
    _, hy0, _, hy1 = small_right.bounds()
    tri = triangle(m, light, TRIANGLE * (hy1 - hy0))
    tri_depth = -min(x for x, _ in tri.points)

    def headed(a: Shape) -> Shape:
        return triangled(a, tri) if triangles else a

    # ↚ ↛ ↮ ⇍ ⇏ ⇎: ≠'s slash in the middle, passing the shafts there as it passes ='s bars; ↚ ↛ ↮ with the pairs'
    # heads, light, their slash as light (TeX's have its small heads; its ⇍ ⇏ ⇎ are as large as ⇐ ⇒ ⇔)
    small_both = arrow(m, "arrowboth", light, ARROW_HEAD * PAIR)
    slash, past = negation_slash(m, master)
    light_slash, light_past = negation_slash(m, light)
    for cp, base in {0x219A: headed(small_left), 0x219B: headed(small_right), 0x21AE: headed(small_both), 0x21CD: dleft,
                     0x21CF: dright, 0x21CE: dboth}.items():
        bx0, _, bx1, _ = base.bounds()
        cx = (bx0 + bx1) / 2
        edges = column(base, cx)
        cut, by = (light_slash, light_past) if cp in (0x219A, 0x219B, 0x21AE) else (slash, past)
        shapes[cp] = crossed(base, cut, edges[-1] - edges[0] + 2 * by, (cx, (edges[0] + edges[-1]) / 2))
        if cp in (0x219A, 0x219B, 0x21AE):
            # the side bearings of the arrow it negates
            shapes[cp] = respaced(shapes[cp], {0x219A: left, 0x219B: right, 0x21AE: both}[cp])

    # ↿ ↾ ⇃ ⇂: ⇀ ⇁ turned upright (their barb then on the left, on the right), the shaft where ↑'s is
    up_harpoon = harpoon(right)
    down_harpoon = flipped(up_harpoon, (s0 + s1) / 2)
    ux0, _, ux1, _ = up.bounds()
    stem = (ux0 + ux1) / 2

    def stood(h: Shape) -> Shape:
        out = turned_up(h, (0, axis))
        # the shaft's middle (on the axis before the turn) to ↑'s
        shaft_x = -((s0 + s1) / 2 - (h.bounds()[1] + h.bounds()[3]) / 2)
        out = out.moved(stem - shaft_x, 0)
        out.advance = up.advance
        return out

    shapes[0x21BF], shapes[0x21BE] = stood(up_harpoon), stood(down_harpoon)
    shapes[0x21C3], shapes[0x21C2] = flipped(shapes[0x21BF], axis), flipped(shapes[0x21BE], axis)
    # ⇋: ⇌ (⇀ over ↽, their shafts ='s pitch apart: build/arrow_glyphs.py) mirrored
    pitch = gap(m, master) + t
    harpoons = Shape.join([up_harpoon.moved(0, pitch / 2), reversed_in_place(down_harpoon).moved(0, -pitch / 2)], right.advance)
    shapes[0x21CB] = harpoons.mirrored()

    # ⇉ ⇇ ⇄ ⇆: two arrows with smaller heads, the inner barbs meeting on the axis (overlapping by a barb's end, cut level)
    small = arrow(m, "arrowright", lightened(m, master, ring_light(m, master)), ARROW_HEAD * PAIR)
    _, y0, _, y1 = small.bounds()
    reach = (y1 - y0) / 2
    # a barb's end: its two lowest points (the end is cut across the barb)
    lows = sorted(y for _, y in small.points)
    overlap = lows[1] - lows[0]
    apart = 2 * reach - 2 * overlap
    small = headed(small)
    shapes[0x21C9] = pair(small, small, apart, axis, joined=True)
    shapes[0x21C7] = shapes[0x21C9].mirrored()
    # each over the same ink as the other (mirrored within the advance, ← sat 54 units left of →)
    shapes[0x21C4] = pair(small, reversed_in_place(small), apart, axis, joined=False)
    shapes[0x21C6] = pair(reversed_in_place(small), small, apart, axis, joined=False)
    # ⇈ ⇊: the same pair turned upright, on the axis, ↑'s side bearings around them
    upup = turned_up(shapes[0x21C9], (0, axis))
    vx0, _, vx1, _ = upup.bounds()
    upup = upup.moved(ux0 - vx0, 0)
    upup.advance = (vx1 - vx0) + ux0 + up.advance - ux1
    shapes[0x21C8] = upup
    shapes[0x21CA] = flipped(upup, axis)

    # ⇛ ⇚: three shafts at ='s gap (as ≡'s bars, ⇒'s thick) into the arrow's head, larger to hold them (as
    # build/operators.py grows the double arrows' heads): the outer shafts end in the barbs, the middle one in the point
    bar = bar_stroke(m.shape(case(m, "arrowdblright"), master))
    pitch3 = gap(m, master) + bar
    head = ARROW_HEAD * max(1.0, 1.35 * (pitch3 + bar) / barb_reach(arrow(m, "arrowright", master)))
    big = arrow(m, "arrowright", master, head)
    bx0 = big.bounds()[0]
    tip = max(big.points, key=lambda p: p[0])
    lows = sorted(big.points, key=lambda p: p[1])[:2]
    end_mid = ((lows[0][0] + lows[1][0]) / 2, (lows[0][1] + lows[1][1]) / 2)
    joint3 = junction(big)
    # the head alone, its neck (where the shaft entered) as thick as the shafts
    _, n0, n1 = shaft_of(big)
    head_only = tail_to(big, joint3).map(
        lambda x, y: (x, axis - bar / 2 if abs(y - n0) < 0.5 else axis + bar / 2 if abs(y - n1) < 0.5 else y))

    def shaft(y: float, to: float) -> Shape:
        return Shape.polygon([(bx0, y - bar / 2), (bx0, y + bar / 2), (to, y + bar / 2), (to, y - bar / 2)])

    # the outer shafts end on the barbs' middle lines (along the outer edge, through the middle of the end), the
    # middle one in the point, where the barbs' inner edges meet (the upper barb is the lower one's mirror)
    slope = (tip[0] - lows[0][0]) / (tip[1] - lows[0][1])
    outer_end = end_mid[0] + (axis - pitch3 - end_mid[1]) * slope
    point = max(x for (x, y), on in zip(head_only.points, head_only.on) if on and abs(y - axis) < bar and x < tip[0] - 1)
    triple = Shape.join([head_only, shaft(axis, point), shaft(axis + pitch3, outer_end), shaft(axis - pitch3, outer_end)], big.advance)
    shapes[0x21DB] = triple
    shapes[0x21DA] = triple.mirrored()

    # ↠ ↞: the head again behind it, as far as » sets its second chevron behind the first, for the heads' height
    guillemets = m.shape("guillemotright", master)
    first_, second_ = sorted(guillemets.contours(), key=lambda c: c.bounds()[0])
    behind = (second_.bounds()[0] - first_.bounds()[0]) / (first_.bounds()[3] - first_.bounds()[1])
    s = sign(m, "arrowright", light, ARROW_HEAD * PAIR)
    grow = arrow_growth(m, "arrowright", light, s)
    _, ry0, _, ry1 = small_right.bounds()
    back = behind * (ry1 - ry0)
    long_ = drawn_out(s, (1, 0), grow)
    if triangles:
        tip_ = max(long_.points, key=lambda p: p[0])
        shapes[0x21A0] = Shape.join([triangled(long_, tri), tri.moved(tip_[0] - back, tip_[1])], right.advance)
    else:
        shapes[0x21A0] = Shape.join([long_, drawn_out(s, (1, 0), grow - back)], right.advance)
    shapes[0x219E] = shapes[0x21A0].mirrored()

    # ↣ ↢: the head again at the tail, as a chevron (its stub, kept, stuck out into the notch), the shaft starting at
    # its point as it ends in the head
    joint = junction(small_right)
    fletching = chevron(small_right)
    tip_x = small_right.bounds()[2]
    notch = max(x for x, y in fletching.points if ls0 < y < ls1 and x < tip_x - 1)
    shapes[0x21A3] = respaced(Shape.join([headed(tail_to(small_right, lx0 + notch - joint)), fletching.moved(lx0 - joint, 0)], right.advance), right)
    shapes[0x21A2] = shapes[0x21A3].mirrored()

    # ⇢ ⇠: drawn out as long as TeX's, the shaft in dashes (the last one in the head)
    rx0, _, rx1, _ = small_right.bounds()
    dashed = drawn_out(small_right, (1, 0), (DASHED - 1) * (rx1 - rx0))
    joint = junction(dashed)
    dash = (joint - lx0) / (DASHES + (DASHES - 1) * GAP)
    pieces = [headed(tail_to(dashed, joint - dash))]
    for k in range(DASHES - 1):
        a = lx0 + k * dash * (1 + GAP)
        pieces.append(Shape.polygon([(a, ls0), (a, ls1), (a + dash, ls1), (a + dash, ls0)]))
    shapes[0x21E2] = Shape.join(pieces, dashed.advance)
    shapes[0x21E0] = shapes[0x21E2].mirrored()

    # the pairs' head alone (its shaft folded to where it runs straight to), as → points; or the triangle, its neck
    # (where a stroke ends in it) half a shaft into it
    joint = junction(small_right)
    head = tail_to(small_right, joint)
    tip_x = small_right.bounds()[2]
    mid = (ls0 + ls1) / 2
    end_head, neck = (tri, (-tri_depth + lt / 2, 0)) if triangles else (head, (joint, mid))

    # ⇝ ↭: a zigzag at the shaft's stroke, its legs parallel to the head's barbs (TeX's ↭'s are at their 45°) and its
    # turns mitered, from the axis up to a crest, a run down to a trough and so on back to the axis, then straight
    # into the head (its stroke half a shaft into it, so that no seam shows), as TeX's: ⇝ as long as → (TeX's are),
    # three runs of zigzag then SQUIG_STRAIGHT runs straight; ↭ SQUIG_BOTH times as long as ↔, five runs between
    # SQUIG_BOTH_STRAIGHT runs straight at each end
    _, _, sx1, _ = small_right.bounds()
    reach = sx1 - joint
    barb_tip = max(small_right.points, key=lambda p: p[0])
    barb_top = max(small_right.points, key=lambda p: p[1])
    slope = (barb_top[1] - barb_tip[1]) / (barb_tip[0] - barb_top[0])
    level = axis

    def zigzag(runs: int, run: float) -> list[tuple[float, float]]:
        half = run * slope / 2
        turns = [(run / 2 + k * run, level + (half if k % 2 == 0 else -half)) for k in range(runs)]
        return [(0.0, level), *turns, (runs * run, level)]

    rx0, _, rx1, _ = right.bounds()
    # the square-cut start reaches left of its point by the stroke's half across a leg
    lead_in = lt / 2 * slope / math.hypot(1, slope)
    run = (rx1 - rx0 - lead_in - reach) / (3 + SQUIG_STRAIGHT)
    on = (3 + SQUIG_STRAIGHT) * run
    wave = polyline([*zigzag(3, run), (on + lt / 2, level)], lt)
    right_head = head.moved(on - joint, level - mid)
    bx0, _, bx1, _ = both.bounds()
    run = (SQUIG_BOTH * (bx1 - bx0) - 2 * reach) / (5 + 2 * SQUIG_BOTH_STRAIGHT)
    straight = SQUIG_BOTH_STRAIGHT * run
    both_wave = polyline([(-straight - lt / 2, level), *zigzag(5, run), (5 * run + straight + lt / 2, level)], lt)
    both_right = head.moved(5 * run + straight - joint, level - mid)
    left_head = head.mirrored()
    left_head = left_head.moved(-straight - (left_head.advance - joint), level - mid)
    if triangles:
        # their tips where the heads' are
        def tip(h: Shape, way: int) -> tuple[float, float]:
            return max(h.points, key=lambda p: way * p[0])

        right_head, both_right = tri.moved(*tip(right_head, 1)), tri.moved(*tip(both_right, 1))
        left_head = Shape([(-x, y) for x, y in reversed(tri.points)], list(reversed(tri.on)), list(tri.ends), 0).moved(*tip(left_head, -1))
    shapes[0x21DD] = respaced(Shape.join([wave, right_head], 0), right)
    shapes[0x21AD] = respaced(Shape.join([left_head, both_wave, both_right], 0), both)

    # ↶ ↷: half a ring (Inter's ○'s arcs) at the shaft's stroke, the head on at its left end pointing down (TeX's):
    # as wide as →, standing on its point, its ink centred on the axis
    _, hy0, _, hy1 = small_right.bounds()
    half_head = (hy1 - hy0) / 2
    r = (tip_x - lx0 - half_head - lt / 2) / 2
    cx = r + half_head
    down, cut = on_ring(end_head, neck, (cx, 0), r, 180, tangent=True)
    curve = Shape.join([ring_stroke((cx, 0), r, lt, 0, 180, cut), down], 0).centred(axis)
    shapes[0x21B6] = respaced(curve, right)
    shapes[0x21B7] = shapes[0x21B6].mirrored()

    # ↫ ↬: ← run on into a loop, as TeX's: the shaft is the bottom of Inter's ρ's bowl, drawn straight from where it
    # runs level back to the stem (`looped`), and curls up round the bowl to the stem, down through the shaft; ρ as
    # tall against the x-height as TeX's loop (LOOP), at the weight whose bowl's side is the shaft's stroke (Inter's
    # arrows are monoline: fitted by its bottom, the loop's sides and stem came out a fifth heavier at Black), its
    # bowl's bottom on the shaft's bottom edge (its counter's floor a little under the shaft's top, by Inter's
    # contrast at that weight: past the stem, where it doesn't show); the arrow's own shaft ends in the stem, the
    # loop's ink at the arrow's tail
    rho = m.shape("rho", master)
    floor, _ = bowl_floor(rho)
    x_height = m.shape("x", master).bounds()[3]
    k = LOOP * x_height / (rho.bounds()[3] - floor)
    # its bowl's stroke: its right side, halfway up
    bowl_side = lambda s_: (lambda r: r[-1][1] - r[-1][0])(s_.runs(s_.bounds()[3] / 2))  # noqa: E731
    loop = looped(m.fitted("rho", master, k, lt, bowl_side))
    tail_x = small_left.bounds()[2]
    loop = loop.moved(tail_x - loop.bounds()[2], ls0 - bowl_floor(loop)[0])
    stem_x0 = loop.bounds()[0]
    stem_x1 = min(x for x, y in loop.points if y < ls0 - 1 and x > stem_x0 + 1)
    shaft_ = small_left.map(lambda x, y: ((stem_x0 + stem_x1) / 2 if abs(x - tail_x) < 0.5 else x, y))
    shapes[0x21AB] = respaced(Shape.join([headed(shaft_), loop], 0), left)
    shapes[0x21AC] = shapes[0x21AB].mirrored()

    # ↺ ↻: Inter's ring, as large, at the shaft's stroke, from its left end (cut level) round to its top, where the
    # pairs' head goes on, centred on the curve it ends (on_ring)
    inter_ring = m.shape("uni21BA", master)
    rx0, ry0, rx1, ry1 = max(inter_ring.contours(), key=lambda c: c.bounds()[2] - c.bounds()[0]).bounds()
    centre, radius = ((rx0 + rx1) / 2, (ry0 + ry1) / 2), (rx1 - rx0) / 2 - lt / 2
    round_head, cut = on_ring(end_head, neck, centre, radius, 450)
    shapes[0x21BA] = respaced(Shape.join([ring_stroke(centre, radius, lt, 180, 450, cut), round_head], 0), inter_ring)
    shapes[0x21BB] = shapes[0x21BA].mirrored()

    # ↰ ↱: Inter's L at the shaft's stroke: ← with the pairs' head, its tip where Inter's triangle's is and its shaft
    # on the triangle's middle, drawn on to the stem, which stands on the baseline up to the bar's top
    lsh = m.shape("uni21B0", master)
    inter_head = min(lsh.contours(), key=lambda c: c.bounds()[0])
    tx0, ty0, _, ty1 = inter_head.bounds()
    bar_y, stem_right = (ty0 + ty1) / 2, lsh.bounds()[2]
    to_left = small_left.moved(tx0 - small_left.bounds()[0], bar_y - (ls0 + ls1) / 2)
    tail_end = to_left.bounds()[2]
    to_left = to_left.map(lambda x, y: (stem_right if abs(x - tail_end) < 0.5 else x, y))
    stem_ = Shape.polygon([(stem_right - lt, 0), (stem_right - lt, bar_y + lt / 2), (stem_right, bar_y + lt / 2), (stem_right, 0)])
    shapes[0x21B0] = respaced(Shape.join([headed(to_left), stem_], 0), lsh)
    shapes[0x21B1] = shapes[0x21B0].mirrored()
    return shapes


# KaTeX's pieces of a stretched arrow (\left\uparrow… past the text size, \big\Uparrow: its Size1 font), each PIECE
# tall and standing on the baseline, as its: code point → (the arrow, the part)
ARROW_PIECES = {
    0x2191: ("up", "head"), 0x2193: ("up", "foot"), 0x23D0: ("up", "stem"),
    0x21D1: ("double", "head"), 0x21D3: ("double", "foot"), 0x2016: ("double", "stem"),
}
PIECE = 0.6
PIECES_FROM = {
    0x23D0: ("the shaft of Inter Math's ↑ (KaTeX draws it between the pieces of a stretched arrow, as long as needed)", "arrowup"),
    0x2016: ("the shafts of Inter Math's ⇑ (as ⏐)", "arrowdblright"),
}


def arrow_pieces(path, upem: int) -> list[NewGlyph]:
    """
    The pieces KaTeX stacks a stretched arrow from (its Size1 font): Inter
    Math's ↑ and ⇑ cut level across their shafts PIECE under the point (the
    head, standing on the baseline by its cut), the same turned down (the
    foot), and their shafts PIECE tall (the stem, which KaTeX draws as an
    image between the pieces as long as needed: src/svg.ts). At the text
    optical size whatever the size: the stem image can't follow it.
    """
    m = Masters(path, [*SOURCES, *(f"{n}.case" for n in CASED)])
    text = {master["wght"]: master for master in m.masters if master["opsz"] == m.axes["opsz"].defaultValue}
    h = PIECE * upem
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        master = m.lighter(text[design["wght"]], OFFSET)
        up = even_bars(m, "arrowup", master)
        ux0, uy0, ux1, uy1 = up.bounds()
        # ⇑: ⇒ turned upright where ↑ stands (build/arrow_glyphs.py)
        double = turned_up(even_bars(m, "arrowdblright", master), ((ux0 + ux1) / 2, (uy0 + uy1) / 2))
        double.advance = up.advance
        for cp, (which, part) in ARROW_PIECES.items():
            a = up if which == "up" else double
            _, y0, _, y1 = a.bounds()
            head = clipped(a, y1 - h, above=True).moved(0, h - y1)
            if part == "head":
                s = head
            elif part == "foot":
                s = flipped(head, h / 2)
            else:
                shafts = a.runs(y0 + (y1 - y0) * 0.25)
                s = Shape.join([Shape.polygon([(l, 0), (l, h), (r, h), (r, 0)]) for l, r in shafts], 0)
            s.advance = a.advance
            shapes.setdefault(cp, []).append(s)
    return [m.glyph(f"uni{cp:04X}.size1", s, cp) for cp, s in shapes.items()]


def ams_arrow_glyphs(path, triangles: bool = False) -> list[NewGlyph]:
    """
    The family's glyphs; with `triangles`, the small-headed ones' triangle
    alternates instead (unmapped, named uniXXXX.tri: the ss01 stylistic set
    reaches them).
    """
    m = Masters(path, [*SOURCES, *(f"{n}.case" for n in CASED)])
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in ams_arrow_shapes(m, m.lighter(design, OFFSET), triangles).items():
            if not triangles or cp in SMALL_HEADED:
                shapes.setdefault(cp, []).append(s)
    if triangles:
        return [m.glyph(f"uni{cp:04X}.tri", s) for cp, s in shapes.items()]
    taken = set(m.font.getGlyphOrder())
    return [m.glyph(f"uni{cp:04X}" + (".math" if f"uni{cp:04X}" in taken else ""), s, cp) for cp, s in shapes.items()]
