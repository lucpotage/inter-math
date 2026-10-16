// Inter Math against KaTeX's Computer Modern on school math, a box to try any LaTeX in both, and the characters
// Inter Math still borrows from KaTeX.
import { INTER_MATH_CLASS, keptFromKatex, versions } from "../src/index.ts";
import { controls, escapeHtml, markInter, render } from "./workbench.js";

const SPECIMENS = [
  ["Letters", "abcdefghijklmnopqrstuvwxyz"],
  ["Capitals", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"],
  ["Digits", "0123456789"],
  ["Look-alikes", "l\\,I\\,1\\,|\\quad \\mathrm{l\\,I\\,1}\\quad O\\,0\\,o"],
  ["Greek", "\\alpha\\beta\\gamma\\delta\\epsilon\\varepsilon\\zeta\\eta\\theta\\vartheta\\iota\\kappa\\lambda\\mu\\nu\\xi\\pi\\rho\\sigma\\tau\\upsilon\\phi\\varphi\\chi\\psi\\omega"],
  ["Greek capitals", "\\Gamma\\Delta\\Theta\\Lambda\\Xi\\Pi\\Sigma\\Upsilon\\Phi\\Psi\\Omega"],
  ["Point", "A = (3;\\,5)"],
  ["Line", "f: y = 2x + 1"],
  ["Circle", "(x - 2)^2 + (y + 1)^2 = 9"],
  ["Distance", "AB = \\sqrt{(x_B - x_A)^2 + (y_B - y_A)^2}"],
  ["Midpoint", "I = \\left(\\frac{x_A + x_B}{2};\\, \\frac{y_A + y_B}{2}\\right)"],
  ["Angles", "\\alpha + \\beta + \\gamma = 180\\degree \\qquad \\widehat{ABC} = 45^\\circ \\qquad \\angle ABC"],
  ["Relations", "(AB) \\parallel (CD) \\quad (AB) \\perp (EF) \\quad M \\in [AB]"],
  ["Vectors", "\\vec{u} + \\vec{v} = \\overrightarrow{AB}, \\quad \\overrightarrow{AB} + \\overrightarrow{BC} = \\overrightarrow{AC}, \\quad \\vec{F} = m\\vec{a}"],
  ["Arrows", "\\overleftarrow{AB} \\quad \\overleftrightarrow{AB} \\quad \\Overrightarrow{AB} \\quad A \\xrightarrow{f} B \\quad A \\xLeftarrow{g} B \\quad x \\to 0"],
  ["Pythagoras", "BC^2 = AB^2 + AC^2"],
  ["Scripts", "x_A + y_B, \\quad a_{n+1} = 2a_n - 1, \\quad e^{i\\theta}, \\quad 10^{-3}, \\quad x^{2n}, \\quad 2^{2^{n}}"],
  ["Brackets", "\\left(x+1\\right) \\left(x^2+1\\right) \\left(x_B-x_A\\right) \\left(\\sqrt{2}\\right) \\left(\\frac{1}{2}\\right) \\left[\\frac{\\sqrt{2}}{2}\\right] \\left(\\frac{\\frac{1}{2}}{3}\\right)"],
  ["Braces", "\\{1; 2\\} \\quad \\left\\{x_A\\right\\} \\quad \\left\\{x^2\\right\\} \\quad \\left\\{\\sqrt{2}\\right\\} \\quad \\left\\{\\frac{1}{2}\\right\\} \\quad \\left\\{\\frac{\\sqrt{2}}{2}\\right\\}"],
  ["Fractions", "\\frac{1}{2} + \\frac{x + 1}{x - 1} = \\frac{\\frac{a}{b}}{c}, \\quad \\overline{AB}"],
  ["Roots", "\\sqrt{2} \\quad \\sqrt{x} \\quad \\sqrt{x^2 + 1} \\quad \\sqrt[3]{8} \\quad \\sqrt{\\frac{a}{b}}"],
  ["Tall roots", "\\sqrt{\\frac{\\frac{1}{2}}{\\frac{3}{4}}} \\quad \\sqrt{\\frac{\\frac{\\frac{1}{2}}{3}}{\\frac{4}{\\frac{5}{6}}}} \\quad \\sqrt{\\begin{matrix} 1 \\\\ 2 \\\\ 3 \\\\ 4 \\\\ 5 \\end{matrix}}"],
  ["Trigonometry", "\\sin\\theta = \\frac{\\text{opposite}}{\\text{hypotenuse}}, \\quad \\cos^2 x + \\sin^2 x = 1"],
  ["Quadratic", "x = \\frac{-b \\pm \\sqrt{\\Delta}}{2a}, \\quad \\Delta = b^2 - 4ac"],
  ["Operators", "a \\times b \\div c \\cdot d \\ne e \\le f \\ge g \\approx h"],
  ["Inequalities", "0 \\leqslant x \\leqslant 1 \\quad n \\geqslant 2 \\quad x \\le y \\leqq z \\quad u_n \\lesssim v_n \\quad x_{i \\leqslant n}"],
  ["Order relations", "a \\leqslant b \\geqslant c \\eqslantless d \\eqslantgtr e \\leqq f \\geqq g \\lesssim h \\gtrsim i \\lessapprox j \\gtrapprox k \\lessgtr l \\gtrless m \\lesseqgtr n \\gtreqless o \\lesseqqgtr p \\gtreqqless q \\lll r \\ggg s \\lessdot t \\gtrdot u"],
  ["Precedence", "a \\prec b \\succ c \\preceq d \\succeq e \\quad a \\preccurlyeq b \\succcurlyeq c \\curlyeqprec d \\curlyeqsucc e \\quad a \\precsim b \\succsim c \\precapprox d \\succapprox e"],
  ["Precedence negations", "a \\nprec b \\nsucc c \\npreceq d \\nsucceq e \\quad a \\precneqq b \\succneqq c \\precnsim d \\succnsim e \\precnapprox f \\succnapprox g"],
  ["Binary triangles, products", "a \\triangleleft b \\triangleright c \\quad H \\lhd G \\rhd K \\unlhd L \\unrhd M \\quad A \\ltimes B \\rtimes C \\leftthreetimes D \\rightthreetimes E"],
  ["Circled, boxed", "a \\circledast b \\circledcirc c \\circleddash d \\quad a \\boxplus b \\boxminus c \\boxtimes d \\boxdot e"],
  ["Wedges, dots, others", "p \\barwedge q \\veebar r \\doublebarwedge s \\curlywedge t \\curlyvee u \\quad a \\divideontimes b \\dotplus c \\quad A^\\intercal \\quad G \\wr H \\quad a \\diamond b"],
  ["Triangle negations", "H \\ntriangleleft G \\ntriangleright K \\ntrianglelefteq L \\ntrianglerighteq M"],
  ["School shapes", "x > 0 \\therefore x^2 > 0 \\quad \\because a = b \\quad \\angle ABC = \\measuredangle ABC = 30^\\circ \\quad \\sphericalangle A"],
  ["Squares, checks", "\\square ABCD \\quad \\Box \\quad \\text{so } x = 2.\\ \\blacksquare \\quad \\checkmark"],
  ["Black shapes", "\\blacktriangle ABC \\; \\blacktriangledown \\quad a \\blacktriangleleft b \\blacktriangleright c \\quad \\lozenge \\Diamond p \\; \\blacklozenge \\quad \\bigstar \\; \\maltese"],
  ["Diagonals, back prime", "A \\diagup B \\diagdown C \\quad \\backprime x \\; x' \\; f^{\\backprime\\backprime} \\quad \\triangle \\; \\square \\; \\lozenge"],
  ["Suits", "\\spadesuit \\heartsuit \\diamondsuit \\clubsuit \\quad A\\spadesuit \\; K\\heartsuit \\; Q\\diamondsuit \\; J\\clubsuit"],
  ["AMS variants", "\\varnothing \\; \\hslash \\; a \\centerdot b \\; A \\smallsetminus B \\; a \\thicksim b \\thickapprox c \\; x \\varpropto y"],
  ["AMS variants, short", "a \\shortmid b \\nshortmid c \\shortparallel d \\nshortparallel e \\; \\vartriangle \\triangledown \\; a \\smallfrown b \\smallsmile c \\; \\Bbbk \\; p \\vDash q"],
  ["Sans serif", "\\mathsf{ABC\\,xyz\\,123} \\quad \\mathsfit{Ab} \\quad \\textsf{Text}"],
  ["Music","\\flat \\natural \\sharp \\quad B\\flat \\; C\\sharp \\; F\\natural \\quad X^\\flat \\; \\omega^\\sharp"],
  ["Proportional, defined, arcs", "y \\propto x \\quad u_n \\triangleq 2^n \\quad \\overset{\\frown}{AB} \\quad \\overset{\\smile}{CD} \\quad f \\asymp g"],
  ["Marked equalities", "a \\doteqdot b \\fallingdotseq c \\risingdotseq d \\eqcirc e \\circeq f \\triangleq g \\bumpeq h \\Bumpeq i \\eqsim j \\backsim k \\backsimeq l \\approxeq m \\between n \\asymp o \\frown p \\smile q \\propto r"],
  ["Negations", "x \\ne 0 \\quad 3 \\nmid 7 \\quad (d) \\nparallel (d') \\quad x \\notin A \\quad A \\nsubseteq B \\subsetneq C \\quad a \\nless b \\ngtr c \\nleq d \\ngeq e \\nleqslant f \\ngeqslant g \\quad ABC \\ncong DEF \\quad x \\nsim y"],
  ["More negations", "a \\nleqq b \\ngeqq c \\lneq d \\gneq e \\lneqq f \\gneqq g \\lvertneqq h \\gvertneqq i \\lnsim j \\gnsim k \\lnapprox l \\gnapprox m \\quad A \\subseteqq B \\supseteqq C \\subsetneqq D \\supsetneqq E \\nsubseteqq F \\nsupseteqq G \\varsubsetneq H \\varsupsetneq I \\varsubsetneqq J \\varsupsetneqq K \\quad p \\nvdash q \\nvDash r"],
  ["Complement, sets", "\\complement_E A = \\{x \\in E \\mid x \\notin A\\} \\quad x \\backepsilon A \\quad A \\sqsubset B \\sqsupset C \\quad A \\Subset B \\Supset C"],
  ["Joins, turnstiles", "A \\Cup B \\Cap C \\quad A \\pitchfork B \\quad R \\bowtie S \\quad \\Gamma \\Vdash \\varphi \\quad \\Gamma \\Vvdash \\psi \\quad p \\nVdash q \\nVDash r"],
  ["Maps", "A \\multimap B \\quad f \\origof g \\quad g \\imageof f \\quad R \\Join S"],
  ["Letter-like", "(O;\\, \\vec{\\imath}, \\vec{\\jmath}) \\quad \\varkappa \\; \\digamma \\; \\Game \\; \\Finv \\; \\mho \\; \\eth \\; \\yen \\; \\circledR \\; \\circledS"],
  ["Rings, primes, empty set", "\\mathring{A} \\; \\mathring{E} \\; \\mathring{a} \\quad f'(x),\\, f''(x),\\, f'''(x) \\quad A \\cap B = \\emptyset \\quad 0"],
  ["Primes, accents beside text", "a' \\; \\text{a’} \\quad a'' \\; \\text{a”} \\quad \\'{a} \\; \\text{á} \\quad \\tilde{a} \\; \\text{ã} \\quad \\bar{a} \\; \\text{ā} \\quad \\text{\\aa\\ å \\AA\\ Å}"],
  ["Lines", "\\overline{AB} \\; \\underline{AB} \\quad \\text{\\sout{abc}} \\quad \\cancel{5} \\; \\bcancel{5} \\; \\xcancel{AB} \\quad \\phase{-78^\\circ}"],
  ["Over and under", "\\widetilde{ac} \\; \\widehat{ac} \\; \\widecheck{ac} \\; \\utilde{AB} \\quad \\overgroup{AB} \\; \\undergroup{AB} \\quad \\overleftharpoon{ac} \\; \\overrightharpoon{ac}"],
  ["Braces and brackets over", "\\overbrace{a+b+c}^{\\text{note}} \\quad \\underbrace{a+b+c}_{\\text{note}} \\quad \\overbracket{AB} \\; \\underbracket{AB} \\quad \\overlinesegment{AB}"],
  ["Double strokes", "\\llbracket a, b \\rrbracket \\quad \\lBrace x \\rBrace \\quad x \\in \\R, \\N, \\Z, \\mathbb{Q}, \\Complex \\quad A \\Cup B \\Cap C \\quad \\iint \\; \\iiint \\; \\oiint"],
  ["Function", "f(x) = 3x^2 - 2x + 1, \\quad f'(x) = 6x - 2"],
  ["Area", "\\mathcal{A} = \\pi r^2, \\quad V = \\frac{4}{3}\\pi r^3"],
  ["Set operations", "A \\cup B, \\quad A \\cap B, \\quad A \\subseteq B, \\quad B \\supseteq A, \\quad M \\notin (d), \\quad f \\circ g"],
  ["Sets", "\\{x \\in \\mathbb{R} \\mid x > 0\\} \\quad \\mathbb{N} \\subset \\mathbb{Z} \\subset \\mathbb{Q}"],
  ["Blackboard", "\\mathbb{N} \\subset \\mathbb{Z} \\subset \\mathbb{Q} \\subset \\mathbb{R} \\subset \\mathbb{C} \\quad \\mathbb{ABCDEFGHIJKLMNOPQRSTUVWXYZ}"],
  // each capital, then its blackboard one (the line may break between pairs)
  ["Blackboard pairs", [..."ABCDEFGHIJKLMNOPQRSTUVWXYZ"].map((c) => `\\mathrm{${c}}\\mathbb{${c}}`).join("\\;\\;\\allowbreak ")],
  ["Logic", "x \\le 3 \\Rightarrow x^2 \\ge 0 \\quad A \\Leftrightarrow B"],
  ["More arrows", "f: x \\mapsto x^2 \\quad x \\longmapsto y \\quad \\rightharpoonup \\rightharpoondown \\leftharpoonup \\leftharpoondown \\quad A \\rightleftharpoons B \\quad \\Uparrow \\Downarrow \\Updownarrow \\quad \\nearrow \\searrow"],
  ["Negated arrows", "A \\nleftarrow B \\nrightarrow C \\nleftrightarrow D \\quad A \\nLeftarrow B \\nRightarrow C \\nLeftrightarrow D"],
  ["Paired arrows", "\\rightrightarrows \\leftleftarrows \\rightleftarrows \\leftrightarrows \\upuparrows \\downdownarrows"],
  ["Harpoons, triples", "\\upharpoonleft \\upharpoonright \\downharpoonleft \\downharpoonright \\leftrightharpoons \\quad \\Rrightarrow \\Lleftarrow"],
  ["Heads, tails, dashes", "\\twoheadrightarrow \\twoheadleftarrow \\rightarrowtail \\leftarrowtail \\dashrightarrow \\dashleftarrow"],
  ["Waves, curves", "\\rightsquigarrow \\leftrightsquigarrow \\curvearrowleft \\curvearrowright \\circlearrowleft \\circlearrowright"],
  ["Loops, turns", "\\looparrowleft \\looparrowright \\Lsh \\Rsh \\quad f \\rightsquigarrow g \\quad A \\twoheadrightarrow B"],
  ["Stretched arrows", "\\left\\uparrow \\begin{matrix} 1 \\\\ 2 \\\\ 3 \\end{matrix} \\right\\downarrow \\quad \\left\\Updownarrow \\begin{matrix} a \\\\ b \\end{matrix} \\right. \\quad \\bigl\\uparrow \\Bigl\\uparrow \\biggl\\Uparrow"],
  ["Symbols", "\\vdash \\dashv \\top \\models \\quad 1, \\cdots, n \\quad \\vdots \\ddots \\quad A \\setminus B \\quad a \\ast b \\star c \\quad x \\ll y \\gg z \\quad x \\doteq y"],
  ["Circled", "a \\oplus b \\ominus c \\otimes d \\oslash e \\odot f \\quad A \\sqcup B \\sqcap C \\quad A \\sqsubseteq B \\uplus C \\quad a \\amalg b \\quad \\hbar \\quad f'(x) = f''(x)"],
  ["Shapes", "\\triangle ABC \\quad a \\bigtriangleup b \\bigtriangledown c \\bigcirc d \\quad A \\cap B = \\emptyset \\quad A \\hookrightarrow B \\hookleftarrow C \\quad \\lnot p \\quad \\Updownarrow \\updownarrow \\quad |x| \\parallel"],
  ["Delimiters", "\\langle u, v \\rangle \\quad \\lfloor x \\rfloor \\quad \\lceil x \\rceil \\quad \\left\\langle \\frac{1}{2} \\right\\rangle \\quad \\left\\lfloor \\frac{x}{2} \\right\\rfloor \\quad \\left\\lceil \\sqrt{x} \\right\\rceil"],
  ["Groups, moustaches", "\\lgroup x \\rgroup \\quad \\lmoustache x \\rmoustache \\quad \\left\\lgroup \\frac{a}{b} \\right\\rgroup"],
  ["Group sizes", "\\bigl\\lgroup \\Bigl\\lgroup \\biggl\\lgroup \\Biggl\\lgroup x \\Biggr\\rgroup \\biggr\\rgroup \\Bigr\\rgroup \\bigr\\rgroup"],
  ["Moustaches, matrix", "\\Bigl\\lmoustache x \\Bigr\\rmoustache \\quad \\left\\lgroup \\begin{matrix} a & b \\\\ c & d \\end{matrix} \\right\\rgroup"],
  ["Tall bars", "\\left| \\frac{a}{b} \\right| \\quad \\left\\| \\frac{\\vec{u}}{2} \\right\\| \\quad \\bigl| \\Bigl| \\biggl| \\Biggl| x \\Biggr| \\biggr| \\Bigr| \\bigr|"],
  ["Determinants", "\\begin{vmatrix} a & b \\\\ c & d \\end{vmatrix} \\quad \\begin{vmatrix} 1 & 2 & 3 \\\\ 4 & 5 & 6 \\\\ 7 & 8 & 9 \\end{vmatrix}"],
  ["Tall brackets", "\\begin{pmatrix} 1 & 0 & 0 \\\\ 0 & 1 & 0 \\\\ 0 & 0 & 1 \\end{pmatrix} \\quad \\begin{bmatrix} a \\\\ b \\\\ c \\\\ d \\end{bmatrix}"],
  ["Tall ceilings, floors", "\\left\\lceil \\begin{matrix} x \\\\ y \\\\ z \\end{matrix} \\right\\rceil \\quad \\left\\lfloor \\begin{matrix} x \\\\ y \\\\ z \\end{matrix} \\right\\rfloor"],
  ["Tall braces", "f(x) = \\begin{cases} -1 & x < 0 \\\\ 0 & x = 0 \\\\ 1 & x > 0 \\end{cases} \\quad \\left\\{ \\begin{matrix} a \\\\ b \\\\ c \\\\ d \\end{matrix} \\right\\}"],
  ["Tall groups", "\\left\\lgroup \\begin{matrix} 1 & 2 \\\\ 3 & 4 \\\\ 5 & 6 \\end{matrix} \\right\\rgroup \\quad \\left\\lmoustache \\begin{matrix} x \\\\ y \\\\ z \\end{matrix} \\right\\rmoustache"],
  ["Corners", "\\ulcorner \\varphi \\urcorner \\quad \\ulcorner A \\to B \\urcorner \\quad \\llcorner x \\lrcorner \\quad \\llcorner \\frac{1}{2} \\lrcorner \\quad (\\lceil x \\rceil)"],
  ["Slashes", "(a/b)^2 \\quad \\mathbb{Z}/n\\mathbb{Z} \\quad \\text{and/or}"],
  ["Sized slashes","a / \\bigl/ \\Bigl/ \\biggl/ \\Biggl/ \\quad \\backslash \\bigl\\backslash \\Bigl\\backslash \\biggl\\backslash \\Biggl\\backslash"],
  ["Slashes between fractions", "\\left. \\frac{a}{b} \\middle/ \\frac{c}{d} \\right. \\quad \\left( \\dfrac{x+1}{y} \\middle/ z \\right)"],
  ["Quantifiers", "\\forall x \\in \\mathbb{R}, \\exists n \\in \\mathbb{N}, \\quad \\nexists y, \\quad p \\land q \\lor \\lnot r, \\quad \\nabla f, \\quad a \\mp b"],
  ["Equivalences", "a \\equiv b \\pmod{n} \\quad ABC \\sim DEF \\quad ABC \\cong DEF \\quad x \\simeq y \\quad x \\approx y"],
  ["Limits", "\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1, \\quad \\infty"],
  ["Sums", "\\sum_{k=1}^{n} k = \\frac{n(n+1)}{2}, \\quad \\int_0^1 x^2\\,dx = \\frac{1}{3}"],
  ["Big operators", "\\sum_{k=1}^{n} k^2 \\quad \\prod_{i=1}^{n} x_i \\quad \\coprod_{i} A_i \\quad \\int_0^1 f(x)\\,dx \\quad \\iint_D f \\quad \\iiint_V g"],
  ["Inline operators", "\\textstyle \\sum_{k=1}^{n} k = \\frac{n(n+1)}{2}, \\quad \\int_0^1 x^2\\,dx, \\quad \\prod_{i} x_i"],
  ["Big set operators", "\\bigcup_{i \\in I} A_i \\quad \\bigcap_{n} B_n \\quad \\bigsqcup_k C_k \\quad \\biguplus_j D_j"],
  ["Big logic, circled", "\\bigwedge_i p_i \\; \\bigvee_j q_j \\; \\bigoplus_i E_i \\; \\bigotimes_k V_k \\; \\bigodot_j W_j"],
  ["Contour integrals", "\\oint_C f \\quad \\oiint_S g \\quad \\oiiint_V h"],
  ["Inline set operators", "\\textstyle \\bigcup_i A_i \\, \\bigcap_n B_n \\, \\bigsqcup_k C_k \\, \\biguplus_j D_j \\, \\bigwedge_i p_i \\, \\bigvee_j q_j"],
  ["Inline circled, contours", "\\textstyle \\bigoplus_i E_i \\, \\bigotimes_k V_k \\, \\bigodot_j W_j \\, \\oint_C f \\, \\oiint_S g \\, \\oiiint_V h"],
  ["Matrix", "\\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}"],
  ["Text", "\\text{Médiatrice}(A;\\,B) \\quad \\text{Cercle}(O;\\,3)"],
  ["Bold", "\\mathbf{u} = \\boldsymbol{\\alpha} + \\mathbf{2}"],
];

const $ = (id) => document.getElementById(id);
const display = (tex) => `\\displaystyle ${tex}`;
$("versions").textContent = `Inter ${versions.inter} · KaTeX ${versions.katex}`;

const state = controls((weight) => {
  for (const [i, [, tex]] of SPECIMENS.entries()) document.querySelector(`[data-inter="${i}"]`).innerHTML = render(display(tex), "inter", weight);
  markInter($("rows"));
  tryIt();
});

$("rows").innerHTML = SPECIMENS.map(
  ([name, tex], i) =>
    `<tr title="${escapeHtml(tex)}"><td class="source">${escapeHtml(name)}</td>` +
    `<td class="math">${render(display(tex), "classic")}</td>` +
    `<td class="math ${INTER_MATH_CLASS}" data-inter="${i}">${render(display(tex), "inter", state.weight)}</td></tr>`,
).join("");
// blue: Inter's glyphs (as they are, or only resized, moved, turned, drawn out); the rest is drawn for Inter Math
document.fonts.ready.then(() => markInter($("rows")));

// whatever is typed, in both
$("try-inter").classList.add(INTER_MATH_CLASS);
function tryIt() {
  const tex = $("tex").value;
  $("try-classic").innerHTML = tex ? render(display(tex), "classic") : "";
  $("try-inter").innerHTML = tex ? render(display(tex), "inter", state.weight) : "";
  markInter($("try-inter"));
  try {
    localStorage.setItem("inter-math-workbench.try", tex);
  } catch {
    // private windows: the box starts empty
  }
}
try {
  $("tex").value = localStorage.getItem("inter-math-workbench.try") ?? "";
} catch {
  // private windows
}
$("tex").addEventListener("input", tryIt);
tryIt();

// the characters Inter Math leaves to KaTeX's fonts, by font
const KEPT = [
  ["Main-Regular", "Upright", ""],
  ["Math-Italic", "Italic", "mathnormal"],
  ["AMS-Regular", "AMS", "amsrm"],
];
$("kept").innerHTML = KEPT.map(([font, label, cls]) => {
  const chars = keptFromKatex(font)
    .filter((cp) => cp > 32 && !(cp >= 0x300 && cp < 0x370) && !(cp >= 0xe000 && cp < 0xf900))
    .map((cp) => String.fromCodePoint(cp));
  const cells = chars.map((c) => `<span class="kept ${cls}" title="U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}">${escapeHtml(c)}</span>`);
  return `<h3>${label} · ${chars.length}</h3><div class="${INTER_MATH_CLASS}"><div class="katex kept-grid">${cells.join("")}</div></div>`;
}).join("");
