import { readFileSync } from "node:fs";
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
    expect(css).toMatch(/"Inter Math AMS"[^}]*unicode-range:[^;]*U\+2204\b/);
  });

  it("sends Inter Math every AMS symbol it draws, and only those", () => {
    // its faces: the upright font for the AMS symbols whose design it has, InterMath-AMS for the AMS font's own
    // designs at code points Main has its own at (\varnothing…), and \Bbbk
    const faces = [...css.matchAll(/font-family: "Inter Math AMS";[^}]*src: url\("([^"]+)"\)[^}]*unicode-range: ([^;]+);/g)];
    expect(faces.map((f) => f[1])).toEqual(["../fonts/InterMath-Upright.woff2", "../fonts/InterMath-AMS.woff2"]);
    const listed = faces.map((f) => f[2]!.split(",").flatMap((part) => {
      const [first, last = first] = part.trim().replace(/^U\+/i, "").split("-").map((hex) => parseInt(hex, 16));
      return Array.from({ length: last! - first! + 1 }, (_, i) => first! + i);
    }));
    // no code point in two faces
    expect(listed[0]!.filter((cp) => listed[1]!.includes(cp))).toEqual([]);
    // the blackboard letters, KaTeX's AMS A-Z, have a face of their own
    const drawn = Object.keys(inter["AMS-Regular"]).map(Number).filter((cp) => cp < 0x41 || cp > 0x5a);
    expect(listed.flat().sort((a, b) => a - b)).toEqual(drawn.sort((a, b) => a - b));
  });

  it("targets the classes KaTeX puts on blackboard letters", () => {
    expect(katex.renderToString("\\mathbb{R}")).toContain('class="mord mathbb">R');
    expect(css).toMatch(/\.katex \.mathbb,\s*\.inter-math \.katex \.textbb \{\s*font-family: "Inter Math Blackboard"/);
    expect(css).toMatch(/"Inter Math Blackboard";\s*src: url\("\.\.\/fonts\/InterMath-Blackboard\.woff2"\)/);
  });

  it("sets sans serif in Inter Math, with its metrics", () => {
    for (const [tex, cls] of [["\\mathsf{A}", "mathsf"], ["\\textsf{A}", "textsf"], ["\\mathsfit{A}", "mathsfit"], ["\\textbf{\\textsf{A}}", "textsf"]]) {
      expect(katex.renderToString(tex!)).toContain(cls!);
      expect(css).toMatch(new RegExp(`\\.katex \\.${cls}[,\\s][^}]*font-family: "Inter Math", KaTeX_SansSerif`));
    }
    for (const font of ["SansSerif-Regular", "SansSerif-Bold", "SansSerif-Italic"] as const) expect(inter[font][0x41]).toBeDefined();
  });

  it("targets the classes KaTeX puts on root indices", () => {
    expect(katex.renderToString("\\sqrt[3]{x}")).toContain('class="katex-root"');
    expect(css).toContain(".katex-root");
  });
});
