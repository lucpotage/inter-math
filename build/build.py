#!/usr/bin/env python3
"""
Inter Math: KaTeX's upright and italic fonts redrawn from Inter, still
variable (weight 100-900, optical size 14-32), with the metrics KaTeX lays
them out with.

    pnpm font:build

Reads sources/inter/InterVariable*.ttf and the installed KaTeX (its metric
tables), writes one font per role KaTeX sets math in (build/out/*.ttf),
src/metrics.ts and src/provenance.ts (what each glyph is drawn from), and the
reference of what each glyph is built on (build/parts.md, by build/parts.py);
then build/opentype.py makes the OpenType math font of them, which KaTeX takes
too (fonts/InterMathVariable.woff2: its roles are features of the font's).

What changes from Inter:
- one font per role (upright, italic) holding Inter's glyphs for the
  characters KaTeX sets in that role, plus accented Latin letters for text;
  whatever Inter lacks falls back to KaTeX's own font through the CSS stack;
- scaled through the units per em (outlines and variations untouched) so
  that the centre of Inter's + − = sits on TeX's math axis, 0.25 em (that
  sets the size of Inter Math); math then sets its signs and brackets at the
  height Inter gives its arrows and brackets next to lowercase, between its
  lowercase and its capitals, and TeX's axis follows them (src/index.ts);
- math alternates baked in: a serifed I, and a tailed l in italic
  (variables), so l, I, 1 and | can't be confused;
- operators as heavy as the letters (as Inter's), and larger than Inter's
  text ones (TeX's sizes: build/operators.py);
- KaTeX's Size fonts' delimiters and big operators, from Inter's
  (build/delimiters.py, build/big_operators.py), with ⟮ ⟯ ⎰ ⎱ at every size
  (Inter's braces without their point) and the corners ┌ ┐ └ ┘ (Inter's [);
- new glyphs made of Inter's own outlines, with their variations: the slash
  of \not (KaTeX sets ≠ as \not=) is the one of Inter's ≠; scripts get
  their own digits, signs and letters, after Inter's fraction figures
  (build/script_glyphs.py); geometry and set symbols are drawn from Inter's
  (build/geometry_glyphs.py), the AMS order relations (⩽ ≦ ≲ ≶ ⋚…),
  negated relations (≮ ≰ ⊈ ⊊ ∤…), equalities with marks (≑ ≖ ≜ ≏ ∝ ≍…),
  school shapes (∴ ∵ ∡ ∢, with Inter's own □ ■ ✓), sets, turnstiles and
  joins (∁ ⊏ ⋐ ⋓ ⋔ ⊩ ⊸ ⋈…) and precedence relations (≺ ⪯ ≼ ⋞ ≾ ⪷, a
  curved chevron of ○'s arcs) and binary operators (◃ ⊲ ⊴ ⋉ ⋋ ⊛ ⊞ ⊼ ⋏ ⋇ ∔ ⊺
  ≀ ⋄…) and the AMS arrows (↛ ⇉ ⇛ ↠ ↣ ⇢ ⇝ ↶ ↫ ↾…, Inter's own ↺ ↻ ↰ ↱) from
  Inter Math's own, the shapes, suits and music signs (▲ ◀ ◊ ⧫ ★ ╱ ‵ ✠,
  ♠ ♢ ♣ with Inter's own ♡, ♭ ♮ ♯) from Inter's ▲ ◊ ★ / ♥ ● ◇ # and
  superior b, and letter-like symbols (ϰ ϝ ⅁ ℧ ® Ⓢ, Inter's Ⅎ ð ¥) from
  Inter's letters (build/order_glyphs.py, build/negated_glyphs.py,
  build/equality_glyphs.py, build/shape_glyphs.py, build/set_glyphs.py,
  build/precedence_glyphs.py, build/binary_glyphs.py,
  build/ams_arrow_glyphs.py, build/misc_glyphs.py,
  build/letter_glyphs.py); \\imath \\jmath are Inter's italic ı ȷ at the
  private-use code points KaTeX uses, and the italic ℏ its ħ (ITALIC_ALIASES);
- kerning is the only layout feature kept (no contextual alternates: KaTeX
  sets every atom on its own);
- the AMS font's own designs at code points it shares with Main (\\varnothing
  \\hslash \\centerdot \\smallsetminus \\thicksim \\varpropto \\shortmid
  \\vartriangle \\smallfrown…), and \\Bbbk's blackboard k: a font of their own,
  InterMath-AMS (build/ams_variants.py, build_ams());
- \\mathsf \\textsf (and their bold and italic) set in Inter Math: Inter is a
  sans serif (KaTeX's are Computer Modern Sans); typewriter, Fraktur,
  calligraphic and script stay KaTeX's (Inter has none);
- KaTeX_Main's ascent and descent, so line boxes don't change with the font
  (the stylesheet gives the OpenType font the same).
"""

import json
import math
import re
import subprocess
from dataclasses import replace
from pathlib import Path

from fontTools import subset
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.varLib.hvar import add_HVAR
from arrow_glyphs import DRAWN_FROM as ARROWS_FROM, arrow_glyphs, harpoon
from blackboard import blackboard_glyphs
from symbol_glyphs import ACCENTS_FROM, DRAWN_FROM as SYMBOLS_FROM, ITALIC_FROM, accent_glyphs, symbol_glyphs
from big_operators import DRAWN_FROM as BIG_OPERATORS_FROM, ITALIC, SUMS, big_operator_glyphs
from delimiters import BRACES, CORNERS, CURVED, DRAWN_FROM as DELIMITERS_FROM, NORMAL, SIZES, SLASHES, STRAIGHT, delimiter_glyphs
from geometry_glyphs import ALIASES, DRAWN_FROM as GEOMETRY_FROM, geometry_glyphs
from operators import OPERATORS, barb_reach, column, doubled, gap, operator_glyphs
from equality_glyphs import AMS as EQUALITY_AMS, DRAWN_FROM as EQUALITY_FROM, equality_glyphs
from negated_glyphs import DRAWN_FROM as NEGATED_FROM, negated_glyphs
from order_glyphs import DRAWN_FROM as ORDER_FROM, order_glyphs
from shape_glyphs import DRAWN_FROM as SHAPES_FROM, KEPT as SHAPES_KEPT, shape_glyphs
from set_glyphs import AMS as SETS_AMS, DRAWN_FROM as SETS_FROM, UNSET as SETS_UNSET, set_glyphs
from letter_glyphs import DRAWN_FROM as LETTERS_FROM, KEPT as LETTERS_KEPT, letter_glyphs
from precedence_glyphs import DRAWN_FROM as PRECEDENCE_FROM, MAIN as PRECEDENCE_MAIN, precedence_glyphs
from binary_glyphs import DRAWN_FROM as BINARY_FROM, MAIN as BINARY_MAIN, binary_glyphs
from ams_arrow_glyphs import (
    DRAWN_FROM as AMS_ARROWS_FROM, KEPT as AMS_ARROWS_KEPT, PIECES_FROM as ARROW_PIECES_FROM, TRIANGLE, ams_arrow_glyphs,
    arrow_pieces, clipped, triangle, triangled,
)
from misc_glyphs import AMS as MISC_AMS, DRAWN_FROM as MISC_FROM, misc_glyphs
from ams_variants import DRAWN_FROM as VARIANTS_FROM, SHARED as AMS_SHARED, variant_glyphs
from script_glyphs import script_glyphs
from parts import katex_commands, macros, reference as parts_reference
from variable import Masters, NewGlyph, Shape, add_glyphs, mark_anchor

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources" / "inter"
OUT = ROOT / "build" / "out"
METRICS_TS = ROOT / "src" / "metrics.ts"
PROVENANCE_TS = ROOT / "src" / "provenance.ts"
# what each glyph is built on, and what is built on it (build/parts.py)
PARTS_MD = ROOT / "build" / "parts.md"

FAMILY = "Inter Math"
# Inter Math's version (package.json's): the fonts carry it as M.(100X+Y) for M.X.Y, as Geist's do (1.0.0: 1.000)
VERSION = json.loads((ROOT / "package.json").read_text())["version"]
_major, _minor, _patch = (int(p) for p in VERSION.split("-")[0].split("."))
FONT_VERSION = f"{_major}.{_minor * 100 + _patch:03d}"
# TeX's math axis (sigma22), in em: Inter's lowercase + − = are centred on it at Inter Math's size
AXIS = 0.25
# KaTeX_Main's ascent and descent, in em
ASCENT, DESCENT = 0.903, 0.272

ROLES = {
    "Upright": {
        "source": "InterVariable.ttf",
        "style": "Regular",
        # KaTeX metric table → the weight it is measured at (sans serif: Inter is one, \\mathsf is set in it)
        "tables": {"Main-Regular": 400, "Main-Bold": 700, "SansSerif-Regular": 400, "SansSerif-Bold": 700},
        # cv08: I with serifs (upright too: \mathrm{I} next to l)
        "alternates": ["cv08"],
    },
    "Italic": {
        "source": "InterVariable-Italic.ttf",
        "style": "Italic",
        "tables": {"Main-Italic": 400, "Main-BoldItalic": 700, "Math-Italic": 400, "Math-BoldItalic": 700, "SansSerif-Italic": 400},
        # cv05: l with a tail, cv08: I with serifs
        "alternates": ["cv05", "cv08"],
    },
}

# Math beyond KaTeX's Main tables: ∉ (KaTeX overlays ∈ and /; Inter Math draws it, see src/index.ts),
# and AMS symbols Inter Math draws (KaTeX sets them from its AMS font: the "Inter Math KaTeX AMS" face of
# src/inter-math.css sends these code points to ours, and test/css.test.ts checks it lists them all)
AMS_DRAWN = {0x2204, *ORDER_FROM, *NEGATED_FROM, *EQUALITY_AMS, *SHAPES_FROM, *SHAPES_KEPT, *SETS_AMS, *LETTERS_FROM, *LETTERS_KEPT,
             *(set(PRECEDENCE_FROM) - PRECEDENCE_MAIN), *(set(BINARY_FROM) - BINARY_MAIN), *CORNERS, *AMS_ARROWS_FROM,
             *AMS_ARROWS_KEPT, *MISC_AMS, *AMS_SHARED}
# ⊶ ⊷ (\\origof \\imageof): KaTeX sets them from Main, which lacks them (as its metrics do); ∌ ⟦ ⟧ ⦃ ⦄
# (\\notni \\llbracket \\rrbracket \\lBrace \\rBrace), which KaTeX builds from two glyphs and Inter Math draws (src/index.ts
# sets them through its macros)
MATH_EXTRA = {0x2209, 0x220C, 0x27E6, 0x27E7, 0x2983, 0x2984, *AMS_DRAWN, *SETS_UNSET}
# \imath \jmath: KaTeX's math italic font has its dotless i and j at private-use code points (Inter's hold its own
# alternates there): Inter's italic ı ȷ; ℏ (\mathit{\hbar}, \textit): Inter's italic ħ, as Inter Math's upright ℏ is
# (build/symbol_glyphs.py; Inter has no ℏ)
ITALIC_ALIASES = {0xE131: "dotlessi", 0xE237: "uni0237", 0x210F: "hbar"}
# Letters drawn for scripts (build/script_glyphs.py): Latin, Greek and its variants; ! ? as the letters (n!,
# \stackrel{!}{=}: Inter has no fraction forms of them, and scaled down they were lighter than the script beside them)
SCRIPT_LETTERS = [
    *range(0x41, 0x5B), *range(0x61, 0x7B), *range(0x391, 0x3AA), *range(0x3B1, 0x3CA),
    0x3D1, 0x3D5, 0x3D6, 0x3F1, 0x3F5, 0x21, 0x3F,
]
# Text beyond KaTeX's tables: accented Latin letters (\text{Médiatrice}), quotes, dashes
TEXT_EXTRA = {*range(0x00C0, 0x0180), 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x00AB, 0x00BB}
# KaTeX picks its normal surd by this glyph's size; ours (src/surd.ts) are as tall as its
SIZED_LIKE_KATEX = {0x221A}
# Inter has these, but KaTeX expects a different design, or they would not match their siblings: kept from KaTeX's font
KEEP_KATEX = {
    *range(0x0300, 0x0370),  # combining marks
}


def katex_dir() -> Path:
    out = subprocess.run(
        ["node", "-p", "require.resolve('katex/package.json')"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return Path(out.stdout.strip()).parent


def katex_metrics(katex: Path) -> dict:
    """KaTeX's metric tables (src/fontMetricsData.js: a JS object literal)."""
    js = (katex / "src" / "fontMetricsData.js").read_text()
    body = js[js.index("{") : js.rindex("}") + 1]
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", body))


def default_location(font: TTFont) -> dict:
    return {a.axisTag: a.defaultValue for a in font["fvar"].axes}


def feature_singles(font: TTFont, tags: list[str]) -> dict:
    """The single substitutions of some GSUB features (glyph → alternate)."""
    gsub = font["GSUB"].table
    lookups = sorted(
        {i for fr in gsub.FeatureList.FeatureRecord if fr.FeatureTag in tags for i in fr.Feature.LookupListIndex}
    )
    mapping = {}
    for i in lookups:
        lookup = gsub.LookupList.Lookup[i]
        for st in lookup.SubTable:
            if lookup.LookupType == 7:
                st = st.ExtSubTable
            if getattr(st, "mapping", None):
                mapping.update(st.mapping)
    return mapping


def bake_alternates(font: TTFont, tags: list[str]) -> None:
    mapping = feature_singles(font, tags)
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap = {cp: mapping.get(g, g) for cp, g in table.cmap.items()}


# the stylistic set of the triangle arrowheads (src/inter-math.css turns it on: setMathFont's arrowHeads)
TRIANGLE_FEATURE = "ss01"


def add_script_glyphs(font: TTFont, glyphs: list[NewGlyph], features: dict[str, list[tuple[str, str]]]) -> None:
    """
    Glyphs reached through stylistic sets: the script glyphs (the CSS turns
    them on in KaTeX's smaller sizes), the triangle arrowheads.
    """
    add_glyphs(font, glyphs)
    fea = ["languagesystem DFLT dflt;", "languagesystem latn dflt;", "languagesystem grek dflt;"]
    for tag, subs in features.items():
        rules = " ".join(f"sub {base} by {name};" for base, name in subs)
        fea.append(f"feature {tag} {{ {rules} }} {tag};")
    addOpenTypeFeaturesFromString(font, "\n".join(fea), tables=["GSUB"])


def bounds(font: TTFont, cp: int, location: dict) -> tuple:
    gs = font.getGlyphSet(location=location)
    pen = BoundsPen(gs)
    gs[font.getBestCmap()[cp]].draw(pen)
    return pen.bounds


def axis_upem(font: TTFont) -> int:
    """The units per em that put the centre of the minus sign on the math axis."""
    _, y0, _, y1 = bounds(font, 0x2212, default_location(font))
    return round((y0 + y1) / 2 / AXIS)


def set_names(font: TTFont, style: str, inter_version: str, family: str = FAMILY) -> None:
    name = font["name"]
    italic = style == "Italic"
    base = family.replace(" ", "")
    ps = f"{base}-{style}"
    names = {
        0: f"{name.getDebugName(0)}. Inter Math modifications: Copyright (c) 2026 Luc Potage.",
        1: family,
        2: style,
        3: f"{FONT_VERSION};{ps}",
        4: f"{family} Italic" if italic else family,
        5: f"Version {FONT_VERSION}; Inter Math {VERSION}, from Inter {inter_version}",
        6: ps,
        10: "Inter, subset and adapted for KaTeX's math layout.",
        25: f"{base}Italic" if italic else base,
    }
    for nid in (*names, 16, 17, 21, 22):
        name.removeNames(nameID=nid)
    for nid, s in names.items():
        name.setName(s, nid, 3, 1, 0x409)
        name.setName(s, nid, 1, 0, 0)


class Sampler(BasePen):
    """Points along an outline (curves sampled), for ink extents."""

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
            self.points.append(
                tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))
            )

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        for i in range(1, 9):
            t = i / 8
            u = 1 - t
            self.points.append(tuple(u * u * a + 2 * u * t * b + t * t * c for a, b, c in zip(p0, p1, p2)))


def measure(font: TTFont, cps: list[int], location: dict, italic: bool, skews: dict[int, float] | None = None) -> dict:
    """
    KaTeX metrics, [depth, height, italic correction, skew, width] in em, per
    code point. `skews`: a letter's skew where Inter puts marks over it (font
    units, accent_skews()).
    """
    upem = font["head"].unitsPerEm
    gs = font.getGlyphSet(location=location)
    cmap = font.getBestCmap()
    em = lambda v: round(v / upem, 5) + 0.0  # noqa: E731 (+ 0.0: no -0.0)
    table = {}
    for cp in cps:
        glyph = gs[cmap[cp]]
        pen = Sampler(gs)
        glyph.draw(pen)
        adv = glyph.width
        if not pen.points:
            table[cp] = [0, 0, 0, 0, em(adv)]
            continue
        xs = [x for x, _ in pen.points]
        ys = [y for _, y in pen.points]
        y_min, y_max = min(ys), max(ys)
        # italic correction: how far the ink sticks out past the advance
        ic = max(0, max(xs) - adv)
        skew = 0
        if skews and cp in skews:
            # accents go where Inter puts its marks over the letter (KaTeX centres one on the letter, then shifts it
            # by the skew): measured from the ink, the dots of \ddot{a} sat left of ä's
            skew = skews[cp]
        elif italic:
            # a letter Inter puts no marks over: the centre of its top quarter
            floor = y_max - 0.25 * (y_max - max(y_min, 0))
            top = [x for x, y in pen.points if y >= floor]
            skew = (min(top) + max(top)) / 2 - adv / 2
        table[cp] = [em(max(0, -y_min)), em(max(0, y_max)), em(ic), em(skew), em(adv)]
    return table


# the mark whose place stands for every accent over a letter (Inter's ä), and the accent KaTeX sets for it (\ddot)
TOP_MARK = 0x0308


def accent_skews(source: Path, cps: list[int]) -> dict[int, dict[int, float]]:
    """
    Each letter's skew by weight (font units): how far from the letter's
    middle KaTeX must centre an accent's advance for the accent to land
    where Inter puts its mark over the letter at that weight. The accents
    are Inter Math's (build/symbol_glyphs.py's accent_glyphs: the upright
    font's over upright letters, the italic font's over italic ones): ¨'s
    dots in the middle of an advance as wide at every weight, every other
    mark as far off them as Inter puts it, so the skew is where Inter puts
    the dots of its ¨ (italic marks lean right of their anchors; an upright
    letter's anchor is off its middle when its ink is: Γ b d). Letters Inter
    puts no marks over are left out. KaTeX holds one skew a letter at every size, and
    Inter's display size spaces its letters and marks otherwise: the skew is
    the mean of the text and display sizes' (exact halfway along the axis,
    up to 0.014 em off at either end).
    """
    inter = TTFont(source)
    cmap = inter.getBestCmap()
    mark = cmap[TOP_MARK]
    regular = {"wght": 400, "opsz": 14}

    def ink(gs, name: str) -> float:
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        return (pen.bounds[0] + pen.bounds[2]) / 2

    letters = [cp for cp in cps if cp in cmap and mark_anchor(inter, cmap[cp], mark, regular) is not None]
    out: dict[int, dict[int, float]] = {cp: {} for cp in letters}
    # KaTeX centres the accent over the letter's box with its italic correction, Regular's (measure())
    glyphs400 = inter.getGlyphSet(location=regular)

    def italic_correction(cp: int) -> float:
        pen = BoundsPen(glyphs400)
        glyphs400[cmap[cp]].draw(pen)
        return max(0.0, pen.bounds[2] - glyphs400[cmap[cp]].width) if pen.bounds else 0.0

    corrections = {cp: italic_correction(cp) for cp in letters}
    sizes = [o for o in (14, 32)]
    for w in WEIGHTS:
        for cp in letters:
            out[cp][w] = 0.0
        for opsz in sizes:
            location = {"wght": w, "opsz": opsz}
            glyphs = inter.getGlyphSet(location=location)
            dots_middle = ink(glyphs, mark)
            for cp in letters:
                base = mark_anchor(inter, cmap[cp], mark, location)
                own = mark_anchor(inter, cmap[cp], mark, location, own=True)
                dots = base[0] - own[0] + dots_middle
                # KaTeX centres the accent's advance on the letter's box (its advance and italic correction) moved by the skew
                skew = dots - (glyphs[cmap[cp]].width + corrections[cp]) / 2
                out[cp][w] += skew / len(sizes)
    return out


def subset_to(font: TTFont, cps: list[int], features: list[str]) -> None:
    options = subset.Options()
    options.layout_features = features
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    options.hinting = False
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=cps)
    subsetter.subset(font)


def finish(font: TTFont, upem: int, file: str, style: str, inter_version: str, family: str = FAMILY) -> TTFont:
    """Scale, vertical metrics, names; saved as .ttf (what build/opentype.py merges), and read back."""
    # scale: everything is in font units, so a new units per em scales it all
    font["head"].unitsPerEm = upem
    asc, desc = round(ASCENT * upem), round(DESCENT * upem)
    hhea, os2 = font["hhea"], font["OS/2"]
    hhea.ascent, hhea.descent, hhea.lineGap = asc, -desc, 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = asc, -desc, 0
    os2.usWinAscent, os2.usWinDescent = asc, desc
    # MVAR would vary those metrics again across the axes
    if "MVAR" in font:
        del font["MVAR"]
    add_HVAR(font)
    # named instances carry Inter's names; a web font doesn't need them
    font["fvar"].instances = []
    font["head"].fontRevision = float(FONT_VERSION)
    # Inter's own timestamp, not the build's: the same sources build the same files (pnpm release checks it)
    font.recalcTimestamp = False
    set_names(font, style, inter_version, family)

    OUT.mkdir(parents=True, exist_ok=True)
    font.save(OUT / f"{file}.ttf")
    return TTFont(OUT / f"{file}.ttf")


def build_size(size: int, glyphs: list[NewGlyph], upem: int, katex_tables: dict) -> dict:
    """The font of one of KaTeX's sizes (build/delimiters.py, build/big_operators.py), standing for KaTeX_Size{size}."""
    font = TTFont(SOURCES / ROLES["Upright"]["source"])
    inter_version = f"{font['head'].fontRevision:.3f}"
    add_glyphs(font, glyphs)
    del font["HVAR"]
    cps = sorted(g.unicode for g in glyphs)
    subset_to(font, cps, [])
    font = finish(font, upem, f"InterMath-Size{size}", "Regular", inter_version, f"{FAMILY} Size{size}")
    table = f"Size{size}-Regular"
    location = {"wght": 400, "opsz": default_location(font)["opsz"]}
    print(f"InterMath-Size{size}: {len(cps)} characters")
    metrics = measure(font, cps, location, italic=False)
    for cp, italic in ITALIC.get(size, {}).items():
        metrics[cp][2] = italic[400]
    return {table: metrics}


def build_blackboard(upem: int) -> dict:
    """Blackboard bold (build/blackboard.py), standing for KaTeX_AMS's A-Z (\\mathbb)."""
    font = TTFont(SOURCES / ROLES["Upright"]["source"])
    inter_version = f"{font['head'].fontRevision:.3f}"
    glyphs = blackboard_glyphs(SOURCES / ROLES["Upright"]["source"])
    add_glyphs(font, glyphs)
    del font["HVAR"]
    cps = sorted(g.unicode for g in glyphs)
    subset_to(font, cps, [])
    font = finish(font, upem, "InterMath-Blackboard", "Regular", inter_version, f"{FAMILY} Blackboard")
    print(f"InterMath-Blackboard: {len(cps)} characters")
    location = {"wght": 400, "opsz": default_location(font)["opsz"]}
    return {"AMS-Regular": measure(font, cps, location, italic=False)}


def build_ams(upem: int) -> dict:
    """
    The AMS font's own designs at the code points it shares with Main (\\varnothing \\hslash…, build/ams_variants.py)
    and \\Bbbk's blackboard k (build/blackboard.py): a font of their own, KaTeX's AMS role in the OpenType font (KTXA).
    """
    font = TTFont(SOURCES / ROLES["Upright"]["source"])
    inter_version = f"{font['head'].fontRevision:.3f}"
    upright, italic = SOURCES / ROLES["Upright"]["source"], SOURCES / ROLES["Italic"]["source"]
    glyphs = variant_glyphs(upright, italic, upem) + [replace(g, name="k.ams") for g in blackboard_glyphs(upright, ["k"])]
    add_glyphs(font, glyphs)
    del font["HVAR"]
    cps = sorted(g.unicode for g in glyphs)
    subset_to(font, cps, [])
    font = finish(font, upem, "InterMath-AMS", "Regular", inter_version, f"{FAMILY} AMS")
    print(f"InterMath-AMS: {len(cps)} characters")
    location = {"wght": 400, "opsz": default_location(font)["opsz"]}
    return {"AMS-Regular": measure(font, cps, location, italic=False)}


def build_role(role: str, spec: dict, katex_tables: dict, upem: int, delimiters: list[NewGlyph]) -> dict:
    font = TTFont(SOURCES / spec["source"])
    inter_version = f"{font['head'].fontRevision:.3f}"
    bake_alternates(font, spec["alternates"])
    # Inter's private-use glyphs mean something else than KaTeX's (U+E020 is \\not for KaTeX, U+E006-E01B its
    # negated AMS relations Unicode has no character for): those Inter Math draws take their code points
    private = {cp for cp in font.getBestCmap() if 0xE000 <= cp <= 0xF8FF}
    if role == "Upright":
        private -= {0xE020, *AMS_DRAWN}
        source = SOURCES / spec["source"]
        italic = SOURCES / ROLES["Italic"]["source"]
        drawn = (operator_glyphs(source) + geometry_glyphs(source, upem) + arrow_glyphs(source) + symbol_glyphs(source, italic, upem)
                 + accent_glyphs(source)
                 + order_glyphs(source) + negated_glyphs(source, upem) + equality_glyphs(source, upem) + shape_glyphs(source)
                 + set_glyphs(source) + letter_glyphs(source, italic) + precedence_glyphs(source)
                 + binary_glyphs(source) + ams_arrow_glyphs(source) + misc_glyphs(source)
                 + delimiters)
        assert not {g.name for g in drawn} & set(font.getGlyphOrder()), "a drawn glyph's name is taken"
        add_glyphs(font, drawn)
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap.update({cp: name for cp, name in ALIASES.items()})
    if role == "Italic":
        private -= set(ITALIC_ALIASES)
        # the accents over italic letters (build/patch_katex.py takes them from this font): Inter's italic marks
        drawn = accent_glyphs(SOURCES / spec["source"])
        assert not {g.name for g in drawn} & set(font.getGlyphOrder()), "a drawn glyph's name is taken"
        add_glyphs(font, drawn)
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap.update(ITALIC_ALIASES)
    # rebuilt from the glyphs' phantom points once they are final
    del font["HVAR"]

    inter_cmap = font.getBestCmap()
    wanted = TEXT_EXTRA | MATH_EXTRA
    for table in spec["tables"]:
        wanted |= {int(cp) for cp in katex_tables[table]}
    cps = sorted(cp for cp in wanted - KEEP_KATEX - private if cp in inter_cmap)

    subset_to(font, cps, ["kern"])
    cmap = font.getBestCmap()
    letters = list(dict.fromkeys(cmap[cp] for cp in SCRIPT_LETTERS if cp in cmap))
    # the script signs stand for the glyphs the font maps their characters to (Inter Math's operators, brackets)
    signs = [(0x2B, "plus"), (0x2212, "minus"), (0x3D, "equal"), (0x28, "parenleft"), (0x29, "parenright"), (0x2C, "comma"), (0x2E, "period")]
    bases = {name: cmap[cp] for cp, name in signs if cp in cmap}
    glyphs, features = script_glyphs(SOURCES / spec["source"], letters, figures=role == "Upright", bases=bases)
    if role == "Upright":
        # the small-headed arrows' triangle heads, Inter's own small arrows' (ss01: setMathFont's arrowHeads)
        triangles = ams_arrow_glyphs(SOURCES / spec["source"], triangles=True)
        glyphs = [*glyphs, *triangles]
        features[TRIANGLE_FEATURE] = [(cmap[int(g.name[3:7], 16)], g.name) for g in triangles]
    add_script_glyphs(font, glyphs, features)

    font = finish(font, upem, f"InterMath-{role}", spec["style"], inter_version)
    if 0x2212 in font.getBestCmap():
        # one axis for all the operators
        _, m0, _, m1 = bounds(font, 0x2212, default_location(font))
        for ch in "+=":
            _, y0, _, y1 = bounds(font, ord(ch), default_location(font))
            centre = (y0 + y1) / 2 / upem
            assert abs(centre - (m0 + m1) / 2 / upem) < 0.005, f"{ch} is centred at {centre:.3f} em, off the minus sign's centre"
    opsz = default_location(font).get("opsz")
    metrics = {}
    # where accents go over the letters, by weight (KaTeX is given the weight's by setMathFont)
    skews = accent_skews(SOURCES / spec["source"], cps)
    for table, weight in spec["tables"].items():
        location = {"wght": weight, **({"opsz": opsz} if opsz else {})}
        # sans serif: the characters KaTeX's table has (\\mathsf sets letters, digits and punctuation)
        own = [cp for cp in cps if str(cp) in katex_tables[table]] if table.startswith("SansSerif") else cps
        at_weight = {cp: s[weight] for cp, s in skews.items() if weight in s}
        metrics[table] = measure(font, own, location, italic=spec["style"] == "Italic", skews=at_weight)
        for cp in SIZED_LIKE_KATEX & set(metrics[table]) & {int(c) for c in katex_tables[table]}:
            metrics[table][cp] = katex_tables[table][str(cp)]
        missing = sorted(int(cp) for cp in katex_tables[table] if int(cp) not in metrics[table])
        print(f"  {table}: {len(metrics[table])} glyphs from Inter, {len(missing)} from KaTeX's font")
    if "Main-Regular" in metrics:
        metrics["AMS-Regular"] = {cp: metrics["Main-Regular"][cp] for cp in sorted(AMS_DRAWN) if cp in metrics["Main-Regular"]}
    print(f"InterMath-{role}: {len(cps)} characters")
    return {"metrics": metrics, "version": inter_version, "skews": {role: skews}}


WEIGHTS = range(100, 1000, 100)


def outline(font: TTFont, cp: int, location: dict) -> list[list[tuple]]:
    """A glyph's contours as polygons (em), for glyphs drawn with straight lines only."""
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    upem = font["head"].unitsPerEm
    gs = font.getGlyphSet(location=location)
    pen = DecomposingRecordingPen(gs)
    gs[font.getBestCmap()[cp]].draw(pen)
    contours, current = [], []
    for op, args in pen.value:
        if op == "moveTo":
            current = [args[0]]
        elif op == "lineTo":
            current.append(args[0])
        elif op in ("closePath", "endPath"):
            contours.append([(round(x / upem, 5), round(y / upem, 5)) for x, y in current])
        else:
            raise ValueError(f"U+{cp:04X} has curves ({op})")
    return contours


def radical(font: TTFont, location: dict) -> dict:
    """
    Inter's √ (y up, from the baseline): an entry bar, a down-stroke, and an
    up-stroke rebuilt at any height from its bottom, its join inside the
    down-stroke and its top (width and lean).
    """
    contours = outline(font, 0x221A, location)
    height = lambda c: max(y for _, y in c) - min(y for _, y in c)  # noqa: E731
    top = max(y for c in contours for _, y in c)
    up = next(c for c in contours if any(y == top for _, y in c))
    bar = min((c for c in contours if c is not up), key=height)
    down = next(c for c in contours if c is not up and c is not bar)
    tops = sorted(p for p in up if p[1] == top)
    bottoms = sorted(p for p in up if p[1] == 0)
    rest = [p for p in up if p not in tops and p not in bottoms]
    assert len(tops) == 2 and len(bottoms) == 2 and len(rest) == 1, f"unexpected √ up-stroke {up}"
    return {
        "bar": bar,
        "down": down,
        "join": rest[0],
        "bottomInner": bottoms[0],
        "bottomRight": bottoms[1],
        "topLeft": tops[0],
        "topRight": tops[1],
    }


def underline(inter: TTFont, location: dict, upem: int) -> list:
    """
    Inter's underline: the line under its ḇ (U+1E07, a b with a line below),
    how far under the baseline its top is and how thick, in Inter Math's em.
    """
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    gs = inter.getGlyphSet(location=location)
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
    return [round(-max(ys) / upem, 5), round((max(ys) - min(ys)) / upem, 5)]


# the letters Inter cancels with a stroke across (Ɇ ȼ; Ⱥ's stroke thins past Regular), for \cancel
CANCELLED = (0x0246, 0x023C)


def strike(inter: TTFont, upem: int) -> float:
    """
    Inter's strike-through: how far over the baseline its top is, in Inter
    Math's em (OS/2; MVAR's 'stro' doesn't move it). It is as thick as Inter's
    underline (MVAR's 'strs' is its 'unds').
    """
    return round(inter["OS/2"].yStrikeoutPosition / upem, 5)


def cancel_stroke(inter: TTFont, location: dict, upem: int) -> float:
    """
    How thick across Inter's strokes that cancel a letter are at a location
    (CANCELLED, their mean), in Inter Math's em: four-point contours cut level,
    which grow to Regular and hold past it (a letter stays readable under them).
    """
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    gs = inter.getGlyphSet(location=location)
    across = []
    for cp in CANCELLED:
        pen = DecomposingRecordingPen(gs)
        gs[inter.getBestCmap()[cp]].draw(pen)
        # its straight contours (the stroke is one, four points cut level)
        contours, current, straight = [], [], True
        for op, args in pen.value:
            if op == "moveTo":
                current, straight = [args[0]], True
            elif op in ("closePath", "endPath"):
                if straight:
                    contours.append(current)
            elif op == "lineTo":
                current.extend(args)
            else:
                straight = False
        stroke = max((c for c in contours if len(c) == 4), key=lambda c: max(y for _, y in c) - min(y for _, y in c))
        low = sorted(stroke, key=lambda p: (p[1], p[0]))[:2]
        high = sorted(stroke, key=lambda p: (-p[1], p[0]))[:2]
        run = abs(low[1][0] - low[0][0])
        slant = math.atan2(high[0][1] - low[0][1], high[0][0] - low[0][0])
        across.append(run * abs(math.sin(slant)))
    return round(sum(across) / len(across) / upem, 5)


def strokes(font: TTFont) -> dict:
    """What TeX's rules, surds and underlines are drawn from, by weight (optical size 14)."""
    inter = TTFont(SOURCES / ROLES["Upright"]["source"])
    upem = font["head"].unitsPerEm
    rules, radicals, underlines, cancels, logo = {}, {}, {}, {}, {}
    # \\TeX's E (Inter's, as Inter Math's is): the bottom of its middle bar, where T and X stand (src/index.ts)
    e = Masters(SOURCES / ROLES["Upright"]["source"], ["E"])
    for w in WEIGHTS:
        location = {"wght": w, "opsz": 14}
        _, y0, _, y1 = bounds(font, 0x2212, location)
        rules[w] = round((y1 - y0) / upem, 5)
        radicals[w] = radical(font, location)
        # Inter Math has no ḇ: Inter's, whose outlines its are (only its units per em differ)
        underlines[w] = underline(inter, location, upem)
        cancels[w] = cancel_stroke(inter, location, upem)
        s = e.shape("E", location)
        ex0, _, ex1, _ = s.bounds()
        logo[w] = round(column(s, ex0 + 0.45 * (ex1 - ex0))[2] / upem, 5)
    _, _, _, x_top = bounds(font, ord("x"), {"wght": 400, "opsz": 14})
    _, m0, _, m1 = bounds(font, 0x2212, {"wght": 400, "opsz": 14})
    return {"rules": rules, "radicals": radicals, "underlines": underlines, "cancels": cancels, "strike": strike(inter, upem), "logo": logo,
            "xHeight": round(x_top / upem, 5), "axis": round((m0 + m1) / 2 / upem, 5)}


# Inter Math's long arrows (Inter's calt draws --> as ⟶: the same outline as →,
# a longer shaft) for KaTeX's stretchy arrows, so that \xrightarrow is ⟶; for
# \vec and the over and under arrows, Inter's → with a small head (vec_arrow(),
# keyed by Inter's accent arrow, U+0362); and its circumflex, the lowest accent
# over lowercase.
ARROWS = {"right": 0x27F6, "left": 0x27F5, "doubleRight": 0x27F9, "doubleLeft": 0x27F8,
          # the stretched harpoons: Inter Math's (Inter's → keeping one barb; ⟶ is → with a longer shaft), drawn out
          "harpoonUpRight": 0x21C0, "harpoonDownRight": 0x21C1, "harpoonUpLeft": 0x21BC, "harpoonDownLeft": 0x21BD,
          "harpoonsRightLeft": 0x21CC, "harpoonsLeftRight": 0x21CB,
          # KaTeX's other arrows on the line (\\xhookrightarrow…, \\xlongequal): Inter Math's ↪ ↩ ↦ ⇄ ↠ ↞ =, drawn out
          # across their shaft's straight run (src/svg.ts)
          "hookRight": 0x21AA, "hookLeft": 0x21A9, "mapsTo": 0x21A6, "toFrom": 0x21C4, "twoHeadRight": 0x21A0,
          "twoHeadLeft": 0x219E, "equals": 0x3D}
# of those, the small-headed ones, with triangle heads too (their ss01 alternates: setMathFont's arrowHeads)
TRIANGLE_ARROWS = ["toFrom", "twoHeadRight", "twoHeadLeft"]
ACCENTS = {"vec": 0x0362}
ACCENT = 0x0302
# the vector arrows: their head against the arrows' at Regular, the same at every weight (Inter's accent arrow's
# is 0.43 of it, and 0.6 still too short); their stroke, barbs and shaft alike, the arrows' (Inter's → drawn
# that small is too light, and the accent's 0.55 of it too); how long over a letter against Inter's n (they
# widen with the letters, not their head)
VEC_HEAD = 0.75
# the arrows' head the vector arrows are sized against: 0.8 of Inter's (the arrows' until review 1)
VEC_ARROW = 0.8
VEC_SPAN = 1.15
# past Regular, their strokes are the arrows' at a lighter weight, gaining at this pace against the letters' (a
# head that small holds no more: its barbs would close it)
VEC_PACE = 0.5
# the heaviest weight a vector arrow is drawn from (past Black, drawn on: Inter's → keeps its shape up to there)
VEC_HEAVIEST = 1300
# the vector double arrow's room: its barbs' inner ends this far out from the axis against its shafts' outer edges
# (where they aren't, its stroke is lighter)
VEC_ROOM = 1.15


def tail_of(shape: Shape) -> list[int]:
    """A right-pointing arrow's flat tail: its points at its left end (two, four for two shafts)."""
    x_lo = shape.bounds()[0]
    tail = [i for i, (x, _) in enumerate(shape.points) if abs(x - x_lo) < 0.5]
    assert len(tail) in (2, 4), tail
    return tail


def barb(shape: Shape) -> float:
    """A right-pointing arrow's barbs' thickness: from its lower barb's inner end to the line of its outer edge."""
    tip = max(shape.points, key=lambda p: p[0])
    (ox, oy), (ix, iy) = sorted(shape.points, key=lambda p: p[1])[:2]
    dx, dy = tip[0] - ox, tip[1] - oy
    return abs((ix - ox) * dy - (iy - oy) * dx) / math.hypot(dx, dy)


def barbs(shape: Shape) -> list[tuple[bool, int, int, list[int]]]:
    """
    A right-pointing arrow's barbs (one contour, Inter's →, ⟹): above the
    axis or not, the indices of its outer end and inner end, and of the rest
    of its side but the tail (its junction with the shaft, or the shafts).
    """
    pts = shape.points
    tail = tail_of(shape)
    tip = max(range(len(pts)), key=lambda i: pts[i][0])
    out = []
    for up in (True, False):
        mine = [i for i, (_, y) in enumerate(pts) if i not in tail and i != tip and (y > pts[tip][1]) == up]
        far, near = sorted(mine, key=lambda i: -abs(pts[i][1] - pts[tip][1]))[:2]
        out.append((up, far, near, [i for i in mine if i not in (far, near)]))
    return out


def barbs_thickened(shape: Shape, by: float) -> Shape:
    """
    A right-pointing arrow with its barbs `by` thicker, inward: its tip, outer
    edges and the barbs' outer ends kept (the head as long and as tall), the
    inner ends sliding along the barbs' cut ends, and each junction (the
    shaft's edge vanishing into a barb's inner edge) along the shaft's edge,
    with the inner edge.
    """
    pts = list(shape.points)
    tip = max(pts, key=lambda p: p[0])
    for up, far, near, rest in barbs(shape):
        ux, uy = tip[0] - pts[far][0], tip[1] - pts[far][1]
        n = math.hypot(ux, uy)
        # across the barb, inwards
        nx, ny = (uy / n, -ux / n) if up else (-uy / n, ux / n)
        pts[near] = (pts[near][0] + by * nx, pts[near][1] + by * ny)
        for i in rest:
            pts[i] = (pts[i][0] - by / abs(nx), pts[i][1])
    return Shape(pts, shape.on, shape.ends, shape.advance)


def shaft_to(shape: Shape, half: float) -> Shape:
    """
    A right-pointing arrow (one shaft) with its shaft's edges `half` from the
    axis, each junction sliding along its barb with its edge (as doubled() in
    build/operators.py moves them); the tip and the barbs' ends kept.
    """
    pts = list(shape.points)
    tip = max(pts, key=lambda p: p[0])
    tail = tail_of(shape)
    d = half - (max(pts[i][1] for i in tail) - min(pts[i][1] for i in tail)) / 2
    for up, far, _, rest in barbs(shape):
        slope = abs(pts[far][0] - tip[0]) / abs(pts[far][1] - tip[1])
        dy = d if up else -d
        for i in rest:
            pts[i] = (pts[i][0] - d * slope, pts[i][1] + dy)
        for i in tail:
            if (pts[i][1] > tip[1]) == up:
                pts[i] = (pts[i][0], pts[i][1] + dy)
    return Shape(pts, shape.on, shape.ends, shape.advance)


def tall(shape: Shape) -> float:
    return shape.bounds()[3] - shape.bounds()[1]


def thick(shape: Shape) -> float:
    """A right-pointing arrow's shaft (or shafts and the gap): the height of its flat tail."""
    ys = [shape.points[i][1] for i in tail_of(shape)]
    return max(ys) - min(ys)


def vec_stroke(m: Masters, location: dict) -> float:
    """The vector arrows' stroke: the arrows' barbs (as thick as their shaft), past Regular as at a lighter weight (VEC_PACE)."""
    w = location["wght"]
    return barb(m.shape("arrowright", {**location, "wght": w if w <= 400 else 400 + (w - 400) * VEC_PACE}))


def vec_head(m: Masters, location: dict, stroke: float) -> Shape:
    """
    The vector arrows' head, on Inter's → (its head as the arrows', with
    their junction): VEC_HEAD as tall as the arrows' at Regular (the same at
    every weight), its barbs `stroke` thick: drawn at the weight that gives it
    them, up to VEC_HEAVIEST, and scaled, its barbs thickened inward the rest
    of the way (its shaft as drawn).
    """
    head = VEC_HEAD * VEC_ARROW * tall(m.shape("arrowright", {**location, "wght": 400}))
    s = m.shape("arrowright", location)
    for _ in range(3):  # how much it is scaled depends on its weight's head, and the weight on the scale
        k = head / tall(s)
        w = min(m.weight_for(lambda w, k=k: barb(m.shape("arrowright", location, w)) * k, stroke), VEC_HEAVIEST)
        s = m.shape("arrowright", location, w)
    s = s.scaled(head / tall(s))
    return barbs_thickened(s, max(0.0, stroke - barb(s)))


def vec_arrow(m: Masters, location: dict) -> Shape:
    """\\vec's arrow (and the over and under arrows'): the vector arrows' head, its shaft as thick as its barbs."""
    stroke = vec_stroke(m, location)
    return shaft_to(vec_head(m, location, stroke), stroke / 2)


def vec_double(m: Masters, location: dict) -> Shape:
    """
    \\Overrightarrow's arrow: the vector arrows' head doubled, as ⟹ doubles
    ⟶ (doubled() in build/operators.py: the junctions on both sides of the
    shafts), the shafts as far apart as ⟹'s made as small (='s gap), shafts
    and barbs at the vector arrows' stroke where the head leaves the shafts
    room (VEC_ROOM: the barbs' inner ends that far out), lighter where it
    doesn't (heavier barbs come further in).
    """
    stroke = vec_stroke(m, location)
    s = vec_head(m, location, stroke)
    space = gap(m, location) * tall(s) / (VEC_ARROW * tall(m.shape("arrowright", location)))
    # the barbs' inner ends come in across them as they thicken: by the slant of their cut ends
    tip = max(s.points, key=lambda p: p[0])
    (_, far, _, _), _ = barbs(s)
    come_in = abs(tip[0] - s.points[far][0]) / math.hypot(tip[0] - s.points[far][0], tip[1] - s.points[far][1])
    fits = (barb_reach(s) + come_in * stroke) / VEC_ROOM - space / 2
    if fits / (1 + come_in / VEC_ROOM) < stroke:
        stroke = fits / (1 + come_in / VEC_ROOM)
        s = vec_head(m, location, stroke)
    # drawn out first: doubled() tells the head from the tail by the middle
    tail = tail_of(s)
    s = Shape([(x - 4 * tall(s), y) if i in tail else (x, y) for i, (x, y) in enumerate(s.points)], s.on, s.ends, s.advance)
    return doubled(s, space, stroke)


def arrows(upem: int) -> dict:
    """Arrow outlines by weight (em, y up from the baseline; TrueType points), and where accents start."""
    src = SOURCES / ROLES["Upright"]["source"]
    ours = OUT / "InterMath-Upright.ttf"
    cmap, our_cmap = TTFont(src).getBestCmap(), TTFont(ours).getBestCmap()
    m = Masters(src, [cmap[cp] for cp in [*ACCENTS.values(), ACCENT]] + ["arrowright", "n", "equal", "equal.case", "uni21B0"])
    heads = feature_singles(TTFont(ours), [TRIANGLE_FEATURE])
    mine = Masters(ours, [our_cmap[cp] for cp in ARROWS.values()] + [heads[our_cmap[ARROWS[k]]] for k in TRIANGLE_ARROWS])
    em = lambda v: round(v / upem, 5)  # noqa: E731
    out, accents, lengths = {}, {}, {}
    for w in WEIGHTS:
        location = {"wght": w, "opsz": 14}
        out[w] = {}
        for key, (masters, cp, names) in {
            **{k: (mine, cp, our_cmap) for k, cp in ARROWS.items()},
            **{k: (m, cp, cmap) for k, cp in ACCENTS.items()},
        }.items():
            s = vec_arrow(m, location) if key in ACCENTS else masters.shape(names[cp], location)
            out[w][key] = {"points": [[em(x), em(y)] for x, y in s.points], "on": [int(o) for o in s.on], "ends": s.ends}
            if key in TRIANGLE_ARROWS:
                t = mine.shape(heads[names[cp]], location)
                out[w][f"{key}Triangle"] = {"points": [[em(x), em(y)] for x, y in t.points], "on": [int(o) for o in t.on], "ends": t.ends}
            if key == "vec":
                d = vec_double(m, location)
                out[w]["vecDouble"] = {"points": [[em(x), em(y)] for x, y in d.points], "on": [int(o) for o in d.on], "ends": d.ends}
                # \overleftharpoon \overrightharpoon: the vector arrow keeping its upper barb, as ⇀ keeps →'s
                h = harpoon(s)
                out[w]["vecHarpoon"] = {"points": [[em(x), em(y)] for x, y in h.points], "on": [int(o) for o in h.on], "ends": h.ends}
                # the same with triangle heads (setMathFont's arrowHeads), as tall against the head as the glyphs'
                # (ams_arrow_glyphs.TRIANGLE); the harpoon's, the triangle above its shaft's lower edge
                tri = triangle(m, location, TRIANGLE * tall(s))
                for name, shape in (("vecTriangle", triangled(s, tri)), ("vecDoubleTriangle", triangled(d, tri))):
                    out[w][name] = {"points": [[em(x), em(y)] for x, y in shape.points], "on": [int(o) for o in shape.on], "ends": shape.ends}
                low = min(y for x, y in s.points if abs(x - s.bounds()[0]) < 0.5)
                ht = clipped(triangled(s, tri), low, above=True)
                out[w]["vecHarpoonTriangle"] = {"points": [[em(x), em(y)] for x, y in ht.points], "on": [int(o) for o in ht.on], "ends": ht.ends}
        accents[w] = em(m.shape(cmap[ACCENT], location).bounds()[1])
        lengths[w] = em(VEC_SPAN * m.shape("n", location).advance)
    return {"arrows": out, "accentBottom": accents, "vecLength": lengths}


# KaTeX's images over and under their content, after Inter's own double accents and Inter Math's ⟮ and {:
# \\widetilde \\utilde Inter's ͠ (its combining double tilde), \\widehat Inter's ᷍ (its double circumflex) and
# \\widecheck that upside down, drawn to the base's width (src/svg.ts); \\overgroup \\undergroup ⟮ turned a
# quarter, as tall and as thick as Inter's ͜ (its double breve below); \\overbrace \\underbrace { turned a
# quarter; the groups and braces drawn out along their straight stretches
WIDE_ACCENTS = {"wideTilde": 0x0360, "wideHat": 0x1DCD}
GROUP_SIZE = 0x035C


def stretch_cuts(shape: Shape) -> tuple[float, float]:
    """
    Where an upright brace is cut to be drawn out: in the middle of the run
    where both edges of its stem go straight (lines between on-curve points),
    above its point and under it.
    """
    _, y0, _, y1 = shape.bounds()
    centre = (y0 + y1) / 2
    lines: list[tuple[float, float, float]] = []
    for c in shape.contours():
        pts, on = c.points, c.on
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            (ax, ay), (bx, by) = pts[i], pts[j]
            if on[i] and on[j] and abs(ax - bx) < 1 and abs(ay - by) > 1:
                lines.append(((ax + bx) / 2, min(ay, by), max(ay, by)))
    cuts = []
    for above in (True, False):
        side = [ln for ln in lines if (ln[1] > centre if above else ln[2] < centre)]
        # the stem's two edges: the longest line on each, at two places across
        edges: dict[int, tuple[float, float, float]] = {}
        for ln in sorted(side, key=lambda ln: ln[2] - ln[1]):
            edges[round(ln[0])] = ln
        (_, a0, a1), (_, b0, b1) = sorted(edges.values(), key=lambda ln: ln[2] - ln[1])[-2:]
        lo, hi = max(a0, b0), min(a1, b1)
        assert hi > lo, "the brace's stem edges don't run straight side by side"
        cuts.append((lo + hi) / 2)
    return cuts[0], cuts[1]


def check_parted(shape: Shape, parts: list[int], where: str) -> None:
    """Every segment between two parts is a straight line along the stretch (upright), or drawing out bends it."""
    start = 0
    for end in shape.ends:
        for i in range(start, end + 1):
            j = i + 1 if i < end else start
            if parts[i] != parts[j]:
                (ax, _), (bx, _) = shape.points[i], shape.points[j]
                assert shape.on[i] and shape.on[j] and abs(ax - bx) < 0.5, f"{where}: the cut crosses a curve at point {i}"
        start = end + 1


def parted(shape: Shape, parts: list[int], em) -> dict:
    return {"outline": {"points": [[em(x), em(y)] for x, y in shape.points], "on": [int(o) for o in shape.on], "ends": shape.ends}, "parts": parts}


def accent_images(upem: int) -> dict:
    """
    KaTeX's wide accents, groups and braces, by weight (em, y up; TrueType
    points; the groups and braces over their content, turned): for each point
    of a group or a brace its part, 0 the left end, 1 the middle (a brace's
    point), 2 the right end, which src/svg.ts draws apart to the width.
    """
    src = SOURCES / ROLES["Upright"]["source"]
    cmap = TTFont(src).getBestCmap()
    our_cmap = TTFont(OUT / "InterMath-Upright.ttf").getBestCmap()
    m = Masters(src, [cmap[cp] for cp in (*WIDE_ACCENTS.values(), GROUP_SIZE)])
    mine = Masters(OUT / "InterMath-Upright.ttf", [our_cmap[0x27EE], our_cmap[0x7B]])
    em = lambda v: round(v / upem, 5)  # noqa: E731
    group_name, brace_name = our_cmap[0x27EE], our_cmap[0x7B]
    # the brace is cut once, at Regular, and keeps its points on the same sides at every weight: cut again at each
    # weight, the cut ran past a stretch's end from 300 up, and the curve beyond it, its control point drawn out to
    # the far end, put the middle of the brace higher than its sides
    upper, lower = stretch_cuts(mine.shape(brace_name, {"wght": 400, "opsz": 14}))
    brace_parts = [2 if y > upper else 0 if y < lower else 1 for _, y in mine.shape(brace_name, {"wght": 400, "opsz": 14}).points]

    def group_at(location: dict) -> tuple[Shape, float]:
        """Inter Math's ⟮ at the weight whose stem, against its height, is ͜'s stroke against its own; ͜'s height."""
        breve = m.shape(cmap[GROUP_SIZE], location)
        bx0, by0, bx1, by1 = breve.bounds()
        crossing = column(breve, (bx0 + bx1) / 2)
        stroke, tall = crossing[1] - crossing[0], by1 - by0

        def thickness(wght: float) -> float:
            g = mine.shape(group_name, location, wght)
            gx0, _, gx1, _ = g.bounds()
            return g.side(0.5) / (gx1 - gx0)

        return mine.shape(group_name, location, mine.weight_for(thickness, stroke / tall)), tall

    # the group too, in its straight stretches (its middle, where the brace's point folds into the stem, curves)
    regular, _ = group_at({"wght": 400, "opsz": 14})
    g_upper, g_lower = stretch_cuts(regular)
    group_parts = [2 if y > g_upper else 0 if y < g_lower else 1 for _, y in regular.points]
    out = {}
    for w in WEIGHTS:
        location = {"wght": w, "opsz": 14}
        out[w] = {key: parted(m.shape(cmap[cp], location), [], em)["outline"] for key, cp in WIDE_ACCENTS.items()}
        # the group: ⟮'s stem across, its hooks towards the base, as tall as ͜ and its stem as thick as ͜'s bowl;
        # turned clockwise, its top goes right
        group, tall = group_at(location)
        check_parted(group, group_parts, f"the group at {w}")
        gx0, _, gx1, _ = group.bounds()
        out[w]["group"] = parted(group.scaled(tall / (gx1 - gx0)).turned(-90), group_parts, em)
        # the brace: its point up (turned clockwise), its hooks at the ends; the point between its straight stretches
        brace = mine.shape(brace_name, location)
        check_parted(brace, brace_parts, f"the brace at {w}")
        out[w]["brace"] = parted(brace.turned(-90), brace_parts, em)
    return {"images": out}


# KaTeX's ovals over ∬ ∭ for \\oiint \\oiiint (SVG images: its fonts have no ∯ ∰): name → (size font, integral)
OVALS = {"oiintSize1": (1, 0x222C), "oiintSize2": (2, 0x222C), "oiiintSize1": (1, 0x222D), "oiiintSize2": (2, 0x222D)}


def ovals(upem: int) -> dict:
    """
    KaTeX's ovals for \\oiint \\oiiint, by weight (em, y up from the
    baseline, x from the integral's origin; TrueType points), with their
    integral's advance: ∮'s ring (build/big_operators.py) drawn out sideways,
    Inter's ○ made an ellipse as tall and as thick as the ring, its inside
    passing the outer stems as the ring's passes ∮'s stem.
    """
    circles = Masters(SOURCES / ROLES["Upright"]["source"], ["circlewhite"])
    em = lambda v: round(v / upem, 5)  # noqa: E731
    wide = lambda c: c.bounds()[2] - c.bounds()[0]  # noqa: E731
    out: dict = {w: {} for w in WEIGHTS}
    for size in sorted({size for size, _ in OVALS.values()}):
        path = OUT / f"InterMath-Size{size}.ttf"
        cmap = TTFont(path).getBestCmap()
        mine = Masters(path, [cmap[cp] for cp in (0x222E, *(cp for s, cp in OVALS.values() if s == size))])
        for w in WEIGHTS:
            location = {"wght": w, "opsz": 14}
            # ∮: the integral, then the ring's outer and inner circles
            *integral, outer, inner = mine.shape(cmap[0x222E], location).contours()
            _, oy0, _, oy1 = outer.bounds()
            middle, big, small = (oy0 + oy1) / 2, wide(outer) / 2, wide(inner) / 2
            (s0, s1), = Shape.join(integral, 0).runs(middle)
            past = small - (s1 - s0) / 2
            o_big, o_small = sorted(circles.shape("circlewhite", location).contours(), key=wide, reverse=True)
            for name, (s, cp) in OVALS.items():
                if s != size:
                    continue
                integrals = mine.shape(cmap[cp], location)
                stems = integrals.runs(middle)
                left, right = stems[0][0], stems[-1][1]
                centre, inside = (left + right) / 2, (right - left) / 2 + past

                def stretched(c: Shape, rx: float, ry: float) -> Shape:
                    x0, y0, x1, y1 = c.bounds()
                    return c.map(lambda x, y: (centre + (x - (x0 + x1) / 2) * 2 * rx / (x1 - x0), middle + (y - (y0 + y1) / 2) * 2 * ry / (y1 - y0)))

                oval = Shape.join([stretched(o_big, inside + big - small, big), stretched(o_small, inside, small)], 0)
                outline = {"points": [[em(x), em(y)] for x, y in oval.points], "on": [int(o) for o in oval.on], "ends": oval.ends}
                out[w][name] = {"outline": outline, "advance": em(integrals.advance)}
    return {"ovals": out}


# KaTeX's tall | and ‖ (\\left| past the text size, \\big|, vmatrix): one SVG image of any height, its path and
# box drawn as Inter Math's ∣ ∥ (src/svg.ts); and the straight stem it draws between a tall brace's pieces, as
# Inter Math's ⎪ (build/delimiters.py), or a stretched arrow's, as its ⏐ ‖ (build/ams_arrow_glyphs.py). Name → (the
# font, the glyph's code point)
BARS = {"vert": ("Upright", 0x2223), "doublevert": ("Upright", 0x2225), "brace": ("Size4", 0x23AA), "arrow": ("Size1", 0x23D0),
        "double": ("Size1", 0x2016)}


def bars(upem: int) -> dict:
    """Inter Math's ∣ ∥ ⎪ by weight (em, optical size 14): each bar's left and right edges, and the advance."""
    em = lambda v: round(v / upem, 5)  # noqa: E731
    out: dict = {w: {} for w in WEIGHTS}
    for name, (font, cp) in BARS.items():
        path = OUT / f"InterMath-{font}.ttf"
        cmap = TTFont(path).getBestCmap()
        mine = Masters(path, [cmap[cp]])
        for w in WEIGHTS:
            s = mine.shape(cmap[cp], {"wght": w, "opsz": 14})
            edges = sorted([em(c.bounds()[0]), em(c.bounds()[2])] for c in s.contours())
            out[w][name] = {"bars": edges, "advance": em(s.advance)}
    return {"bars": out}


# KaTeX's delimiters Inter Math draws as one SVG image at any height past its text size (our KaTeX patch's anyHeight,
# src/svg.ts): KaTeX's name for the image → the delimiter. Its five sizes of each (the text size's, then KaTeX's four)
# are mixed between; past the largest, the largest is drawn out, as TeX's tall ones are (a straight stretch between
# their ends; ⟨ ⟩ / \\ stop at the largest, as KaTeX's). KaTeX's sizes made a delimiter jump from one to the next as
# its content grew with the weight (TeX's spaces follow the rule). The right ones that are their left one mirrored
# are left out (src/svg.ts mirrors them): ( and ) are drawn apart
TALLS = {"lparen": 0x28, "rparen": 0x29, "lbrack": 0x5B, "lfloor": 0x230A, "lceil": 0x2308, "lbrace": 0x7B, "langle": 0x27E8,
         "lgroup": 0x27EE, "lmoustache": 0x23B0, "slash": 0x2F}
TALL_MIRRORS = {"rbrack": "lbrack", "rfloor": "lfloor", "rceil": "lceil", "rbrace": "lbrace", "rangle": "langle", "rgroup": "lgroup",
                "rmoustache": "lmoustache", "backslash": "slash"}
# those drawn out past the largest along their stems' straight stretches, above and under their middle (cut at
# Regular), and those that stop at the largest
STRETCHED = {"lbrace", "lgroup", "lmoustache"}
CAPPED = {"langle", "slash"}


def cut_across(shape: Shape, convex: str | None) -> tuple[Shape, list[int]]:
    """
    A delimiter cut across where it is drawn out, as TeX's tall ones are (a
    straight stretch between their ends): each point, and whether it moves up
    (1) or down. A parenthesis is cut where its curves turn vertical (its
    on-curve points farthest out on its `convex` side, on both edges): each is
    doubled, the two copies moving apart into a straight stretch. A bracket
    (no convex side) is cut across its stem, in its middle.
    """
    _, y0, _, y1 = shape.bounds()
    if convex is None:
        middle = (y0 + y1) / 2
        return shape, [int(y > middle) for _, y in shape.points]
    pts = [p for p, on in zip(shape.points, shape.on) if on]
    _, middle = (min if convex == "left" else max)(pts, key=lambda p: p[0])
    points, on, ends, up = [], [], [], []
    for c in shape.contours():
        for i, ((x, y), o) in enumerate(zip(c.points, c.on)):
            if o and abs(y - middle) < 0.5:
                # coming from below: the lower copy first
                below = c.points[i - 1][1] < middle
                points += [(x, y), (x, y)]
                on += [True, True]
                up += [0, 1] if below else [1, 0]
            else:
                points.append((x, y))
                on.append(o)
                up.append(int(y > middle))
        ends.append(len(points) - 1)
    assert sum(1 for u, o in zip(up, on) if o) > 0
    return Shape(points, on, ends, shape.advance), up


def talls(upem: int) -> dict:
    """
    Inter Math's ( ) [ ⌊ ⌈ { ⟨ ⟮ ⎰ / at its five sizes, by weight (em, y up,
    optical size 14): the same points at each size, cut where the largest is
    drawn out (each point's part: 0 moves down, 1 stays, 2 moves up), and
    each size's advance.
    """
    fonts = [OUT / "InterMath-Upright.ttf", *(OUT / f"InterMath-Size{n}.ttf" for n in SIZES)]
    sized = []
    for path in fonts:
        cmap = TTFont(path).getBestCmap()
        sized.append((Masters(path, [cmap[cp] for cp in TALLS.values()]), cmap))
    em = lambda v: round(v / upem, 5)  # noqa: E731
    largest, largest_cmap = sized[-1]
    stretched = {}
    for name in STRETCHED:
        shape = largest.shape(largest_cmap[TALLS[name]], {"wght": 400, "opsz": 14})
        upper, lower = stretch_cuts(shape)
        stretched[name] = [2 if y > upper else 0 if y < lower else 1 for _, y in shape.points]
    out: dict = {}
    for w in WEIGHTS:
        location = {"wght": w, "opsz": 14}
        out[w] = {}
        for name, cp in TALLS.items():
            shapes = [m.shape(cmap[cp], location) for m, cmap in sized]
            if name in stretched:
                parts = stretched[name]
                check_parted(shapes[-1], parts, f"{name} at {w}")
            elif name in CAPPED:
                parts = [1] * len(shapes[-1].points)
            else:
                cuts = [cut_across(s, {0x28: "left", 0x29: "right"}.get(cp)) for s in shapes]
                assert all(up == cuts[-1][1] for _, up in cuts), f"{name} at {w}: its sizes cut differently"
                shapes = [cut for cut, _ in cuts]
                parts = [2 if up else 0 for up in cuts[-1][1]]
            assert all(len(s.points) == len(shapes[0].points) and s.ends == shapes[0].ends for s in shapes), f"{name}: its sizes differ"
            out[w][name] = {
                "sizes": [[[em(x), em(y)] for x, y in s.points] for s in shapes],
                "on": [int(o) for o in shapes[0].on],
                "ends": shapes[0].ends,
                "parts": parts,
                "advances": [em(s.advance) for s in shapes],
            }
    # the same points at every weight (the images are mixed between them)
    for name in TALLS:
        assert len({tuple(out[w][name]["parts"]) for w in WEIGHTS}) == 1, f"{name}: cut differently across weights"
    return {"talls": out, "tallHeights": [NORMAL, *SIZES.values()]}


def ts_table(table: dict) -> str:
    fmt = lambda v: "0" if v == 0 else repr(v)  # noqa: E731
    rows = (f"{int(cp)}:[{','.join(fmt(v) for v in vals)}]" for cp, vals in sorted(table.items(), key=lambda kv: int(kv[0])))
    return "{" + ",".join(rows) + "}"


def write_metrics(classic: dict, inter: dict, measured: dict, inter_version: str, katex_version: str) -> None:
    names = list(classic)
    lines = [
        f"// GENERATED by build/build.py from Inter {inter_version} and KaTeX {katex_version}. Do not edit.",
        "",
        "/** KaTeX's metrics for one character: depth, height, italic correction, skew, width (em). */",
        "export type CharMetrics = [number, number, number, number, number];",
        "export type MetricTable = Record<number, CharMetrics>;",
        f"export type KatexFont = {' | '.join(json.dumps(n) for n in names)};",
        "",
        f'export const versions = {{ inter: "{inter_version}", katex: "{katex_version}" }};',
        "",
        "/** KaTeX's own tables (Computer Modern) for the fonts Inter Math replaces. */",
        "export const classic: Record<KatexFont, MetricTable> = {",
        *(f"  {json.dumps(n)}: {ts_table(classic[n])}," for n in names),
        "};",
        "",
        "/** Inter Math's glyphs, measured at the table's weight and optical size 14 (the rest stays KaTeX's). */",
        "export const inter: Record<KatexFont, MetricTable> = {",
        *(f"  {json.dumps(n)}: {ts_table(inter[n])}," for n in names),
        "};",
        "",
        "export type Point = [number, number];",
        "/** Inter's √ (em, y up from the baseline): bar and down-stroke as drawn, the up-stroke's defining points. */",
        "export interface Radical {",
        "  bar: Point[];",
        "  down: Point[];",
        "  join: Point;",
        "  bottomInner: Point;",
        "  bottomRight: Point;",
        "  topLeft: Point;",
        "  topRight: Point;",
        "}",
        "",
        "/** Inter Math's x-height (em), TeX's sigma 5. */",
        f"export const xHeight = {measured['xHeight']};",
        "/** Inter Math's math axis (em), TeX's sigma 22: the centre of its operators, between its lowercase and its capitals. */",
        f"export const axisHeight = {measured['axis']};",
        "",
        "/** Thickness of Inter Math's minus sign (em) by weight: TeX's rules (fraction bars, vinculums) follow it. */",
        f"export const rules: Record<number, number> = {json.dumps(measured['rules']).replace(chr(34), '')};",
        "",
        "/** A glyph's TrueType outline (em, y up from the baseline). */",
        "export interface Outline {",
        "  points: Point[];",
        "  on: number[];",
        "  ends: number[];",
        "}",
        "export type ArrowName = " + " | ".join(json.dumps(k) for k in {**ARROWS, **ACCENTS, "vecDouble": 0, "vecHarpoon": 0, "vecTriangle": 0,
                                                                       "vecDoubleTriangle": 0, "vecHarpoonTriangle": 0,
                                                                       **{f"{k}Triangle": 0 for k in TRIANGLE_ARROWS}}) + ";",
        "",
        "/** Inter Math's long arrows and Inter's accent arrow (U+0362) by weight (optical size 14). */",
        "export const arrows: Record<number, Record<ArrowName, Outline>> = {",
        *(f"  {w}: {json.dumps(a, separators=(',', ':'))}," for w, a in measured["arrows"].items()),
        "};",
        "",
        "/** Where Inter's accents over lowercase start (the bottom of its circumflex, em), by weight. */",
        f"export const accentBottom: Record<number, number> = {json.dumps(measured['accentBottom']).replace(chr(34), '')};",
        "",
        "/** How long a vector arrow is over a letter (em), by weight: it widens as the letters do. */",
        f"export const vecLength: Record<number, number> = {json.dumps(measured['vecLength']).replace(chr(34), '')};",
        "",
        "/** Inter's underline (the line under its ḇ) by weight: [how far under the baseline its top is, its thickness] (em). */",
        f"export const underlines: Record<number, [number, number]> = {json.dumps(measured['underlines']).replace(chr(34), '')};",
        "",
        "/** Inter's strike-through (\\sout): how far over the baseline its top is (em); it is as thick as the underline. */",
        f"export const strikeTop = {measured['strike']};",
        "",
        "/** \\TeX's E: how far over its baseline the bottom of its middle bar is (em), by weight (T and X stand there). */",
        f"export const logoBar: Record<number, number> = {json.dumps(measured['logo']).replace(chr(34), '')};",
        "",
        "/**",
        " * Where KaTeX centres an accent over each italic letter Inter puts marks over (the letter's skew, em), by",
        " * weight: under the middle of the dots of Inter's ¨ over it. KaTeX reads one table (Regular's): setMathFont",
        " * gives it the weight's.",
        " */",
        f"export const italicSkews: Record<number, Record<number, number>> = {json.dumps(measured['italicSkews'], separators=(',', ':'))};",
        "",
        "/** The same over each upright letter (Main's), by weight. */",
        f"export const uprightSkews: Record<number, Record<number, number>> = {json.dumps(measured['uprightSkews'], separators=(',', ':'))};",
        "",
        "/**",
        " * The integrals' italic corrections (em), by Size font and weight: where KaTeX sets their superscripts, the",
        " * advance (where it sets their subscripts) changing with the weight. KaTeX reads Regular's: setMathFont gives it",
        " * the weight's.",
        " */",
        f"export const operatorItalics: Partial<Record<KatexFont, Record<number, Record<number, number>>>> = {json.dumps(measured['operatorItalics'], separators=(',', ':'))};",
        "",
        "/** How thick Inter's strokes that cancel a letter (Ɇ ȼ) are across, by weight (em): \\cancel's. */",
        f"export const cancels: Record<number, number> = {json.dumps(measured['cancels']).replace(chr(34), '')};",
        "",
        "/** KaTeX's ovals over ∬ ∭ for \\oiint \\oiiint (its SVG images) by weight (optical size 14): ∮'s ring drawn out sideways, with the integral's advance. */",
        "export type OvalName = " + " | ".join(json.dumps(k) for k in OVALS) + ";",
        "export interface Oval {",
        "  outline: Outline;",
        "  advance: number;",
        "}",
        "export const ovals: Record<number, Record<OvalName, Oval>> = {",
        *(f"  {w}: {json.dumps(o, separators=(',', ':'))}," for w, o in measured["ovals"].items()),
        "};",
        "",
        "/** Inter Math's ∣ ∥ by weight (optical size 14), for the tall | and ‖ KaTeX draws as one image of any height, and its ⎪ ⏐ ‖, for the stem KaTeX draws between a tall brace's or a stretched arrow's pieces: each bar's left and right edges, and the advance (em). */",
        "export type BarName = " + " | ".join(json.dumps(k) for k in BARS) + ";",
        "export interface Bars {",
        "  bars: [number, number][];",
        "  advance: number;",
        "}",
        "export const bars: Record<number, Record<BarName, Bars>> = {",
        *(f"  {w}: {json.dumps(b, separators=(',', ':'))}," for w, b in measured["bars"].items()),
        "};",
        "",
        "/**",
        " * Inter Math's ( ) [ ⌊ ⌈ { ⟨ ⟮ ⎰ / at its five sizes (the text size's, then KaTeX's four: tallHeights, em), by weight",
        " * (optical size 14), for the delimiters KaTeX sets as one image at any height past the text size: the same points at",
        " * each size (mixed between two), each point's part when the largest is drawn out (0 moves down, 1 stays, 2 moves",
        " * up), and each size's advance (em). ] ⌋ ⌉ } ⟩ ⟯ ⎱ \\ are the left ones mirrored (src/svg.ts).",
        " */",
        f"export const tallHeights: number[] = {json.dumps(measured['tallHeights'])};",
        "export type TallName = " + " | ".join(json.dumps(k) for k in TALLS) + ";",
        "export interface Tall {",
        "  sizes: Point[][];",
        "  on: number[];",
        "  ends: number[];",
        "  parts: number[];",
        "  advances: number[];",
        "}",
        "export const talls: Record<number, Record<TallName, Tall>> = {",
        *(f"  {w}: {json.dumps(t, separators=(',', ':'))}," for w, t in measured["talls"].items()),
        "};",
        "",
        "/** KaTeX's images over and under their content, by weight (optical size 14): \\widetilde \\utilde Inter's ͠, \\widehat \\widecheck its ᷍, as they are (src/svg.ts draws them to the width); \\overgroup \\undergroup ⟮ turned (as tall and as thick as Inter's ͜), \\overbrace \\underbrace { turned, each point's part (0 the left end, 1 the middle, 2 the right end) drawn apart to the width. */",
        "export interface Parted {",
        "  outline: Outline;",
        "  parts: number[];",
        "}",
        "export interface Images {",
        "  wideTilde: Outline;",
        "  wideHat: Outline;",
        "  group: Parted;",
        "  brace: Parted;",
        "}",
        "export const images: Record<number, Images> = {",
        *(f"  {w}: {json.dumps(i, separators=(',', ':'))}," for w, i in measured["images"].items()),
        "};",
        "",
        "/** Inter's √ by weight (optical size 14). */",
        "export const radicals: Record<number, Radical> = {",
        *(f"  {w}: {json.dumps(r, separators=(',', ':'))}," for w, r in measured["radicals"].items()),
        "};",
        "",
    ]
    METRICS_TS.parent.mkdir(parents=True, exist_ok=True)
    METRICS_TS.write_text("\n".join(lines))


def merge(tables: dict, more: dict) -> None:
    """Metric tables into others, font by font (several fonts of ours may fill one of KaTeX's)."""
    for name, table in more.items():
        tables.setdefault(name, {}).update(table)


# What Inter Math draws its glyphs from, for the workbench (/dev/symbols): code point → (how, Inter's glyphs), for
# the glyphs Inter lacks (and a few of its own drawn from others); its own redrawn (larger, moved…) need none
# the glyphs this module maps: the italic dotless letters
OWN_FROM = {
    0xE131: ("Inter's italic ı (\\imath)", "italic:dotlessi"),
    0xE237: ("Inter's italic ȷ (\\jmath)", "italic:uni0237"),
}
DRAWN_FROM = {
    **GEOMETRY_FROM, **SYMBOLS_FROM, **ORDER_FROM, **NEGATED_FROM, **EQUALITY_FROM, **SHAPES_FROM, **SETS_FROM, **LETTERS_FROM, **PRECEDENCE_FROM, **BINARY_FROM, **ARROWS_FROM, **BIG_OPERATORS_FROM, **DELIMITERS_FROM,
    **AMS_ARROWS_FROM, **ARROW_PIECES_FROM, **MISC_FROM, **OWN_FROM, **ACCENTS_FROM,
}
# KaTeX's SVG images and rules Inter Math draws (src/surd.ts, src/svg.ts, src/index.ts), by the commands that use them
_VECTOR = ("Inter's →, its head smaller, its barbs and shaft one stroke", "arrowright")
SVG_FROM = {
    "\\sqrt": ("Inter's √, larger for taller surds; its up-stroke rebuilt, the vinculum as thick", "radical"),
    **dict.fromkeys(["\\vec", "\\overrightarrow", "\\overleftarrow", "\\overleftrightarrow", "\\underrightarrow",
                     "\\underleftarrow", "\\underleftrightarrow"], _VECTOR),
    "\\Overrightarrow": ("the vector arrow doubled, as ⟹ doubles ⟶", "arrowdblright"),
    "\\xrightarrow": ("Inter Math's ⟶, drawn out", "uni27F6"),
    "\\xleftarrow": ("Inter Math's ⟵, drawn out", "uni27F5"),
    "\\xleftrightarrow": ("Inter Math's ⟵ and ⟶, drawn out", "uni27F5 uni27F6"),
    "\\xRightarrow": ("Inter Math's ⟹, drawn out", "uni27F9"),
    "\\xLeftarrow": ("Inter Math's ⟸, drawn out", "uni27F8"),
    "\\xLeftrightarrow": ("Inter Math's ⟸ and ⟹, drawn out", "uni27F8 uni27F9"),
    "\\xhookrightarrow": ("Inter Math's ↪, its shaft drawn out", "arrowright"),
    "\\xhookleftarrow": ("Inter Math's ↩, its shaft drawn out", "arrowleft"),
    "\\xmapsto": ("Inter Math's ↦, its shaft drawn out", "arrowright"),
    "\\xtofrom": ("Inter Math's ⇄, its shafts drawn out", "arrowright arrowleft"),
    "\\xtwoheadrightarrow": ("Inter Math's ↠, its shaft drawn out", "arrowright"),
    "\\xtwoheadleftarrow": ("Inter Math's ↞, its shaft drawn out", "arrowleft"),
    "\\xlongequal": ("Inter Math's =, its bars drawn out", "equal"),
    **dict.fromkeys(["\\underline", "\\underbar"], ("the line under Inter's ḇ: as far under the text, as thick", "uni1E07")),
    **dict.fromkeys(["\\oiint", "\\oiiint"], ("∮'s ring of ○ drawn out sideways over ∬ ∭", "circlewhite italic:integral")),
    # the tall | and ‖ (src/svg.ts): the documented examples that stretch them
    **dict.fromkeys(["vmatrix", "Vmatrix", "\\bigm", "\\Bigm", "\\biggm", "\\Biggm"], ("Inter Math's ∣ ∥ drawn out to the height", "bar")),
    # over and under their content (src/svg.ts, accent_images())
    "\\widetilde": ("the wide tilde: Inter's ͠ (its double tilde) drawn out to the width, its stroke kept", "uni0360"),
    "\\utilde": ("the wide tilde, under", "uni0360"),
    "\\widehat": ("Inter's ᷍ (its double circumflex) drawn out to the width", "uni1DCD"),
    "\\widecheck": ("Inter's ᷍ upside down, drawn out to the width", "uni1DCD"),
    **dict.fromkeys(["\\overgroup", "\\undergroup"], ("Inter Math's ⟮ turned a quarter, as tall and as thick as Inter's ͜, drawn out", "braceleft uni035C")),
    **dict.fromkeys(["\\overbrace", "\\underbrace"], ("Inter Math's { turned a quarter, drawn out along its straight stretches", "braceleft")),
    **dict.fromkeys(["\\overbracket", "\\underbracket"], ("a line as thick as the underline, its ends upright", "uni1E07")),
    **dict.fromkeys(["\\overlinesegment", "\\underlinesegment"], ("a line as thick as the underline through upright ends as tall as the vector arrows' heads", "uni1E07")),
    **dict.fromkeys(["\\overleftharpoon", "\\overrightharpoon"], ("the vector arrow keeping its upper barb, as ⇀ keeps →'s, in the arrow's box", "arrowright")),
    "\\xrightharpoonup": ("Inter Math's ⇀, drawn out, in ⟶'s box", "arrowright"),
    "\\xrightharpoondown": ("Inter Math's ⇁, drawn out, in ⟶'s box", "arrowright"),
    "\\xleftharpoonup": ("Inter Math's ↼, drawn out, in ⟵'s box", "arrowright"),
    "\\xleftharpoondown": ("Inter Math's ↽, drawn out, in ⟵'s box", "arrowright"),
    "\\xrightleftharpoons": ("Inter Math's ⇌, each harpoon drawn out", "arrowright"),
    "\\xleftrightharpoons": ("Inter Math's ⇋, each harpoon drawn out", "arrowright"),
    # KaTeX's lines (our patch's metrics: src/index.ts)
    "\\overline": ("the underline's mirror: as far over the content and as thick", "uni1E07"),
    "\\sout": ("Inter's strike-through: its height, as thick as the underline", "uni1E07"),
    **dict.fromkeys(["\\cancel", "\\bcancel", "\\xcancel"], ("a stroke as thick as Inter's across Ɇ ȼ", "uni0246 uni023C")),
    "\\phase": ("its line and its angle as thick as the underline", "uni1E07"),
}
# what the larger sizes and the blackboard letters are, against Inter's glyph for the character
ROLE_HOW = {**{f"Size{n}": f"KaTeX's size {n}" for n in range(1, 5)}, "Blackboard": "hollow strokes on Inter's letter (\\mathbb)"}
# Inter Math's fonts and the Inter each is drawn from
FONT_ROLES = {
    "Upright": ("InterMath-Upright", "Upright"), "Italic": ("InterMath-Italic", "Italic"),
    **{f"Size{n}": (f"InterMath-Size{n}", "Upright") for n in range(1, 5)}, "Blackboard": ("InterMath-Blackboard", "Upright"),
    "AMS": ("InterMath-AMS", "Upright"),
}
# Inter Math's families, for the reference of what each glyph is built on (build/parts.py): title, the module that
# draws it, the fonts it goes in, its code points (None: all the fonts'). A glyph with no DRAWN_FROM entry is
# Inter's own, redrawn (larger, moved, at another size)
MATH_FONTS = ("Upright", "Size1", "Size2", "Size3", "Size4")
FAMILIES = [
    ("Operators and arrows: Inter's, larger, on the axis", "operators.py", MATH_FONTS, set(OPERATORS)),
    ("Geometry and sets", "geometry_glyphs.py", MATH_FONTS, set(GEOMETRY_FROM)),
    ("More symbols", "symbol_glyphs.py", MATH_FONTS, set(SYMBOLS_FROM)),
    ("Arrows", "arrow_glyphs.py", MATH_FONTS, set(ARROWS_FROM)),
    ("Delimiters", "delimiters.py", MATH_FONTS, {*DELIMITERS_FROM, *CURVED, *STRAIGHT, *BRACES, *SLASHES}),
    ("Big operators", "big_operators.py", MATH_FONTS, {*BIG_OPERATORS_FROM, *SUMS}),
    ("Order relations, AMS", "order_glyphs.py", MATH_FONTS, set(ORDER_FROM)),
    ("Negated relations", "negated_glyphs.py", MATH_FONTS, set(NEGATED_FROM)),
    ("Equalities with marks", "equality_glyphs.py", MATH_FONTS, set(EQUALITY_FROM)),
    ("School shapes", "shape_glyphs.py", MATH_FONTS, set(SHAPES_FROM)),
    ("Sets, turnstiles, joins", "set_glyphs.py", MATH_FONTS, set(SETS_FROM)),
    ("Letter-like symbols", "letter_glyphs.py", MATH_FONTS, set(LETTERS_FROM)),
    ("Precedence", "precedence_glyphs.py", MATH_FONTS, set(PRECEDENCE_FROM)),
    ("Binary operators", "binary_glyphs.py", MATH_FONTS, set(BINARY_FROM)),
    ("Arrows, AMS, and the pieces of stretched arrows", "ams_arrow_glyphs.py", MATH_FONTS, {*AMS_ARROWS_FROM, *ARROW_PIECES_FROM}),
    ("Shapes, suits, music", "misc_glyphs.py", MATH_FONTS, set(MISC_FROM)),
    ("Accents: Inter's marks, upright and italic, where Inter puts them", "symbol_glyphs.py", ("Upright", "Italic"), set(ACCENTS_FROM)),
    ("Dotless letters", "build.py", ("Italic",), set(OWN_FROM)),
    ("AMS variants, in their own font", "ams_variants.py", ("AMS",), set(VARIANTS_FROM)),
    ("Blackboard bold", "blackboard.py", ("Blackboard",), None),
]


def glyph_outline(font: TTFont, name: str) -> list:
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[name].draw(pen)
    return pen.value


def inter_glyph(name: str, fonts: dict) -> dict:
    """One of Inter's glyphs, to show it: its character, the feature that picks it (case forms), its font (italic:)."""
    role, key = ("Italic", name.removeprefix("italic:")) if name.startswith("italic:") else ("Upright", name)
    font = fonts[role]
    assert key in font.getGlyphOrder(), f"Inter has no glyph {key}"
    from fontTools.agl import toUnicode

    base, _, feature = key.partition(".")
    cmap = font.getBestCmap()
    # the character its name stands for (quoteright: ’, not ʼ, which Inter maps to it too), or its first one
    named = toUnicode(base)
    text = named if len(named) == 1 and cmap.get(ord(named)) == base else chr(min(cp for cp, n in cmap.items() if n == base))
    return {"text": text, **({"features": feature} if feature else {}), **({"italic": True} if role == "Italic" else {})}


def structure(outline: list) -> list[tuple[int, int]]:
    """
    An outline's contours, each as how many segments and points it has
    (sorted: their order may change): the same for a glyph only moved,
    scaled, mirrored, turned, drawn out or taken at another weight.
    """
    contours, current = [], None
    for op, args in outline:
        if op == "moveTo":
            current = [0, 0]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            # a contour of off-curve points only starts with its first curve
            current = current or [0, 0]
            current[0] += 1
            current[1] += len(args)
        elif op in ("closePath", "endPath") and current:
            contours.append(tuple(current))
            current = None
    return sorted(contours)


# a glyph drawn from one of Inter's is still Inter's (`kept`) when, both scaled to the same box, its points are within
# this share of the box of Inter's (on average, the worst contour): resized, moved, turned or drawn out, at another
# weight. Glyphs reshaped (a bar slanted, an arm folded) or rebuilt from rectangles are further
KEPT_DISTANCE = 0.14
# the turns and mirrors a kept glyph may have been drawn with
TURNS = [(c, m) for c in range(8) for m in (False, True)]


def outline_contours(outline: list) -> list[list[tuple[float, float]]]:
    """An outline's contours as their stored points (on- and off-curve)."""
    contours, current = [], None
    for op, args in outline:
        if op == "moveTo":
            current = [args[0]]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            current = (current or []) + [a for a in args if a is not None]
        elif op in ("closePath", "endPath") and current:
            contours.append(current)
            current = None
    return contours


def shape_distance(mine: list, theirs: list) -> float:
    """
    How far apart two outlines of the same structure are, each scaled to its
    box: the mean distance between their points (in the box's share), for
    the worst contour, at the best turn (eighths) or mirror of Inter's.
    """

    def boxed(contours: list) -> list:
        xs, ys = [x for c in contours for x, _ in c], [y for c in contours for _, y in c]
        x0, y0 = min(xs), min(ys)
        w, h = (max(xs) - x0) or 1, (max(ys) - y0) or 1
        return [[((x - x0) / w, (y - y0) / h) for x, y in c] for c in contours]

    def apart(a: list, b: list) -> float:
        # the best start and direction: the same contour may start elsewhere, or run the other way once mirrored
        n = len(a)
        return min(sum(math.dist(a[i], seq[(i + k) % n]) for i in range(n)) / n for seq in (b, b[::-1]) for k in range(n))

    ours = boxed(outline_contours(mine))
    best = math.inf
    for eighths, mirror in TURNS:
        c, s = math.cos(eighths * math.pi / 4), math.sin(eighths * math.pi / 4)
        turned = [[((-x if mirror else x) * c - y * s, (-x if mirror else x) * s + y * c) for x, y in contour] for contour in outline_contours(theirs)]
        candidates, used, worst = boxed(turned), set(), 0.0
        for contour in ours:
            fits = [j for j, other in enumerate(candidates) if j not in used and len(other) == len(contour)]
            if not fits:
                worst = math.inf
                break
            j = min(fits, key=lambda j: apart(contour, candidates[j]))
            used.add(j)
            worst = max(worst, apart(contour, candidates[j]))
        best = min(best, worst)
    return best


def provenance() -> dict:
    """
    By font, how Inter Math draws each of its characters that isn't Inter's
    own glyph unchanged: an alternate of it (I, l), Inter's glyph redrawn
    (larger, moved, cut…), or a new one drawn from others (DRAWN_FROM); and
    every character each font has (the rest falls back to KaTeX's fonts).
    `kept`: the glyph is still the Inter glyph it is drawn from (its own, or
    the first one DRAWN_FROM names), only resized, moved, turned, drawn out or
    taken at another weight: the same contours with the same points, and
    about the same shape (KEPT_DISTANCE).
    """
    inter = {role: TTFont(SOURCES / spec["source"]) for role, spec in ROLES.items()}

    def kept(mine: list, name: str) -> dict:
        role, key = ("Italic", name.removeprefix("italic:")) if name.startswith("italic:") else ("Upright", name)
        theirs = glyph_outline(inter[role], key)
        return {"kept": True} if structure(mine) == structure(theirs) and shape_distance(mine, theirs) < KEPT_DISTANCE else {}

    drawn, coverage = {}, {}
    for role, (file, source) in FONT_ROLES.items():
        ours, ref = TTFont(OUT / f"{file}.ttf"), inter[source]
        rcmap = ref.getBestCmap()
        alternates = {tag: feature_singles(ref, [tag]) for tag in ROLES[role]["alternates"]} if role in ROLES else {}
        drawn[role], coverage[role] = {}, sorted(ours.getBestCmap())
        for cp, name in sorted(ours.getBestCmap().items()):
            # Inter's private-use code points hold its own alternates, not the character KaTeX means there
            mine, theirs = glyph_outline(ours, name), None if 0xE000 <= cp <= 0xF8FF else rcmap.get(cp)
            if theirs and mine == glyph_outline(ref, theirs):
                continue
            tag = next((t for t, alt in alternates.items() if theirs in alt and mine == glyph_outline(ref, alt[theirs])), None)
            if tag:
                drawn[role][cp] = {"kind": "alternate", "from": [{"text": chr(cp), "features": tag}]}
            elif (role == "AMS" and cp in VARIANTS_FROM) or (role == "Italic" and cp in ITALIC_FROM) or cp in DRAWN_FROM:
                # the AMS font's glyphs are the AMS designs of code points Main has its own designs at, the italic
                # font's accents the italic designs of Main's
                how, names = VARIANTS_FROM[cp] if role == "AMS" else ITALIC_FROM[cp] if role == "Italic" and cp in ITALIC_FROM else DRAWN_FROM[cp]
                drawn[role][cp] = {"kind": "redrawn" if theirs else "new", "how": how, "from": [inter_glyph(n, inter) for n in names.split()],
                                   **kept(mine, names.split()[0])}
            else:
                assert theirs, f"{file} U+{cp:04X}: drawn from what? (a DRAWN_FROM entry, in the module that draws it)"
                drawn[role][cp] = {"kind": "redrawn", **({"how": ROLE_HOW[role]} if role in ROLE_HOW else {}),
                                   "from": [inter_glyph(theirs, inter)] if role != "Italic" else [{"text": chr(cp), "italic": True}],
                                   **kept(mine, theirs if source == "Upright" else f"italic:{theirs}")}
    svg = {cmd: {"kind": "new", "how": how, "from": [inter_glyph(n, inter) for n in names.split()]} for cmd, (how, names) in SVG_FROM.items()}
    return {"drawn": drawn, "coverage": coverage, "svg": svg}


def write_provenance(data: dict) -> None:
    dump = lambda v: json.dumps(v, ensure_ascii=False, separators=(",", ":"))  # noqa: E731
    lines = [
        "// GENERATED by build/build.py from Inter Math's fonts and Inter's. Do not edit.",
        "",
        "/** One of Inter's glyphs: its character, the OpenType features that pick it, whether in Inter's italic. */",
        "export interface InterGlyph {",
        "  text: string;",
        "  features?: string;",
        "  italic?: boolean;",
        "}",
        "/** How Inter Math draws a character: Inter's own glyph redrawn (larger, moved…), an alternate of it, or a new one from others. */",
        "export interface Drawn {",
        '  kind: "redrawn" | "alternate" | "new";',
        "  how?: string;",
        "  from: InterGlyph[];",
        "  /** Still the Inter glyph it is drawn from (resized, moved, turned, drawn out, at another weight): the same contours and points. */",
        "  kept?: boolean;",
        "}",
        f"export type FontRole = {' | '.join(json.dumps(r) for r in FONT_ROLES)};",
        "",
        "/** By font, the characters Inter Math draws (Inter's own glyphs, kept as they are, are left out). */",
        f"export const drawn: Record<FontRole, Record<number, Drawn>> = {dump(data['drawn'])};",
        "",
        "/** By font, every character it has (anything else falls back to KaTeX's fonts). */",
        f"export const coverage: Record<FontRole, number[]> = {dump(data['coverage'])};",
        "",
        "/** KaTeX's SVG images and rules that Inter Math draws, by the commands that use them. */",
        f"export const svgDrawn: Record<string, Drawn> = {dump(data['svg'])};",
        "",
    ]
    PROVENANCE_TS.write_text("\n".join(lines))


def write_parts(data: dict) -> None:
    PARTS_MD.write_text(parts_reference(data, FAMILIES, katex_commands(katex_dir()), macros(ROOT / "src" / "index.ts")))


def main() -> None:
    katex = katex_dir()
    katex_version = json.loads((katex / "package.json").read_text())["version"]
    katex_tables = katex_metrics(katex)
    upem = axis_upem(TTFont(SOURCES / ROLES["Upright"]["source"]))
    print(f"KaTeX {katex_version}; units per em {upem} (Inter: 2048, scale {2048 / upem:.4f})")

    sizes = delimiter_glyphs(SOURCES / ROLES["Upright"]["source"], upem)
    inter, version, skews = {}, "", {}
    for role, spec in ROLES.items():
        built = build_role(role, spec, katex_tables, upem, sizes.pop(0) if role == "Upright" else [])
        merge(inter, built["metrics"])
        version = built["version"]
        skews |= built["skews"]
    # KaTeX's Size fonts: larger delimiters, and the big operators (text style: Size1, display: Size2)
    operators = big_operator_glyphs(SOURCES / ROLES["Upright"]["source"], SOURCES / ROLES["Italic"]["source"], upem, OUT / "InterMath-Upright.ttf")
    # and the pieces of stretched arrows (Size1)
    pieces = arrow_pieces(SOURCES / ROLES["Upright"]["source"], upem)
    for size, glyphs in sizes.items():
        merge(inter, build_size(size, glyphs + operators.get(size, []) + (pieces if size == 1 else []), upem, katex_tables))
    merge(inter, build_blackboard(upem))
    merge(inter, build_ams(upem))
    classic = {n: katex_tables[n] for n in inter}
    measured = strokes(TTFont(OUT / "InterMath-Upright.ttf")) | arrows(upem) | ovals(upem) | bars(upem) | talls(upem) | accent_images(upem)
    for role, key in (("Italic", "italicSkews"), ("Upright", "uprightSkews")):
        measured[key] = {cp: {w: round(v / upem, 5) for w, v in s.items()} for cp, s in sorted(skews[role].items())}
    measured["operatorItalics"] = {f"Size{size}-Regular": dict(sorted(italics.items())) for size, italics in ITALIC.items()}
    print(f"rules (minus): {measured['rules'][100]}–{measured['rules'][900]} em; x-height {measured['xHeight']} em; axis {measured['axis']} em")
    write_metrics(classic, inter, measured, version, katex_version)
    print(f"wrote {METRICS_TS.relative_to(ROOT)}")
    drawn = provenance()
    write_provenance(drawn)
    print(f"wrote {PROVENANCE_TS.relative_to(ROOT)}")
    write_parts(drawn)
    print(f"wrote {PARTS_MD.relative_to(ROOT)}")
    # the OpenType math font, from the fonts and metrics above (build/opentype.py), and MathJax's font from it
    # (build/mathjax.py)
    from mathjax import build as build_mathjax
    from opentype import build as build_opentype

    build_opentype()
    build_mathjax()


if __name__ == "__main__":
    main()
