"""
Building new variable glyphs from Inter's, master by master.

Inter is drawn at six masters (Thin, Regular, Black × text and display
optical sizes). A new glyph is constructed at each of them, from static
instances of Inter (at the master, or at another weight when a part is scaled
and its stroke must not thin), then its masters become gvar variations: the
glyph follows the weight and optical size like Inter's own.

A part scaled down is drawn heavier, and one scaled up lighter, so that its
stroke still matches the rest: past Black or under Thin when it must (Inter's
outlines vary linearly between its masters: they are drawn on along those
lines), or the scaled part would be lighter (or heavier) than its neighbours
at the ends of the weight axis.
"""

from dataclasses import dataclass, field

from fontTools import subset
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib import instancer
from fontTools.varLib.models import VariationModel, piecewiseLinearMap

# the glyph whose stem measures the weight of a design
STEM = "one"


@dataclass
class Shape:
    """One master's outline: TrueType points (on-curve flags), contour ends, advance."""

    points: list[tuple[float, float]]
    on: list[bool]
    ends: list[int]
    advance: float

    @staticmethod
    def of(font: TTFont, name: str) -> "Shape":
        """A static font's glyph, components flattened."""
        coords, ends, flags = font["glyf"][name].getCoordinates(font["glyf"])
        return Shape([(x, y) for x, y in coords], [bool(f & 1) for f in flags], list(ends), font["hmtx"][name][0])

    @staticmethod
    def polygon(points: list[tuple[float, float]], advance: float = 0) -> "Shape":
        return Shape(list(points), [True] * len(points), [len(points) - 1], advance)

    def contours(self) -> list["Shape"]:
        out, start = [], 0
        for end in self.ends:
            out.append(Shape(self.points[start : end + 1], self.on[start : end + 1], [end - start], self.advance))
            start = end + 1
        return out

    def select(self, indices: list[int]) -> "Shape":
        cs = self.contours()
        return Shape.join([cs[i] for i in indices], self.advance)

    @staticmethod
    def join(shapes: list["Shape"], advance: float) -> "Shape":
        points, on, ends = [], [], []
        for s in shapes:
            base = len(points)
            points += s.points
            on += s.on
            ends += [base + e for e in s.ends]
        return Shape(points, on, ends, advance)

    def __add__(self, other: "Shape") -> "Shape":
        return Shape.join([self, other], self.advance)

    def map(self, f) -> "Shape":
        return Shape([f(x, y) for x, y in self.points], list(self.on), list(self.ends), self.advance)

    def moved(self, dx: float, dy: float) -> "Shape":
        return self.map(lambda x, y: (x + dx, y + dy))

    def scaled(self, s: float) -> "Shape":
        out = self.map(lambda x, y: (x * s, y * s))
        out.advance = self.advance * s
        return out

    def mirrored(self) -> "Shape":
        """Left to right, within the advance (contours reversed: a mirror flips their direction)."""
        out = []
        for c in self.contours():
            pts = [(self.advance - x, y) for x, y in reversed(c.points)]
            out.append(Shape(pts, list(reversed(c.on)), c.ends, self.advance))
        return Shape.join(out, self.advance)

    def rotated(self) -> "Shape":
        """Half a turn, about the centre of the ink (a rotation keeps the contours' direction)."""
        x0, y0, x1, y1 = self.bounds()
        return self.map(lambda x, y: (x0 + x1 - x, y0 + y1 - y))

    def turned(self, degrees: float, about: tuple[float, float] | None = None) -> "Shape":
        """Turned anticlockwise about a point (by default the centre of the ink; a rotation keeps the contours' direction)."""
        import math

        if about is None:
            x0, y0, x1, y1 = self.bounds()
            about = ((x0 + x1) / 2, (y0 + y1) / 2)
        cx, cy = about
        c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
        return self.map(lambda x, y: (cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c))

    def bounds(self) -> tuple[float, float, float, float]:
        xs = [x for x, _ in self.points]
        ys = [y for _, y in self.points]
        return min(xs), min(ys), max(xs), max(ys)

    def span(self, y: float) -> tuple[float, float]:
        """Horizontal extent at height y (points taken as a polygon: enough across straight stems)."""
        xs = []
        for c in self.contours():
            pts = c.points
            for i, p in enumerate(pts):
                q = pts[(i + 1) % len(pts)]
                if (p[1] - y) * (q[1] - y) <= 0 and p[1] != q[1]:
                    xs.append(p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]))
        return min(xs), max(xs)

    def runs(self, y: float) -> list[tuple[float, float]]:
        """
        The ink at height y, as (left, right) runs (points taken as a polygon):
        where the winding is not zero, as Inter's outlines overlap.
        """
        hits = []
        for c in self.contours():
            pts = c.points
            for i, p in enumerate(pts):
                q = pts[(i + 1) % len(pts)]
                # half open: a point on the line counts once
                if (p[1] <= y < q[1]) or (q[1] <= y < p[1]):
                    hits.append((p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]), 1 if q[1] > p[1] else -1))
        edges, winding = [], 0
        for x, turn in sorted(hits):
            before, winding = winding, winding + turn
            if (before == 0) != (winding == 0):
                edges.append(x)
        return list(zip(edges[::2], edges[1::2]))

    def side(self, height: float = 0.5) -> float:
        """The width of its leftmost stroke at a height (a share of its ink's), a measure of its weight."""
        _, y0, _, y1 = self.bounds()
        x0, x1 = self.runs(y0 + (y1 - y0) * height)[0]
        return x1 - x0

    def across(self, height: float = 0.5) -> float:
        """The width of its leftmost stroke across it (it may slant), at a height (a share of its ink's)."""
        import math

        _, y0, _, y1 = self.bounds()
        lo, hi = y0 + (y1 - y0) * (height - 0.1), y0 + (y1 - y0) * (height + 0.1)
        slope = (self.runs(hi)[0][0] - self.runs(lo)[0][0]) / (hi - lo)
        return self.side(height) / math.hypot(1, slope)

    def bars_to(self, x0: float, x1: float, square: float | None = None) -> "Shape":
        """
        Its horizontal bars (four-point contours wider than tall) spanning x0 to
        x1; with `square` (a height), its vertical bar as long, centred on it.
        """
        out = []
        for c in self.contours():
            bx0, by0, bx1, by1 = c.bounds()
            if len(c.points) == 4 and all(c.on) and bx1 - bx0 > by1 - by0:
                mid = (bx0 + bx1) / 2
                c = c.map(lambda x, y: (x0 if x < mid else x1, y))
            elif len(c.points) == 4 and all(c.on) and square is not None:
                mid, half = (by0 + by1) / 2, (x1 - x0) / 2
                c = c.map(lambda x, y: (x, square - half if y < mid else square + half))
            out.append(c)
        return Shape.join(out, self.advance)

    def centred(self, y: float) -> "Shape":
        """Ink centred vertically on y."""
        _, y0, _, y1 = self.bounds()
        return self.moved(0, y - (y0 + y1) / 2)

    def spaced(self, side: float) -> "Shape":
        """Ink with `side` on each side: the advance follows."""
        x0, _, x1, _ = self.bounds()
        out = self.moved(side - x0, 0)
        out.advance = x1 - x0 + 2 * side
        return out


@dataclass
class NewGlyph:
    name: str
    glyph: Glyph
    advance: int
    variations: list[TupleVariation]
    unicode: int | None = None


@dataclass
class Masters:
    """Inter's masters, its static instances (cached), and the weight of its stems."""

    path: object
    glyphs: list[str]
    font: TTFont = field(init=False)
    masters: list[dict] = field(init=False)
    default: int = field(init=False)

    def __post_init__(self):
        self.font = TTFont(self.path)
        axes = {a.axisTag: a for a in self.font["fvar"].axes}
        self.axes = axes
        wght, opsz = axes["wght"], axes["opsz"]
        self.masters = [
            {"wght": w, "opsz": o} for o in (opsz.defaultValue, opsz.maxValue) for w in (wght.minValue, wght.defaultValue, wght.maxValue)
        ]
        self.default = self.masters.index({"wght": wght.defaultValue, "opsz": opsz.defaultValue})
        self.model = VariationModel([self._normalized(m) for m in self.masters], axisOrder=["wght", "opsz"])
        self.weights = range(int(wght.minValue), int(wght.maxValue) + 1, 10)
        # the glyphs drawn from, alone, to make instances of quickly
        small = TTFont(self.path)
        options = subset.Options()
        options.layout_features = []
        options.notdef_outline = True
        sub = subset.Subsetter(options)
        names = set(self.font.getGlyphOrder())
        sub.populate(glyphs=[n for n in dict.fromkeys([*self.glyphs, STEM]) if n in names])
        sub.subset(small)
        self._small = small
        self._instances: dict[tuple, TTFont] = {}
        self._stems: dict[tuple, tuple] = {}

    def _normalized(self, location: dict) -> dict:
        return {t: (-1.0 if v == self.axes[t].minValue else 1.0) for t, v in location.items() if v != self.axes[t].defaultValue}

    def instance(self, wght: float, opsz: float) -> TTFont:
        key = (wght, opsz)
        if key not in self._instances:
            self._instances[key] = instancer.instantiateVariableFont(self._small, {"wght": wght, "opsz": opsz}, inplace=False)
        return self._instances[key]

    def shape(self, name: str, master: dict, wght: float | None = None) -> Shape:
        """
        A glyph at a master, or at another weight of its optical size (past
        Black, drawn on from Regular to Black; under Thin, from Regular to Thin).
        """
        w = wght if wght is not None else master["wght"]
        thin, regular, black = self.axes["wght"].minValue, self.axes["wght"].defaultValue, self.axes["wght"].maxValue
        if thin <= w <= black:
            return Shape.of(self.instance(w, master["opsz"]), name)
        end = black if w > black else thin
        a, b = Shape.of(self.instance(regular, master["opsz"]), name), Shape.of(self.instance(end, master["opsz"]), name)
        t = (w - end) / (end - regular)
        points = [(bx + (bx - ax) * t, by + (by - ay) * t) for (ax, ay), (bx, by) in zip(a.points, b.points)]
        return Shape(points, list(b.on), list(b.ends), b.advance + (b.advance - a.advance) * t)

    def section(self, name: str, wght: float, opsz: float) -> tuple[float, float, float]:
        """Width of a glyph's single stem at mid-height, and its bottom and top."""
        key = (name, wght, opsz)
        if key not in self._stems:
            self._stems[key] = cross_section(self.font, name, {"wght": wght, "opsz": opsz})
        return self._stems[key]

    def stem(self, wght: float, opsz: float) -> float:
        return self.section(STEM, wght, opsz)[0]

    def lighter(self, master: dict, offset: float) -> dict:
        """A master's location, `offset` weight units lighter (no lighter than the axis allows)."""
        return {**master, "wght": max(self.axes["wght"].minValue, master["wght"] - offset)}

    def weight_for(self, measure, target: float) -> float:
        """
        The weight at which measure(weight) (a stroke's width) is target.
        Inter's outlines are linear between its masters in the axis's mapped
        coordinate (its avar bends the weight axis between Regular and Black),
        and drawn on past Black or under Thin (shape()).
        """
        wght = self.axes["wght"]
        lo, mid, hi = wght.minValue, wght.defaultValue, wght.maxValue
        m_lo, m_mid, m_hi = measure(lo), measure(mid), measure(hi)
        if target >= m_mid:
            t = (target - m_mid) / (m_hi - m_mid) if m_hi != m_mid else 0.0
        else:
            t = (target - m_mid) / (m_mid - m_lo) if m_mid != m_lo else 0.0
        if t > 1:
            return hi + (t - 1) * (hi - mid)
        if t < -1:
            return lo + (t + 1) * (mid - lo)
        # from the mapped coordinate back to a weight
        segments = self.font["avar"].segments.get("wght", {}) if "avar" in self.font else {}
        n = piecewiseLinearMap(t, {v: k for k, v in segments.items()}) if segments else t
        return mid + n * ((hi - mid) if n >= 0 else (mid - lo))

    def interpolated(self, values: dict[float, float], wght: float) -> float:
        """
        A measure known at the weight axis's masters (`values`: Thin's,
        Regular's and Black's, by weight) at any weight between them: linear in
        the axis's mapped coordinate, as the outlines are.
        """
        wght_axis = self.axes["wght"]
        lo, mid, hi = wght_axis.minValue, wght_axis.defaultValue, wght_axis.maxValue
        t = (wght - mid) / ((hi - mid) if wght >= mid else (mid - lo))
        segments = self.font["avar"].segments.get("wght", {}) if "avar" in self.font else {}
        n = piecewiseLinearMap(t, segments) if segments else t
        return values[mid] + n * ((values[hi] - values[mid]) if n >= 0 else (values[mid] - values[lo]))

    def heavier(self, master: dict, scale: float) -> float:
        """The weight whose stems, scaled by `scale`, are as thick as the master's."""
        return self.weight_for(lambda w: self.stem(w, master["opsz"]) * scale, self.stem(master["wght"], master["opsz"]))

    def fitted(self, name: str, master: dict, scale: float, target: float, probe=Shape.side) -> Shape:
        """A glyph scaled by `scale`, at the weight that makes its stroke (`probe`, scaled) `target` wide."""
        w = self.weight_for(lambda w: probe(self.shape(name, master, w)) * scale, target)
        return self.shape(name, master, w).scaled(scale)

    def glyph(self, name: str, shapes: list[Shape], unicode: int | None = None) -> NewGlyph:
        """A variable glyph from its shape at each master (same points, in the same order)."""
        base = shapes[self.default]
        assert all(len(s.points) == len(base.points) and s.ends == base.ends for s in shapes), f"{name}: masters differ"
        glyph = Glyph()
        glyph.numberOfContours = len(base.ends)
        glyph.coordinates = GlyphCoordinates([(round(x), round(y)) for x, y in base.points])
        glyph.flags = bytearray(int(on) for on in base.on)
        glyph.flags[0] |= 0x40  # OVERLAP_SIMPLE: parts and flattened components may overlap
        glyph.endPtsOfContours = list(base.ends)
        glyph.program = ttProgram.Program()
        glyph.program.fromBytecode(b"")
        # each master's points plus the phantom points (origin, advance, top, bottom)
        values = [GlyphCoordinates([(round(x), round(y)) for x, y in s.points] + [(0, 0), (round(s.advance), 0), (0, 0), (0, 0)]) for s in shapes]
        deltas = self.model.getDeltas(values)
        variations = [
            TupleVariation(support, [tuple(p) for p in delta])
            for support, delta in zip(self.model.supports, deltas)
            if support and any(x or y for x, y in delta)
        ]
        return NewGlyph(name, glyph, round(base.advance), variations, unicode)


def cross_section(font: TTFont, name: str, location: dict) -> tuple[float, float, float]:
    """Width of a glyph's single stem at mid-height, and its bottom and top."""
    gs = font.getGlyphSet(location=location)
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    segments, current, start = [], None, None
    for op, args in pen.value:
        if op == "moveTo":
            current = start = args[0]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            segments.append((current, args[-1]))
            current = args[-1]
        elif op == "closePath":
            segments.append((current, start))
    ys = [p[1] for s in segments for p in s]
    bottom, top = min(ys), max(ys)
    mid = (bottom + top) / 2
    xs = sorted(a[0] + (mid - a[1]) * (b[0] - a[0]) / (b[1] - a[1]) for a, b in segments if (a[1] - mid) * (b[1] - mid) < 0)
    assert len(xs) == 2, f"{name} is not a single stem at mid-height ({len(xs)} crossings)"
    return xs[1] - xs[0], bottom, top


def add_glyphs(font: TTFont, glyphs: list[NewGlyph]) -> None:
    """Into a font with gvar (HVAR is rebuilt afterwards); mapped in the cmap when they have a code point."""
    # read the tables before the glyph order grows (fontTools decompiles them lazily, against it)
    glyf, hmtx, gvar = font["glyf"], font["hmtx"], font["gvar"]
    for g in glyphs:
        font.setGlyphOrder([*font.getGlyphOrder(), g.name])
        glyf.glyphOrder = font.getGlyphOrder()
        glyf[g.name] = g.glyph
        g.glyph.recalcBounds(glyf)
        hmtx[g.name] = (g.advance, g.glyph.xMin)
        gvar.variations[g.name] = g.variations
        if g.unicode is not None:
            for table in font["cmap"].tables:
                if table.isUnicode():
                    table.cmap[g.unicode] = g.name


def kerning(font: TTFont, left: str, right: str, location: dict) -> float:
    """The kern between two glyphs at a location (its GPOS pair adjustment of the left one's advance, font units)."""
    from fontTools.varLib.models import normalizeLocation
    from fontTools.varLib.varStore import VarStoreInstancer

    if "GPOS" not in font:
        return 0.0
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes}
    normalized = normalizeLocation(location, axes)
    if "avar" in font:
        normalized = {t: piecewiseLinearMap(v, font["avar"].segments[t]) if font["avar"].segments.get(t) else v for t, v in normalized.items()}
    store = VarStoreInstancer(font["GDEF"].table.VarStore, font["fvar"].axes, normalized) if getattr(font["GDEF"].table, "VarStore", None) else None

    def value(record) -> float:
        v = getattr(record, "XAdvance", 0) or 0 if record is not None else 0
        device = getattr(record, "XAdvDevice", None)
        if store is not None and device is not None and getattr(device, "DeltaFormat", 0) == 0x8000:
            v += store[(device.StartSize << 16) + device.EndSize]
        return v

    gpos = font["GPOS"].table
    lookups = sorted({i for r in gpos.FeatureList.FeatureRecord if r.FeatureTag == "kern" for i in r.Feature.LookupListIndex})
    for index in lookups:
        lookup = gpos.LookupList.Lookup[index]
        for st in (s.ExtSubTable if lookup.LookupType == 9 else s for s in lookup.SubTable):
            if getattr(st, "Format", None) == 1 and left in st.Coverage.glyphs:
                for pair in st.PairSet[st.Coverage.glyphs.index(left)].PairValueRecord:
                    if pair.SecondGlyph == right:
                        return value(pair.Value1)
            elif getattr(st, "Format", None) == 2 and left in st.Coverage.glyphs:
                v = value(st.Class1Record[st.ClassDef1.classDefs.get(left, 0)].Class2Record[st.ClassDef2.classDefs.get(right, 0)].Value1)
                if v:
                    return v
    return 0.0


def mark_anchor(font: TTFont, base: str, mark: str, location: dict, own: bool = False) -> tuple[float, float] | None:
    """
    Where a font's mark feature attaches `mark` over or under `base` at a
    location: the base's anchor for the mark's class (font units), or None;
    with `own`, the mark's own anchor (the point of it that goes there).
    """
    from fontTools.varLib.models import normalizeLocation
    from fontTools.varLib.varStore import VarStoreInstancer

    if "GPOS" not in font:
        return None
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes} if "fvar" in font else {}
    normalized = normalizeLocation(location, axes) if axes else {}
    if "avar" in font:
        normalized = {t: piecewiseLinearMap(v, font["avar"].segments[t]) if font["avar"].segments.get(t) else v for t, v in normalized.items()}
    gdef = font["GDEF"].table if "GDEF" in font else None
    store = VarStoreInstancer(gdef.VarStore, font["fvar"].axes, normalized) if gdef is not None and getattr(gdef, "VarStore", None) else None

    def coordinate(anchor, axis: str) -> float:
        v = getattr(anchor, f"{axis}Coordinate")
        device = getattr(anchor, f"{axis}DeviceTable", None)
        if store is not None and device is not None and getattr(device, "DeltaFormat", 0) == 0x8000:
            v += store[(device.StartSize << 16) + device.EndSize]
        return v

    gpos = font["GPOS"].table
    lookups = sorted({i for r in gpos.FeatureList.FeatureRecord if r.FeatureTag == "mark" for i in r.Feature.LookupListIndex})
    for index in lookups:
        lookup = gpos.LookupList.Lookup[index]
        for st in (s.ExtSubTable if lookup.LookupType == 9 else s for s in lookup.SubTable):
            if getattr(st, "LookupType", lookup.LookupType) != 4 or not hasattr(st, "BaseCoverage"):
                continue
            if base in st.BaseCoverage.glyphs and mark in st.MarkCoverage.glyphs:
                record = st.MarkArray.MarkRecord[st.MarkCoverage.glyphs.index(mark)]
                anchor = record.MarkAnchor if own else st.BaseArray.BaseRecord[st.BaseCoverage.glyphs.index(base)].BaseAnchor[record.Class]
                if anchor is not None:
                    return coordinate(anchor, "X"), coordinate(anchor, "Y")
    return None
