#!/usr/bin/env python3
"""
Inter Math for MathJax 4: a font for MathJax's SVG output, made from the
OpenType math font at one weight (Regular, the text optical size).

    build/.venv/bin/python build/mathjax.py     (pnpm font:build runs it after build/opentype.py)

MathJax's fonts are each made from an OpenType math font (its font tools
aren't published), as data MathJax lays math out with: each character's
height, depth, width, italic correction and skew, and its outline as an SVG
path, by variant; the delimiters' sizes and how taller ones are stacked; TeX's
parameters. Here, from InterMath-Regular.ttf:
- every character the font maps, in the normal variant: MathJax reaches the
  italic, bold, double-struck and sans serif letters through Unicode's math
  alphabets (its variants' SMP mapping), which the font has; script, Fraktur
  and monospace letters, which Inter Math has none of, are MathJax's text
  fallback;
- the AMS designs (\\varnothing \\thicksim…) as the TeX variant forms;
- the MATH table's variants (one size variant each: normal, -smallop,
  -largeop, -size3…) and assemblies (their pieces in -lf-tp, -ext, -rt-bt,
  -mid, at the delimiter's code point), the big operators' display size in
  -largeop;
- TeX's parameters from the MATH table's constants, and those it has none for
  KaTeX's, in Inter's em (the OpenType font's: math as large as Inter's text);
- each glyph's skew from where accents go over it, less the share of its
  italic correction MathJax adds itself.

Out: src/mathjax-font/svg.js, the font as a MathJax component: the package's svg.js,
at its root, so that MathJax loads it from the package's URL (MathJax takes
<url>/svg.js, its last part naming the font):
    MathJax = { output: { font: "https://cdn.jsdelivr.net/npm/inter-math" } }
with a component without a font of its own (tex-svg-nofont.js).
"""

import json
import re
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "build" / "out" / "opentype" / "InterMath-Regular.ttf"
# KaTeX's fonts, whose em TeX's parameters are given in (build.py's)
KATEX_FONT = ROOT / "build" / "out" / "InterMath-Upright.ttf"
OUT = ROOT / "src" / "mathjax-font" / "svg.js"
# the font's name in MathJax: its loader path, the last part of its URL
NAME = "inter-math"
VERSION = json.loads((ROOT / "package.json").read_text())["version"]

# MathJax's paths are in thousandths of an em
PATH_EM = 1000
# the share of a base's italic correction MathJax adds to an accent's skew (FontData's skewIcFactor)
SKEW_IC_FACTOR = 0.75
# TeX's parameters the MATH table has none for, in KaTeX's em (KaTeX's, as TeX's cmsy10 and cmex10): the subscript
# shift with a superscript (σ17), the delimiters around a generalized fraction in display and text style (σ20, σ21),
# the space below and above big operators' limits (ξ13), the null delimiter's width and the shortfall delimiters are
# allowed (\nulldelimiterspace, \delimitershortfall as MathJax has it), MathJax's extra italic correction
SUB2, DELIM1, DELIM2, BIG_OP_SPACING5, NULL_DELIMITER, DELIMITER_SHORTFALL, EXTRA_IC = 0.247, 2.39, 1.01, 0.1, 0.12, 0.3, 0.033
# the stretch variants MathJax looks pieces up in, by index (stretchv)
STRETCH = ["normal", "-ext", "-lf-tp", "-rt-bt", "-mid"]
# the big operators: their text style is the normal variant's, their display style -largeop's
BIG_OPERATORS = {0x220F, 0x2210, 0x2211, 0x222B, 0x222C, 0x222D, 0x222E, 0x22C0, 0x22C1, 0x22C2, 0x22C3, 0x2A00, 0x2A01,
                 0x2A02, 0x2A04, 0x2A06}
# the integrals (∫ ∬ ∭ ∮ and their sizes), whose advance the math font widens by their italic correction
INTEGRALS = ("integral", "uni222C", "uni222D", "uni222E")
# MathJax's line accents (\overline, \underline: U+2015 drawn out) and the bar they are drawn from
LINES = {0x2015: 0x203E}
# the accents MathJax's TeX input sets with characters the font doesn't map (\bar ¯, \grave `), and the ones KaTeX
# sets them with (ˉ ˋ), which the font has
ACCENTS = {0x00AF: 0x02C9, 0x0060: 0x02CB}


def number(v: float) -> str:
    """A length in em, as MathJax's fonts write them (.5, -.25)."""
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    s = re.sub(r"^(-?)0\.", r"\1.", s)
    return "0" if s in ("", "-0", "-") else s


class Glyphs:
    """The font's glyphs as MathJax's character data: [h, d, w, {p, ic, sk}] in em."""

    def __init__(self, font: TTFont):
        self.font, self.upem = font, font["head"].unitsPerEm
        self.set, self.hmtx = font.getGlyphSet(), font["hmtx"]
        info = font["MATH"].table.MathGlyphInfo
        italics, accents = info.MathItalicsCorrectionInfo, info.MathTopAccentAttachment
        self.italics = {g: v.Value for g, v in zip(italics.Coverage.glyphs, italics.ItalicsCorrection)}
        self.accents = {g: v.Value for g, v in zip(accents.TopAccentCoverage.glyphs, accents.TopAccentAttachment)}
        self.cache = {}

    def bounds(self, name: str):
        pen = BoundsPen(self.set)
        self.set[name].draw(pen)
        return pen.bounds

    def path(self, name: str) -> str:
        """The glyph's outline as MathJax's fonts have it: SVG path data without its first M, which MathJax adds."""
        pen = SVGPathPen(self.set, ntos=lambda v: str(round(v)))
        self.set[name].draw(TransformPen(pen, (PATH_EM / self.upem, 0, 0, PATH_EM / self.upem, 0, 0)))
        return pen.getCommands().removeprefix("M")

    def em(self, units: float) -> float:
        return units / self.upem

    def data(self, name: str, skew: bool = True) -> str:
        if (name, skew) in self.cache:
            return self.cache[name, skew]
        b = self.bounds(name)
        h, d = (self.em(b[3]), self.em(-b[1])) if b else (0, 0)
        # MathJax counts a character's italic correction in its width, as TeX does: the integrals' advance without
        # it, their copy for KaTeX's (the math font's counts it, for MathML Core and LuaTeX: build/opentype.py)
        w = self.em(self.hmtx[f"{name}.katex" if f"{name}.katex" in self.hmtx.metrics and name.startswith(INTEGRALS) else name][0])
        extra = []
        ic = self.em(self.italics.get(name, 0))
        if ic:
            extra.append(f"ic:{number(ic)}")
        if skew and name in self.accents:
            # MathJax shifts an accent by the skews' difference and a share of the base's italic correction; the
            # skew is the rest of where the accent goes, from the glyph's middle
            sk = self.em(self.accents[name] - self.hmtx[name][0] / 2) - SKEW_IC_FACTOR * ic
            if round(sk, 3):
                extra.append(f"sk:{number(sk)}")
        extra.append(f"p:{json.dumps(self.path(name))}")
        out = f"[{number(h)},{number(d)},{number(w)},{{{','.join(extra)}}}]"
        self.cache[name, skew] = out
        return out


def parts_of(assembly, glyphs: Glyphs, vertical: bool):
    """
    An assembly as MathJax's stretch: [top, extender, bottom, middle]
    (vertical) or [left, extender, right, middle] (horizontal), glyph names
    or None, from the MATH table's parts (bottom to top, left to right).
    """
    parts = [(p.glyph, bool(p.PartFlags & 1)) for p in assembly.PartRecords]
    extenders = {g for g, ext in parts if ext}
    assert len(extenders) == 1, f"assembly with extenders {extenders}"
    ext = extenders.pop()
    # ends that are the extender itself (a bar's) are no ends
    ends = [g for g, is_ext in parts if not is_ext and g != ext]
    first, last, middle = None, None, None
    if parts[0][0] in ends and not parts[0][1]:
        first = parts[0][0]
    if parts[-1][0] in ends and not parts[-1][1]:
        last = parts[-1][0]
    inner = [g for g in ends[1 if first else 0: len(ends) - (1 if last else 0)]]
    assert len(inner) <= 1, f"assembly with middles {inner}"
    middle = inner[0] if inner else None
    # MathJax: the top (vertical) or left (horizontal) piece first
    return [last, ext, first, middle] if vertical else [first, ext, last, middle]


def build() -> None:
    font = TTFont(FONT)
    glyphs = Glyphs(font)
    upem, katex_em = glyphs.upem, TTFont(KATEX_FONT)["head"].unitsPerEm
    katex = lambda v: v * katex_em / upem  # noqa: E731  (KaTeX's em in Inter's)
    cmap = {cp: g for cp, g in font.getBestCmap().items() if not 0xE000 <= cp <= 0xF8FF}
    by_glyph = {}
    for cp, g in cmap.items():
        by_glyph.setdefault(g, []).append(cp)

    accents = {cp: cmap[accent] for cp, accent in ACCENTS.items() if accent in cmap and cp not in cmap}
    chars = {"normal": {cp: glyphs.data(g) for cp, g in sorted({**cmap, **accents}.items())}}
    sizes_needed = 1

    # the AMS designs where TeX asks for a variant form (\varnothing…): the AMS role's glyphs (build/opentype.py)
    ams = {}
    for record in font["GSUB"].table.FeatureList.FeatureRecord:
        if record.FeatureTag == "KTXA":
            for i in record.Feature.LookupListIndex:
                for st in font["GSUB"].table.LookupList.Lookup[i].SubTable:
                    ams.update(st.mapping)
    chars["-tex-variant"] = {cp: glyphs.data(ams[g]) for cp, g in sorted(cmap.items()) if g in ams and cp > 0x7F}

    variants = font["MATH"].table.MathVariants
    delimiters, pieces = {}, {v: {} for v in STRETCH[1:]}
    sized = {}  # size variant index → {cp: data}

    def stretchy(cp: int, base: str, construction, vertical: bool) -> dict:
        records = [(r.VariantGlyph, r.AdvanceMeasurement) for r in construction.MathGlyphVariantRecord]
        b = glyphs.bounds(base)
        h, d = (glyphs.em(b[3]), glyphs.em(-b[1])) if b else (0, 0)
        entry = {"dir": "V" if vertical else "H"}
        if not records:
            records = [(base, (b[3] - b[1]) if vertical else glyphs.hmtx[base][0])]
        if cp in BIG_OPERATORS:
            # text style: the normal variant's; display style: -largeop's
            entry["sizes"] = [glyphs.em(records[0][1]), glyphs.em(records[1][1])]
            entry["variants"] = [0, 2]
            sized.setdefault(2, {})[cp] = glyphs.data(records[1][0])
        else:
            entry["sizes"] = [glyphs.em(a) for _, a in records]
            for i, (g, _) in enumerate(records[1:], 1):
                sized.setdefault(i, {})[cp] = glyphs.data(g)
        width = glyphs.em(glyphs.hmtx[base][0])
        if construction.GlyphAssembly:
            names = parts_of(construction.GlyphAssembly, glyphs, vertical)
            stretch, stretchv = [], []
            for name, variant in zip(names, ["-lf-tp", "-ext", "-rt-bt", "-mid"]):
                if name is None:
                    stretch.append(0)
                    stretchv.append(0)
                    continue
                pieces[variant][cp] = glyphs.data(name, skew=False)
                stretch.append(cp)
                stretchv.append(STRETCH.index(variant))
            while stretch and stretch[-1] == 0:
                stretch.pop()
                stretchv.pop()
            entry["stretch"], entry["stretchv"] = stretch, stretchv
            if vertical:
                width = max(glyphs.em(glyphs.hmtx[n][0]) for n in names if n)
            else:
                e = glyphs.bounds(names[1])
                entry["hd"] = [glyphs.em(e[3]), glyphs.em(-e[1])]
        entry["HDW"] = [h, d, width]
        return entry

    for vertical, coverage, constructions in ((True, variants.VertGlyphCoverage, variants.VertGlyphConstruction),
                                             (False, variants.HorizGlyphCoverage, variants.HorizGlyphConstruction)):
        for base, construction in zip(coverage.glyphs, constructions):
            for cp in by_glyph.get(base, []):
                delimiters[cp] = stretchy(cp, base, construction, vertical)
    # the line accents, drawn out from their bar
    for cp, bar in LINES.items():
        if bar in delimiters and cp not in delimiters:
            delimiters[cp] = {**delimiters[bar], "c": bar}
    sizes_needed = max(len(e["sizes"]) for e in delimiters.values())

    size_variants = ["normal", "-smallop", "-largeop", *(f"-size{i}" for i in range(3, sizes_needed))]
    for i, table in sorted(sized.items()):
        chars[size_variants[i]] = dict(sorted(table.items()))
    for variant, table in pieces.items():
        chars[variant] = dict(sorted(table.items()))

    mc = font["MATH"].table.MathConstants
    c = lambda name: glyphs.em(getattr(mc, name).Value)  # noqa: E731
    params = {
        "x_height": glyphs.em(font["OS/2"].sxHeight),
        "quad": 1,
        "num1": c("FractionNumeratorDisplayStyleShiftUp"),
        "num2": c("FractionNumeratorShiftUp"),
        "num3": c("StackTopShiftUp"),
        "denom1": c("FractionDenominatorDisplayStyleShiftDown"),
        "denom2": c("FractionDenominatorShiftDown"),
        "sup1": c("SuperscriptShiftUp"),
        "sup2": c("SuperscriptShiftUp"),
        "sup3": c("SuperscriptShiftUpCramped"),
        "sub1": c("SubscriptShiftDown"),
        "sub2": katex(SUB2),
        "sup_drop": c("SuperscriptBaselineDropMax"),
        "sub_drop": c("SubscriptBaselineDropMin"),
        "delim1": katex(DELIM1),
        "delim2": katex(DELIM2),
        "axis_height": c("AxisHeight"),
        "rule_thickness": c("FractionRuleThickness"),
        "big_op_spacing1": c("UpperLimitGapMin"),
        "big_op_spacing2": c("LowerLimitGapMin"),
        "big_op_spacing3": c("UpperLimitBaselineRiseMin"),
        "big_op_spacing4": c("LowerLimitBaselineDropMin"),
        "big_op_spacing5": katex(BIG_OP_SPACING5),
        "surd_height": c("RadicalRuleThickness"),
        # an accent's gap above its base, in rule thicknesses: the one the font's accents keep above the x-height
        "separation_factor": (glyphs.bounds(cmap[0x2C6])[1] - font["OS/2"].sxHeight) / getattr(mc, "FractionRuleThickness").Value,
        "scriptspace": c("SpaceAfterScript"),
        "nulldelimiterspace": katex(NULL_DELIMITER),
        "delimitershortfall": katex(DELIMITER_SHORTFALL),
        "extra_ic": katex(EXTRA_IC),
    }

    def table(entries: dict) -> str:
        return "{\n" + ",\n".join(f"  {cp}:{data}" for cp, data in entries.items()) + "\n}"

    def delimiter(e: dict) -> str:
        fields = []
        for k, v in e.items():
            if k == "dir":
                fields.append(f"dir:{v}")
            elif k in ("sizes", "HDW", "hd"):
                fields.append(f"{k}:[{','.join(number(x) for x in v)}]")
            else:
                fields.append(f"{k}:{json.dumps(v)}")
        return "{" + ",".join(fields) + "}"

    variant_names = list(chars)
    extra_variants = [*size_variants[3:], "-lf-tp", "-rt-bt", "-ext", "-mid"]
    js = TEMPLATE.substitute(
        version=VERSION,
        name=NAME,
        params=json.dumps({k: round(v, 4) for k, v in params.items()}),
        variants=json.dumps([[v, "normal"] for v in extra_variants]),
        css=json.dumps({v: ["serif", False, False] for v in extra_variants}),
        sizes=json.dumps(size_variants),
        stretch=json.dumps(STRETCH),
        ids=json.dumps({v: f"V{i}" for i, v in enumerate(variant_names)}),
        delimiters="{\n" + ",\n".join(f"  {cp}:{delimiter(e)}" for cp, e in sorted(delimiters.items())) + "\n}",
        chars="{\n" + ",\n".join(f"{json.dumps(v)}:{table(t)}" for v, t in chars.items()) + "\n}",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(js)
    print(f"{OUT.relative_to(ROOT)}: {len(chars['normal'])} characters, {len(delimiters)} delimiters, "
          f"{len(size_variants)} sizes, {OUT.stat().st_size / 1024:.0f} KB")


class Template:
    def __init__(self, text: str):
        self.text = text

    def substitute(self, **values) -> str:
        return re.sub(r"\$\{(\w+)\}", lambda m: str(values[m.group(1)]), self.text)


TEMPLATE = Template("""\
/*!
 * Inter Math ${version} for MathJax 4 (SVG output): the OpenType math font at its Regular weight, as MathJax's font
 * data. SIL Open Font License 1.1. Made by build/mathjax.py (github.com/lucpotage/inter-math): don't edit.
 *
 * MathJax loads it from the package's URL (it takes <url>/svg.js), with a component that has no font of its own:
 *   window.MathJax = { output: { font: "https://cdn.jsdelivr.net/npm/inter-math@${version}" } };
 *   <script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg-nofont.js"></script>
 */
(() => {
  "use strict";
  const global = MathJax._.components.global;
  const { SvgFontData } = MathJax._.output.svg.FontData;
  const { FontData } = MathJax._.output.common.FontData;
  const { V, H } = MathJax._.output.common.Direction;

  class InterMathFont extends SvgFontData {
    constructor(options = {}) {
      super(options);
      const ids = this.constructor.variantCacheIds;
      for (const variant of Object.keys(this.variant)) this.variant[variant].cacheID = "IM-" + (ids[variant] || "N");
    }
  }
  InterMathFont.NAME = "InterMath";
  InterMathFont.OPTIONS = { ...SvgFontData.OPTIONS };
  // the size variants (the MATH table's variants, by index) and the pieces' (-lf-tp top or left, -ext the extender,
  // -rt-bt bottom or right, -mid middle) take what they don't have from normal; \\mathcal falls back as MathJax's
  // fonts do, through script
  InterMathFont.defaultVariants = [
    ...FontData.defaultVariants.filter(([name]) => !/^-tex-(bold-)?calligraphic$/.test(name)),
    ["-tex-calligraphic", "script"],
    ["-tex-bold-calligraphic", "bold-script"],
    ...${variants},
  ];
  InterMathFont.defaultCssFonts = { ...FontData.defaultCssFonts, ...${css} };
  InterMathFont.defaultAccentMap = { ...FontData.defaultAccentMap };
  InterMathFont.defaultParams = { ...FontData.defaultParams, ...${params} };
  InterMathFont.defaultSizeVariants = ${sizes};
  InterMathFont.defaultStretchVariants = ${stretch};
  InterMathFont.variantCacheIds = ${ids};
  InterMathFont.defaultDelimiters = ${delimiters};
  InterMathFont.defaultChars = ${chars};

  global.combineWithMathJax({ _: { output: { fonts: { "${name}": { svg_ts: { InterMathFont } } } } } });
  if (MathJax.startup) {
    global.combineDefaults(MathJax, "config", { output: { font: "[${name}]" }, svg: { fontData: InterMathFont } });
  }
})();
""")


if __name__ == "__main__":
    build()
