"""
Blackboard bold (\\mathbb: ℝ ℕ ℤ ℚ ℂ…, and \\Bbbk), from Inter's capitals and k.

KaTeX sets \\mathbb{R} as "R" in its AMS font, whose A-Z are double-struck;
Inter Math's are a font of their own (the CSS sends \\mathbb there). They
are built the way STIX Two's are (sources/stix-two, its Math font from
U+1D538): the strokes a seriffed capital draws thick are hollow, two lines
around a gap, closed at both ends; the others stay single lines. The letters
are Inter's capitals, drawn at the weight whose stem is LINE of the letter's
own (their strokes are the lines: a letter then reads about as heavy as
Inter's at its weight), each thick stroke doubled on its middle: the
original stroke runs down the middle of the hollow one, a line either side
of it (DESIGN):

- stems (B D E F H I K L M P R T): the letter widened across the stem (what
  lies right of its middle moved aside) and a hole cut in it, a bar's
  thickness from its ends (I is Inter Math's, with bars: BASES); U and J:
  the second line beside the stem, down into the curve (drawn out level at
  its lowest), and a bar across the top;
- diagonals (A M N V W Z): the letter widened across the stroke (what lies
  right of its middle moved aside, the stroke's parallel) and a hole cut
  along it; K R: the leg replaced by a line either side of it, from a bar
  across the foot into the arm or bowl it springs from, which is drawn out
  as far as the foot now reaches (the right side aligned as Inter's); X: a
  line either side of its stroke from the top left, bars across the ends,
  the other stroke in two, each ending in a line (the hollow stays empty);
  Y: its left arm and stem, each on its middle, the right arm single (as
  STIX's), the stem's right line centred under the crotch (the junction
  even);
- bowls (C D G O Q): a chord inside the bowl where a seriffed one is thick,
  closing a crescent, and the letter drawn out by half a doubled stroke for
  each (the crescent straddles the curve); B P R's bowls stay single (P's
  eye would close); Q's tail starts in the ring, not among the chords;
- k (\\Bbbk, the one lowercase letter of KaTeX's AMS font): K's stem and leg
  on Inter's k, its leg and arm measured against the x-height where K's are
  against the cap height (TeX's and STIX's are hollow there too);
- S: its arcs drawn out towards their terminals as far as its doubled
  stroke moves each bowl's other side (each bowl widens both ways, the
  letter stays upright), its stroke hollow from the upper arc round to the
  lower one (the spine between), the hole a lens along its middle.
The gap is the same in every letter, measured across the stroke: GAP lines
at the regular weight (STIX's is 75 for a 43 line) and below, narrowing as
the lines grow heavier than the regular weight's (as the square root). The
lines grow no heavier than a bar of Inter's ǁ: its two bars grow less than a
stem, which keeps the white between them open at heavy weights (the gap,
narrowing with the lines, then stays wider too).
"""

import math
from dataclasses import dataclass, replace

from operators import pipe_bars
from variable import Masters, NewGlyph, Shape

# the lines: as thick as this share of Inter's stem at the letter's weight (no
# thinner than Inter's thinnest), so that a letter reads as heavy as Inter's
LINE = float(__import__("os").environ.get("BB_LINE", "0.7"))
# the gap, in lines at the regular weight
GAP = float(__import__("os").environ.get("BB_GAP", "1.25"))
# where stems are found (a fraction of the cap height: clear of bars and bowls)
PROBE = 0.3
# S: how many points each redrawn edge has (the same at every master)
EDGE_POINTS = 40

# each letter's thick strokes, hollowed in this order (run: which stroke,
# left to right, crosses the probe height, in the letter as it is by then):
#   ("stem", run)
#   ("diagonal", run, (lo, hi)[, arms]) — measured at heights lo and hi; arms: Z's
#   ("leg", (lo, hi), follow) — K R's, the last stroke at those heights; the arm or bowl follows its foot
#   ("chord", side, (lo, hi)) — in the bowl between heights lo and hi
#   ("wide", share) — C G O Q drawn out level, by `share` of a doubled stroke
#   ("arcs",) — S's arcs drawn out towards their terminals
#   ("bowl", share) — D's bowl drawn out
#   ("curved", side) — U J's stem, beside which side the curve runs
#   ("tail",) — Q's, from the ring
#   ("crossed",) — X
#   ("forked",) — Y
#   ("spine",) — S
DESIGN = {
    "A": [("diagonal", 1, (0.55, 0.8))],
    "B": [("stem", 0)],
    "C": [("wide", 0.5), ("chord", "left", (0, 1))],
    "D": [("stem", 0), ("bowl", 0.5), ("chord", "right", (0, 1))],
    "E": [("stem", 0)],
    "F": [("stem", 0)],
    "G": [("wide", 0.5), ("chord", "left", (0, 1))],
    "H": [("stem", 0), ("stem", -1)],
    "I": [("stem", 0)],
    "J": [("curved", "right")],
    "K": [("stem", 0), ("leg", (0.08, 0.28), "arm")],
    "L": [("stem", 0)],
    "M": [("diagonal", 1, (0.35, 0.65)), ("stem", -1)],
    "N": [("diagonal", 1, (0.35, 0.65))],
    "O": [("wide", 1), ("chord", "left", (0, 1)), ("chord", "right", (0, 1))],
    "P": [("stem", 0)],
    "Q": [("wide", 1), ("tail",), ("chord", "left", (0, 1)), ("chord", "right", (0, 1))],
    "R": [("stem", 0), ("leg", (0.08, 0.28), "bowl")],
    "S": [("arcs",), ("spine",)],
    "T": [("stem", 0)],
    "U": [("curved", "left")],
    "V": [("diagonal", 0, (0.4, 0.7))],
    "W": [("diagonal", 0, (0.35, 0.65)), ("diagonal", 3, (0.35, 0.65))],
    "X": [("crossed",)],
    "Y": [("forked",)],
    "Z": [("diagonal", 0, (0.35, 0.65), True)],
    "k": [("stem", 0), ("leg", (0.08, 0.28), "arm")],
}
# the glyph each letter is drawn from, where it is not the letter's own: Inter Math's I has bars (cv08)
BASES = {"I": "I.1"}
SOURCES = [*DESIGN, "H", "x", *BASES.values(), "pipedbl"]


@dataclass
class Lines:
    """A master's lines: a stem's thickness, a bar's, the gap between doubled lines, the cap height."""

    t: float
    bar: float
    gap: float
    cap: float


def crossings(shape: Shape, y: float) -> list[float]:
    """
    The edges of the ink at height y, left to right (the outline's points taken
    as a polygon). Inter's variable outlines overlap (K's arm runs into its
    stem) and holes are cut by contours drawn the other way: the ink is where
    the winding is not zero.
    """
    hits = []
    for c in shape.contours():
        pts = c.points
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            if (p[1] - y) * (q[1] - y) < 0:
                hits.append((p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]), 1 if q[1] > p[1] else -1))
    edges, winding = [], 0
    for x, turn in sorted(hits):
        before, winding = winding, winding + turn
        if (before == 0) != (winding == 0):
            edges.append(x)
    return edges


def runs(shape: Shape, y: float) -> list[tuple[float, float]]:
    """The ink at height y, as (left, right) runs."""
    e = crossings(shape, y)
    return list(zip(e[::2], e[1::2]))


def column(shape: Shape, x: float) -> list[tuple[float, float]]:
    """The ink along the vertical at x, as (bottom, top) runs."""
    return runs(shape.map(lambda px, py: (py, px)), x)


def inked(shape: Shape, x: float, y: float) -> bool:
    return any(a <= x <= b for a, b in runs(shape, y))


def rect(x0: float, y0: float, x1: float, y1: float) -> Shape:
    return Shape.polygon([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])


def hole(points: list[tuple[float, float]]) -> Shape:
    """A contour drawn anticlockwise (from clockwise points): it cuts the ink under it."""
    return Shape.polygon(list(reversed(points)))


def slanted(middle, a: float, b: float, y0: float, y1: float, y0_right: float | None = None, y1_right: float | None = None) -> Shape:
    """
    The strip between offsets a < b from a slanted stroke's middle (x =
    middle(y)), from y0 to y1 (its right edge from y0_right to y1_right), drawn
    clockwise.
    """
    r0 = y0 if y0_right is None else y0_right
    r1 = y1 if y1_right is None else y1_right
    return Shape.polygon([(middle(y0) + a, y0), (middle(y1) + a, y1), (middle(r1) + b, r1), (middle(r0) + b, r0)])


def stem(s: Shape, lines: Lines, run: int) -> Shape:
    """A vertical stem hollow: the letter widened across it, a hole in it a bar from its ends."""
    x0, x1 = runs(s, lines.cap * PROBE)[run]
    mid = (x0 + x1) / 2
    room = lines.gap + (x1 - x0)
    col = column(s, mid)
    y0, y1 = col[0][0], col[-1][1]
    parts = []
    for c in s.contours():
        if any(abs(x - x0) < 1 for x, _ in c.points):
            # drawn through the stem: its right edge and all beyond move
            parts.append(c.map(lambda x, y: (x + room if x > mid else x, y)))
        elif sum(x for x, _ in c.points) / len(c.points) > mid:
            # another part (an arm, a counter) beyond the stem
            parts.append(c.moved(room, 0))
        else:
            parts.append(c)
    gap = hole([(x1, y0 + lines.bar), (x1, y1 - lines.bar), (x1 + lines.gap, y1 - lines.bar), (x1 + lines.gap, y0 + lines.bar)])
    return Shape.join([*parts, gap], s.advance + room)


def diagonal(s: Shape, lines: Lines, run: int, heights: tuple[float, float], arms: bool = False) -> Shape:
    """
    A slanted stroke hollow: the letter widened across it (its parallel), a
    hole cut along it. With `arms` (Z), the stroke ends in bars: what lies in
    them moves as their ends do.
    """
    ya, yb = (lines.cap * f for f in heights)
    ra, rb = runs(s, ya)[run], runs(s, yb)[run]
    slope = (rb[0] - ra[0]) / (yb - ya)
    w = (ra[1] - ra[0] + rb[1] - rb[0]) / 2
    # across the stroke, as wide as a stem's gap
    gap = lines.gap * math.hypot(1, slope)
    room = gap + w

    def left(y: float) -> float:
        return ra[0] + slope * (y - ya)

    parts = []
    for c in s.contours():
        if any(a < r[1] and r[0] < b for y, r in ((ya, ra), (yb, rb)) for a, b in runs(c, y)):
            # drawn through the stroke: its right edge and all beyond move (Z's
            # corners as its arms do; at a point, where the strokes' inner edges
            # cross, the next stroke's from a quarter of the way across)
            def side(y: float) -> float:
                return left(min(max(y, lines.bar), lines.cap - lines.bar) if arms else y) + (0.25 if y < 2 * lines.bar else 0.5) * w

            parts.append(c.map(lambda x, y: (x + room if x > side(y) else x, y)))
        else:
            # another part (A's crossbar), beyond the stroke or not
            cx, cy = (sum(v) / len(c.points) for v in zip(*c.points))
            parts.append(c.moved(room, 0) if cx > left(cy) + w / 2 else c)
    out = Shape.join(parts, s.advance + room)

    # the hole, from the middle of the stroke both ways while ink stays on
    # either side (half a line beyond it: Inter thins its diagonals into their
    # joints), and up to a bar from where the ink ends
    def covered(y: float, a: float, b: float) -> bool:
        return any(r0 <= a and b <= r1 for r0, r1 in runs(out, y))

    def inside(y: float) -> bool:
        return covered(y, left(y) + 0.1 * w, left(y) + w + gap + 0.5 * w)

    def reach(direction: int) -> float:
        best = y = (ya + yb) / 2
        step = lines.cap / 300
        while 0 <= y + direction * step <= lines.cap and inside(y + direction * step):
            y += direction * step
            if covered(y + direction * lines.bar, left(y) + w, left(y) + w + gap):
                best = y
        return best

    y0, y1 = reach(-1), reach(1)
    cut = hole([(left(y0) + w, y0), (left(y1) + w, y1), (left(y1) + w + gap, y1), (left(y0) + w + gap, y0)])
    return Shape.join([out, cut], out.advance)


def edges(lo: tuple[float, float], hi: tuple[float, float], y_lo: float, y_hi: float):
    """A straight slanted stroke crossing two heights at the runs lo and hi: its middle (a function of y), slope and width across."""
    slope = (hi[0] - lo[0]) / (y_hi - y_lo)
    w = (lo[1] - lo[0] + hi[1] - hi[0]) / 2
    return (lambda y: (lo[0] + lo[1]) / 2 + slope * (y - y_lo)), slope, w


def crossed(s: Shape, lines: Lines) -> Shape:
    """
    X, redrawn from its two strokes (Inter's is one outline crossing itself,
    its arms wound opposite ways): the stroke from the top left hollow on its
    middle, a line either side of it and bars across the ends; the other
    stroke as it was, in two, each ending in a line (the hollow stays empty).
    """
    cap, bar = lines.cap, lines.bar
    lo_y, hi_y = cap * 0.2, cap * 0.8
    below, above = runs(s, lo_y), runs(s, hi_y)
    # the stroke from the top left is the left run above the crossing and the right one below; the other, the reverse
    middle, slope, w = edges(below[-1], above[0], lo_y, hi_y)
    other, _, other_w = edges(below[0], above[-1], lo_y, hi_y)
    gap = lines.gap * math.hypot(1, slope)
    near, far = gap / 2, gap / 2 + w
    parts = [
        slanted(middle, -far, -near, 0, cap),
        slanted(middle, near, far, 0, cap),
        slanted(middle, -far, far, cap - bar, cap),
        slanted(middle, -far, far, 0, bar),
    ]

    def meeting(edge: float, offset: float) -> float:
        """Where the other stroke's edge (offset from its middle) meets a line of the hollow one (offset from its)."""
        return (middle(0) + offset - other(0) - edge) / (other(1) - other(0) - (middle(1) - middle(0)))

    # the other stroke in two, each ending in the middle of a line (the hollow stays empty)
    side = (near + far) / 2
    left_edge, right_edge = -other_w / 2, other_w / 2
    below = Shape.polygon([
        (other(0) + left_edge, 0), (other(meeting(left_edge, -side)) + left_edge, meeting(left_edge, -side)),
        (other(meeting(right_edge, -side)) + right_edge, meeting(right_edge, -side)), (other(0) + right_edge, 0),
    ])
    above = Shape.polygon([
        (other(meeting(left_edge, side)) + left_edge, meeting(left_edge, side)), (other(cap) + left_edge, cap),
        (other(cap) + right_edge, cap), (other(meeting(right_edge, side)) + right_edge, meeting(right_edge, side)),
    ])
    return Shape.join([*parts, below, above], s.advance + gap + w)


def curved(s: Shape, lines: Lines, side: str) -> Shape:
    """U J: a second line beside the stem, down into the curve (which runs flatter, widened at its bottom), a bar across the top."""
    cap, t, gap = lines.cap, lines.t, lines.gap
    row = runs(s, cap * 0.6)
    x0, x1 = row[0] if side == "left" else row[-1]
    room = gap + (x1 - x0)
    out = flattened(s, room if side == "left" else -room, cap)
    if side == "left":
        lx = x1 + gap
        top = rect(x0, cap - lines.bar, lx + t, cap)
    else:
        out = out.moved(room, 0)
        x0, x1 = x0 + room, x1 + room
        lx = x0 - gap - t
        top = rect(lx, cap - lines.bar, x1, cap)
    # into the curve below, by half its thickness
    curve = column(out, lx + t / 2)[0]
    line = rect(lx, (curve[0] + curve[1]) / 2, lx + t, cap)
    return Shape.join([out, line, top], s.advance + room)


def flattened(s: Shape, room: float, cap: float, top: bool = False) -> Shape:
    """
    A curve drawn out level at its lowest (U's bowl, J's hook), and its highest
    with `top` (O's), by `room` (rightwards, or leftwards when negative): its
    extreme on-curve points (outside and in, where the curve runs level)
    doubled, the copies and the curve's far side moved; a part without them
    (Q's tail) moved whole when it lies on that side.
    """
    x0, _, x1, _ = s.bounds()
    centre, width = (x0 + x1) / 2, x1 - x0
    sign = 1 if room > 0 else -1
    contours, cuts = [], []
    for c in s.contours():
        pts, on, n = list(c.points), list(c.on), len(c.points)
        lowest = [
            i for i in range(n)
            if on[i] and (pts[i][1] < cap / 4 or top and pts[i][1] > cap * 3 / 4) and abs(pts[i][0] - centre) < width / 10
            and abs(pts[i - 1][1] - pts[i][1]) < 1 and abs(pts[(i + 1) % n][1] - pts[i][1]) < 1
        ]
        if not lowest:
            contours.append((pts, on, None))
            continue
        moving = [False] * n
        # each doubled beside its neighbour on the far side (the copy moves with it)
        for i in sorted(lowest, reverse=True):
            after = sign * (pts[(i + 1) % n][0] - pts[i][0]) > 0
            at = i + 1 if after else i
            pts.insert(at, pts[i])
            on.insert(at, True)
            moving.insert(at, True)
            cuts.append(pts[i][0])
        contours.append((pts, on, moving))
    cut = max(cuts) if sign > 0 else min(cuts)
    parts = []
    for pts, on, moving in contours:
        if moving is None:
            whole = sign * (sum(x for x, _ in pts) / len(pts) - cut) > 0
            moved = [(x + room, y) if whole else (x, y) for x, y in pts]
        else:
            moved = [(x + room, y) if m or sign * (x - cut) > 0.5 else (x, y) for (x, y), m in zip(pts, moving)]
        parts.append(Shape(moved, on, [len(moved) - 1], s.advance))
    return Shape.join(parts, s.advance)


def wide(s: Shape, lines: Lines, share: float) -> Shape:
    """C G O Q: drawn out level at the top and bottom by `share` of a doubled stroke's room (half for each crescent)."""
    room = share * (lines.gap + lines.t)
    out = flattened(s, room, lines.cap, top=True)
    out.advance = s.advance + room
    return out


def bowl(s: Shape, lines: Lines, share: float) -> Shape:
    """D: its bowl drawn out by `share` of a doubled stroke's room, the bars that run straight from the stem to its turn made longer."""
    room = share * (lines.gap + lines.t)
    stem_right = runs(s, lines.cap * PROBE)[1][1]
    turn = max(x for (x, y), on in zip(s.points, s.on) if on and y > lines.cap - 1)
    cut = (stem_right + turn) / 2
    out = s.map(lambda x, y: (x + room if x > cut else x, y))
    out.advance = s.advance + room
    return out


def tail(s: Shape, lines: Lines) -> Shape:
    """
    Q's tail, starting in the bowl's ring rather than inside the counter (where
    it would stand among the chords): its top end moved down along its edges
    until both corners are in the ring.
    """
    contours = s.contours()
    k = min(range(len(contours)), key=lambda i: contours[i].bounds()[1])
    piece, rest = contours[k], Shape.join([c for i, c in enumerate(contours) if i != k], s.advance)
    pts = piece.points
    by_height = sorted(range(len(pts)), key=lambda i: pts[i][1])
    bottom = sorted(by_height[:2], key=lambda i: pts[i][0])
    top = sorted(by_height[-2:], key=lambda i: pts[i][0])
    (bl, br), (tl, tr) = [pts[i] for i in bottom], [pts[i] for i in top]

    def along(a, b, y: float) -> float:
        return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])

    def inked(x: float, y: float) -> bool:
        return any(r0 <= x <= r1 for r0, r1 in runs(rest, y))

    y, step = tl[1], lines.cap / 400
    while y > bl[1] and not (inked(along(tl, bl, y), y) and inked(along(tr, br, y), y)):
        y -= step
    # a little further in, so the cut is buried in the ring
    cut = y - lines.t / 4
    mx, my = (tl[0] + tr[0] + bl[0] + br[0]) / 4, (tl[1] + tr[1] + bl[1] + br[1]) / 4
    dx, dy = (tl[0] + tr[0] - bl[0] - br[0]) / 2, (tl[1] + tr[1] - bl[1] - br[1]) / 2

    def moved(x: float, y: float) -> tuple[float, float]:
        if y <= cut:
            return x, y
        # along its own edge, down to the cut
        left = dx * (y - my) - dy * (x - mx) > 0
        a = bl if left else br
        return along((x, y), a, cut), cut

    piece = piece.map(moved)
    contours[k] = piece
    return Shape.join(contours, s.advance)


def leg(s: Shape, lines: Lines, heights: tuple[float, float], follow: str) -> Shape:
    """
    K R's leg hollow, on its middle: the leg (its own contour) taken out, a
    line either side of where it ran, each from a bar across the foot into
    the arm or bowl it sprang from; that arm or bowl drawn out as far as the
    foot now reaches (`follow`).
    """
    cap, bar = lines.cap, lines.bar
    ya, yb = (cap * f for f in heights)
    ra, rb = runs(s, ya)[-1], runs(s, yb)[-1]
    middle, slope, w = edges(ra, rb, ya, yb)
    gap = lines.gap * math.hypot(1, slope)
    near, far = gap / 2, gap / 2 + w
    kept = [c for c in s.contours() if not any(a < ra[1] and ra[0] < b for a, b in runs(c, ya))]
    # the doubled foot reaches further right by half its room: the arm (K) or the
    # bowl (R) as much, keeping the right side aligned as Inter's is
    further = (gap + w) / 2
    if follow == "arm":
        # the contour reaching the cap height furthest right, slanted on about where it leaves the stem
        k = max(range(len(kept)), key=lambda i: max((x for x, y in kept[i].points if y > cap - 1), default=-math.inf))
        low = kept[k].bounds()[1]
        kept[k] = kept[k].map(lambda x, y: (x + further * (y - low) / (cap - low), y))
    elif follow == "bowl":
        # the bowl's straight bars made longer, halfway between the stem and its turn
        stem_right = runs(Shape.join(kept, s.advance), cap * 0.6)[1][1]
        turn = max(x for c in kept for (x, y), on in zip(c.points, c.on) if on and y > cap - 1)
        cut = (stem_right + turn) / 2
        kept = [c.map(lambda x, y: (x + further if x > cut else x, y)) for c in kept]
    rest = Shape.join(kept, s.advance)

    # each edge of a line up to where it meets the arm or bowl above, and a
    # little in: its end runs along that outline (K's arm is straight, R's bowl convex)
    def meets(offset: float) -> float:
        step, y = cap / 300, yb
        while y < cap and not any(r0 <= middle(y) + offset <= r1 for r0, r1 in runs(rest, y)):
            y += step
        return y + lines.t / 4

    parts = [slanted(middle, a, b, 0, meets(a), 0, meets(b)) for a, b in ((-far, -near), (near, far))]
    parts.append(slanted(middle, -far, far, 0, bar))
    return Shape.join([rest, *parts], s.advance + (gap + w) / 2)


def forked(s: Shape, lines: Lines) -> Shape:
    """
    Y: its left arm and its stem hollow, each on its middle, the right arm a
    single line (as STIX's), one hole bending from the stem into the arm. The
    stem's right line stands under the crotch, centred on it, so that the
    three strokes meet evenly: the right arm leaves the stem's outer edge as
    far under the crotch as the hole turns into the left arm (STIX's crotch
    is over the line's outer quarter, the arm leaving lower; with the stem's
    edge run up to the crotch's height, ink massed in the junction at heavy
    weights).
    """
    cap, gap, bar = lines.cap, lines.gap, lines.bar
    pts, n = s.points, len(s.points)
    x0, x1 = runs(s, cap * 0.25)[0]
    t = x1 - x0
    ya, yb = cap * 0.75, cap * 0.92
    lm, ls, lw = edges(runs(s, ya)[0], runs(s, yb)[0], ya, yb)
    lg = gap * math.hypot(1, ls)
    # how far the left arm's edges move (half its stroke's room), and the hollow stem's half width
    lh, half = (lg + lw) / 2, gap / 2 + t

    feet = sorted((i for i in range(n) if pts[i][1] < 1), key=lambda i: pts[i][0])
    tops = sorted((i for i in range(n) if pts[i][1] > cap - 1), key=lambda i: pts[i][0])
    left_out, left_in, right_in, right_out = tops
    knee_left = max((i for i in range(n) if abs(pts[i][0] - x0) < 1 and pts[i][1] > 1), key=lambda i: pts[i][1])
    knee_right = max((i for i in range(n) if abs(pts[i][0] - x1) < 1 and pts[i][1] > 1), key=lambda i: pts[i][1])
    # the inner edges, from the left arm's top down to the crotch and up to the right arm's
    forward = [(left_in + k) % n for k in range((right_in - left_in) % n + 1)]
    inner = forward if feet[0] not in forward else [(left_in - k) % n for k in range((left_in - right_in) % n + 1)]
    lowest = min(range(1, len(inner) - 1), key=lambda k: (pts[inner[k]][1], k))
    left_inner, right_inner = inner[1 : lowest + 1], inner[lowest + 1 : -1]

    def across(a, b, y: float) -> float:
        """Where the line through a and b crosses height y."""
        return a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])

    def meet(a, b, x: float) -> float:
        """Where the line through a and b reaches x (its height)."""
        return a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0])

    moved = list(pts)
    moved[left_out] = (pts[left_out][0] - lh, cap)
    moved[left_in] = (pts[left_in][0] + lh, cap)
    for i in left_inner:
        moved[i] = (pts[i][0] + lh, pts[i][1])
    # the fork: the left arm's inner edge, moved, meets the right arm's (their straight parts) higher; what lay below it there
    la, lb = moved[left_in], moved[left_inner[0]]
    ra, rb = moved[right_in], moved[right_inner[-1]]
    sl, sr = (lb[0] - la[0]) / (lb[1] - la[1]), (rb[0] - ra[0]) / (rb[1] - ra[1])
    y_fork = (ra[0] - la[0] + sl * la[1] - sr * ra[1]) / (sl - sr)
    fork = (la[0] + sl * (y_fork - la[1]), y_fork)
    for i in left_inner + right_inner:
        if moved[i][1] < y_fork:
            moved[i] = fork
    # the stem: its right line centred under the crotch; the right arm's outer edge comes down to its outer edge
    outer_right = (pts[right_out], pts[knee_right])
    middle = fork[0] - t / 2 - gap / 2
    outer_left = (moved[left_out], (pts[knee_left][0] - lh, pts[knee_left][1]))
    moved[feet[0]] = (middle - half, 0)
    moved[feet[1]] = (middle + half, 0)
    moved[knee_left] = (middle - half, meet(*outer_left, middle - half))
    moved[knee_right] = (middle + half, meet(*outer_right, middle + half))
    out = Shape(moved, list(s.on), list(s.ends), s.advance + lh)

    # the hole: the stem's, bending where its sides meet the arm's hole
    top = cap - bar
    bend_left = (middle - gap / 2 + lg / 2 - lm(0)) / ls
    bend_right = (middle + gap / 2 - lg / 2 - lm(0)) / ls
    cut = hole([
        (middle - gap / 2, bar), (middle - gap / 2, bend_left), (lm(top) - lg / 2, top), (lm(top) + lg / 2, top),
        (middle + gap / 2, bend_right), (middle + gap / 2, bar),
    ])
    return Shape.join([out, cut], out.advance)


def chord(s: Shape, lines: Lines, side: str, heights: tuple[float, float]) -> Shape:
    """A straight line inside a bowl, a gap from it at its middle, into the arcs above and below by half their thickness."""
    mid = lines.cap * (heights[0] + heights[1]) / 2
    row = runs(s, mid)
    x = row[0][1] + lines.gap if side == "left" else row[-1][0] - lines.gap - lines.t
    col = column(s, x + lines.t / 2)
    below = max((r for r in col if r[1] < mid), key=lambda r: r[1])
    above = min((r for r in col if r[0] > mid), key=lambda r: r[0])
    line = rect(x, (below[0] + below[1]) / 2, x + lines.t, (above[0] + above[1]) / 2)
    return Shape.join([s, line], s.advance)


def curve_samples(points: list[tuple[float, float]], on: list[bool], per: int = 16) -> list[tuple[float, float]]:
    """Points along an open TrueType path (from an on-curve point to another), `per` to a segment."""
    out = [points[0]]
    start, pending = points[0], None

    def quad(a, c, b):
        for k in range(1, per + 1):
            u = k / per
            out.append(((1 - u) ** 2 * a[0] + 2 * u * (1 - u) * c[0] + u * u * b[0], (1 - u) ** 2 * a[1] + 2 * u * (1 - u) * c[1] + u * u * b[1]))

    for p, is_on in zip(points[1:], on[1:]):
        if not is_on:
            if pending is not None:
                mid = ((pending[0] + p[0]) / 2, (pending[1] + p[1]) / 2)
                quad(start, pending, mid)
                start = mid
            pending = p
            continue
        if pending is None:
            quad(start, ((start[0] + p[0]) / 2, (start[1] + p[1]) / 2), p)
        else:
            quad(start, pending, p)
        start, pending = p, None
    return out


def unfolded(line: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """A polyline with any loop it makes (crossing itself) cut out at the crossing."""

    def crossing(p, q, r, t):
        d = (q[0] - p[0]) * (t[1] - r[1]) - (q[1] - p[1]) * (t[0] - r[0])
        if abs(d) < 1e-9:
            return None
        u = ((r[0] - p[0]) * (t[1] - r[1]) - (r[1] - p[1]) * (t[0] - r[0])) / d
        v = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
        return (p[0] + u * (q[0] - p[0]), p[1] + u * (q[1] - p[1])) if 0 < u < 1 and 0 < v < 1 else None

    i = 0
    while i < len(line) - 1:
        for j in range(len(line) - 2, i + 1, -1):
            x = crossing(line[i], line[i + 1], line[j], line[j + 1])
            if x is not None:
                line = line[: i + 1] + [x] + line[j + 1 :]
                break
        i += 1
    return line


def smooth(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def resampled(line: list[tuple[float, float]], count: int) -> list[tuple[float, float]]:
    """`count` - 1 points evenly along a polyline, its ends left out."""
    lengths = [0.0]
    for a, b in zip(line, line[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    out, j = [], 0
    for k in range(1, count):
        target = lengths[-1] * k / count
        while lengths[j + 1] < target:
            j += 1
        f = (target - lengths[j]) / ((lengths[j + 1] - lengths[j]) or 1)
        out.append((line[j][0] + (line[j + 1][0] - line[j][0]) * f, line[j][1] + (line[j + 1][1] - line[j][1]) * f))
    return out


def arcs(s: Shape, lines: Lines) -> Shape:
    """
    S, before its stroke is doubled (spine): its arcs drawn out towards their
    terminals (scaled across about their tops and bottoms, outside and in, the
    terminals moved out whole), by as much as doubling the stroke moves each
    bowl's other side out, so that each bowl widens both ways and the letter
    stays upright.
    """
    pts, on, n = s.points, s.on, len(s.points)
    level = sorted((i for i in range(n) if on[i] and abs(pts[i - 1][1] - pts[i][1]) < 1 and abs(pts[(i + 1) % n][1] - pts[i][1]) < 1), key=lambda i: pts[i][1])
    bottom_out, bottom_in, top_in, top_out = level[0], level[1], level[-2], level[-1]
    upright = sorted((i for i in range(n) if on[i] and abs(pts[i - 1][0] - pts[i][0]) < 1 and abs(pts[(i + 1) % n][0] - pts[i][0]) < 1), key=lambda i: pts[i][1])
    lower, upper = sorted(upright[:2], key=lambda i: pts[i][0]), sorted(upright[2:], key=lambda i: pts[i][0])
    thickness = (pts[upper[1]][0] - pts[upper[0]][0] + pts[lower[1]][0] - pts[lower[0]][0]) / 2
    half = (lines.gap + thickness) / 2

    def walk(i: int, j: int) -> list[int]:
        """The contour's indices from i to j the way round through no upright point (by the terminal)."""
        forward = [(i + k) % n for k in range((j - i) % n + 1)]
        return forward if not set(forward) & set(upright) else [(i - k) % n for k in range((i - j) % n + 1)]

    moved = list(pts)
    for path, sign in ((walk(top_out, top_in), 1), (walk(bottom_out, bottom_in), -1)):
        # the terminal: where the arc's path is cut level between two on-curve points
        cut = next(k for k in range(1, len(path) - 2) if on[path[k]] and on[path[k + 1]] and abs(pts[path[k]][1] - pts[path[k + 1]][1]) < 1)
        for part, apex, end in ((path[: cut + 1], path[0], path[cut]), (path[cut + 1 :], path[-1], path[cut + 1])):
            k = 1 + sign * half / (pts[end][0] - pts[apex][0])
            for i in part:
                moved[i] = (pts[apex][0] + (pts[i][0] - pts[apex][0]) * k, pts[i][1])
    return Shape(moved, list(on), list(s.ends), s.advance + 2 * half)


def spine(s: Shape, lines: Lines) -> Shape:
    """
    S: its stroke hollow on its middle (as STIX's, the arcs' tops single, the
    letter its height), by moving its edges half a doubled stroke apart:
    the quarter curves from the arcs' tops to where the bowls stand upright
    scaled across (the outer ones out, the inner ones in: Inter's curves, still
    convex), the stroke between (through the spine) offset either way; the
    hole wherever the edges are more than two lines apart, its tips in the
    quarters.
    """
    pts, on, n = s.points, s.on, len(s.points)
    gap = lines.gap
    # the arcs' tops and bottoms, outside and in (on-curve, where they run level; drawn out
    # level, the stroke starts from the top's left end and ends at the bottom's right one)
    level = [i for i in range(n) if on[i] and abs(pts[i - 1][1] - pts[i][1]) < 1 and abs(pts[(i + 1) % n][1] - pts[i][1]) < 1]
    heights = sorted({round(pts[i][1]) for i in level})

    def ends(h: int, last) -> int:
        return last((i for i in level if abs(pts[i][1] - h) < 1), key=lambda i: pts[i][0])

    bottom_out, bottom_in = ends(heights[0], max), ends(heights[1], max)
    top_in, top_out = ends(heights[-2], min), ends(heights[-1], min)
    # where the bowls stand upright, outside and in
    upright = {i for i in range(n) if on[i] and abs(pts[i - 1][0] - pts[i][0]) < 1 and abs(pts[(i + 1) % n][0] - pts[i][0]) < 1}

    def walk(i: int, j: int, avoid: int) -> tuple[list[int], bool]:
        """The contour's indices from i to j, the way round that does not pass `avoid` (and whether that is forwards)."""
        forward = [(i + k) % n for k in range((j - i) % n + 1)]
        return (forward, True) if avoid not in forward else ([(i - k) % n for k in range((i - j) % n + 1)], False)

    # the stroke's two edges, from the top round to the bottom: the one inside the
    # upper arc (which turns outside the lower), and the one outside it
    edges_ = [walk(top_in, bottom_out, top_out), walk(top_out, bottom_in, top_in)]
    ups = []
    for indices, _ in edges_:
        found = [k for k in indices if k in upright]
        ups.append((found[0], found[-1]))
    # the room: half to either side of the stroke (a doubled stroke less the line it was)
    thickness = (abs(pts[ups[0][0]][0] - pts[ups[1][0]][0]) + abs(pts[ups[0][1]][0] - pts[ups[1][1]][0])) / 2
    half = (gap + thickness) / 2

    def away(k: int, other: int) -> float:
        """Which way an upright point moves: away from the other edge's upright point level with it."""
        mate = min(ups[other], key=lambda j: abs(pts[j][1] - pts[k][1]))
        return 1.0 if pts[k][0] > pts[mate][0] else -1.0

    def normals(curve):
        out = []
        for q in range(len(curve)):
            a, b = curve[max(q - 1, 0)], curve[min(q + 1, len(curve) - 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            length = math.hypot(tx, ty)
            out.append((-ty / length, tx / length))
        return out

    new_edges, dense = [], []  # the moved edges (points and flags, in their own order), and dense samples (original, moved)
    for e, ((indices, _), (first_up, second_up)) in enumerate(zip(edges_, ups)):
        other = 1 - e
        i1, i2 = indices.index(first_up), indices.index(second_up)
        scales = []
        # the quarters: scaled across about the arc's top or bottom, the upright point half the room out
        for apex, up in ((indices[0], first_up), (indices[-1], second_up)):
            target = pts[up][0] + away(up, other) * half
            scales.append((pts[apex][0], (target - pts[apex][0]) / (pts[up][0] - pts[apex][0])))

        def scaled(p, which: int) -> tuple[float, float]:
            x0, k = scales[which]
            return x0 + (p[0] - x0) * k, p[1]

        heads = [scaled(pts[j], 0) for j in indices[: i1 + 1]]
        tails = [scaled(pts[j], 1) for j in indices[i2:]]
        # between: offset along the stroke, redrawn through samples (on the upright points' verticals at its ends)
        middle = indices[i1 : i2 + 1]
        curve = curve_samples([pts[j] for j in middle], [on[j] for j in middle], 24)
        across = normals(curve)
        flip = 1.0 if across[0][0] * away(first_up, other) > 0 else -1.0
        line = [(q[0] + flip * nx * half, q[1] + flip * ny * half) for q, (nx, ny) in zip(curve, across)]
        # where the curve turns tighter than the offset (a counter's corner) the offset folds
        # over itself: the fold cut out (the corner then comes to a point, as a stroke's would)
        line = unfolded(line)
        between = resampled(line, EDGE_POINTS)
        between[0] = (heads[-1][0], between[0][1])
        between[-1] = (tails[0][0], between[-1][1])
        new_edges.append((heads + between + tails, [on[j] for j in indices[: i1 + 1]] + [False] * len(between) + [on[j] for j in indices[i2:]]))
        # the whole edge, densely: as it was and as it is now
        head = curve_samples([pts[j] for j in indices[: i1 + 1]], [on[j] for j in indices[: i1 + 1]], 24)
        tail = curve_samples([pts[j] for j in indices[i2:]], [on[j] for j in indices[i2:]], 24)
        dense.append((head + curve + tail, [scaled(p, 0) for p in head] + line + [scaled(p, 1) for p in tail]))

    # the contour again, its edges replaced (in the contour's own order)
    replaced = {}
    for (indices, forward), (seq, flags) in zip(edges_, new_edges):
        if not forward:
            indices, seq, flags = indices[::-1], seq[::-1], flags[::-1]
        replaced[indices[0]] = (set(indices), seq, flags)
    ring, ring_on = [], []
    done: set[int] = set()
    for i in range(n):
        if i in done:
            continue
        if i in replaced:
            inner, seq, flags = replaced[i]
            done |= inner
            ring += seq
            ring_on += flags
        elif not any(i in inner for inner, _, _ in replaced.values()):
            ring.append(pts[i])
            ring_on.append(on[i])
    out = Shape(ring, ring_on, [len(ring) - 1], s.advance + 2 * half)

    # the hole: across the stroke as it was (the nearest point of the other edge, a line
    # away), carried to where both points now are; wherever they are more than two lines apart
    (first_old, first_new), (second_old, second_new) = dense

    def nearest(p, curve) -> int:
        return min(range(len(curve)), key=lambda i: (curve[i][0] - p[0]) ** 2 + (curve[i][1] - p[1]) ** 2)

    spans = []
    for a_old, a in zip(first_old, first_new):
        j = nearest(a_old, second_old)
        b = second_new[j]
        width = math.dist(a, b)
        h = (width - 2 * math.dist(a_old, second_old[j])) / 2
        if h > lines.t / 20:
            spans.append((((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), ((a[0] - b[0]) / width, (a[1] - b[1]) / width), min(h, gap / 2)))
    lengths = [0.0]
    for (m1, _, _), (m2, _, _) in zip(spans, spans[1:]):
        lengths.append(lengths[-1] + math.dist(m1, m2))
    # closer together towards the tips, where the hole narrows
    count = 32
    picks = [min(range(len(spans)), key=lambda i: abs(lengths[i] - lengths[-1] * (1 - math.cos(math.pi * k / count)) / 2)) for k in range(count + 1)]
    side_a = [(spans[i][0][0] + spans[i][1][0] * spans[i][2], spans[i][0][1] + spans[i][1][1] * spans[i][2]) for i in picks[1:-1]]
    side_b = [(spans[i][0][0] - spans[i][1][0] * spans[i][2], spans[i][0][1] - spans[i][1][1] * spans[i][2]) for i in picks[1:-1]]
    lens = [spans[picks[0]][0], *side_a, spans[picks[-1]][0], *reversed(side_b)]
    lens_on = [True, *[False] * len(side_a), True, *[False] * len(side_b)]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(lens, lens[1:] + lens[:1]))
    if area < 0:
        # anticlockwise, to cut the ink
        lens, lens_on = lens[::-1], lens_on[::-1]
    return Shape.join([out, Shape(lens, lens_on, [len(lens) - 1], out.advance)], out.advance)


def doubled(letter: str, s: Shape, lines: Lines) -> Shape:
    ops = {
        "stem": stem, "diagonal": diagonal, "leg": leg, "crossed": crossed, "curved": curved, "chord": chord,
        "forked": forked, "wide": wide, "bowl": bowl, "spine": spine, "tail": tail, "arcs": arcs,
    }
    for kind, *args in DESIGN[letter]:
        s = ops[kind](s, lines, *args)
    return s


def line_weight(m: Masters, design: dict) -> dict:
    """
    The weight whose stem is LINE of the letter's, and no heavier than a bar of
    Inter's ǁ (its two bars grow less than a stem and keep their white open at
    heavy weights): Inter's capitals are drawn there, their strokes the lines.
    """
    bar, _ = pipe_bars(m, {**design, "wght": min(design["wght"], m.axes["wght"].maxValue)})
    target = min(LINE * m.stem(design["wght"], design["opsz"]), bar)
    return {**design, "wght": min(m.weights, key=lambda w: abs(m.stem(w, design["opsz"]) - target))}


def measure(m: Masters, light: dict) -> Lines:
    """The lines at a weight: Inter's H's stem and crossbar; the gap from the regular weight's lines."""
    cap = m.section("one", light["wght"], light["opsz"])[2]

    def h_stem(location: dict) -> float:
        a, b = runs(m.shape("H", location), cap * PROBE)[0]
        return b - a

    h = m.shape("H", light)
    x0, _, x1, _ = h.bounds()
    bar = next(b - a for a, b in column(h, (x0 + x1) / 2) if 0.3 * cap < a < 0.7 * cap)
    t = h_stem(light)
    t_regular = h_stem(line_weight(m, {**light, "wght": m.axes["wght"].defaultValue}))
    # narrower as the lines grow heavier than the regular weight's (no wider below it)
    return Lines(t, bar, GAP * t_regular * min(1.0, math.sqrt(t_regular / t)), cap)


def letters(m: Masters, design: dict, which=None) -> tuple[dict[str, Shape], Lines]:
    """The blackboard letters at a master (or any location), with Inter's side bearings."""
    light = line_weight(m, design)
    lines = measure(m, light)
    out = {}
    # lowercase (k): its strokes found against the x-height where the capitals' are against the cap height
    small = replace(lines, cap=m.shape("x", light).bounds()[3])
    for letter in which or DESIGN:
        base = m.shape(BASES.get(letter, letter), light)
        s = doubled(letter, base, lines if letter.isupper() else small)
        x0, _, x1, _ = s.bounds()
        bx0, _, bx1, _ = base.bounds()
        s = s.moved(bx0 - x0, 0)
        s.advance = (x1 - x0) + bx0 + (base.advance - bx1)
        out[letter] = s
    return out, lines


def blackboard_glyphs(path, which=None) -> list[NewGlyph]:
    """The blackboard letters (or only `which` of them), variable."""
    m = Masters(path, [*SOURCES, "one"])
    shapes: dict[str, list[Shape]] = {}
    for design in m.masters:
        for letter, s in letters(m, design, which)[0].items():
            shapes.setdefault(letter, []).append(s)
    return [m.glyph(f"{letter}.bb", s, ord(letter)) for letter, s in shapes.items()]
