#!/usr/bin/env node
/**
 * Inter Math's delivery: the npm package and the release ZIP, from the built
 * fonts (pnpm font:build) and src/.
 *
 *     pnpm dist                  dist/: the package, its tarball and the ZIP, checked
 *     pnpm release --dry-run     the same after the font build, tests and typecheck; npm's dry run
 *     pnpm release               …then publishes to npm, tags vX.Y.Z, makes the GitHub release
 *                                (by hand: the first release; then a pushed tag is enough, .github/workflows/release.yml)
 *
 * The version is package.json's (the fonts carry it as M.(100X+Y): build.py).
 * The root package stays private: only dist/npm/ is published, as the tarball
 * checked here. It brings KaTeX with it (KaTeX 0.19.0 with patches/…, as
 * pnpm installs it here), so an app needs no patch:
 *
 *   dist/npm/                     the package, inter-math
 *     lib/                        setMathFont… (src/, compiled), lib/katex.js the patched KaTeX, lib/contrib/ KaTeX's
 *     katex.css, katex.min.css    KaTeX's stylesheet with Inter Math's (src/inter-math.css)
 *     mathml.css                  the OpenType math font for MathML, its nine weights (src/mathml.css);
 *     mathml-variable.css         variable (src/mathml-variable.css)
 *     svg.js                      the OpenType math font as MathJax 4's (SVG output), at its Regular weight
 *                                 (build/mathjax.py: src/mathjax-font/svg.js): MathJax loads <package URL>/svg.js
 *     fonts/                      Inter Math's WOFF2 (the OpenType math font: variable, which KaTeX and
 *                                 mathml-variable.css load, and its nine weights) and KaTeX's (the fallback and
 *                                 Computer Modern)
 *   dist/inter-math-X.Y.Z.tgz     npm pack of dist/npm/
 *   dist/InterMath-X.Y.Z.zip      the GitHub release's asset: opentype/ (the OpenType math font: its weights, and
 *                                 variable), mathjax-font/ (MathJax's), katex/ (the package)
 */
import { execFileSync, spawnSync } from "node:child_process";
import { copyFileSync, cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { createInterface } from "node:readline/promises";
import { fileURLToPath } from "node:url";
import { transform } from "lightningcss";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIST = join(ROOT, "dist");
const PKG = join(DIST, "npm");
const KATEX = join(ROOT, "node_modules", "katex");

const root = JSON.parse(readFileSync(join(ROOT, "package.json"), "utf8"));
const katexVersion = JSON.parse(readFileSync(join(KATEX, "package.json"), "utf8")).version;
const VERSION = root.version;
const [major, minor, patch] = VERSION.split("-")[0].split(".").map(Number);
const FONT_VERSION = `${major}.${String(minor * 100 + patch).padStart(3, "0")}`;
const TAG = `v${VERSION}`;
const TARBALL = join(DIST, `${root.name}-${VERSION}.tgz`);
const ZIP_NAME = `InterMath-${VERSION}`;
const ZIP = join(DIST, `${ZIP_NAME}.zip`);
/** The OpenType math font (build/opentype.py): its weights, and variable (KaTeX's, and MathML's). */
const WEIGHTS = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"];
const OPENTYPE = [...WEIGHTS.map((w) => `InterMath-${w}`), "InterMathVariable"];

const args = new Set(process.argv.slice(2));
const release = args.has("--release");
const dryRun = args.has("--dry-run");

function step(title) {
  console.log(`\n▸ ${title}`);
}

function fail(message) {
  console.error(`\n✗ ${message}`);
  process.exit(1);
}

/** npm without the settings pnpm passes its scripts (npm warns of those it doesn't know). */
function envFor(cmd) {
  if (cmd !== "npm") return process.env;
  return Object.fromEntries(Object.entries(process.env).filter(([key]) => !/^npm_config_/i.test(key)));
}

/** Runs a command in the terminal (its output shown); stops the delivery if it fails. */
function run(cmd, cmdArgs, options = {}) {
  const r = spawnSync(cmd, cmdArgs, { cwd: ROOT, stdio: "inherit", env: envFor(cmd), ...options });
  if (r.status !== 0) fail(`${cmd} ${cmdArgs.join(" ")} failed`);
}

/** A command's output, or null if it fails. */
function output(cmd, cmdArgs, options = {}) {
  try {
    return execFileSync(cmd, cmdArgs, { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], env: envFor(cmd), ...options }).trim();
  } catch {
    return null;
  }
}

async function confirm(question) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  const answer = await rl.question(`\n? ${question} [y/N] `);
  rl.close();
  return /^y(es)?$/i.test(answer.trim());
}

const isGit = output("git", ["rev-parse", "--is-inside-work-tree"]) === "true";

// ---------------------------------------------------------------------------------------------------------------
// before a release: the sources as committed, built again and tested

if (release) {
  if (isGit && output("git", ["status", "--porcelain"])) fail("commit your changes first: a release is built from a clean tree");
  step("pnpm font:build");
  run("pnpm", ["font:build"]);
  if (isGit && spawnSync("build/.venv/bin/python", ["build/check_build.py"], { cwd: ROOT, stdio: "inherit" }).status !== 0)
    fail("the font build changed tracked files (fonts/, src/metrics.ts…): commit them, then release again");
  step("pnpm test");
  run("pnpm", ["test"]);
  step("pnpm typecheck");
  run("pnpm", ["typecheck"]);
}

// ---------------------------------------------------------------------------------------------------------------
// the fonts: built, and at this version

step(`fonts at version ${FONT_VERSION}`);
const check = `
import sys
from fontTools.ttLib import TTFont
for path in sys.argv[2:]:
    font = TTFont(path)
    version = f"{font['head'].fontRevision:.3f}"
    if version != sys.argv[1] or not font["name"].getDebugName(5).startswith(f"Version {sys.argv[1]};"):
        sys.exit(f"{path}: version {version}, not {sys.argv[1]}: run pnpm font:build")
`;
const fontFiles = [
  ...OPENTYPE.map((f) => join(ROOT, "build", "out", "opentype", `${f}.ttf`)),
  ...OPENTYPE.map((f) => join(ROOT, "fonts", `${f}.woff2`)),
];
for (const file of fontFiles) if (!existsSync(file)) fail(`${relative(ROOT, file)} is missing: run pnpm font:build`);
run(join(ROOT, "build", ".venv", "bin", "python"), ["-c", check, FONT_VERSION, ...fontFiles]);

// ---------------------------------------------------------------------------------------------------------------
// the package

step(`dist/npm: ${root.name}@${VERSION}, KaTeX ${katexVersion}`);
rmSync(DIST, { recursive: true, force: true });
mkdirSync(join(PKG, "lib", "contrib"), { recursive: true });
mkdirSync(join(PKG, "fonts"), { recursive: true });

// src/ compiled; relative imports get their .js, as Node's ES modules need
run("pnpm", ["exec", "tsc", "-p", "tsconfig.build.json"]);
const relativeImport = /((?:from|import)\s*\(?\s*["'])(\.\.?\/[^"']+?)(["'])/g;
for (const file of readdirSync(join(DIST, "build"))) {
  const code = readFileSync(join(DIST, "build", file), "utf8");
  writeFileSync(join(PKG, "lib", file), code.replace(relativeImport, (_, a, path, b) => `${a}${/\.[cm]?js$/.test(path) ? path : `${path}.js`}${b}`));
}
rmSync(join(DIST, "build"), { recursive: true });

// lib/katex.js: KaTeX as pnpm patched it, in place of src/katex.ts's re-export of it
const katexModule = readFileSync(join(KATEX, "dist", "katex.mjs"), "utf8");
for (const hook of ["__setGlobalMetrics", "__setSurd", "__setSvgDesign", "__setComposedText", "__setRuleImages"])
  if (!katexModule.includes(hook)) fail(`node_modules/katex isn't patched (no ${hook}): run pnpm install`);
writeFileSync(
  join(PKG, "lib", "katex.js"),
  `/*! KaTeX ${katexVersion} (MIT, Khan Academy and other contributors), with Inter Math's hooks (patches/katex@${katexVersion}.patch) */\n${katexModule}`,
);
copyFileSync(join(KATEX, "types", "katex.d.ts"), join(PKG, "lib", "katex.d.ts"));
// KaTeX's extensions, on this KaTeX (they import their package's own)
for (const file of readdirSync(join(KATEX, "dist", "contrib")).filter((f) => f.endsWith(".mjs"))) {
  const name = file.replace(/\.mjs$/, "");
  const code = readFileSync(join(KATEX, "dist", "contrib", file), "utf8");
  writeFileSync(join(PKG, "lib", "contrib", `${name}.js`), code.replaceAll("'../katex.mjs'", "'../katex.js'"));
  copyFileSync(join(KATEX, "types", "contrib", `${name}.d.mts`), join(PKG, "lib", "contrib", `${name}.d.ts`));
}

// fonts: Inter Math's, and KaTeX's (WOFF2: what browsers that run KaTeX 0.19 load)
for (const f of OPENTYPE) copyFileSync(join(ROOT, "fonts", `${f}.woff2`), join(PKG, "fonts", `${f}.woff2`));
for (const f of readdirSync(join(KATEX, "dist", "fonts")).filter((f) => f.endsWith(".woff2")))
  copyFileSync(join(KATEX, "dist", "fonts", f), join(PKG, "fonts", f));

// katex.css: KaTeX's stylesheet (its fonts as WOFF2 only) and Inter Math's, the fonts beside it in fonts/
const katexCss = readFileSync(join(KATEX, "dist", "katex.css"), "utf8").replace(
  /(url\(fonts\/[^)]+\.woff2\) format\("woff2"\))(?:, url\([^)]+\) format\("(?:woff|truetype)"\))+/g,
  "$1",
);
const interCss = readFileSync(join(ROOT, "src", "inter-math.css"), "utf8").replaceAll('url("../fonts/', 'url("fonts/');
const css = [
  `/*! Inter Math ${VERSION} for KaTeX ${katexVersion}: KaTeX's stylesheet (MIT, Khan Academy and other contributors) and Inter Math's (SIL OFL 1.1) */`,
  katexCss.trim(),
  "",
  interCss.trim(),
  "",
].join("\n");
writeFileSync(join(PKG, "katex.css"), css);
const minified = transform({ filename: "katex.css", code: Buffer.from(css), minify: true });
writeFileSync(join(PKG, "katex.min.css"), minified.code);
// mathml.css, mathml-variable.css: the OpenType math font for MathML, the fonts beside them in fonts/
for (const sheet of ["mathml.css", "mathml-variable.css"])
  writeFileSync(
    join(PKG, sheet),
    `/*! Inter Math ${VERSION} for MathML (SIL OFL 1.1) */\n${readFileSync(join(ROOT, "src", sheet), "utf8").replaceAll('url("../fonts/', 'url("fonts/').trim()}\n`,
  );
// svg.js: the OpenType math font as MathJax's (build/mathjax.py), at the root: MathJax loads <package URL>/svg.js
copyFileSync(join(ROOT, "src", "mathjax-font", "svg.js"), join(PKG, "svg.js"));
if (!readFileSync(join(PKG, "svg.js"), "utf8").includes(`Inter Math ${VERSION} for MathJax`))
  fail("src/mathjax-font/svg.js isn't at this version: run pnpm font:build");
for (const sheet of ["katex.css", "katex.min.css", "mathml.css", "mathml-variable.css"]) {
  const missing = [...readFileSync(join(PKG, sheet), "utf8").matchAll(/url\("?([^")]+)"?\)/g)]
    .map((m) => m[1])
    .filter((url) => !existsSync(join(PKG, url)));
  if (missing.length) fail(`${sheet} loads files the package lacks: ${missing.join(", ")}`);
}

// licences, README, changelog
copyFileSync(join(ROOT, "OFL.txt"), join(PKG, "OFL.txt"));
writeFileSync(
  join(PKG, "LICENSE.md"),
  `# Licences

| What | Licence |
|---|---|
| Inter Math's fonts (\`fonts/InterMath*.woff2\`) and its code and stylesheets (\`lib/\` but \`lib/katex.js\` and \`lib/contrib/\`, Inter Math's part of \`katex.css\`, \`mathml.css\`, \`mathml-variable.css\`) | SIL Open Font License 1.1: [OFL.txt](OFL.txt) |
| KaTeX ${katexVersion} (\`lib/katex.js\`, with Inter Math's hooks; \`lib/contrib/\`; KaTeX's part of \`katex.css\`) | MIT, below |
| KaTeX's fonts (\`fonts/KaTeX_*.woff2\`, unmodified) | SIL Open Font License 1.1, with the Reserved Font Names \`KaTeX_*\` (in each font) |

## KaTeX

\`\`\`
${readFileSync(join(KATEX, "LICENSE"), "utf8").trim()}
\`\`\`
`,
);
writeFileSync(join(PKG, "README.md"), readFileSync(join(ROOT, "build", "README.npm.md"), "utf8").replaceAll("{{VERSION}}", VERSION).replaceAll("{{KATEX}}", katexVersion));
copyFileSync(join(ROOT, "CHANGELOG.md"), join(PKG, "CHANGELOG.md"));

const lib = (name) => ({ types: `./lib/${name}.d.ts`, default: `./lib/${name}.js` });
const manifest = {
  name: root.name,
  version: VERSION,
  description: root.description,
  keywords: root.keywords,
  author: root.author,
  license: root.license,
  repository: root.repository,
  homepage: root.homepage,
  bugs: root.bugs,
  type: "module",
  sideEffects: ["*.css", "./lib/contrib/*.js"],
  main: "./lib/index.js",
  types: "./lib/index.d.ts",
  exports: {
    ".": lib("index"),
    "./katex": lib("katex"),
    "./katex/contrib/*": lib("contrib/*"),
    "./katex.css": "./katex.css",
    "./katex.min.css": "./katex.min.css",
    "./mathml.css": "./mathml.css",
    "./mathml-variable.css": "./mathml-variable.css",
    "./svg.js": "./svg.js",
    "./provenance": lib("provenance"),
    "./fonts/*": "./fonts/*",
    "./package.json": "./package.json",
  },
  // KaTeX is inside (lib/katex.js): the version Inter Math's metrics and hooks are made for
  katex: katexVersion,
};
writeFileSync(join(PKG, "package.json"), `${JSON.stringify(manifest, null, 2)}\n`);

// ---------------------------------------------------------------------------------------------------------------
// the tarball, installed and used as an app would

step(`dist/${relative(DIST, TARBALL)}`);
run("npm", ["pack", "--pack-destination", DIST], { cwd: PKG, stdio: ["ignore", "ignore", "inherit"] });
if (!existsSync(TARBALL)) fail(`npm pack made no ${relative(ROOT, TARBALL)}`);

step("the tarball, installed in a fresh app");
const app = join(DIST, "smoke");
mkdirSync(app);
writeFileSync(join(app, "package.json"), JSON.stringify({ name: "smoke", private: true, type: "module" }));
run("npm", ["install", "--no-audit", "--no-fund", "--no-package-lock", "--ignore-scripts", TARBALL], { cwd: app, stdio: ["ignore", "ignore", "inherit"] });
writeFileSync(
  join(app, "smoke.ts"),
  `import katex from "inter-math/katex";
import renderMathInElement from "inter-math/katex/contrib/auto-render";
import "inter-math/katex/contrib/mhchem";
import { setMathFont, versions, type MathFont } from "inter-math";
import { drawn } from "inter-math/provenance";

const font: MathFont = "inter";
setMathFont(font, { weight: 500 });
const html: string = katex.renderToString("\\\\sqrt{\\\\frac{a}{b}} + \\\\ce{H2O} \\\\leqslant \\\\mathbb{R}", { throwOnError: true });
if (!html.includes("katex")) throw new Error("KaTeX rendered nothing");
if (versions.katex !== katex.version) throw new Error(\`KaTeX \${katex.version}, metrics for \${versions.katex}\`);
if (typeof renderMathInElement !== "function" || !Object.keys(drawn).length) throw new Error("an export is missing");
setMathFont("classic");
console.log(\`  rendered with KaTeX \${katex.version} and Inter Math (\${html.length} characters of HTML)\`);
`,
);
// types, as a Node app checks them; then the code, by Node itself
run(join(ROOT, "node_modules", ".bin", "tsc"), ["--noEmit", "--strict", "--module", "nodenext", "--moduleResolution", "nodenext", "--target", "es2022", "--skipLibCheck", "false", "smoke.ts"], { cwd: app });
run(join(ROOT, "node_modules", ".bin", "tsc"), ["--module", "nodenext", "--moduleResolution", "nodenext", "--target", "es2022", "--skipLibCheck", "smoke.ts"], { cwd: app });
run("node", ["smoke.js"], { cwd: app });
rmSync(app, { recursive: true });

// ---------------------------------------------------------------------------------------------------------------
// the ZIP: what the GitHub release offers for download

step(`dist/${ZIP_NAME}.zip`);
const stage = join(DIST, "zip", ZIP_NAME);
mkdirSync(join(stage, "opentype"), { recursive: true });
mkdirSync(join(stage, "mathjax-font"), { recursive: true });
copyFileSync(join(PKG, "svg.js"), join(stage, "mathjax-font", "svg.js"));
for (const f of OPENTYPE) copyFileSync(join(ROOT, "build", "out", "opentype", `${f}.ttf`), join(stage, "opentype", `${f}.ttf`));
cpSync(PKG, join(stage, "katex"), { recursive: true });
copyFileSync(join(ROOT, "OFL.txt"), join(stage, "OFL.txt"));
writeFileSync(
  join(stage, "README.txt"),
  `Inter Math ${VERSION}

Math drawn from Inter: variable in weight (100-900) and optical size
(14-32). The fonts carry version ${FONT_VERSION}.

opentype/  Inter Math as an OpenType math font: one font with a MATH table,
           for LaTeX (LuaLaTeX, XeLaTeX with unicode-math), Typst, Word,
           PowerPoint, LibreOffice and MathML. Its nine weights
           (InterMath-Thin.ttf to InterMath-Black.ttf), and
           InterMathVariable.ttf, variable in weight and optical size.
mathjax-font/  the same font for MathJax 4's SVG output, at its Regular
           weight (svg.js): MathJax loads it from the folder's URL
           (output: { font: "https://…/mathjax-font" }; a folder named
           mathjax would clash with MathJax's own), with a component that
           has no font of its own (tex-svg-nofont.js).
katex/     the KaTeX integration, as published on npm (inter-math): KaTeX
           ${katexVersion} with Inter Math's hooks (lib/katex.js),
           setMathFont (lib/index.js), the stylesheet (katex.css,
           katex.min.css), the stylesheets for MathML (mathml.css,
           mathml-variable.css), and their fonts (fonts/: the OpenType math
           font, which KaTeX takes too, its roles being features of the
           font's, and KaTeX's own). katex/README.md says how to use them.

The fonts are under the SIL Open Font License 1.1 (OFL.txt); KaTeX's code is
under the MIT licence (katex/LICENSE.md).
`,
);
run("zip", ["-q", "-r", "-X", ZIP, ZIP_NAME], { cwd: join(DIST, "zip") });
rmSync(join(DIST, "zip"), { recursive: true });

const size = (file) => `${(readFileSync(file).length / 1024).toFixed(0)} KB`;
console.log(`\n✓ ${relative(ROOT, TARBALL)} (${size(TARBALL)}), ${relative(ROOT, ZIP)} (${size(ZIP)})`);
if (!release) process.exit(0);

// ---------------------------------------------------------------------------------------------------------------
// the release: npm, then GitHub

const npmUser = output("npm", ["whoami"]);
if (!npmUser) fail("not logged in to npm: run npm login");
const published = output("npm", ["view", `${root.name}@${VERSION}`, "version"]);
if (published) fail(`${root.name}@${VERSION} is already on npm: raise the version in package.json`);

if (dryRun) {
  step(`npm publish --dry-run (as ${npmUser})`);
  run("npm", ["publish", TARBALL, "--dry-run", "--access", "public"]);
  console.log(`\n✓ dry run: nothing published, no tag made`);
  process.exit(0);
}

if (!isGit) fail("the GitHub release needs this folder in a GitHub repository (git init, gh repo create): nothing published");
if (output("git", ["tag", "--list", TAG])) fail(`the tag ${TAG} exists already: raise the version in package.json`);
const notes = (readFileSync(join(ROOT, "CHANGELOG.md"), "utf8").split(/^## /m).find((s) => s.startsWith(`${VERSION}`)) ?? "")
  .split("\n")
  .slice(1)
  .join("\n")
  .trim();
if (!notes) fail(`CHANGELOG.md has no "## ${VERSION}" section: write the release's notes there`);

if (!(await confirm(`Publish ${root.name}@${VERSION} to npm as ${npmUser}, tag ${TAG} and make its GitHub release?`))) fail("stopped: nothing published");
// npm first: the tag pushed after starts .github/workflows/release.yml, which then finds the version published
step(`npm publish (npm asks for your second factor)`);
run("npm", ["publish", TARBALL, "--access", "public"]);
step(`git tag ${TAG}`);
run("git", ["tag", "-a", TAG, "-m", `Inter Math ${VERSION}`]);
run("git", ["push", "origin", "HEAD", TAG]);
step(`GitHub release ${TAG}`);
const notesFile = join(DIST, "notes.md");
writeFileSync(notesFile, `${notes}\n`);
run("gh", ["release", "create", TAG, ZIP, "--verify-tag", "--title", `Inter Math ${VERSION}`, "--notes-file", notesFile]);
console.log(`\n✓ ${root.name}@${VERSION} is on npm (https://www.npmjs.com/package/${root.name}), and ${TAG} on GitHub with ${ZIP_NAME}.zip`);
