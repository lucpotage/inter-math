# Changelog

`pnpm release` takes a version's notes from here for its GitHub release.

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
