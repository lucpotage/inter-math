# Changelog

`pnpm release` takes a version's notes from here for its GitHub release.

## 1.1.0

- Inter Math as an OpenType math font (`opentype/` in the release ZIP): one
  font with a MATH table for LaTeX (`unicode-math`), Typst, Word, PowerPoint,
  LibreOffice and MathML. Its nine weights, and variable (its MATH table's
  rules and gaps varying with the weight). The same glyphs as KaTeX's Inter
  Math, laid out by the same TeX parameters; Unicode's math alphabets
  (italic, bold, bold italic, sans serif, double-struck), script forms
  (`ssty`), dotless letters for accents (`dtls`); delimiters and √ every tenth
  of an em and stacked past their largest; arrows, braces, brackets, wide
  and vector accents that stretch sideways. Its em is Inter's.
- `inter-math/mathml.css` (its nine weights as web fonts) and
  `inter-math/mathml-variable.css` (the variable font) for MathML, math at
  the weight of its text, scripts in the font's script forms.
- KaTeX takes the same font: each role it has a font for (upright, italic,
  AMS, blackboard, the four sizes) is a feature of the font's own, which the
  stylesheet turns on, with KaTeX's em, ascent and descent (`size-adjust` and
  overrides). One file in place of eight: `fonts/InterMathVariable.woff2`, and
  the release ZIP's `ttf/` is gone. KaTeX's layout is unchanged; the optical
  size now follows the glyphs' size, as in Inter's text (24 px math: 25.5
  rather than 29).
- KaTeX's stylesheet names its faces "Inter Math KaTeX…", so that it and
  `mathml.css` can share a page.
- MathJax 4: the OpenType font as MathJax's (SVG output, Regular weight),
  the package's `svg.js` (`mathjax-font/` in the release ZIP), which MathJax
  loads from the package's URL.
- Examples (`examples/`): the same formulas set with KaTeX, MathML, Temml,
  TeXZilla and MathJax.
- ¯ (the spacing macron, TeXZilla's \bar and \overline) is ˉ, stretched as the
  overline.

## 1.0.1

The same fonts and code as 1.0.0, released from GitHub Actions: staged on npm
through trusted publishing, with provenance, and approved by hand.

- The fonts carry version 1.001.
- The build is reproducible: the same sources give the same files, on macOS
  as on GitHub's Linux machines.

## 1.0.0

The first release.

- Every symbol KaTeX documents drawn from Inter, variable in weight (100–900)
  and optical size (14–32): KaTeX's upright, italic, AMS, blackboard and size
  fonts; typewriter, Fraktur, calligraphic and script letters stay in KaTeX's.
- `setMathFont("inter" | "classic")`: KaTeX lays math out with Inter Math's
  metrics, rules, surds and arrows at any weight, or with its own.
- On npm as `inter-math`, with KaTeX 0.19.0 inside (`inter-math/katex`) and
  its stylesheet (`inter-math/katex.css`, `inter-math/katex.min.css`).
- `InterMath-1.0.0.zip`: the variable fonts as TTF, and the KaTeX integration.
