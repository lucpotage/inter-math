"""
Delimiters ( ) [ ] { } at every size, after Inter's.

Math sets brackets taller than text does (Computer Modern: 1 em, to Inter's
0.8), and KaTeX grows them for \\left … \\right through four sizes before
stacking pieces (its fonts KaTeX_Size1-4), taking the first one tall enough for
the content. Inter Math's are as tall as TeX's (NORMAL, the font's own
( ) [ ] { }, then SIZES), and as TeX's they grow wider as they grow taller:
by the power WIDEN of their height over Inter's text bracket's, a power for
each kind, so that every size comes out about as wide as Computer Modern's
(Inter's own proportions at the small ones). All are Inter's case forms,
lowered onto the math axis as the operators are (build/operators.py), and
their stems thin as they grow, from Inter's at the text size to the rule's
(the minus sign's thickness: the fraction bars' and surds') at the largest
and past it (`stroke_weight`: Inter's letters' stems, 3 em tall at Black,
read far heavier than the bars and surds of their formula), each measured on
itself (`own_stroke`):

- ( ): taller and wider, taken at the weight whose stroke, once widened, is
  as thick as that;
- [ ]: the stem drawn out, the arms drawn longer: at every weight at least as
  long as at Regular (Inter's shorten to stubs at Black, where the stem
  eats into them), REACH times as long at the text size, easing to the
  larger sizes' own (`arm_reach`);
- { }: the whole brace larger (hooks and point keep their shape), taken at
  the weight that keeps its stroke, then its two straight stretches drawn out;
- ⌈ ⌉ ⌊ ⌋: the brackets, one arm folded into the stem;
- ⟨ ⟩: two strokes as thick as the brackets' stem, as wide as the
  parentheses, their point cut flat as Inter cuts its < (by FLAT of the
  stroke) and their ends cut level, as ∠ and √ are;
- / \\ (\\big/, \\left/ … \\right\\backslash: KaTeX never stacks them, it
  takes them from its Size fonts at every height): Inter's / and \\ drawn out
  along their slant to each size, the text size's included (1.0 em, as
  TeX's and the parentheses are: Inter's own are 0.77 em), their stroke,
  level ends and side bearings kept (TeX's keep their slant, and grow wider
  as they grow taller), centred as the brackets are; the text size's in an
  advance as wide as = less two thin spaces, its ink in the middle, so that
  \\mathrlap{\\,/}{=} and {=}\\mathllap{/\\,} cross = in its middle (TeX's /
  is set that way); ∕ and ∖ (\\setminus) are the text size's / and \\, as
  TeX's are;
- ⟮ ⟯ ⎰ ⎱ (\\lgroup \\rgroup \\lmoustache \\rmoustache): TeX builds them from
  a brace's pieces, its hooks on a straight stem. Here the brace at that size
  with its point folded into the stem (`pointless`: the curves from the stem
  to the point moved onto the stem's edges, the point's edge cut level across
  it), spaced as the brace; ⎰ ⎱ turn their lower hook the other way about the
  stem, the hooks' white on both sides. (Inter's own ⟯ is a bracket with
  angled ends, and it has no ⟮.)
- ⟦ ⟧ ⦃ ⦄ (\\llbracket \\rrbracket \\lBrace \\rBrace): KaTeX overlaps two of
  its [ or { at a fixed kern, which the stems close as they grow. Here one
  glyph: [ or { at the weight whose stem is a bar of Inter's ǁ, with a second
  stem inside as far from it as ǁ's bars are apart (`double`): ǁ's bars grow
  little and its gap stays open at Black. ⟦'s arms are carried past the
  second stem; ⦃'s hooks run on straight past it as far, as [ 's arms do
  (only their ends move: their bends stay {'s), the second stem straight
  between them, into each hook halfway: { and [ combined. Text size only;
  macros set them (src/index.ts).

Tall, a corner where two full strokes meet reads heavy (the top of [, the
turn of a brace's hook): in the larger sizes a bracket's arms are drawn
lighter (ARM of their thickness) and a brace's hooks taper to their ends
(TAPER of theirs), as large delimiters are drawn.

The larger sizes are fonts of their own, as KaTeX's are. KaTeX has no sizes
of ⟮ ⟯ ⎰ ⎱ (past the text size it stacks Computer Modern's brace pieces):
Inter Math's reach it through a hook of its KaTeX patch (`SIZED_DELIMITERS`
in src/index.ts), as ( [ {'s do.

Past the largest size KaTeX stacks a brace (and ⟮ ⎰) from the Size4 font's
pieces ⎧ ⎨ ⎩ ⎫ ⎬ ⎭, with an image of the straight stem between them as tall as
needed (src/svg.ts draws it as Inter Math's ⎪). Inter Math's pieces are its
largest brace cut level across its stem above and under the point, where
both edges run straight at every master (`brace_cuts`: KaTeX measures the
pieces once, so they keep their heights across the weights): the pieces
stacked with no stem between them are that brace, and a taller brace is it
with both straight stretches drawn out, as at every size. They share one
frame, the stem in the middle of the brace's advance (KaTeX stacks them flush
left); ⎪ is that stem as tall as KaTeX's (STEM_PIECE: the steps in which
KaTeX grows a brace). They keep the text optical size at every size: the stem
image between them can't follow the optical size, and at 32 the stem sits
elsewhere (the joints would show).

The corners ┌ ┐ └ ┘ (\\ulcorner \\urcorner \\llcorner \\lrcorner, at the code
points of KaTeX's AMS font) are the corner of Inter's [ (its stem and arm, as
thick), with arms CORNER of the cap height long as TeX's; the upper ones hang
from the cap height (Inter's ascenders: TeX's hang from its), the lower ones
stand on the baseline, ['s side bearings around them. Text size only, as TeX's.
"""

import math

from operators import axis_drop, column, even_bars, pipe_bars
from variable import Masters, NewGlyph, Shape

# total heights (em): the normal size (the font's), then KaTeX's sizes (TeX's)
NORMAL = 1.0
SIZES = {1: 1.2, 2: 1.8, 3: 2.4, 4: 3.0}
CURVED = {0x0028: "parenleft", 0x0029: "parenright"}
STRAIGHT = {0x005B: "bracketleft", 0x005D: "bracketright"}
BRACES = {0x007B: "braceleft", 0x007D: "braceright"}
# code point → (the bracket it is drawn from, the arm it keeps)
FLOORS = {0x2308: ("bracketleft", "top"), 0x2309: ("bracketright", "top"), 0x230A: ("bracketleft", "bottom"), 0x230B: ("bracketright", "bottom")}
ANGLES = {0x27E8: "angleleft", 0x27E9: "angleright"}
# / \, drawn out to every size, the text size's included: code point → Inter's glyph
SLASHES = {0x002F: "slash", 0x005C: "backslash"}
# ∕ ∖ (\setminus): the text size's / \ (TeX's are the same glyphs)
TWINS = {0x2215: "slash", 0x2216: "backslash"}
# ⟮ ⟯ ⎰ ⎱: code point → the brace it is drawn from
GROUPS = {0x27EE: "braceleft", 0x27EF: "braceright", 0x23B0: "braceleft", 0x23B1: "braceright"}
# ┌ ┐ └ ┘ (KaTeX's AMS font): code point → (on the right, at the bottom)
CORNERS = {0x250C: (False, False), 0x2510: (True, False), 0x2514: (False, True), 0x2518: (True, True)}
# what the ones Inter lacks are drawn from (the workbench shows it, /dev/symbols): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x2215: ("/ drawn out along its slant to 1.0 em, as / is (TeX's ∕ is its /)", "slash"),
    0x2216: ("\\ drawn out along its slant to 1.0 em, as \\backslash is (TeX's \\setminus is its \\backslash)", "backslash"),
    0x2308: ("[ keeping its top arm", "bracketleft"),
    0x2309: ("] keeping its top arm", "bracketright"),
    0x230A: ("[ keeping its bottom arm", "bracketleft"),
    0x230B: ("] keeping its bottom arm", "bracketright"),
    0x27E8: ("two strokes as thick as ['s, the point cut as <'s", "less bracketleft"),
    0x27E9: ("⟨ mirrored", "greater bracketright"),
    0x27EE: ("{ without its point: its hooks on a straight stem, as TeX builds ⟮ from a brace's pieces", "braceleft"),
    0x27EF: ("} without its point (Inter's ⟯ is a bracket)", "braceright"),
    0x23B0: ("{ without its point, its lower hook turned the other way (TeX's ⎰: a brace's pieces)", "braceleft braceright"),
    0x23B1: ("⎰ mirrored", "braceright braceleft"),
    0x250C: ("the top of [: its stem and arm, as long as TeX's ⌜", "bracketleft"),
    0x2510: ("┌ mirrored", "bracketright"),
    0x2514: ("the bottom of [: its stem and arm, as long as TeX's ⌞", "bracketleft"),
    0x2518: ("└ mirrored", "bracketright"),
    0x23A7: ("the top of Inter Math's largest {: its hook, cut level across the stem", "braceleft"),
    0x23A8: ("the middle of Inter Math's largest {: its point, cut level across the stem", "braceleft"),
    0x23A9: ("the bottom of Inter Math's largest {: its hook", "braceleft"),
    0x23AB: ("the top of Inter Math's largest }", "braceright"),
    0x23AC: ("the middle of Inter Math's largest }", "braceright"),
    0x23AD: ("the bottom of Inter Math's largest }", "braceright"),
    0x23AA: ("the stem of Inter Math's largest { (KaTeX draws it between the pieces, as tall as needed)", "braceleft"),
    0x27E6: ("[ with a second stem inside, its stems and the white between them ǁ's", "bracketleft pipedbl"),
    0x27E7: ("⟦ mirrored", "bracketright pipedbl"),
    0x2983: ("{ with [ 's straight stem inside, its hooks run on straight past it as [ 's arms, its stems and the white between them ǁ's", "braceleft bracketleft pipedbl"),
    0x2984: ("⦃ mirrored", "braceright pipedbl"),
}
# the corners' arms against the cap height (TeX's: 388 to 683)
CORNER = 388 / 683
# KaTeX's pieces of a tall brace (Size4: ⎧ ⎨ ⎩ ⎫ ⎬ ⎭, and the straight stem ⎪ it draws between them as tall as
# needed): code point → (the brace, the part)
PIECES = {
    0x23A7: ("braceleft", "top"), 0x23A8: ("braceleft", "middle"), 0x23A9: ("braceleft", "bottom"),
    0x23AB: ("braceright", "top"), 0x23AC: ("braceright", "middle"), 0x23AD: ("braceright", "bottom"),
    0x23AA: ("braceleft", "stem"),
}
# the stem piece's height, KaTeX's ⎪ (em): the steps in which KaTeX grows a tall brace
STEM_PIECE = (-0.01, 0.31)
# the height of an angle bracket's flat point, in strokes (Inter's <: 126 for a 175 stroke)
FLAT = 0.72
# n times as tall as Inter's text bracket: n ** WIDEN times wider
# (the whole parenthesis or brace; the arms of a bracket)
WIDEN = {**dict.fromkeys(CURVED, 0.75), **dict.fromkeys({**STRAIGHT, **FLOORS}, 1.15), **dict.fromkeys(BRACES, 0.7)}
# ⟦ ⟧ ⦃ ⦄ (\\llbracket \\rrbracket \\lBrace \\rBrace): KaTeX overlaps two glyphs at a fixed kern ([\\mkern-3.2mu[),
# whose gap Inter Math's strokes close at heavy weights. Inter Math draws them, their two stems and the white between
# after Inter's ǁ (its bars grow less than a stem and keep their gap: 0.109 to 0.035 em from Thin to Black)
DOUBLES = {0x27E6: ("bracketleft", 0x005B), 0x2983: ("braceleft", 0x007B)}
DOUBLE_MIRRORS = {0x27E7: 0x27E6, 0x2984: 0x2983}
# a bracket's arms (beyond its stem): at every weight as long as Inter's at Regular (they shorten at Black, where its
# stem thickens inward), and REACH times that at the text size, less as the bracket grows, as long as the larger
# sizes made them from 3 times on (Inter's arms are short beside math's heavier strokes; TeX's shorten against the
# height in its larger sizes)
REACH = 1.25
# the larger sizes: a bracket's arms, a brace's hook ends, as much of their thickness
ARM = 0.75
TAPER = 0.7


def own_stroke(m: Masters, name: str, master: dict, wght: float) -> float:
    """
    A delimiter's stroke on Inter's glyph `name` at a weight (of the master's
    optical size): across a parenthesis's middle (where it runs upright) or a
    bracket's stem, across a brace's straight stretches, across a slash's
    slant.
    """
    s = m.shape(name, master, wght)
    x0, y0, x1, y1 = s.bounds()
    y = straight_stretches(s)[0] if name.startswith("brace") else (y0 + y1) / 2
    left, right = s.runs(y)[0]
    if name in SLASHES.values():
        lean = (min(x for x, y in s.points if abs(y - y1) < 0.5) - min(x for x, y in s.points if abs(y - y0) < 0.5)) / (y1 - y0)
        return (right - left) / math.hypot(1, lean)
    return right - left


def stroke_weight(m: Masters, name: str, master: dict, height: float, scale: float = 1.0) -> float:
    """
    The weight a delimiter `height` em tall is drawn at, from Inter's glyph
    `name` (`scale` times as large across: a parenthesis or a brace is
    widened): its own stroke (`own_stroke`) the master's at the text size,
    thinning as it grows towards the rule's (the minus sign's thickness, the
    fraction bars' and the surds'), the rule's from the largest size up (its
    tall forms are drawn out from it). Inter's brackets carry its letters'
    stems: 3 em tall at Black (0.17 em thick) they read far heavier than the
    bars and surds of the formula (0.14 em). Measured on the delimiter
    itself: Inter's 1's stem, which the strokes were first matched by, gains
    weight at another pace than a parenthesis's or a brace's, most under
    Thin, where the larger sizes are drawn (the widening takes their weight
    there): at Thin they came out a fifth heavier than the rule, at Regular
    the brackets and slashes a tenth lighter.
    """
    t = min(max((height - NORMAL) / (SIZES[4] - NORMAL), 0.0), 1.0)
    if t == 0 and scale == 1:
        return master["wght"]
    own = own_stroke(m, name, master, master["wght"])
    _, y0, _, y1 = m.shape("minus.case", master).bounds()
    return m.weight_for(lambda w: own_stroke(m, name, master, w) * scale, own + (y1 - y0 - own) * t)


def straight_stretches(shape: Shape) -> tuple[float, float]:
    """The middle heights of a brace's upper and lower straight stretches (vertical lines between on-curve points)."""
    middles = []
    for c in shape.contours():
        pts, on = c.points, c.on
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            (x0, y0), (x1, y1) = pts[i], pts[j]
            if on[i] and on[j] and abs(x1 - x0) < 1 and abs(y1 - y0) > 50:
                middles.append((y0 + y1) / 2)
    _, b0, _, b1 = shape.bounds()
    centre, near = (b0 + b1) / 2, (b1 - b0) * 0.15
    # away from the point (whose edges are vertical too)
    upper = [y for y in middles if y > centre + near]
    lower = [y for y in middles if y < centre - near]
    return sum(upper) / len(upper), sum(lower) / len(lower)


def rect(x0: float, y0: float, x1: float, y1: float) -> Shape:
    return Shape([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], [True] * 4, [3], 0)


def double(m: Masters, cp: int, master: dict, target: float) -> Shape:
    """
    ⟦ or ⦃, `target` units tall: [ or { at the weight whose stem is as thick
    as a bar of Inter's ǁ, with a second, straight stem inside it as far from
    the first as ǁ's bars are apart. ⟦'s arms and ⦃'s hooks are carried past
    it by as much (⦃'s hooks ended on it, short beside the doubled stem): a
    hook runs on straight, as [ 's arm, its bend {'s; the second stem
    between them, into each halfway, square as [ 's.
    """
    name, base = DOUBLES[cp]
    bar, space = pipe_bars(m, master)

    def at(wght: float) -> Shape:
        return drawn(m, name, base, {**master, "wght": wght}, target, False)

    def stem(s: Shape) -> tuple[float, float]:
        _, y0, _, y1 = s.bounds()
        level = straight_stretches(s)[0] if base == 0x007B else (y0 + y1) / 2
        return s.span(level)

    s = at(m.weight_for(lambda w: (lambda e: e[1] - e[0])(stem(at(w))), bar))
    left, right = stem(s)
    x0, y0, x1, y1 = s.bounds()
    inner = (right + space, right + space + bar)
    if base == 0x005B:
        # the arms carried past the second stem by as much as it takes
        s = s.map(lambda x, y: (x + space + bar if x > right + 0.5 else x, y))
        s.advance += space + bar
        bottom, top = y0, y1
    else:
        # the hooks run on straight past it as far, as [ 's arms do: only their ends move (they end level), their bends
        # stay {'s (drawn out with them, the bends stretched); the stem between them, into each halfway
        s = s.map(lambda x, y: (x + space + bar if abs(x - x1) < 0.5 else x, y))
        s.advance += space + bar
        ys = column(s, (inner[0] + inner[1]) / 2)
        bottom, top = ((ys[0] + ys[1]) / 2, (ys[-2] + ys[-1]) / 2) if len(ys) >= 4 else (y0, y1)
    return Shape.join([s, rect(inner[0], bottom, inner[1], top)], s.advance)


def arm_reach(m: Masters, name: str, master: dict, grown: float) -> float:
    """How much longer than Inter's at the master a bracket's arms are drawn (REACH): never shorter."""

    def clear(location: dict) -> float:
        s = m.shape(f"{name}.case", location)
        x0, y0, x1, y1 = s.bounds()
        left, right = s.span((y0 + y1) / 2)
        return max(x1 - right, left - x0)

    regular = {**master, "wght": m.axes["wght"].defaultValue}
    reach = max(1.0, REACH - (REACH - 1) * (grown - 1) / 2)
    return max(1.0, clear(regular) * reach / clear(master))


def widened(shape: Shape, left: float, right: float, wide: float) -> Shape:
    """What lies beyond a stem's edges `wide` times farther from it, the side bearings kept."""
    x0, _, x1, _ = shape.bounds()
    out = shape.map(lambda x, y: (right + (x - right) * wide if x > right else left - (left - x) * wide if x < left else x, y))
    grown = (left - x0) * (wide - 1)
    out = out.moved(grown, 0)
    out.advance = shape.advance + grown + (x1 - right) * (wide - 1)
    return out


def lighter_arms(shape: Shape) -> Shape:
    """A bracket with its arms ARM of their thickness (their inner edges moved out)."""
    ys = sorted({y for _, y in shape.points})
    top, inner_top, inner_bottom, bottom = ys[-1], ys[-2], ys[1], ys[0]
    thin_top, thin_bottom = top - (top - inner_top) * ARM, bottom + (inner_bottom - bottom) * ARM
    return shape.map(lambda x, y: (x, thin_top if y == inner_top else thin_bottom if y == inner_bottom else y))


def tapered(shape: Shape, upper: float, lower: float) -> Shape:
    """A brace whose hooks thin towards their ends to TAPER of their thickness (their inner edges moved out)."""
    x0, y0, x1, y1 = shape.bounds()
    left, right = shape.span(upper)
    # the hooks end at the top and bottom, the point is in the middle
    towards = 1 if max(y for x, y in shape.points if abs(x - x1) < 1) > upper else -1
    end = x1 if towards > 0 else x0
    start = right if towards > 0 else left
    begin = start + (end - start) * 0.35
    ends = [p for p in shape.points if abs(p[0] - end) < 1]
    top_inner = min(y for _, y in ends if y > upper)
    bottom_inner = max(y for _, y in ends if y < lower)
    thin_top = (y1 - top_inner) * (1 - TAPER)
    thin_bottom = (bottom_inner - y0) * (1 - TAPER)

    def edit(x, y):
        along = (x - begin) / (end - begin)
        if along <= 0:
            return x, y
        if upper < y < (y1 + top_inner) / 2:
            return x, y + thin_top * along
        if (y0 + bottom_inner) / 2 < y < lower:
            return x, y - thin_bottom * along
        return x, y

    return shape.map(edit)


def stem_edges(brace: Shape) -> tuple[float, float]:
    """A left brace's stem: its left and right edges (along its upper straight stretch)."""
    upper, _ = straight_stretches(brace)
    return brace.span(upper)


def pointless(brace: Shape) -> Shape:
    """
    A left brace without its point: in each half, the curves from the stem to
    the point moved onto the stem's edges and the point's edge cut level
    across the stem where the other half begins (the halves overlap there, as
    the brace's do; the patch between them goes across the stem).
    """
    left, right = stem_edges(brace)
    top = brace.bounds()[3]
    out = []
    for c in brace.contours():
        pts, on, n = list(c.points), c.on, len(c.points)
        if n == 4:
            lo = min(x for x, _ in pts)
            out.append(c.map(lambda x, y: (left if x == lo else right, y)))
            continue
        # the point's edge: two on-curve points in a row, the farthest out
        x0 = min(x for x, _ in pts)
        i = next(k for k in range(n) if on[k] and on[(k + 1) % n] and abs(pts[k][0] - x0) < 1 and abs(pts[(k + 1) % n][0] - x0) < 1)
        j = (i + 1) % n
        # the upper half down to the point's lower corner, the lower half up to its upper one
        ys = (pts[i][1], pts[j][1])
        cut = min(ys) if c.bounds()[3] == top else max(ys)
        for corner_, step in ((i, -1), (j, 1)):
            # from that corner along the curve to the stem: its points onto the edge it reaches
            k, path = (corner_ + step) % n, []
            while not (on[k] and min(abs(pts[k][0] - left), abs(pts[k][0] - right)) < 1):
                path.append(k)
                k = (k + step) % n
            edge = left if abs(pts[k][0] - left) < 1 else right
            for p in path:
                pts[p] = (edge, pts[p][1])
            pts[corner_] = (edge, cut)
        out.append(Shape(pts, list(on), list(c.ends), c.advance))
    return Shape.join(out, brace.advance)


def group(m: Masters, cp: int, master: dict, target: float, large: bool, em: float | None = None) -> Shape:
    """⟮ ⟯ ⎰ ⎱ `target` units tall: the brace without its point, spaced as the brace."""
    name = GROUPS[cp]
    brace = drawn(m, name, 0x7B if name == "braceleft" else 0x7D, master, target, large, em)
    # drawn as from a left brace (hooks to the right), mirrored back for the right ones
    if name == "braceright":
        brace = brace.mirrored()
    left, right = stem_edges(brace)
    x0, y0, x1, _ = brace.bounds()
    flat = pointless(brace)
    if cp in (0x27EE, 0x27EF):
        # the brace's white outside the stem, as outside its point
        out = flat.moved(x0 - left, 0)
        out.advance = brace.advance - (left - x0)
    else:
        # the lower hook turned the other way about the stem (a mirror reverses a contour: its points too)
        parts = []
        for c in flat.contours():
            if len(c.points) > 4 and c.bounds()[1] == y0:
                c = Shape([(left + right - x, y) for x, y in reversed(c.points)], list(reversed(c.on)), c.ends, c.advance)
            parts.append(c)
        side = brace.advance - x1
        out = Shape.join(parts, 0)
        ix0, _, ix1, _ = out.bounds()
        out = out.moved(side - ix0, 0)
        out.advance = ix1 - ix0 + 2 * side
    return out.mirrored() if name == "braceright" else out


def clipped(c: Shape, cut: float, above: bool) -> Shape:
    """
    One contour of a brace cut level at `cut`, keeping what lies above it (or
    below): each run of points on the other side folded onto the cut, those
    before the run's turn (its two on-curve points in a row farthest from the
    stem: the point's edge, a hook's end) onto the stem's edge the run leaves
    by, the rest onto the edge it comes back by. The points stay: every master
    keeps them.
    """
    pts, on, n = list(c.points), c.on, len(c.points)
    gone = [(y < cut) if above else (y > cut) for _, y in pts]
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
        leaves, returns = pts[(run[0] - 1) % n][0], pts[k][0]
        stem = (leaves + returns) / 2
        pairs = [j for j in range(len(run) - 1) if on[run[j]] and on[run[j + 1]] and abs(pts[run[j]][0] - pts[run[j + 1]][0]) < 1]
        turn = max(pairs, key=lambda j: abs(pts[run[j]][0] - stem))
        for j, i in enumerate(run):
            pts[i] = (leaves if j <= turn else returns, cut)
    return Shape(pts, list(on), list(c.ends), c.advance)


def straight_edges(brace: Shape) -> tuple[tuple[float, float], tuple[float, float]]:
    """A left brace's stem: where both its edges run straight, above its point and under it (y from, to)."""
    left, right = stem_edges(brace)
    _, y0, _, y1 = brace.bounds()
    centre = (y0 + y1) / 2
    upper, lower = [y0, y1], [y0, y1]
    for edge in (left, right):
        spans = []
        for c in brace.contours():
            pts, on = c.points, c.on
            for i in range(len(pts)):
                j = (i + 1) % len(pts)
                if on[i] and on[j] and abs(pts[i][0] - edge) < 1 and abs(pts[j][0] - edge) < 1:
                    spans.append(sorted((pts[i][1], pts[j][1])))
        up = max((s for s in spans if s[0] > centre), key=lambda s: s[1] - s[0])
        down = max((s for s in spans if s[1] < centre), key=lambda s: s[1] - s[0])
        upper = [max(upper[0], up[0]), min(upper[1], up[1])]
        lower = [max(lower[0], down[0]), min(lower[1], down[1])]
    return (upper[0], upper[1]), (lower[0], lower[1])


def brace_cuts(m: Masters, upem: int) -> tuple[float, float]:
    """
    Where the largest braces are cut into KaTeX's pieces: in the middle of
    their stem's straight stretches above and under the point, as straight at
    every master and in both braces (KaTeX measures the pieces once: they keep
    their heights across the weights).
    """
    upper, lower = [-1e9, 1e9], [-1e9, 1e9]
    for master in m.masters:
        for name, cp in (("braceleft", 0x7B), ("braceright", 0x7D)):
            brace = drawn(m, name, cp, master, SIZES[4] * upem, True, upem)
            (u0, u1), (l0, l1) = straight_edges(brace if name == "braceleft" else brace.mirrored())
            upper = [max(upper[0], u0), min(upper[1], u1)]
            lower = [max(lower[0], l0), min(lower[1], l1)]
    assert upper[1] - upper[0] > 0.05 * upem and lower[1] - lower[0] > 0.05 * upem, "the braces' stems are not straight across the masters"
    return (upper[0] + upper[1]) / 2, (lower[0] + lower[1]) / 2


def piece(m: Masters, cp: int, master: dict, cuts: tuple[float, float], upem: int) -> Shape:
    """
    A piece of a tall brace at a master: the largest brace cut level across its
    stem (top, middle, bottom), or its stem as tall as KaTeX's ⎪. All in one
    frame, the stem in the middle of the brace's advance: KaTeX stacks them
    flush left.
    """
    name, part = PIECES[cp]
    brace = drawn(m, name, 0x7B if name == "braceleft" else 0x7D, master, SIZES[4] * upem, True, upem)
    if name == "braceright":
        brace = brace.mirrored()
    left, right = stem_edges(brace)
    upper_cut, lower_cut = cuts
    top = brace.bounds()[3]
    halves = [c for c in brace.contours() if len(c.points) > 4]
    upper = next(c for c in halves if c.bounds()[3] == top)
    lower = next(c for c in halves if c is not upper)
    patch = next(c for c in brace.contours() if len(c.points) == 4)
    # set on the baseline by their cuts, as KaTeX's are (⎧ ⎨ stand on it, ⎩ hangs from it): KaTeX stacks them by
    # their metrics, which are their ink's, so the cuts meet exactly
    if part == "top":
        s = clipped(upper, upper_cut, above=True).moved(0, -upper_cut)
    elif part == "bottom":
        s = clipped(lower, lower_cut, above=False).moved(0, -lower_cut)
    elif part == "middle":
        s = Shape.join([clipped(upper, upper_cut, above=False), clipped(lower, lower_cut, above=True), patch], 0).moved(0, -lower_cut)
    else:
        y0, y1 = (v * upem for v in STEM_PIECE)
        s = Shape.polygon([(left, y0), (left, y1), (right, y1), (right, y0)])
    s = s.moved(brace.advance / 2 - (left + right) / 2, 0)
    s.advance = brace.advance
    return s.mirrored() if name == "braceright" else s


def corner(m: Masters, cp: int, master: dict) -> Shape:
    """┌ ┐ └ ┘: the stem and arm of Inter's [ meeting, CORNER of the cap height long, with ['s side bearings."""
    right, bottom = CORNERS[cp]
    b = m.shape("bracketleft.case", master)
    x0, y0, x1, y1 = b.bounds()
    left_edge, right_edge = b.span((y0 + y1) / 2)
    t = right_edge - left_edge
    ys = sorted({y for _, y in b.points})
    a = ys[-1] - ys[-2]
    cap = m.shape("H", master).bounds()[3]
    arm = CORNER * cap
    if bottom:
        pts = [(0, 0), (0, arm), (t, arm), (t, a), (arm, a), (arm, 0)]
    else:
        pts = [(0, cap - arm), (0, cap), (arm, cap), (arm, cap - a), (t, cap - a), (t, cap - arm)]
    s = Shape.polygon([(x + x0, y) for x, y in pts], x0 + arm + b.advance - x1)
    return s.mirrored() if right else s


def angle(m: Masters, cp: int, master: dict, target: float, large: bool, em: float | None = None) -> Shape:
    """⟨ (or ⟩, mirrored), `target` units tall (given the em, as thin as the brackets that tall: `stroke_weight`)."""
    paren = drawn(m, "parenleft", 0x28, master, target, large, em)
    px0, py0, px1, py1 = paren.bounds()
    centre, half = (py0 + py1) / 2, target / 2
    bracket = m.shape("bracketleft.case", master, stroke_weight(m, "bracketleft.case", master, target / em) if em else master["wght"])
    _, b0, _, b1 = bracket.bounds()
    left, right = bracket.span((b0 + b1) / 2)
    t = right - left
    v = t * FLAT / 2
    x0, x1 = px0, px1
    across = t
    for _ in range(4):  # the horizontal width of a stroke depends on its slant
        run, rise = (x1 - across) - x0, half - v
        across = t * (run * run + rise * rise) ** 0.5 / rise
    a, b, c = (x0, centre + v), (x1 - across, centre + half), (x1, centre + half)
    s = half / (half - v)
    d = (c[0] - (b[0] - a[0]) * s, centre)
    e, f, g = (x1, centre - half), (x1 - across, centre - half), (x0, centre - v)
    shape = Shape.polygon([a, b, c, d, e, f, g], paren.advance)
    return shape if cp == 0x27E8 else shape.mirrored()


def slash(m: Masters, name: str, master: dict, target: float, within: float = 0.0, em: float | None = None) -> Shape:
    """
    Inter's / (or \\, `name`) `target` units tall at a master: its ends moved
    along its slant (its stroke and level ends kept; given the em, as thin as
    the brackets that tall: `stroke_weight`), centred as the brackets are, its
    side bearings kept; in an advance `within` wide at least, its ink in the
    middle.
    """
    s = m.shape(name, master, stroke_weight(m, name, master, target / em) if em else master["wght"])
    x0, y0, x1, y1 = s.bounds()
    assert all(abs(y - y0) < 0.5 or abs(y - y1) < 0.5 for _, y in s.points), f"{name} is not a stroke cut level at both ends"
    # how far its edges run across per unit up (a slash leans right, a backslash left)
    lean = (min(x for x, y in s.points if abs(y - y1) < 0.5) - min(x for x, y in s.points if abs(y - y0) < 0.5)) / (y1 - y0)
    base = m.shape("parenleft.case", master).moved(0, -axis_drop(m, master))
    _, b0, _, b1 = base.bounds()
    top, bottom = (b0 + b1 + target) / 2, (b0 + b1 - target) / 2
    out = s.map(lambda x, y: (x + lean * (top - y1), top) if abs(y - y1) < 0.5 else (x + lean * (bottom - y0), bottom))
    ox0, _, ox1, _ = out.bounds()
    out = out.moved(x0 - ox0, 0)
    out.advance = s.advance + (ox1 - ox0) - (x1 - x0)
    if within > out.advance:
        out = out.moved((within - out.advance) / 2, 0)
        out.advance = within
    return out


def drawn(m: Masters, name: str, cp: int, master: dict, target: float, large: bool, em: float | None = None) -> Shape:
    """
    A delimiter `target` units tall at a master, centred where Inter's is (`large`: one of KaTeX's sizes); given the
    em, its stems thinner the taller it is (`stroke_weight`).
    """
    if cp in ANGLES:
        return angle(m, cp, master, target, large, em)
    if cp in GROUPS:
        return group(m, cp, master, target, large, em)
    keep = None
    if cp in FLOORS:
        name, keep = FLOORS[cp]
    # on the math axis: Inter's case forms, lowered as its operators are (build/operators.py)
    base = m.shape(f"{name}.case", master).moved(0, -axis_drop(m, master))
    _, y0, _, y1 = base.bounds()
    centre = (y0 + y1) / 2
    wide = (target / (y1 - y0)) ** WIDEN[cp]
    height = target / em if em else NORMAL
    if cp in CURVED:
        # at the weight whose stroke, widened, is the stroke weight's
        s = m.shape(f"{name}.case", master, stroke_weight(m, f"{name}.case", master, height, wide))
        _, sy0, _, sy1 = s.bounds()
        sc, k = (sy0 + sy1) / 2, target / (sy1 - sy0)
        shaped = s.map(lambda x, y: (x * wide, centre + (y - sc) * k))
        # as wide as Inter's at the master, widened (a lighter weight is narrower)
        shaped.advance = base.advance * wide
        shaped = shaped.moved((shaped.advance - s.advance * wide) / 2, 0)
        return shaped
    if cp in BRACES:
        s = m.shape(f"{name}.case", master, stroke_weight(m, f"{name}.case", master, height, wide)).scaled(wide)
        _, sy0, _, sy1 = s.bounds()
        s = s.moved(0, centre - (sy0 + sy1) / 2)
        upper, lower = straight_stretches(s)
        reach = (target - (sy1 - sy0)) / 2
        if large:
            s = tapered(s, upper, lower)
        return s.map(lambda x, y: (x, y + reach if y > upper else y - reach if y < lower else y))
    # a bracket: Inter's at the stroke weight, centred where the master's is
    stroked = stroke_weight(m, f"{name}.case", master, height)
    if stroked != master["wght"]:
        base = m.shape(f"{name}.case", master, stroked).moved(0, -axis_drop(m, master))
        _, sy0, _, sy1 = base.bounds()
        base = base.moved(0, centre - (sy0 + sy1) / 2)
        y0, y1 = centre - (sy1 - sy0) / 2, centre + (sy1 - sy0) / 2
    grow = (target - (y1 - y0)) / 2
    left, right = base.span(centre)
    wide *= arm_reach(m, name, {**master, "wght": stroked}, target / (y1 - y0))
    out = widened(lighter_arms(base) if large else base, left, right, wide)
    out = out.map(lambda x, y: (x, y + grow if y > centre else y - grow))
    if keep:
        # the other arm folds into the stem (its points onto the stem's edge)
        ox0, _, ox1, _ = out.bounds()
        sl, sr = out.span(centre)

        def fold(x, y):
            if (y < centre) == (keep == "top"):
                return (sr if x > sr else sl if x < sl else x), y
            return x, y

        out = out.map(fold)
    return out


def delimiter_glyphs(path, upem: int) -> dict[int, list[NewGlyph]]:
    """
    Each size's glyphs, mapped to their code points: 0 for the font's own
    (named .math, with the corners), 1-4 for KaTeX's Size fonts (named .size1 …).
    """
    names = {**CURVED, **STRAIGHT, **BRACES, **{cp: f"{n}{'ceiling' if k == 'top' else 'floor'}" for cp, (n, k) in FLOORS.items()}, **ANGLES,
             **{cp: f"uni{cp:04X}" for cp in GROUPS}}
    m = Masters(path, [*(f"{n}.case" for n in {**CURVED, **STRAIGHT, **BRACES}.values()), "H", *SLASHES.values(), "pipedbl",
                       "minus", "minus.case", "equal", "equal.case"])
    out: dict[int, list[NewGlyph]] = {}
    for size, total in {0: NORMAL, **SIZES}.items():
        suffix = "math" if size == 0 else f"size{size}"
        out[size] = [
            m.glyph(f"{name}.{suffix}", [drawn(m, name, cp, master, total * upem, size > 0, upem) for master in m.masters], cp)
            for cp, name in names.items()
        ]
    out[0] += [m.glyph(f"uni{cp:04X}.math", [corner(m, cp, master) for master in m.masters], cp) for cp in CORNERS]
    for size, total in {0: NORMAL, **SIZES}.items():
        suffix = "math" if size == 0 else f"size{size}"
        # the text size's in an advance as wide as = less two thin spaces: \\mathrlap{\\,/}{=} and {=}\\mathllap{/\\,} (TeX's
        # ≠, its documentation's) centre it on =, as TeX's (its / wider) nearly does
        within = (lambda master: even_bars(m, "equal", master).advance - upem / 3) if size == 0 else (lambda master: 0.0)
        out[size] += [m.glyph(f"{name}.{suffix}", [slash(m, name, master, total * upem, within(master), upem) for master in m.masters], cp) for cp, name in SLASHES.items()]
    out[0] += [m.glyph(f"uni{cp:04X}.math", [slash(m, name, master, NORMAL * upem) for master in m.masters], cp) for cp, name in TWINS.items()]
    # ⟦ ⦃ at the text size (KaTeX has no larger ones), ⟧ ⦄ mirrored
    doubles = {cp: [double(m, cp, master, NORMAL * upem) for master in m.masters] for cp in DOUBLES}
    out[0] += [m.glyph(f"uni{cp:04X}.math", shapes, cp) for cp, shapes in doubles.items()]
    out[0] += [m.glyph(f"uni{cp:04X}.math", [s.mirrored() for s in doubles[of]], cp) for cp, of in DOUBLE_MIRRORS.items()]
    # the pieces KaTeX stacks a brace from past the largest size, at the text optical size whatever the size:
    # the stem between them is an image, which can't follow the optical size (src/svg.ts)
    cuts = brace_cuts(m, upem)
    text = {master["wght"]: master for master in m.masters if master["opsz"] == m.axes["opsz"].defaultValue}
    out[4] += [
        m.glyph(f"uni{cp:04X}.size4", [piece(m, cp, text[master["wght"]], cuts, upem) for master in m.masters], cp)
        for cp in PIECES
    ]
    return out
