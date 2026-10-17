"""
The MATH table of Inter Math's OpenType font (build/opentype.py): what a math
layout engine reads from a math font.

- Constants: TeX's parameters as Inter Math lays KaTeX out with them
  (src/index.ts, build/patch_katex.py): rules as thick as the minus sign; the
  vertical spaces TeX counts in rules counted in ruleSpacing (Regular's rule,
  across the weights as the gap under Inter's underline); the axis on the
  operators' centre, fractions moved up with it; underlines and overlines
  Inter's own; the rest TeX's (KaTeX's), in KaTeX's em (Inter Math's for
  KaTeX: 2332 units). The rules and what follows them are the text optical
  size's at every size, as KaTeX's (its surds are drawn so).
- Per glyph: italic corrections (the ink past the advance; the integrals' as
  KaTeX has them, by weight), where accents go over letters (where Inter's
  mark feature puts the middle of its ¨'s dots; an italic letter it puts no
  marks over, the middle of its top quarter, as KaTeX's skews), and the
  extended shapes (the larger sizes, the pieces, the big operators).
- Variants (build/math_glyphs.py): the delimiters at every tenth of an em
  from the text size to KaTeX's largest, and the pieces taller ones are
  stacked from; the bars drawn out as tall; √ at as many heights and its
  pieces; the big operators' display style; the arrows upright stacked from
  KaTeX's pieces; and sideways the arrows on the line, the braces, groups and
  brackets over and under, the wide accents and the vector accents.

The variable font's values follow the weight and the optical size through
GDEF's item variation store (VariationIndex device tables, which HarfBuzz
reads from its version after 14.6.0); a static font gets them at its location.
"""

import math
from dataclasses import dataclass, field

from fontTools.otlLib.builder import buildMathTable
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.varLib.builder import buildVarDevTable
from fontTools.varLib.models import VariationModel, normalizeLocation, piecewiseLinearMap
from fontTools.varLib.varStore import OnlineVarStoreBuilder

from math_glyphs import bold_weight
from variable import mark_anchor

# where values are measured: the masters (Thin, Regular, Black at the text and display optical sizes), outlines being
# linear between them; and every weight, for glyphs that aren't (bold letters, at the weight's bold)
MASTERS = [(w, o) for o in (14, 32) for w in (100, 400, 900)]
BOTH_SIZES = [(w, o) for o in (14, 32) for w in range(100, 1000, 100)]
REGULAR = (400, 14)

# TeX's parameters Inter Math keeps (KaTeX's src/fontMetrics.ts, em; a script's at the script size, 0.7): fractions
# and stacks (σ8-σ12), scripts (σ14-σ19: KaTeX's text-style shift, sup2, and the one in cramped styles, sup3; the
# subscript's without a superscript, sub1), limits (ξ9-ξ12), \scriptspace (0.5 pt)
NUM1, NUM2, NUM3, DENOM1, DENOM2 = 0.677, 0.394, 0.444, 0.686, 0.345
SUP2, SUP3, SUB1 = 0.363, 0.289, 0.150
SUP_DROP, SUB_DROP = 0.353 * 0.7, 0.071 * 0.7
BIG_OP_SPACING = (0.111, 0.166, 0.2, 0.6)
SCRIPT_SPACE = 0.05
TEX_AXIS = 0.25
# KaTeX's script sizes (Inter Math's script forms are drawn for them: build/script_glyphs.py)
SCRIPT_PERCENT, SCRIPTSCRIPT_PERCENT = 70, 50
# a radical's index: 5 mu before it (TeX's), and after it Inter Math's -0.36 em (src/inter-math.css: its surd is
# narrower than TeX's), raised by 60 % of the surd's height (TeX's)
ROOT_BEFORE, ROOT_AFTER, ROOT_RAISE = 5 / 18, -0.36, 60
# a delimited formula and a display operator: as tall as ∑ in display style (KaTeX's Size2, 1.3 em). Word reads these
# two the other way round (HarfBuzz swaps them back for Cambria Math only): equal, they read the same everywhere
DISPLAY_MIN = 1.3
# white between math formulas (Latin Modern Math's), a skewed fraction's gaps (Latin Modern Math's)
MATH_LEADING, SKEWED_GAPS = 0.154, (0.35, 0.096)
# how much stacked pieces overlap at least (font units)
MIN_OVERLAP = 40
# what taller braces and groups are stacked from, bottom to top (KaTeX's: build/delimiters.py's brace pieces, Size4); the
# extender is the brace's straight stem
STACKED = {
    0x7B: [0x23A9, 0x23AA, 0x23A8, 0x23AA, 0x23A7],
    0x7D: [0x23AD, 0x23AA, 0x23AC, 0x23AA, 0x23AB],
    0x27EE: [0x23A9, 0x23AA, 0x23A7],
    0x27EF: [0x23AD, 0x23AA, 0x23AB],
    0x23B0: [0x23AD, 0x23AA, 0x23A7],
    0x23B1: [0x23A9, 0x23AA, 0x23AB],
}
EXTENDERS = {0x23AA}

Location = tuple[float, float]
Value = float | dict[Location, float]


@dataclass
class Space:
    """The variable font's axes (min, default, max) and avar, to interpolate values between locations."""

    axes: dict[str, tuple[float, float, float]]
    segments: dict[str, dict[float, float]]

    @staticmethod
    def of(font: TTFont) -> "Space":
        return Space({a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes},
                     font["avar"].segments if "avar" in font else {})

    def normalized(self, loc: Location) -> dict[str, float]:
        """A user location in the axes' normalized coordinates, after avar (where variations live)."""
        n = normalizeLocation({"wght": loc[0], "opsz": loc[1]}, self.axes)
        return {t: piecewiseLinearMap(v, self.segments[t]) if self.segments.get(t) else v for t, v in n.items()}

    def at(self, value: "Value", loc: Location) -> float:
        """A value at a location: as measured there, or between the locations it was measured at."""
        if not isinstance(value, dict):
            return value
        if loc in value:
            return value[loc]
        locations = list(value)
        model = VariationModel([self.normalized(l) for l in locations], axisOrder=["wght", "opsz"])
        return model.interpolateFromMasters(self.normalized(loc), [value[l] for l in locations])


@dataclass
class MathData:
    """The MATH table's content, each value a number or a value by location."""

    space: Space
    constants: dict[str, Value] = field(default_factory=dict)
    italics: dict[str, Value] = field(default_factory=dict)
    accents: dict[str, Value] = field(default_factory=dict)
    extended: set[str] = field(default_factory=set)
    vertical: dict[str, list[tuple[str, int]]] = field(default_factory=dict)
    vertical_assembly: dict[str, list[tuple[str, int, int, int, int]]] = field(default_factory=dict)
    horizontal: dict[str, list[tuple[str, int]]] = field(default_factory=dict)
    horizontal_assembly: dict[str, list[tuple[str, int, int, int, int]]] = field(default_factory=dict)


class Sampler(BasePen):
    """Points along an outline, curves sampled (build.py's)."""

    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.points = []

    def _moveTo(self, p):
        self.points.append(p)

    def _lineTo(self, p):
        self.points.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        for i in range(1, 9):
            t = i / 8
            u = 1 - t
            self.points.append(tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3)))

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        for i in range(1, 9):
            t = i / 8
            u = 1 - t
            self.points.append(tuple(u * u * a + 2 * u * t * b + t * t * c for a, b, c in zip(p0, p1, p2)))


class Measures:
    """A variable font's glyphs at user locations (wght, opsz), cached."""

    def __init__(self, font: TTFont):
        self.font = font
        self._sets: dict[Location, object] = {}

    def glyphs(self, loc: Location):
        if loc not in self._sets:
            self._sets[loc] = self.font.getGlyphSet(location={"wght": loc[0], "opsz": loc[1]})
        return self._sets[loc]

    def bounds(self, name: str, loc: Location) -> tuple[float, float, float, float] | None:
        gs = self.glyphs(loc)
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        return pen.bounds

    def advance(self, name: str, loc: Location) -> float:
        return self.glyphs(loc)[name].width

    def points(self, name: str, loc: Location) -> list[tuple[float, float]]:
        gs = self.glyphs(loc)
        pen = Sampler(gs)
        gs[name].draw(pen)
        return pen.points


def by_location(f, locations: list[Location] = MASTERS) -> dict[Location, float]:
    return {loc: f(loc) for loc in locations}


def underline(inter: TTFont, loc: Location) -> tuple[float, float]:
    """Inter's underline (the line under its ḇ): how far under the baseline its top is, and how thick (font units)."""
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    gs = inter.getGlyphSet(location={"wght": loc[0], "opsz": loc[1]})
    pen = DecomposingRecordingPen(gs)
    gs[inter.getBestCmap()[0x1E07]].draw(pen)
    contours, current = [], []
    for op, args in pen.value:
        if op == "moveTo":
            current = [args[0]]
        elif op in ("closePath", "endPath"):
            contours.append(current)
        else:
            current.extend(args)
    ys = [y for c in contours if max(y for _, y in c) <= 0 for _, y in c]
    return -max(ys), max(ys) - min(ys)


def constants(font: TTFont, m: Measures, cmap: dict[int, str], katex_em: float, inter: TTFont) -> dict[str, Value]:
    """TeX's parameters as Inter Math's KaTeX has them (src/index.ts's globalMetrics), in font units."""
    em = lambda v: v * katex_em  # noqa: E731
    minus, x = cmap[0x2212], cmap[ord("x")]

    def rule(loc: Location) -> float:
        _, y0, _, y1 = m.bounds(minus, loc)
        return y1 - y0

    def axis(loc: Location) -> float:
        _, y0, _, y1 = m.bounds(minus, loc)
        return (y0 + y1) / 2

    # the rules, and what follows them, are the text optical size's at every size, as KaTeX's (its surds are drawn so)
    text = lambda f: {loc: f((loc[0], 14)) for loc in MASTERS}  # noqa: E731
    lines = text(lambda loc: underline(inter, loc))
    rules = text(rule)
    # TeX's vertical spaces: Regular's rule, across the weights as the gap under Inter's underline (src/index.ts)
    spacing = {loc: rules[(400, loc[1])] * lines[loc][0] / lines[(400, loc[1])][0] for loc in MASTERS}
    x_height = by_location(lambda loc: m.bounds(x, loc)[3])
    axes = by_location(axis)
    # fractions and stacks move up with the axis, keeping their distances to it (src/index.ts)
    up = lambda v: {loc: em(v) + axes[loc] - em(TEX_AXIS) for loc in MASTERS}  # noqa: E731
    down = lambda v: {loc: em(v) - axes[loc] + em(TEX_AXIS) for loc in MASTERS}  # noqa: E731
    times = lambda k, value: {loc: k * value[loc] for loc in MASTERS}  # noqa: E731
    gap, thickness = {loc: lines[loc][0] for loc in MASTERS}, {loc: lines[loc][1] for loc in MASTERS}
    cap_height = font["OS/2"].sCapHeight
    # a surd clears its radicand by TeX's display clearance in every style (build/patch_katex.py)
    radical_gap = {loc: spacing[loc] + x_height[loc] / 4 for loc in MASTERS}
    return {
        "ScriptPercentScaleDown": SCRIPT_PERCENT,
        "ScriptScriptPercentScaleDown": SCRIPTSCRIPT_PERCENT,
        "DelimitedSubFormulaMinHeight": em(DISPLAY_MIN),
        "DisplayOperatorMinHeight": em(DISPLAY_MIN),
        "MathLeading": em(MATH_LEADING),
        "AxisHeight": axes,
        "AccentBaseHeight": x_height,
        "FlattenedAccentBaseHeight": cap_height,
        "SubscriptShiftDown": em(SUB1),
        "SubscriptTopMax": times(0.8, x_height),
        "SubscriptBaselineDropMin": em(SUB_DROP),
        "SuperscriptShiftUp": em(SUP2),
        "SuperscriptShiftUpCramped": em(SUP3),
        "SuperscriptBottomMin": times(0.25, x_height),
        "SuperscriptBaselineDropMax": em(SUP_DROP),
        "SubSuperscriptGapMin": times(4, spacing),
        "SuperscriptBottomMaxWithSubscript": times(0.8, x_height),
        "SpaceAfterScript": em(SCRIPT_SPACE),
        "UpperLimitGapMin": em(BIG_OP_SPACING[0]),
        "UpperLimitBaselineRiseMin": em(BIG_OP_SPACING[2]),
        "LowerLimitGapMin": em(BIG_OP_SPACING[1]),
        "LowerLimitBaselineDropMin": em(BIG_OP_SPACING[3]),
        "StackTopShiftUp": up(NUM3),
        "StackTopDisplayStyleShiftUp": up(NUM1),
        "StackBottomShiftDown": down(DENOM2),
        "StackBottomDisplayStyleShiftDown": down(DENOM1),
        "StackGapMin": times(3, spacing),
        "StackDisplayStyleGapMin": times(7, spacing),
        "StretchStackTopShiftUp": em(BIG_OP_SPACING[2]),
        "StretchStackBottomShiftDown": em(BIG_OP_SPACING[3]),
        "StretchStackGapAboveMin": em(BIG_OP_SPACING[0]),
        "StretchStackGapBelowMin": em(BIG_OP_SPACING[1]),
        "FractionNumeratorShiftUp": up(NUM2),
        "FractionNumeratorDisplayStyleShiftUp": up(NUM1),
        "FractionDenominatorShiftDown": down(DENOM2),
        "FractionDenominatorDisplayStyleShiftDown": down(DENOM1),
        "FractionNumeratorGapMin": spacing,
        "FractionNumDisplayStyleGapMin": times(3, spacing),
        "FractionRuleThickness": rules,
        "FractionDenominatorGapMin": spacing,
        "FractionDenomDisplayStyleGapMin": times(3, spacing),
        "SkewedFractionHorizontalGap": em(SKEWED_GAPS[0]),
        "SkewedFractionVerticalGap": em(SKEWED_GAPS[1]),
        "OverbarVerticalGap": gap,
        "OverbarRuleThickness": thickness,
        "OverbarExtraAscender": spacing,
        "UnderbarVerticalGap": gap,
        "UnderbarRuleThickness": thickness,
        "UnderbarExtraDescender": spacing,
        "RadicalVerticalGap": radical_gap,
        "RadicalDisplayStyleVerticalGap": radical_gap,
        "RadicalRuleThickness": rules,
        "RadicalExtraAscender": spacing,
        "RadicalKernBeforeDegree": em(ROOT_BEFORE),
        "RadicalKernAfterDegree": em(ROOT_AFTER),
        "RadicalDegreeBottomRaisePercent": ROOT_RAISE,
    }


def italic_corrections(m: Measures, names: list[str], by_weight: set[str]) -> dict[str, Value]:
    """
    How far each glyph's ink goes past its advance, where it does (italic
    letters; never a glyph of no advance); measured at every weight for those
    that don't vary as the masters (`by_weight`: bold letters).
    """
    out = {}
    for name in names:
        def past(loc: Location, name=name) -> float:
            b = m.bounds(name, loc)
            return max(0.0, b[2] - m.advance(name, loc)) if b else 0.0

        values = by_location(past, BOTH_SIZES if name in by_weight else MASTERS)
        if max(values.values()) >= 1 and m.advance(name, REGULAR) > 0:
            out[name] = values
    return out


def accent_attachments(m: Measures, letters: dict[str, tuple[TTFont, int, bool, bool]], italics: dict[str, Value], space: Space) -> dict[str, Value]:
    """
    Where accents go over each letter (its glyph → Inter's font, its
    character, italic): the middle of the dots of Inter's ¨ over it, where
    Inter's mark feature puts them (Inter Math's accents are Inter's marks, as
    far off ¨'s dots as Inter sets them, in the middle of their advance:
    build/symbol_glyphs.py); over an italic letter Inter puts no marks over,
    the middle of its top quarter and half its italic correction (KaTeX's
    skew, build.py's measure()); over an upright one, its middle (the default).
    """
    out = {}
    marks: dict[int, tuple] = {}
    for name, (inter, cp, italic, bold) in letters.items():
        cmap = inter.getBestCmap()
        # a bold letter is its letter at the weight's bold: where Inter puts marks over that (the bold weight stops at
        # Black: measured by weight)
        locations = BOTH_SIZES if bold else MASTERS
        drawn_at = (lambda loc: (bold_weight(loc[0]), loc[1])) if bold else (lambda loc: loc)
        if id(inter) not in marks:
            mark = cmap[0x0308]

            def dots(loc: Location, inter=inter, mark=mark) -> float:
                gs = inter.getGlyphSet(location={"wght": loc[0], "opsz": loc[1]})
                pen = BoundsPen(gs)
                gs[mark].draw(pen)
                return (pen.bounds[0] + pen.bounds[2]) / 2

            marks[id(inter)] = (mark, {})
        mark, middles = marks[id(inter)]
        base = cmap.get(cp)
        if base is not None and mark_anchor(inter, base, mark, {"wght": 400, "opsz": 14}) is not None:
            values = {}
            for loc in locations:
                at = drawn_at(loc)
                if at not in middles:
                    middles[at] = dots(at)
                location = {"wght": at[0], "opsz": at[1]}
                anchor, own = mark_anchor(inter, base, mark, location), mark_anchor(inter, base, mark, location, own=True)
                values[loc] = anchor[0] - own[0] + middles[at]
            out[name] = values
        elif italic:
            def top_middle(loc: Location, name=name) -> float:
                pts = m.points(name, loc)
                if not pts:
                    return m.advance(name, loc) / 2
                ys = [y for _, y in pts]
                floor = max(ys) - 0.25 * (max(ys) - max(min(ys), 0))
                top = [x for x, y in pts if y >= floor]
                return (min(top) + max(top)) / 2 + space.at(italics.get(name, 0.0), loc) / 2

            out[name] = by_location(top_middle, locations)
    return out


def ink_height(m: Measures, name: str) -> int:
    _, y0, _, y1 = m.bounds(name, REGULAR)
    return round(y1 - y0)


def straight_end(m: Measures, name: str, top: bool) -> int:
    """
    How long the straight stem is at one end of a piece (its connector): the
    shortest of the vertical edges reaching that end, at every master.
    """
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    lengths = []
    for loc in MASTERS:
        gs = m.glyphs(loc)
        pen = DecomposingRecordingPen(gs)
        gs[name].draw(pen)
        _, y0, _, y1 = m.bounds(name, loc)
        edges, current, start = [], None, None
        for op, args in pen.value:
            if op == "moveTo":
                current = start = args[0]
            elif op == "lineTo":
                edges.append((current, args[0]))
                current = args[0]
            elif op in ("qCurveTo", "curveTo"):
                current = args[-1]
            elif op == "closePath":
                edges.append((current, start))
        # the vertical edges that reach the end, how far they run from it
        reach = [abs(a[1] - b[1]) for a, b in edges
                 if abs(a[0] - b[0]) < 0.5 and abs(a[1] - b[1]) > 0.5
                 and abs((max(a[1], b[1]) if top else min(a[1], b[1])) - (y1 if top else y0)) < 0.5]
        lengths.append(min(reach) if reach else 0)
    return math.floor(min(lengths))


def variants(m: Measures, cmap: dict[int, str], sizes: dict[int, dict[int, str]], maps: dict) -> tuple[dict, dict, set]:
    """
    The vertical variants: each delimiter at the text size, KaTeX's four
    sizes and between them (build/math_glyphs.py), the bars drawn out to as
    many, √ at as many heights, the big operators' display style; and what
    taller ones are stacked from.
    """
    vertical, assembly, extended = {}, {}, set()
    chains, cut = maps["delimiters"]
    for cp, chain in chains.items():
        vertical[cmap[cp]] = [(g, ink_height(m, g)) for g in chain]
        extended |= set(chain[1:])
        if cp in cut:
            assembly[cmap[cp]] = cut[cp]
            extended |= {name for name, *_ in cut[cp]}
    for cp, drawn in maps["bars"].items():
        chain = [cmap[cp], *drawn]
        vertical[cmap[cp]] = [(g, ink_height(m, g)) for g in chain]
        extended |= set(drawn)
        # past the tallest, the bar stacked from itself (its whole height straight)
        bar, full = drawn[-1], ink_height(m, drawn[-1])
        assembly[cmap[cp]] = [(bar, 0, 0, full, full), (bar, 1, full, full, full)]
    radicals, parts = maps["radical"]
    vertical[radicals[0]] = [(g, ink_height(m, g)) for g in radicals]
    assembly[radicals[0]] = parts
    extended |= set(radicals[1:]) | {name for name, *_ in parts}
    for cp in sizes[1]:
        if cp in sizes[2] and cp not in chains and cmap.get(cp) == sizes[1][cp]:
            vertical[cmap[cp]] = [(sizes[1][cp], ink_height(m, sizes[1][cp])), (sizes[2][cp], ink_height(m, sizes[2][cp]))]
            extended |= {sizes[1][cp], sizes[2][cp]}
    stacked = {cmap[cp]: [(cmap[p], p in EXTENDERS) for p in pieces] for cp, pieces in STACKED.items() if cp in cmap}
    # the arrows upright: KaTeX's Size1 pieces, ⏐ and ‖ the shafts between
    shafts = {maps["roles"]["Size1"].get(cp) for cp in (0x23D0, 0x2016)}
    stacked |= {base: [(p, p in shafts) for p in pieces] for base, pieces in maps["upright arrows"].items()}
    for base, pieces in stacked.items():
        parts = []
        for i, (name, extender) in enumerate(pieces):
            full = ink_height(m, name)
            if extender:
                parts.append((name, 1, full, full, full))
            else:
                start = straight_end(m, name, top=False) if i > 0 else 0
                end = straight_end(m, name, top=True) if i < len(pieces) - 1 else 0
                parts.append((name, 0, start, end, full))
            extended.add(name)
        assembly[base] = parts
    return vertical, assembly, extended


def horizontal_variants(m: Measures, maps: dict) -> tuple[dict, dict]:
    """
    What stretches sideways (build/math_glyphs.py): each glyph's variants,
    measured by their advance (an accent's, of no advance, by its ink), and its
    pieces.
    """
    chains, parts = maps["horizontal"]

    def width(name: str) -> int:
        advance = m.advance(name, REGULAR)
        if advance:
            return round(advance)
        b = m.bounds(name, REGULAR)
        return round(b[2] - b[0]) if b else 0

    variants = {base: [(g, width(g)) for g in chain] for base, chain in chains.items()}
    return variants, {base: p for base, p in parts.items() if p}


class Store:
    """MATH values that vary, appended to GDEF's item variation store (HarfBuzz reads MATH's variations there)."""

    def __init__(self, font: TTFont, space: Space):
        self.font, self.space = font, space
        self.builder = OnlineVarStoreBuilder([a.axisTag for a in font["fvar"].axes])
        self.models: dict[tuple, VariationModel] = {}
        self.pending: list[tuple[ot.MathValueRecord, int]] = []

    def record(self, record: ot.MathValueRecord, value: Value) -> None:
        if not isinstance(value, dict) or len({round(v) for v in value.values()}) == 1:
            record.Value = round(self.space.at(value, REGULAR))
            return
        locations = tuple(value)
        if locations not in self.models:
            self.models[locations] = VariationModel([self.space.normalized(l) for l in locations], axisOrder=["wght", "opsz"])
        self.builder.setModel(self.models[locations])
        base, index = self.builder.storeMasters([value[l] for l in locations])
        record.Value = base
        self.pending.append((record, index))

    def finish(self) -> None:
        """Our variation data after GDEF's, its regions merged, and each record's device table pointing to its row."""
        store = self.builder.finish()
        gdef = self.font["GDEF"].table
        target = gdef.VarStore
        regions = target.VarRegionList.Region
        key = lambda r: tuple((a.StartCoord, a.PeakCoord, a.EndCoord) for a in r.VarRegionAxis)  # noqa: E731
        known = {key(r): i for i, r in enumerate(regions)}
        remap = []
        for r in store.VarRegionList.Region:
            if key(r) not in known:
                known[key(r)] = len(regions)
                regions.append(r)
            remap.append(known[key(r)])
        target.VarRegionList.RegionCount = len(regions)
        offset = len(target.VarData)
        for data in store.VarData:
            data.VarRegionIndex = [remap[i] for i in data.VarRegionIndex]
            data.VarRegionCount = len(data.VarRegionIndex)
            target.VarData.append(data)
        target.VarDataCount = len(target.VarData)
        for record, index in self.pending:
            record.DeviceTable = buildVarDevTable(((index >> 16) + offset) << 16 | (index & 0xFFFF))


def build_table(font: TTFont, data: MathData, location: Location | None) -> None:
    """The MATH table: its values at a location (a static font), or varying (the variable font, location None)."""
    plain = lambda v: round(data.space.at(v, location or REGULAR))  # noqa: E731
    buildMathTable(
        font,
        constants={k: plain(v) for k, v in data.constants.items()},
        italicsCorrections={g: plain(v) for g, v in data.italics.items()},
        topAccentAttachments={g: plain(v) for g, v in data.accents.items()},
        extendedShapes=data.extended,
        minConnectorOverlap=MIN_OVERLAP,
        vertGlyphVariants=data.vertical,
        vertGlyphAssembly={g: (parts, 0) for g, parts in data.vertical_assembly.items()},
        horizGlyphVariants=data.horizontal or None,
        horizGlyphAssembly={g: (parts, 0) for g, parts in data.horizontal_assembly.items()} or None,
    )
    if location is not None:
        return
    table = font["MATH"].table
    store = Store(font, data.space)
    mc = table.MathConstants
    for name, value in data.constants.items():
        record = getattr(mc, name)
        if isinstance(record, ot.MathValueRecord):
            store.record(record, value)
    info = table.MathGlyphInfo
    for coverage, records, values in (
        (info.MathItalicsCorrectionInfo.Coverage, info.MathItalicsCorrectionInfo.ItalicsCorrection, data.italics),
        (info.MathTopAccentAttachment.TopAccentCoverage, info.MathTopAccentAttachment.TopAccentAttachment, data.accents),
    ):
        for glyph, record in zip(coverage.glyphs, records):
            store.record(record, values[glyph])
    store.finish()


def add_math(font: TTFont, maps: dict, katex_em: float, operator_italics: dict) -> MathData:
    """The variable font's MATH table; its content, for the static fonts'."""
    from opentype import SOURCES

    m = Measures(font)
    cmap = font.getBestCmap()
    inter = {"Upright": TTFont(SOURCES / "InterVariable.ttf"), "Italic": TTFont(SOURCES / "InterVariable-Italic.ttf")}
    data = MathData(Space.of(font))
    data.constants = constants(font, m, cmap, katex_em, inter["Upright"])

    roles = maps["roles"]
    order = font.getGlyphOrder()
    bold = {*maps["bold"].values(), *maps["bold italic"].values()}
    # (KaTeX's own glyphs, which only its features reach, left out)
    katex_only = maps.get("katex only", set())
    data.italics = italic_corrections(m, [g for g in order if not g.startswith(".") and g not in katex_only], bold)
    # the integrals' as KaTeX's build has them, by weight (em)
    for size, table in operator_italics.items():
        n = int(size[4])
        for cp, by_weight in table.items():
            name = roles[f"Size{n}"].get(int(cp))
            if name in order:
                data.italics[name] = {(int(w), 14): v * katex_em for w, v in by_weight.items()}

    letters = {}
    for role, italic in (("Upright", False), ("Italic", True)):
        for cp, name in roles[role].items():
            if chr(cp).isalpha() and name in order:
                letters[name] = (inter[role], cp, italic, False)
    for cp, name in maps["greek"].items():
        letters[name] = (inter["Upright"], cp, False, False)
    for (cps, role, italic) in ((maps["bold"], "Upright", False), (maps["bold italic"], "Italic", True)):
        for cp, name in cps.items():
            if chr(cp).isalpha():
                letters[name] = (inter[role], cp, italic, True)
    data.accents = accent_attachments(m, letters, data.italics, data.space)
    for name, value in maps.get("attachments", {}).items():
        data.accents[name] = value

    sizes = {n: roles[f"Size{n}"] for n in range(1, 5)}
    data.vertical, data.vertical_assembly, data.extended = variants(m, cmap, sizes, maps)
    data.horizontal, data.horizontal_assembly = horizontal_variants(m, maps)
    build_table(font, data, None)
    return data


def static_math(font: TTFont, data: MathData, location: dict) -> None:
    """A static font's MATH table, its values at its location."""
    build_table(font, data, (location["wght"], location["opsz"]))
