import { radicals, type Point, type Radical } from "./metrics";

/**
 * Inter's √ for KaTeX's \sqrt (the `__setSurd` hook of our KaTeX patch).
 *
 * KaTeX draws every surd as one SVG path (1000 units per em, y down): the sign
 * and its vinculum, a bar that runs off to the right and is clipped to the
 * radicand's width. It picks one of five heights (the normal surd, then four
 * sizes); ours is drawn at any height (`anyHeight`): the normal one up to
 * 1 em, then as tall as the radicand needs. TeX's spaces in a radicand follow
 * the rule's thickness, which follows the weight: with KaTeX's five heights,
 * a radicand growing with the weight made its surd jump from one to the next.
 *
 * Its strokes are the rule's (the minus sign's, the fraction bars') at every
 * weight: Inter's own √ is heavier than its minus up to Regular, lighter past
 * it (0.79 of it at Black). Its entry bar and down-stroke are Inter's √ at the
 * weight whose up-stroke is that thick, larger for the taller surds as
 * Computer Modern's (drawn lighter: their strokes keep the rule's); never
 * heavier than Regular's: past it, Regular's scaled up to the rule's stroke
 * (DESIGN_WEIGHT). The up-stroke is rebuilt for each height, from its bottom
 * up to the vinculum: at Inter's lean for the normal surd (1 em), a little
 * more upright for the taller ones. The vinculum is as thick as the up-stroke.
 */

/** KaTeX's normal surd's height (em), and the height past which a surd's design stops growing (KaTeX's largest size). */
const NORMAL = 1.0;
const LARGEST = 3.0;
/** Of the height above the normal surd's, how much still goes into the up-stroke's lean (taller surds lean as much as 3 em ones). */
const LEAN_GROWTH = 0.25;
/** The entry bar and down-stroke grow as the surd's height to this power (Computer Modern's hardly less than in proportion; past 3 em they stop). */
const HOOK_GROWTH = 0.8;
/** KaTeX's viewBox: units per em, and the length of the vinculum. */
const UNITS = 1000;
const VINCULUM_END = 400000;

export interface Surd {
  /** Drawn at any height: KaTeX asks for the normal surd and for tall ones, never its four sizes. */
  anyHeight: true;
  path(name: string, extraVinculum: number, viewBoxHeight: number, hLinePad: number): string;
  box(name: string, height?: number): { minWidth: number; advanceWidth: number };
}

const weights = Object.keys(radicals)
  .map(Number)
  .sort((a, b) => a - b);

const mix = (a: Point, b: Point, t: number): Point => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];

/** Inter's √ at any weight: linear between the measured ones (100 apart), and drawn on under Thin (linear there too). */
export function radicalAt(weight: number): Radical {
  const w = Math.min(weight, weights[weights.length - 1]!);
  if (radicals[w]) return radicals[w]!;
  const i = Math.max(1, weights.findIndex((x) => x >= w));
  const [lo, hi] = [weights[i - 1]!, weights[i]!];
  const t = (w - lo) / (hi - lo);
  const [a, b] = [radicals[lo]!, radicals[hi]!];
  return {
    bar: a.bar.map((p, i) => mix(p, b.bar[i]!, t)),
    down: a.down.map((p, i) => mix(p, b.down[i]!, t)),
    join: mix(a.join, b.join, t),
    bottomInner: mix(a.bottomInner, b.bottomInner, t),
    bottomRight: mix(a.bottomRight, b.bottomRight, t),
    topLeft: mix(a.topLeft, b.topLeft, t),
    topRight: mix(a.topRight, b.topRight, t),
  };
}

/** Inter's lean of the up-stroke (run over rise). */
const leanOf = (r: Radical) => (r.topRight[0] - r.bottomRight[0]) / (r.topRight[1] - r.bottomRight[1]);
/** Inter's up-stroke thickness, across it. */
const strokeOf = (r: Radical) => (r.topRight[0] - r.topLeft[0]) / Math.hypot(1, leanOf(r));

/** Inter's own √'s stroke at a weight (em): its up-stroke's thickness. */
export function surdStroke(weight: number): number {
  return strokeOf(radicalAt(weight));
}

/** Horizontal extent of a polygon at height y. */
function span(polygon: Point[], y: number): [number, number] {
  const xs: number[] = [];
  polygon.forEach((p, i) => {
    const q = polygon[(i + 1) % polygon.length]!;
    if ((p[1] - y) * (q[1] - y) <= 0 && p[1] !== q[1]) xs.push(p[0] + ((y - p[1]) / (q[1] - p[1])) * (q[0] - p[0]));
  });
  return [Math.min(...xs), Math.max(...xs)];
}

/**
 * The heaviest of Inter's √ whose design the surds take: one whose strokes must be heavier than its (the normal surd
 * past Regular, as heavy as the rule) is it with its strokes thickened (`thickened`). Inter's heavier √ shorten their
 * entry bar against its thickness (twice as long as thick at Regular, 1.4 times at Black): Black's, thickened to the
 * rule, turned it into a low block beside the taller surds' slim angular start.
 */
const DESIGN_WEIGHT = 400;

/**
 * Regular's √ with its entry bar and down-stroke `f` times as thick (the rule's, past Regular's strokes): the bar
 * about its middle, which stays on the axis where Inter sets it, and as much longer, so that it keeps its proportions;
 * the down-stroke drawn on up its slant to the bar's new top, then thickened outwards from its inner edge (its foot
 * stays inside the up-stroke's). The up-stroke is rebuilt at its own thickness.
 */
function thickened(r: Radical, f: number): Radical {
  if (f === 1) return r;
  const ys = r.bar.map((p) => p[1]);
  const xs = r.bar.map((p) => p[0]);
  const [top, bottom, start, end] = [Math.max(...ys), Math.min(...ys), Math.min(...xs), Math.max(...xs)];
  const [middle, half] = [(top + bottom) / 2, ((top - bottom) / 2) * f];
  const raised = middle + half;
  // the down-stroke's top points up their edges (from the neighbour that isn't at the top) to the bar's new top
  const n = r.down.length;
  const drawnOn = r.down.map(([x, y], i): Point => {
    if (Math.abs(y - top) > 1e-6) return [x, y];
    const [a, b] = [r.down[(i + n - 1) % n]!, r.down[(i + 1) % n]!];
    const [px, py] = Math.abs(a[1] - top) > 1e-6 ? a : b;
    return [x + ((x - px) / (y - py)) * (raised - y), raised];
  });
  const down = drawnOn.map(([x, y]): Point => {
    const [, x1] = span(drawnOn, y);
    return [x1 - (x1 - x) * f, y];
  });
  // the bar's end inside the down-stroke's top, its start as much farther as it is thicker
  const [, inner] = span(down, raised);
  const barEnd = Math.min(end, inner);
  const barStart = barEnd - (end - start) * f;
  return {
    ...r,
    bar: r.bar.map(([x, y]): Point => [x < (start + end) / 2 ? barStart : barEnd, y > middle ? raised : middle - half]),
    down,
  };
}

/**
 * Inter's √ `k` times as large, its strokes `stroke` thick: Inter's at the weight whose up-stroke, k times as large,
 * is that thick; past Regular, Regular's with its strokes thickened to it.
 */
function fitted(stroke: number, k: number): Radical {
  const target = stroke / k;
  let r: Radical;
  if (surdStroke(DESIGN_WEIGHT) > target) {
    let [lo, hi] = [weights[0]! - 100, DESIGN_WEIGHT];
    for (let n = 0; n < 40; n++) {
      const mid = (lo + hi) / 2;
      if (surdStroke(mid) < target) lo = mid;
      else hi = mid;
    }
    r = radicalAt((lo + hi) / 2);
  } else {
    r = thickened(radicalAt(DESIGN_WEIGHT), target / surdStroke(DESIGN_WEIGHT));
  }
  const s = (p: Point): Point => [p[0] * k, p[1] * k];
  return {
    bar: r.bar.map(s),
    down: r.down.map(s),
    join: s(r.join),
    bottomInner: s(r.bottomInner),
    bottomRight: s(r.bottomRight),
    topLeft: s(r.topLeft),
    topRight: s(r.topRight),
  };
}

/** The up-stroke's horizontal run for a surd of a height (em), past 3 em that of a 3 em one. */
function run(r: Radical, height: number): number {
  return leanOf(r) * (1 + LEAN_GROWTH * (Math.min(height, LARGEST) - NORMAL));
}

/** The up-stroke `stroke` thick across, from Inter's bottom to a top at `height` (em, y up), leaning by `dx`. */
function upStroke(r: Radical, height: number, dx: number, stroke: number): Point[] {
  const slope = dx / (height - r.bottomRight[1]);
  const width = stroke * Math.hypot(1, slope);
  const topRight: Point = [r.bottomRight[0] + dx, height];
  const topLeft: Point = [topRight[0] - width, height];
  // the left edge starts inside the down-stroke, where Inter's does
  const [inLeft, inRight] = span(r.down, r.join[1]);
  const joinX = topLeft[0] - slope * (height - r.join[1]);
  const join: Point = [Math.min(Math.max(joinX, inLeft + 0.002), inRight - 0.002), r.join[1]];
  return [join, topLeft, topRight, r.bottomRight, r.bottomInner];
}

/** SVG path of polygons in KaTeX's viewBox, all wound the same way (they overlap: no holes). */
function svgPath(polygons: Point[][]): string {
  const area = (pts: Point[]) => pts.reduce((s, p, i) => s + p[0] * pts[(i + 1) % pts.length]![1] - pts[(i + 1) % pts.length]![0] * p[1], 0);
  const f = (v: number) => String(Math.round(v * 10) / 10);
  return polygons
    .map((pts) => (area(pts) < 0 ? [...pts].reverse() : pts))
    .map((pts) => `M${pts.map((p) => `${f(p[0])} ${f(p[1])}`).join("L")}Z`)
    .join("");
}

/** Inter's √, its strokes and vinculum `ruleThickness` thick (em): the rule's at a weight. */
export function interSurd(ruleThickness: number): Surd {
  // the √ for a surd's height, larger for the taller ones (the same past 3 em)
  const signs = new Map<number, Radical>();
  const sign = (height: number) => {
    const h = Math.min(Math.max(height, NORMAL), LARGEST);
    if (!signs.has(h)) signs.set(h, fitted(ruleThickness, h ** HOOK_GROWTH));
    return signs.get(h)!;
  };
  // the surd's height, its vinculum's top over its bottom (em): the normal one's, or a tall one's (KaTeX asks for no
  // other with `anyHeight`)
  const heightOf = (name: string, extraVinculum: number, viewBoxHeight: number, hLinePad: number) =>
    name === "sqrtMain" ? NORMAL + extraVinculum : (viewBoxHeight - hLinePad) / UNITS;

  return {
    anyHeight: true,
    path(name, extraVinculum, viewBoxHeight, hLinePad) {
      const height = heightOf(name, extraVinculum, viewBoxHeight, hLinePad);
      const r = sign(height);
      const t = ruleThickness + extraVinculum;
      const up = upStroke(r, height, run(r, height), ruleThickness);
      const vinculum: Point[] = [
        [up[1]![0], height],
        [VINCULUM_END / UNITS, height],
        [VINCULUM_END / UNITS, height - t],
        [up[1]![0], height - t],
      ];
      // em, y up → viewBox, y down
      const bottom = hLinePad + height * UNITS;
      const toBox = (pts: Point[]) => pts.map(([x, y]): Point => [x * UNITS, bottom - y * UNITS]);
      return svgPath([r.bar, r.down, up, vinculum].map(toBox));
    },
    box(name, height) {
      const h = name === "sqrtMain" ? NORMAL : Math.max(height ?? NORMAL, NORMAL);
      const r = sign(h);
      const dx = run(r, h);
      const slope = dx / (h - r.bottomRight[1]);
      const right = r.bottomRight[0];
      return {
        // the radicand starts at the stroke's inner corner, under the vinculum
        advanceWidth: right + slope * (h - ruleThickness),
        minWidth: right + dx + 0.01,
      };
    },
  };
}
