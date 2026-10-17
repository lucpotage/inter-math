# Inter Math

Math drawn from [Inter](https://rsms.me/inter/), variable in weight
(100–900) and optical size (14–32): an OpenType math font, for KaTeX (with
the metrics KaTeX lays it out with and a switch back to Computer Modern),
MathML and MathJax.

Every symbol KaTeX documents is drawn from Inter. What Inter has no design for
stays in KaTeX's fonts: typewriter, Fraktur, calligraphic and script letters,
and ℜ ℑ ℘ ℵ ℶ ℷ ℸ.

```bash
pnpm add inter-math
```

## With KaTeX

The package brings its own KaTeX ({{KATEX}}, with the hooks Inter Math lays
math out through): render with it, not with the `katex` package.

```ts
import "inter-math/katex.min.css"; // KaTeX's stylesheet and Inter Math's, with their fonts
import katex from "inter-math/katex"; // KaTeX {{KATEX}} with Inter Math's hooks
import { setMathFont } from "inter-math";

setMathFont("inter", { weight: 400 }); // "classic" gives KaTeX's own layout back, exactly
katex.render("e^{i\\pi} + 1 = 0", element);
```

Put the `inter-math` class on an ancestor of the math (the stylesheet switches
KaTeX's fonts to Inter Math there: the OpenType math font, each role KaTeX
has a font for being a feature of the font's own), and give it the same
weight:

```html
<article class="inter-math" style="--inter-math-weight: 400">…</article>
```

KaTeX's settings are global: math already rendered keeps its layout until it
is rendered again. `withMathFont(font, render)` renders with one font and then
restores the current one.

- `katex.css` is the stylesheet unminified; `katex.min.css` minified.
- KaTeX's extensions are there too, on the same KaTeX:
  `inter-math/katex/contrib/auto-render`, `…/mhchem`, `…/copy-tex`,
  `…/render-a11y-string`, `…/mathtex-script-type`.
- Libraries that import `katex` themselves (rehype-katex, markdown-it
  plugins…) render with Inter Math once your bundler resolves `katex` to
  `inter-math/katex`. With Vite:

  ```ts
  resolve: { alias: [{ find: /^katex$/, replacement: "inter-math/katex" }] }
  ```

- `setMathFont("inter", { arrowHeads: "triangle" })` gives the small arrows
  (↣ ⇉ ↺ ↰, `\vec`, `\overrightarrow`…) filled triangle heads, like Inter's
  own small arrows.

## For MathML

Browsers lay MathML out themselves (and what builds on it: Temml, KaTeX's
MathML output) from a math font's MATH table. The package has Inter Math as an
OpenType math font, the same design laid out by the same rules:

```ts
import "inter-math/mathml.css"; // math { font-family: "Inter Math" }: its nine weights as web fonts
```

Math takes the weight of its text (`font-weight`, which browsers otherwise set
to normal for math), from Thin to Black in steps of 100: one font per weight,
each with its own rules and gaps. Scripts take the font's script forms (its
`ssty`, which browsers don't apply), as KaTeX's do. Load it after another
stylesheet for MathML (Temml's), which names its own font. Its em is
Inter's: math is as large as Inter's text at the same size.

`inter-math/mathml-variable.css` is the variable font instead (any weight and
optical size), its rules and gaps varying with the weight through the MATH
table's variations, which browsers apply once their HarfBuzz does (its version
after 14.6.0): until then a weight other than Regular gets Regular's rules.

The release ZIP on GitHub has the same font as TTF (`opentype/`), for LaTeX
(`\setmathfont{Inter Math}` with `unicode-math`), Typst, Word and the like.

## For MathJax

MathJax 4 lays math out from its own font data, made from an OpenType math
font. The package has Inter Math's (its SVG output, at the Regular weight),
`svg.js` at its root, so that MathJax loads it from the package's URL, with a
component that has no font of its own:

```html
<script>
  window.MathJax = { output: { font: "https://cdn.jsdelivr.net/npm/inter-math@{{VERSION}}" } };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg-nofont.js"></script>
```

Served from your own site, the URL is the folder holding `svg.js` (a full URL:
`new URL("…", location.href).href`), any folder not named `mathjax`, whose
name MathJax would take for its own.

## Without a bundler

From a CDN, as ES modules:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/inter-math@{{VERSION}}/katex.min.css" />
<script type="module">
  import katex from "https://cdn.jsdelivr.net/npm/inter-math@{{VERSION}}/lib/katex.js";
  import { setMathFont } from "https://cdn.jsdelivr.net/npm/inter-math@{{VERSION}}/lib/index.js";
  setMathFont("inter");
  katex.render("\\sum_{n=1}^\\infty \\frac{1}{n^2} = \\frac{\\pi^2}{6}", document.querySelector("#formula"));
</script>
```

The release ZIP on GitHub holds the same files, and the fonts as TTF.
`mathml.css` is at `https://cdn.jsdelivr.net/npm/inter-math@{{VERSION}}/mathml.css`.

## Licences

The fonts are under the SIL Open Font License 1.1 ([OFL.txt](OFL.txt)), as
Inter's. KaTeX ({{KATEX}}, inside) is under the MIT licence, and its own fonts
under the OFL: [LICENSE.md](LICENSE.md).
