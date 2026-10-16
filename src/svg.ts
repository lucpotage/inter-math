import { accentBottom, arrows, bars, images, ovals, tallHeights, talls, underlines, vecLength, xHeight, type ArrowName, type BarName, type Bars, type Images, type Outline, type Oval, type OvalName, type Parted, type Point, type Tall, type TallName } from "./metrics";

/**
 * Inter's arrows for KaTeX's SVG images (the `__setSvgDesign` hook of our
 * KaTeX patch).
 *
 * Stretchy arrows: KaTeX draws a 400 em long arrow and crops it to the width
 * needed, from the head's side. Ours grow the way Inter grows its own (its calt
 * turns -> into → and --> into ⟶: the same outline, the head moved along): the
 * head kept, the shaft drawn out to 400 em.
 * - over and under arrows (\overrightarrow{AB}…, vectors): Inter's →, its
 *   head smaller than the arrows' (the same at every weight) but its barbs as
 *   thick, its shaft lighter (build/build.py); \Overrightarrow's, that arrow
 *   doubled, as ⟹ doubles ⟶;
 * - arrows on the line (\xrightarrow, \xLeftarrow…): Inter's long arrows
 *   (⟶ ⟵ ⟹ ⟸); harpoons (\xrightharpoonup…) Inter Math's ⇀ ⇁ ↼ ↽ drawn
 *   out, and the pairs (\xrightleftharpoons \xleftrightharpoons) its ⇌ ⇋,
 *   each harpoon towards its head; the others (\xhookrightarrow \xmapsto
 *   \xtofrom \xtwoheadrightarrow \xlongequal…) Inter Math's ↪ ↦ ⇄ ↠ =…
 *   drawn out across their shaft's straight run, one path for both halves
 *   of a two-part image (KaTeX shows each half from its own side), in a box
 *   centred on the axis with room for the ink both ways (↪'s hook rises).
 * A harpoon sits in its arrow's box, its shaft where the arrow's is (KaTeX's
 * share one box too): boxed to its own ink, the one barb it keeps, it sat
 * lower over its content than the arrow.
 * Their box keeps, above and below, the gap Inter keeps between lowercase and
 * its accents (KaTeX sets the box right on the letters; under arrows and
 * \xrightarrow stay centred).
 *
 * \vec: that arrow, its shaft a little wider than a lowercase letter, its
 * head starting where Inter's accents start over lowercase (KaTeX places the
 * image as it does any accent).
 *
 * \oiint \oiiint: KaTeX draws ∬ ∭ with an oval over them, an image in a box
 * that starts at the integral's origin, OVAL_DROP under its baseline. Ours is
 * ∮'s ring drawn out sideways to pass the outer stems of Inter Math's ∬ ∭
 * (build/build.py): its box as wide as the integral, or the oval if wider.
 *
 * Delimiters at any height (\left \right past the text size): KaTeX takes a
 * delimiter from four sizes (1.2 to 3 em), then stacks pieces in steps of the
 * repeated one. TeX's spaces follow the rule, the rule the weight: content
 * growing with the weight made its delimiters jump from size to size. Ours are
 * one image as tall as the content needs (`anyHeight`: our KaTeX patch routes
 * them here):
 * - ( ) [ ] ⌈ ⌉ ⌊ ⌋ { } ⟮ ⟯ ⎰ ⎱: Inter Math's five sizes (the text size's,
 *   then KaTeX's four) mixed between the two around the height (the same
 *   points at each, build/build.py); past the largest, the largest drawn out
 *   as TeX's tall ones are, a straight stretch between its ends: a
 *   parenthesis cut where its curves turn vertical, a bracket across its
 *   stem, a brace in its stem's straight stretches above and under its point;
 * - ⟨ ⟩ / \: the same up to the largest, where they stop, as KaTeX's;
 * - | ‖: Inter Math's ∣ ∥ drawn out to the height, their bars and box as the
 *   glyph's at the weight (optical size 14, as the other images: the glyph
 *   itself is narrower in the display size).
 * Stretched arrows (\left\uparrow…) still stack the Size1 font's pieces
 * (build/ams_arrow_glyphs.py), with Inter Math's ⏐ ‖ between them as tall as
 * needed.
 *
 * Over and under their content (build/build.py, accent_images()), with
 * Inter's gap between lowercase and its accents on the content's side:
 * - \widetilde \utilde: Inter's ͠ (its double tilde), \widehat its ᷍ (its
 *   double circumflex), \widecheck that upside down, drawn out to the width
 *   of a box sized for the base (KaTeX stretches the image to it: a box near
 *   the base's width keeps its stroke);
 * - \overgroup \undergroup: ⟮ turned a quarter, as tall and as thick as
 *   Inter's ͜; \overbrace \underbrace: { turned a quarter; both drawn out
 *   along their straight stretches;
 * - \overbracket \underbracket \overlinesegment \underlinesegment: lines
 *   as thick as Inter's underline, their ends upright and as thick (a
 *   segment's as tall as the vector arrows' heads, the line through their
 *   middle: ↔ over its content with ends for heads, as TeX's are 0.334 em);
 * - \overleftharpoon \overrightharpoon: the vector arrow keeping its upper
 *   barb, as ⇀ keeps →'s, in the vector arrow's box.
 */

export interface SvgDesign {
  path(name: string): string | undefined;
  static(name: string): [string, number, number] | undefined;
  image(label: string, data: KatexImage): KatexImage;
  /** A tall delimiter KaTeX draws as one image (its name, the height in viewBox units): its path and width. */
  tall(label: string, height: number): [string, number] | undefined;
  /**
   * A delimiter (as \left names it) drawn as one image at any height past its text size: its image's name (`tall`),
   * or undefined (KaTeX's sizes and stacks).
   */
  anyHeight(delim: string): string | undefined;
  /** The height (em) at which the ones that don't grow past the largest size (⟨ ⟩ / \) stop. */
  largest: number;
  /**
   * The straight piece KaTeX draws between a tall delimiter's glyphs (its character, the height in viewBox units): its
   * path, and its width (em) at the weight, the glyphs' own (KaTeX's metrics are Regular's: narrower, the piece was
   * centred off the glyphs' stem where a column centres them, as CD does).
   */
  inner(ch: string, height: number): [string, number] | undefined;
  /** A wide accent's box (its label, KaTeX's path name): the path's name, the viewBox's width and height, the height (em). */
  wide(label: string, pathName: string): [string, number, number, number] | undefined;
}
/** KaTeX's stretchy images: path names, minimum width (em), viewBox height, alignment. */
export type KatexImage = [string[], number, number, string?];

/** KaTeX's delimiters (as \left names them) drawn at any height, and their image (`tall`). */
const ANY_HEIGHT: Record<string, string> = {
  "(": "lparen", "\\lparen": "lparen", ")": "rparen", "\\rparen": "rparen",
  "[": "lbrack", "\\lbrack": "lbrack", "]": "rbrack", "\\rbrack": "rbrack",
  "\\lfloor": "lfloor", "\u230a": "lfloor", "\\rfloor": "rfloor", "\u230b": "rfloor",
  "\\lceil": "lceil", "\u2308": "lceil", "\\rceil": "rceil", "\u2309": "rceil",
  "\\{": "lbrace", "\\lbrace": "lbrace", "\\}": "rbrace", "\\rbrace": "rbrace",
  "\\langle": "langle", "\\rangle": "rangle", "/": "slash", "\\backslash": "backslash",
  "\\lgroup": "lgroup", "\u27ee": "lgroup", "\\rgroup": "rgroup", "\u27ef": "rgroup",
  "\\lmoustache": "lmoustache", "\u23b0": "lmoustache", "\\rmoustache": "rmoustache", "\u23b1": "rmoustache",
  "|": "vert", "\\vert": "vert", "\\lvert": "vert", "\\rvert": "vert",
  "\\|": "doublevert", "\\Vert": "doublevert", "\\lVert": "doublevert", "\\rVert": "doublevert",
};
/** The right delimiters drawn as their left one mirrored (the build leaves them out of `talls`). */
const MIRRORED: Record<string, TallName> = {
  rbrack: "lbrack", rfloor: "lfloor", rceil: "lceil", rbrace: "lbrace", rangle: "langle", rgroup: "lgroup", rmoustache: "lmoustache", backslash: "slash",
};
/** The straight pieces KaTeX draws between a tall delimiter's glyphs (its innerPath), and Inter Math's piece for each. */
const INNER: Record<string, BarName> = { "\u23aa": "brace", "\u23d0": "arrow", "\u2016": "double" };
/** KaTeX's stretchy paths, and ours (light ones for over and under arrows), with Inter's arrows for them. */
const STRETCHY: Record<string, [ArrowName, "right" | "left"]> = {
  rightarrow: ["right", "right"],
  leftarrow: ["left", "left"],
  doublerightarrow: ["doubleRight", "right"],
  doubleleftarrow: ["doubleLeft", "left"],
  lightrightarrow: ["vec", "right"],
  lightleftarrow: ["vec", "left"],
  lightdoublerightarrow: ["vecDouble", "right"],
  lightleftharpoon: ["vecHarpoon", "left"],
  lightrightharpoon: ["vecHarpoon", "right"],
  rightharpoon: ["harpoonUpRight", "right"],
  rightharpoondown: ["harpoonDownRight", "right"],
  leftharpoon: ["harpoonUpLeft", "left"],
  leftharpoondown: ["harpoonDownLeft", "left"],
};
/** The arrow whose box a harpoon sits in, its shaft where the arrow's is. */
const FRAME: Partial<Record<ArrowName, ArrowName>> = {
  vecHarpoon: "vec",
  harpoonUpRight: "right",
  harpoonDownRight: "right",
  harpoonUpLeft: "left",
  harpoonDownLeft: "left",
};
/** KaTeX's paired harpoons, both halves of each image: Inter Math's ⇌ ⇋ (which way the upper harpoon points). */
const PAIRS: Record<string, [ArrowName, "right" | "left"]> = {
  leftharpoondownplus: ["harpoonsRightLeft", "right"],
  rightharpoonplus: ["harpoonsRightLeft", "right"],
  leftharpoonplus: ["harpoonsLeftRight", "left"],
  rightharpoondownplus: ["harpoonsLeftRight", "left"],
};
/** KaTeX's other arrows on the line, by their image's label: the Inter Math glyph drawn out for it (DRAWN_PATH + name). */
const DRAWN: Record<string, ArrowName> = {
  xhookrightarrow: "hookRight",
  xhookleftarrow: "hookLeft",
  xmapsto: "mapsTo",
  xtofrom: "toFrom",
  xtwoheadrightarrow: "twoHeadRight",
  xtwoheadleftarrow: "twoHeadLeft",
  xlongequal: "equals",
  // the CD environment's @= (its arrows are \\cdrightarrow \\cdleftarrow: ⟶ ⟵ already)
  "\\cdlongequal": "equals",
};
const DRAWN_PATH = "interMath:";
/** KaTeX's images over or under their content: our light arrows instead of its. */
const OVER_UNDER = new Set(["overrightarrow", "underrightarrow", "overleftarrow", "underleftarrow", "overleftrightarrow", "underleftrightarrow", "Overrightarrow", "overleftharpoon", "overrightharpoon"]);
const LIGHT: Record<string, string> = {
  rightarrow: "lightrightarrow",
  leftarrow: "lightleftarrow",
  doublerightarrow: "lightdoublerightarrow",
  leftharpoon: "lightleftharpoon",
  rightharpoon: "lightrightharpoon",
};
/** KaTeX's wide accents: our box's width for its path's size (the base: one character, two or three, four or five, more), em. */
const WIDE_WIDTH: Record<string, number> = { 1: 0.6, 2: 1.1, 3: 2.2, 4: 3.3 };
/** KaTeX's images over or under their content that we draw: their paths, and which of our shapes each is. */
const GROUPS: Record<string, "over" | "under"> = { leftgroup: "over", rightgroup: "over", leftgroupunder: "under", rightgroupunder: "under" };
const BRACES: Record<string, "over" | "under"> = {
  leftbrace: "over",
  midbrace: "over",
  rightbrace: "over",
  leftbraceunder: "under",
  midbraceunder: "under",
  rightbraceunder: "under",
};
const BRACKETS: Record<string, ["over" | "under", "left" | "right"]> = {
  leftbracketover: ["over", "left"],
  rightbracketover: ["over", "right"],
  leftbracketunder: ["under", "left"],
  rightbracketunder: ["under", "right"],
};
const SEGMENTS: Record<string, "left" | "right"> = { leftlinesegment: "left", rightlinesegment: "right" };
/** How long the upright ends of \overbracket are (em: KaTeX's bracket's; a segment's are the vector arrows' heads). */
const BRACKET_END = 0.29;
/** How far under the integral's baseline KaTeX sets the box of its oval (display style: 0.08 em). */
const OVAL_DROP: Record<OvalName, number> = { oiintSize1: 0, oiiintSize1: 0, oiintSize2: 0.08, oiiintSize2: 0.08 };
/** KaTeX's viewBox: units per em, and the length of a stretchy image. */
const UNITS = 1000;
const LENGTH = 400000;

const weights = Object.keys(arrows)
  .map(Number)
  .sort((a, b) => a - b);

/** A table measured at weights 100 apart, at any weight (linear: Inter's own outlines are, between masters). */
function at<T>(table: Record<number, T>, weight: number, mix: (a: T, b: T, t: number) => T): T {
  const w = Math.min(Math.max(weight, weights[0]!), weights[weights.length - 1]!);
  const hi = weights.find((x) => x >= w)!;
  const lo = [...weights].reverse().find((x) => x <= w)!;
  return hi === lo ? table[lo]! : mix(table[lo]!, table[hi]!, (w - lo) / (hi - lo));
}

const mixOutline = (a: Outline, b: Outline, t: number): Outline => ({
  ...a,
  points: a.points.map((p, i): Point => [p[0] + (b.points[i]![0] - p[0]) * t, p[1] + (b.points[i]![1] - p[1]) * t]),
});

/** Left to right (Inter's accent arrow only points right). */
function mirrored(o: Outline): Outline {
  return { ...o, points: o.points.map(([x, y]): Point => [-x, y]) };
}

function bounds(o: Outline): [number, number, number, number] {
  const xs = o.points.map((p) => p[0]);
  const ys = o.points.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}

/** A TrueType outline as an SVG path (quadratic curves; consecutive off-curve points imply the on-curve one between). */
function svgPath(o: Outline, map: (p: Point) => Point): string {
  const f = (v: number) => String(Math.round(v * 10) / 10);
  const pt = (p: Point) => `${f(p[0])} ${f(p[1])}`;
  const mid = (a: Point, b: Point): Point => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  let d = "";
  let start = 0;
  for (const end of o.ends) {
    const pts = o.points.slice(start, end + 1).map(map);
    const on = o.on.slice(start, end + 1);
    start = end + 1;
    // begin on an on-curve point
    const first = on.indexOf(1);
    const ring = [...pts.slice(first), ...pts.slice(0, first)];
    const flags = [...on.slice(first), ...on.slice(0, first)];
    d += `M${pt(ring[0]!)}`;
    for (let i = 1; i <= ring.length; i++) {
      const p = ring[i % ring.length]!;
      if (flags[i % ring.length]) {
        d += `L${pt(p)}`;
        continue;
      }
      // off-curve: up to the next on-curve point, or the midpoint with the next off-curve one
      const next = ring[(i + 1) % ring.length]!;
      const nextOn = flags[(i + 1) % ring.length];
      d += `Q${pt(p)} ${pt(nextOn ? next : mid(p, next))}`;
      if (nextOn) i++;
    }
    d += "Z";
  }
  return d;
}

const ovalsAt = (weight: number) =>
  at(ovals, weight, (a, b, t) =>
    Object.fromEntries(
      Object.keys(a).map((k) => {
        const n = k as OvalName;
        return [n, { outline: mixOutline(a[n].outline, b[n].outline, t), advance: a[n].advance + (b[n].advance - a[n].advance) * t }];
      }),
    ) as Record<OvalName, Oval>,
  );

const barsAt = (weight: number) =>
  at(bars, weight, (a, b, t) =>
    Object.fromEntries(
      Object.keys(a).map((k) => {
        const n = k as BarName;
        const mix = (u: number, v: number) => u + (v - u) * t;
        return [n, { bars: a[n].bars.map(([x0, x1], i) => [mix(x0, b[n].bars[i]![0]), mix(x1, b[n].bars[i]![1])]), advance: mix(a[n].advance, b[n].advance) }];
      }),
    ) as Record<BarName, Bars>,
  );

const mixPoint = (a: Point, b: Point, t: number): Point => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
const tallsAt = (weight: number) =>
  at(talls, weight, (a, b, t) =>
    Object.fromEntries(
      Object.keys(a).map((k) => {
        const n = k as TallName;
        return [
          n,
          {
            ...a[n],
            sizes: a[n].sizes.map((points, s) => points.map((p, i) => mixPoint(p, b[n].sizes[s]![i]!, t))),
            advances: a[n].advances.map((v, s) => v + (b[n].advances[s]! - v) * t),
          },
        ];
      }),
    ) as Record<TallName, Tall>,
  );

const mixParted = (a: Parted, b: Parted, t: number): Parted => ({ outline: mixOutline(a.outline, b.outline, t), parts: a.parts });
const imagesAt = (weight: number) =>
  at(images, weight, (a, b, t): Images => ({
    wideTilde: mixOutline(a.wideTilde, b.wideTilde, t),
    wideHat: mixOutline(a.wideHat, b.wideHat, t),
    group: mixParted(a.group, b.group, t),
    brace: mixParted(a.brace, b.brace, t),
  }));

/** The vectors' arrows with triangle heads (setMathFont's arrowHeads), in their place. */
const TRIANGLES: [ArrowName, ArrowName][] = [
  ["vec", "vecTriangle"],
  ["vecDouble", "vecDoubleTriangle"],
  ["vecHarpoon", "vecHarpoonTriangle"],
  ["toFrom", "toFromTriangle"],
  ["twoHeadRight", "twoHeadRightTriangle"],
  ["twoHeadLeft", "twoHeadLeftTriangle"],
];

const arrowsAt = (weight: number, triangles = false) => {
  const set = at(arrows, weight, (a, b, t) =>
    Object.fromEntries(Object.keys(a).map((k) => [k, mixOutline(a[k as ArrowName], b[k as ArrowName], t)])) as Record<ArrowName, Outline>,
  );
  // a copy: at a measured weight the set is the table's own
  return triangles ? { ...set, ...Object.fromEntries(TRIANGLES.map(([name, triangle]) => [name, set[triangle]])) } : set;
};

/** Inter's arrows at a weight, the vectors' heads triangles with `triangles`. */
export function interSvg(weight: number, triangles = false): SvgDesign {
  const set = arrowsAt(weight, triangles);
  const accent = at(accentBottom, weight, (a, b, t) => a + (b - a) * t);
  const gap = accent - xHeight;
  // an arrow's box: its ink (a harpoon's arrow's) with Inter's accent gap above and below
  const height = (name: ArrowName) => {
    const [, y0, , y1] = bounds(set[FRAME[name] ?? name]);
    return (y1 - y0 + 2 * gap) * UNITS;
  };

  /** An outline drawn out to KaTeX's length towards its head, its top `top` (em) a gap under the box's. */
  function drawnOut400(o: Outline, towards: "right" | "left", top: number): string {
    const [x0, , x1] = bounds(o);
    const eps = 1e-4;
    return svgPath(o, ([x, y]) => {
      const vy = (top - y + gap) * UNITS;
      // the end of the shaft goes out to the far side; everything else keeps its distance to the tip
      if (towards === "right") return [Math.abs(x - x0) < eps ? 0 : LENGTH - (x1 - x) * UNITS, vy];
      return [Math.abs(x - x1) < eps ? LENGTH : (x - x0) * UNITS, vy];
    });
  }

  function stretchy(name: ArrowName, towards: "right" | "left"): string {
    const o = (name === "vec" || name === "vecHarpoon") && towards === "left" ? mirrored(set[name]) : set[name];
    return drawnOut400(o, towards, bounds(set[FRAME[name] ?? name])[3]);
  }

  // ⇌ ⇋: each harpoon (a contour) drawn out towards its head, the upper one `upper`'s way; one path for both halves
  function pair(name: ArrowName, upper: "right" | "left"): string {
    const o = set[name];
    const [, y0, , y1] = bounds(o);
    let path = "";
    let start = 0;
    for (const end of o.ends) {
      const c: Outline = { points: o.points.slice(start, end + 1), on: o.on.slice(start, end + 1), ends: [end - start] };
      start = end + 1;
      const [, cy0, , cy1] = bounds(c);
      const above = cy0 + cy1 > y0 + y1;
      path += drawnOut400(c, above === (upper === "right") ? "right" : "left", y1);
    }
    return path;
  }

  // ↪ ↩ ↦ ⇄ ↠ ↞ =: drawn out to KaTeX's length across the widest run where it has no point (its shaft's straight
  // stretch), each side keeping its distance to its end; the box centred on the axis (KaTeX centres it there), as
  // high as the ink reaches either way plus the accent gap; and how far each end reaches in from its side (em)
  const [, ry0, , ry1] = bounds(set.right);
  const axis = (ry0 + ry1) / 2;
  const drawnCache = new Map<ArrowName, { path: string; height: number; ends: [number, number] }>();
  function drawn(name: ArrowName) {
    const known = drawnCache.get(name);
    if (known) return known;
    const o = set[name];
    const xs = [...new Set(o.points.map((p) => p[0]))].sort((a, b) => a - b);
    let [from, to] = [xs[0]!, xs[0]!];
    for (let i = 1; i < xs.length; i++) if (xs[i]! - xs[i - 1]! > to - from) [from, to] = [xs[i - 1]!, xs[i]!];
    const cut = (from + to) / 2;
    const [x0, y0, x1, y1] = bounds(o);
    const half = Math.max(y1 - axis, axis - y0) + gap;
    const out = {
      path: svgPath(o, ([x, y]) => [x < cut ? (x - x0) * UNITS : LENGTH - (x1 - x) * UNITS, (axis + half - y) * UNITS]),
      height: Math.round(2 * half * UNITS),
      ends: [from - x0, x1 - to] as [number, number],
    };
    drawnCache.set(name, out);
    return out;
  }

  // \vec's arrow: a little wider than a lowercase letter, as the letters are at the weight
  const span = at(vecLength, weight, (a, b, t) => a + (b - a) * t);
  const vec = (() => {
    const o = set.vec;
    const [x0, y0, x1, y1] = bounds(o);
    const top = accent + (y1 - y0);
    const eps = 1e-4;
    const path = svgPath(o, ([x, y]) => [
      (Math.abs(x - x0) < eps ? 0 : span - (x1 - x)) * UNITS,
      (top - (accent + y - y0)) * UNITS,
    ]);
    return { path, box: ["vec", span, top] as [string, number, number] };
  })();

  // \oiint \oiiint: the oval in its box, the box centred on it (its bottom OVAL_DROP under the baseline)
  const ovalSet = ovalsAt(weight);
  const isOval = (name: string): name is OvalName => name in OVAL_DROP;
  const oval = (name: OvalName) => {
    const { outline, advance } = ovalSet[name];
    const [, y0, x1, y1] = bounds(outline);
    const drop = OVAL_DROP[name];
    const height = 2 * ((y0 + y1) / 2 + drop);
    return {
      path: svgPath(outline, ([x, y]) => [x * UNITS, (height - drop - y) * UNITS]),
      // rounded up to a unit: the path is rounded too, and an image is cut at its box
      box: [name, Math.ceil(Math.max(advance, x1) * UNITS) / UNITS, height] as [string, number, number],
    };
  };

  // tall | and ‖: the bars from the top of the box to its bottom, the box as wide as the glyph
  const barSet = barsAt(weight);
  const isBar = (label: string): label is BarName => label === "vert" || label === "doublevert";
  const round = (v: number) => Math.round(v * UNITS * 10) / 10;
  const barsPath = (name: BarName, height: number) =>
    barSet[name].bars.map(([x0, x1]) => `M${round(x0)} 0H${round(x1)}V${height}H${round(x0)}Z`).join("");
  // a delimiter at a height: between two sizes, both mixed; past the largest, the largest drawn out (its upper part
  // moved up, its lower part down, the middle of a brace staying); a right one as its left one mirrored
  const tallSet = tallsAt(weight);
  const largest = tallHeights[tallHeights.length - 1]!;
  function delimiterAt(label: string, height: number): { outline: Outline; advance: number } | undefined {
    const name = label in tallSet ? (label as TallName) : MIRRORED[label];
    if (!name) return undefined;
    const { sizes, on, ends, parts, advances } = tallSet[name];
    const last = sizes.length - 1;
    let points: Point[];
    let advance: number;
    if (height >= largest) {
      const reach = (height - largest) / 2;
      points = sizes[last]!.map(([x, y], i): Point => [x, y + (parts[i] === 2 ? reach : parts[i] === 0 ? -reach : 0)]);
      advance = advances[last]!;
    } else {
      const k = Math.max(0, Math.min(last - 1, tallHeights.findIndex((h) => h > height) - 1));
      const t = Math.max(0, (height - tallHeights[k]!) / (tallHeights[k + 1]! - tallHeights[k]!));
      points = sizes[k]!.map((p, i) => mixPoint(p, sizes[k + 1]![i]!, t));
      advance = advances[k]! + (advances[k + 1]! - advances[k]!) * t;
    }
    if (name !== label) points = points.map(([x, y]): Point => [advance - x, y]);
    return { outline: { points, on, ends }, advance };
  }

  // over and under their content: Inter's gap between lowercase and its accents on the content's side, lines as
  // thick as Inter's underline
  const img = imagesAt(weight);
  const line = at(underlines, weight, (a, b, t): [number, number] => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])[1];
  const L = LENGTH / UNITS;
  const toPath = (o: Outline) => svgPath(o, ([x, y]) => [x * UNITS, y * UNITS]);
  const rect = (x0: number, y0: number, x1: number, y1: number) => `M${round(x0)} ${round(y0)}H${round(x1)}V${round(y1)}H${round(x0)}Z`;

  // a wide accent: drawn out to its box's width, its ink a gap over the content (\widetilde \widehat \widecheck)
  // or, under it, at the top of its box (\utilde: KaTeX keeps 0.12 em between)
  const wides = new Map<string, string>();
  function wide(label: string, pathName: string): [string, number, number, number] | undefined {
    const index = pathName.slice(-1);
    const o = label === "widetilde" || label === "utilde" ? img.wideTilde : label === "widehat" || label === "widecheck" ? img.wideHat : undefined;
    const width = WIDE_WIDTH[index];
    if (!o || !width) return undefined;
    const [x0, y0, x1, y1] = bounds(o);
    const under = label === "utilde";
    const top = under ? 0 : gap;
    const boxHeight = Math.round((y1 - y0 + gap + top) * UNITS) / UNITS;
    const name = `${label}${index}`;
    const flip = label === "widecheck";
    wides.set(name, toPath({ ...o, points: o.points.map(([x, y]): Point => [((x - x0) / (x1 - x0)) * width, top + (flip ? y - y0 : y1 - y)]) }));
    return [name, Math.round(width * UNITS), Math.round(boxHeight * UNITS), boxHeight];
  }

  // a group or a brace drawn out to KaTeX's length: its ends at the box's ends, a brace's point in the middle;
  // turned over for under its content
  function drawnOut(p: Parted, under: boolean, margin: number) {
    const [x0, y0, x1, y1] = bounds(p.outline);
    const shift = [0, (L - (x1 - x0)) / 2, L - (x1 - x0)];
    const points = p.outline.points.map(([x, y], i): Point => [x - x0 + shift[p.parts[i]!]!, margin + (under ? y - y0 : y1 - y)]);
    return { path: toPath({ ...p.outline, points }), height: Math.round((y1 - y0 + 2 * margin) * UNITS) };
  }
  const groups = { over: drawnOut(img.group, false, gap), under: drawnOut(img.group, true, gap) };
  const braces = { over: drawnOut(img.brace, false, 0), under: drawnOut(img.brace, true, 0) };

  // \overbracket \underbracket: the line at the far side, its ends upright towards the content
  const bracketHeight = Math.round((BRACKET_END + line) * UNITS);
  function bracket(side: "over" | "under", end: "left" | "right"): string {
    const t = line, e = BRACKET_END;
    const [lineTop, endTop, endBottom] = side === "over" ? [0, 0, t + e] : [e, 0, e + t];
    const [ex0, ex1] = end === "left" ? [0, t] : [L - t, L];
    return rect(0, lineTop, L, lineTop + t) + rect(ex0, endTop, ex1, endBottom);
  }
  // \overlinesegment \underlinesegment: the line through the middle of upright ends as tall as the vector arrows' heads
  // (the angle ones, whatever the arrows' heads), a gap from the content on either side
  const [, hy0, , hy1] = bounds(triangles ? arrowsAt(weight).vec : set.vec);
  const segmentEnd = hy1 - hy0;
  const segmentHeight = Math.round((segmentEnd + 2 * gap) * UNITS);
  function segment(end: "left" | "right"): string {
    const t = line, e = segmentEnd, middle = gap + e / 2;
    const [ex0, ex1] = end === "left" ? [0, t] : [L - t, L];
    return rect(0, middle - t / 2, L, middle + t / 2) + rect(ex0, gap, ex1, gap + e);
  }

  return {
    path(name) {
      if (name === "vec") return vec.path;
      if (name.startsWith(DRAWN_PATH)) return drawn(name.slice(DRAWN_PATH.length) as ArrowName).path;
      if (isOval(name)) return oval(name).path;
      const s = STRETCHY[name];
      if (s) return stretchy(...s);
      if (name in PAIRS) return pair(...PAIRS[name]!);
      if (wides.has(name)) return wides.get(name);
      if (name in GROUPS) return groups[GROUPS[name]!].path;
      if (name in BRACES) return braces[BRACES[name]!].path;
      if (name in BRACKETS) return bracket(...BRACKETS[name]!);
      if (name in SEGMENTS) return segment(SEGMENTS[name]!);
      return undefined;
    },
    static(name) {
      if (isOval(name)) return oval(name).box;
      return name === "vec" ? vec.box : undefined;
    },
    image(label, data) {
      if (!data) return data;
      const own = DRAWN[label];
      if (own) {
        // never so short that an end is cut: a half as long as the longer end, one image as long as the end it shows
        const { height, ends } = drawn(own);
        const shortest = data[0].length === 2 ? 2 * Math.max(...ends) : ends[data[3] === "xMinYMin" ? 0 : 1];
        return [data[0].map(() => DRAWN_PATH + own), Math.max(data[1], shortest), height, data[3]];
      }
      const paths = OVER_UNDER.has(label) ? data[0].map((p) => LIGHT[p] ?? p) : data[0];
      // images made of our arrows alone (a hook would sit in another box)
      if (paths.every((p) => p in STRETCHY)) return [paths, data[1], Math.max(...paths.map((p) => height(STRETCHY[p]![0]))), data[3]];
      const box = (h: number): KatexImage => [data[0], data[1], h, data[3]];
      if (data[0].every((p) => p in PAIRS)) return box(height(PAIRS[data[0][0]!]![0]));
      if (data[0].every((p) => p in GROUPS)) return box(groups.over.height);
      if (data[0].every((p) => p in BRACES)) return box(braces.over.height);
      if (data[0].every((p) => p in BRACKETS)) return box(bracketHeight);
      if (data[0].every((p) => p in SEGMENTS)) return box(segmentHeight);
      return data;
    },
    wide,
    tall(label, height) {
      if (isBar(label)) return [barsPath(label, height), round(barSet[label].advance)];
      const delimiter = delimiterAt(label, height / UNITS);
      if (!delimiter) return undefined;
      // from the top of the box down (the ink is as tall as the box)
      const [, , , top] = bounds(delimiter.outline);
      return [svgPath(delimiter.outline, ([x, y]) => [x * UNITS, (top - y) * UNITS]), round(delimiter.advance)];
    },
    anyHeight: (delim) => ANY_HEIGHT[delim],
    largest,
    inner(ch, height) {
      // a brace's stem, an arrow's shaft or shafts (each box as wide as Inter Math's ⎪ ⏐ ‖: KaTeX reads the metrics)
      const name = INNER[ch];
      return name ? [barsPath(name, height), barSet[name].advance] : undefined;
    },
  };
}
