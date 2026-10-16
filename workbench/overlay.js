// Inter Math's math laid over Inter's own text, at every weight. Where math sets what text sets too (an accented
// letter, a prime after a letter), it must come out as Inter sets it: an overlay shows a difference at once, where two
// pictures side by side hide it (the dots of \ddot{a} sat left of ä's). Inter's text is set as large as KaTeX sets
// Inter Math's letters (KaTeX's 1.21 em, Inter Math's em being Inter's 2048 units in 2332) and at the same optical size.
import { controls, escapeHtml, render } from "./workbench.js";

const WEIGHTS = [100, 200, 300, 400, 500, 600, 700, 800, 900];

// [group, [[LaTeX, Inter's text for it, italic (a math letter)]…]]; a letter Inter has no precomposed glyph for is
// typed with its combining mark, which Inter places through its mark feature
const GROUPS = [
  [
    "Accents over letters Inter has precomposed (the math letter is Inter's italic one)",
    [
      ["\\acute{a}", "á", true],
      ["\\grave{a}", "à", true],
      ["\\hat{a}", "â", true],
      ["\\tilde{a}", "ã", true],
      ["\\ddot{a}", "ä", true],
      ["\\check{a}", "ǎ", true],
      ["\\breve{a}", "ă", true],
      ["\\dot{a}", "ȧ", true],
      ["\\mathring{a}", "å", true],
      ["\\hat{e} \\ddot{o} \\tilde{n} \\check{s}", "ê ö ñ š", true],
      ["\\hat{A} \\ddot{A} \\acute{E} \\mathring{A}", "Â Ä É Å", true],
      ["\\bar{a} \\bar{y}", "ā ȳ", true],
    ],
  ],
  [
    "Accents over letters Inter has none for (KaTeX's accent, where Inter's mark feature puts the mark)",
    [
      ["\\ddot{q}", "q̈", true],
      ["\\hat{x}", "x̂", true],
      ["\\tilde{x}", "x̃", true],
      ["\\acute{x}", "x́", true],
      ["\\check{x}", "x̌", true],
      ["\\dot{x}", "ẋ", true],
      ["\\hat{X}", "X̂", true],
      ["\\grave{x}", "x̀", true],
      ["\\breve{x}", "x̆", true],
      ["\\mathit{\\hat{x}}", "x̂", true],
    ],
  ],
  [
    "Accents drawn otherwise than Inter's on purpose: \\bar as wide as TeX's against x, the ring as close as over capitals",
    [
      ["\\bar{x}", "x̄", true],
      ["\\mathring{x}", "x̊", true],
    ],
  ],
  [
    "Accents over upright letters (Inter's upright marks)",
    [
      ["\\hat{\\mathrm{X}}", "X̂", false],
      ["\\acute{\\mathrm{x}}", "x́", false],
      ["\\ddot{\\mathrm{x}}", "ẍ", false],
    ],
  ],
  [
    "Primes (Inter's ′), after a letter as ’ ” are in text",
    [
      ["a'", "a’", true],
      ["a''", "a”", true],
      ["a' \\; f' \\; A' \\; x'", "a’ f’ A’ x’", true],
    ],
  ],
  [
    "Text accents",
    [
      ["\\text{\\'{e} \\v{c} \\aa\\ \\AA}", "é č å Å", false],
      ["\\text{é}", "é", false],
    ],
  ],
];

controls(() => {}); // the header's theme and size (every weight shows here)

const pair = ([tex, text, italic], weight) =>
  `<span class="overlay-pair"><span class="over-math">${render(tex, "inter", weight)}</span>` +
  `<span class="over-text${italic ? " italic" : ""}">${escapeHtml(text)}</span></span>`;

// ?group=2,3 shows only those groups (counted from 1)
const only = new URLSearchParams(location.search).get("group")?.split(",").map(Number);
const rows = document.querySelector("#rows");
rows.innerHTML = GROUPS.filter((_, i) => !only || only.includes(i + 1)).map(
  ([group, pairs]) =>
    `<tr class="group"><td colspan="${WEIGHTS.length + 1}">${escapeHtml(group)}</td></tr>` +
    pairs
      .map(
        (p) =>
          `<tr><td class="source"><code>${escapeHtml(p[0])}</code></td>` +
          WEIGHTS.map((w) => `<td class="math inter-math" style="--inter-math-weight: ${w}">${pair(p, w)}</td>`).join("") +
          "</tr>",
      )
      .join(""),
).join("");

// Inter's text at KaTeX's optical size (KaTeX sets the math 1.21 times the text's size: browsers pick the optical size
// from the font size)
function opticalSize() {
  const cell = rows.querySelector("td.math");
  if (!cell) return;
  const px = parseFloat(getComputedStyle(cell).fontSize) * 1.21;
  rows.style.setProperty("--text-opsz", String(Math.min(32, Math.max(14, px))));
}
opticalSize();
document.addEventListener("input", opticalSize);
