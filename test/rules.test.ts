import katex from "katex";
import { afterEach, describe, expect, it } from "vitest";
import { cancelThickness, interSurd, interSvg, ruleSpacing, ruleThickness, setMathFont, surdStroke, underline } from "../src/index";
import { bars, inter, operatorItalics, radicals, rules, talls, vecLength, xHeight } from "../src/metrics";

/** A rule's thickness (em) in KaTeX's HTML, by its class: its image's (Inter Math draws them), or its border's. */
const rule = (html: string, className: string) => {
  const m = new RegExp(`class="${className}" style="([^"]*)">(?:<svg [^>]*><path d="M0 ([\\d.]+)H400000V([\\d.]+)H0Z"/></svg>)?`).exec(html);
  if (!m) return NaN;
  return m[2] ? (Number(m[3]) - Number(m[2])) / 1000 : Number(/border-bottom-width:([\d.]+)em/.exec(m[1]!)?.[1]);
};
const fracLine = (html: string) => rule(html, "frac-line");
/** A rule's image: one band from its box's left edge to KaTeX's far right. */
const isRule = (d: string) => /^M0 [\d.]+H400000V[\d.]+H0Z$/.test(d);
/** The ink's runs across an outline at a height (its points taken as a polygon: exact across straight stems). */
function runsAt(points: [number, number][], ends: number[], y: number): [number, number][] {
  const xs: number[] = [];
  let start = 0;
  for (const end of ends) {
    for (let i = start; i <= end; i++) {
      const [a, b] = [points[i]!, points[i === end ? start : i + 1]!];
      if ((a[1] - y) * (b[1] - y) < 0) xs.push(a[0] + ((y - a[1]) / (b[1] - a[1])) * (b[0] - a[0]));
    }
    start = end + 1;
  }
  xs.sort((p, q) => p - q);
  return xs.flatMap((x, i) => (i % 2 ? [] : [[x, xs[i + 1]!] as [number, number]]));
}
const surdPath = (html: string) => /<path d="([^"]+)"/.exec(html)?.[1] ?? "";
const CASES = ["\\vec{u} + \\overrightarrow{AB}", "\\oiint \\displaystyle \\oiiint", "\\xrightarrow{f} \\overleftrightarrow{AB} \\Overrightarrow{AB}", "M \\notin (AB)", "\\frac{1}{2}", "\\sqrt{x}", "\\sqrt{\\frac{a}{b}}", "\\sqrt{\\frac{\\frac{1}{2}}{\\frac{3}{4}}}", "\\sqrt[3]{x^2 + 1}", "\\overline{AB}", "\\underline{AB}", "\\underbar{X}", "\\left\\lgroup \\frac{a}{b} \\right\\rgroup \\bigl\\lmoustache x \\bigr\\rmoustache", "\\left| \\frac{a}{b} \\right| \\begin{Vmatrix} 1 \\\\ 2 \\end{Vmatrix}", "\\left( \\begin{matrix} 1 \\\\ 2 \\\\ 3 \\\\ 4 \\end{matrix} \\right]", "\\left\\{ \\begin{matrix} 1 \\\\ 2 \\\\ 3 \\\\ 4 \\end{matrix} \\right\\rgroup", "\\left\\Uparrow \\begin{matrix} 1 \\\\ 2 \\\\ 3 \\end{matrix} \\right\\updownarrow", "\\widetilde{ac} \\utilde{AB} \\widehat{ac} \\widecheck{ac}", "\\overgroup{AB} \\undergroup{AB} \\overbrace{AB} \\underbracket{AB} \\overlinesegment{AB} \\overrightharpoon{ac}", "\\text{\\'{a} \\aa\\ é \\sout{x}}", "\\cancel{5} \\xcancel{AB} \\phase{x}", "\\notni \\llbracket x \\rrbracket \\lBrace x \\rBrace"];

describe("rules and surds", () => {
  afterEach(() => setMathFont("classic"));

  it("are a minus sign thick in Inter Math, and follow the weight", () => {
    expect(fracLine(katex.renderToString("\\frac{1}{2}"))).toBe(0.04);
    setMathFont("inter");
    expect(fracLine(katex.renderToString("\\frac{1}{2}"))).toBeCloseTo(rules[400]!, 3);
    setMathFont("inter", { weight: 700 });
    expect(fracLine(katex.renderToString("\\frac{1}{2}"))).toBeCloseTo(rules[700]!, 3);
    expect(ruleThickness(450)).toBeCloseTo((rules[400]! + rules[500]!) / 2, 6);
  });

  it("draw the rules as images in Inter Math, as thick as they are (a border is rounded to whole device pixels)", () => {
    const tex = "\\frac{1}{2} \\overline{AB} \\underline{AB} \\begin{array}{c} a \\\\ \\hline b \\\\ \\hdashline c \\end{array}";
    const classes = ["frac-line", "overline-line", "underline-line", "katex-hline"];
    const classic = katex.renderToString(tex);
    expect(classic).not.toMatch(/H400000V/);
    for (const c of classes) expect(rule(classic, c)).toBeGreaterThan(0);
    for (const weight of [100, 900]) {
      setMathFont("inter", { weight });
      const html = katex.renderToString(tex);
      for (const c of classes) {
        // the border gone, the image's bottom on the rule's (its box reaches as far under it as over it)
        expect(html).toMatch(new RegExp(`class="${c}" style="border-bottom-width:0;position:relative;"><svg [^>]*style="bottom:-0.5em;`));
        expect(rule(html, c)).toBeGreaterThan(0);
      }
      expect(rule(html, "frac-line")).toBeCloseTo(rules[weight]!, 4);
      expect(rule(html, "overline-line")).toBeCloseTo(underline(weight).thickness, 4);
      // a dashed line keeps its border
      expect(html).toMatch(/class="katex-hdashline" style="border-bottom-width:[\d.]+em;"><\/span>/);
    }
  });

  it("draw Inter's √ in Inter Math, KaTeX's otherwise", () => {
    const classic = surdPath(katex.renderToString("\\sqrt{x}"));
    setMathFont("inter");
    const inter = surdPath(katex.renderToString("\\sqrt{x}"));
    expect(inter).not.toBe(classic);
    // straight lines only: four polygons (entry bar, down-stroke, up-stroke, vinculum)
    expect(inter.match(/M/g)).toHaveLength(4);
    expect(inter).not.toMatch(/[cCsSqQ]/);
  });

  it("space fractions, surds and scripts in Inter's whites, not in the rule: as Regular's at Regular, a little less white at Black", () => {
    expect(ruleSpacing(400)).toBeCloseTo(ruleThickness(400), 6);
    expect(ruleSpacing(900)).toBeLessThan(ruleSpacing(400));
    expect(ruleSpacing(100)).toBeGreaterThan(ruleSpacing(400));
    // the formulas' heights from Regular to Black: their rules thicken (by 0.066 em), the whites around them don't grow
    // (TeX's 3 rules over a display fraction's bar grew by 0.2 em, then as much under it)
    const height = (tex: string) => {
      const struts = [...katex.renderToString(tex, { displayMode: true }).matchAll(/class="katex-strut" style="height:([\d.]+)em;/g)];
      return Math.max(...struts.map((m) => Number(m[1])));
    };
    // a surd as tall as its radicand: a spacing unit and a quarter x-height under its vinculum, in text style too
    // (TeX's text clearance, 1¼ units, counted on a size taller than needed for more white)
    const inline = (tex: string) => Math.max(...[...katex.renderToString(tex).matchAll(/class="katex-strut" style="height:([\d.]+)em;/g)].map((m) => Number(m[1])));
    for (const weight of [100, 400, 900]) {
      setMathFont("inter", { weight });
      // over the radicand: the clearance, the vinculum, and TeX's kern over it (a spacing unit)
      const clearance = inline("\\sqrt{\\dfrac{x}{y}}") - inline("\\dfrac{x}{y}") - ruleThickness(weight) - ruleSpacing(weight);
      expect(clearance, `weight ${weight}`).toBeCloseTo(ruleSpacing(weight) + xHeight / 4, 2);
    }
    const thickening = ruleThickness(900) - ruleThickness(400);
    for (const tex of ["\\dfrac{x}{y}", "\\dfrac{\\dfrac{a}{b}}{\\dfrac{c}{d}}", "\\sqrt{x}", "\\sqrt{\\dfrac{x}{y}}", "x_1^2"]) {
      setMathFont("inter", { weight: 400 });
      const regular = height(tex);
      setMathFont("inter", { weight: 900 });
      expect(height(tex) - regular, tex).toBeLessThan(thickening);
    }
  });

  it("start the radicand where the surd's box says", () => {
    setMathFont("inter");
    const html = katex.renderToString("\\sqrt{x}");
    const padding = Number(/padding-left:([\d.]+)em/.exec(html)?.[1]);
    expect(padding).toBeCloseTo(interSurd(ruleThickness(400)).box("sqrtMain").advanceWidth, 3);
  });

  it("draw the surd's strokes as thick as the rule at every weight (Inter's √ is heavier, then lighter), the √ larger on taller surds", () => {
    const polygons = (d: string) => d.split("M").slice(1).map((p) => p.replace("Z", "").split("L").map((q) => q.split(" ").map(Number)));
    const tall = (pts: number[][]) => Math.max(...pts.map((p) => p[1]!)) - Math.min(...pts.map((p) => p[1]!));
    // the up-stroke across: its top edge's width over its slant's
    const across = (pts: number[][]) => {
      const top = Math.min(...pts.map((p) => p[1]!));
      const [a, b] = pts.filter((p) => Math.abs(p[1]! - top) < 0.2).sort((p, q) => p[0]! - q[0]!);
      const low = pts.reduce((p, q) => (q[1]! > p[1]! || (q[1] === p[1] && q[0]! > p[0]!) ? q : p));
      const slope = (b![0]! - low[0]!) / (low[1]! - top);
      return (b![0]! - a![0]!) / Math.hypot(1, slope);
    };
    for (const weight of [100, 400, 900]) {
      const surd = interSurd(ruleThickness(weight));
      // entry bar, down-stroke, up-stroke, vinculum
      const main = polygons(surd.path("sqrtMain", 0, 1080, 80));
      expect(tall(main[3]!) / 1000).toBeCloseTo(ruleThickness(weight), 3);
      expect(across(main[2]!) / 1000).toBeCloseTo(ruleThickness(weight), 2);
    }
    expect(surdStroke(400) / ruleThickness(400)).toBeGreaterThan(1.1);
    expect(surdStroke(900) / ruleThickness(900)).toBeLessThan(0.85);
    // past Regular, Regular's √ with its strokes thickened to the rule's: its entry bar keeps Regular's proportions
    // (twice as long as thick: Black's, thickened, was a block) and its middle stays where Regular's is, on the axis
    const extent = (pts: number[][]) => {
      const [xs, ys] = [pts.map((p) => p[0]!), pts.map((p) => p[1]!)];
      return { wide: Math.max(...xs) - Math.min(...xs), tall: Math.max(...ys) - Math.min(...ys), middle: (Math.max(...ys) + Math.min(...ys)) / 2 };
    };
    const bar = extent(polygons(interSurd(ruleThickness(900)).path("sqrtMain", 0, 1080, 80))[0]!.map(([x, y]) => [x! / 1000, (1080 - y!) / 1000]));
    const regular = extent(radicals[400]!.bar);
    expect(bar.wide / bar.tall).toBeCloseTo(regular.wide / regular.tall, 1);
    expect(bar.middle).toBeCloseTo(regular.middle, 2);
    const surd = interSurd(ruleThickness(400));
    const [main, threeEm] = [surd.path("sqrtMain", 0, 1080, 80), surd.path("sqrtTall", 0, 3080, 80)].map(polygons);
    expect(tall(threeEm![1]!) / tall(main![1]!)).toBeGreaterThan(2);
  });

  it("draw a surd at any height, the normal one up to 1 em: one design, growing smoothly from it", () => {
    const surd = interSurd(rules[400]!);
    expect(surd.anyHeight).toBe(true);
    // a tall surd 1 em tall is the normal one
    expect(surd.path("sqrtTall", 0, 1080, 80)).toBe(surd.path("sqrtMain", 0, 1080, 80));
    expect(surd.box("sqrtTall", 1).advanceWidth).toBeCloseTo(surd.box("sqrtMain").advanceWidth, 6);
    // from 1 to 6 em every 0.05 em: growing, never by a step
    const widths = Array.from({ length: 101 }, (_, i) => surd.box("sqrtTall", 1 + i * 0.05).advanceWidth);
    expect([...widths].sort((a, b) => a - b)).toEqual(widths);
    widths.slice(1).forEach((w, i) => expect(w - widths[i]!).toBeLessThan(0.02));
    setMathFont("inter");
    // KaTeX's four sizes never come
    const html = katex.renderToString("\\sqrt{x} \\sqrt{\\frac{a}{b}} \\sqrt{\\dfrac{a}{b}} \\sqrt{\\dfrac{\\dfrac{a}{b}}{c}}");
    for (const [, box] of html.matchAll(/viewBox="0 0 400000 (\d+)"/g)) expect([1296, 1944, 2592, 3240]).not.toContain(Number(box));
    expect(surdPath(katex.renderToString("\\sqrt{\\begin{pmatrix}1\\\\2\\\\3\\\\4\\\\5\\\\6\\end{pmatrix}}"))).not.toMatch(/NaN|Infinity/);
  });

  it("grow \\left( \\right) and surds with their content as the weight changes, never by a step", () => {
    // TeX's spaces follow the rule, the rule the weight: the content grows with it (the hero of the site's page)
    const tex = String.raw`\left( \sqrt{\frac{5 + \sqrt{5}}{2}} - \frac{\sqrt{5} + 1}{2} \right) \sqrt[5]{e^{2\pi}}`;
    // in order, each paren's height (KaTeX's largest glyph, 3 em, until its content outgrows it, then an image) and
    // each surd's (an image)
    const heights = (html: string) =>
      [...html.matchAll(/class="delimsizing (size\d)"|<svg [^>]*height="([\d.]+)em"/g)].map((m) => (m[1] ? [0, 1.2, 1.8, 2.4, 3][Number(m[1].slice(4))]! : Number(m[2])));
    let last: number[] = [];
    for (let weight = 100; weight <= 900; weight += 5) {
      setMathFont("inter", { weight });
      const now = heights(katex.renderToString(tex, { displayMode: true }));
      if (last.length) {
        expect(now.length).toBe(last.length);
        now.forEach((h, i) => expect(Math.abs(h - last[i]!), `weight ${weight}, image ${i}`).toBeLessThan(0.05));
      }
      last = now;
    }
  });

  it("underline as Inter does (the line of its ḇ) in Inter Math, as TeX does otherwise", () => {
    const line = (html: string) => rule(html, "underline-line");
    expect(line(katex.renderToString("\\underline{AB}"))).toBe(0.04);
    setMathFont("inter");
    for (const tex of ["\\underline{AB}", "\\underbar{X}"]) expect(line(katex.renderToString(tex))).toBeCloseTo(underline(400).thickness, 3);
    setMathFont("inter", { weight: 900 });
    expect(line(katex.renderToString("\\underline{AB}"))).toBeCloseTo(underline(900).thickness, 3);
  });

  it("overline as Inter underlines, its mirror, in Inter Math, as TeX does otherwise", () => {
    const line = (html: string) => rule(html, "overline-line");
    expect(line(katex.renderToString("\\overline{AB}"))).toBe(0.04);
    setMathFont("inter", { weight: 900 });
    // as thick as the underline, not as the fraction bars (the minus sign, 0.14 em at Black)
    expect(line(katex.renderToString("\\overline{AB}"))).toBeCloseTo(underline(900).thickness, 3);
    expect(underline(900).thickness).toBeLessThan(ruleThickness(900));
  });

  it("strike through, cancel and phase with Inter's lines at the weight in Inter Math, KaTeX's fixed ones otherwise", () => {
    const cancel = (html: string) => /stroke-width="([^"]+)"/.exec(html)?.[1];
    const sout = (html: string) => /katex-sout"[^>]*style="[^"]*border-bottom-width:([\d.]+)em/.exec(html)?.[1];
    const phase = (html: string) => /<path d="(M400000[^"]+)"/.exec(html)?.[1];
    const classic = katex.renderToString("\\cancel{5} \\text{\\sout{x}} \\phase{x}");
    expect(cancel(classic)).toBe("0.046em");
    expect(sout(classic)).toBeUndefined();
    setMathFont("inter", { weight: 100 });
    const light = katex.renderToString("\\cancel{5} \\text{\\sout{x}} \\phase{x}");
    setMathFont("inter", { weight: 900 });
    const heavy = katex.renderToString("\\cancel{5} \\text{\\sout{x}} \\phase{x}");
    expect(Number.parseFloat(cancel(heavy)!)).toBeCloseTo(cancelThickness(900), 3);
    expect(Number.parseFloat(cancel(light)!)).toBeLessThan(Number.parseFloat(cancel(heavy)!));
    expect(Number(sout(heavy))).toBeGreaterThan(Number(sout(light)));
    expect(phase(heavy)).not.toBe(phase(classic));
  });

  it("set accented letters as Inter's precomposed ones in Inter Math, as KaTeX's accents otherwise", () => {
    const tex = "\\text{\\'{a} \\aa\\ \\AA\\ é}";
    expect(katex.renderToString(tex)).toContain("accent");
    setMathFont("inter");
    const html = katex.renderToString(tex);
    expect(html).not.toContain("accent");
    for (const ch of ["á", "å", "Å", "é"]) expect(html).toContain(ch);
    // in math, \'{a} is the italic á, and so are \acute{a} and a typed á; the other math accents likewise
    for (const tex of ["\\'{a}", "\\acute{a}", "\\acute a", "á"]) expect(katex.renderToString(tex)).toContain('<span class="mord mathnormal">á</span>');
    for (const [tex, ch] of [["\\ddot{a}", "ä"], ["\\hat{a}", "â"], ["\\tilde{n}", "ñ"], ["\\check{c}", "č"], ["\\mathring{A}", "Å"], ["\\grave{e}", "è"]]) {
      // (KaTeX marks letters past Latin-1 latin_fallback; Inter Math's italic still sets them)
      expect(katex.renderToString(tex!)).toMatch(new RegExp(`<span class="mord mathnormal[^"]*"[^>]*>${ch}</span>`));
    }
    // \bar stays an accent, drawn wider than a macron; so does a letter with no precomposed glyph
    expect(katex.renderToString("\\bar{a}")).toContain("accent");
    expect(katex.renderToString("\\ddot{q}")).toContain("accent");
  });

  it("draw ∌ ⟦ ⟧ ⦃ ⦄ as one glyph in Inter Math, as KaTeX builds them from two otherwise", () => {
    const tex = "\\notni \\llbracket x \\rrbracket \\lBrace x \\rBrace";
    const classic = katex.renderToString(tex);
    expect(classic).toContain("margin-right:-0.1778em");
    setMathFont("inter", { weight: 900 });
    const html = katex.renderToString(tex);
    expect(html).not.toContain("margin-right:-0.1778em");
    for (const ch of ["∌", "⟦", "⟧", "⦃", "⦄"]) expect(html).toContain(ch);
  });

  it("draw KaTeX's images over and under their content as Inter Math's, none left KaTeX's", () => {
    const tex = "\\widetilde{ac} \\utilde{AB} \\widehat{ac} \\widecheck{ac} \\overgroup{AB} \\undergroup{AB} \\overbrace{AB} \\underbrace{AB} \\overbracket{AB} \\underbracket{AB} \\overlinesegment{AB} \\underlinesegment{AB} \\overleftharpoon{ac} \\overrightharpoon{ac}";
    const paths = (h: string) => [...h.matchAll(/<path d="([^"]+)"/g)].map((m) => m[1]!);
    const classic = paths(katex.renderToString(tex));
    setMathFont("inter");
    const html = katex.renderToString(tex);
    // our patch marks KaTeX's own paths while Inter Math is set
    expect(html).not.toContain("data-katex-path");
    expect(paths(html)).toHaveLength(classic.length);
    paths(html).forEach((p, i) => {
      expect(p).not.toBe(classic[i]);
      expect(p).not.toMatch(/NaN|Infinity|undefined/);
    });
  });

  it("put an accent over an italic letter where Inter puts its mark, at the weight", () => {
    const left = (weight: number) => {
      setMathFont("inter", { weight });
      return Number(katex.renderToString("\\ddot{x}").match(/class="accent-body" style="left:(-?[\d.]+)em/)![1]);
    };
    // KaTeX centres the accent, then shifts it by the letter's skew: the weight's, from Inter's ¨ over x
    const regular = left(400);
    expect(left(900)).not.toBeCloseTo(regular, 3);
    expect(left(400)).toBeCloseTo(regular, 6);
  });

  it("put an accent over an upright letter where Inter puts its mark, at the weight", () => {
    const left = (weight: number) => {
      setMathFont("inter", { weight });
      return Number(katex.renderToString("\\ddot{\\mathrm{b}}").match(/class="accent-body" style="left:(-?[\d.]+)em/)![1]);
    };
    // Inter puts b's marks over its bowl, off its middle: the farther, the heavier
    expect(left(900)).not.toBeCloseTo(left(400), 3);
  });

  it("give the small arrows triangle heads when asked: the glyphs through the root's class, the vectors drawn so", () => {
    const root = (tex: string) => /<span class="(katex[^"]*)"/.exec(katex.renderToString(tex))![1];
    const vec = () => katex.renderToString("\\vec{u} \\overrightarrow{AB}").match(/<path d="([^"]+)"/g)!.join();
    expect(root("a \\rightarrowtail b")).toBe("katex");
    setMathFont("inter");
    expect(root("a \\rightarrowtail b")).toBe("katex");
    const angle = vec();
    setMathFont("inter", { arrowHeads: "triangle" });
    expect(root("a \\rightarrowtail b")).toBe("katex inter-math-triangles");
    expect(vec()).not.toBe(angle);
    // back to angles, and Computer Modern never has them
    setMathFont("inter");
    expect(root("a \\rightarrowtail b")).toBe("katex");
    expect(vec()).toBe(angle);
    setMathFont("classic", { arrowHeads: "triangle" });
    expect(root("a \\rightarrowtail b")).toBe("katex");
  });

  it("set a math accent over an italic letter from the italic font in Inter Math, as Inter's text does", () => {
    const accent = (tex: string) => /class="accent-body"[^>]*><span class="([^"]+)"/.exec(katex.renderToString(tex))?.[1];
    expect(accent("\\hat{x}")).toBe("mord");
    setMathFont("inter");
    for (const tex of ["\\hat{x}", "\\acute{q}", "\\ddot{\\alpha}", "\\bar{x}", "\\mathring{x}", "\\check{x}_1"]) {
      expect(accent(tex)).toBe("mord mathnormal");
    }
    expect(accent("\\mathit{\\hat{x}}")).toBe("mord mathit");
    expect(accent("\\boldsymbol{\\hat{x}}")).toBe("mord boldsymbol");
    // over an upright letter, in text, over more than a letter: Main's, upright
    for (const tex of ["\\hat{\\Gamma}", "\\hat{\\mathrm{x}}", "\\text{\\'{x}}", "\\hat{xy}"]) {
      expect(accent(tex)).not.toMatch(/mathnormal|mathit|boldsymbol/);
    }
  });

  it("set a harpoon in its arrow's box, its shaft where the arrow's is", () => {
    setMathFont("inter", { weight: 700 });
    const box = (tex: string) => katex.renderToString(tex).match(/<svg [^>]*height="([\d.]+)em"/)![1];
    expect(box("\\overrightharpoon{ac}")).toBe(box("\\overrightarrow{ac}"));
    expect(box("\\overleftharpoon{ac}")).toBe(box("\\overleftarrow{ac}"));
    for (const harpoon of ["\\xrightharpoonup", "\\xrightharpoondown", "\\xleftharpoonup", "\\xleftharpoondown"]) {
      expect(box(`${harpoon}{abc}`)).toBe(box("\\xrightarrow{abc}"));
    }
  });

  it("draw the stretched harpoons as Inter Math's, none left KaTeX's", () => {
    const tex = "\\xrightharpoonup{abc} \\xrightharpoondown{abc} \\xleftharpoonup{abc} \\xleftharpoondown{abc} \\xrightleftharpoons{abc} \\xleftrightharpoons{abc}";
    setMathFont("inter");
    const html = katex.renderToString(tex);
    expect(html).not.toContain("data-katex-path");
    expect(html).not.toMatch(/NaN|Infinity|undefined/);
  });

  it("draw out braces and groups along level lines, so that KaTeX's slices meet at every weight", () => {
    for (const weight of [100, 300, 450, 700, 900]) {
      setMathFont("inter", { weight });
      for (const tex of ["\\overbrace{AB}", "\\underbrace{AB}", "\\overgroup{AB}", "\\undergroup{AB}"]) {
        const d = katex.renderToString(tex).match(/<path d="([^"]+)"/)![1]!;
        // every segment as long as KaTeX's images (400 em) is a level line
        const tokens = d.match(/[MLQZ]|-?[\d.]+/g)!;
        let cmd = "";
        let at = [0, 0];
        let start = [0, 0];
        const level = (from: number[], to: number[], line: boolean) => {
          if (Math.abs(to[0]! - from[0]!) <= 1000) return;
          expect(line).toBe(true);
          expect(to[1]).toBeCloseTo(from[1]!, 0);
        };
        for (let i = 0; i < tokens.length; ) {
          if (/[MLQZ]/.test(tokens[i]!)) {
            cmd = tokens[i++]!;
            // the closing line back to the contour's start
            if (cmd === "Z") level(at, start, true);
            continue;
          }
          const n = cmd === "Q" ? 4 : 2;
          const to = tokens.slice(i, i + n).map(Number).slice(-2);
          if (cmd === "M") start = to;
          else level(at, to, cmd === "L");
          at = to;
          i += n;
        }
      }
    }
  });

  it("draw the shaft between a stretched arrow's pieces as wide as they are at the weight", () => {
    setMathFont("inter", { weight: 900 });
    const width = katex.renderToString("\\Big\\downarrow").match(/<svg [^>]*width="([\d.]+)em"/)![1]!;
    expect(Number(width)).toBeCloseTo(bars[900]!.arrow.advance, 3);
  });

  it("draw every documented arrow on the line from Inter Math's glyphs, the small-headed ones' heads triangles when asked", () => {
    const commands = ["\\xleftarrow", "\\xrightarrow", "\\xLeftarrow", "\\xRightarrow", "\\xleftrightarrow", "\\xLeftrightarrow",
      "\\xhookleftarrow", "\\xhookrightarrow", "\\xmapsto", "\\xrightharpoondown", "\\xrightharpoonup", "\\xleftharpoondown",
      "\\xleftharpoonup", "\\xrightleftharpoons", "\\xleftrightharpoons", "\\xlongequal", "\\xtwoheadrightarrow",
      "\\xtwoheadleftarrow", "\\xtofrom"];
    setMathFont("inter");
    const paths = (h: string) => [...h.matchAll(/<path d="([^"]+)"/g)].map((m) => m[1]!);
    for (const command of commands) {
      const html = katex.renderToString(`${command}{abc}`);
      expect(html, command).not.toContain("data-katex-path");
      for (const p of paths(html)) expect(p, command).not.toMatch(/NaN|Infinity|undefined/);
    }
    // the CD environment's arrows (@> @< @=)
    expect(katex.renderToString("\\begin{CD} A @>a>> B @<<< C @= D \\end{CD}", { displayMode: true })).not.toContain("data-katex-path");
    // ⇄ ↠ have small heads (triangles with arrowHeads), ↪ the arrows'; a two-part image is one path in both halves
    const tex = "\\xtofrom{abc} \\xtwoheadrightarrow{abc} \\xhookrightarrow{abc}";
    const [toFrom, , twoHead, hook] = paths(katex.renderToString(tex));
    setMathFont("inter", { arrowHeads: "triangle" });
    const [toFromT, toFromT2, twoHeadT, hookT] = paths(katex.renderToString(tex));
    expect(toFromT2).toBe(toFromT);
    expect(toFromT).not.toBe(toFrom);
    expect(twoHeadT).not.toBe(twoHead);
    expect(hookT).toBe(hook);
  });

  it("raise \\TeX's T and X onto E's middle bar in Inter Math (\\LaTeX's L and A with them), by weight; KaTeX's logos back with classic", () => {
    const logos = () => ["\\TeX", "\\LaTeX", "\\KaTeX"].map((m) => katex.renderToString(m));
    const katexOwn = logos();
    setMathFont("inter", { weight: 100 });
    const [light] = logos();
    setMathFont("inter", { weight: 900 });
    const [heavy] = logos();
    expect(light).not.toBe(katexOwn[0]);
    // the bar is lower at Black: T and X rise less
    expect(heavy).not.toBe(light);
    setMathFont("classic");
    expect(logos()).toEqual(katexOwn);
  });

  it("draw ∉ in Inter Math, and KaTeX's ∈ and slash otherwise", () => {
    expect(katex.renderToString("\\notin")).toContain("llap");
    setMathFont("inter");
    const html = katex.renderToString("\\notin");
    expect(html).not.toContain("llap");
    // a relation (its spacing) holding the one glyph
    expect(html).toContain('<span class="mrel"><span class="mord">∉</span></span>');
  });

  it("draw Inter's arrows for vectors and stretchy arrows", () => {
    const classic = katex.renderToString("\\vec{u} \\overrightarrow{AB} \\Overrightarrow{AB}");
    setMathFont("inter");
    const html = katex.renderToString("\\vec{u} \\overrightarrow{AB} \\Overrightarrow{AB}");
    const paths = (h: string) => [...h.matchAll(/<path d="([^"]+)"/g)].map((m) => m[1]!);
    expect(paths(html)).toHaveLength(3);
    paths(html).forEach((p, i) => {
      expect(p).not.toBe(paths(classic)[i]);
      expect(p).not.toMatch(/NaN|Infinity|undefined/);
    });
    // the boxes are Inter Math's arrows', with room around them: the light arrow's
    // lower than KaTeX's (0.522 em), and the double one as tall (the vector arrow doubled)
    const [over, double] = [...html.matchAll(/viewBox="0 0 400000 ([\d.]+)"/g)].map((m) => Number(m[1]));
    expect(over).toBeLessThan(522);
    expect(double).toBeCloseTo(over!, 0);
    // \vec's arrow as wide as Inter Math's vectors at the weight (they widen with the letters)
    const vec = Number(/viewBox="0 0 ([\d.]+) [\d.]+"/.exec(html)?.[1]);
    expect(vec).toBeCloseTo(vecLength[400]! * 1000, 0);
  });

  it("draw the ovals of \\oiint and \\oiiint round Inter Math's ∬ ∭, in their box, at the weight", () => {
    const oval = (h: string) => {
      const m = /viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*><path d="([^"]+)"/.exec(h);
      return { width: Number(m?.[1]), height: Number(m?.[2]), d: m?.[3] ?? "" };
    };
    // the path's points (x y pairs: M, L, Q, Z only), by contour
    const contours = (d: string) => d.split("M").slice(1).map((c) => [...c.matchAll(/-?[\d.]+/g)].map((n) => Number(n[0])));
    const across = (pts: number[]) => Math.max(...pts.filter((_, i) => i % 2 === 0)) - Math.min(...pts.filter((_, i) => i % 2 === 0));
    const classic = oval(katex.renderToString("\\oiint"));
    setMathFont("inter");
    for (const tex of ["\\oiint", "\\oiiint", "\\displaystyle \\oiint", "\\displaystyle \\oiiint"]) {
      const o = oval(katex.renderToString(tex));
      expect(o.d).not.toBe(classic.d);
      expect(o.d).not.toMatch(/NaN|Infinity|undefined/);
      // an image is cut at its box: the oval stays in it
      const pts = contours(o.d).flat();
      const xs = pts.filter((_, i) => i % 2 === 0);
      const ys = pts.filter((_, i) => i % 2 === 1);
      expect(Math.min(...xs)).toBeGreaterThanOrEqual(0);
      expect(Math.max(...xs)).toBeLessThanOrEqual(o.width);
      expect(Math.min(...ys)).toBeGreaterThanOrEqual(0);
      expect(Math.max(...ys)).toBeLessThanOrEqual(o.height);
    }
    // its stroke (the outer ellipse against the inner one) follows the weight, as ∮'s ring does
    const stroke = (weight: number) => {
      const [outer, inner] = contours(interSvg(weight).path("oiintSize1")!);
      return across(outer!) - across(inner!);
    };
    expect(stroke(900)).toBeGreaterThan(3 * stroke(100));
  });

  it("size \\lgroup and \\lmoustache as ( in Inter Math, and stack them as KaTeX does otherwise", () => {
    const groups = "\\left\\lgroup \\frac{a}{b} \\right\\rgroup \\left\\lmoustache \\dfrac{a}{b} \\right\\rmoustache \\Bigl⟮ x \\Bigr⟯";
    const parens = "\\left( \\frac{a}{b} \\right) \\left( \\dfrac{a}{b} \\right) \\Bigl( x \\Bigr)";
    const sizes = (h: string) => [...h.matchAll(/delimsizing (size\d|mult)/g)].map((m) => m[1]);
    // KaTeX's: Computer Modern's brace pieces, stacked
    expect(katex.renderToString(groups)).toContain("delimsizinginner delim-size4");
    expect(sizes(katex.renderToString(groups))).not.toEqual(sizes(katex.renderToString(parens)));
    setMathFont("inter");
    expect(katex.renderToString(groups)).not.toContain("delimsizinginner");
    expect(sizes(katex.renderToString(groups))).toEqual(sizes(katex.renderToString(parens)));
  });

  it("draw / and \\backslash as tall as ( in Inter Math at every size, the larger ones from its Size fonts (KaTeX never stacks them)", () => {
    for (const font of ["Main-Regular", "Size1-Regular", "Size2-Regular", "Size3-Regular", "Size4-Regular"] as const) {
      const table = inter[font];
      // as tall as the parenthesis of that size, centred as it is
      const [depth, height] = table[0x28]!;
      for (const cp of [0x2f, 0x5c]) {
        expect(table[cp]![0]).toBeCloseTo(depth, 3);
        expect(table[cp]![1]).toBeCloseTo(height, 3);
      }
    }
    const slashes = "\\bigl/ \\Bigl/ \\biggl\\backslash \\Biggl\\backslash \\left/ \\dfrac{a}{b} \\right\\backslash";
    const parens = "\\bigl( \\Bigl( \\biggl( \\Biggl( \\left( \\dfrac{a}{b} \\right)";
    const sizes = (h: string) => [...h.matchAll(/delimsizing (size\d|mult)/g)].map((m) => m[1]);
    setMathFont("inter");
    expect(sizes(katex.renderToString(slashes))).toEqual(sizes(katex.renderToString(parens)));
  });

  it("draw tall | and ‖ as Inter Math's ∣ ∥ drawn out, at any height and at the weight", () => {
    const tex = "\\left| \\frac{a}{b} \\right| \\Bigm\\| \\begin{vmatrix} 1 \\\\ 2 \\\\ 3 \\\\ 4 \\end{vmatrix}";
    // (the fraction's bar an image too in Inter Math)
    const images = (h: string) =>
      [...h.matchAll(/<svg [^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*><path d="([^"]+)"/g)]
        .map((m) => ({ width: Number(m[1]), height: Number(m[2]), d: m[3]! }))
        .filter((img) => !isRule(img.d));
    // KaTeX's: \left| \right|, \Bigm\|, and vmatrix's bars, each one image
    const classic = images(katex.renderToString(tex));
    expect(classic).toHaveLength(5);
    const stroke = (weight: number) => {
      setMathFont("inter", { weight });
      const all = images(katex.renderToString(tex));
      expect(all).toHaveLength(5);
      all.forEach((img, i) => {
        expect(img.d).not.toBe(classic[i]!.d);
        // bars from the top of the image to its bottom
        for (const bar of img.d.match(/M[^Z]+Z/g)!) expect(bar).toMatch(new RegExp(`^M[\\d.]+ 0H[\\d.]+V${img.height}H[\\d.]+Z$`));
      });
      // as wide as Inter Math's ∣, and ‖ two bars as its ∥
      expect(all[0]!.width).toBeCloseTo(bars[weight]!.vert.advance * 1000, 0);
      expect(all[2]!.width).toBeCloseTo(bars[weight]!.doublevert.advance * 1000, 0);
      expect(all[2]!.d.match(/M/g)).toHaveLength(2);
      const [, x0, x1] = /^M([\d.]+) 0H([\d.]+)/.exec(all[0]!.d)!.map(Number);
      return x1! - x0!;
    };
    expect(stroke(900)).toBeGreaterThan(3 * stroke(100));
  });

  it("draw ( [ ⌈ ⌊ { ⟮ ⎰ taller than the largest size as Inter Math's largest drawn out, in their box", () => {
    const column = "\\begin{matrix} 1 \\\\ 2 \\\\ 3 \\\\ 4 \\end{matrix}";
    const pairs = [["(", ")"], ["[", "]"], ["\\lceil", "\\rceil"], ["\\lfloor", "\\rfloor"], ["\\{", "\\}"], ["\\lgroup", "\\rgroup"], ["\\lmoustache", "\\rmoustache"]];
    const tex = pairs.map(([l, r]) => `\\left${l} ${column} \\right${r}`).join(" ");
    const images = (h: string) =>
      [...h.matchAll(/<svg [^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*><path d="([^"]+)"/g)].map((m) => ({ width: Number(m[1]), height: Number(m[2]), d: m[3]! }));
    // KaTeX stacks them past 3 em: ( [ ⌈ ⌊ as one image each, { ⟮ ⎰ from Computer Modern's brace pieces (with images of
    // their stems between, two in a brace)
    expect(images(katex.renderToString(tex))).toHaveLength(8 + 8);
    setMathFont("inter");
    const html = katex.renderToString(tex);
    expect(html).not.toMatch(/[⎧⎨⎩⎫⎬⎭]/);
    const inter = images(html);
    expect(inter).toHaveLength(14);
    // as wide as the largest's advance (the right ones: their left one's, mirrored)
    const names = ["lparen", "rparen", "lbrack", "lbrack", "lceil", "lceil", "lfloor", "lfloor", "lbrace", "lbrace", "lgroup", "lgroup", "lmoustache", "lmoustache"] as const;
    inter.forEach((img, i) => {
      expect(img.d).not.toMatch(/NaN|Infinity|undefined/);
      expect(img.width).toBeCloseTo(talls[400]![names[i]!].advances[4]! * 1000, 0);
      // from the top of its box to the bottom (the path's numbers are x y pairs)
      const ys = [...img.d.matchAll(/-?[\d.]+/g)].map((m) => Number(m[0])).filter((_, j) => j % 2 === 1);
      expect(Math.min(...ys)).toBeCloseTo(0, 0);
      expect(Math.max(...ys)).toBeCloseTo(img.height, 0);
    });
  });

  it("draw \\left \\right delimiters at any height past the text size: one image, between Inter Math's sizes, never a step", () => {
    const sizes = (html: string) => [...html.matchAll(/class="delimsizing (size\d|mult)"/g)].map((m) => m[1]);
    const heights = (html: string) => [...html.matchAll(/<svg [^>]*height="([\d.]+)em"/g)].map((m) => Number(m[1]));
    setMathFont("inter");
    // \bigl… keep KaTeX's sizes; \left… past the text size is one image (⟨ ⟩ / \\ up to the largest)
    expect(sizes(katex.renderToString("\\Bigl( x \\Bigr) \\biggl\\{ x \\biggr\\}"))).toEqual(["size2", "size2", "size3", "size3"]);
    for (const [l, r] of [["(", ")"], ["[", "]"], ["\\{", "\\}"], ["\\langle", "\\rangle"], ["/", "\\backslash"], ["|", "|"]]) {
      let last = 0;
      for (const content of ["x^2", "\\tfrac{a}{b}", "\\dfrac{a}{b}", "\\dfrac{a^2}{b_1}"]) {
        const html = katex.renderToString(`\\left${l} ${content} \\right${r}`, { displayMode: true });
        expect(sizes(html)).toEqual(["mult", "mult"]);
        const [h] = heights(html);
        expect(h).toBeGreaterThan(last);
        last = h!;
      }
      // past the largest, drawn out (⟨ ⟩ / \\ stop at it, as KaTeX's)
      const tall = katex.renderToString(`\\left${l} \\dfrac{\\dfrac{a}{b}}{c} \\right${r}`, { displayMode: true });
      expect(sizes(tall)).toEqual(l === "\\langle" || l === "/" ? ["size4", "size4"] : ["mult", "mult"]);
    }
    // a delimiter mixed between two sizes is as tall as asked, and as KaTeX's sizes at theirs
    const svg = interSvg(400);
    for (const height of [1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3, 3.6]) {
      const [d] = svg.tall("lparen", height * 1000)!;
      const ys = [...d.matchAll(/-?[\d.]+/g)].map((m) => Number(m[0])).filter((_, j) => j % 2 === 1);
      expect(Math.max(...ys) - Math.min(...ys)).toBeCloseTo(height * 1000, 0);
    }
    expect(svg.anyHeight("\\langle")).toBe("langle");
    expect(svg.anyHeight("\\uparrow")).toBeUndefined();
  });

  it("draw the tall delimiters as heavy as the rule from the largest size up, at every weight", () => {
    for (let weight = 100; weight <= 900; weight += 100) {
      for (const name of ["lparen", "lbrack", "lbrace", "lfloor", "lceil", "langle", "slash"] as const) {
        const { sizes, ends } = talls[weight]![name];
        const largest = sizes[sizes.length - 1]!;
        const ys = largest.map((p) => p[1]);
        const [y0, y1] = [Math.min(...ys), Math.max(...ys)];
        // across the middle, or a brace's stem between its point and its lower hook; ⟨ and / across their slant
        const heights = name === "lbrace" ? [0.2, 0.25, 0.3, 0.35].map((t) => y0 + (y1 - y0) * t) : [y0 + (y1 - y0) * (name === "langle" ? 0.25 : 0.5)];
        const across = (y: number) => {
          const [run] = runsAt(largest, ends, y);
          if (name !== "langle" && name !== "slash") return run![1] - run![0];
          const [next] = runsAt(largest, ends, y + 0.01);
          return (run![1] - run![0]) / Math.hypot(1, (next![0] - run![0]) / 0.01);
        };
        const stroke = Math.min(...heights.map(across));
        expect(Math.abs(stroke / rules[weight]! - 1), `${name} at ${weight}`).toBeLessThan(0.02);
      }
    }
  });

  it("set an integral's upper limit where it goes at every weight, its lower one closer past Regular as Inter's letters", () => {
    const italic = (html: string) => Number(/class="mop op-symbol (?:small|large)-op" style="margin-right:([\d.]+)em/.exec(html)?.[1]);
    for (const [size, tex] of [["Size1-Regular", "\\int_a^b"], ["Size2-Regular", "\\displaystyle \\int_a^b"]] as const) {
      const table = operatorItalics[size]![0x222b]!;
      // KaTeX's table holds Regular's
      expect(inter[size][0x222b]![2]).toBe(table[400]);
      for (const weight of [100, 400, 900]) {
        setMathFont("inter", { weight });
        expect(italic(katex.renderToString(tex))).toBeCloseTo(table[weight]!, 4);
      }
      // the advance closer to the limit at Black: the italic correction makes up for it
      expect(table[900]!).toBeGreaterThan(table[400]!);
    }
  });

  it("stack stretched arrows from Inter Math's pieces, with its shafts between them", () => {
    const column = "\\begin{matrix} 1 \\\\ 2 \\\\ 3 \\\\ 4 \\end{matrix}";
    const tex = [["\\uparrow", "\\downarrow"], ["\\Uparrow", "\\Downarrow"], ["\\updownarrow", "\\Updownarrow"]].map(([l, r]) => `\\left${l} ${column} \\right${r}`).join(" ");
    const pieces = (h: string) => h.match(/[↑↓⇑⇓⏐‖]/g);
    const stems = (h: string) =>
      [...h.matchAll(/<svg [^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*><path d="([^"]+)"/g)].map((m) => ({ width: Number(m[1]), height: Number(m[2]), d: m[3]! }));
    const classic = katex.renderToString(tex);
    setMathFont("inter");
    const html = katex.renderToString(tex);
    // KaTeX's pieces (Inter Math's Size1 font draws them), in the same order
    expect(pieces(html)).toEqual(pieces(classic));
    // the shafts between them: Inter Math's, from the top of each image to its bottom (one or two)
    const ours = stems(html);
    expect(ours).toHaveLength(stems(classic).length);
    ours.forEach((stem, i) => {
      expect(stem.d).not.toBe(stems(classic)[i]!.d);
      expect(stem.d).toMatch(new RegExp(`^(M[\\d.]+ 0H[\\d.]+V${stem.height}H[\\d.]+Z){1,2}$`));
    });
  });

  it("come back exactly to KaTeX's when switching back", () => {
    const before = CASES.map((c) => katex.renderToString(c));
    setMathFont("inter", { weight: 600 });
    CASES.forEach((c) => katex.renderToString(c));
    setMathFont("classic");
    expect(CASES.map((c) => katex.renderToString(c))).toEqual(before);
  });
});
