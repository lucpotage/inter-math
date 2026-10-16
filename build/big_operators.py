"""
Big operators (∑ ∏ ∐ ∫ ∬ ∭ ∮ ⋃ ⋂ ⋀ ⋁ ⨁ ⨂ ⨀ ⨄ ⨆) for KaTeX's \\sum, \\prod,
\\int, \\bigcup…, after Inter's.

KaTeX sets them from its Size1 font in text style and its Size2 font in
display style; Inter Math puts its own in the same sizes' fonts (see
build/delimiters.py). Their strokes are as thick as the letters' (Inter's ∑
and ∏ are drawn like its M), whatever their size. Centred on the math axis
(build/operators.py; KaTeX centres them on it anyway):

- ∑ ∏: Inter's (drawn for math: they reach below the baseline), larger, taken
  at the weight that keeps their stroke once scaled; ∐ is ∏ turned over;
- ∫: Inter's italic one (ʄ and ʃ are built on the upright one), slanted on
  to SLANT degrees (Inter's italic angle is 9.4°): its hooks kept (a little
  larger in display style), its straight stem drawn out along its slant;
- ∬ ∭: integrals drawn together, the way a double letter is (ll): stems as
  far apart as two l's, the inner hooks (the top one of every integral but
  the last, the bottom one of every integral but the first) drawn in towards
  their stem to end half a stem short of the next one; the outer hooks whole;
- ∮: ∫ with Inter's ○ drawn around its stem, centred on the axis (TeX's), as
  heavy as Inter draws ○ (lighter than the letters at Black): as large
  against the integral as TeX's ring (RING) at the regular weight, and
  keeping beside the stem, at every weight, the white Inter's ɸ keeps
  beside its own (it halves from Regular to Black): the ring grows with the
  weight, as ɸ's bowl does (TeX's at Black would close on the stem). KaTeX
  draws ∯ ∰ as ∬ ∭ with an oval over them: ∮'s ring drawn out sideways to
  pass their outer stems as it passes ∮'s (build.py's ovals(), src/svg.ts);
- ⋃ ⋂: Inter's U as wide against ∑'s height as TeX's ⋃ (CUP), drawn out to
  it (as ∪ ∩ are U cut down, build/geometry_glyphs.py); ⨄ with ⨁'s +
  inside (lighter past Regular), across PLUS of the opening and centred in
  it, as TeX's (⊎'s, half of it, closes up at Black); ⨆ square: U's
  stems and its bottom's thickness, in ⋃'s box (as ⊔ is drawn from bars;
  Inter's ∏ has no overhang, so ∐ is square too);
- ⋀ ⋁: Inter's Λ as tall as ∑ (as ∧ ∨ are), turned;
- ⨁ ⨂ ⨀: ⊕ ⊗ ⊙ as tall as ∑ (build/symbol_glyphs.py's circled(): the
  sign meets the ring, both as heavy as Inter's ⊕, lighter than the
  operators past Regular); ⨀'s dot Inter's middle dot, as large against the
  ring as TeX's (DOT) at the regular weight, growing with the weight as it.
KaTeX sets an integral's lower limit after its advance, and its upper limit
and what follows after its italic correction too (ITALIC). The advance goes
where a script 0 beside the integral keeps TeX's white from its ink
(SUB_WHITE, against the x-height) up to Regular: the slant leans the stem
towards the lower limit, and an advance half a stem past the stem's foot left
it 0.04 em (it touched the integral). Past Regular the white tightens as
Inter's letters' does (`letter_fit`: 0.6 of Regular's at Black, where TeX's
read loose); under Regular their looser fit set the limits off the integral.
The italic correction ends half a stem past the top hook (which reaches over
it, as in TeX), less what the advance took, at every weight (KaTeX reads
Regular's; setMathFont gives it the weight's).
The integrals keep the text optical size at every size, as a tall brace's
pieces do: the ovals KaTeX lays over ∬ ∭ for ∯ ∰ are images, which can't
follow it (in the display size the stems stepped closer, and the oval sat
off them).

Sizes, in em: Computer Modern's (∑ 1 and 1.4, ∫ 1.11 and 2.22) in proportion
to the capitals, Inter's being smaller.
"""

import math

from fontTools.ttLib import TTFont

from equality_glyphs import ring
from geometry_glyphs import rect, stems_to
from operators import column, math_axis, sign
from symbol_glyphs import circled, ring_light
from variable import Masters, NewGlyph, Shape

# KaTeX size font → total heights (em) and the scale of the integral's hooks
SIZES = {
    1: {"sum": 0.9, "integral": 1.0, "hooks": 1.0},
    2: {"sum": 1.3, "integral": 1.8, "hooks": 1.15},
}
# TeX's, by size: ⋃'s width against its height (CUP), ⨄'s + against the opening (PLUS), ∮'s ring against the
# integral's height (RING), ⨀'s dot against its ring (DOT)
CUP = {1: 722 / 1000, 2: 1000 / 1400}
PLUS = {1: 386 / 553, 2: 608 / 804}
RING = {1: 370 / 1111, 2: 540 / 2222}
DOT = {1: 154 / 998, 2: 180 / 1398}
SUMS = {0x2211: "summation", 0x220F: "product"}
COPRODUCT = 0x2210
INTEGRALS = {0x222B: 1, 0x222C: 2, 0x222D: 3}
CONTOUR = 0x222E
# Inter's ɸ (U+0278): a bowl around a stem, like ∮'s ring
PHI = "philatin"
# what each is drawn from (the workbench shows it, /dev/symbols): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x2210: ("∏ turned over", "product"),
    0x222B: ("Inter's italic ∫, slanted on", "italic:integral"),
    0x222C: ("two italic ∫ drawn together, apart enough to keep their inner hooks", "italic:integral"),
    0x222D: ("three italic ∫ drawn together, apart enough to keep their inner hooks", "italic:integral"),
    0x222E: ("∫ with a ring of ○ around its stem", "italic:integral circlewhite"),
    0x22C3: ("U, drawn out to ∑'s height", "U"),
    0x22C2: ("⋃ turned", "U"),
    0x2A04: ("⋃ with a + inside", "U"),
    0x2A06: ("U's stems and bottom, square", "U"),
    0x22C0: ("Λ as tall as ∑", "Lambda"),
    0x22C1: ("⋀ turned", "Lambda"),
    0x2A01: ("○ around plus's bars, as tall as ∑", "circlewhite plus"),
    0x2A02: ("○ around plus's bars, turned", "circlewhite plus"),
    0x2A00: ("○ around the middle dot", "circlewhite periodcentered"),
}
# the integrals' slant, in degrees
SLANT = 15
# size → code point → weight → italic correction (em), for KaTeX's metrics (build.py): it moves with the advance
ITALIC: dict[int, dict[int, dict[int, float]]] = {}
WEIGHTS = range(100, 1000, 100)
# a subscript beside ∫ ∬ ∭ ∮: where KaTeX sets its baseline with Inter Math's metrics (em, by size: measured in the
# workbench), and the white its ink keeps from the integral's in TeX, against the x-height (a 0 beside TeX's ∫: 0.158
# and 0.221 em of its 0.431)
SUBSCRIPT = {1: -0.2696, 2: -0.6698}
SUB_WHITE = {1: 0.158 / 0.431, 2: 0.221 / 0.431}
SCRIPT_SIZE = 0.7


def script_figure(path, char: str) -> str:
    """The glyph Inter Math sets a figure with in scripts (its ss19 alternate: build/script_glyphs.py)."""
    font = TTFont(path)
    name = font.getBestCmap()[ord(char)]
    gsub = font["GSUB"].table
    for record in gsub.FeatureList.FeatureRecord:
        if record.FeatureTag == "ss19":
            for index in record.Feature.LookupListIndex:
                lookup = gsub.LookupList.Lookup[index]
                for st in lookup.SubTable:
                    st = st.ExtSubTable if lookup.LookupType == 7 else st
                    if name in getattr(st, "mapping", {}):
                        return st.mapping[name]
    return name


def hooks_kept(m: Masters, master: dict, k: float) -> float:
    """The share of their length the inner hooks of ∬ ∭ keep at Regular, two l's apart and half a stem short of the next stem."""
    regular = {**master, "wght": m.axes["wght"].defaultValue}
    src = m.shape("integral", regular, m.heavier(regular, k)).scaled(k)
    lean = math.tan(math.radians(-m.font["post"].italicAngle))
    u = src.map(lambda x, y: (x - lean * y, y))
    x0, y0, x1, y1 = u.bounds()
    left, right = u.span((y0 + y1) / 2)
    stem = right - left
    room = m.shape("l", regular).advance * k - stem - stem / 2
    return min(1.0, room / (x1 - right), room / (left - x0))


def integrals(m: Masters, master: dict, hooks: float, height: float, axis: float) -> dict[int, Shape]:
    """∫ ∬ ∭ at a master, from Inter's italic ∫ (its hooks `hooks` times larger), `height` tall, centred on `axis`."""
    k = hooks
    src = m.shape("integral", master, m.heavier(master, k)).scaled(k)
    # work upright (the stem vertical), slant at the end
    lean = math.tan(math.radians(-m.font["post"].italicAngle))
    u = src.map(lambda x, y: (x - lean * y, y))
    x0, y0, x1, y1 = u.bounds()
    middle = (y0 + y1) / 2
    left, right = u.span(middle)
    stem = right - left
    grow = (height - (y1 - y0)) / 2
    u = u.map(lambda x, y: (x, y + grow if y > middle else y - grow)).centred(axis)
    foot = min(y for x, y in u.points if abs(x - right) < 2)
    gap = stem / 2
    # two l's apart; the inner hooks end half a stem short of the next stem, and keep at least the share of their
    # length they keep at Regular: heavier, the stems leave them less room, so the integrals step further apart (two
    # l's apart, the hooks of Inter Math's heaviest ∬ came to nothing)
    step = m.shape("l", master).advance * k
    kept = hooks_kept(m, master, k)
    step = max(step, stem + gap + max(kept * (x1 - right), kept * (left - x0)))
    top = min(1, (step - stem - gap) / (x1 - right))
    bottom = min(1, (step - stem - gap) / (left - x0))
    slant = math.tan(math.radians(SLANT))

    def drawn(count: int) -> Shape:
        copies = []
        for i in range(count):
            def edit(x, y, i=i):
                if y > axis and x > right and i < count - 1:
                    x = right + (x - right) * top
                if y < axis and x < left and i > 0:
                    x = left - (left - x) * bottom
                return x + i * step, y
            copies.append(u.map(edit))
        s = Shape.join(copies, 0).map(lambda x, y: (x + slant * (y - axis), y))
        # the ink from half a stem; the advance half a stem past the last stem's foot
        ix0, _, ix1, _ = s.bounds()
        s = s.moved(gap / 2 - ix0, 0)
        s.advance = right + (count - 1) * step + slant * (foot - axis) + gap / 2 - ix0 + gap
        # the italic correction: on to half a stem past the top hook
        return s, (ix1 - ix0 + gap / 2 + gap) - s.advance

    return {cp: drawn(count) for cp, count in INTEGRALS.items()}


def letter_fit(m: Masters, master: dict) -> float:
    """Inter's white between its l and its 0 (l's right side bearing and 0's left) at a master, against Regular's."""

    def white(location: dict) -> float:
        l, zero = m.shape("l", location), m.shape("zero", location)
        return l.advance - l.bounds()[2] + zero.bounds()[0]

    return white(master) / white({**master, "wght": m.axes["wght"].defaultValue})


def width(shape: Shape) -> float:
    x0, _, x1, _ = shape.bounds()
    return x1 - x0


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def scaled(m: Masters, master: dict, name: str, k: float) -> Shape:
    """Inter's glyph k times larger, at the weight whose stroke comes out as thick as the master's."""
    return m.shape(name, master, m.heavier(master, k)).scaled(k)


def beside(m: Masters, location: dict) -> float:
    """The white Inter's ɸ keeps between its stem and its bowl, where the bowl is widest."""
    phi = m.shape(PHI, location)
    _, y0, _, y1 = phi.bounds()
    rows = [r for r in (phi.runs(y0 + (y1 - y0) * i / 80) for i in range(8, 73)) if len(r) == 3]
    (_, bowl), (stem, _), _ = max(rows, key=lambda r: r[2][1] - r[0][0])
    return stem - bowl


def circle_stroke(m: Masters, location: dict) -> float:
    """How thick Inter draws its ○ (its two circles' left edges apart)."""
    outer, inner = sorted(m.shape("circlewhite", location).contours(), key=lambda c: c.bounds()[0])
    return inner.bounds()[0] - outer.bounds()[0]


def contour_ring(m: Masters, master: dict, integral: Shape, at_regular: Shape, across: float, axis: float) -> Shape:
    """
    ∮'s ring at a master: Inter's ○ (as thick as Inter draws it) around the
    stem of `integral` on the axis, `across` wide at the regular weight (where
    the integral is `at_regular`), keeping beside the stem the white ɸ keeps
    beside its own, as that changes with the weight.
    """
    regular = {**master, "wght": m.axes["wght"].defaultValue}
    (r0, r1), = at_regular.runs(axis)
    white = (across - (r1 - r0)) / 2 - circle_stroke(m, regular)
    white *= beside(m, master) / beside(m, regular)
    (x0, x1), = integral.runs(axis)
    inner = (x1 - x0) / 2 + white
    return ring(m.shape("circlewhite", master), ((x0 + x1) / 2, axis), inner + circle_stroke(m, master), inner)


def cups(m: Masters, master: dict, tall: float, wide: float, plus: float, bars: tuple[float, float], axis: float) -> dict[int, Shape]:
    """
    ⋃ ⋂ ⨄ ⨆ at a master: Inter's U `wide` wide, at the weight that keeps its
    stems the letters', drawn out to `tall`, on the axis; ⨄ with a + inside
    (its vertical and horizontal `bars`), across `plus` of the opening and
    centred in it; ⨆ square in its box. Past Regular they widen by as much as
    their stems thicken, the weight going outward: the opening stays
    Regular's, room for ⨄'s + (in the width TeX gives them, the + filled the
    opening at Black).
    """

    def fitted(location: dict, w: float) -> Shape:
        u = scaled(m, location, "U", w / width(m.shape("U", location)))
        return u.scaled(w / width(u))

    def stem(u: Shape) -> float:
        (a0, a1), *_ = u.runs((u.bounds()[1] + u.bounds()[3]) / 2)
        return a1 - a0

    regular = {**master, "wght": m.axes["wght"].defaultValue}
    u = fitted(master, wide)
    grown = stem(u) - stem(fitted(regular, wide))
    if grown > 0:
        u = fitted(master, wide + 2 * grown)
    cup = stems_to(u, u.bounds()[1] + tall).centred(axis)
    x0, y0, x1, y1 = cup.bounds()
    (a0, a1), (b0, _) = cup.runs(axis)
    stem, middle = a1 - a0, (x0 + x1) / 2
    ys = column(cup, middle)
    bottom, arm, centre = ys[1] - ys[0], plus * (b0 - a1) / 2, (ys[1] + y1) / 2
    upward, across = bars
    cross = [rect(middle - arm, centre - across / 2, middle + arm, centre + across / 2), rect(middle - upward / 2, centre - arm, middle + upward / 2, centre + arm)]
    square = [rect(x0, y0, x0 + stem, y1), rect(x1 - stem, y0, x1, y1), rect(x0, y0, x1, y0 + bottom)]
    return {0x22C3: cup, 0x22C2: cup.rotated(), 0x2A04: Shape.join([cup, *cross], cup.advance), 0x2A06: Shape.join(square, cup.advance)}


def big_operator_glyphs(path, italic_path, upem: int, scripts) -> dict[int, list[NewGlyph]]:
    """
    Each size font's big operators (named after Inter's, mapped to their code
    points). `scripts`: Inter Math's upright font, whose script figures a
    subscript beside an integral is measured with.
    """
    m = Masters(path, [*SUMS.values(), "minus", "minus.case", "plus", "plus.case", "one", "l", "zero", "U", "Lambda", "circlewhite", "uni25EF", "periodcentered", PHI])
    mi = Masters(italic_path, ["integral", "l", "one", "x"])
    zero = script_figure(scripts, "0")
    ms = Masters(scripts, [zero])
    out: dict[int, list[NewGlyph]] = {}
    for size, heights in SIZES.items():
        shapes: dict[int, list[Shape]] = {}
        italics: dict[int, dict[float, float]] = {}
        tall = heights["sum"] * upem

        def put(cp: int, s: Shape) -> None:
            shapes.setdefault(cp, []).append(s)

        for master in m.masters:
            axis = math_axis(m, master)
            regular = {**master, "wght": m.axes["wght"].defaultValue}

            for cp, name in SUMS.items():
                _, y0, _, y1 = m.shape(name, master).bounds()
                s = scaled(m, master, name, tall / (y1 - y0))
                put(cp, s.scaled(tall / height(s)).centred(axis))
            put(COPRODUCT, shapes[0x220F][-1].rotated())

            # the integrals keep the text optical size at every size, as a tall brace's pieces do: the ovals KaTeX lays
            # over ∬ ∭ (images) can't follow it, and in the display size the stems stepped closer (the oval sat off
            # them at large sizes)
            text = {**master, "opsz": m.axes["opsz"].minValue}
            text_axis = math_axis(m, text)
            ints = integrals(mi, text, heights["hooks"], heights["integral"] * upem, text_axis)
            # a subscript: KaTeX starts it at the advance, the superscript at the advance and the italic correction
            # on. The slant leans the stem towards the subscript, so the advance goes where a 0 there keeps TeX's
            # white from the integral's ink (it kept 0.04 em: the limit touched the integral) up to Regular, and past
            # it as much less as Inter's letters keep (`letter_fit`: TeX's white read loose at Black, where Inter's
            # letters keep 0.6 of theirs; under Regular their looser fit set the limits off their integral, a quarter
            # farther at Thin); the italic correction gives that back, so that the superscript stays
            figure = ms.shape(zero, text).scaled(SCRIPT_SIZE).moved(0, SUBSCRIPT[size] * upem)
            fy0, fy1 = figure.bounds()[1], figure.bounds()[3]
            room = SUB_WHITE[size] * mi.shape("x", text).bounds()[3] * min(1.0, letter_fit(m, text))

            def widened(s: Shape) -> float:
                ys = [fy0 + (fy1 - fy0) * i / 40 for i in range(1, 40)]
                white = min(f[0][0] + s.advance - r[-1][1] for y in ys for f, r in [(figure.runs(y), s.runs(y))] if f and r)
                more = max(0.0, room - white)
                s.advance += more
                return more

            # the italic corrections at the weight's masters (the integrals keep the text optical size)
            measured = master["opsz"] == m.axes["opsz"].minValue
            for cp, (s, italic) in ints.items():
                italic -= widened(s)
                put(cp, s)
                if measured:
                    italics.setdefault(cp, {})[master["wght"]] = max(italic, 0) / upem
            # ∮: ∫ and its ring (its last two contours: build.py's ovals() finds them there); its superscript where
            # ∫'s is
            integral = ints[0x222B][0]
            text_regular = {**text, "wght": m.axes["wght"].defaultValue}
            at_regular = integrals(mi, text_regular, heights["hooks"], heights["integral"] * upem, math_axis(m, text_regular))[0x222B][0]
            around = contour_ring(m, text, integral, at_regular, RING[size] * heights["integral"] * upem, text_axis)
            contour = Shape.join([integral, around], integral.advance)
            more = widened(contour)
            put(CONTOUR, contour)
            if measured:
                italics.setdefault(CONTOUR, {})[master["wght"]] = max(italics[0x222B][master["wght"]] - more / upem, 0)

            # the circled operators' strokes (as heavy as the operators, lighter past Regular as Inter's rings)
            light = ring_light(m, master)
            stem = width(max(sign(m, "plus", master).contours(), key=height))
            _, my0, _, my1 = sign(m, "minus", master).bounds()
            for cp, s in cups(m, master, tall, CUP[size] * tall, PLUS[size], (stem * light, (my1 - my0) * light), axis).items():
                put(cp, s)
            wedge = scaled(m, master, "Lambda", tall / height(m.shape("Lambda", master)))
            wedge = wedge.scaled(tall / height(wedge)).centred(axis)
            put(0x22C0, wedge)
            put(0x22C1, wedge.rotated())

            # ⨁ ⨂ ⨀: the dot as large against the ring as TeX's at the regular weight
            dot = m.shape("periodcentered", master).scaled(DOT[size] * tall / width(m.shape("periodcentered", regular)))
            ops = circled(m, master, tall, stem * light, (my1 - my0) * light, dot, axis)
            put(0x2A01, ops[0x2295])
            put(0x2A02, ops[0x2297])
            put(0x2A00, ops[0x2299])
        names = {**SUMS, COPRODUCT: "coproduct", 0x222B: "integral", 0x222C: "dblintegral", 0x222D: "tripleintegral"}
        out[size] = [m.glyph(f"{names.get(cp, f'uni{cp:04X}')}.size{size}", s, cp) for cp, s in shapes.items()]
        ITALIC[size] = {cp: {w: round(m.interpolated(v, w), 5) for w in WEIGHTS} for cp, v in italics.items()}
    return out
