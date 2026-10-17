#!/usr/bin/env python3
"""
Inter Math as an OpenType math font: one font with a MATH table, the
standard way fonts carry math layout, for LaTeX (LuaLaTeX and XeLaTeX with
unicode-math), Typst, Word, PowerPoint and LibreOffice, and MathML in
browsers (and what builds on it: Temml, MathJax 4's fonts).

    build/.venv/bin/python build/opentype.py     (pnpm font:build runs it last)

It is made from the fonts build.py draws for KaTeX's roles (build/out/), the
same glyphs in one font:
- the upright font's glyphs, mapped as there;
- the italic font's letters at Unicode's math italic letters (U+1D434…, ℎ,
  the dotless 𝚤 𝚥); Inter being a sans serif, the sans serif letters are the
  upright and italic ones (\\mathsf is Inter Math in KaTeX too);
- the blackboard letters at the double-struck ones;
- the four sizes' delimiters and big operators as the larger sizes of the
  text ones (the big operators' text style is Size1's, their display style
  Size2's), with the pieces taller ones are stacked from;
- KaTeX's script forms as the script styles' (ssty), dotless i and j for
  accents (dtls), the triangle arrowheads through ss01 as in KaTeX;
- the MATH table (math_table.py): TeX's parameters as Inter Math gives them to
  KaTeX (src/index.ts), the glyphs' italic corrections, where accents go over
  them, the delimiters' sizes and how taller ones are built.

KaTeX takes the same font (src/inter-math.css): each of its roles is a feature
of the font's own (KTXM upright, KTXI italic, KTXA AMS, KTXB blackboard, KTX1
to KTX4 the sizes: uppercase tags, which no app shows), giving the role's
glyph where the math font maps another, its script forms ss19 and ss20, its
private-use code points mapped. Its em, ascent and descent are the stylesheet's
(size-adjust and overrides).

The em is Inter's, 2048 units, so that math is as large as Inter's text at
the same size; KaTeX's fonts have the same units in a larger em (2332: Inter's
+ − = on TeX's axis), which TeX's parameters, in KaTeX's em, are measured in.

Out: build/out/opentype/InterMathVariable.ttf (weight and optical size, its
MATH values following the weight: GDEF's item variation store, which
HarfBuzz reads from its version after 14.6.0) and its WOFF2 in fonts/;
build/out/opentype/InterMath-<Weight>.ttf, the nine weights at the text
optical size, for desktop apps, which read a font's one MATH table, and
their WOFF2 in fonts/ for the web (browsers don't apply a MATH table's
variations yet).
"""

import json
import re
from copy import deepcopy
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent, GlyphCoordinates
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib import instancer
from fontTools.varLib.hvar import add_HVAR
from fontTools.varLib.models import VariationModel

from math_glyphs import DELIMITER_HEIGHTS, bold_glyphs, copied_glyphs, delimiter_glyphs, horizontal_glyphs, radical_glyphs
from math_table import Space, add_math, static_math
from variable import add_glyphs

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "out"
OPENTYPE = OUT / "opentype"
FONTS = ROOT / "fonts"
SOURCES = ROOT / "sources" / "inter"

FAMILY = "Inter Math"
VARIABLE = "InterMathVariable"
# Inter's em: math as large as Inter's text at the same size
UPEM = 2048
# the weights, at the text optical size, as Inter's named instances
STYLES = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold",
          800: "ExtraBold", 900: "Black"}
TEXT_OPSZ = 14
VERSION = json.loads((ROOT / "package.json").read_text())["version"]
_major, _minor, _patch = (int(p) for p in VERSION.split("-")[0].split("."))
FONT_VERSION = f"{_major}.{_minor * 100 + _patch:03d}"

# the fonts build.py draws for KaTeX's roles, and the suffix their glyphs take here (the upright font's keep their names)
ROLES = {"Upright": "", "Italic": ".it", "AMS": ".ams", "Blackboard": ".bb", "Size1": ".s1", "Size2": ".s2", "Size3": ".s3",
         "Size4": ".s4"}
# KaTeX's roles as features of the font's own (custom tags are uppercase), which src/inter-math.css turns on one at a
# time: the role's glyph at each code point where the math font maps another
KATEX = {"Upright": "KTXM", "Italic": "KTXI", "AMS": "KTXA", "Blackboard": "KTXB", "Size1": "KTX1", "Size2": "KTX2",
         "Size3": "KTX3", "Size4": "KTX4"}
# KaTeX's stylistic sets: its script forms (scripts, second-level scripts: the script style's ssty alternates 1 and 2),
# its triangle arrowheads (setMathFont's arrowHeads), kept as they are
SCRIPT, SCRIPTSCRIPT, TRIANGLES = "ss19", "ss20", "ss01"

# Unicode's math alphabets, in their order: Latin, then the Greek capitals (ϴ among them), ∇, the small letters (ς
# among them), ∂ and the variants ϵ ϑ ϰ ϕ ϱ ϖ; the holes the Letterlike Symbols block fills (ℎ ℂ ℍ…) listed apart
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GREEK_CAPITALS = [0x391, 0x392, 0x393, 0x394, 0x395, 0x396, 0x397, 0x398, 0x399, 0x39A, 0x39B, 0x39C, 0x39D, 0x39E, 0x39F,
                  0x3A0, 0x3A1, 0x3F4, 0x3A3, 0x3A4, 0x3A5, 0x3A6, 0x3A7, 0x3A8, 0x3A9]
# the letter each Greek capital looks like: the Latin ones where KaTeX's fonts have no Greek glyph (Α is A)
GREEK_AS_LATIN = "ABΓΔEZHΘIKΛMNΞOΠPΘΣTΥΦXΨΩ"
GREEK_SMALL = [*range(0x3B1, 0x3CA)]
GREEK_AFTER = [0x2202, 0x3F5, 0x3D1, 0x3F0, 0x3D5, 0x3F1, 0x3D6]
HOLES = {0x1D455: 0x210E, 0x1D49D: 0x212C, 0x1D4A0: 0x2130, 0x1D4A1: 0x2131, 0x1D4A3: 0x210B, 0x1D4A4: 0x2110,
         0x1D4A7: 0x2112, 0x1D4A8: 0x2133, 0x1D4AD: 0x211B, 0x1D4BA: 0x212F, 0x1D4BC: 0x210A, 0x1D4C4: 0x2134,
         0x1D506: 0x212D, 0x1D50B: 0x210C, 0x1D50C: 0x2111, 0x1D515: 0x211C, 0x1D51D: 0x2128, 0x1D53A: 0x2102,
         0x1D53F: 0x210D, 0x1D545: 0x2115, 0x1D547: 0x2119, 0x1D548: 0x211A, 0x1D549: 0x211D, 0x1D551: 0x2124}
# Inter's upright small Greek (KaTeX has none: \upalpha, MathML's upright α)
UPRIGHT_GREEK = [*range(0x3B1, 0x3CA), 0x3D1, 0x3D5, 0x3D6, 0x3F1, 0x3F5, 0x3F0]
# the big operators: their text style is Size1's, their display style Size2's (KaTeX's)
BIG_OPERATORS = [0x220F, 0x2210, 0x2211, 0x222B, 0x222C, 0x222D, 0x222E, 0x22C0, 0x22C1, 0x22C2, 0x22C3, 0x2A00, 0x2A01,
                 0x2A02, 0x2A04, 0x2A06]
# the brace's pieces (Size4), which KaTeX stacks taller braces from
BRACE_PIECES = [0x23A7, 0x23A8, 0x23A9, 0x23AA, 0x23AB, 0x23AC, 0x23AD]
# math accents: Unicode's combining marks (unicode-math's \hat \tilde…; MathML) → the character KaTeX sets each
# accent with, which Inter Math draws as Inter's mark, where Inter puts it over x (build/symbol_glyphs.py)
ACCENTS = {0x0300: 0x02CB, 0x0301: 0x02CA, 0x0302: 0x005E, 0x0303: 0x007E, 0x0304: 0x02C9, 0x0306: 0x02D8, 0x0307: 0x02D9,
           0x0308: 0x00A8, 0x030A: 0x02DA, 0x030C: 0x02C7}
# KaTeX's \not slash (private use) at Unicode's combining long solidus overlay (unicode-math's \not)
NOT_SLASH = (0xE020, 0x0338)
# negated relations KaTeX sets as \not over the relation (≠ is \not=) and unicode-math as one character: the relation
# with \not's slash across its middle
NEGATED = {0x2260: 0x3D, 0x2262: 0x2261, 0x2249: 0x2248, 0x2244: 0x2243, 0x2247: 0x2245, 0x2284: 0x2282, 0x2285: 0x2283,
           0x226D: 0x224D, 0x22E2: 0x2291, 0x22E3: 0x2292, 0x2274: 0x2272, 0x2275: 0x2273, 0x2278: 0x2276, 0x2279: 0x2277}
# the integrals, whose italic correction an engine counts in their advance (MathML Core, LuaTeX: a large operator's
# subscript goes at its advance less its italic correction, its superscript at its advance)
INTEGRALS = [0x222B, 0x222C, 0x222D, 0x222E]
MASTERS = [(w, o) for o in (14, 32) for w in (100, 400, 900)]


def singles(font: TTFont, tag: str) -> dict[str, str]:
    """A feature's single substitutions (glyph → alternate)."""
    if "GSUB" not in font:
        return {}
    gsub = font["GSUB"].table
    lookups = sorted({i for r in gsub.FeatureList.FeatureRecord if r.FeatureTag == tag for i in r.Feature.LookupListIndex})
    out = {}
    for i in lookups:
        lookup = gsub.LookupList.Lookup[i]
        for st in lookup.SubTable:
            st = st.ExtSubTable if lookup.LookupType == 7 else st
            out.update(getattr(st, "mapping", {}) or {})
    return out


class Role:
    """
    One of build.py's fonts, its glyphs renamed for the math font: the role's
    suffix, and a name for the forms its stylistic sets reach (A.it.ssty…),
    so that a PDF still reads them (a name's base is its character).
    """

    def __init__(self, role: str):
        path = OUT / f"InterMath-{role}.ttf"
        probe = TTFont(path)
        suffix = ROLES[role]
        order = probe.getGlyphOrder()
        names = {n: n + suffix for n in order}
        script, scriptscript, triangles = singles(probe, SCRIPT), singles(probe, SCRIPTSCRIPT), singles(probe, TRIANGLES)
        for base, alt in script.items():
            names[alt] = f"{base}{suffix}.ssty" if scriptscript.get(base) == alt else f"{base}{suffix}.ssty1"
        for base, alt in scriptscript.items():
            if script.get(base) != alt:
                names[alt] = f"{base}{suffix}.ssty2"
        for base, alt in triangles.items():
            names[alt] = f"{base}{suffix}.ss01"
        names[".notdef"] = ".notdef"
        assert len(set(names.values())) == len(names), f"{role}: glyph names collide"
        self.role, self.names = role, names
        self.path = path
        self.probe_cmap = probe.getBestCmap()
        self.cmap = {cp: names[g] for cp, g in self.probe_cmap.items()}
        self.script = {names[b]: names[a] for b, a in script.items()}
        self.scriptscript = {names[b]: names[a] for b, a in scriptscript.items()}
        self.triangles = {names[b]: names[a] for b, a in triangles.items()}
        # read again, renamed before any table is: every table then decompiles with the new names
        self.font = TTFont(path)
        self.font.setGlyphOrder([names[n] for n in order])

    def closure(self, wanted: set[str]) -> list[str]:
        """The glyphs wanted with the components they are made of, in the font's order."""
        glyf, seen, todo = self.font["glyf"], set(), list(wanted)
        while todo:
            name = todo.pop()
            if name in seen:
                continue
            seen.add(name)
            g = glyf[name]
            if g.isComposite():
                todo.extend(c.glyphName for c in g.components)
        return [n for n in self.font.getGlyphOrder() if n in seen]


def copy_glyphs(font: TTFont, source: TTFont, names: list[str]) -> None:
    """Glyphs (already renamed) from another of the fonts into this one, with their variations."""
    glyf, hmtx, gvar = font["glyf"], font["hmtx"], font["gvar"]
    sglyf, shmtx, sgvar = source["glyf"], source["hmtx"], source["gvar"]
    new = [n for n in names if n not in glyf.glyphs]
    font.setGlyphOrder([*font.getGlyphOrder(), *new])
    glyf.glyphOrder = font.getGlyphOrder()
    for n in new:
        glyf.glyphs[n] = sglyf[n]
        hmtx.metrics[n] = shmtx.metrics[n]
        gvar.variations[n] = sgvar.variations.get(n, [])


def duplicate(font: TTFont, name: str, new: str) -> None:
    """A copy of a glyph (its outline or components, advance and variations) under another name."""
    glyf, hmtx, gvar = font["glyf"], font["hmtx"], font["gvar"]
    font.setGlyphOrder([*font.getGlyphOrder(), new])
    glyf.glyphOrder = font.getGlyphOrder()
    glyf.glyphs[new] = deepcopy(glyf[name])
    hmtx.metrics[new] = hmtx.metrics[name]
    gvar.variations[new] = deepcopy(gvar.variations.get(name, []))


def merge_kerning(font: TTFont, source: TTFont) -> None:
    """
    Another of the fonts' kerning (renamed already: its glyphs are this
    font's) added to this font's: its lookups after this font's, in its kern
    features, their variations in this font's item variation store.
    """
    store, source_store = font["GDEF"].table.VarStore, source["GDEF"].table.VarStore
    key = lambda region: tuple((a.StartCoord, a.PeakCoord, a.EndCoord) for a in region.VarRegionAxis)  # noqa: E731
    regions = {key(r): i for i, r in enumerate(store.VarRegionList.Region)}
    remap = []
    for region in source_store.VarRegionList.Region:
        if key(region) not in regions:
            regions[key(region)] = len(store.VarRegionList.Region)
            store.VarRegionList.Region.append(deepcopy(region))
        remap.append(regions[key(region)])
    store.VarRegionList.RegionCount = len(store.VarRegionList.Region)
    outer = len(store.VarData)
    for data in source_store.VarData:
        data = deepcopy(data)
        data.VarRegionIndex = [remap[i] for i in data.VarRegionIndex]
        data.VarRegionCount = len(data.VarRegionIndex)
        store.VarData.append(data)
    store.VarDataCount = len(store.VarData)

    gpos = font["GPOS"].table
    first, seen = len(gpos.LookupList.Lookup), set()
    for lookup in source["GPOS"].table.LookupList.Lookup:
        lookup = deepcopy(lookup)
        for st in lookup.SubTable:
            st = st.ExtSubTable if lookup.LookupType == 9 else st
            assert st.LookupType == 2, f"kerning lookup of type {st.LookupType}"
            if st.Format == 1:
                values = [v for ps in st.PairSet for r in ps.PairValueRecord for v in (r.Value1, r.Value2)]
            else:
                values = [v for c1 in st.Class1Record for c2 in c1.Class2Record for v in (c2.Value1, c2.Value2)]
            for value in values:
                for attr in ("XPlaDevice", "YPlaDevice", "XAdvDevice", "YAdvDevice"):
                    device = getattr(value, attr, None) if value is not None else None
                    if device is not None and device.DeltaFormat == 0x8000 and id(device) not in seen:
                        seen.add(id(device))
                        device.StartSize += outer
        gpos.LookupList.Lookup.append(lookup)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    for record in gpos.FeatureList.FeatureRecord:
        if record.FeatureTag == "kern":
            record.Feature.LookupListIndex = [*record.Feature.LookupListIndex, *range(first, gpos.LookupList.LookupCount)]
            record.Feature.LookupCount = len(record.Feature.LookupListIndex)


def derived(font: TTFont, name: str, new: str, transform, advance: float | None = None) -> None:
    """
    A glyph made from another of the font's, its points moved by
    `transform(x, y)` (the same move at every master: its variations are
    kept), its advance `advance` (fixed: its variations dropped) or kept.
    """
    glyf, hmtx, gvar = font["glyf"], font["hmtx"], font["gvar"]
    glyph = deepcopy(glyf[name])
    assert not glyph.isComposite(), f"{name}: a composite"
    glyph.coordinates = GlyphCoordinates([transform(x, y) for x, y in glyph.coordinates])
    font.setGlyphOrder([*font.getGlyphOrder(), new])
    glyf.glyphOrder = font.getGlyphOrder()
    glyf.glyphs[new] = glyph
    glyph.recalcBounds(glyf)
    hmtx.metrics[new] = (round(hmtx.metrics[name][0] if advance is None else advance), glyph.xMin)
    variations = deepcopy(gvar.variations.get(name, []))
    if advance is not None:
        # the phantom points after the outline's: the origin and the advance stay where they are
        n = len(glyph.coordinates)
        for v in variations:
            v.coordinates[n] = v.coordinates[n + 1] = (0, 0)
    gvar.variations[new] = variations


def master_model(font: TTFont) -> VariationModel:
    """The model of the masters glyphs are drawn at (build/variable.py's: Thin, Regular, Black × opsz 14, 32)."""
    space = Space.of(font)
    return VariationModel([space.normalized(loc) for loc in MASTERS], axisOrder=["wght", "opsz"])


def composite(font: TTFont, new: str, parts: list[tuple[str, list[float]]], advance: list[float]) -> None:
    """A glyph of other glyphs (each moved across by an offset by master, MASTERS' order), its advance by master."""
    glyf, hmtx, gvar = font["glyf"], font["hmtx"], font["gvar"]
    default = MASTERS.index((400, TEXT_OPSZ))
    glyph = Glyph()
    glyph.numberOfContours = -1
    glyph.components = []
    for name, dx in parts:
        component = GlyphComponent()
        component.glyphName, component.x, component.y, component.flags = name, round(dx[default]), 0, 0
        glyph.components.append(component)
    font.setGlyphOrder([*font.getGlyphOrder(), new])
    glyf.glyphOrder = font.getGlyphOrder()
    glyf.glyphs[new] = glyph
    glyph.recalcBounds(glyf)
    hmtx.metrics[new] = (round(advance[default]), glyph.xMin)
    # a component's offset varies as a point does, then the phantom points (origin, advance, top, bottom)
    model = master_model(font)
    values = [GlyphCoordinates([(round(dx[i]), 0) for _, dx in parts] + [(0, 0), (round(advance[i]), 0), (0, 0), (0, 0)])
              for i in range(len(MASTERS))]
    deltas = model.getDeltas(values)
    gvar.variations[new] = [TupleVariation(support, [(round(x), round(y)) for x, y in delta])
                            for support, delta in zip(model.supports, deltas) if support and any(x or y for x, y in delta)]


def widened(font: TTFont, name: str, extra: list[float]) -> None:
    """A glyph's advance widened by `extra` (by master, MASTERS' order): its hmtx advance and its gvar's."""
    glyf, hmtx, gvar = font["glyf"], font["hmtx"], font["gvar"]
    model = master_model(font)
    deltas = model.getDeltas(extra)
    width, lsb = hmtx.metrics[name]
    hmtx.metrics[name] = (round(width + deltas[0]), lsb)
    advance = len(glyf[name].getCoordinates(glyf)[0]) + 1
    key = lambda axes: tuple(sorted((t, tuple(round(v, 4) for v in s)) for t, s in axes.items()))  # noqa: E731
    variations = gvar.variations.get(name, [])
    known = {key(v.axes): v for v in variations}
    for support, delta in zip(model.supports[1:], deltas[1:]):
        if not round(delta):
            continue
        v = known.get(key(support))
        if v is None:
            v = TupleVariation(support, [None] * (advance + 3))
            variations.append(v)
        x, y = v.coordinates[advance] or (0, 0)
        v.coordinates[advance] = (x + round(delta), y)
    gvar.variations[name] = variations


def set_cmap(font: TTFont, mapping: dict[int, str]) -> None:
    """A cmap of the mapping: format 4 for the BMP, 12 for every plane (the math alphabets are in plane 1)."""
    table = newTable("cmap")
    table.tableVersion = 0
    table.tables = []
    bmp = {cp: g for cp, g in mapping.items() if cp <= 0xFFFF}
    for platform, encoding, fmt, m in ((0, 3, 4, bmp), (3, 1, 4, bmp), (0, 4, 12, mapping), (3, 10, 12, mapping)):
        sub = CmapSubtable.newSubtable(fmt)
        sub.platformID, sub.platEncID, sub.language = platform, encoding, 0
        sub.cmap = dict(m)
        table.tables.append(sub)
    font["cmap"] = table


def alphabets(upright: dict[int, str], italic: dict[int, str], blackboard: dict[int, str], bold: dict[int, str],
              bold_italic: dict[int, str]) -> dict[int, str]:
    """
    Unicode's math alphabets Inter Math draws: italic (the italic font's),
    bold and bold italic (their letters at the weight's bold), sans serif
    (Inter is one: the upright and italic letters, bold too), double-struck
    (the blackboard letters), and the dotless italic 𝚤 𝚥. Script, Fraktur and
    monospace Inter has no design for.
    """
    out: dict[int, str] = {}

    def put(start: int, chars: list[int], cmap: dict[int, str]) -> None:
        for i, ch in enumerate(chars):
            cp = HOLES.get(start + i, start + i)
            if ch in cmap:
                out[cp] = cmap[ch]

    capitals, small = [ord(c) for c in LATIN], [ord(c) for c in LATIN.lower()]
    greek = [*GREEK_CAPITALS, 0x2207, *GREEK_SMALL, *GREEK_AFTER]
    # italic: Latin, Greek (its capitals that are Latin's are the italic Latin ones; ∂ and ∇ are KaTeX's \partial
    # \nabla, Inter Math's upright ones)
    as_latin = lambda m: {cp: m[ord(c)] for cp, c in zip(GREEK_CAPITALS, GREEK_AS_LATIN) if ord(c) in m}  # noqa: E731
    italic_greek = {**as_latin(italic), **{cp: upright[cp] for cp in (0x2202, 0x2207) if cp in upright}, **italic}
    put(0x1D434, capitals, italic)
    put(0x1D44E, small, italic)
    put(0x1D6E2, greek, italic_greek)
    # sans serif: the upright and italic letters, and the digits
    put(0x1D5A0, capitals, upright)
    put(0x1D5BA, small, upright)
    put(0x1D608, capitals, italic)
    put(0x1D622, small, italic)
    digits = [ord(c) for c in "0123456789"]
    put(0x1D7E2, digits, upright)
    # bold and bold italic, and sans serif bold the same
    bold_greek = {**as_latin(bold), **bold}
    bold_italic_greek = {**as_latin(bold_italic), **{cp: bold[cp] for cp in (0x2202, 0x2207) if cp in bold}, **bold_italic}
    for start, chars, m in ((0x1D400, capitals, bold), (0x1D41A, small, bold), (0x1D468, capitals, bold_italic), (0x1D482, small, bold_italic),
                            (0x1D6A8, greek, bold_greek), (0x1D71C, greek, bold_italic_greek), (0x1D7CE, digits, bold),
                            (0x1D5D4, capitals, bold), (0x1D5EE, small, bold), (0x1D63C, capitals, bold_italic), (0x1D656, small, bold_italic),
                            (0x1D756, greek, bold_greek), (0x1D790, greek, bold_italic_greek), (0x1D7EC, digits, bold)):
        put(start, chars, m)
    # double-struck: the blackboard letters (A-Z, and k for \Bbbk)
    put(0x1D538, capitals, blackboard)
    put(0x1D552, small, blackboard)
    # the dotless italic i and j
    for cp, ch in ((0x1D6A4, 0x131), (0x1D6A5, 0x237)):
        if ch in italic:
            out[cp] = italic[ch]
    return out


def features(font: TTFont, katex: dict[str, dict[str, str]], script: dict[str, str], scriptscript: dict[str, str],
             dotless: dict[str, str], triangles: dict[str, str]) -> None:
    """
    GSUB, written again: KaTeX's roles (KATEX), first, so that what follows
    reaches each role's glyphs; KaTeX's script forms (ss19, ss20) and the
    math script styles' (ssty: the first alternate for scripts, the second for
    second-level scripts), dtls (dotless letters under accents), ss01 (the
    triangle arrowheads), for the math script too.
    """
    if "GSUB" in font:
        del font["GSUB"]
    singles = lambda tag, subs: f"feature {tag} {{ {' '.join(f'sub {b} by {a};' for b, a in sorted(subs.items()))} }} {tag};"  # noqa: E731
    fea = ["languagesystem DFLT dflt;", "languagesystem math dflt;", "languagesystem latn dflt;", "languagesystem grek dflt;"]
    fea += [singles(tag, subs) for tag, subs in katex.items() if subs]
    fea += [singles(SCRIPT, script), singles(SCRIPTSCRIPT, scriptscript)]
    rules = " ".join(f"sub {b} from [{a} {scriptscript.get(b, a)}];" for b, a in sorted(script.items()))
    fea.append(f"feature ssty {{ {rules} }} ssty;")
    fea += [singles("dtls", dotless), singles(TRIANGLES, triangles)]
    addOpenTypeFeaturesFromString(font, "\n".join(fea), tables=["GSUB"])


def merged(italics: dict) -> tuple[TTFont, dict]:
    """
    The fonts of KaTeX's roles in one: the upright font, and what the math
    font takes from the others (renamed), its cmap and features; for KaTeX,
    the italic and AMS fonts whole, its roles' features (KATEX).
    """
    roles = {role: Role(role) for role in ROLES}
    upright, italic, blackboard = roles["Upright"], roles["Italic"], roles["Blackboard"]
    font = upright.font
    # KaTeX's private-use code points are KaTeX's alone (its negations Unicode has no character for are \not and the
    # relation in unicode-math): mapped below, with its roles
    cmap = {cp: g for cp, g in upright.cmap.items() if not 0xE000 <= cp <= 0xF8FF}
    # the Greek capitals Latin has (KaTeX's fonts have only the others): the Latin ones
    for cp, latin in zip(GREEK_CAPITALS, GREEK_AS_LATIN):
        if cp not in cmap and ord(latin) in cmap:
            cmap[cp] = cmap[ord(latin)]
    # ‖ (\Vert, \|): Inter Math's ∥
    cmap.setdefault(0x2016, cmap[0x2225])
    # ¯ (the spacing macron, which MathML's writers use for \bar, some for \overline): KaTeX's \bar, ˉ (stretched as the
    # overline: build/math_glyphs.py)
    cmap.setdefault(0xAF, cmap[0x2C9])

    # the italic letters (and their script forms and components)
    letters = {cp: g for cp, g in italic.cmap.items() if chr(cp) in LATIN + LATIN.lower() or 0x370 <= cp < 0x400 or cp in (0x131, 0x237)}
    wanted = set(letters.values())
    wanted |= {italic.script[g] for g in wanted if g in italic.script} | {italic.scriptscript[g] for g in wanted if g in italic.scriptscript}
    math_italic = italic.closure(wanted)
    # for KaTeX, the italic font whole (its kerning too) and the AMS font's designs
    katex_only = set()
    for role in (italic, roles["AMS"]):
        names = [n for n in role.font.getGlyphOrder() if n != ".notdef"]
        copy_glyphs(font, role.font, names)
        katex_only |= set(names) - set(math_italic)
    merge_kerning(font, italic.font)
    # the blackboard letters
    copy_glyphs(font, blackboard.font, blackboard.closure(set(blackboard.cmap.values())))
    # Inter's upright small Greek, as it is
    space = Space.of(font)
    inter = TTFont(SOURCES / "InterVariable.ttf").getBestCmap()
    greek = {cp: inter[cp] for cp in UPRIGHT_GREEK if cp not in cmap and cp in inter}
    add_glyphs(font, copied_glyphs(space, SOURCES / "InterVariable.ttf", {n: n for n in greek.values()}))
    cmap |= greek
    # bold and bold italic: the letters (Latin, Greek, the dotless ı ȷ), digits and ∂ ∇ at each weight's bold
    upright_bold = [*map(ord, LATIN + LATIN.lower() + "0123456789"), 0x131, 0x237, 0x2202, 0x2207,
                    *(cp for cp in range(0x391, 0x3AA) if cp in upright.cmap)]
    probe = {r: {v: k for k, v in roles[r].names.items()} for r in ("Upright", "Italic")}
    bold = {cp: f"{upright.cmap[cp]}.bf" for cp in upright_bold if cp in upright.cmap}
    bold |= {cp: f"{name}.bf" for cp, name in greek.items()}
    bold_italic = {cp: f"{name}.bf" for cp, name in letters.items()}
    add_glyphs(font, bold_glyphs(space, [
        (upright.path, {probe["Upright"][upright.cmap[cp]]: bold[cp] for cp in upright_bold if cp in upright.cmap}),
        (SOURCES / "InterVariable.ttf", {name: f"{name}.bf" for name in greek.values()}),
        (italic.path, {probe["Italic"][name]: f"{name}.bf" for name in letters.values()}),
    ]))
    cmap |= alphabets(cmap, letters, blackboard.cmap, bold, bold_italic)

    # the four sizes, whole
    sizes = {}
    for n in range(1, 5):
        role = roles[f"Size{n}"]
        copy_glyphs(font, role.font, role.closure(set(role.cmap.values())))
        sizes[n] = role.cmap
    for cp in BIG_OPERATORS:
        cmap[cp] = sizes[1][cp]
    # the integrals' advance counts their italic correction (KaTeX's, by weight: TeX's box is as wide); KaTeX keeps
    # its own (a copy)
    katex_em = font["head"].unitsPerEm
    katex_copies = {}
    for n in (1, 2):
        for cp in INTEGRALS:
            by_weight = italics[f"Size{n}-Regular"][str(cp)]
            katex_copies[sizes[n][cp]] = f"{sizes[n][cp]}.katex"
            duplicate(font, sizes[n][cp], katex_copies[sizes[n][cp]])
            widened(font, sizes[n][cp], [by_weight[str(w)] * katex_em for w, _ in MASTERS])
    # the brace's pieces stand on the baseline (an engine stacks them by their ink, from its bottom: KaTeX's stand on
    # their cuts, a copy)
    for cp in BRACE_PIECES:
        cmap.setdefault(cp, sizes[4][cp])
        piece = sizes[4][cp]
        katex_copies[piece] = f"{piece}.katex"
        duplicate(font, piece, katex_copies[piece])
        _, y0, _, _ = bounds(font, piece, {"wght": 400, "opsz": TEXT_OPSZ})
        glyph = font["glyf"][piece]
        glyph.coordinates = GlyphCoordinates([(x, y - round(y0)) for x, y in glyph.coordinates])
        glyph.recalcBounds(font["glyf"])

    # math accents (combining marks): KaTeX's accents with no advance, their middle on the origin (accents don't widen
    # what they are over: a browser's MathML takes the wider of the two), and \not's slash likewise
    attachments = {}
    for mark, accent in ACCENTS.items():
        if accent in upright.cmap:
            name, half = f"uni{mark:04X}", font["hmtx"].metrics[upright.cmap[accent]][0] / 2
            derived(font, upright.cmap[accent], name, lambda x, y, half=half: (x - half, y), advance=0)
            cmap[mark], attachments[name] = name, 0
    if NOT_SLASH[0] in upright.cmap:
        slash = upright.cmap[NOT_SLASH[0]]
        x0, _, x1, _ = bounds(font, slash, {"wght": 400, "opsz": TEXT_OPSZ})
        name = f"uni{NOT_SLASH[1]:04X}"
        derived(font, slash, name, lambda x, y: (x - (x0 + x1) / 2, y), advance=0)
        cmap[NOT_SLASH[1]], attachments[name] = name, 0

    # the negated relations KaTeX sets as \not over the relation: \not's slash across the relation's middle
    def middles(name: str) -> list[float]:
        return [(lambda b: (b[0] + b[2]) / 2)(bounds(font, name, {"wght": w, "opsz": o})) for w, o in MASTERS]

    for cp, relation in NEGATED.items():
        if relation in cmap and cp not in cmap:
            name = f"uni{cp:04X}"
            composite(font, name, [(cmap[relation], [0.0] * len(MASTERS)), (cmap[NOT_SLASH[1]], middles(cmap[relation]))],
                      [font.getGlyphSet(location={"wght": w, "opsz": o})[cmap[relation]].width for w, o in MASTERS])
            cmap[cp] = name

    # √ at every height KaTeX draws it, and the pieces of taller ones (build/math_glyphs.py)
    radicals, radical_variants, radical_parts = radical_glyphs(space, katex_em)
    add_glyphs(font, radicals)
    cmap[0x221A] = radical_variants[0]
    # the delimiters between KaTeX's sizes, and the pieces of taller ones
    delimiters, delimiter_variants, delimiter_parts = delimiter_glyphs(
        space, katex_em, {r: roles[r].path for r in roles}, {r: roles[r].probe_cmap for r in roles}, {r: roles[r].cmap for r in roles})
    add_glyphs(font, delimiters)
    # what stretches sideways (arrows, braces over and under, wide accents), the vector accents, the arrows upright
    stretchy, horizontal, horizontal_parts, upright_arrows, more, accent_attachments = horizontal_glyphs(
        space, katex_em, roles["Upright"].path, SOURCES / "InterVariable.ttf", cmap,
        {r: roles[r].probe_cmap for r in roles}, {r: roles[r].cmap for r in roles})
    add_glyphs(font, stretchy)
    cmap |= more
    attachments |= accent_attachments

    # the bars as tall as the delimiters' sizes (KaTeX draws them out: src/svg.ts)
    bars = {}
    for cp in (0x7C, 0x2016):
        bar = cmap[cp]
        _, b0, _, b1 = bounds(font, bar, {"wght": 400, "opsz": TEXT_OPSZ})
        middle = (b0 + b1) / 2
        bars[cp] = []
        for i, h in enumerate(DELIMITER_HEIGHTS[1:], 1):
            half = h * katex_em / 2
            y0, y1 = middle - half, middle + half
            name = f"{bar}.v{i}"
            derived(font, bar, name, lambda x, y, y0=y0, y1=y1: (x, y1 + (y - b1) if y > middle else y0 + (y - b0)))
            bars[cp].append(name)

    # KaTeX's roles: the role's glyph wherever the math font maps another, its private-use code points mapped
    katex = {}
    for role, tag in KATEX.items():
        subs = katex[tag] = {}
        for cp, glyph in roles[role].cmap.items():
            glyph = katex_copies.get(glyph, glyph)
            if cp not in cmap:
                assert 0xE000 <= cp <= 0xF8FF, f"{role}: U+{cp:04X} is KaTeX's alone"
                cmap[cp] = glyph
            if cmap[cp] != glyph:
                subs[cmap[cp]] = glyph
        wrong = [f"U+{cp:04X}" for cp, glyph in roles[role].cmap.items()
                 if subs.get(cmap[cp], cmap[cp]) != katex_copies.get(glyph, glyph)]
        assert not wrong, f"{tag}: glyphs the math font shares between code points the role doesn't: {', '.join(wrong)}"
    set_cmap(font, cmap)

    dotless = {upright.cmap[ord("i")]: upright.cmap[0x131], upright.cmap[ord("j")]: upright.cmap[0x237],
               italic.cmap[ord("i")]: italic.cmap[0x131], italic.cmap[ord("j")]: italic.cmap[0x237],
               bold[ord("i")]: bold[0x131], bold[ord("j")]: bold[0x237],
               bold_italic[ord("i")]: bold_italic[0x131], bold_italic[ord("j")]: bold_italic[0x237]}
    script = {b: a for role in roles.values() for b, a in role.script.items()}
    scriptscript = {b: a for role in roles.values() for b, a in role.scriptscript.items()}
    features(font, katex, script, scriptscript, dotless, upright.triangles)
    # the italic font's letters alone are the math font's (its other glyphs KaTeX's)
    return font, {"roles": {**{r: role.cmap for r, role in roles.items()}, "Italic": letters}, "cmap": cmap,
                  "attachments": attachments, "bars": bars, "greek": greek, "bold": bold, "bold italic": bold_italic,
                  "radical": (radical_variants, radical_parts), "delimiters": (delimiter_variants, delimiter_parts),
                  "horizontal": (horizontal, horizontal_parts), "upright arrows": upright_arrows,
                  "katex": katex, "katex only": katex_only | set(katex_copies.values())}


def set_names(font: TTFont, style: str, variable: bool) -> None:
    """The family and style names, for a weight (static) or the variable font."""
    name = font["name"]
    inter = name.getDebugName(0).split(". Inter Math modifications")[0]
    ribbi = style in ("Regular", "Bold")
    family = FAMILY if ribbi or variable else f"{FAMILY} {style}"
    ps_family = FAMILY.replace(" ", "")
    ps = f"{VARIABLE}" if variable else f"{ps_family}-{style}"
    names = {
        0: f"{inter}. Inter Math modifications: Copyright (c) 2026 Luc Potage.",
        1: family,
        2: style if ribbi or variable else "Regular",
        3: f"{FONT_VERSION};{ps}",
        4: FAMILY if variable or style == "Regular" else f"{FAMILY} {style}",
        5: f"Version {FONT_VERSION}; Inter Math {VERSION}",
        6: ps,
        10: "Inter, made a math font: OpenType MATH table, Unicode's math alphabets, script forms.",
        16: FAMILY,
        17: style,
        25: ps_family if variable else None,
    }
    for nid in (*names, 21, 22):
        name.removeNames(nameID=nid)
    for nid, s in names.items():
        if s is not None:
            name.setName(s, nid, 3, 1, 0x409)
            name.setName(s, nid, 1, 0, 0)


def finish(font: TTFont) -> None:
    """Inter's em and vertical metrics, glyph names kept, the deltas optimized, HVAR."""
    font["head"].unitsPerEm = UPEM
    inter = TTFont(SOURCES / "InterVariable.ttf")
    for table in ("hhea", "OS/2"):
        for attr in ("ascent", "descent", "lineGap", "sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent",
                     "usWinDescent", "sxHeight", "sCapHeight", "yStrikeoutPosition", "yStrikeoutSize"):
            if hasattr(inter[table], attr):
                setattr(font[table], attr, getattr(inter[table], attr))
    # names for every glyph: script forms, sizes and pieces read in a PDF (pdfTeX and LuaTeX name what isn't mapped)
    post = font["post"]
    post.formatType = 2.0
    post.extraNames, post.mapping = [], {}
    # the deltas a renderer infers from their neighbours left out (Inter's own glyphs have them so; those drawn for
    # KaTeX don't, nor the math font's own)
    glyf, gvar, hmtx = font["glyf"], font["gvar"], font["hmtx"]
    for name in font.getGlyphOrder():
        variations = gvar.variations.get(name)
        if not variations or all(None in v.coordinates for v in variations):
            continue
        coordinates, controls = glyf._getCoordinatesAndControls(name, hmtx.metrics)
        for v in variations:
            v.optimize(coordinates, controls.endPts, tolerance=0.5)
    if "HVAR" in font:
        del font["HVAR"]
    add_HVAR(font)
    font.recalcTimestamp = False


def named_instances(font: TTFont) -> None:
    """Inter's named instances: the nine weights at the text optical size."""
    fvar, name = font["fvar"], font["name"]
    fvar.instances = []
    for wght, style in STYLES.items():
        inst = NamedInstance()
        inst.subfamilyNameID = name.addMultilingualName({"en": style}, font, minNameID=256)
        inst.postscriptNameID = name.addMultilingualName({"en": f"{FAMILY.replace(' ', '')}-{style}"}, font, minNameID=256)
        inst.coordinates = {"wght": wght, "opsz": TEXT_OPSZ}
        fvar.instances.append(inst)


def bounds(font: TTFont, name: str, location: dict) -> tuple | None:
    gs = font.getGlyphSet(location=location)
    pen = BoundsPen(gs)
    gs[name].draw(pen)
    return pen.bounds


def operator_italics() -> dict:
    """The integrals' italic corrections by Size font and weight (em, KaTeX's: src/metrics.ts, from build.py)."""
    text = (ROOT / "src" / "metrics.ts").read_text()
    body = re.search(r"export const operatorItalics[^=]*= (\{.*\});", text).group(1)
    return json.loads(body)


def build() -> None:
    OPENTYPE.mkdir(parents=True, exist_ok=True)
    italics = operator_italics()
    font, maps = merged(italics)
    katex_em = font["head"].unitsPerEm
    set_names(font, "Regular", variable=True)
    named_instances(font)
    finish(font)
    # the MATH table measures the glyphs at their locations: from the font as saved
    path = OPENTYPE / f"{VARIABLE}.ttf"
    font.save(path)
    font = TTFont(path)
    font.recalcTimestamp = False
    data = add_math(font, maps, katex_em, italics)
    font.save(path)
    font.flavor = "woff2"
    font.save(FONTS / f"{VARIABLE}.woff2")
    print(f"{path.relative_to(ROOT)}: {len(font.getGlyphOrder())} glyphs, {len(font.getBestCmap())} characters")

    # the weights, each with its MATH table at that weight
    for wght, style in STYLES.items():
        source = TTFont(path)
        del source["MATH"]
        static = instancer.instantiateVariableFont(source, {"wght": wght, "opsz": TEXT_OPSZ})
        set_names(static, style, variable=False)
        static["OS/2"].usWeightClass = wght
        static["OS/2"].fsSelection = (static["OS/2"].fsSelection & ~0x61) | (0x20 if style == "Bold" else 0x40 if style == "Regular" else 0) | 0x80
        static["head"].macStyle = 1 if style == "Bold" else 0
        static_math(static, data, {"wght": wght, "opsz": TEXT_OPSZ})
        # Inter's timestamp, as the variable font: the same sources build the same files
        static.recalcTimestamp = False
        out = OPENTYPE / f"{FAMILY.replace(' ', '')}-{style}.ttf"
        static.save(out)
        # and for the web (src/mathml.css): browsers read one MATH table, the one of the weight they pick (none applies
        # a MATH table's variations yet: HarfBuzz does from its version after 14.6.0)
        static.flavor = "woff2"
        static.save(FONTS / f"{FAMILY.replace(' ', '')}-{style}.woff2")
    print(f"{OPENTYPE.relative_to(ROOT)}/InterMath-*.ttf, fonts/InterMath-*.woff2: {', '.join(STYLES.values())}")


if __name__ == "__main__":
    build()
