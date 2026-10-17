# Inter Math

Math drawn from [Inter](https://rsms.me/inter/), variable in weight
(100–900) and optical size (14–32): an OpenType math font for what sets math
(LaTeX, Typst, Word, MathML, MathJax), which KaTeX takes too, with the metrics
KaTeX lays it out with and a switch back to Computer Modern.

Every symbol KaTeX documents is drawn from Inter: letters and digits, the
operators and relations, the AMS symbols (with their own designs where they
share a character with Main), the larger delimiters and big operators,
blackboard bold, and sans serif (`\mathsf`, Inter being one). What Inter has
no design for stays in KaTeX's fonts: typewriter, Fraktur, calligraphic and
script letters, and ℜ ℑ ℘ ℵ ℶ ℷ ℸ.

TeX's layout follows the font too: fraction bars, rules and √ are as thick as
Inter Math's minus sign at every weight, the math axis sits on its operators'
centre, and underlines, strike-throughs and arrows are Inter's own.

## Use it

### The OpenType math font

One font with a MATH table, the standard way fonts carry math layout, for
LaTeX (LuaLaTeX and XeLaTeX with `unicode-math`), Typst, Word, PowerPoint,
LibreOffice and MathML in browsers. It is the same design as KaTeX's Inter
Math, laid out by TeX's rules as Inter Math gives them to KaTeX: rules as
thick as the minus sign at every weight, √ and delimiters growing a tenth of
an em at a time and stacked past their largest, Unicode's math alphabets
(italic, bold, sans serif, double-struck).

Each [release](https://github.com/lucpotage/inter-math/releases)'s ZIP has it
in `opentype/`: its nine weights (`InterMath-Thin.ttf` to
`InterMath-Black.ttf`, the family "Inter Math"), which desktop apps take, and
`InterMathVariable.ttf`. Install the weights, then:

```latex
\usepackage{unicode-math}
\setmathfont{Inter Math}
```

```typ
#show math.equation: set text(font: "Inter Math")
```

In Word and PowerPoint, pick it as the equations' font (Equation Options).
For MathML (browsers' own math layout, Temml), the npm package has
`inter-math/mathml.css`: its nine weights as web fonts, math taking the weight
of its text.

For MathJax 4, the package has the same font as MathJax's (its `svg.js`: the
SVG output, at the Regular weight), which MathJax loads from the package's
URL, with a component that has no font of its own:

```html
<script>
  window.MathJax = { output: { font: "https://cdn.jsdelivr.net/npm/inter-math" } };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg-nofont.js"></script>
```

Its em is Inter's: math is as large as Inter's text at the same size. Script,
Fraktur and monospace letters, which Inter has no design for, come from
another math font (`unicode-math`'s `range` option).

### With KaTeX, from npm

```bash
pnpm add inter-math
```

The package brings its own KaTeX (0.19.0, with the hooks Inter Math lays math
out through), its stylesheet and the fonts:

```ts
import "inter-math/katex.min.css"; // KaTeX's stylesheet and Inter Math's (katex.css unminified)
import katex from "inter-math/katex"; // KaTeX with Inter Math's hooks; its extensions at inter-math/katex/contrib/*
import { setMathFont } from "inter-math";

setMathFont("inter", { weight: 400 }); // "classic" restores KaTeX's own layout exactly
katex.render("e^{i\\pi} + 1 = 0", element);
```

Put the `inter-math` class on an ancestor of the math, and give the CSS the
same weight (`--inter-math-weight`). KaTeX's settings are global: math already
rendered keeps its layout until it is rendered again. `withMathFont` renders
with one font and then restores the current one.

The stylesheet sets KaTeX's math in the OpenType math font (its variable
font): each role KaTeX has a font for (upright, italic, AMS, blackboard, the
four sizes of delimiters and big operators) is a feature of the font's own,
in KaTeX's em.

The arrows drawn with small heads (AMS arrows such as ↣ ⇉ ↺ ↰, and the vectors
`\vec`, `\overrightarrow`…) have angle heads, as every other arrow does.
`setMathFont("inter", { arrowHeads: "triangle" })` gives them filled
triangles, like Inter's own small arrows (the font's `ss01` stylistic set).

The package's own README ([build/README.npm.md](build/README.npm.md)) says
more: KaTeX's extensions, libraries that import `katex` themselves, a CDN.

### The fonts

Each [release](https://github.com/lucpotage/inter-math/releases) has a ZIP:
the OpenType math font (`opentype/`), the same font for MathJax
(`mathjax-font/`), and the npm package (`katex/`: the KaTeX integration, the
stylesheets for MathML, their fonts).

## Develop

```bash
pnpm install       # KaTeX 0.19.0, with patches/katex@0.19.0.patch applied
pnpm font:setup    # once: the build's Python, with fontTools, in build/.venv
pnpm font:build    # the fonts, the OpenType math font, and the sources generated from them
```

| Command | What it does |
|---|---|
| `pnpm font:build` | builds a font per role KaTeX sets math in from Inter (`build/out/*.ttf`) and writes the generated sources (`src/metrics.ts`, `src/provenance.ts`) and `build/parts.md` (what each glyph is built on, and what is built on it); then the OpenType math font from them (`build/opentype.py`: `build/out/opentype/`, `fonts/InterMath-*.woff2`, `fonts/InterMathVariable.woff2`), and MathJax's font from it (`build/mathjax.py`: `src/mathjax-font/`) |
| `pnpm test` | KaTeX's layout in both fonts: rules, surds, arrows, underlines, the switch back to KaTeX's fonts |
| `pnpm typecheck` | TypeScript |
| `pnpm workbench` | the test pages on http://localhost:3150 |
| `pnpm examples` | the examples (`examples/`: KaTeX, MathML, Temml, TeXZilla, MathJax, from the package `pnpm dist` builds) on http://127.0.0.1:3153/examples/ |
| `pnpm dist` | builds the deliverables into `dist/` and checks them (`build/deliver.mjs`): the npm package (`dist/npm/`, its tarball) and the release ZIP |
| `pnpm release` | builds the fonts again, tests, typechecks, `pnpm dist`, then tags `vX.Y.Z`, publishes to npm and makes the GitHub release with the ZIP (`--dry-run`: npm's dry run, no tag) |
| `node workbench/katex-docs.mjs` | re-extracts the examples of KaTeX's documentation for the installed version (`workbench/katex-docs.json`) |

The workbench pages have weight and size sliders and a white-on-black mode:
school-math specimens with a box to try any LaTeX; every symbol and function
in KaTeX's documentation in Computer Modern, in Inter Math, and in the Inter
glyphs each one is drawn from (Inter's own glyphs in blue, the rest drawn for
Inter Math); the package as `pnpm dist` builds it.

Linked from this repository (`inter-math@link:`), the package is `src/`: the
app needs the same patched KaTeX through pnpm's `patchedDependencies`, and
loads `inter-math/inter-math.css` after KaTeX's own stylesheet.

| Path | What |
|---|---|
| `sources/inter/` | Inter's variable fonts, the source |
| `build/` | the build (Python and fontTools): `build.py`, one module per family of glyphs, `patch_katex.py` (KaTeX's hooks); the OpenType math font, `opentype.py` (its MATH table: `math_table.py`; its variants and pieces: `math_glyphs.py`); MathJax's font, `mathjax.py`; the delivery, `deliver.mjs`, and the package's README |
| `src/` | `setMathFont`, surds, KaTeX's SVG images redrawn, the CSS (KaTeX's, and MathML's: `mathml.css`), MathJax's font (`mathjax-font/`, generated), generated metrics and provenance |
| `fonts/` | the built WOFF2 files the CSS loads |
| `patches/` | KaTeX's patch, generated by `build/patch_katex.py` |
| `test/` | the vitest suite |
| `workbench/` | the test pages: plain HTML and ES modules, served by Vite |
| `examples/` | the examples: plain HTML, the package from `dist/npm/` |

## Release

`package.json`'s version is the release's: the npm package's, the tag's
(`v1.0.0`) and the fonts' (`head.fontRevision` and name ID 5, as Geist's:
M.X.Y is M.(100X+Y), 1.0.0 is 1.000). To release:

1. raise the version in `package.json` and write its notes in
   [CHANGELOG.md](CHANGELOG.md) (`## X.Y.Z`);
2. `pnpm font:build` (the fonts carry the version), `pnpm dist` to check,
   and commit;
3. `git tag vX.Y.Z && git push origin main vX.Y.Z`.

The tag starts [the release workflow](.github/workflows/release.yml): it
builds the fonts again (they must come out as committed), tests, packs,
stages the version on npm through trusted publishing, and makes the GitHub
release with the ZIP and the changelog's notes. The version goes public on
npm once approved with a maintainer's second factor:

```bash
npm stage list inter-math
npm stage approve <stage-id>
```

(or npmjs.com, the package's Staged Packages tab). `pnpm release` does the same from
this machine (the first release, before npm trusted the workflow).
Commits follow [Conventional Commits](https://www.conventionalcommits.org/).

## Licence

The fonts are under the SIL Open Font License 1.1, as Inter's
([OFL.txt](OFL.txt)), and so is the rest of this repository. The npm package
also carries KaTeX, under the MIT licence, and KaTeX's own fonts, under the
OFL (its `LICENSE.md`).
