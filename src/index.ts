import katex from "./katex";
import { axisHeight, cancels, classic, inter, italicSkews, logoBar, operatorItalics, rules, strikeTop, underlines, uprightSkews, xHeight, type KatexFont, type MetricTable } from "./metrics";
import { interSurd, type Surd } from "./surd";
import { interSvg, type SvgDesign } from "./svg";

export { versions, type CharMetrics, type KatexFont, type MetricTable } from "./metrics";
export { interSurd, radicalAt, surdStroke, type Surd } from "./surd";
export { interSvg, type SvgDesign } from "./svg";

/** KaTeX's own fonts (Computer Modern), or Inter Math. */
export type MathFont = "classic" | "inter";

/** Heads of the arrows drawn small (AMS arrows such as ↣ ⇉ ↺ ↰, and the vectors: \vec, \overrightarrow…). */
export type ArrowHeads = "angle" | "triangle";

export interface MathFontOptions {
  /**
   * Weight of regular math, 100-900 (Inter Math only; default 400): fraction
   * bars and √ follow it. Give the CSS the same (`--inter-math-weight`).
   */
  weight?: number;
  /**
   * The small arrowheads (Inter Math only): "angle", like every other arrow's
   * (the default), or "triangle", filled, like Inter's own small arrows
   * (↰ ↺). The glyphs switch through the font's `ss01` stylistic set, which
   * the CSS turns on for math rendered with "triangle"; the vectors are
   * drawn so.
   */
  arrowHeads?: ArrowHeads;
}

/** The class our KaTeX patch puts on math rendered with triangle arrowheads (inter-math.css turns `ss01` on there). */
export const TRIANGLE_HEADS_CLASS = "inter-math-triangles";

/** The class that switches KaTeX's fonts to Inter Math, on any ancestor of the math (see inter-math.css). */
export const INTER_MATH_CLASS = "inter-math";

// not in KaTeX's typings; __setGlobalMetrics, __setSurd, __setSvgDesign, __setSizedDelimiters, __setComposedText,
// __setItalicAccents, __setRootClasses and __setRuleImages come from our patch (patches/katex@0.19.0.patch)
const hooks = katex as unknown as {
  __defineMacro(name: string, body: string): void;
  __setFontMetrics(font: string, metrics: MetricTable): void;
  __setGlobalMetrics(overrides: Record<string, [number, number, number]> | null): void;
  __setComposedText(chars: string[] | null): void;
  __setItalicAccents(on: boolean): void;
  __setRootClasses(classes: string[] | null): void;
  __setRuleImages(on: boolean): void;
  __setSurd(surd: Surd | null): void;
  __setSvgDesign(design: SvgDesign | null): void;
  __setSizedDelimiters(delimiters: string[] | null): void;
};

/**
 * Delimiters KaTeX always stacks (from Computer Modern's brace pieces) that
 * Inter Math draws at KaTeX's four sizes (build/delimiters.py): \left and \big
 * take those first, as they do ( [ {.
 */
const SIZED_DELIMITERS = ["\\lgroup", "\\rgroup", "⟮", "⟯", "\\lmoustache", "\\rmoustache", "⎰", "⎱"];

const fonts = Object.keys(classic) as KatexFont[];
/** Inter Math's tables: its glyphs over KaTeX's (what Inter lacks is still set in KaTeX's fonts). */
const merged = Object.fromEntries(fonts.map((f) => [f, { ...classic[f], ...inter[f] }])) as Record<
  KatexFont,
  MetricTable
>;

/** A table by weight, at any weight: linear between the measured ones. */
function byWeight<T extends number | number[]>(table: Record<number, T>, weight: number): T {
  const ws = Object.keys(table)
    .map(Number)
    .sort((a, b) => a - b);
  const w = Math.min(Math.max(weight, ws[0]!), ws[ws.length - 1]!);
  const hi = ws.find((x) => x >= w)!;
  const lo = [...ws].reverse().find((x) => x <= w)!;
  const t = hi === lo ? 0 : (w - lo) / (hi - lo);
  const mix = (a: number, b: number) => a + (b - a) * t;
  const [a, b] = [table[lo]!, table[hi]!];
  return (Array.isArray(a) ? a.map((v, i) => mix(v, (b as number[])[i]!)) : mix(a as number, b as number)) as T;
}

/** The tables whose letters' skews change with the weight: math's italic, \mathit's, and the upright letters. */
const SKEWED: Partial<Record<KatexFont, Record<number, Record<number, number>>>> = {
  "Math-Italic": italicSkews,
  "Main-Italic": italicSkews,
  "Main-Regular": uprightSkews,
};

/**
 * A font's table at a weight: the letters' skews the weight's (where Inter puts its marks over them; KaTeX reads
 * one table, whose skews are Regular's: an accent drifted from Inter's place as the weight changed), and the
 * integrals' italic corrections (their superscripts stay where they go as their advances change).
 */
function tableAt(font: KatexFont, weight: number): MetricTable {
  const skewed = SKEWED[font];
  const italics = operatorItalics[font];
  if (!skewed && !italics) return merged[font];
  const table = { ...merged[font] };
  for (const [cp, skews] of Object.entries(skewed ?? {})) {
    const m = table[Number(cp)];
    if (m) table[Number(cp)] = [m[0], m[1], m[2], byWeight(skews, weight), m[4]];
  }
  for (const [cp, italic] of Object.entries(italics ?? {})) {
    const m = table[Number(cp)];
    if (m) table[Number(cp)] = [m[0], m[1], byWeight(italic, weight), m[3], m[4]];
  }
  return table;
}

/** Thickness of Inter Math's minus sign at a weight (em): the thickness of TeX's rules. */
export function ruleThickness(weight: number): number {
  return byWeight(rules, weight);
}

/** Inter's underline at a weight (the line under its ḇ): how far under the baseline (or a descender) and how thick (em). */
export function underline(weight: number): { gap: number; thickness: number } {
  const [gap, thickness] = byWeight(underlines, weight);
  return { gap, thickness };
}

/**
 * The unit TeX's vertical spaces count in at a weight (em): a fraction's clearances (3 of them over and under a display
 * fraction's bar, 1 in a text one's), a surd's over its radicand (1¼ of them, or 1 and a quarter x-height in display
 * style), a superscript's from its subscript (4). TeX counts them in its rule's thickness, which in Inter Math follows
 * the weight (0.02 em at Thin, 0.14 at Black): they grew sevenfold from Thin to Black, where Inter's own whites shrink
 * (under its underline, between ='s bars, under its accents). So Regular's rule, and across the weights as the gap
 * under Inter's underline: a little more white at Thin, a fifth less at Black.
 */
export function ruleSpacing(weight: number): number {
  return (ruleThickness(400) * underline(weight).gap) / underline(400).gap;
}

/** How thick Inter's strokes that cancel a letter (Ɇ ȼ) are at a weight (em): \cancel's. */
export function cancelThickness(weight: number): number {
  return byWeight(cancels, weight);
}

/**
 * The accented letters Inter Math draws precomposed, upright and italic (À to ſ):
 * KaTeX sets them as they are, not as the letter and an accent, and \'{a}
 * \r{A}… become them (our patch's __setComposedText).
 */
const COMPOSED = Object.keys(inter["Main-Regular"])
  .map(Number)
  .filter((cp) => cp in inter["Math-Italic"] && String.fromCodePoint(cp).normalize("NFD").length > 1)
  .map((cp) => String.fromCodePoint(cp));

type Sizes = [number, number, number];

/** KaTeX's fraction shifts (TeX's sigmas 8-12; text, script, scriptscript), from its src/fontMetrics.ts. */
export const KATEX_FRACTION_SHIFTS: Record<string, Sizes> = {
  num1: [0.677, 0.732, 0.925],
  num2: [0.394, 0.384, 0.387],
  num3: [0.444, 0.471, 0.504],
  denom1: [0.686, 0.752, 1.025],
  denom2: [0.345, 0.344, 0.532],
};
/** KaTeX's math axis (TeX's sigma 22). */
export const KATEX_AXIS = 0.25;

/**
 * TeX parameters that follow the font: rules are a minus sign thick (Inter
 * Math's operators are as heavy as its letters), the √'s bar and strokes too
 * (src/surd.ts), the spaces TeX counts in rules Inter's whites (`ruleSpacing`),
 * underlines Inter's own (\underline, \underbar: as far under the
 * text and as thick as the line of its ḇ, where TeX puts three rules under it
 * and one rule thick), and so are the other lines a font can set through our
 * patch (\overline the underline's mirror; \sout Inter's strike-through;
 * \cancel its strokes across Ɇ ȼ; \phase as thick as the underline); the
 * x-height is Inter Math's; the math axis is its operators' centre (between
 * its lowercase and its capitals), and fractions move up with it, keeping
 * their distances to the bar.
 */
function globalMetrics(weight: number): Record<string, Sizes> {
  const rule = ruleThickness(weight);
  const line = underline(weight);
  const all = (v: number): Sizes => [v, v, v];
  const raise = axisHeight - KATEX_AXIS;
  const shifted = (name: string, by: number) => KATEX_FRACTION_SHIFTS[name]!.map((v) => v + by) as Sizes;
  return {
    axisHeight: all(axisHeight),
    num1: shifted("num1", raise),
    num2: shifted("num2", raise),
    num3: shifted("num3", raise),
    denom1: shifted("denom1", -raise),
    denom2: shifted("denom2", -raise),
    defaultRuleThickness: all(rule),
    // read by our KaTeX patch: TeX's vertical spaces, apart from the rules' thickness
    ruleSpacing: all(ruleSpacing(weight)),
    sqrtRuleThickness: all(rule),
    // read by our KaTeX patch's \underline (TeX's three rules under, one thick, when they're not set)
    underlineGap: all(line.gap),
    underlineRuleThickness: all(line.thickness),
    // \overline the underline's mirror: as far over the content and as thick (TeX's: three rules over, one thick)
    overlineGap: all(line.gap),
    overlineRuleThickness: all(line.thickness),
    // \sout: Inter's strike-through, as thick as its underline (KaTeX's: 0.08 em, half the x-height up)
    soutRuleThickness: all(line.thickness),
    soutShift: all(strikeTop - line.thickness),
    // \cancel \bcancel \xcancel: Inter's strokes across Ɇ ȼ (KaTeX's: 0.046 em)
    cancelRuleThickness: all(cancelThickness(weight)),
    // \phase: its line and its angle as thick as the underline (KaTeX's: 0.6 pt)
    phaseRuleThickness: all(line.thickness),
    arrayRuleWidth: all(rule),
    fboxrule: all(rule),
    xHeight: all(xHeight),
  };
}

/**
 * Symbols KaTeX builds from two glyphs that Inter Math draws as one: ∉ ∌ (∈ ∋ and a slash: ∌'s is ∉'s, the longer
 * of KaTeX's two), ⟦ ⟧ ⦃ ⦄ (two glyphs overlapped at a fixed kern, which Inter Math's strokes close at heavy
 * weights). KaTeX's own definitions come back with "classic".
 */
const MACROS: Record<string, Record<MathFont, string>> = {
  "\\notin": {
    classic: "\\html@mathml{\\mathrel{{\\in}\\mathllap{/\\mskip1mu}}}{\\mathrel{\\char`∉}}",
    inter: "\\html@mathml{\\mathrel{\\char`∉}}{\\mathrel{\\char`∉}}",
  },
  "\\notni": {
    classic: "\\html@mathml{\\not\\ni}{\\mathrel{\\char`\u220C}}",
    inter: "\\html@mathml{\\mathrel{\\char`\u220C}}{\\mathrel{\\char`\u220C}}",
  },
  "\\llbracket": {
    classic: "\\html@mathml{\\mathopen{[\\mkern-3.2mu[}}{\\mathopen{\\char`\u27e6}}",
    inter: "\\html@mathml{\\mathopen{\\char`\u27e6}}{\\mathopen{\\char`\u27e6}}",
  },
  "\\rrbracket": {
    classic: "\\html@mathml{\\mathclose{]\\mkern-3.2mu]}}{\\mathclose{\\char`\u27e7}}",
    inter: "\\html@mathml{\\mathclose{\\char`\u27e7}}{\\mathclose{\\char`\u27e7}}",
  },
  "\\lBrace": {
    classic: "\\html@mathml{\\mathopen{\\{\\mkern-3.2mu[}}{\\mathopen{\\char`\u2983}}",
    inter: "\\html@mathml{\\mathopen{\\char`\u2983}}{\\mathopen{\\char`\u2983}}",
  },
  "\\rBrace": {
    classic: "\\html@mathml{\\mathclose{]\\mkern-3.2mu\\}}}{\\mathclose{\\char`\u2984}}",
    inter: "\\html@mathml{\\mathclose{\\char`\u2984}}{\\mathclose{\\char`\u2984}}",
  },
};

/**
 * KaTeX's logos: \TeX (E lowered half an ex between T and X); \LaTeX and \KaTeX set it after their L or K and a
 * script A raised to the T's top (by its metrics: KaTeX's own are Computer Modern's).
 */
function logos(font: MathFont, weight: number): Record<string, string> {
  const main = font === "inter" ? tableAt("Main-Regular", weight) : classic["Main-Regular"];
  // T and X (and L K A) raised to stand on the bottom of E's middle bar, which half an ex down leaves over them in
  // Inter Math (its x-height is tall: the letters stood on two lines); by weight, as the bar thickens
  const up = font === "inter" ? byWeight(logoBar, weight) - xHeight / 2 : 0;
  const em = (v: number) => `${+v.toFixed(4)}em`;
  const raised = (box: string) => (up ? `\\raisebox{${em(up)}}{${box}}` : box);
  const a = `\\raisebox{${em(main[0x54]![1] - 0.7 * main[0x41]![1] + up)}}{\\scriptstyle A}`;
  const logo = (tex: string, text: string) => `\\textrm{\\html@mathml{${tex}}{${text}}}`;
  return {
    "\\TeX": logo(`${raised("T")}\\kern-.1667em\\raisebox{-.5ex}{E}\\kern-.125em${raised("X")}`, "TeX"),
    "\\LaTeX": logo(`${raised("L")}\\kern-.36em${a}\\kern-.15em\\TeX`, "LaTeX"),
    "\\KaTeX": logo(`${raised("K")}\\kern-.17em${a}\\kern-.15em\\TeX`, "KaTeX"),
  };
}

let current: { font: MathFont; weight: number; arrowHeads: ArrowHeads } = { font: "classic", weight: 400, arrowHeads: "angle" };

/**
 * Lay KaTeX out with a font, for everything rendered from now on: its glyph
 * metrics, its rules, its surds and its arrows. KaTeX's settings are global: math already
 * rendered keeps its layout until it is rendered again. The `inter-math` class
 * must match (CSS picks the glyphs).
 */
export function setMathFont(font: MathFont, options: MathFontOptions = {}): void {
  const weight = options.weight ?? 400;
  const arrowHeads = options.arrowHeads ?? "angle";
  if (font === current.font && (font === "classic" || (weight === current.weight && arrowHeads === current.arrowHeads))) return;
  const triangles = font === "inter" && arrowHeads === "triangle";
  for (const f of fonts) hooks.__setFontMetrics(f, font === "inter" ? tableAt(f, weight) : classic[f]);
  hooks.__setGlobalMetrics(font === "inter" ? globalMetrics(weight) : null);
  hooks.__setSurd(font === "inter" ? interSurd(ruleThickness(weight)) : null);
  hooks.__setSvgDesign(font === "inter" ? interSvg(weight, triangles) : null);
  hooks.__setRootClasses(triangles ? [TRIANGLE_HEADS_CLASS] : null);
  hooks.__setSizedDelimiters(font === "inter" ? SIZED_DELIMITERS : null);
  hooks.__setComposedText(font === "inter" ? COMPOSED : null);
  // a math accent over an italic letter from the italic font, as Inter's text sets them (build/symbol_glyphs.py)
  hooks.__setItalicAccents(font === "inter");
  // the rules as thick as the minus sign and the surds beside them (a border is rounded to whole device pixels)
  hooks.__setRuleImages(font === "inter");
  for (const [name, bodies] of Object.entries(MACROS)) hooks.__defineMacro(name, bodies[font]);
  for (const [name, body] of Object.entries(logos(font, weight))) hooks.__defineMacro(name, body);
  current = { font, weight, arrowHeads };
}

/** The font KaTeX currently lays out with. */
export function mathFont(): MathFont {
  return current.font;
}

/** Characters KaTeX sets in one of its fonts that Inter Math lacks (they stay in Computer Modern). */
export function keptFromKatex(font: KatexFont): number[] {
  return Object.keys(classic[font])
    .map(Number)
    .filter((cp) => !(cp in inter[font]));
}

/** Run `render` with a font, then restore the current one (to show both fonts side by side). */
export function withMathFont<T>(font: MathFont, render: () => T, options: MathFontOptions = {}): T {
  const previous = current;
  setMathFont(font, options);
  try {
    return render();
  } finally {
    setMathFont(previous.font, { weight: previous.weight, arrowHeads: previous.arrowHeads });
  }
}
