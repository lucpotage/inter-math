// Inter Math's OpenType font in the browser's MathML (KaTeX's MathML output, laid out from the font's MATH table)
// beside KaTeX's own layout in Inter Math, and MathJax 4 with the font made of it: fractions, scripts, radicals, big
// operators, delimiters at every size, accents and what stretches, the math alphabets, at every weight.
import katex from "katex";
import staticSheet from "../src/mathml.css?url";
import variableSheet from "../src/mathml-variable.css?url";
import mathjaxFont from "../src/mathjax-font/svg.js?url";
import { INTER_MATH_CLASS } from "../src/index.ts";
import { controls, escapeHtml, render } from "./workbench.js";

const FORMULAS = [
  ["Letters, digits", "abcxyz\\;ABCXYZ\\;0123456789"],
  ["Greek", "\\alpha\\beta\\gamma\\delta\\varepsilon\\theta\\vartheta\\lambda\\mu\\pi\\rho\\sigma\\phi\\varphi\\omega\\;\\Gamma\\Delta\\Theta\\Lambda\\Sigma\\Phi\\Omega"],
  ["Operators, relations", "a + b - c = d \\times e \\div f \\pm g \\le h \\ge i \\ne j \\approx k \\equiv l \\subset m \\in n \\to o"],
  ["Scripts", "x^2 + y^2 = z^2,\\quad x_i^2,\\quad a_{n+1} = 2a_n,\\quad e^{i\\pi} + 1 = 0,\\quad 2^{2^n},\\quad f'(x), f''(x)"],
  ["Fractions", "\\frac{1}{2} + \\frac{x + 1}{x - 1} = \\frac{\\frac{a}{b}}{c},\\quad \\tfrac{1}{2},\\quad \\binom{n}{k}"],
  ["Display fraction", "\\dfrac{a + b}{c + d} = \\dfrac{\\dfrac{1}{2}}{\\dfrac{3}{4}}"],
  ["Radicals", "\\sqrt{2}\\quad \\sqrt{x}\\quad \\sqrt{x^2 + 1}\\quad \\sqrt[3]{8}\\quad \\sqrt{\\frac{a}{b}}\\quad \\sqrt{\\frac{\\frac{1}{2}}{\\frac{3}{4}}}\\quad \\sqrt{\\begin{matrix}1\\\\2\\\\3\\\\4\\\\5\\end{matrix}}"],
  ["Big operators, text", "\\textstyle \\sum_{n=1}^\\infty \\frac{1}{n^2},\\ \\int_0^1 x\\,dx,\\ \\prod_k a_k,\\ \\oint_C \\omega,\\ \\bigcup_i A_i"],
  ["Big operators, display", "\\displaystyle \\sum_{n=1}^\\infty \\frac{1}{n^2} = \\frac{\\pi^2}{6},\\quad \\int_0^1 x^2\\,dx,\\quad \\iint_D f,\\quad \\prod_{k=1}^n a_k,\\quad \\bigoplus_i V_i"],
  ["Delimiters", "\\left(\\frac{a}{b}\\right) \\left[\\frac{\\frac{a}{b}}{c}\\right] \\left\\{\\frac{\\frac{\\frac{a}{b}}{c}}{d}\\right\\} \\left|\\frac{a}{\\frac{b}{c}}\\right| \\left\\langle x \\right\\rangle \\bigl(\\Bigl(\\biggl(\\Biggl(\\Biggr)\\biggr)\\Bigr)\\bigr)"],
  ["Tall delimiters", "\\begin{pmatrix}1\\\\2\\\\3\\\\4\\\\5\\\\6\\end{pmatrix} \\begin{bmatrix}1\\\\2\\\\3\\\\4\\\\5\\\\6\\end{bmatrix} \\left\\{\\begin{matrix}a\\\\b\\\\c\\\\d\\\\e\\\\f\\end{matrix}\\right. \\begin{vmatrix}1\\\\2\\\\3\\\\4\\\\5\\end{vmatrix} \\left\\lfloor\\begin{matrix}1\\\\2\\\\3\\\\4\\\\5\\end{matrix}\\right\\rceil"],
  ["Accents", "\\hat{x}\\ \\tilde{a}\\ \\bar{z}\\ \\dot{x}\\ \\ddot{x}\\ \\check{j}\\ \\breve{u}\\ \\acute{e}\\ \\grave{a}\\ \\mathring{A}\\ \\hat{A}\\ \\vec{v}\\ \\hat{\\imath}"],
  ["Wide accents", "\\widehat{x}\\ \\widehat{xy}\\ \\widehat{xyz}\\ \\widehat{abcdef}\\ \\widetilde{a}\\ \\widetilde{abc}\\ \\widetilde{abcdefgh}\\ \\widecheck{xy}"],
  ["Over, under", "\\overline{AB}\\ \\underline{xyz}\\ \\overbrace{a+b+c}^{n}\\ \\underbrace{x_1+\\cdots+x_n}_{n}\\ \\overrightarrow{AB}\\ \\overleftarrow{xy}\\ \\overleftrightarrow{PQRS}"],
  ["Stretched arrows", "A \\xrightarrow{f} B \\xleftarrow{g} C \\xRightarrow{\\text{implies}} D \\xleftrightarrow{\\text{both}} E \\xhookrightarrow{i} F \\xmapsto{\\phi} G"],
  ["Alphabets", "\\mathbf{F} = m\\mathbf{a},\\ \\boldsymbol{\\alpha\\beta},\\ \\mathsf{ABC},\\ \\mathbb{R}\\mathbb{N}\\mathbb{Z},\\ \\mathrm{d}x,\\ \\mathit{diff}"],
  ["Negations", "a \\ne b,\\ x \\notin A,\\ A \\not\\subset B,\\ a \\nleq b,\\ \\not\\equiv,\\ \\nexists x"],
  ["Matrix", "\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} \\begin{pmatrix} x \\\\ y \\end{pmatrix} = \\begin{pmatrix} ax + by \\\\ cx + dy \\end{pmatrix}"],
  ["Cases", "|x| = \\begin{cases} x & \\text{if } x \\ge 0 \\\\ -x & \\text{otherwise} \\end{cases}"],
];

/** KaTeX's MathML for some LaTeX: its <math> alone (KaTeX's own wrapper sets its font and size). */
function mathml(tex, displayMode) {
  const html = katex.renderToString(tex, { throwOnError: false, strict: "ignore", output: "mathml", displayMode });
  const start = html.indexOf("<math");
  return start < 0 ? html : html.slice(start, html.lastIndexOf("</math>") + "</math>".length);
}

// the nine weights (mathml.css: each its own MATH table), or the variable font (?variable: its rules and gaps follow
// the weight only where the browser applies the MATH table's variations)
const variable = new URLSearchParams(location.search).has("variable");
// ?overlay: the MathML laid over KaTeX's rendering of the same LaTeX, from the same origin and baseline, KaTeX in red
// and MathML in cyan: dark where they agree, a fringe wherever they don't
const overlay = new URLSearchParams(location.search).has("overlay");
// a stylesheet of its own (its fonts' URLs relative to it)
const sheet = document.createElement("link");
sheet.rel = "stylesheet";
sheet.href = variable ? variableSheet : staticSheet;
document.head.append(sheet);

const rows = document.querySelector("#rows");
let weight = 400;

// MathJax 4 (SVG output) with Inter Math's font for it, loaded from its folder's URL (the last part names the font),
// laid out at the MathML column's size
window.MathJax = {
  output: { font: new URL(mathjaxFont, location.href).href.replace(/\/svg\.js(\?.*)?$/, "") },
  svg: { matchFontHeight: false, fontCache: "local" },
  startup: { typeset: false },
  options: { enableMenu: false },
};
const mathjaxReady = new Promise((resolve, reject) => {
  const script = document.createElement("script");
  script.src = "https://cdn.jsdelivr.net/npm/mathjax@4.1.3/tex-svg-nofont.js";
  script.onload = () => MathJax.startup.promise.then(resolve, reject);
  script.onerror = reject;
  document.head.append(script);
});
async function mathjax(cell, tex, display) {
  await mathjaxReady;
  cell.replaceChildren(await MathJax.tex2svgPromise(tex, { display }));
}

/** KaTeX's rendering and the MathML laid over it (?overlay): both inline, \\displaystyle for display formulas. */
function pair(tex, display) {
  const source = display ? `\\displaystyle ${tex}` : tex;
  return `<span class="pair"><span class="k ${INTER_MATH_CLASS}">${render(source, "inter", weight)}</span><span class="m">${mathml(source, false)}</span></span>`;
}

function draw() {
  rows.innerHTML = FORMULAS.map(([name, tex]) => {
    const display = /\\displaystyle|\\dfrac|matrix|cases/.test(tex);
    return `<tr><td class="source"><strong>${escapeHtml(name)}</strong><code>${escapeHtml(tex)}</code></td>
      <td class="math ${INTER_MATH_CLASS}">${render(tex, "inter", weight, display)}</td>
      <td class="math mathml">${overlay ? pair(tex, display) : mathml(tex, display)}</td><td class="math mathjax"></td></tr>`;
  }).join("");
  [...rows.querySelectorAll(".mathjax")].forEach((cell, i) => {
    const [, tex] = FORMULAS[i];
    mathjax(cell, tex, /\\displaystyle|\\dfrac|matrix|cases/.test(tex));
  });
  tryIt();
}

const box = document.querySelector("#tex");
function tryIt() {
  const tex = box.value.trim();
  document.querySelector("#try-katex").innerHTML = tex ? render(tex, "inter", weight) : "";
  document.querySelector("#try-katex").className = `math ${INTER_MATH_CLASS}`;
  document.querySelector("#try-mathml").innerHTML = tex ? (overlay ? pair(tex, false) : mathml(tex, false)) : "";
  const cell = document.querySelector("#try-mathjax");
  if (tex) mathjax(cell, tex, false);
  else cell.replaceChildren();
}
box.addEventListener("input", tryIt);

const state = controls((w) => {
  weight = w;
  draw();
});
weight = state.weight;
const toggle = document.createElement("label");
toggle.className = "control";
toggle.innerHTML = `<input type="checkbox"${variable ? " checked" : ""}> Variable font`;
document.querySelector("header").append(toggle);
toggle.querySelector("input").addEventListener("change", (e) => {
  const url = new URL(location.href);
  if (e.target.checked) url.searchParams.set("variable", "");
  else url.searchParams.delete("variable");
  location.href = url.href;
});
const overlayToggle = document.createElement("label");
overlayToggle.className = "control";
overlayToggle.innerHTML = `<input type="checkbox"${overlay ? " checked" : ""}> MathML over KaTeX`;
document.querySelector("header").append(overlayToggle);
overlayToggle.querySelector("input").addEventListener("change", (e) => {
  const url = new URL(location.href);
  if (e.target.checked) url.searchParams.set("overlay", "");
  else url.searchParams.delete("overlay");
  location.href = url.href;
});

// the browser's MathML in the OpenType font, at the page's weight, its letters as large as KaTeX's: KaTeX sets math at
// 1.21 em of KaTeX's fonts' em, Inter Math's for KaTeX being Inter's 2048 units in 2332, the OpenType font's Inter's own
const style = document.createElement("style");
style.textContent = `.mathml math { font-size: calc(var(--math-size, 24px) * 1.21 * 2048 / 2332); font-weight: var(--inter-math-weight, 400); }
  .mathjax mjx-container { font-size: calc(var(--math-size, 24px) * 1.21 * 2048 / 2332); }
  .mathjax mjx-container[display] { margin: 0; }
  .pair { display: inline-grid; align-items: baseline; }
  .pair > * { grid-area: 1 / 1; }
  .pair .k { color: #e3003a; }
  .pair .m { color: #00b4d8; mix-blend-mode: multiply; }`;
document.head.append(style);
draw();
