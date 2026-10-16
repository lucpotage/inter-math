// The review's points (REVIEW.md), each in KaTeX's Computer Modern and in Inter Math at every weight from 100 to 900
// (a page that shows them all is one picture to check), with what Inter's own text sets for the same thing where it
// does (in Inter itself, at the same weight and size): math set like text where they meet.
import { controls, escapeHtml, markInter, render } from "./workbench.js";

const WEIGHTS = [100, 200, 300, 400, 500, 600, 700, 800, 900];

// [REVIEW.md's number, what, LaTeX, its reference in Inter's own text (or ""), "italic" where the math letter is]
const POINTS = [
  [1, "a′ like a’", "a' \\quad f' \\quad A' \\quad x'", "a’ f’ A’ x’", "italic"],
  [2, "a″ like a”", "a'' \\quad a''' \\quad f'' \\quad x^{\\prime\\prime}", "a” a”’ f”", "italic"],
  [3, "Wide tilde", "\\widetilde{a} \\; \\widetilde{ac} \\; \\widetilde{AB} \\; \\widetilde{abc} \\; \\widetilde{abcdef} \\quad \\tilde{a}", "ã Ã", "italic"],
  [4, "Over group", "\\overgroup{AB} \\quad \\overgroup{abcdef}", ""],
  [5, "Under tilde", "\\utilde{AB} \\quad \\utilde{abcdef}", ""],
  [6, "Under group", "\\undergroup{AB} \\quad \\undergroup{abcdef}", ""],
  [7, "Bar", "\\bar{y} \\; \\bar{a} \\; \\bar{x} \\; \\bar{A} \\quad \\futurelet\\foo\\bar x", "ā ȳ Ā", "italic"],
  [8, "Harpoons over", "\\overleftharpoon{ac} \\quad \\overrightharpoon{ac} \\quad \\overrightarrow{ac}", ""],
  [9, "Braces", "\\overbrace{AB} \\quad \\underbrace{AB} \\quad \\overbrace{a+b+c}^{\\text{note}} \\quad \\underbrace{a+b+c}_{\\text{note}}", ""],
  [10, "Overline", "\\overline{AB} \\quad \\overline{ab} \\quad \\overline{\\overline{x}} \\quad \\underline{AB} \\quad \\underline{ab} \\quad e^{\\overline{z}}", ""],
  [11, "Brackets over and under", "\\overbracket{AB} \\quad \\underbracket{AB} \\quad \\overbracket{a+b+c}^{\\text{note}}", ""],
  [12, "Line segments", "\\overlinesegment{AB} \\quad \\underlinesegment{AB}", ""],
  [13, "Wide check and hat", "\\widecheck{ac} \\; \\widecheck{AB} \\; \\widehat{ac} \\; \\widehat{AB} \\; \\widehat{abcdef} \\quad \\check{a} \\; \\hat{a}", "ǎ â Â", "italic"],
  [14, "Text accents", "\\'{a} \\quad \\text{\\'{a} \\`{a} \\^{a} \\~{a} \\={a} \\u{a} \\.{a} \\\"{a} \\r{a} \\H{o} \\v{c} \\c{c} é}", "á à â ã ā ă ȧ ä å ő č ç é"],
  [15, "Bracket arms", "\\lceil x \\rceil \\; \\lfloor x \\rfloor \\; [x] \\quad \\big[ \\Big[ \\bigg[ \\Bigg[ \\quad \\Bigg\\lceil \\Bigg\\rfloor", ""],
  [16, "Arrow heads", "\\gets \\; \\to \\; \\leftrightarrow \\quad \\Leftarrow \\; \\Rightarrow \\; \\Leftrightarrow \\quad \\impliedby \\; \\implies \\; \\iff \\quad \\Uparrow \\; \\Downarrow \\; \\Updownarrow", "← → ⇒ ⇔"],
  [17, "⟦ ⟧", "\\llbracket x \\rrbracket \\quad \\llbracket a, b \\rrbracket", ""],
  [18, "Double strokes", "\\lBrace x \\rBrace \\quad \\Reals \\; \\N \\; \\Z \\; \\cnums \\; \\Complex \\; \\R \\; \\Bbbk \\quad \\Vert x \\Vert", "ǁ ‖"],
  [19, "@", "a@b \\quad A@B \\quad 1@2 \\quad \\text{user@example.org, A@B}", ""],
  [20, "Game", "\\Game \\quad G", ""],
  [21, "\\aa", "\\text{\\aa}", "å"],
  [22, "\\AA", "\\text{\\AA}", "Å"],
  [23, "h-slash", "\\hslash \\quad \\hbar \\quad \\mathit{\\hbar}", "ħ ₺", "italic"],
  [24, "Cancel", "\\cancel{5} \\quad \\bcancel{5} \\quad \\cancel{x+y}", "ȼ Ɇ Ⱥ"],
  [25, "Cross cancel", "\\xcancel{ABC} \\quad \\xcancel{5}", ""],
  [26, "Strike-through", "\\text{\\sout{abc} \\sout{ABC}}", ""],
  [27, "Phase", "\\phase{-78^\\circ} \\quad \\phase{x}", ""],
  [28, "Overlaps", "{=}\\mathllap{/\\,} \\quad \\mathrlap{\\,/}{=} \\quad \\ne \\quad \\not=", ""],
  [29, "∉ ∌", "x \\notin A \\quad A \\notni x \\quad \\not\\in \\quad \\nexists", ""],
  [30, "∬ ∭", "\\iint \\; \\iiint \\quad \\displaystyle \\iint \\; \\iiint", ""],
  [31, "⨄ and its kin", "\\biguplus \\; \\bigcup \\; \\bigcap \\; \\bigsqcup \\quad \\displaystyle \\biguplus \\; \\bigcup \\; \\bigsqcup \\quad \\textstyle a \\uplus b \\cup c \\sqcup d", "˟"],
  [32, "∯ ∰", "\\oiint \\; \\oiiint \\quad \\displaystyle \\oiint \\; \\oiiint \\; \\oint", ""],
  [33, "⋖ ⋗", "a \\lessdot b \\gtrdot c", "ͽ"],
  [34, "⋉ ⋊", "A \\ltimes B \\rtimes C \\quad \\times", ""],
  [35, "⋓ ⋒", "A \\Cup B \\Cap C \\quad \\Subset \\; \\Supset", ""],
  [36, "⊴ ⊵", "H \\unlhd G \\unrhd K \\quad a \\le b \\ge c", ""],
  [37, "≀", "G \\wr H \\quad \\widetilde{ac}", ""],
  // your notes on the build (REVIEW.md's B17–B25)
  ["B17", "⦃ ⦄: hooks past the second stem", "\\lBrace x \\rBrace \\quad \\llbracket x \\rrbracket \\quad \\{ x \\}", ""],
  ["B18", "≬ at heavy weights", "a \\between b \\quad \\between", ""],
  ["B19", "Blackboard Y", "\\mathbb{Y} \\; \\mathbb{X} \\; \\mathbb{V} \\; \\mathbb{W}", ""],
  ["B20", "Diagonal arrows as wide as →", "\\nearrow \\; \\searrow \\; \\nwarrow \\; \\swarrow \\quad \\to", ""],
  ["B21", "Negated arrows' heads", "\\nleftarrow \\; \\nrightarrow \\; \\nleftrightarrow \\quad \\nLeftarrow \\; \\nRightarrow \\; \\nLeftrightarrow", ""],
  ["B22", "Paired arrows' joints", "\\rightrightarrows \\; \\leftleftarrows \\; \\upuparrows \\; \\downdownarrows \\quad \\rightleftarrows \\; \\leftrightarrows", ""],
  ["B23", "Tails", "\\rightarrowtail \\; \\leftarrowtail \\quad \\twoheadrightarrow \\; \\twoheadleftarrow", ""],
  ["B24", "Circle and corner arrows", "\\circlearrowleft \\; \\circlearrowright \\quad \\Lsh \\; \\Rsh \\quad \\curvearrowleft \\; \\curvearrowright", ""],
  ["B25", "Small heads (the header's Triangle heads)", "\\nrightarrow \\; \\rightrightarrows \\; \\twoheadrightarrow \\; \\rightarrowtail \\; \\dashrightarrow \\; \\rightsquigarrow \\; \\looparrowleft \\quad \\circlearrowleft \\; \\curvearrowright \\; \\Lsh \\quad \\vec{u} \\; \\overrightarrow{AB} \\; \\overleftrightarrow{AB} \\; \\Overrightarrow{AB} \\; \\overrightharpoon{ac} \\quad x^{\\rightarrowtail}", ""],
  // your notes of 2026-10-16 (REVIEW.md's B27–B46: the glyphs among them)
  ["B27", "Line segments: the bar, taller ends", "\\overlinesegment{AB} \\quad \\underlinesegment{AB} \\quad \\overline{AB} \\quad \\overleftrightarrow{AB}", ""],
  ["B28", "⦃ ⦄ after { and [", "\\lBrace x \\rBrace \\quad \\{ x \\} \\quad [ x ]", ""],
  ["B29", "ℏ's bar across the stem's middle", "\\hslash \\quad \\hbar \\quad h", "ħ"],
  ["B30", "! ? in scripts", "\\stackrel{!}{=} \\quad n! \\quad x^{n!} \\quad y_{?}", ""],
  ["B33", "⊂ ∈ ⊆ ⫅ ⋐ from U turned", "\\subset \\; \\supset \\; \\in \\; \\ni \\; \\notin \\quad \\subseteq \\; \\subseteqq \\; \\subsetneq \\quad \\Subset \\; \\Supset \\quad \\cup \\; \\Cup", ""],
  ["B35", "⋉ ⋊ in ×'s box", "A \\ltimes B \\rtimes C \\quad \\times", ""],
  ["B36", "⊴ ⊵ as wide as ≥", "H \\unlhd G \\unrhd K \\quad \\le \\; \\ge \\quad \\lhd \\; \\rhd", ""],
  ["B37", "⋇ with ÷'s bar", "\\divideontimes \\quad \\div \\; \\times", ""],
  ["B38", "⊎'s plus at Black", "a \\uplus b \\quad \\cup \\quad \\biguplus", ""],
  ["B39", "⋈'s sides in line", "\\Join \\; \\bowtie \\quad \\ltimes \\; \\rtimes", ""],
  ["B40", "↺ ↻'s heads along the ring", "\\circlearrowleft \\; \\circlearrowright \\quad \\curvearrowleft \\; \\curvearrowright", ""],
  ["B41", "⇝ ↭ zigzag", "\\rightsquigarrow \\; \\leadsto \\; \\leftrightsquigarrow \\quad \\to \\; \\leftrightarrow", ""],
  ["B42", "↫ ↬: the loop's junction", "\\looparrowleft \\; \\looparrowright \\quad \\gets \\; \\to", ""],
  ["B43", "Arrows on the line, Inter Math's", "\\xhookleftarrow{abc} \\quad \\xhookrightarrow{abc} \\quad \\xmapsto{abc} \\quad \\xtofrom{abc} \\quad \\xtwoheadleftarrow{abc} \\quad \\xtwoheadrightarrow{abc} \\quad \\xlongequal{abc} \\quad \\xrightarrow{abc}", ""],
  ["B46", "\\TeX: T and X on E's middle bar", "\\TeX \\quad \\LaTeX \\quad \\KaTeX \\quad \\text{\\TeX}", ""],
  // your notes from the site's hero (REVIEW.md's B47–B53)
  ["B47", "Delimiters and surds as tall as their content", "\\left( \\sqrt{\\frac{5 + \\sqrt{5}}{2}} - \\frac{\\sqrt{5} + 1}{2} \\right) \\sqrt[5]{e^{2\\pi}} \\quad \\left[ \\dfrac{a^2}{b_1} \\right] \\quad \\left\\{ \\tfrac{a}{b} \\right\\}", ""],
  ["B48", "Surds as heavy as the bars", "\\sqrt{x} \\; \\frac{a}{b} \\; \\sqrt{\\frac{a}{b}} \\; - \\quad \\sqrt[3]{y} \\quad \\sqrt{\\dfrac{x}{y}}", ""],
  ["B49", "Vertical spaces as Inter's whites", "\\dfrac{\\dfrac{a}{b}}{\\dfrac{c}{d}} \\quad \\sqrt{\\dfrac{1}{x}} \\quad x_1^2 \\quad \\binom{n}{k}", ""],
  ["B50", "Large delimiters thinner", "\\Bigg( \\Bigg[ \\Bigg\\{ \\Bigg\\langle \\quad \\bigg( \\Big( \\big( ( \\quad x", ""],
  ["B51", "Rules as thick as the minus and the surds", "\\frac{1}{2} - \\sqrt{x} \\quad \\dfrac{a}{b} - \\overline{AB} \\; \\underline{AB} \\quad \\begin{array}{c} a \\\\ \\hline b \\end{array}", ""],
  ["B52", "Tall delimiters as heavy as the rule", "\\left( \\sqrt{\\dfrac{5 + \\sqrt{5}}{2}} - \\dfrac{1}{2} \\right) \\quad \\Bigg( \\Bigg[ \\Bigg\\{ \\Bigg\\langle \\Bigg\\lfloor \\Bigg/ - \\quad \\left| \\dfrac{\\dfrac{a}{b}}{c} \\right|", ""],
  ["B53", "Integral limits as close as Inter's letters", "\\int_a^b f \\; \\int_0^1 \\; \\oint_C \\; \\iint_D \\quad \\displaystyle \\int_a^b f \\; \\int_0^\\infty \\; \\oint_C", ""],
];

controls(() => {}); // the header's theme and size (every weight shows here)

/** A point's LaTeX, its pieces (apart at \\quad) set one by one so that a cell wraps between them. */
const pieces = (tex, font, weight) =>
  tex
    .split(/\s*\\quad\s*/)
    .map((piece) => `<span class="piece">${render(piece, font, weight)}</span>`)
    .join(" ");

function cellHtml([, , tex, ref, style], weight) {
  const math = pieces(tex, "inter", weight);
  return ref ? `${math} <span class="piece ref reference ${style ?? ""}">${escapeHtml(ref)}</span>` : math;
}

// ?points=B17,B18 shows only those points
const only = new URLSearchParams(location.search).get("points")?.split(",");
const rows = document.querySelector("#rows");
rows.innerHTML = POINTS.filter((point) => !only || only.includes(String(point[0]))).map(
  (point) =>
    `<tr id="p${point[0]}"><td class="number">${point[0]}</td><td class="source"><b>${escapeHtml(point[1])}</b><br><code>${escapeHtml(point[2])}</code></td>` +
    `<td class="math">${pieces(point[2], "classic")}</td>` +
    WEIGHTS.map((w) => `<td class="math inter-math" style="--inter-math-weight: ${w}">${cellHtml(point, w)}</td>`).join("") +
    "</tr>",
).join("");
markInter(rows);
