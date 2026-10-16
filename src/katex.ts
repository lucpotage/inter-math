/**
 * KaTeX with Inter Math's hooks: here the installed KaTeX, which pnpm patches
 * (patches/katex@0.19.0.patch); in the npm package, the patched KaTeX itself
 * (build/deliver.mjs puts it in place of this file), so an app needs no patch.
 */
export { default } from "katex";
