import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import katex from "katex";
import { afterEach, describe, expect, it } from "vitest";
import { KATEX_AXIS, KATEX_FRACTION_SHIFTS, mathFont, setMathFont, withMathFont } from "../src/index";
import { classic, inter, versions } from "../src/metrics";

const katexDir = dirname(createRequire(import.meta.url).resolve("katex/package.json"));

/** KaTeX's metric tables, as installed (a JS object literal). */
function installedTables(): Record<string, Record<string, number[]>> {
  const js = readFileSync(join(katexDir, "src/fontMetricsData.js"), "utf8");
  return JSON.parse(js.slice(js.indexOf("{"), js.lastIndexOf("}") + 1).replace(/,(\s*[}\]])/g, "$1"));
}

/** The strut of a rendering: height + depth in em (KaTeX sizes it from the metrics). */
const strut = (html: string) => Number(/class="katex-strut" style="height:([\d.]+)em/.exec(html)?.[1]);
const extent = ([depth, height]: number[]) => depth! + height!;

describe("metrics", () => {
  afterEach(() => setMathFont("classic"));

  it("were generated from the installed KaTeX (rebuild the font after a KaTeX update)", () => {
    const pkg = JSON.parse(readFileSync(join(katexDir, "package.json"), "utf8"));
    expect(versions.katex).toBe(pkg.version);
    const tables = installedTables();
    for (const [font, table] of Object.entries(classic)) {
      expect(Object.fromEntries(Object.entries(table).map(([k, v]) => [k, v]))).toEqual(tables[font]);
    }
  });

  it("shift fractions from KaTeX's own values (src/fontMetrics.ts)", () => {
    const src = readFileSync(join(katexDir, "src/fontMetrics.ts"), "utf8");
    const value = (name: string) => JSON.parse(new RegExp(`${name}: (\\[[^\\]]+\\])`).exec(src)![1]!);
    for (const [name, sizes] of Object.entries(KATEX_FRACTION_SHIFTS)) expect(value(name), name).toEqual(sizes);
    expect(value("axisHeight")).toEqual([KATEX_AXIS, KATEX_AXIS, KATEX_AXIS]);
  });

  it("give every glyph sane values", () => {
    for (const [font, table] of Object.entries(inter)) {
      // the larger delimiters' fonts are taller by design
      const tallest = font.startsWith("Size") ? 3.5 : 1.5;
      for (const [cp, [depth, height, italic, , width]] of Object.entries(table)) {
        expect([depth, height, italic, width].every((v) => Number.isFinite(v) && v >= 0), `U+${Number(cp).toString(16)}`).toBe(true);
        expect(height + depth).toBeLessThan(tallest);
      }
    }
  });

  it("switch KaTeX's layout", () => {
    const classicX = strut(katex.renderToString("x"));
    setMathFont("inter");
    expect(mathFont()).toBe("inter");
    const interX = strut(katex.renderToString("x"));
    expect(interX).toBeCloseTo(extent(inter["Math-Italic"][120]!), 4);
    expect(interX).not.toBeCloseTo(classicX, 3);
    // what Inter Math lacks is still laid out with KaTeX's metrics (the first of these it lacks)
    const lacked = ([["\\wp", 8472], ["\\spadesuit", 9824], ["\\lmoustache", 9136]] as const).find(([, cp]) => !(cp in inter["Main-Regular"]));
    expect(lacked, "a Main glyph Inter Math lacks").toBeDefined();
    const [command, cp] = lacked!;
    expect(strut(katex.renderToString(command))).toBeCloseTo(extent(classic["Main-Regular"][cp]!), 4);
    setMathFont("classic");
    expect(strut(katex.renderToString("x"))).toBeCloseTo(classicX, 4);
  });

  it("render with another font for a moment", () => {
    const html = withMathFont("inter", () => katex.renderToString("x"));
    expect(strut(html)).toBeCloseTo(extent(inter["Math-Italic"][120]!), 4);
    expect(mathFont()).toBe("classic");
  });
});
