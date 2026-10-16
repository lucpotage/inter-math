# Inter Math

KaTeX's fonts redrawn from [Inter](https://rsms.me/inter/), variable in
weight (100–900) and optical size (14–32), with the metrics KaTeX lays them
out with and a switch back to Computer Modern.

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
KaTeX's fonts to Inter Math there), and give it the same weight:

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

## Licences

The fonts are under the SIL Open Font License 1.1 ([OFL.txt](OFL.txt)), as
Inter's. KaTeX ({{KATEX}}, inside) is under the MIT licence, and its own fonts
under the OFL: [LICENSE.md](LICENSE.md).
