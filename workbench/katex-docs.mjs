// The examples of KaTeX's documentation, for the workbench's symbols page (symbols.html): every LaTeX
// snippet of "Supported Functions" (katex.org/docs/supported, sorted by type) and of "Support Table"
// (katex.org/docs/support_table, alphabetical), read from their sources in KaTeX's repository at the
// installed version. Writes katex-docs.json, next to this script.
//
//   node workbench/katex-docs.mjs
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";

const require = createRequire(new URL("../package.json", import.meta.url));
const { version } = require("katex/package.json");
const OUT = new URL("./katex-docs.json", import.meta.url);
const SOURCE = (page) => `https://raw.githubusercontent.com/KaTeX/KaTeX/v${version}/docs/${page}.md`;

const ENTITIES = { "&lt;": "<", "&gt;": ">", "&amp;": "&", "&quot;": '"', "&nbsp;": " " };
const unescapeHtml = (s) => s.replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n))).replace(/&[a-z]+;/g, (e) => ENTITIES[e] ?? e);

/**
 * The code spans of a line of markdown, outside its math ($…$, which may hold a backtick: \\`{a}): `…` as
 * written, <code>…</code> unescaped (its \\\\ is a backslash).
 */
function codeSpans(line) {
  const out = [];
  let math = false;
  for (let i = 0; i < line.length; i++) {
    if (!math && line.startsWith("<code>", i)) {
      const end = line.indexOf("</code>", i);
      if (end < 0) break;
      out.push(unescapeHtml(line.slice(i + 6, end)).replace(/\\\\/g, "\\"));
      i = end + 6;
    } else if (!math && line[i] === "`") {
      const end = line.indexOf("`", i + 1);
      if (end < 0) break;
      out.push(line.slice(i + 1, end));
      i = end;
    } else if (line[i] === "$" && line[i - 1] !== "\\") math = !math;
  }
  return out;
}

/** A table row's cells: split at | outside code spans and math, \| kept. */
function cells(row) {
  const out = [];
  let cell = "";
  let code = false;
  for (let i = 1; i < row.length; i++) {
    const c = row[i];
    if (c === "`") code = !code;
    if (c === "|" && !code && row[i - 1] !== "\\") {
      out.push(cell);
      cell = "";
    } else cell += c;
  }
  if (cell.trim()) out.push(cell);
  return out;
}

const isSeparator = (line) => /^\|[\s:|-]+\|?\s*$/.test(line);
// snippets that aren't LaTeX to render as they are: KaTeX's HTML output, a command named without its arguments
const katex = require("katex");
const isLatex = (s) => {
  if (!s.trim() || s.includes("<span")) return false;
  try {
    katex.renderToString(s, { throwOnError: true, strict: "ignore", trust: true });
    return true;
  } catch {
    return false;
  }
};

const STYLED = /^\\(?:display|text|script|scriptscript)style\s*/;
/**
 * An example as the docs render it: its code, or the math they render where that is the code in a style the code
 * leaves out ($\displaystyle\sum_{\mathclap{…}}…$ `\sum_{\mathclap{…}}…`: inline, its clapped limit overlaps).
 */
const asRendered = (code, maths) => maths.find((m) => STYLED.test(m) && m.replace(STYLED, "").trim() === code.trim()) ?? code;

// KaTeX's lines (a fraction's, \overline's, a table's rules…): drawn though they hold no glyph
const LINES = /class="[^"]*\b(?:rule|frac-line|overline-line|underline-line|hline|hdashline|vertical-separator|fbox|sout)\b/;
const VOID = new Set(["img", "br", "path", "line"]);
/**
 * Whether a snippet draws anything: KaTeX's spaces draw nothing, nor its phantoms (their glyphs transparent), and
 * the symbols page leaves them out (rows of nothing). Read from KaTeX's HTML: its text, images and lines outside
 * transparent elements.
 */
function draws(tex) {
  const html = katex.renderToString(tex, { output: "html", strict: "ignore", trust: true, displayMode: /\\begin\{CD\}/.test(tex) });
  const hidden = [false];
  for (const [, close, tag, attrs, self, text] of html.matchAll(/<(\/)?([a-zA-Z]+)([^>]*?)(\/)?>|([^<]+)/g)) {
    if (text !== undefined) {
      if (!hidden.at(-1) && /[^\s\u200b]/.test(unescapeHtml(text))) return true;
    } else if (close) hidden.pop();
    else {
      const out = hidden.at(-1) || /color:\s*transparent/.test(attrs);
      if (!out && (tag === "svg" || tag === "img" || LINES.test(attrs))) return true;
      if (!self && !VOID.has(tag)) hidden.push(out);
    }
  }
  return false;
}

/** "Supported Functions": its sections (## › ###, and a bold line under them), each with its snippets. */
function supported(md) {
  const sections = [];
  let path = [];
  let label = "";
  const section = () => {
    // markdown escapes a backslash as \\
    const name = [...path, label].filter(Boolean).join(" › ").replace(/\\\\/g, "\\");
    if (!sections.length || sections.at(-1).section !== name) sections.push({ section: name, items: [] });
    return sections.at(-1);
  };
  for (const line of md.split("\n")) {
    const heading = /^(#{2,4})\s+(.*)$/.exec(line);
    if (heading) {
      const level = heading[1].length - 2;
      path = [...path.slice(0, level), heading[2].trim()];
      label = "";
      continue;
    }
    const bold = /^\*{2,3}([^*]+)\*{2,3}\s*$/.exec(line.trim());
    if (bold) {
      label = bold[1].trim();
      continue;
    }
    if (!path.length || isSeparator(line)) continue;
    // direct input: the characters themselves, in math
    const direct = /^Direct Input:\s*(.*)$/.exec(line.trim());
    if (direct) {
      for (const m of direct[1].matchAll(/\$([^$]+)\$/g)) section().items.push(m[1].trim());
      continue;
    }
    // table rows, and lines that start with an example ($…$ `…`)
    if (!line.startsWith("|") && !line.startsWith("$")) continue;
    const maths = [...line.matchAll(/\$([^$]+)\$/g)].map((m) => m[1].trim());
    for (const code of codeSpans(line)) {
      const tex = asRendered(code, maths);
      if (isLatex(tex) && draws(tex) && !section().items.includes(tex)) section().items.push(tex);
    }
  }
  return sections.filter((s) => s.items.length);
}

/** "Support Table": by letter group, each function or symbol with a snippet that renders it (unsupported ones left out). */
function supportTable(md) {
  const out = [];
  let group = "";
  for (const line of md.split("\n")) {
    const heading = /^##\s+(.*)$/.exec(line);
    if (heading) {
      group = heading[1].trim();
      continue;
    }
    if (!group || !line.startsWith("|") || isSeparator(line) || line.startsWith("|Symbol/Function")) continue;
    const [name = "", rendered = "", comment = ""] = cells(line);
    const math = /\$([\s\S]+)\$/.exec(rendered)?.[1]?.trim();
    if (!math) continue;
    // the snippet: the source column's code (lines of an environment joined), else what is rendered
    const code = codeSpans(comment).join("\n");
    const tex = [asRendered(code, [math]), math].find(isLatex);
    if (tex && draws(tex)) out.push({ group, name: name.replace(/\\(.)/g, "$1").trim(), tex });
  }
  return out;
}

// the commutative diagram of "Supported Functions" (the support table has none), its lines joined
const CD = "\\begin{CD}\nA  @>a>>  B  \\\\\n@VbVV    @AAcA \\\\\nC  @=   D\n\\end{CD}";

/**
 * "Supported Functions" writes its environments' examples line by line (A @>a>> B, darray…), which the symbols page
 * would render one fragment at a time: its Environments sections take the support table's examples instead, whole.
 */
function wholeEnvironments(sections, table) {
  const whole = [...new Set([...table.map((e) => e.tex).filter((tex) => /\\begin\{/.test(tex)), CD])];
  return sections
    .map((s) => (s.section.startsWith("Environments") ? { ...s, items: s.section === "Environments" ? whole : s.items.filter((tex) => /\\begin\{/.test(tex)) } : s))
    .filter((s) => s.items.length);
}

const [supportedMd, tableMd] = await Promise.all(["supported", "support_table"].map((page) => fetch(SOURCE(page)).then((r) => (r.ok ? r.text() : Promise.reject(new Error(`${SOURCE(page)}: ${r.status}`))))));
const data = { katex: version, source: "https://katex.org/docs/supported, https://katex.org/docs/support_table", supported: supported(supportedMd), table: supportTable(tableMd) };
data.supported = wholeEnvironments(data.supported, data.table);
writeFileSync(OUT, `${JSON.stringify(data, null, 1)}\n`);
const count = data.supported.reduce((n, s) => n + s.items.length, 0);
console.log(`KaTeX ${version}: ${data.supported.length} sections, ${count} snippets; support table: ${data.table.length} entries → ${OUT.pathname}`);
