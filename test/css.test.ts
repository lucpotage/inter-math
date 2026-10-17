import { existsSync, readFileSync } from "node:fs";
import katex from "katex";
import { describe, expect, it } from "vitest";
import { inter } from "../src/metrics";

const css = readFileSync(new URL("../src/inter-math.css", import.meta.url), "utf8");

describe("inter-math.css", () => {
  it("targets the classes KaTeX puts on scripts", () => {
    // x^{2^{3}}: a script (size3) holding a second-level script (size1)
    const html = katex.renderToString("x^{2^{3}}");
    for (const size of ["size3", "size1"]) {
      const cls = new RegExp(`class="(katex-sizing) reset-size\\d+ ${size}\\b`).exec(html)?.[1];
      expect(cls, `KaTeX's sizing class for ${size}`).toBeDefined();
      expect(css).toContain(`.${cls}.${size}`);
    }
  });

  it("targets the classes KaTeX puts on big operators and larger delimiters", () => {
    expect(katex.renderToString("\\displaystyle \\sum")).toContain("op-symbol large-op");
    expect(katex.renderToString("\\textstyle \\sum")).toContain("op-symbol small-op");
    expect(katex.renderToString("\\left(\\frac{1}{2}\\right)", { displayMode: true })).toMatch(/delimsizing size\d/);
    for (const cls of [".op-symbol.large-op", ".op-symbol.small-op", ".delimsizing.size1", ".delimsizing.size4"]) expect(css).toContain(cls);
  });

  it("targets the class KaTeX puts on AMS symbols, for the ones Inter Math draws", () => {
    expect(katex.renderToString("\\nexists")).toContain('class="mord amsrm">∄');
    expect(katex.renderToString("\\leqslant")).toContain('class="mrel amsrm">⩽');
    expect(css).toContain(".katex .amsrm");
    expect(css).toMatch(/"Inter Math KaTeX AMS"[^}]*unicode-range:[^;]*U\+2204\b/);
  });

  it("sends Inter Math every AMS symbol it draws, and only those", () => {
    // the one font: the AMS font's own designs at code points Main has its own at (\varnothing…) and \Bbbk through
    // the AMS role's feature, the upright ones for the rest
    const faces = [...css.matchAll(/font-family: "Inter Math KaTeX AMS";[^}]*src: url\("([^"]+)"\)[^}]*unicode-range: ([^;]+);/g)];
    expect(faces.map((f) => f[1])).toEqual(["../fonts/InterMathVariable.woff2"]);
    const listed = faces[0]![2]!.split(",").flatMap((part) => {
      const [first, last = first] = part.trim().replace(/^U\+/i, "").split("-").map((hex) => parseInt(hex, 16));
      return Array.from({ length: last! - first! + 1 }, (_, i) => first! + i);
    });
    // the blackboard letters, KaTeX's AMS A-Z, are the blackboard role's
    const drawn = Object.keys(inter["AMS-Regular"]).map(Number).filter((cp) => cp < 0x41 || cp > 0x5a);
    expect(listed.sort((a, b) => a - b)).toEqual(drawn.sort((a, b) => a - b));
  });

  it("targets the classes KaTeX puts on blackboard letters", () => {
    expect(katex.renderToString("\\mathbb{R}")).toContain('class="mord mathbb">R');
    expect(css).toMatch(/\.katex \.mathbb,\s*\.inter-math \.katex \.textbb \{\s*font-family: "Inter Math KaTeX", KaTeX_AMS;\s*--inter-math-role: "KTXB";/);
  });

  it("loads the OpenType math font, in KaTeX's em, with KaTeX_Main's ascent and descent", () => {
    // KaTeX's em: Inter's 2048 units in 2332 (build.py's axis_upem: Inter's + − = on TeX's axis); its ascent and
    // descent build.py's ASCENT and DESCENT, overrides which size-adjust scales
    const faces = [...css.matchAll(/@font-face \{([^}]*)\}/g)].map((m) => m[1]!);
    expect(faces.length).toBe(3);
    for (const face of faces) {
      expect(face).toContain('src: url("../fonts/InterMathVariable.woff2") format("woff2");');
      const value = (name: string) => Number(new RegExp(`${name}: ([\\d.]+)%;`).exec(face)?.[1]) / 100;
      expect(value("size-adjust")).toBeCloseTo(2048 / 2332, 6);
      expect(value("ascent-override") * value("size-adjust")).toBeCloseTo(0.903, 3);
      expect(value("descent-override") * value("size-adjust")).toBeCloseTo(0.272, 3);
      expect(value("line-gap-override")).toBe(0);
    }
    expect(existsSync(new URL("../fonts/InterMathVariable.woff2", import.meta.url))).toBe(true);
  });

  it("turns on the role of the font KaTeX picks, through the font's features", () => {
    // the features build/opentype.py gives KaTeX's roles
    const tags = new Set([...readFileSync(new URL("../build/opentype.py", import.meta.url), "utf8").matchAll(/"(KTX[A-Z0-9])"/g)].map((m) => m[1]));
    expect(tags.size).toBe(8);
    const roles = [...css.matchAll(/--inter-math-role: "([^"]+)"/g)].map((m) => m[1]);
    for (const tag of roles) expect(tags, tag).toContain(tag);
    expect(css).toMatch(/\.inter-math \.katex,\s*\.inter-math \.katex \* \{\s*font-feature-settings: var\(--inter-math-role\), var\(--inter-math-scripts\), var\(--inter-math-heads\);/);
    // every class KaTeX's stylesheet slants is the italic role, every one it sets upright again the upright one (in
    // KaTeX's order, so that the same class wins)
    const katexCss = readFileSync(new URL("../node_modules/katex/dist/katex.css", import.meta.url), "utf8");
    const styled = [...katexCss.matchAll(/((?:\.katex \.[\w-]+,?\s*)+)\{[^}]*font-style: (italic|normal);/g)]
      .flatMap((m) => [...m[1]!.matchAll(/\.katex \.([\w-]+)/g)].map((c) => [c[1]!, m[2]!] as const));
    expect(styled.length).toBeGreaterThan(5);
    const role = (cls: string) => [...css.matchAll(new RegExp(`\\.katex \\.${cls}[,\\s][^{]*\\{[^}]*--inter-math-role: "([^"]+)"`, "g"))].at(-1)?.[1];
    for (const [cls, style] of styled) expect(role(cls), cls).toBe(style === "italic" ? "KTXI" : "KTXM");
  });

  it("sets sans serif in Inter Math, with its metrics", () => {
    for (const [tex, cls] of [["\\mathsf{A}", "mathsf"], ["\\textsf{A}", "textsf"], ["\\mathsfit{A}", "mathsfit"], ["\\textbf{\\textsf{A}}", "textsf"]]) {
      expect(katex.renderToString(tex!)).toContain(cls!);
      expect(css).toMatch(new RegExp(`\\.katex \\.${cls}[,\\s][^}]*font-family: "Inter Math KaTeX", KaTeX_SansSerif`));
    }
    for (const font of ["SansSerif-Regular", "SansSerif-Bold", "SansSerif-Italic"] as const) expect(inter[font][0x41]).toBeDefined();
  });

  it("targets the classes KaTeX puts on root indices", () => {
    expect(katex.renderToString("\\sqrt[3]{x}")).toContain('class="katex-root"');
    expect(css).toContain(".katex-root");
  });
});

describe("mathml.css", () => {
  const sheet = (name: string) => readFileSync(new URL(`../src/${name}`, import.meta.url), "utf8");
  const faces = (css: string) => [...css.matchAll(/@font-face \{[^}]*font-family: "Inter Math";[^}]*src: url\("([^"]+)"\)[^}]*font-weight: ([^;]+);/g)];

  it("gives Inter Math a face per weight, Thin to Black, each a font the build writes", () => {
    const found = faces(sheet("mathml.css"));
    expect(found.map((f) => f[2])).toEqual(["100", "200", "300", "400", "500", "600", "700", "800", "900"]);
    for (const [, url] of found) expect(existsSync(new URL(url!, new URL("../src/", import.meta.url))), url).toBe(true);
  });

  it("gives the variable font every weight", () => {
    const [face, ...more] = faces(sheet("mathml-variable.css"));
    expect(more).toEqual([]);
    expect(face![2]).toBe("100 900");
    expect(existsSync(new URL(face![1]!, new URL("../src/", import.meta.url)))).toBe(true);
  });

  it("sets scripts in the font's script forms, which browsers don't apply", () => {
    for (const name of ["mathml.css", "mathml-variable.css"]) {
      const css = sheet(name);
      // scripts and text style's fractions take ssty's first alternate, their scripts and roots' indices the second
      expect(css).toMatch(/:is\(msub, msup, msubsup, mmultiscripts, munder, mover, munderover\) > :not\(:first-child\),[^{]*\{\s*font-feature-settings: "ssty" 1;/);
      expect(css).toMatch(/mroot > :not\(:first-child\) \{\s*font-feature-settings: "ssty" 2;/);
    }
  });

  it("sets math in Inter Math, at its text's weight, apart from KaTeX's stylesheet", () => {
    // browsers' own stylesheet (MathML Core) and Temml's set math at the normal weight
    for (const name of ["mathml.css", "mathml-variable.css"]) expect(sheet(name)).toMatch(/math \{\s*font-family: "Inter Math", math;\s*font-weight: inherit;/);
    // KaTeX's faces have names of their own: both stylesheets can share a page
    expect(css).not.toMatch(/font-family: "Inter Math"[;,]/);
  });
});
