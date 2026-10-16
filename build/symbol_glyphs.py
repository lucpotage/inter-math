"""
More symbols Inter lacks, or draws for text, drawn from Inter's own glyphs, as
heavy as the operators and centred like them (build/operators.py) unless they
are letters. A part drawn smaller or larger is taken at the weight that keeps
its stroke the operators' (build/variable.py: past Black when it must).

- ⊤ ⊢ ⊣ ⊨: the bars of ⊥ (build/geometry_glyphs.py): the minus sign's and
  plus's vertical one, cap height tall (⊤ on the baseline; ⊢ ⊣ ⊨ centred on
  the axis, their crossing bars across its middle); ⊨ with ='s two bars;
- ⋯ ⋮ ⋱: Inter's ellipsis on the axis, upright, and turned down to the right
  (its dots as large as ⋅'s: build/geometry_glyphs.py);
- ∗ ⋆: Inter's asterisk (its case form, as much larger as the dots) and
  star (as tall as the asterisk), on the axis (∖ ∕ are \\ / at the text
  size: build/delimiters.py);
- ≪ ≫: two of Inter's < (or >), the second nested in, as far from the
  first across their arms as ='s bars are apart (build/operators.py);
- ≐: = with Inter's middle dot above, as far as its bars are apart;
- ⨿: ∏ turned, as tall as ⊂;
- ⊕ ⊖ ⊗ ⊘ ⊙: Inter's circle (○) RING times as tall as + (it grows with the
  weight as + does), the sign inside clear of it, as in Inter's own (1.2 em
  wide: they are replaced too); past the regular weight, ring and sign grow
  lighter than the operators, as Inter's rings do, so that they stay open;
- △ ▽ ◯: Inter's, △ ▽ as heavy as Inter draws them, ▽ the image of △ in the
  axis (its ◯, 1.2 em wide, BIG_CIRCLE times as tall as △, as TeX's are, and
  as heavy as the circled operators);
- ∅: Inter's 0 crossed by the slash of its slashed zero (the `zero`
  feature), drawn out along its slant to pass the 0 by EMPTY of its height,
  at the letters' weight: TeX's ∅ is its 0 crossed (Inter's own ∅ is a
  circle, the size of a lowercase letter);
- ⊓ ⊔ ⊑ ⊒ ⊎: square versions of ∩ ∪ ⊆ in their box: plus's vertical bar and
  the minus sign's bar (⊑ ⊒'s under them as far as ='s bars are apart); ⊎ is ∪
  with a + inside;
- ℏ: Inter's italic ħ (as Computer Modern's, an italic h);
- ′: Inter's italic ′ (math's letters are italic), larger by the inverse of
  KaTeX's script size, its stroke too: KaTeX sets primes as superscripts (a′
  is a^{\\prime}), shrunk to the script size and raised by TeX's shift
  (SUP_SHIFT), so that it comes out as Inter's own, as heavy and as slanted;
  the mark set so that it lands where Inter's text sets ’ after a letter, its
  top as high and as far from an italic a (Inter's side bearings and
  kerning); as wide as the marks of ” are apart, so that a″ and a‴ (primes
  in a row) read as a” and one more;
- @: Inter's case form, which its calt sets beside capitals and figures
  (KaTeX sets every atom alone, so no calt applies), lowered to the math
  axis as the operators are.

KaTeX's accents (accent_glyphs), in the upright font over upright letters
and text, in the italic one over italic letters (build/patch_katex.py):
Inter's combining marks, upright or italic, where Inter puts them:
- ´ ` ¨ ~ ^ ˇ ˘ ˙: as Inter's mark feature puts them over x, each as far off
  ¨'s dots as Inter puts it (an acute leans right of its anchor, a grave
  left), the letters' skews putting ¨'s dots where Inter does;
- ˉ (\\bar): Inter's macron, as high as ā's, drawn out to TeX's width
  against x (MACRON): Inter's is narrow over math's letters;
- ˚ (\\mathring, \\r): Inter's ring, as far over the x-height as its capitals'
  ring (U+EE07, the one of Å) is over the cap height: KaTeX sets one accent
  over every letter, keeping the gap it has over the x-height, and the ring
  mostly marks capitals (the interior of a set).
"""

import math

from geometry_glyphs import DOT, stems_to
from operators import OFFSET, RELATION_SCALE, even_bars, gap, sign
from variable import Masters, NewGlyph, Shape, kerning, mark_anchor

SCRIPT = 0.7  # KaTeX's script size
# KaTeX's superscript shift in text style (TeX's σ14, sup2, em): how far it raises a prime over the baseline
SUP_SHIFT = 0.363
SOURCES = [
    "minus", "plus", "equal", "less", "greater", "ellipsis", "periodcentered", "period", "backslash", "slash",
    "asterisk", "uni2605", "product", "circlewhite", "U", "uni03F5", "lessequal", "one",
    "uni25EF", "uni25B3", "uni25BD", "zero", "zero.slash", "at",
]
# ˉ (\\bar): its width against x's, TeX's (361 of 505): Inter's is narrow over math's letters
MACRON = 361 / 505
# ⊎'s +: its width against its bars' thickness, at least (its arms reach past the crossing by 3/4 of it)
PLUS_IN = 2.5
# \bigcirc against \bigtriangleup, as in TeX
BIG_CIRCLE = 1.3
# ∅: how far its slash passes the 0, a share of the 0's height (TeX's: 81 of 688)
EMPTY = 81 / 688
# the circled operators: their ring against +, and how far their sign is clear of it (a share of the ring's stroke: none, the sign meets it)
RING, CLEAR = 1.2, 0.0
CASED = ["minus", "plus", "equal", "less", "greater", "asterisk", "lessequal", "at"]
# what each is drawn from (the workbench shows it, /dev/symbols): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x22A4: ("minus's bar over plus's vertical bar", "minus plus"),
    0x22A2: ("plus's vertical bar and minus's bar", "plus minus"),
    0x22A3: ("⊢ mirrored", "plus minus"),
    0x22A8: ("plus's vertical bar and ='s bars", "plus equal"),
    0x22EF: ("the ellipsis on the axis", "ellipsis"),
    0x22EE: ("the ellipsis upright", "ellipsis"),
    0x22F1: ("the ellipsis turned down", "ellipsis"),
    0x2217: ("the asterisk, larger, on the axis", "asterisk"),
    0x22C6: ("the star, as tall as ∗", "uni2605"),
    0x226A: ("two <, one nested in", "less"),
    0x226B: ("two >, one nested in", "greater"),
    0x2250: ("= with the middle dot above", "equal periodcentered"),
    0x2A3F: ("∏ turned, as tall as ⊂", "product"),
    0x2295: ("○ around plus's bars", "circlewhite plus"),
    0x2296: ("○ around minus's bar", "circlewhite minus"),
    0x2297: ("○ around plus's bars, turned", "circlewhite plus"),
    0x2298: ("○ across with minus's bar, turned", "circlewhite minus"),
    0x2299: ("○ around the middle dot", "circlewhite periodcentered"),
    0x25BD: ("as low as △ is high", "uni25BD"),
    0x25EF: ("larger, as tall against △ as TeX's", "uni25EF"),
    0x2205: ("0 crossed by its slashed form's slash, drawn out", "zero zero.slash"),
    0x0040: ("Inter's @ as its calt sets it beside capitals (its case form), on the math axis as the operators", "at.case"),
    0x2294: ("plus's vertical bars on minus's bar", "plus minus"),
    0x2293: ("⊔ turned", "plus minus"),
    0x2291: ("a square ⊂ over ≤'s bar", "plus minus lessequal"),
    0x2292: ("⊑ mirrored", "plus minus lessequal"),
    0x228E: ("∪ with a + inside", "U plus"),
    0x210F: ("the italic ħ", "italic:hbar"),
    0x2032: ("Inter's italic ′, larger, its stroke too, set where ’ is after a letter, as far apart as ”'s marks", "italic:prime italic:quoteright italic:quotedblright"),
}


def crossings(shape: Shape, y: float) -> list[float]:
    """Where an outline (its points taken as a polygon) crosses height y."""
    xs = []
    for c in shape.contours():
        pts = c.points
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            if (p[1] - y) * (q[1] - y) < 0:
                xs.append(p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]))
    return xs


def rect(x0: float, y0: float, x1: float, y1: float) -> Shape:
    return Shape.polygon([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])


def nested(m: Masters, master: dict, name: str, count: int = 2) -> Shape:
    """
    `count` of Inter Math's < (or >, `name`), each nested in the one before
    it, as far from it across their arms as ='s bars are apart (≪ ≫, ⋘ ⋙).
    """
    chevron = sign(m, name, master)
    _, my0, _, my1 = sign(m, "minus", master).bounds()
    axis = (my0 + my1) / 2
    # the arms: how wide across, at the axis's level, how slanted
    _, cy0, _, cy1 = chevron.bounds()
    ya, yb = axis + (cy1 - cy0) * 0.2, axis + (cy1 - cy0) * 0.35
    at, bt = sorted(crossings(chevron, ya)), sorted(crossings(chevron, yb))
    arm = at[1] - at[0]
    slope = (bt[0] - at[0]) / (yb - ya)
    step = arm + gap(m, master) * math.hypot(1, slope)
    return Shape.join([chevron.moved(i * step, 0) for i in range(count)], chevron.advance + (count - 1) * step)


def ring_light(m: Masters, master: dict) -> float:
    """
    How much lighter than the operators Inter draws its rings at a master's
    weight (its ◯ against plus's vertical bar, at the text optical size: its
    display ◯ is heavier): 1 up to the regular weight, less past it.
    """
    text = {**master, "opsz": m.axes["opsz"].defaultValue}
    vertical = max(even_bars(m, "plus", text).contours(), key=lambda c: c.bounds()[3] - c.bounds()[1]).bounds()
    return min(1.0, m.shape("uni25EF", text).side() / (vertical[2] - vertical[0]))


def ring_for(m: Masters, master: dict, tall: float, stroke: float, axis: float) -> tuple[Shape, tuple[float, float], float]:
    """The circled operators' ring at a master: Inter's ○ `tall` tall, its side `stroke` thick, on `axis`; its centre and inner radius."""
    _, c0, _, c1 = m.shape("circlewhite", master).bounds()
    ring = m.fitted("circlewhite", master, tall / (c1 - c0), stroke).centred(axis)
    rx0, ry0, rx1, ry1 = ring.bounds()
    return ring, ((rx0 + rx1) / 2, (ry0 + ry1) / 2), min(c.bounds()[2] - c.bounds()[0] for c in ring.contours()) / 2


def circled(m: Masters, master: dict, tall: float, stroke: float, bar: float, dot: Shape, axis: float) -> dict[int, Shape]:
    """
    ⊕ ⊖ ⊗ ⊘ ⊙ at a master: Inter's ○ `tall` tall, its side `stroke` thick,
    centred on `axis` (○'s advance and side bearings kept); the sign's
    vertical bar as thick as the ring, its horizontal one `bar` thick, both
    meeting the ring (CLEAR), turned for ⊗ ⊘; ⊙'s `dot` in its centre.
    """
    ring, centre, inner = ring_for(m, master, tall, stroke, axis)
    inner -= CLEAR * stroke
    across = rect(centre[0] - inner, centre[1] - bar / 2, centre[0] + inner, centre[1] + bar / 2)
    upward = rect(centre[0] - stroke / 2, centre[1] - inner, centre[0] + stroke / 2, centre[1] + inner)
    dot = dot.moved(centre[0] - (dot.bounds()[0] + dot.bounds()[2]) / 2, 0).centred(centre[1])
    return {
        cp: Shape.join([ring, *parts], ring.advance)
        for cp, parts in {
            0x2295: [across, upward], 0x2296: [across],
            0x2297: [across.turned(45, centre), upward.turned(45, centre)], 0x2298: [across.turned(45, centre)],
            0x2299: [dot],
        }.items()
    }


def turnstiles(m: Masters, design: dict, master: dict) -> tuple[Shape, Shape]:
    """⊢ and ⊨ at a master: plus's vertical bar, cap height tall, with minus's bar or ='s bars, centred on the axis."""
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis, rule = (my0 + my1) / 2, my1 - my0
    vertical = max(even_bars(m, "plus", master).contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
    stem = vertical.bounds()[2] - vertical.bounds()[0]
    cap = m.section("one", design["wght"], design["opsz"])[2]
    bars = sorted(even_bars(m, "equal", master).contours(), key=lambda c: c.bounds()[1])
    upright = rect(mx0, axis - cap / 2, mx0 + stem, axis + cap / 2)
    tack = Shape.join([upright, rect(mx0, axis - rule / 2, mx1, axis + rule / 2)], minus.advance)
    return tack, Shape.join([upright, *bars], minus.advance)


def symbol_glyphs(path, italic_path, upem: int) -> list[NewGlyph]:
    m = Masters(path, [*SOURCES, *(f"{n}.case" for n in CASED)])
    mi = Masters(italic_path, ["hbar", "one", "a", "prime", "quoteright", "quotedblright"])
    shapes: dict[int, list[Shape]] = {}

    def put(cp: int, s: Shape) -> None:
        shapes.setdefault(cp, []).append(s)

    for design, italic in zip(m.masters, mi.masters):
        master = m.lighter(design, OFFSET)
        minus = sign(m, "minus", master)
        mx0, my0, mx1, my1 = minus.bounds()
        axis, rule = (my0 + my1) / 2, my1 - my0
        side = (mx0 + minus.advance - mx1) / 2
        plus = even_bars(m, "plus", master)
        vertical = max(plus.contours(), key=lambda c: c.bounds()[3] - c.bounds()[1])
        stem = vertical.bounds()[2] - vertical.bounds()[0]
        cap = m.section("one", design["wght"], design["opsz"])[2]
        eq = even_bars(m, "equal", master)
        bars = sorted(eq.contours(), key=lambda c: c.bounds()[1])
        centre = (mx0 + mx1) / 2

        # ⊤ ⊢ ⊣ ⊨
        put(0x22A4, Shape.join([rect(mx0, cap - rule, mx1, cap), rect(centre - stem / 2, 0, centre + stem / 2, cap)], minus.advance))
        tack, models = turnstiles(m, design, master)
        put(0x22A2, tack)
        put(0x22A3, tack.mirrored())
        put(0x22A8, models)

        # ⋯ ⋮ ⋱
        dots = sign(m, "ellipsis", master, DOT).centred(axis)
        put(0x22EF, dots)
        dot = sign(m, "periodcentered", master, DOT)
        dx0, _, dx1, _ = dot.bounds()
        upright = dots.turned(90)
        ux0, _, ux1, _ = upright.bounds()
        upright = upright.moved(dx0 - ux0, 0)
        upright.advance = dot.advance + (ux1 - ux0) - (dx1 - dx0)
        put(0x22EE, upright)
        diagonal = dots.turned(-45)
        gx0, _, gx1, _ = diagonal.bounds()
        diagonal = diagonal.spaced(dx0)
        put(0x22F1, diagonal)

        # ∗ ⋆ (∖ ∕ are drawn as \ / are: build/delimiters.py)
        asterisk = sign(m, "asterisk", master, DOT).centred(axis)
        put(0x2217, asterisk)
        _, ay0, _, ay1 = asterisk.bounds()
        star = m.shape("uni2605", master)
        _, sy0, _, sy1 = star.bounds()
        put(0x22C6, star.scaled((ay1 - ay0) / (sy1 - sy0)).centred(axis).spaced(side))

        # ≪ ≫: the second chevron nested in the first, ='s gap from it across their arms
        put(0x226A, nested(m, master, "less"))
        put(0x226B, nested(m, master, "greater"))

        # ≐
        pitch = (bars[1].bounds()[1] + bars[1].bounds()[3] - bars[0].bounds()[1] - bars[0].bounds()[3]) / 2
        _, top0, _, top1 = bars[1].bounds()
        cdot = sign(m, "periodcentered", master, DOT)
        cdx0, _, cdx1, _ = cdot.bounds()
        cdot = cdot.moved(centre - (cdx0 + cdx1) / 2, 0).centred((top0 + top1) / 2 + pitch)
        put(0x2250, Shape.join([eq, cdot], eq.advance))

        # the box of ⊂ (as build/geometry_glyphs.py draws it)
        eps = sign(m, "uni03F5", master, RELATION_SCALE)
        _, by0, _, by1 = eps.bounds()
        box = by1 - by0
        less = sign(m, "less", master)
        width = less.bounds()[2] - less.bounds()[0]

        def sized(name: str, height: float) -> Shape:
            """Inter's glyph as tall as `height`, its stroke (at its side) as thick as the operators'."""
            _, y0, _, y1 = m.shape(name, master).bounds()
            return m.fitted(name, master, height / (y1 - y0), stem)

        # ⨿
        put(0x2A3F, sized("product", box).rotated().centred(axis).spaced(side))

        # ⊕ ⊖ ⊗ ⊘ ⊙: a ring RING times as tall as + (it grows with the weight as + does), as heavy as the
        # operators up to the regular weight and lighter past it, as Inter's rings are (its ◯ ⊕, at the
        # text optical size: its display ◯ is heavier), the sign too, and clear of the ring (as Inter's are)
        light = ring_light(m, master)
        ring_stroke = stem * light
        _, p0, _, p1 = plus.bounds()
        for cp, s in circled(m, master, RING * (p1 - p0), ring_stroke, rule * light, cdot, axis).items():
            put(cp, s.spaced(side))

        # △ ▽: Inter's, as heavy as it draws them (lighter than its operators at Black); ◯: its large circle, BIG_CIRCLE
        # times as tall
        up_tri, down_tri = (m.shape(name, master) for name in ("uni25B3", "uni25BD"))
        # ▽ as low as △ is high: its image in the axis (as TeX's pair are; Inter's hangs from the cap height)
        _, u0, _, u1 = up_tri.bounds()
        put(0x25B3, up_tri)
        put(0x25BD, down_tri.centred(2 * axis - (u0 + u1) / 2))
        _, t0, _, t1 = m.shape("uni25B3", master).bounds()
        _, g0, _, g1 = m.shape("uni25EF", master).bounds()
        put(0x25EF, m.fitted("uni25EF", master, BIG_CIRCLE * (t1 - t0) / (g1 - g0), ring_stroke).centred(axis).spaced(side))

        # ∅: Inter's 0 and its slashed form's slash (its four-point contour), drawn out along it to pass the 0 by EMPTY
        # of its height, at the letters' weight
        slashed = m.shape("zero.slash", design)
        cut, *oval = sorted(slashed.contours(), key=lambda c: len(c.points))
        _, z0, _, z1 = Shape.join(oval, 0).bounds()
        ends = sorted(range(4), key=lambda i: cut.points[i][1])
        (bx, by), (tx, ty) = [((cut.points[a][0] + cut.points[b][0]) / 2, (cut.points[a][1] + cut.points[b][1]) / 2) for a, b in (ends[:2], ends[2:])]
        ux, uy = (tx - bx) / math.hypot(tx - bx, ty - by), (ty - by) / math.hypot(tx - bx, ty - by)
        past = EMPTY * (z1 - z0)
        up, down = (z1 + past - cut.points[ends[3]][1]) / uy, (cut.points[ends[0]][1] - (z0 - past)) / uy
        drawn = [(x + ux * up, y + uy * up) if i in ends[2:] else (x - ux * down, y - uy * down) for i, (x, y) in enumerate(cut.points)]
        put(0x2205, Shape.join([*oval, Shape(drawn, cut.on, cut.ends, 0)], slashed.advance))

        # @: Inter's case form (its calt sets it beside capitals and figures; KaTeX sets every atom alone), lowered
        # to the math axis as the operators' are
        put(0x0040, sign(m, "at", master, 1.0))

        # ⊔ ⊓ ⊑ ⊒ ⊎: in ⊂'s box (as wide as <, as tall as ϵ)
        left, right_, bottom, top = side, side + width, axis - box / 2, axis + box / 2
        cup = Shape.join([rect(left, bottom, left + stem, top), rect(right_ - stem, bottom, right_, top), rect(left, bottom, right_, bottom + rule)], width + 2 * side)
        put(0x2294, cup)
        put(0x2293, cup.rotated())
        # ⊑ ⊒: ⊏ shortened over ≤'s bar, as ⊆ is drawn
        le = sign(m, "lessequal", master)
        le_bar, le_chevron = sorted(le.contours(), key=lambda c: len(c.points))
        _, c0, _, c1 = le_chevron.bounds()
        # the bar under it, as far from its lower bar as ='s bars are apart
        b1 = c0 - gap(m, master)
        b0 = b1 - rule
        square = Shape.join([
            rect(left, c0, left + stem, c1), rect(left, c1 - rule, right_, c1), rect(left, c0, right_, c0 + rule), rect(left, b0, right_, b1),
        ], width + 2 * side).centred(axis)
        put(0x2291, square)
        put(0x2292, square.mirrored())
        # ⊎: ∪ (as build/geometry_glyphs.py draws it) with a + inside
        u = m.shape("U", master)
        ux0, _, ux1, _ = u.bounds()
        u = m.fitted("U", master, width / (ux1 - ux0), stem)
        u = stems_to(u, u.bounds()[1] + box).centred(axis).spaced(side)
        ux0, _, ux1, _ = u.bounds()
        # the + filling half the opening between the stems, as light as the rings' signs past Regular (ring_light), and
        # no heavier than PLUS_IN of its width, so that its arms reach past the crossing (at the operators' stroke the
        # opening's + was a blob from 600 up)
        opening = sorted(crossings(u, axis))
        uc, arm = (ux0 + ux1) / 2, (opening[2] - opening[1]) / 4
        cross = min(stem * ring_light(m, master), 2 * arm / PLUS_IN)
        bar_ = cross * rule / stem
        put(0x228E, Shape.join([u, rect(uc - arm, axis - bar_ / 2, uc + arm, axis + bar_ / 2),
                                 rect(uc - cross / 2, axis - arm, uc + cross / 2, axis + arm)], u.advance))

        # ℏ: the italic ħ, at the letters' weight
        put(0x210F, mi.shape("hbar", italic))

        # ′: Inter's italic ′ (math's letters are italic), as a superscript (KaTeX scales it by SCRIPT) as large and
        # as heavy as Inter's: scaled, its stroke with it (one drawn to keep the letters' stroke at the larger size
        # came out 0.7 as heavy, and upright: Inter's leans with the letters), landing where Inter's text sets ’ after
        # an italic a: KaTeX raises it by SUP_SHIFT after the letter's italic correction, so its top goes to ’'s, and
        # its side keeps ’'s gap after the a; as wide as the marks of ” are apart
        k = 1 / SCRIPT
        mark = mi.shape("prime", italic).scaled(k)
        a, quote = mi.shape("a", italic), mi.shape("quoteright", italic)
        _, _, ax1, _ = a.bounds()
        qx0, _, _, q_top = quote.bounds()
        after = a.advance - ax1 + kerning(mi.font, "a", "quoteright", italic) + qx0
        overhang = max(0.0, ax1 - a.advance)
        mx0, _, _, m_top = mark.bounds()
        mark = mark.moved((after - (a.advance + overhang - ax1)) * k - mx0, (q_top - SUP_SHIFT * upem) * k - m_top)
        first, second = sorted(c.bounds()[0] for c in mi.shape("quotedblright", italic).contours())
        mark.advance = (second - first) * k
        put(0x2032, mark)

    return [m.glyph(f"uni{cp:04X}.math", s, cp) for cp, s in shapes.items()]


# KaTeX's accents (the characters it sets them with, \\acute and \\' alike) and the combining marks of Inter they are:
# Main's (upright letters, text) in the upright font, the italic letters' in the italic one (build/patch_katex.py)
ACCENT_MARKS = {0x02CA: "acutecomb", 0x02CB: "gravecomb", 0x00A8: "uni0308", 0x007E: "tildecomb", 0x005E: "uni0302",
                0x02C7: "uni030C", 0x02D8: "uni0306", 0x02D9: "uni0307", 0x02DA: "uni030A", 0x02C9: "uni0304"}
_MARK_NAMES = {0x02CA: "acute", 0x02CB: "grave", 0x00A8: "dieresis", 0x007E: "tilde", 0x005E: "circumflex", 0x02C7: "caron",
               0x02D8: "breve", 0x02D9: "dot", 0x02DA: "ring", 0x02C9: "macron"}


def _accents_from(italic: str) -> dict:
    """What each accent is drawn from (the italic font's: italic="italic ", names "italic:…")."""
    prefix = "italic:" if italic else ""
    out = {cp: (f"Inter's {italic}{_MARK_NAMES[cp]}, where Inter puts it over a letter (it leans off its anchor)",
                f"{prefix}{name}") for cp, name in ACCENT_MARKS.items()}
    out[0x02DA] = (f"Inter's {italic}ring, as close over lowercase as its capitals' ring is over capitals",
                   f"{prefix}uni030A {prefix}uni030A.uc")
    out[0x02C9] = (f"Inter's {italic}macron (ā's) drawn out to TeX's width against x", f"{prefix}uni0304 {prefix}x")
    return out


# the upright font's (DRAWN_FROM) and the italic font's (build.py's provenance takes these for it)
ACCENTS_FROM = _accents_from("")
ITALIC_FROM = _accents_from("italic ")
# the white either side of an accent's ink in its advance at the regular weight (font units)
ACCENT_SIDE = 100


def accent_glyphs(path) -> list[NewGlyph]:
    """
    KaTeX's accents in a font of Inter's, upright or italic: its combining
    marks (an italic accent leans with an italic letter: an upright one over
    it looked off), at the height its mark feature puts them over x. KaTeX
    centres an accent's advance on a letter's skew, one a letter for every
    accent, while Inter's marks sit off their anchors each its own way (an
    acute right, a grave left): each accent is in an advance as wide at
    every weight, its ink's middle off the advance's by as far as Inter puts
    its mark off ¨'s dots, so that the skew that puts ¨ where Inter does
    (build.py's accent_skews) puts every accent where Inter puts its mark.
    ˚ as close over the x-height as Inter's capitals' ring is over the cap
    height (moved along the slant), ˉ (\\bar) drawn out to TeX's width against
    x, its ends' cuts kept.
    """
    m = Masters(path, [*ACCENT_MARKS.values(), "uni030A.uc", "x", "H"])
    slant = math.tan(math.radians(-m.font["post"].italicAngle))

    def placed(name: str, base: str, master: dict) -> Shape:
        """A mark where Inter's mark feature puts it over a base (the base's origin at 0)."""
        (bx, by), (ox, oy) = mark_anchor(m.font, base, name, master), mark_anchor(m.font, base, name, master, own=True)
        return m.shape(name, master).moved(bx - ox, by - oy)

    def middle(s: Shape) -> float:
        x0, _, x1, _ = s.bounds()
        return (x0 + x1) / 2

    def drawn(cp: int, master: dict) -> Shape:
        s = placed(ACCENT_MARKS[cp], "x", master)
        if cp == 0x02DA:
            lowercase = s.bounds()[1] - m.shape("x", master).bounds()[3]
            capitals = placed("uni030A.uc", "H", master).bounds()[1] - m.shape("H", master).bounds()[3]
            s = s.moved((capitals - lowercase) * slant, capitals - lowercase)
        if cp == 0x02C9:
            x0, _, x1, _ = s.bounds()
            xx0, _, xx1, _ = m.shape("x", master).bounds()
            grow, mid = MACRON * (xx1 - xx0) - (x1 - x0), (x0 + x1) / 2
            s = s.map(lambda x, y: (x - grow / 2 if x < mid else x + grow / 2, y))
        return s

    regular = m.masters[m.default]
    advance = {cp: (lambda b: b[2] - b[0])(drawn(cp, regular).bounds()) + 2 * ACCENT_SIDE for cp in ACCENT_MARKS}
    shapes: dict[int, list[Shape]] = {}
    for master in m.masters:
        # where Inter puts ¨'s dots over x: every mark goes as far from them as Inter puts it
        dots = middle(placed("uni0308", "x", master))
        for cp in ACCENT_MARKS:
            s = drawn(cp, master).moved(advance[cp] / 2 - dots, 0)
            s.advance = advance[cp]
            shapes.setdefault(cp, []).append(s)
    return [m.glyph(f"uni{cp:04X}.accent", s, cp) for cp, s in shapes.items()]
