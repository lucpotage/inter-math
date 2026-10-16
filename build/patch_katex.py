"""
Inter Math's KaTeX patch (patches/katex@0.19.0.patch): hooks for fonts other than
Computer Modern, used by src/index.ts. With no font set they change nothing:
KaTeX's output stays the same.

- __setGlobalMetrics: TeX's parameters (rule thicknesses, x-height…), and
  the font's own lines, KaTeX's (TeX's) without them:
  - underlineGap, underlineRuleThickness: \\underline (TeX's: three rules
    under the text, one rule thick);
  - overlineGap, overlineRuleThickness: \\overline (three rules above it,
    one rule thick);
  - soutRuleThickness, soutShift: \\sout (0.08 em, half the x-height up);
  - cancelRuleThickness: \\cancel \\bcancel \\xcancel (0.046 em);
  - phaseRuleThickness: \\phase (0.6 pt, its angle's stroke fixed);
  - ruleSpacing: the unit TeX's vertical spaces count in (a fraction's
    clearances, the surd's, a script's sub and sup apart, \\angl's), apart
    from the rules' own thickness (TeX's: the rule's, which a font whose
    rules follow its weight would space out at heavy weights);
- __setComposedText: accented letters the font draws precomposed (\\'{a}
  is á, \\r{A} is Å, a typed é stays é), which KaTeX otherwise builds from
  the letter and an accent;
- __setItalicAccents: a math accent over an italic letter (\\hat{x},
  \\mathit, \\boldsymbol) from the italic font, as the font's text sets
  them (KaTeX sets them upright over every letter);
- __setRootClasses: classes on the math KaTeX lays out from then on (its
  `.katex` element), for the font's CSS (Inter Math's triangle arrowheads);
- __setRuleImages: the rules (fraction bars, \\overline, \\underline,
  \\hline) drawn as images, as thick as they are: a browser rounds a
  border's width to whole device pixels (down, or up to one), which set a
  light weight's rules off the glyphs and surds beside them (a quarter
  thinner at 1.4 pixels);
- __setSurd: the surds of \\sqrt and where the radicand starts; a font that
  draws its surd at any height (anyHeight) gets one as tall as its radicand
  needs past 1 em, never KaTeX's four sizes;
- __setSvgDesign: SVG images (stretchy arrows, \\vec, the tall | ‖ ( [ KaTeX
  draws as one image of any height, the straight stem it draws between a
  tall brace's pieces); with a design set, a path that is still KaTeX's
  carries data-katex-path (its name), for the workbench to count, and a
  stacked delimiter is as tall as needed (not in steps of its repeated
  piece); a delimiter the design draws at any height (anyHeight) is, past
  its text size, one image as tall as needed instead of KaTeX's four sizes
  (those that never stack stop at the largest). Content growing with the
  font's weight made KaTeX's delimiters and surds jump a size;
- __setSizedDelimiters: delimiters KaTeX always stacks (\\lgroup,
  \\lmoustache…) that the font draws at the four sizes, taken from its Size
  fonts first, as ( [ { are.

To redo it (another KaTeX version, another hook), from the project's root,
with a directory to edit KaTeX's files in:

    pnpm patch katex@<version> --edit-dir <dir> --ignore-existing
    build/.venv/bin/python build/patch_katex.py <dir>
    pnpm patch-commit <dir>

An app that uses Inter Math applies the same patch to its own KaTeX.

It patches dist/katex.mjs and dist/katex.js (what "katex" resolves to), and
fails on any spot it doesn't find exactly once.
"""

import sys
from pathlib import Path

root = Path(sys.argv[1]) / "dist"

GLOBAL = """
// inter-math patch: a font other than Computer Modern sets its own TeX parameters
// (rule thicknesses, x-height…), as {{name: [text, script, scriptscript]}}; null
// restores KaTeX's.
{mut} globalMetricsOverrides = {{}};
function setGlobalMetrics(overrides) {{
  globalMetricsOverrides = overrides || {{}};
  for (const sizeIndex of Object.keys(fontMetricsBySizeIndex)) delete fontMetricsBySizeIndex[sizeIndex];
}}
"""

SURD = """// inter-math patch: a font other than Computer Modern draws its own surds:
// {{path(name, extraVinculum, viewBoxHeight, hLinePad) → SVG path (viewBox units),
// box(name, height) → {{minWidth, advanceWidth}} (em), anyHeight: true when it
// draws one at any height: a surd then is as tall as its radicand needs, never
// shorter than the normal one, and KaTeX's four sizes never come (a radicand
// growing with the font's weight made the surd jump from one to the next)}};
// null restores KaTeX's.
{mut} surdDesign = null;
function setSurd(design) {{
  surdDesign = design || null;
}}
{decl} surdBox = function (name, minWidth, advanceWidth, height) {{
  return surdDesign ? surdDesign.box(name, height) : {{minWidth, advanceWidth}};
}};
"""

LINES = """// inter-math patch: the lines a font sets itself (__setGlobalMetrics): \\cancel's stroke,
// and \\phase's angle `t` thick (viewBox units), its diagonal as thick across, its top cut level.
{decl} cancelStroke = function (options) {{
  {decl} t = options.fontMetrics().cancelRuleThickness;
  return t ? makeEm(t) : "0.046em";
}};
{decl} phasePathOf = function (y, t) {{
  {decl} x = y / 2; // the angle's top, as KaTeX's: its diagonal rises 2 for 1 across
  {decl} h = t * Math.sqrt(5) / 2; // the inner edge, t from the outer one across, along a level line
  return "M400000 " + y + " H0 L" + x + " 0 H" + (x + h) + " L" + (h + t / 2) + " " + (y - t) + " H400000z";
}};
"""

COMPOSED = """// inter-math patch: a font other than Computer Modern sets an accented letter as its own
// precomposed glyph when it has one (\\'{{a}} is á, \\r{{A}} is Å, \\acute{{a}} and a typed á in math
// its italic á) and keeps the ones typed in text as they are (KaTeX builds them all from the
// letter and an accent); null restores KaTeX's. \\bar isn't composed: it is drawn wider than a
// macron, as TeX's is.
{mut} composedText = null;
function setComposedText(chars) {{
  composedText = chars ? new Set(chars) : null;
}}
{decl} ACCENT_MARKS = {{
  "\\\\'": "\\u0301", "\\\\`": "\\u0300", "\\\\^": "\\u0302", "\\\\~": "\\u0303", "\\\\=": "\\u0304", "\\\\u": "\\u0306",
  "\\\\.": "\\u0307", '\\\\"': "\\u0308", "\\\\c": "\\u0327", "\\\\r": "\\u030a", "\\\\H": "\\u030b", "\\\\v": "\\u030c",
  "\\\\acute": "\\u0301", "\\\\grave": "\\u0300", "\\\\hat": "\\u0302", "\\\\tilde": "\\u0303", "\\\\breve": "\\u0306",
  "\\\\dot": "\\u0307", "\\\\ddot": "\\u0308", "\\\\mathring": "\\u030a", "\\\\check": "\\u030c"
}};
{decl} composedAccent = function (label, base) {{
  if (!composedText || !ACCENT_MARKS[label]) return null;
  {decl} letter = base && base.type === "ordgroup" && base.body.length === 1 ? base.body[0] : base;
  if (!letter || letter.type !== "mathord" && letter.type !== "textord" || letter.text.length !== 1) return null;
  {decl} text = (letter.text + ACCENT_MARKS[label]).normalize("NFC");
  return text.length === 1 && composedText.has(text) ? {{
    type: letter.type,
    mode: letter.mode,
    loc: letter.loc,
    text: text
  }} : null;
}};
"""

ITALIC = """// inter-math patch: a font other than Computer Modern sets a math accent over an italic letter
// from its italic font (the letter's), as its text does (KaTeX sets them upright over every
// letter); false restores KaTeX's.
{mut} italicAccents = false;
function setItalicAccents(on) {{
  italicAccents = !!on;
}}
{decl} ITALIC_ACCENT_LABELS = new Set(["\\\\acute", "\\\\grave", "\\\\ddot", "\\\\tilde", "\\\\bar", "\\\\breve", "\\\\check", "\\\\hat", "\\\\dot", "\\\\mathring"]);
// an italic letter's class → the italic font its accent is set from
{decl} ITALIC_LETTERS = {{mathnormal: "Math-Italic", mathit: "Main-Italic", boldsymbol: "Math-BoldItalic"}};
{decl} italicAccentFont = function (label, symbol) {{
  if (!italicAccents || !ITALIC_ACCENT_LABELS.has(label) || !symbol) return null;
  for ({decl} letterClass in ITALIC_LETTERS) {{
    if (symbol.hasClass(letterClass)) return [ITALIC_LETTERS[letterClass], letterClass];
  }}
  return null;
}};
"""


ROOT = """// inter-math patch: classes a font other than Computer Modern puts on the math laid out from
// now on (its .katex element: the font's CSS reads them, as its stylistic sets); null clears them.
{mut} rootClasses = [];
function setRootClasses(classes) {{
  rootClasses = classes || [];
}}
"""

RULES = """// inter-math patch: a font other than Computer Modern draws its rules (fraction bars,
// \\overline, \\underline, \\hline) as images, as thick as they are: a browser draws a border a
// whole number of device pixels thick (its width rounded down, or up to one pixel), off the glyphs
// and surds beside it (a light weight's rule 1.4 pixels thick came out 1 thick); false restores
// KaTeX's borders. The image reaches RULE_PAD over and under its rule: a browser draws an image's
// box a whole number of pixels tall too, its content scaled to it, which leaves the rule's
// thickness all but untouched only in a box much taller than it.
{mut} ruleImages = false;
function setRuleImages(on) {{
  ruleImages = !!on;
}}
{decl} RULE_PAD = 0.5;
{decl} ruleImage = function (line) {{
  {decl} units = function (em) {{
    return Math.round(em * 10000) / 10;
  }};
  {decl} height = 2 * RULE_PAD + line.height;
  line.style.borderBottomWidth = "0";
  line.style.position = "relative";
  line.children.push(new SvgNode([new PathNode("rule", "M0 " + units(RULE_PAD) + "H400000V" + units(RULE_PAD + line.height) + "H0Z")], {{
    "width": "400em",
    "height": makeEm(height),
    "style": "bottom:" + makeEm(-RULE_PAD) + ";height:" + makeEm(height),
    "viewBox": "0 0 400000 " + units(height),
    "preserveAspectRatio": "xMinYMin slice"
  }}));
}};
"""


def mutable(decl: str) -> str:
    """How to declare what a hook sets again (the CommonJS build declares with const)."""
    return "let" if decl == "const" else decl


def replace(src: str, old: str, new: str) -> str:
    assert src.count(old) == 1, f"expected once: {old[:60]!r} ({src.count(old)})"
    return src.replace(old, new)


def patch(name: str, decl: str, esm: bool) -> None:
    path = root / name
    s = path.read_text()
    v = decl
    # global metrics
    s = replace(s, f"{v} fontMetricsBySizeIndex = {{}};\n", f"{v} fontMetricsBySizeIndex = {{}};\n" + GLOBAL.format(decl=v, mut=mutable(v)))
    s = replace(s, "cssEmPerMu: sigmasAndXis.quad[sizeIndex] / 18", "cssEmPerMu: (globalMetricsOverrides.quad || sigmasAndXis.quad)[sizeIndex] / 18")
    s = replace(s, "metrics[key] = sigmasAndXis[key][sizeIndex];", "metrics[key] = (globalMetricsOverrides[key] || sigmasAndXis[key])[sizeIndex];")
    # parameters TeX lacks (the font's underline) come along with its own
    s = replace(s, f"for ({v} key of Object.keys(sigmasAndXis)) {{", f"for ({v} key of Object.keys(Object.assign({{}}, sigmasAndXis, globalMetricsOverrides))) {{")
    # \\underline (and \\underbar): the font's gap and thickness, TeX's 3θ and θ without them
    s = replace(
        s,
        f'{v} line = makeLineSpan("underline-line", options);',
        f'// inter-math patch: the font\'s own underline when it sets one\n    {v} underline = options.fontMetrics();\n    {v} line = makeLineSpan("underline-line", options, underline.underlineRuleThickness);',
    )
    s = replace(
        s,
        '        size: defaultRuleThickness\n      }, {\n        type: "elem",\n        elem: line\n      }, {\n        type: "kern",\n        size: 3 * defaultRuleThickness\n      }, {',
        '        size: underline.underlineRuleThickness || defaultRuleThickness\n      }, {\n        type: "elem",\n        elem: line\n      }, {\n        type: "kern",\n        size: underline.underlineGap || 3 * defaultRuleThickness\n      }, {',
    )
    # \\overline: the font's gap and thickness, TeX's 3θ and θ without them
    s = replace(
        s,
        f'{v} line = makeLineSpan("overline-line", options);',
        f'// inter-math patch: the font\'s own overline when it sets one\n    {v} overline = options.fontMetrics();\n    {v} line = makeLineSpan("overline-line", options, overline.overlineRuleThickness);',
    )
    s = replace(
        s,
        '        size: 3 * defaultRuleThickness\n      }, {\n        type: "elem",\n        elem: line\n      }, {\n        type: "kern",\n        size: defaultRuleThickness\n      }]',
        '        size: overline.overlineGap || 3 * defaultRuleThickness\n      }, {\n        type: "elem",\n        elem: line\n      }, {\n        type: "kern",\n        size: overline.overlineRuleThickness || defaultRuleThickness\n      }]',
    )
    # \\sout: the font's thickness and height
    s = replace(
        s,
        "    imgShift = -0.5 * options.fontMetrics().xHeight;\n",
        "    imgShift = -0.5 * options.fontMetrics().xHeight;\n"
        "    // inter-math patch: the font's own strike-through when it sets one\n"
        "    if (options.fontMetrics().soutRuleThickness) {\n"
        "      img.height = options.fontMetrics().soutRuleThickness / scale;\n"
        "      img.style.borderBottomWidth = makeEm(img.height);\n"
        "      imgShift = -options.fontMetrics().soutShift;\n"
        "    }\n",
    )
    # \\cancel \\bcancel \\xcancel: the font's stroke
    assert s.count('"stroke-width": "0.046em"') == 2
    s = s.replace('"stroke-width": "0.046em"', '"stroke-width": cancelStroke(options)')
    # \\phase: the font's line, its angle as thick across
    s = replace(s, f"{v} lineWeight = calculateSize({{", f"{v} lineWeight = options.fontMetrics().phaseRuleThickness || calculateSize({{")
    s = replace(
        s,
        f"{v} path = phasePath(viewBoxHeight);",
        f"{v} path = options.fontMetrics().phaseRuleThickness ? phasePathOf(viewBoxHeight, 1000 * lineWeight * scale) : phasePath(viewBoxHeight);",
    )
    s = replace(s, "class PathNode {", LINES.format(decl=v) + "class PathNode {")
    # accented letters: the font's precomposed ones
    s = replace(s, "// Text-mode accents\ndefineFunction({", COMPOSED.format(decl=v, mut=mutable(v)) + ITALIC.format(decl=v, mut=mutable(v)) + "// Text-mode accents\ndefineFunction({")
    # a math accent over an italic letter: the italic font's
    s = replace(
        s,
        "      accent = makeOrd({\n        type: \"textord\",\n        mode: group.mode,\n        text: group.label\n      }, options);",
        "      // inter-math patch: over an italic letter, the font's italic accent\n"
        f"      {v} italicFont = mustShift ? italicAccentFont(group.label, getBaseSymbol(body)) : null;\n"
        "      accent = italicFont ? makeSymbol(group.label, italicFont[0], group.mode, options, [\"mord\", italicFont[1]]) : makeOrd({\n        type: \"textord\",\n        mode: group.mode,\n        text: group.label\n      }, options);",
    )
    s = replace(
        s,
        "    return {\n      type: \"accent\",\n      mode: mode,\n      label: context.funcName,\n      isStretchy: false,",
        "    // inter-math patch: the font's own precomposed letter, when it has one\n"
        f"    {v} composed = composedAccent(context.funcName, base);\n"
        "    if (composed) return composed;\n"
        "    return {\n      type: \"accent\",\n      mode: mode,\n      label: context.funcName,\n      isStretchy: false,",
    )
    s = replace(
        s,
        "context.funcName === \"\\\\widecheck\";\n    return {\n      type: \"accent\",\n      mode: context.parser.mode,",
        "context.funcName === \"\\\\widecheck\";\n"
        "    // inter-math patch: the font's own precomposed letter, when it has one\n"
        f"    {v} composed = composedAccent(context.funcName, base);\n"
        "    if (composed) return composed;\n"
        "    return {\n      type: \"accent\",\n      mode: context.parser.mode,",
    )
    # a letter typed with its accent in math: KaTeX splits it, the font's precomposed one comes back
    s = replace(
        s,
        "        symbol = {\n          type: \"accent\",\n          mode: this.mode,\n          loc: SourceLocation.range(nucleus),\n          label: command,",
        "        symbol = composedAccent(command, symbol) || {\n          type: \"accent\",\n          mode: this.mode,\n          loc: SourceLocation.range(nucleus),\n          label: command,",
    )
    s = replace(
        s,
        "hasOwnProperty.call(unicodeSymbols, text[0]) && !",
        "hasOwnProperty.call(unicodeSymbols, text[0]) && !(composedText && this.mode === \"text\" && composedText.has(text[0])) && !",
    )
    # the root's classes
    build_tree = "var buildTree = function buildTree(" if esm else "const buildTree = function ("
    s = replace(s, build_tree, ROOT.format(decl=v, mut=mutable(v)) + build_tree)
    assert s.count('makeSpan(["katex"], [') == 3
    s = s.replace('makeSpan(["katex"], [', 'makeSpan(["katex", ...rootClasses], [')
    # TeX's vertical spaces in the font's spacing unit (ruleSpacing) when it sets one, the rules keeping their thickness
    s = replace(
        s,
        "    ruleSpacing = rule.height;",
        "    // inter-math patch: the font's spacing unit (TeX's: the rule's thickness), but for a bar of a given size\n"
        "    ruleSpacing = group.barSize ? rule.height : options.fontMetrics().ruleSpacing || rule.height;",
    )
    s = replace(
        s,
        "    ruleSpacing = options.fontMetrics().defaultRuleThickness;",
        "    ruleSpacing = options.fontMetrics().ruleSpacing || options.fontMetrics().defaultRuleThickness;",
    )
    s = replace(
        s,
        f"    {mutable(v)} phi = theta;",
        f"    // inter-math patch: the clearance in the font's spacing unit (TeX's: the rule's thickness), the vinculum as thick\n"
        f"    // as the rule\n"
        f"    {v} spacing = metrics.ruleSpacing || theta;\n"
        f"    {mutable(v)} phi = spacing;",
    )
    s = replace(s, f"    {mutable(v)} lineClearance = theta + phi / 4;", f"    {mutable(v)} lineClearance = spacing + phi / 4;")
    # a surd as tall as its radicand: TeX's display clearance in every style
    s = replace(
        s,
        "    if (options.style.id < Style$1.TEXT.id) {\n      phi = options.fontMetrics().xHeight;\n    }" if esm else "    if (options.style.id < src_Style.TEXT.id) {\n      phi = options.fontMetrics().xHeight;\n    }",
        ("    // inter-math patch: a surd drawn as tall as its radicand needs (anyHeight) gets no white from a size taller\n"
         "    // than needed, which TeX's text clearance counts on: TeX's display clearance in every style\n"
         "    if (options.style.id < Style$1.TEXT.id || surdDesign && surdDesign.anyHeight) {\n      phi = options.fontMetrics().xHeight;\n    }")
        if esm else
        ("    // inter-math patch: a surd drawn as tall as its radicand needs (anyHeight) gets no white from a size taller\n"
         "    // than needed, which TeX's text clearance counts on: TeX's display clearance in every style\n"
         "    if (options.style.id < src_Style.TEXT.id || surdDesign && surdDesign.anyHeight) {\n      phi = options.fontMetrics().xHeight;\n    }"),
    )
    # the white TeX keeps over a surd's vinculum (a kern as thick as it): the font's spacing unit
    s = replace(
        s,
        '        type: "kern",\n        size: ruleWidth\n      }]',
        '        type: "kern",\n        // inter-math patch: the font\'s spacing unit (TeX\'s: the vinculum\'s thickness)\n'
        '        size: metrics.ruleSpacing || ruleWidth\n      }]',
    )
    s = replace(
        s,
        f"      {v} ruleWidth = metrics.defaultRuleThickness;",
        f"      // inter-math patch: the font's spacing unit (TeX's: the rule's thickness)\n"
        f"      {v} ruleWidth = metrics.ruleSpacing || metrics.defaultRuleThickness;",
    )
    s = replace(
        s,
        "      topPad = 4 * ruleThickness; // gap = 3 × line, plus the line itself.",
        "      // inter-math patch: the gap in the font's spacing unit (TeX's: the rule's thickness)\n"
        "      topPad = 3 * (options.fontMetrics().ruleSpacing || ruleThickness) + ruleThickness; // gap = 3 × line, plus the line itself.",
    )
    # surds
    sqrt_svg = "var sqrtSvg = function sqrtSvg(" if esm else "const sqrtSvg = function ("
    s = replace(s, sqrt_svg, SURD.format(decl=v, mut=mutable(v)) + sqrt_svg)
    s = replace(
        s,
        f"{v} path = sqrtPath(sqrtName, extraVinculum, viewBoxHeight);",
        f"{v} path = surdDesign ? surdDesign.path(sqrtName, extraVinculum, viewBoxHeight, hLinePad) : sqrtPath(sqrtName, extraVinculum, viewBoxHeight);",
    )
    s = replace(
        s,
        '    span.style.minWidth = "0.853em";\n    advanceWidth = 0.833 / sizeMultiplier; // from the font.',
        f'    {v} box = surdBox("sqrtMain", 0.853, 0.833);\n    span.style.minWidth = makeEm(box.minWidth);\n    advanceWidth = box.advanceWidth / sizeMultiplier; // from the font.',
    )
    s = replace(
        s,
        '    span.style.minWidth = "1.02em";\n    advanceWidth = 1.0 / sizeMultiplier; // 1.0 from the font.',
        f'    {v} box = surdBox("sqrtSize" + delim.size, 1.02, 1.0);\n    span.style.minWidth = makeEm(box.minWidth);\n    advanceWidth = box.advanceWidth / sizeMultiplier; // 1.0 from the font.',
    )
    s = replace(
        s,
        '    span.style.minWidth = "0.742em";\n    advanceWidth = 1.056;',
        f'    {v} box = surdBox("sqrtTall", 0.742, 1.056, height);\n    span.style.minWidth = makeEm(box.minWidth);\n    advanceWidth = box.advanceWidth;',
    )
    # a surd at any height, for a font that draws one: the normal one under 1 em, else as tall as needed
    s = replace(
        s,
        f'{v} delim = traverseSequence("\\\\surd", height * newOptions.sizeMultiplier, stackLargeDelimiterSequence, newOptions);',
        f"// inter-math patch: a font that draws its surd at any height sets the normal one up to 1 em, then one as tall\n"
        f"  // as needed (KaTeX's own sizes: a radicand growing with the weight made the surd jump)\n"
        f'  {v} delim = surdDesign && surdDesign.anyHeight ? {{type: height < 1.0 ? "small" : "stack"}} : traverseSequence("\\\\surd", height * newOptions.sizeMultiplier, stackLargeDelimiterSequence, newOptions);',
    )
    # rules: images as thick as they are, for a font that asks (a dashed \\hdashline keeps its border)
    line_span = "var makeLineSpan = function makeLineSpan(" if esm else "const makeLineSpan = function ("
    s = replace(s, line_span, RULES.format(decl=v, mut=mutable(v)) + line_span)
    s = replace(
        s,
        "  line.style.borderBottomWidth = makeEm(line.height);\n  line.maxFontSize = 1.0;\n",
        "  line.style.borderBottomWidth = makeEm(line.height);\n  line.maxFontSize = 1.0;\n"
        "  // inter-math patch: the rule as an image when the font asks\n"
        '  if (ruleImages && className !== "katex-hdashline") ruleImage(line);\n',
    )
    # exports
    s = replace(s, "  __setFontMetrics: setFontMetrics,\n", "  __setFontMetrics: setFontMetrics,\n  // inter-math patch\n  __setGlobalMetrics: setGlobalMetrics,\n  __setSurd: setSurd,\n  __setComposedText: setComposedText,\n  __setItalicAccents: setItalicAccents,\n  __setRootClasses: setRootClasses,\n  __setRuleImages: setRuleImages,\n")
    if esm:
        s = replace(s, "setFontMetrics as __setFontMetrics, ", "setFontMetrics as __setFontMetrics, setGlobalMetrics as __setGlobalMetrics, setSurd as __setSurd, setComposedText as __setComposedText, setItalicAccents as __setItalicAccents, setRootClasses as __setRootClasses, setRuleImages as __setRuleImages, ")
    path.write_text(s)
    print("patched", name)

SVG = """// inter-math patch: a font other than Computer Modern draws its own SVG images:
// {{path(name) → SVG path (or undefined: KaTeX's), static(name) → [path name,
// width, height] of a fixed-size image (or undefined), image(label, data) →
// the katexImagesData entry of a stretchy one, wide(label, pathName) → [path
// name, viewBox width, viewBox height, height (em)] of a wide accent's box,
// tall(label, height) → [path, width] of a tall delimiter drawn as one image,
// inner(ch, height) → [path, width (em)] of the straight piece between a
// tall delimiter's glyphs, as wide as they are at the font's weight (or
// undefined), anyHeight(delim) → the image's name of a delimiter it draws at
// any height past its text size (or undefined), largest → the height (em)
// where those that never stack stop}};
// null restores KaTeX's.
{mut} svgDesign = null;
function setSvgDesign(design) {{
  svgDesign = design || null;
}}
{decl} svgDesignPath = function (name) {{
  return svgDesign && svgDesign.path(name) || path[name];
}};
"""


def patch_svg(name: str, decl: str, esm: bool, esc: str) -> None:
    p = root / name
    s = p.read_text()
    s = replace(s, "class PathNode {", SVG.format(decl=decl, mut=mutable(decl)) + "class PathNode {")
    s = replace(
        s,
        'node.setAttribute("d", path[this.pathName]);',
        'node.setAttribute("d", svgDesignPath(this.pathName));\n'
        '      if (svgDesign && !svgDesign.path(this.pathName)) node.setAttribute("data-katex-path", this.pathName);',
    )
    s = replace(
        s,
        f"{esc}(path[this.pathName]) + \"\\\"/>\";",
        f"{esc}(svgDesignPath(this.pathName)) + \"\\\"\" + (svgDesign && !svgDesign.path(this.pathName) ? \" data-katex-path=\\\"\" + this.pathName + \"\\\"\" : \"\") + \"/>\";",
    )
    s = replace(s, f"{decl} _svgData$value = svgData[value],", f"{decl} _svgData$value = svgDesign && svgDesign.static(value) || svgData[value],")
    s = replace(s, "width = svgData.vec[1];", 'width = (svgDesign && svgDesign.static("vec") || svgData.vec)[1];')
    s = replace(s, f"{decl} data = katexImagesData[label];", f"{decl} data = svgDesign ? svgDesign.image(label, katexImagesData[label]) : katexImagesData[label];")
    # the wide accents (\\widehat \\widecheck \\widetilde \\utilde): the font's own box, so that a path can be
    # drawn for the width it is stretched to and its gap be on the base's side (\\widetilde and \\utilde
    # share KaTeX's paths)
    height = "_height" if esm else "height"
    s = replace(
        s,
        '          pathName = "tilde" + imgIndex;\n        }\n      }\n',
        '          pathName = "tilde" + imgIndex;\n        }\n      }\n'
        "      // inter-math patch: the font's own box for a wide accent: its path's name, its viewBox, its height\n"
        f"      {decl} fontWide = svgDesign && svgDesign.wide ? svgDesign.wide(label, pathName) : undefined;\n"
        "      if (fontWide) {\n"
        "        pathName = fontWide[0];\n"
        "        viewBoxWidth = fontWide[1];\n"
        "        viewBoxHeight = fontWide[2];\n"
        f"        {height} = fontWide[3];\n"
        "      }\n",
    )
    # \\left \\right past the text size: one image as tall as needed, for a delimiter the font draws at any height
    s = replace(
        s,
        f"{decl} delimType = traverseSequence(delim, height, sequence, options);",
        f"{mutable(decl)} delimType = traverseSequence(delim, height, sequence, options);\n"
        f"  // inter-math patch: a delimiter the font draws at any height, past its text size: one image as tall as needed\n"
        f"  // (KaTeX's sizes: content growing with the weight made it jump from one to the next), those that never stack\n"
        f"  // stopping at the largest as KaTeX's\n"
        f"  if (delimType.type === \"large\" && svgDesign && svgDesign.anyHeight(delim) && (sequence !== stackNeverDelimiterSequence || height < svgDesign.largest)) {{\n"
        f"    delimType = {{\n      type: \"stack\"\n    }};\n  }}",
    )
    s = replace(
        s,
        "  // Get the metrics of the four sections",
        f"  // inter-math patch: a delimiter the font draws as one image at any height\n"
        f"  {decl} fontLabel = svgDesign ? svgDesign.anyHeight(delim) : undefined;\n"
        f"  if (fontLabel) {{\n    svgLabel = fontLabel;\n  }}\n"
        f"  // Get the metrics of the four sections",
    )
    # a stacked delimiter as tall as needed, with a font that draws its own: not in steps of the repeated piece
    s = replace(
        s,
        f"{decl} realHeightTotal = minHeight + repeatCount * middleFactor * repeatHeightTotal;",
        f"// inter-math patch: with a font that draws its own tall delimiters (one image, or a straight piece between\n"
        f"  // glyphs, at any height), as tall as needed: in steps of the repeated piece, a delimiter around content growing\n"
        f"  // with the weight jumped a step at a time\n"
        f"  {decl} realHeightTotal = fontLabel ? heightTotal : svgDesign ? Math.max(minHeight, heightTotal) : minHeight + repeatCount * middleFactor * repeatHeightTotal;",
    )
    # a tall delimiter KaTeX draws as one image (| ‖ past the text size): the font's, as wide as it says
    s = replace(
        s,
        f"{decl} pathStr = tallDelim(svgLabel, Math.round(midHeight * 1000));",
        f"// inter-math patch: the font's own tall delimiter, and its width, when it draws one\n"
        f"    {decl} fontTall = svgDesign && svgDesign.tall ? svgDesign.tall(svgLabel, viewBoxHeight) : undefined;\n"
        f"    if (fontTall) viewBoxWidth = fontTall[1];\n"
        f"    {decl} pathStr = fontTall ? fontTall[0] : tallDelim(svgLabel, Math.round(midHeight * 1000));",
    )
    # the straight piece between a tall brace's glyphs: the font's
    s = replace(
        s,
        f"{decl} width = fontMetricsData['Size4-Regular'][ch.charCodeAt(0)] ?",
        f"{mutable(decl)} width = fontMetricsData['Size4-Regular'][ch.charCodeAt(0)] ?",
    )
    s = replace(
        s,
        f'{decl} path = new PathNode("inner", innerPath(ch, Math.round(1000 * height)));',
        f"// inter-math patch: the font's own straight piece between a tall delimiter's glyphs, as wide as they\n"
        f"  // are at its weight, when it draws one\n"
        f"  {decl} fontInner = svgDesign && svgDesign.inner ? svgDesign.inner(ch, Math.round(1000 * height)) : undefined;\n"
        f"  if (fontInner) width = fontInner[1];\n"
        f'  {decl} path = new PathNode("inner", fontInner ? fontInner[0] : innerPath(ch, Math.round(1000 * height)));',
    )
    s = replace(s, "  __setSurd: setSurd,\n", "  __setSurd: setSurd,\n  __setSvgDesign: setSvgDesign,\n")
    if esm:
        s = replace(s, "setSurd as __setSurd, ", "setSurd as __setSurd, setSvgDesign as __setSvgDesign, ")
    p.write_text(s)
    print("patched", name)


DELIMS = """// inter-math patch: a font other than Computer Modern draws some of the delimiters KaTeX
// always stacks (\\lgroup, \\lmoustache…) at the four sizes: their names and characters,
// taken from the Size fonts first, as ( [ {{ are; null restores KaTeX's.
{mut} sizedDelimiters = new Set();
function setSizedDelimiters(delims) {{
  sizedDelimiters = new Set(delims || []);
}}
"""


def patch_delims(name: str, decl: str, esm: bool) -> None:
    p = root / name
    s = p.read_text()
    never = f"{decl} stackNeverDelimiters = new Set(["
    assert s.count(never) == 1, f"expected once: {never!r}"
    end = s.index("\n", s.index(never)) + 1
    s = s[:end] + DELIMS.format(decl=decl, mut=mutable(decl)) + s[end:]
    # \\bigl… and \\left…\\right: the sizes, then stacked
    s = replace(s, "if (stackLargeDelimiters.has(delim) || stackNeverDelimiters.has(delim)) {", "if (stackLargeDelimiters.has(delim) || stackNeverDelimiters.has(delim) || sizedDelimiters.has(delim)) {")
    s = replace(s, "} else if (stackLargeDelimiters.has(delim)) {", "} else if (stackLargeDelimiters.has(delim) || sizedDelimiters.has(delim)) {")
    s = replace(s, "  __setSvgDesign: setSvgDesign,\n", "  __setSvgDesign: setSvgDesign,\n  __setSizedDelimiters: setSizedDelimiters,\n")
    if esm:
        s = replace(s, "setSvgDesign as __setSvgDesign, ", "setSvgDesign as __setSvgDesign, setSizedDelimiters as __setSizedDelimiters, ")
    p.write_text(s)
    print("patched", name)


if __name__ == "__main__":
    patch("katex.mjs", "var", esm=True)
    patch("katex.js", "const", esm=False)
    patch_svg("katex.mjs", "var", esm=True, esc="escape")
    patch_svg("katex.js", "const", esm=False, esc="utils_escape")
    patch_delims("katex.mjs", "var", esm=True)
    patch_delims("katex.js", "const", esm=False)
