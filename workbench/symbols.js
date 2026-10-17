// KaTeX's documented symbols and functions (katex.org/docs, extracted by katex-docs.mjs), in Computer Modern and in
// Inter Math, with what Inter Math draws each of its glyphs from: Inter's own glyphs (shown in Inter itself), or
// nothing (KaTeX's fonts) where Inter Math has no glyph.
import { drawn, svgDrawn } from "../src/provenance.ts";
import docs from "./katex-docs.json";
import { INTER_MATH_CLASS, ROLE_FEATURES, controls, escapeHtml, fromInter, markInter, render, roleOf } from "./workbench.js";

const $ = (id) => document.getElementById(id);
const KIND = { alternate: "Inter's alternate" };
const INTER_MATH_FAMILIES = /^"?Inter Math[^,]*"?\s*,\s*/;

$("source").textContent = `KaTeX ${docs.katex}, from ${docs.source}`;

function rowsOf(view) {
  return view === "table"
    ? docs.table.map((e, i) => ({ key: `t${i}`, group: e.group, name: e.name, tex: e.tex }))
    : docs.supported.flatMap((s, i) => s.items.map((tex, j) => ({ key: `s${i}.${j}`, group: s.section, tex })));
}

/** A rendered formula's glyphs that Inter Math draws (Inter's own, as they are, left out) or leaves to KaTeX. */
function glyphsOf(cell, tex) {
  const found = new Map();
  // KaTeX's error message, when it can't render the snippet: no glyphs
  const html = cell.querySelector(".katex-html");
  if (!html) return [];
  const walker = document.createTreeWalker(html, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const style = getComputedStyle(node.parentElement);
    for (const char of node.textContent) {
      if (/[\s​]/.test(char)) continue;
      const cp = char.codePointAt(0);
      const role = roleOf(style, cp);
      const how = role ? drawn[role][cp] : undefined;
      if (role && !how) continue;
      // a KaTeX font: the element's family without Inter Math's
      const font = role ? "" : `font-family:${style.fontFamily.replace(INTER_MATH_FAMILIES, "")};font-style:${style.fontStyle}`;
      // one entry per font: the same character in two of KaTeX's fonts is two glyphs (k in \texttt and \Bbbk)
      found.set(role ? `${role}:${char}` : `${font}:${char}`, { char, role, how, font });
    }
  }
  for (const [command, how] of Object.entries(svgDrawn)) {
    if (new RegExp(`${command.replace(/\\/g, "\\\\")}(?![a-zA-Z])`).test(tex)) found.set(command, { command, how });
  }
  // KaTeX's own images Inter Math leaves (our patch marks their paths while Inter Math is set): Computer Modern's
  for (const path of html.querySelectorAll("[data-katex-path]")) found.set(`image:${path.dataset.katexPath}`, { image: path.dataset.katexPath });
  return [...found.values()];
}

/** The KaTeX font a fallback is set in, from its style ("KaTeX_AMS", "KaTeX_Main italic"…). */
const katexFont = (font) => {
  const family = /font-family:\s*"?([^,";]+)/.exec(font)?.[1] ?? "";
  return /font-style:italic/.test(font) ? `${family} italic` : family;
};
const interMathFont = (role) =>
  `font-family:'Inter Math KaTeX${role === "AMS" ? " AMS" : ""}';font-feature-settings:"${ROLE_FEATURES[role]}"${role === "Italic" ? ";font-style:italic" : ""}`;
const referenceFont = (g) =>
  `${g.italic ? "font-style:italic;" : ""}${g.features ? `font-feature-settings:${g.features.split(" ").map((f) => `"${f}"`).join(",")};` : ""}`;
const references = (from) => from.map((g) => `<span class="glyph reference" style="${referenceFont(g)}">${escapeHtml(g.text)}</span>`).join("");

function chip(g) {
  if (g.image) {
    return `<span class="chip katex" title="KaTeX's own image (its path ${escapeHtml(g.image)}): Computer Modern's, not redrawn"><code>${escapeHtml(g.image)}</code>KaTeX image</span>`;
  }
  if (g.command) {
    return `<span class="chip" title="KaTeX's SVG image for ${escapeHtml(g.command)}, drawn by Inter Math"><code>${escapeHtml(g.command)}</code><span class="arrow">←</span>${references(g.how.from)}<span class="how">${escapeHtml(g.how.how)}</span></span>`;
  }
  if (!g.role) {
    return `<span class="chip katex" title="Inter Math has no glyph for U+${g.char.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}: KaTeX's font"><span class="glyph" style="${g.font}">${escapeHtml(g.char)}</span>KaTeX</span>`;
  }
  const how = g.how.how ?? (g.how.kind === "redrawn" ? (g.how.kept ? "Inter's, resized or drawn out" : "Inter's, reshaped") : KIND[g.how.kind]) ?? "";
  // blue: Inter's glyph, only resized, moved, turned or drawn out (as in the formulas)
  const inter = fromInter(g.role, g.char.codePointAt(0)) ? " from-inter" : "";
  return `<span class="chip" title="${g.role}, ${g.how.kind}"><span class="glyph${inter}" style="${interMathFont(g.role)}">${escapeHtml(g.char)}</span><span class="arrow">←</span>${references(g.how.from)}<span class="how">${escapeHtml(how)}</span></span>`;
}

/**
 * Room before each formula for what KaTeX sets left of its box (\mathclap's limit, wider than its ∑), which its cell
 * (scrolling what is too wide for it) would clip: a margin as wide, in ems (the size control scales it). Rows hidden
 * have no layout: measured as they show.
 */
function makeRoom(rows) {
  for (const k of rows.querySelectorAll("tr:not([hidden]) .katex:has(.clap, .llap)")) {
    k.style.marginLeft = "";
    const box = k.getBoundingClientRect();
    const left = Math.min(...[...k.querySelectorAll(".katex-html *")].map((e) => e.getBoundingClientRect().left));
    if (left < box.left) k.style.marginLeft = `${(box.left - left) / parseFloat(getComputedStyle(k).fontSize)}em`;
  }
}

/** A snippet in KaTeX, in display mode where KaTeX sets it only there ({CD}). */
const renderSnippet = (tex, font, weight) => render(tex, font, weight, /\\begin\{CD\}/.test(tex));

let rows = [];
let byKey = new Map();
const glyphs = new Map();
const state = controls((weight) => {
  for (const tr of $("rows").querySelectorAll("tr[data-key]")) tr.querySelector("[data-inter]").innerHTML = renderSnippet(byKey.get(tr.dataset.key).tex, "inter", weight);
  markInter($("rows"));
  makeRoom($("rows"));
});

function draw() {
  rows = rowsOf($("view").value);
  byKey = new Map(rows.map((r) => [r.key, r]));
  const html = [];
  let group = "";
  for (const r of rows) {
    if (r.group !== group) {
      group = r.group;
      html.push(`<tr class="group" data-group="${escapeHtml(group)}"><td colspan="4">${escapeHtml(group)}</td></tr>`);
    }
    const name = r.name ? `<span class="name">${escapeHtml(r.name)}</span>` : "";
    html.push(
      `<tr data-key="${r.key}"><td class="source">${name}<code>${escapeHtml(r.tex)}</code></td>` +
        `<td class="math">${renderSnippet(r.tex, "classic")}</td>` +
        `<td class="math ${INTER_MATH_CLASS}" data-inter>${renderSnippet(r.tex, "inter", state.weight)}</td>` +
        `<td><span class="chips"></span></td></tr>`,
    );
  }
  $("rows").innerHTML = html.join("");
  glyphs.clear();
  for (const tr of $("rows").querySelectorAll("tr[data-key]")) {
    const found = glyphsOf(tr.querySelector("[data-inter]"), byKey.get(tr.dataset.key).tex);
    glyphs.set(tr.dataset.key, found);
    tr.querySelector(".chips").innerHTML = found.map(chip).join("");
  }
  markInter($("rows"));
  filter();
}

function filter() {
  const query = $("query").value.trim().toLowerCase();
  const show = $("show").value;
  const groups = new Set();
  let shown = 0;
  const designed = new Set();
  const fallback = new Map();
  const images = new Set();
  for (const tr of $("rows").querySelectorAll("tr[data-key]")) {
    const r = byKey.get(tr.dataset.key);
    const found = glyphs.get(r.key) ?? [];
    const matches = !query || [r.tex, r.name ?? "", r.group].some((s) => s.toLowerCase().includes(query));
    const kept = show === "all" || (show === "drawn" ? found.some((g) => g.how) : found.some((g) => !g.role && !g.command));
    // (a KaTeX image has neither: it falls back too)
    tr.hidden = !(matches && kept);
    if (tr.hidden) continue;
    shown++;
    groups.add(r.group);
    for (const g of found) {
      if (g.image) images.add(g.image);
      else if (g.command || g.how) designed.add(g.command ?? `${g.role}:${g.char}`);
      else if (!fallback.has(`${g.font}:${g.char}`)) fallback.set(`${g.font}:${g.char}`, g);
    }
  }
  for (const tr of $("rows").querySelectorAll("tr.group")) tr.hidden = !groups.has(tr.dataset.group);
  makeRoom($("rows"));
  const chars = [...fallback.values()];
  $("counts").innerHTML =
    `${shown} of ${rows.length} snippets · ${designed.size} glyphs and images drawn by Inter Math · ${chars.length} glyphs from KaTeX's fonts` +
    (chars.length ? `: <span class="fallbacks">${chars.map((g) => `<span style="${g.font}" title="U+${g.char.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}, ${escapeHtml(katexFont(g.font))}">${escapeHtml(g.char)}</span>`).join(" ")}</span>` : "") +
    ` · ${images.size} of KaTeX's images` + (images.size ? `: <code>${[...images].map(escapeHtml).join(" ")}</code>` : "");
}

const stick = () => document.documentElement.style.setProperty("--header-height", `${document.querySelector("header").offsetHeight}px`);
addEventListener("resize", stick);
stick();
$("view").addEventListener("change", draw);
$("show").addEventListener("change", filter);
$("query").addEventListener("input", filter);
document.fonts.ready.then(draw);
