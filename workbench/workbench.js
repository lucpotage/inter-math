// What the workbench's pages share: KaTeX rendered in Computer Modern or in Inter Math, and the weight and size
// controls in each page's header (kept across visits).
import "katex/dist/katex.min.css";
import "../src/inter-math.css";
import "./workbench.css";
import katex from "katex";
import { INTER_MATH_CLASS, withMathFont } from "../src/index.ts";
import { coverage, drawn } from "../src/provenance.ts";

export { INTER_MATH_CLASS };

const covered = Object.fromEntries(Object.entries(coverage).map(([role, cps]) => [role, new Set(cps)]));

/**
 * The code points a family's faces give it, their unicode-ranges together (null: all of them). "Inter Math AMS" is
 * two faces: the upright font for the AMS symbols whose design it has, InterMath-AMS for the AMS font's own designs
 * at code points Main has its own at (\varnothing…) and \Bbbk; the other AMS symbols stay KaTeX_AMS's.
 */
const ranges = new Map();
function faceRange(family) {
  if (!ranges.has(family)) {
    const faces = [...document.fonts].filter((f) => f.family.replace(/^["']|["']$/g, "") === family);
    // not known yet (the stylesheet still loading): ask again next time
    if (!faces.length) return null;
    const parts = !faces.length || faces.some((f) => f.unicodeRange === "U+0-10FFFF") ? null : faces.flatMap((f) => f.unicodeRange.split(","));
    ranges.set(family, parts && new Set(parts.flatMap((part) => {
      const [first, last = first] = part.trim().replace(/^U\+/i, "").split("-").map((hex) => parseInt(hex, 16));
      return Array.from({ length: last - first + 1 }, (_, i) => first + i);
    })));
  }
  return ranges.get(family);
}

/** The Inter Math font a glyph is set in (from its element's style) if that font has it; null: a KaTeX font's. */
export function roleOf(style, cp) {
  const family = style.fontFamily.split(",")[0].trim().replace(/^["']|["']$/g, "");
  const role =
    family === "Inter Math" ? (style.fontStyle === "italic" ? "Italic" : "Upright")
    : family === "Inter Math AMS" ? (covered.AMS.has(cp) ? "AMS" : "Upright")
    : family === "Inter Math Blackboard" ? "Blackboard"
    : /^Inter Math Size[1-4]$/.test(family) ? `Size${family.at(-1)}`
    : null;
  const range = role && faceRange(family);
  return role && covered[role].has(cp) && (!range || range.has(cp)) ? role : null;
}

/**
 * Whether a glyph Inter Math sets (in font `role`) is Inter's: its own as it is, an alternate of it, or one only
 * resized, moved, turned or drawn out (`kept`: the same contours and points, about the same shape: build.py).
 */
export function fromInter(role, cp) {
  if (!role) return false;
  const how = drawn[role][cp];
  return !how || how.kind === "alternate" || how.kept === true;
}

/**
 * Inter's glyphs in Inter Math's renderings under `root` set in blue (`from-inter`), so that what is left in the
 * text colour is what was drawn for Inter Math; KaTeX's own glyphs (what Inter Math leaves to its fonts) and the
 * images KaTeX draws (rules, surds, stretchy arrows) are left as they are. Runs of characters of the same kind are
 * wrapped together, so that a word keeps its kerning.
 */
export function markInter(root) {
  for (const html of root.querySelectorAll(".katex-html")) {
    const walker = document.createTreeWalker(html, NodeFilter.SHOW_TEXT);
    const nodes = [];
    for (let node = walker.nextNode(); node; node = walker.nextNode()) nodes.push(node);
    for (const node of nodes) {
      if (node.parentElement.classList.contains("from-inter")) continue;
      const style = getComputedStyle(node.parentElement);
      const chars = [...node.textContent];
      // each character Inter's or not; spaces go with the run they are in
      const marks = chars.map((char) => (/[\s\u200b]/.test(char) ? null : fromInter(roleOf(style, char.codePointAt(0)), char.codePointAt(0))));
      if (!marks.includes(true)) continue;
      const parts = document.createDocumentFragment();
      let run = "";
      let kind = false;
      const flush = () => {
        if (!run) return;
        if (kind) {
          const span = document.createElement("span");
          span.className = "from-inter";
          span.textContent = run;
          parts.append(span);
        } else {
          parts.append(run);
        }
        run = "";
      };
      chars.forEach((char, i) => {
        const mark = marks[i] ?? kind;
        if (mark !== kind) {
          flush();
          kind = mark;
        }
        run += char;
      });
      flush();
      node.replaceWith(parts);
    }
  }
}

// \includegraphics would fetch an image from the web; the rest of KaTeX's trusted commands only mark up
const OPTIONS = { throwOnError: false, strict: "ignore", output: "html", trust: (context) => context.command !== "\\includegraphics" };

/** KaTeX's rendering of some LaTeX: in Computer Modern ("classic"), or in Inter Math at a weight ("inter"). */
export function render(tex, font, weight = 400, displayMode = false) {
  return withMathFont(font, () => katex.renderToString(tex, { ...OPTIONS, displayMode }), { weight, arrowHeads: arrowHeads() });
}

/** The small arrows' heads the pages render with: ?heads=triangle, or what the header's switch chose last. */
function arrowHeads() {
  try {
    return (asked.get("heads") ?? localStorage.getItem("inter-math-workbench.heads")) === "triangle" ? "triangle" : "angle";
  } catch {
    return "angle";
  }
}

const escapes = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
export const escapeHtml = (s) => String(s).replace(/[&<>"]/g, (c) => escapes[c]);

// the page's address may set the controls (?weight=700&size=48&theme=dark: a capture by a headless browser), before
// what was chosen last
const asked = new URLSearchParams(location.search);

function stored(key, fallback) {
  try {
    const v = Number(asked.get(key) ?? localStorage.getItem(`inter-math-workbench.${key}`));
    return Number.isFinite(v) && v > 0 ? v : fallback;
  } catch {
    return fallback;
  }
}

function storedTheme() {
  try {
    const v = asked.get("theme") ?? localStorage.getItem("inter-math-workbench.theme");
    return v === "dark" || v === "light" ? v : null;
  } catch {
    return null;
  }
}

function store(key, value) {
  try {
    localStorage.setItem(`inter-math-workbench.${key}`, String(value));
  } catch {
    // private windows: the controls just start over
  }
}

/**
 * The weight (100-900) and size (px) sliders, added to the page's header: they set --inter-math-weight (read by
 * inter-math.css) and --math-size on the page, and call `onWeight` when the weight settles (KaTeX lays Inter
 * Math out again: its rules, surds and arrows follow the weight). With them, white on black (true dark) or
 * black on white: the system's until chosen.
 */
export function controls(onWeight) {
  const header = document.querySelector("header");
  const state = { weight: stored("weight", 400), size: stored("size", 24) };
  const slider = (label, key, min, max, step, unit) => {
    const wrap = document.createElement("label");
    wrap.className = "control";
    wrap.innerHTML = `${label} <input type="range" min="${min}" max="${max}" step="${step}" value="${state[key]}"> <output>${state[key]}${unit}</output>`;
    header.append(wrap);
    return [wrap.querySelector("input"), wrap.querySelector("output")];
  };
  const [weight, weightOut] = slider("Weight", "weight", 100, 900, 10, "");
  const [size, sizeOut] = slider("Size", "size", 12, 72, 1, " px");
  const dark = document.createElement("label");
  dark.className = "control";
  dark.innerHTML = `<input type="checkbox"> White on black`;
  header.append(dark);
  // the small arrows' heads: the pages render once, so the switch renders them again
  const heads = document.createElement("label");
  heads.className = "control";
  heads.innerHTML = `<input type="checkbox"${arrowHeads() === "triangle" ? " checked" : ""}> Triangle heads`;
  header.append(heads);
  heads.querySelector("input").addEventListener("change", (e) => {
    store("heads", e.target.checked ? "triangle" : "angle");
    const url = new URL(location.href);
    url.searchParams.delete("heads");
    location.href = url.href;
  });
  const toggle = dark.querySelector("input");
  toggle.checked = (storedTheme() ?? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";
  const theme = () => {
    document.documentElement.dataset.theme = toggle.checked ? "dark" : "light";
  };
  toggle.addEventListener("change", () => {
    store("theme", toggle.checked ? "dark" : "light");
    theme();
  });
  theme();
  const root = document.documentElement.style;
  const apply = () => {
    root.setProperty("--inter-math-weight", state.weight);
    root.setProperty("--math-size", `${state.size}px`);
  };
  let timer = 0;
  weight.addEventListener("input", () => {
    state.weight = Number(weight.value);
    weightOut.textContent = state.weight;
    store("weight", state.weight);
    apply();
    clearTimeout(timer);
    timer = setTimeout(() => onWeight?.(state.weight), 150);
  });
  size.addEventListener("input", () => {
    state.size = Number(size.value);
    sizeOut.textContent = `${state.size} px`;
    store("size", state.size);
    apply();
  });
  apply();
  return state;
}
