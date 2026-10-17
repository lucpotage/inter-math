import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

type CharData = [number, number, number, { p: string; ic?: number; sk?: number }];
type Delimiter = { dir: string; sizes: number[]; variants?: number[]; stretch?: number[]; stretchv?: number[]; HDW: number[]; c?: number };
type FontClass = {
  NAME: string;
  defaultChars: Record<string, Record<number, CharData>>;
  defaultDelimiters: Record<number, Delimiter>;
  defaultSizeVariants: string[];
  defaultStretchVariants: string[];
  defaultVariants: string[][];
  defaultParams: Record<string, number>;
};

/** src/mathjax-font/svg.js (build/mathjax.py), run against the parts of MathJax it takes. */
function load(): { font: FontClass; config: Record<string, unknown> } {
  const code = readFileSync(new URL("../src/mathjax-font/svg.js", import.meta.url), "utf8");
  let registered: { _: { output: { fonts: Record<string, { svg_ts: { InterMathFont: FontClass } }> } } } | undefined;
  let config: Record<string, unknown> = {};
  class SvgFontData {
    static OPTIONS = {};
  }
  const FontData = { defaultVariants: [["normal"], ["italic", "normal"], ["-tex-calligraphic", "italic"]], defaultCssFonts: {}, defaultAccentMap: {}, defaultParams: { quad: 1 } };
  const MathJax = {
    startup: {},
    _: {
      components: {
        global: {
          combineWithMathJax: (value: typeof registered) => (registered = value),
          combineDefaults: (_: unknown, __: string, value: Record<string, unknown>) => (config = value),
        },
      },
      output: { svg: { FontData: { SvgFontData } }, common: { FontData: { FontData }, Direction: { V: "v", H: "h" } } },
    },
  };
  new Function("MathJax", code)(MathJax);
  return { font: registered!._.output.fonts["inter-math"]!.svg_ts.InterMathFont, config };
}

describe("MathJax's font (src/mathjax-font/svg.js)", () => {
  const { font, config } = load();
  const chars = font.defaultChars;

  it("registers as the font of its folder's name, its class the SVG output's font data", () => {
    expect(font.NAME).toBe("InterMath");
    expect(config).toMatchObject({ output: { font: "[inter-math]" }, svg: { fontData: font } });
  });

  it("has the letters MathJax reaches through Unicode's math alphabets, and the accents its TeX input sets", () => {
    // x, italic x, bold A, double-struck R, sans serif A, italic α; ˆ ˜ ¯ ` ´ and the vector arrow
    for (const cp of [0x78, 0x1d465, 0x1d400, 0x211d, 0x1d5a0, 0x1d6fc, 0x2c6, 0x2dc, 0xaf, 0x60, 0xb4, 0x20d7]) {
      expect(chars.normal![cp], `U+${cp.toString(16).toUpperCase()}`).toBeDefined();
    }
  });

  it("gives every character a path MathJax can take (it adds the first M itself)", () => {
    for (const [variant, table] of Object.entries(chars)) {
      for (const [cp, [h, d, w, data]] of Object.entries(table)) {
        expect([h, d, w].every(Number.isFinite), `${variant} ${cp}`).toBe(true);
        expect(data.p, `${variant} ${cp}`).not.toMatch(/^M/);
      }
    }
  });

  it("has every size and piece its delimiters name, in the variants they name", () => {
    for (const [cp, delim] of Object.entries(font.defaultDelimiters)) {
      const c = delim.c ?? Number(cp);
      expect(delim.sizes.length, cp).toBeLessThanOrEqual(font.defaultSizeVariants.length);
      delim.sizes.forEach((_, i) => {
        const variant = font.defaultSizeVariants[delim.variants?.[i] ?? i]!;
        expect(chars[variant]?.[c], `${cp}: size ${i} in ${variant}`).toBeDefined();
      });
      (delim.stretch ?? []).forEach((piece, i) => {
        if (!piece) return;
        const variant = font.defaultStretchVariants[delim.stretchv?.[i] ?? 0]!;
        expect(chars[variant]?.[piece], `${cp}: piece ${i} (${variant} ${piece})`).toBeDefined();
      });
    }
    // the delimiters, big operators, radical and what stretches sideways
    for (const cp of [0x28, 0x7b, 0x7c, 0x221a, 0x2211, 0x222b, 0x2192, 0x23de, 0x302, 0x2015]) expect(font.defaultDelimiters[cp], String(cp)).toBeDefined();
  });

  it("takes TeX's parameters from the font, in its em", () => {
    for (const [name, value] of Object.entries(font.defaultParams)) expect(Number.isFinite(value), name).toBe(true);
    // Inter's x-height (1118 of 2048), and rules as thick as the minus sign
    expect(font.defaultParams.x_height).toBeCloseTo(1118 / 2048, 3);
    expect(font.defaultParams.rule_thickness).toBeGreaterThan(0.05);
  });
});
