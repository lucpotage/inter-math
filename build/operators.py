"""
Math operators, as heavy as the letters, larger than Inter's text ones, on
the math axis.

Inter draws + − = as heavy as its letters; TeX draws its lighter (Computer
Modern: + and fraction bars 0.04 em thick, letter stems 0.07). Inter Math
keeps Inter's: its operators match the letters around them (OFFSET weight
units lighter would be TeX's way, 0 is Inter's). It is the glyph itself that
is drawn so, not a style on KaTeX's operator classes: KaTeX turns a leading −
(−b) into an ordinary symbol, and both must look the same.

Inter centres its operators, arrows and brackets on the digits next to digits
and capitals (2+2: plus.case, by its calt), and lower next to lowercase. Math
has one axis for both: Inter Math sets them all at the height Inter gives its
brackets and arrows in lowercase text (its case forms lowered by as much as
its arrows' are raised: axis_drop()), 0.58 of the x-height, as TeX's axis
is; capitals then sit a little high, as in TeX. KaTeX's math axis follows
(src/index.ts), so fraction bars line up with the minus sign.

They are drawn larger than Inter draws them for text (SCALE: TeX's and other
math fonts' + = are about as wide as a capital is tall, Inter's 0.6 of it;
relations less, RELATION_SCALE, to the capitals' height), at the weight that
keeps their stroke as Inter draws it (build/variable.py): Inter's outlines,
scaled about the axis. That stroke is the minus sign's, or each sign's own
where Inter draws it lighter at Black (OWN_STROKES; the double arrows'
shafts are its ⇒'s): lighter than the letters' stems there, as Inter's are.
Arrows keep Inter's heads (ARROW_HEAD: 0.8 of them until review 1, too
small against two shafts) and have their shafts drawn out (ARROW_LENGTH), as
TeX's are long; the double arrows are Inter's own ⇒ ⇐ ⇔ ⟹ ⟸ ⟺ drawn out,
not the single doubled.

All their horizontal bars (+ − = ± ÷ ≤ ≥, and what is built on them) are as
wide as the minus sign, as TeX's are (Inter's differ: = is narrower, + wider),
and + stays square. = is drawn out to that width, not scaled: the space
between its bars is Inter's, and it is the space between parallel strokes in
every sign (≡ ≈ ∥ ⇒ ⇔ ⊨ ≪ ⊆…, as in TeX). ¬ and ↕ have no case forms: drawn
at the height of Inter's lowercase arrows, they stay there (¬'s bar is then
the minus sign's).

Fraction bars follow the minus sign and surds the √ (src/metrics.ts measures
them from the font); the geometry symbols (build/geometry_glyphs.py) and the
signs in scripts (build/script_glyphs.py) are drawn as heavy, and as high.
"""

from variable import Masters, NewGlyph, Shape

# how much lighter than the letters the operators are drawn (TeX's would be about 100; Inter's, kept, 0)
OFFSET = 0
# code point → Inter glyph
OPERATORS = {
    0x002B: "plus", 0x2212: "minus", 0x003D: "equal", 0x00D7: "multiply", 0x00F7: "divide", 0x00B1: "plusminus",
    0x003C: "less", 0x003E: "greater", 0x2264: "lessequal", 0x2265: "greaterequal", 0x2248: "approxequal",
    0x00AC: "logicalnot", 0x221A: "radical",
    0x2190: "arrowleft", 0x2191: "arrowup", 0x2192: "arrowright", 0x2193: "arrowdown", 0x2194: "arrowboth",
    0x2195: "arrowupdn", 0x2196: "uni2196", 0x2197: "uni2197", 0x2198: "uni2198", 0x2199: "uni2199",
    0x21D0: "arrowdblleft", 0x21D2: "arrowdblright", 0x21D4: "arrowdblboth",
    0x27F5: "uni27F5", 0x27F6: "uni27F6", 0x27F7: "uni27F7", 0x27F8: "uni27F8", 0x27F9: "uni27F9", 0x27FA: "uni27FA",
}
# signs Inter has no case form of, drawn at the height of its lowercase arrows: raised as its arrows' case forms are
RAISED = {"logicalnot", "arrowupdn"}
# how much larger than Inter's text signs the math ones are drawn: TeX's and STIX's + and = are about as wide
# as a capital is tall, Inter's (sized for text) 0.6 of it; their relations about 0.87 of it, Inter's (tall
# chevrons and bowls) 0.75: the relations grow less, to the capitals' height. Arrows grow less too (Inter's
# are already as wide as a capital is tall, their heads large): TeX's → is a third wider than its =. √ is
# kept (KaTeX sizes surds by it)
SCALE = 1.5
RELATION_SCALE = 1.3
RELATIONS = {"less", "greater", "lessequal", "greaterequal"}
# arrows: Inter's heads as Inter draws them (TeX's and STIX's are 0.6-0.75 of a capital tall, Inter's 0.9: drawn
# 0.8 as large, their heads hardly cleared a double arrow's shafts, review 1), and their shafts drawn out, as Inter
# draws ⟶ from → (TeX's → is 1.3 capitals long, Inter's 1.0): each arrow ARROW_LENGTH times as long as Inter's; the
# way each points (the head's side)
ARROW_HEAD = 1.0
ARROW_LENGTH = 1.3
# TeX's two-headed arrows against its one-headed ones, their lengths (in its Main font: ↔ 889 against → 888, ⇔ 932
# against ⇒ 888, ⟷ 1748 against ⟶ 1469, ⟺ 1746 against ⟹ 1526, ↕ 1044 against ↑ 888, its ⇕ as tall). Inter's are
# much longer than its own (↔ 1.57 times →): drawn out as they are, ↔ ⇔ stood 1.2 em, 1.44 times →, and ↕ ⇕ 1.42 ↑
BOTH_LENGTH = {"arrowboth": 889 / 888, "arrowdblboth": 932 / 888, "uni27F7": 1748 / 1469, "uni27FA": 1746 / 1526,
               "arrowupdn": 1044 / 888}
POINTING = {
    "arrowright": (1, 0), "uni27F6": (1, 0), "arrowdblright": (1, 0), "uni27F9": (1, 0),
    "arrowleft": (-1, 0), "uni27F5": (-1, 0), "arrowdblleft": (-1, 0), "uni27F8": (-1, 0),
    "arrowup": (0, 1), "arrowdown": (0, -1),
    "uni2197": (1, 1), "uni2198": (1, -1), "uni2196": (-1, 1), "uni2199": (-1, -1),
}
# the diagonal arrows: as wide as → (TeX's ↗ spans 915 to its → 888), so √2 times as long along their slant (Inter's
# are as long as its →, 0.75 of its width: drawn out as → is, they stood short beside TeX's)
DIAGONALS = {"uni2197", "uni2198", "uni2196", "uni2199"}
DIAGONAL_SPAN = 915 / 888
# with a head at both ends: along this; as long as the one-headed arrow, with its other head (Inter's ↔ is longer
# than its → by a head and a little shaft: that, its head part smaller)
BOTH_WAYS = {"arrowboth": (1, 0), "uni27F7": (1, 0), "arrowdblboth": (1, 0), "uni27FA": (1, 0), "arrowupdn": (0, 1)}
ONE_HEADED = {"arrowboth": "arrowright", "uni27F7": "uni27F6", "arrowdblboth": "arrowdblright", "uni27FA": "uni27F9", "arrowupdn": "arrowup"}
ARROWS = {*POINTING, *BOTH_WAYS, "uni21AA"}
UNSCALED = {"radical"}



def case(m: Masters, name: str) -> str:
    """Inter's case form of a glyph, when it has one (and it is among the glyphs drawn from)."""
    return f"{name}.case" if f"{name}.case" in m.glyphs and f"{name}.case" in m.font.getGlyphOrder() else name


# the signs whose bars are made as wide as the minus sign's ("plus" also kept square)
BARRED = {"plus", "minus", "equal", "plusminus", "divide", "lessequal", "greaterequal"}


def case_rise(m: Masters, location: dict) -> float:
    """How much higher Inter's case forms are than its lowercase ones (its arrows')."""
    _, a0, _, a1 = m.shape("arrowright", location).bounds()
    _, c0, _, c1 = m.shape("arrowright.case", location).bounds()
    return (c0 + c1 - a0 - a1) / 2


_ARROWS: dict = {}


def axis_drop(m: Masters, location: dict) -> float:
    """How far under Inter's case forms the math axis is: as far as Inter raises its arrows' case forms."""
    source = m
    if not {"arrowright", "arrowright.case"} <= set(m.glyphs):
        key = str(m.path)
        if key not in _ARROWS:
            _ARROWS[key] = Masters(m.path, ["arrowright", "arrowright.case"])
        source = _ARROWS[key]
    return case_rise(source, location)


def math_axis(m: Masters, location: dict) -> float:
    """The math axis at a location: the middle of Inter's case minus, lowered (axis_drop())."""
    _, a0, _, a1 = m.shape("minus.case", location).bounds()
    return (a0 + a1) / 2 - axis_drop(m, location)


def scale_of(name: str) -> float:
    return 1.0 if name in UNSCALED else ARROW_HEAD if name in ARROWS else RELATION_SCALE if name in RELATIONS else SCALE


def bar_stroke(shape: Shape) -> float:
    """A sign's bars' thickness: the shortest side of its straight bars (four-point contours, upright or turned)."""
    import math

    return min(min(math.dist(c.points[i], c.points[(i + 1) % 4]) for i in range(4)) for c in shape.contours() if len(c.points) == 4)


def arm_stroke(shape: Shape) -> float:
    """A chevron's stroke (< > ≤ ≥): its lower arm's, upright halfway along (Inter's arms taper)."""
    chevron = max(shape.contours(), key=lambda c: len(c.points))
    x0, _, x1, _ = chevron.bounds()
    ys = column(chevron, (x0 + x1) / 2)
    return ys[1] - ys[0]


def wave_stroke(shape: Shape) -> float:
    """
    ≈'s stroke: its upper wave's, across it, the median along its middle
    (its curves followed: Inter's waves change shape with the weight, one
    section of them doesn't follow their stroke).
    """
    import math
    import statistics

    wave = flattened(max(shape.contours(), key=lambda c: c.bounds()[3]))
    x0, _, x1, _ = wave.bounds()

    def middle(x: float) -> float:
        ys = column(wave, x)
        return (ys[0] + ys[-1]) / 2

    step = (x1 - x0) / 40
    across = []
    for i in range(4, 37):
        x = x0 + i * step
        ys = column(wave, x)
        slope = (middle(x + step / 2) - middle(x - step / 2)) / step
        across.append((ys[-1] - ys[0]) / math.hypot(1, slope))
    return statistics.median(across)


# the signs kept as heavy as Inter draws them, each by its own stroke: Inter draws them lighter than its minus
# sign at Black (the others gain weight as it does, and keep its stroke)
OWN_STROKES = {
    "less": arm_stroke, "greater": arm_stroke, "lessequal": arm_stroke, "greaterequal": arm_stroke,
    "approxequal": wave_stroke, "multiply": bar_stroke, "divide": bar_stroke, "plusminus": bar_stroke,
}


def scaled_weight(m: Masters, location: dict, k: float, name: str | None = None) -> float:
    """
    The weight at which Inter's signs, k times as large, are as heavy as at
    the location: the minus sign's stroke, or the sign's own (OWN_STROKES).
    """
    probe = OWN_STROKES.get(name)

    def thick(w: float) -> float:
        if probe:
            return probe(m.shape(case(m, name), {**location, "wght": w}))
        _, y0, _, y1 = m.shape("minus.case", {**location, "wght": w}).bounds()
        return y1 - y0

    return location["wght"] if k == 1 else m.weight_for(lambda w: thick(w) * k, thick(location["wght"]))


def about_axis(m: Masters, location: dict, drawn: Shape, base: Shape, k: float) -> Shape:
    """`drawn` k times as large, about the math axis and the left edge of `base`'s ink; `base`'s side bearings kept."""
    if k == 1:
        return drawn
    _, a0, _, a1 = m.shape("minus.case", location).bounds()
    axis = (a0 + a1) / 2
    x0, _, x1, _ = base.bounds()
    dx0, _, dx1, _ = drawn.bounds()
    out = drawn.map(lambda x, y: (x0 + (x - dx0) * k, axis + (y - axis) * k))
    out.advance = x0 + (dx1 - dx0) * k + base.advance - x1
    return out


def sign(m: Masters, name: str, location: dict, scale: float | None = None) -> Shape:
    """
    Inter's case form of a glyph at a location (raised to it, for RAISED),
    `scale` times as large as Inter draws it (by default SCALE, RELATION_SCALE
    for relations, ARROW_HEAD for arrows): drawn lighter so that its stroke
    stays the one it has there (the minus sign's, or its own: OWN_STROKES),
    scaled about the math axis and its ink's left edge, Inter's side bearings
    kept.
    """
    k = scale_of(name) if scale is None else scale
    glyph = case(m, name)
    base = m.shape(glyph, location)
    drawn = base if k == 1 else m.shape(glyph, location, scaled_weight(m, location, k, name))
    if name in RAISED:
        rise = case_rise(m, location)
        base, drawn = base.moved(0, rise), drawn.moved(0, rise)
    # on the math axis (not √: it stands on the baseline, KaTeX places surds)
    return about_axis(m, location, drawn, base, k).moved(0, 0 if name in UNSCALED else -axis_drop(m, location))


def gap(m: Masters, location: dict) -> float:
    """
    The space between Inter's = bars at a location: the space between
    parallel strokes in every sign (= ≡ ≈ ∥ ⇒ ⊨ ≪ ⊆…), = keeping Inter's.
    """
    a, b = sorted((c.bounds() for c in m.shape(case(m, "equal"), location).contours()), key=lambda r: r[1])
    return b[1] - a[3]


def pipe_bars(m: Masters, location: dict) -> tuple[float, float]:
    """
    Inter's ǁ at a location: how thick its bars are and how far apart. Two
    strokes side by side as Inter keeps them at every weight: its bars grow less
    than a stem, which keeps the white between them open at heavy weights (from
    100 to 900: bars 0.020 to 0.084 em, apart 0.096 to 0.031 em). Needs
    "pipedbl" among the glyphs drawn from.
    """
    pipe = m.shape("pipedbl", location)
    _, y0, _, y1 = pipe.bounds()
    (a0, a1), (b0, _) = pipe.runs((y0 + y1) / 2)[:2]
    return a1 - a0, b0 - a1


def shafts_apart(shape: Shape, space: float) -> Shape:
    """A double arrow (its two shafts four-point contours) with its shafts `space` apart, their cut ends kept on the heads' arms."""
    contours = shape.contours()
    lower, upper = sorted((i for i, c in enumerate(contours) if len(c.points) == 4), key=lambda i: contours[i].bounds()[1])
    d = (space - (contours[upper].bounds()[1] - contours[lower].bounds()[3])) / 2
    for i, dy in ((lower, -d), (upper, d)):
        pts = contours[i].points
        order = sorted(range(4), key=lambda k: pts[k][0])
        shift = {}
        for end in (order[:2], order[2:]):
            (xa, ya), (xb, yb) = pts[end[0]], pts[end[1]]
            # a cut end runs along the arm it meets: it slides along it; a flat one stays
            dx = dy * (xb - xa) / (yb - ya) if abs(xb - xa) > 0.5 else 0.0
            shift.update({k: dx for k in end})
        c = contours[i]
        contours[i] = Shape([(x + shift[k], y + dy) for k, (x, y) in enumerate(pts)], c.on, c.ends, c.advance)
    return Shape.join(contours, shape.advance)


def drawn_out(shape: Shape, direction: tuple[float, float], by: float, both: bool = False, cut: float | None = None) -> Shape:
    """
    An arrow's shaft drawn out by `by` along `direction` (its head's way), as
    Inter draws its long arrows from its short ones: all but its tail moves on
    (a head at each end: each half of it, half as far, each its way). The cut
    is in the shaft: near the tail, or in the middle between two heads.
    """
    import math

    n = math.hypot(*direction)
    dx, dy = direction[0] / n, direction[1] / n
    along = [x * dx + y * dy for x, y in shape.points]
    lo, hi = min(along), max(along)
    if cut is None:
        cut = (lo + hi) / 2 if both else lo + (hi - lo) * 0.2
    step = by / 2 if both else by

    def moved(x: float, y: float) -> tuple[float, float]:
        t = x * dx + y * dy
        if t > cut:
            return (x + dx * step, y + dy * step)
        if both and t < cut:
            return (x - dx * step, y - dy * step)
        return (x, y)

    out = shape.map(moved)
    # its ink starts where the sign's did (a head drawn out leftwards would go past the origin): its side bearings kept
    out = out.moved(shape.bounds()[0] - out.bounds()[0], 0)
    out.advance = shape.advance + abs(dx) * by
    return out


def length_of(m: Masters, name: str, location: dict) -> float:
    """How long Inter's arrow is (its case form's ink, along the way it points)."""
    import math

    direction = POINTING.get(name) or BOTH_WAYS[name]
    n = math.hypot(*direction)
    along = [(x * direction[0] + y * direction[1]) / n for x, y in m.shape(case(m, name), location).points]
    return max(along) - min(along)


def arrow_growth(m: Masters, name: str, location: dict, drawn: Shape) -> float:
    """How far an arrow (drawn with its head ARROW_HEAD as large) is drawn out to be ARROW_LENGTH times as long as Inter's."""
    import math

    direction = POINTING.get(name) or BOTH_WAYS[name]
    n = math.hypot(*direction)

    def length(shape: Shape) -> float:
        along = [(x * direction[0] + y * direction[1]) / n for x, y in shape.points]
        return max(along) - min(along)

    inter = length(m.shape(case(m, name), location))
    if name in DIAGONALS:
        target = length_of(m, "arrowright", location) * ARROW_LENGTH * DIAGONAL_SPAN * math.sqrt(2)
    elif name in ONE_HEADED:
        single = length(m.shape(case(m, ONE_HEADED[name]), location))
        target = single * ARROW_LENGTH * BOTH_LENGTH[name]
    else:
        target = inter * ARROW_LENGTH
    return target - length(drawn)


def arrow(m: Masters, name: str, location: dict, head: float = ARROW_HEAD) -> Shape:
    """
    Inter's arrow, its head `head` as large (its stroke kept), its shaft drawn
    out to ARROW_LENGTH of Inter's length; on the axis. A two-headed one past
    Regular is drawn longer as its heads grow into its shaft, keeping the shaft
    it has at Regular between them, as Inter's letters widen with the weight
    (at TeX's length, ↔'s heads all but met at Black).
    """
    s = sign(m, name, location, head)
    both = name in BOTH_WAYS
    out = drawn_out(s, POINTING.get(name) or BOTH_WAYS[name], arrow_growth(m, name, location, s), both)
    direction = POINTING.get(name) or BOTH_WAYS[name]
    regular = m.axes["wght"].defaultValue
    if both and location["wght"] > regular:
        short = shaft_length(arrow(m, name, {**location, "wght": regular}, head), direction) - shaft_length(out, direction)
        if short > 0:
            out = drawn_out(out, direction, short, True)
    if direction[1]:
        # upright or slanted: its middle on the axis again (a head drawn out on one side moved it)
        out = out.centred(math_axis(m, location))
    return out


def shaft_length(shape: Shape, direction: tuple[float, float]) -> float:
    """
    How far a two-headed arrow's shaft (or shafts) runs between its heads:
    from its middle along the arrow, both ways, as long as the ink across it
    is no wider than there.
    """
    s = shape if direction[0] else shape.map(lambda x, y: (y, x))
    flat = flattened(s)
    x0, _, x1, _ = s.bounds()
    middle = (x0 + x1) / 2

    def across(x: float) -> float:
        ys = column(flat, x)
        return ys[-1] - ys[0] if ys else 0.0

    width, step = across(middle), 2.0
    ends = []
    for way in (1, -1):
        x = middle
        while x0 < x < x1 and across(x + way * step) <= width + 1:
            x += way * step
        ends.append(x)
    return ends[0] - ends[1]


def flattened(shape: Shape, steps: int = 8) -> Shape:
    """Its outline as polygons, its quadratic curves sampled (for measures across curves)."""
    out = []
    for c in shape.contours():
        pts, on, n = c.points, c.on, len(c.points)
        start = next(i for i in range(n) if on[i])
        poly, cur, k = [pts[start]], pts[start], 1
        while k < n + 1:
            j = (start + k) % n
            if on[j]:
                poly.append(pts[j])
                cur, k = pts[j], k + 1
                continue
            ctrl, after = pts[j], (start + k + 1) % n
            # an off-curve point between two: the curve passes halfway between them
            end = pts[after] if on[after] else ((ctrl[0] + pts[after][0]) / 2, (ctrl[1] + pts[after][1]) / 2)
            k += 2 if on[after] else 1
            for i in range(1, steps + 1):
                t = i / steps
                poly.append(tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * e for a, b, e in zip(cur, ctrl, end)))
            cur = end
        out.append(Shape.polygon(poly[:-1], shape.advance))
    return Shape.join(out, shape.advance)


def column(shape: Shape, x: float) -> list[float]:
    """Where an outline (its points taken as a polygon) crosses the vertical at x, bottom to top."""
    ys = []
    for c in shape.contours():
        pts = c.points
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            if (p[0] <= x < q[0]) or (q[0] <= x < p[0]):
                ys.append(p[1] + (x - p[0]) / (q[0] - p[0]) * (q[1] - p[1]))
    return sorted(ys)


def barb_reach(single: Shape) -> float:
    """How far from the axis a one-shafted arrow's barbs reach inside (their inner ends: the second farthest points)."""
    x_lo, _, x_hi, _ = single.bounds()
    axis = max(single.points, key=lambda p: p[0])[1] if sum(abs(x - x_hi) < 0.5 for x, _ in single.points) == 1 else min(single.points, key=lambda p: p[0])[1]
    above = sorted((y - axis for _, y in single.points if y > axis), reverse=True)
    return above[1]




def doubled(single: Shape, space: float, bar: float) -> Shape:
    """
    A one-shafted arrow (one contour, its head or heads Inter's, with their
    junctions: the shaft's edges flow into the barbs and vanish to a point)
    with two shafts `bar` thick and `space` apart: its shaft's edges moved out,
    each junction sliding along its barb with them (so it is kept, on both
    sides of the pair), and the space between the shafts cut from the tail (or
    the other head) to the head's inner corner.
    """
    pts, on, ends = list(single.points), list(single.on), list(single.ends)
    x_lo, _, x_hi, _ = single.bounds()
    centre = (x_lo + x_hi) / 2
    # a head ends in one point (its tip, on the axis); a tail is flat (two points)
    tips = {side: [p for p in pts if abs(p[0] - (x_hi if side == "right" else x_lo)) < 0.5] for side in ("right", "left")}
    heads = {side: len(found) == 1 for side, found in tips.items()}
    axis = next(found[0][1] for side, found in tips.items() if heads[side])
    edges = column(single, centre)
    d = space / 2 + bar - (edges[-1] - edges[0]) / 2

    keep, slope, inner = set(), {}, {}
    for side in ("right", "left"):
        if not heads[side]:
            continue
        tip_x = x_hi if side == "right" else x_lo
        for up in (True, False):
            # a barb's end: its two points farthest from the axis
            mine = [i for i, p in enumerate(pts) if (p[0] > centre) == (side == "right") and (p[1] > axis) == up]
            end_cut = sorted(mine, key=lambda i: abs(pts[i][1] - axis))[-2:]
            keep |= set(end_cut)
            far, near = sorted(end_cut, key=lambda i: abs(pts[i][1] - axis))[::-1]
            slope[side] = abs(pts[far][0] - tip_x) / abs(pts[far][1] - axis)
            inner[(side, up)] = pts[near]

    moved = []
    for i, (x, y) in enumerate(pts):
        if abs(y - axis) < 0.5 or i in keep:
            moved.append((x, y))
            continue
        dy = d if y > axis else -d
        side = "right" if x > centre else "left"
        # a junction slides along its barb (towards the tail); a flat tail only grows
        dx = (-1 if side == "right" else 1) * d * slope[side] if heads[side] else 0.0
        moved.append((x + dx, y + dy))

    def corner(side: str, up: bool, y: float) -> tuple[float, float]:
        """Where a barb's inner edge (from its inner end, along its slant) reaches height y."""
        px, py = inner[(side, up)]
        return (px + (1 if side == "right" else -1) * abs(py - y) * slope[side], y)

    # each junction made smaller about its corner (where the shaft's edge meets the barb's) when the barb is too
    # short for it now (a shaft out there meets the barb nearer its end)
    for side in ("right", "left"):
        if not heads[side]:
            continue
        for up in (True, False):
            sign_ = 1 if up else -1
            c = corner(side, up, axis + sign_ * (space / 2 + bar))
            quarter = [i for i, (x, y) in enumerate(pts) if i not in keep and abs(y - axis) >= 0.5
                       and (x > centre) == (side == "right") and (y > axis) == up]
            if not quarter:
                continue
            reach = max(abs(moved[i][1] - c[1]) for i in quarter if (moved[i][1] - c[1]) * sign_ > 0) if any(
                (moved[i][1] - c[1]) * sign_ > 0 for i in quarter) else 0.0
            room = max(0.0, (inner[(side, up)][1] - c[1]) * sign_)
            k = min(1.0, 0.8 * room / reach) if reach else 1.0
            for i in quarter:
                x, y = moved[i]
                moved[i] = (c[0] + (x - c[0]) * k, c[1] + (y - c[1]) * k)

    top, bottom = axis + space / 2, axis - space / 2
    if heads["right"] and heads["left"]:
        # a slot from one head's inner corner to the other's
        slot = [corner("left", True, top), corner("right", True, top), corner("right", True, axis),
                corner("right", False, bottom), corner("left", False, bottom), corner("left", True, axis)]
        hole = list(reversed(slot))
        return Shape(moved + hole, on + [True] * len(hole), ends + [len(moved) + len(hole) - 1], single.advance)
    side = "right" if heads["right"] else "left"
    tail_x = x_lo if side == "right" else x_hi
    # a notch from the flat tail to the head's inner corner, between the tail's two points
    lo_i, hi_i = sorted((i for i, p in enumerate(moved) if abs(p[0] - tail_x) < 0.5), key=lambda i: moved[i][1])
    notch = [(tail_x, bottom), corner(side, False, bottom), corner(side, True, axis), corner(side, True, top), (tail_x, top)]
    at = hi_i if (lo_i + 1) % len(moved) == hi_i else lo_i
    if at == lo_i:
        notch.reverse()
    return Shape(moved[:at] + notch + moved[at:], on[:at] + [True] * len(notch) + on[at:], [e + len(notch) for e in ends], single.advance)


def even_bars(m: Masters, name: str, location: dict) -> Shape:
    """
    A sign at a location (sign()), its horizontal bars as wide as the minus
    sign's there (+ square); ≤ ≥'s as wide as their chevron (it grows less).
    = is Inter's drawn out, not scaled (its gap kept: gap()); ≈'s waves as
    far apart as its bars; arrows Inter's, drawn out (arrow()), the double
    ones too (their own shafts and heads).
    """
    if name == "equal":
        minus = sign(m, "minus", location)
        x0, _, x1, _ = minus.bounds()
        out = m.shape(case(m, name), location).bars_to(x0, x1).moved(0, -axis_drop(m, location))
        out.advance = minus.advance
        return out
    s = arrow(m, name, location) if name in POINTING or name in BOTH_WAYS else sign(m, name, location)
    if name in POINTING or name in BOTH_WAYS:
        return s
    if name == "approxequal":
        wave = max(s.contours(), key=lambda c: c.bounds()[3])
        low, high = sorted(even_bars(m, "equal", location).contours(), key=lambda c: c.bounds()[1])
        pitch = (high.bounds()[1] + high.bounds()[3] - low.bounds()[1] - low.bounds()[3]) / 2
        axis = math_axis(m, location)
        return Shape.join([wave.centred(axis - pitch / 2), wave.centred(axis + pitch / 2)], s.advance)
    if name not in BARRED:
        return s
    if name in RELATIONS:
        chevron = max(s.contours(), key=lambda c: len(c.points)).bounds()
        return s.bars_to(chevron[0], chevron[2])
    x0, y0, x1, y1 = sign(m, "minus", location).bounds()
    return s.bars_to(x0, x1, (y0 + y1) / 2 if name == "plus" else None)


def operator_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, [n for name in OPERATORS.values() for n in (name, f"{name}.case")] + ["minus.case"])
    return [
        m.glyph(f"{name}.math", [even_bars(m, name, m.lighter(master, OFFSET)) for master in m.masters], cp)
        for cp, name in OPERATORS.items()
    ]
