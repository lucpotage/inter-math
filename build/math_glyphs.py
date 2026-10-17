"""
Glyphs Inter Math's OpenType font adds to KaTeX's (build/opentype.py): what
KaTeX draws as images at any size, or stacks, made the variants and pieces a
MATH table lists.

- Radicals: KaTeX's surd (src/surd.ts, through our patch's `__setSurd`) at a
  range of heights, the variants of √; past the tallest, its hook and the
  up-stroke made upright (TeX's tall radicals are), stacked from a straight
  piece. Each is the surd src/surd.ts draws for that height at each weight
  (its strokes the rule's), without its vinculum: the engine draws that from
  the glyph's advance, where KaTeX starts the radicand.
- Delimiters: between KaTeX's sizes (the text size, then 1.2, 1.8, 2.4, 3.0
  em), the two neighbouring sizes mixed (the same points at each: KaTeX's
  `anyHeight` images are drawn so), so that a delimiter grows in small steps;
  past the largest, its pieces: the largest cut where KaTeX draws it out (a
  parenthesis where its curves turn upright, a bracket across its stem), and
  the straight stretch between (talls() in build.py, src/svg.ts).
- What stretches sideways, as KaTeX's images (src/svg.ts): the arrows on the
  line and = cut across their shaft's straight run, and the straight run
  between; the vector accents (KaTeX's light arrow, as an accent and
  stretched); the wide accents (Inter's ᷍ ͠ drawn out to widths); the braces
  and groups over and under (Inter Math's { and ⟮ turned, drawn out, and their
  pieces), the brackets (the underline's line); the overline; the arrows
  upright, from KaTeX's Size1 pieces.
- Letters KaTeX has none of: Inter's upright small Greek, as it is, and the
  bold and bold italic letters, each weight's letter at a heavier weight.
"""

import json
import math
import subprocess
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib.models import VariationModel

from variable import NewGlyph, Shape

ROOT = Path(__file__).resolve().parent.parent
WEIGHTS = list(range(100, 1000, 100))

# the radical's heights (em, KaTeX's): every tenth from the normal surd's to KaTeX's largest, then coarser
RADICAL_HEIGHTS = [round(1.0 + 0.1 * i, 2) for i in range(21)] + [3.25, 3.5, 4.0, 4.5, 5.0]
# the normal surd's bottom (em): KaTeX's √ (its metrics: 0.2 em deep, 0.8 high)
RADICAL_DEPTH = 0.2
# how far up the stacked radical's hook its up-stroke goes upright (em), and its straight piece's length
RADICAL_UPRIGHT, RADICAL_PIECE = 0.3, 0.6


def variable_glyph(name: str, shapes: dict[tuple, Shape], space) -> NewGlyph:
    """A variable glyph from its shapes at any locations (wght, opsz), one of them Regular at the text size."""
    locations = list(shapes)
    base = shapes[(400, 14)]
    assert all(len(s.points) == len(base.points) and s.ends == base.ends for s in shapes.values()), f"{name}: shapes differ"
    model = VariationModel([space.normalized(loc) for loc in locations], axisOrder=["wght", "opsz"])
    glyph = Glyph()
    glyph.numberOfContours = len(base.ends)
    glyph.coordinates = GlyphCoordinates([(round(x), round(y)) for x, y in base.points])
    glyph.flags = bytearray(int(on) for on in base.on)
    glyph.flags[0] |= 0x40  # OVERLAP_SIMPLE: its parts overlap
    glyph.endPtsOfContours = list(base.ends)
    glyph.program = ttProgram.Program()
    glyph.program.fromBytecode(b"")
    values = [GlyphCoordinates([(round(x), round(y)) for x, y in shapes[loc].points] + [(0, 0), (round(shapes[loc].advance), 0), (0, 0), (0, 0)])
              for loc in locations]
    deltas = model.getDeltas(values)
    variations = [TupleVariation(support, [(round(x), round(y)) for x, y in delta])
                  for support, delta in zip(model.supports, deltas) if support and any(x or y for x, y in delta)]
    # the deltas a renderer infers from their neighbours' left out (as Inter's own: IUP)
    coordinates = GlyphCoordinates([(round(x), round(y)) for x, y in base.points] + [(0, 0), (round(base.advance), 0), (0, 0), (0, 0)])
    for v in variations:
        v.optimize(coordinates, list(base.ends), tolerance=0.5)
    return NewGlyph(name, glyph, round(base.advance), variations)


def clockwise(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """A polygon wound clockwise (y up), as TrueType's outer contours are."""
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]))
    return points if area < 0 else points[::-1]


def surds(heights: list[float]) -> dict[int, dict[float, dict]]:
    """
    KaTeX's surd as src/surd.ts draws it, by weight and height (em): its
    polygons (em, y up from the surd's bottom: the entry bar, the down-stroke,
    the up-stroke, the vinculum) and where the radicand starts. src/surd.ts,
    compiled, run by Node.
    """
    out = ROOT / "build" / "out" / "surd-js"
    subprocess.run([str(ROOT / "node_modules" / ".bin" / "tsc"), "--module", "commonjs", "--target", "es2022", "--skipLibCheck",
                    "--outDir", str(out), str(ROOT / "src" / "surd.ts")], check=True, cwd=ROOT)
    # CommonJS, where the project's package.json says ES modules
    (out / "package.json").write_text('{"type": "commonjs"}\n')
    script = """
const { interSurd } = require(process.argv[1] + "/surd.js");
const { rules } = require(process.argv[1] + "/metrics.js");
const heights = JSON.parse(process.argv[2]);
const out = {};
for (const w of Object.keys(rules)) {
  const surd = interSurd(rules[w]);
  out[w] = {};
  for (const h of heights) {
    // em, y up from the bottom: KaTeX's viewBox is 1000 units per em, y down from the top
    const polygons = surd.path("sqrtTall", 0, h * 1000, 0).split("Z").filter(Boolean).map((p) =>
      p.slice(1).split("L").map((xy) => { const [x, y] = xy.split(" ").map(Number); return [x / 1000, h - y / 1000]; }));
    out[w][h] = { polygons, advance: surd.box("sqrtTall", h).advanceWidth };
  }
}
console.log(JSON.stringify(out));
"""
    result = subprocess.run(["node", "-e", script, str(out), json.dumps(heights)], check=True, capture_output=True, text=True)
    return {int(w): {float(h): v for h, v in by_h.items()} for w, by_h in json.loads(result.stdout).items()}


def radical_glyphs(space, katex_em: float) -> tuple[list[NewGlyph], list[str], list[tuple]]:
    """
    √'s variants at RADICAL_HEIGHTS, and the pieces of taller ones (bottom to
    top: the hook, the straight piece, the top): the glyphs, the variants'
    names, the assembly's parts (name, extender, start and end connectors,
    advance).
    """
    data = surds([*RADICAL_HEIGHTS])
    em = lambda v: v * katex_em  # noqa: E731
    depth = em(RADICAL_DEPTH)
    glyphs, variants = [], []

    def shape(w: int, h: float, pieces) -> Shape:
        polygons = [clockwise([(em(x), em(y) - depth) for x, y in p]) for p in pieces]
        return Shape.join([Shape.polygon(p) for p in polygons], em(data[w][h]["advance"]))

    for i, h in enumerate(RADICAL_HEIGHTS):
        shapes = {}
        for w in WEIGHTS:
            bar, down, up, _vinculum = data[w][h]["polygons"]
            # the same at every optical size: KaTeX's surds are the text size's
            shapes[(w, 14)] = shape(w, h, [bar, down, up])
        name = f"radical.v{i}"
        glyphs.append(variable_glyph(name, shapes, space))
        variants.append(name)

    # past the tallest: its hook, the up-stroke upright for its last RADICAL_UPRIGHT em (its top's width kept), then
    # a straight piece, and the top, as thick, where the engine starts the vinculum (the glyph's advance: its right edge)
    h = RADICAL_HEIGHTS[-1]
    upright, piece = em(RADICAL_UPRIGHT), em(RADICAL_PIECE)
    hooks, straights, tops = {}, {}, {}
    for w in WEIGHTS:
        bar, down, up, _vinculum = data[w][h]["polygons"]
        join, top_left, top_right, bottom_right, bottom_inner = [(em(x), em(y) - depth) for x, y in up]
        top = top_left[1]
        slope = (top_right[0] - bottom_right[0]) / (top_right[1] - bottom_right[1])
        kink = top - upright
        left, right = top_left[0] - slope * upright, top_right[0] - slope * upright
        stroke = [join, (left, kink), (left, top), (right, top), (right, kink), bottom_right, bottom_inner]
        polygons = [clockwise([(em(x), em(y) - depth) for x, y in p]) for p in (bar, down)] + [clockwise(stroke)]
        hook = Shape.join([Shape.polygon(p) for p in polygons], right)
        bottom = hook.bounds()[1]
        hooks[(w, 14)] = hook.moved(0, -bottom)
        rect = lambda length: Shape.polygon(clockwise([(left, 0), (left, length), (right, length), (right, 0)]), right)  # noqa: E731
        straights[(w, 14)] = rect(piece)
        tops[(w, 14)] = rect(piece)
    names = ("radical.bot", "radical.ext", "radical.top")
    for name, shapes in zip(names, (hooks, straights, tops)):
        glyphs.append(variable_glyph(name, shapes, space))
    regular = hooks[(400, 14)]
    hook_height = regular.bounds()[3] - regular.bounds()[1]
    full = round(piece)
    parts = [(names[0], 0, 0, round(upright), round(hook_height)), (names[1], 1, full, full, full), (names[2], 0, full, 0, full)]
    return glyphs, variants, parts


# the delimiters drawn at sizes between KaTeX's (every one that has sizes), each tenth of an em from the text size's
# (1.0 em) to the largest (3.0 em)
MIXED = [0x28, 0x29, 0x5B, 0x5D, 0x2308, 0x2309, 0x230A, 0x230B, 0x7B, 0x7D, 0x27E8, 0x27E9, 0x27EE, 0x27EF, 0x23B0, 0x23B1,
         0x2F, 0x5C]
DELIMITER_HEIGHTS = [round(1.0 + 0.1 * i, 2) for i in range(21)]
# those stacked past the largest from its pieces, and how it is cut (talls() in build.py): a parenthesis where its
# curves turn upright (its on-curve points farthest out on that side), a bracket across its stem, in its middle
CUT = {0x28: "left", 0x29: "right", 0x5B: None, 0x5D: None, 0x2308: None, 0x2309: None, 0x230A: None, 0x230B: None}
# the straight stretch past each piece's cut, and the length of the straight piece between (em, KaTeX's)
CONNECTOR, EXTENDER = 0.15, 0.3


def mix(a: Shape, b: Shape, t: float) -> Shape:
    """Two shapes of the same points, a share t of the way from a to b."""
    assert len(a.points) == len(b.points) and a.ends == b.ends, "the sizes differ"
    points = [(ax + (bx - ax) * t, ay + (by - ay) * t) for (ax, ay), (bx, by) in zip(a.points, b.points)]
    return Shape(points, list(a.on), list(a.ends), a.advance + (b.advance - a.advance) * t)


def cut_across(shape: Shape, y: float) -> tuple[Shape, list[int]]:
    """
    A shape cut across at a height: each point's side (1 above), and on the
    cut each on-curve point there doubled, and each straight segment across
    it given two points where it crosses (one for each side, the lower first
    coming from below), so that each side closes along the cut.
    """
    points, on, ends, up = [], [], [], []
    for c in shape.contours():
        n = len(c.points)
        for i in range(n):
            (x0, y0), o0 = c.points[i], c.on[i]
            (x1, y1), o1 = c.points[(i + 1) % n], c.on[(i + 1) % n]
            if o0 and abs(y0 - y) < 0.5:
                below = c.points[i - 1][1] < y
                points += [(x0, y), (x0, y)]
                on += [True, True]
                up += [0, 1] if below else [1, 0]
            else:
                points.append((x0, y0))
                on.append(o0)
                up.append(int(y0 > y))
            if (y0 - y) * (y1 - y) < 0 and abs(y0 - y) >= 0.5 and abs(y1 - y) >= 0.5:
                assert o0 and o1, "the cut crosses a curve"
                x = x0 + (y - y0) / (y1 - y0) * (x1 - x0)
                points += [(x, y), (x, y)]
                on += [True, True]
                up += [0, 1] if y0 < y else [1, 0]
        ends.append(len(points) - 1)
    return Shape(points, on, ends, shape.advance), up


def halves(shape: Shape, up: list[int], y: float, connector: float) -> tuple[Shape, Shape, tuple[float, float]]:
    """
    The two sides of a shape cut across (cut_across()), each run on straight
    `connector` past the cut (the other side's points on the cut, moved on)
    or closed along it, and the ink's extent along the cut.
    """
    on_cut = [i for i, (p, o) in enumerate(zip(shape.points, shape.on)) if o and abs(p[1] - y) < 0.5]
    xs = [shape.points[i][0] for i in on_cut]
    sides = []
    for side in (0, 1):
        points, on, ends, start = [], [], [], 0
        for end in shape.ends:
            for i in range(start, end + 1):
                if up[i] == side:
                    points.append(shape.points[i])
                    on.append(shape.on[i])
                elif i in on_cut and connector:
                    # the other side's copy of a point on the cut, moved on past it
                    x, _ = shape.points[i]
                    points.append((x, y + connector if side == 0 else y - connector))
                    on.append(True)
            if points and (not ends or len(points) - 1 > ends[-1]):
                ends.append(len(points) - 1)
            start = end + 1
        sides.append(Shape(points, on, ends, shape.advance))
    return sides[0], sides[1], (min(xs), max(xs))


def delimiter_glyphs(space, katex_em: float, fonts: dict[str, Path], cmaps: dict[str, dict[int, str]], names: dict[str, dict[int, str]]):
    """
    The delimiters between KaTeX's sizes, and the pieces of the taller ones:
    the glyphs; by delimiter, its variants (glyph names, in the math font) and
    its assembly's parts (or None).
    """
    from delimiters import NORMAL, SIZES
    from variable import Masters

    roles = ["Upright", "Size1", "Size2", "Size3", "Size4"]
    heights = [NORMAL, *SIZES.values()]
    masters = {role: Masters(fonts[role], [cmaps[role][cp] for cp in MIXED if cp in cmaps[role]]) for role in roles}
    em = lambda v: v * katex_em  # noqa: E731
    glyphs, variants, assemblies = [], {}, {}
    for cp in MIXED:
        if not all(cp in cmaps[role] for role in roles):
            continue
        sized = [names[role][cp] for role in roles]
        chain = []
        for i, h in enumerate(DELIMITER_HEIGHTS):
            if h in heights:
                chain.append(sized[heights.index(h)])
                continue
            k = max(j for j, s in enumerate(heights) if s < h)
            t = (h - heights[k]) / (heights[k + 1] - heights[k])
            a, b = masters[roles[k]], masters[roles[k + 1]]
            name = f"{sized[0]}.v{i}"
            shapes = {(m["wght"], m["opsz"]): mix(a.shape(cmaps[roles[k]][cp], m), b.shape(cmaps[roles[k + 1]][cp], m), t)
                      for m in a.masters}
            glyphs.append(variable_glyph(name, shapes, space))
            chain.append(name)
        variants[cp] = chain
        if cp not in CUT:
            continue
        # past the largest: its two sides, each run on straight past the cut, and a straight piece of the stroke there
        largest = masters["Size4"]

        def cut_height(s: Shape) -> float:
            """Across a bracket's stem in its middle; where a parenthesis's curves turn upright (it moves with the weight)."""
            _, b0, _, b1 = s.bounds()
            if CUT[cp] is None:
                return (b0 + b1) / 2
            ons = [p for p, o in zip(s.points, s.on) if o]
            return (min if CUT[cp] == "left" else max)(ons, key=lambda p: p[0])[1]

        regular = largest.shape(cmaps["Size4"][cp], {"wght": 400, "opsz": 14})
        _, y0, _, y1 = regular.bounds()
        y = cut_height(regular)
        connector, extender = em(CONNECTOR), em(EXTENDER)
        bottoms, tops, stems = {}, {}, {}
        parts = None
        for m in largest.masters:
            s = largest.shape(cmaps["Size4"][cp], m)
            ym = cut_height(s)
            cut, up = cut_across(s, ym)
            assert parts is None or parts == up, f"U+{cp:04X}: cut differently at {m}"
            parts = up
            low, high, (x0, x1) = halves(cut, up, ym, connector)
            loc = (m["wght"], m["opsz"])
            bottoms[loc] = low.moved(0, -y0)
            tops[loc] = high.moved(0, -(ym - connector))
            stems[loc] = Shape.polygon(clockwise([(x0, 0), (x0, extender), (x1, extender), (x1, 0)]), s.advance)
        base = sized[0]
        piece_names = (f"{base}.bot", f"{base}.ext", f"{base}.top")
        glyphs += [variable_glyph(piece_names[0], bottoms, space), variable_glyph(piece_names[1], stems, space),
                   variable_glyph(piece_names[2], tops, space)]
        c, e = round(connector), round(extender)
        assemblies[cp] = [(piece_names[0], 0, 0, c, round(y + connector - y0)), (piece_names[1], 1, e, e, e),
                          (piece_names[2], 0, c, 0, round(y1 - (y - connector)))]
    return glyphs, variants, assemblies


def swapped(shape: Shape) -> Shape:
    """x and y swapped: a cut across x is a cut across y of this (and back)."""
    return Shape([(y, x) for x, y in shape.points], list(shape.on), list(shape.ends), shape.advance)


def run(shapes: list[Shape]) -> tuple[float, float]:
    """
    The widest stretch along x where none of the shapes (a glyph at its
    masters) has a point: its shaft's straight run, at every master
    (src/svg.ts's drawn() takes it at one weight).
    """
    def straight(s: Shape) -> list[tuple[float, float]]:
        """The stretches between its points where every edge crossing an upright is a straight level line."""
        xs = sorted({round(x, 3) for x, _ in s.points})
        out = []
        for a, b in zip(xs, xs[1:]):
            x = (a + b) / 2
            level = True
            for c in s.contours():
                n = len(c.points)
                for i in range(n):
                    (x0, y0), (x1, y1) = c.points[i], c.points[(i + 1) % n]
                    if (x0 - x) * (x1 - x) < 0 and not (c.on[i] and c.on[(i + 1) % n] and abs(y1 - y0) < 0.5):
                        level = False
            if level:
                out.append((a, b))
        return out

    def meet(xs: list[tuple[float, float]], ys: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [(max(a, c), min(b, d)) for a, b in xs for c, d in ys if min(b, d) > max(a, c)]

    common = straight(shapes[0])
    for s in shapes[1:]:
        common = meet(common, straight(s))
    assert common, "no straight run at every master"
    return max(common, key=lambda r: r[1] - r[0])


def apart(shapes: dict[tuple, Shape], least: float) -> dict[tuple, Shape]:
    """
    A glyph of arrows stacked (⇌ ⇄), each contour drawn out towards its head
    (KaTeX draws each out so: src/svg.ts's pair()) by as much at every master,
    until all their shafts run straight along a common stretch at least
    `least` long; the ink moved back to start where it did.
    """
    def own_run(c: Shape) -> tuple[float, float]:
        return run([c])

    def drawn(s: Shape, d: float) -> Shape:
        out, shift = [], 0.0
        for c in s.contours():
            a, b = own_run(c)
            middle = (a + b) / 2
            right = sum(x > middle for x, _ in c.points) > sum(x < middle for x, _ in c.points)
            moved = [(x + d, y) if right and x > middle else (x - d, y) if not right and x < middle else (x, y) for x, y in c.points]
            shift = max(shift, 0.0 if right else d)
            out.append(Shape(moved, c.on, c.ends, s.advance))
        joined = Shape.join(out, s.advance + 2 * d)
        return joined.moved(shift, 0)

    d = least
    for _ in range(40):
        trial = {loc: drawn(s, d) for loc, s in shapes.items()}
        try:
            a, b = run(list(trial.values()))
            if b - a >= least:
                return trial
        except AssertionError:
            pass
        d += least / 2
    raise AssertionError("its arrows can't be drawn apart")


def cut_sideways(shape: Shape, x: float) -> tuple[Shape, Shape, list[float]]:
    """
    A shape cut upright at x, across straight lines only (a shaft's edges):
    its left side, its right side moved to start at the cut, and where the
    edges cross the cut (y, bottom to top).
    """
    cut, up = cut_across(swapped(shape), x)
    left, right, _ = halves(cut, up, x, 0)
    ys = sorted({round(p[0], 3) for p, o in zip(cut.points, cut.on) if o and abs(p[1] - x) < 0.5})
    left, right = swapped(left), swapped(right)
    left.advance = x
    right = right.moved(-x, 0)
    right.advance = shape.advance - x
    return left, right, ys


def bars(ys: list[float], length: float, advance: float | None = None) -> Shape:
    """Horizontal bars from 0 to `length` between each pair of heights (bottom, top: a shaft's edges)."""
    pairs = list(zip(ys[::2], ys[1::2]))
    return Shape.join([Shape.polygon(clockwise([(0, y0), (0, y1), (length, y1), (length, y0)])) for y0, y1 in pairs],
                      length if advance is None else advance)


def stretched_pieces(name: str, shapes: dict[tuple, Shape], space, katex_em: float) -> tuple[list[NewGlyph], list[tuple]]:
    """
    A glyph's pieces to stretch it sideways (an arrow, =, a bracket): cut
    across its shaft's straight run where it is one at every master, its two
    sides and a straight piece of its shafts between. The glyphs, and the
    assembly's parts (left to right).
    """
    try:
        a, b = run(list(shapes.values()))
    except AssertionError:
        # its contours' heads overlap along x at some master (⇌'s at Black): each drawn out towards its head first
        shapes = apart(shapes, katex_em * EXTENDER / 2)
        a, b = run(list(shapes.values()))
    x = (a + b) / 2
    extender = katex_em * EXTENDER
    lefts, rights, mids = {}, {}, {}
    for loc, s in shapes.items():
        left, right, ys = cut_sideways(s, x)
        lefts[loc], rights[loc], mids[loc] = left, right, bars(ys, extender)
    names = (f"{name}.lft", f"{name}.ext", f"{name}.rgt")
    glyphs = [variable_glyph(n, by_loc, space) for n, by_loc in zip(names, (lefts, mids, rights))]
    regular = (400, 14)
    e = round(extender)
    parts = [(names[0], 0, 0, round(x - a), round(x)), (names[1], 1, e, e, e),
             (names[2], 0, round(b - x), 0, round(rights[regular].advance))]
    return glyphs, parts


# arrows on the line (and =) KaTeX stretches (\xrightarrow…: src/svg.ts): code point → its long form, a variant
STRETCHED = {0x2192: 0x27F6, 0x2190: 0x27F5, 0x2194: 0x27F7, 0x21D2: 0x27F9, 0x21D0: 0x27F8, 0x21D4: 0x27FA, 0x21A6: 0x27FC,
             0x21A9: None, 0x21AA: None, 0x21C0: None, 0x21C1: None, 0x21BC: None, 0x21BD: None, 0x21CC: None, 0x21CB: None,
             0x21C4: None, 0x21C6: None, 0x219E: None, 0x21A0: None, 0x3D: None}
# arrows upright, stacked from KaTeX's Size1 pieces (build/ams_arrow_glyphs.py), bottom to top: ⏐ and its ‖ between
UPRIGHT = {0x2191: ["shaft", 0x2191], 0x2193: [0x2193, "shaft"], 0x2195: [0x2193, "shaft", 0x2191],
           0x21D1: ["shafts", 0x21D1], 0x21D3: [0x21D3, "shafts"], 0x21D5: [0x21D3, "shafts", 0x21D1]}
# the wide accents (\widehat \widetilde \widecheck: Inter's ᷍ ͠, drawn out to a width, src/svg.ts): the accents they
# vary, the mark, upside down; their widths (em, KaTeX's boxes 0.6 to 3.3 em, and between)
WIDE = {0x0302: (0x1DCD, False), 0x0303: (0x0360, False), 0x030C: (0x1DCD, True)}
WIDE_WIDTHS = [0.6, 0.85, 1.1, 1.6, 2.2, 2.75, 3.3, 4.0, 5.0]
# the over and under braces and groups' variants: drawn out every quarter of an em past their own width, to 4 em
OVER_STEP, OVER_LONGEST = 0.25, 4.0
# \overbracket's upright ends (em, KaTeX's bracket's: src/svg.ts)
BRACKET_END = 0.29


def flipped(shape: Shape) -> Shape:
    """Upside down about its ink's middle (contours reversed: a flip turns their direction)."""
    _, y0, _, y1 = shape.bounds()
    out = []
    for c in shape.contours():
        out.append(Shape([(x, y0 + y1 - y) for x, y in reversed(c.points)], list(reversed(c.on)), c.ends, shape.advance))
    return Shape.join(out, shape.advance)


def mirrored(shape: Shape, width: float) -> Shape:
    """Left to right within `width` (contours reversed)."""
    out = []
    for c in shape.contours():
        out.append(Shape([(width - x, y) for x, y in reversed(c.points)], list(reversed(c.on)), c.ends, shape.advance))
    return Shape.join(out, shape.advance)


def parted_pieces(base: str, shapes: dict[tuple, Shape], parts: list[int], space, katex_em: float):
    """
    A shape lying along x whose points are in three parts (0 its left end, 1
    its middle, 2 its right end: a brace turned) cut in the straight
    stretches between them: the glyphs of its ends and middle and of the
    stretch, and the assembly's parts (left to right).
    """
    def gap(s: Shape, lo: int, hi: int) -> tuple[float, float]:
        a = max(x for (x, _), p in zip(s.points, parts) if p == lo)
        b = min(x for (x, _), p in zip(s.points, parts) if p == hi)
        assert b > a, "its parts overlap"
        return a, b

    # cut in the middle of each stretch at each master (a group's length follows the weight: its stretches move); each
    # piece then declared as long as it is at its shortest, and its straight ends likewise
    extender = katex_em * EXTENDER
    lefts, middles, rights, stems = {}, {}, {}, {}
    lengths: dict[str, list[float]] = {k: [] for k in ("left", "left end", "middle start", "middle end", "middle", "right start", "right")}
    for loc, s in shapes.items():
        (a0, b0), (a1, b1) = gap(s, 0, 1), gap(s, 1, 2)
        x0, x1 = (a0 + b0) / 2, (a1 + b1) / 2
        left, rest, ys = cut_sideways(s, x0)
        middle, right, _ = cut_sideways(rest, x1 - x0)
        lefts[loc], middles[loc], rights[loc], stems[loc] = left, middle, right, bars(ys, extender)
        for k, v in (("left", x0), ("left end", x0 - a0), ("middle start", b0 - x0), ("middle end", x1 - a1),
                     ("middle", x1 - x0), ("right start", b1 - x1), ("right", s.advance - x1)):
            lengths[k].append(v)
    least = {k: math.floor(min(v)) for k, v in lengths.items()}
    names = (f"{base}.lft", f"{base}.ext", f"{base}.mid", f"{base}.rgt")
    glyphs = [variable_glyph(n, by_loc, space) for n, by_loc in zip(names, (lefts, stems, middles, rights))]
    e = round(extender)
    assembly = [(names[0], 0, 0, least["left end"], least["left"]), (names[1], 1, e, e, e),
                (names[2], 0, least["middle start"], least["middle end"], least["middle"]), (names[1], 1, e, e, e),
                (names[3], 0, least["right start"], 0, least["right"])]
    return glyphs, assembly


def horizontal_glyphs(space, katex_em: float, upright: Path, inter: Path, cmap: dict[int, str],
                      cmaps: dict[str, dict[int, str]], names: dict[str, dict[int, str]]):
    """
    What stretches sideways, and the vector accents: the glyphs; horizontal
    variants and assemblies (by the math font's glyph name); vertical
    assemblies of the arrows upright; the characters it maps; accent
    attachments (the combining ones': their middle, on their origin).
    """
    from build import ACCENT, ACCENTS, GROUP_SIZE, VEC_SPAN, stretch_cuts, vec_arrow
    from arrow_glyphs import harpoon
    from operators import column
    from variable import Masters

    em = lambda v: v * katex_em  # noqa: E731
    glyphs, horizontal, horizontal_assembly, vertical_assembly, mapped, attachments = [], {}, {}, {}, {}, {}

    # arrows on the line: their long form, then their pieces (the long form's are the same: one outline, a longer shaft)
    m = Masters(upright, [cmaps["Upright"][cp] for cp in {*STRETCHED, *(v for v in STRETCHED.values() if v)} if cp in cmaps["Upright"]])
    for cp, long in STRETCHED.items():
        if cp not in cmaps["Upright"]:
            continue
        name = names["Upright"][cp]
        shapes = {(ms["wght"], ms["opsz"]): m.shape(cmaps["Upright"][cp], ms) for ms in m.masters}
        pieces, parts = stretched_pieces(name, shapes, space, katex_em)
        glyphs += pieces
        chain = [name, *([names["Upright"][long]] if long and long in names["Upright"] else [])]
        horizontal[name] = chain
        horizontal_assembly[name] = parts
        if long and long in names["Upright"]:
            horizontal[names["Upright"][long]] = [names["Upright"][long]]
            horizontal_assembly[names["Upright"][long]] = parts

    # arrows upright: KaTeX's Size1 pieces (the head with its shaft's start, ⏐, ‖)
    s1 = names["Size1"]
    shaft, shafts = s1.get(0x23D0), s1.get(0x2016)
    for cp, pieces in UPRIGHT.items():
        if cp not in names["Upright"] or not shaft or not shafts:
            continue
        vertical_assembly[names["Upright"][cp]] = [{"shaft": shaft, "shafts": shafts}[p] if isinstance(p, str) else s1[p] for p in pieces]
    if shaft:
        mapped[0x23D0] = shaft

    # the overline (‾, MathML's \overline) and the underscore, stretched: bars as thick as Inter's underline, the
    # overline as far over the x-height as Inter's underline is under the baseline
    icmap = TTFont(inter).getBestCmap()
    line_name, under_name = icmap[0x1E07], icmap[0x5F]
    im = Masters(inter, [line_name, "x", under_name])
    over, under = {}, {}
    for ms in im.masters:
        loc = (ms["wght"], ms["opsz"])
        text = {**ms, "opsz": 14}
        line = [c for c in im.shape(line_name, text).contours() if c.bounds()[3] <= 0]
        top = max(c.bounds()[3] for c in line)
        thickness = top - min(c.bounds()[1] for c in line)
        x_height = im.shape("x", ms).bounds()[3]
        bottom = x_height - top
        width = em(0.5)
        over[loc] = Shape.polygon(clockwise([(0, bottom), (0, bottom + thickness), (width, bottom + thickness), (width, bottom)]), width)
        u = im.shape(under_name, ms)
        _, uy0, _, uy1 = u.bounds()
        under[loc] = Shape.polygon(clockwise([(0, uy0), (0, uy1), (width, uy1), (width, uy0)]), width)
    for code, name, shapes in ((0x203E, "uni203E", over), (0x5F, "underscore.ext", under)):
        glyphs.append(variable_glyph(name, shapes, space))
        full = round(em(0.5))
        base = name if code == 0x203E else names["Upright"].get(0x5F, name)
        if code == 0x203E:
            mapped[code] = name
        horizontal_assembly[base] = [(name, 0, 0, full, full), (name, 1, full, full, full)]
    # the macron (ˉ, KaTeX's \bar; ¯, which TeXZilla writes \bar and \overline with): KaTeX's accent, drawn out as the
    # overline, at its height and thickness
    macron = names["Upright"].get(0x2C9)
    if macron:
        horizontal[macron] = [macron]
        horizontal_assembly[macron] = horizontal_assembly["uni203E"]

    # the vector accents (\vec \overrightarrow…: KaTeX's light arrow, build.py's vec_arrow): as an accent, its head
    # where Inter's accents start over lowercase, a little wider than a lowercase letter; stretched, its pieces
    vm = Masters(inter, [icmap[cp] for cp in [*ACCENTS.values(), ACCENT, *(mark for mark, _ in WIDE.values())]]
                 + ["arrowright", "n", "equal", "equal.case", "uni21B0"])
    vec, half = {}, {}
    for w in WEIGHTS:
        location = {"wght": w, "opsz": 14}
        arrow = vec_arrow(vm, location)
        accent = vm.shape(icmap[ACCENT], location).bounds()[1]
        span = VEC_SPAN * vm.shape("n", location).advance
        x0, y0, x1, _ = arrow.bounds()
        drawn = Shape([(0 if abs(x - x0) < 0.5 else span - (x1 - x), accent + y - y0) for x, y in arrow.points], list(arrow.on), list(arrow.ends), span)
        vec[(w, 14)] = drawn
        half[(w, 14)] = harpoon(drawn)
    accents = {0x20D7: ("uni20D7", vec, False), 0x20D6: ("uni20D6", vec, True), 0x20D1: ("uni20D1", half, False), 0x20D0: ("uni20D0", half, True)}
    for code, (name, shapes, left) in accents.items():
        shapes = {loc: (mirrored(s, s.advance) if left else s) for loc, s in shapes.items()}
        centred = {loc: Shape([(x - s.advance / 2, y) for x, y in s.points], s.on, s.ends, 0) for loc, s in shapes.items()}
        glyphs.append(variable_glyph(name, centred, space))
        mapped[code], attachments[name] = name, 0
        # stretched (\overrightarrow): its pieces, the head kept, the shaft drawn out
        pieces, parts = stretched_pieces(name, shapes, space, katex_em)
        glyphs += pieces
        horizontal[name] = [name]
        horizontal_assembly[name] = parts
    # ⃡ (\overleftrightarrow): the left head's piece and the right head's, as short as they go, and stretched between
    lefts = {loc: mirrored(s, s.advance) for loc, s in vec.items()}
    left_glyphs, left_parts = stretched_pieces("uni20E1.l", lefts, space, katex_em)
    right_glyphs, right_parts = stretched_pieces("uni20E1.r", vec, space, katex_em)
    glyphs += [left_glyphs[0], right_glyphs[1], right_glyphs[2]]
    both = [left_parts[0], right_parts[1], right_parts[2]]
    horizontal_assembly["uni20E1"] = both
    # the accent itself: each arrow cut in the middle of its shaft, the two heads' sides joined, centred on its origin
    left_cut, right_cut = sum(run(list(lefts.values()))) / 2, sum(run(list(vec.values()))) / 2
    shortest = {}
    for loc in vec:
        lp, rp = cut_sideways(lefts[loc], left_cut)[0], cut_sideways(vec[loc], right_cut)[1]
        width = lp.advance + rp.advance
        joined = Shape.join([lp, rp.moved(lp.advance, 0)], width)
        shortest[loc] = Shape([(x - width / 2, y) for x, y in joined.points], joined.on, joined.ends, 0)
    glyphs.append(variable_glyph("uni20E1", shortest, space))
    mapped[0x20E1], attachments["uni20E1"] = "uni20E1", 0
    horizontal["uni20E1"] = ["uni20E1"]

    # the wide accents: Inter's ᷍ ͠ drawn out to each width, where the accent sits (over the x-height)
    for code, (mark, upside_down) in WIDE.items():
        base = cmap.get(code)
        if base is None:
            continue
        chain = [base]
        for i, width in enumerate(WIDE_WIDTHS):
            shapes = {}
            for w in WEIGHTS:
                location = {"wght": w, "opsz": 14}
                o = vm.shape(icmap[mark], location)
                bottom = vm.shape(icmap[ACCENT], location).bounds()[1]
                x0, y0, x1, y1 = o.bounds()
                s = flipped(o) if upside_down else o
                shapes[(w, 14)] = Shape([((x - x0) / (x1 - x0) * em(width), bottom + y - y0) for x, y in s.points], s.on, s.ends, em(width))
            name = f"{base}.w{i}"
            glyphs.append(variable_glyph(name, shapes, space))
            chain.append(name)
        horizontal[base] = chain
        for spacing in {0x0302: (0x5E, 0x2C6), 0x0303: (0x7E, 0x2DC), 0x030C: (0x2C7,)}[code]:
            if spacing in cmap:
                horizontal[cmap[spacing]] = [cmap[spacing], *chain[1:]]

    # \overbrace \underbrace: Inter Math's { turned a quarter (its point up), drawn out along its stem's straight
    # stretches (KaTeX's images, build.py's accent_images()); \overparen \underparen: its ⟮ turned, as tall and thick as
    # Inter's ͜; their ends, middle and stretches to stack from
    brace_name = cmaps["Upright"][0x7B]
    group_name = cmaps["Upright"][0x27EE]
    um = Masters(upright, [brace_name, group_name])
    regular = um.shape(brace_name, {"wght": 400, "opsz": 14})
    upper, lower = stretch_cuts(regular)
    brace_parts = [2 if y > upper else 0 if y < lower else 1 for _, y in regular.points]
    bm = Masters(inter, [icmap[GROUP_SIZE]])

    def group_at(location: dict) -> Shape:
        """⟮ at the weight whose stem, against its height, is ͜'s stroke against its own, as tall as ͜ (build.py)."""
        breve = bm.shape(icmap[GROUP_SIZE], location)
        bx0, by0, bx1, by1 = breve.bounds()
        crossing = column(breve, (bx0 + bx1) / 2)
        stroke, tall = crossing[1] - crossing[0], by1 - by0

        def thickness(wght: float) -> float:
            g = um.shape(group_name, location, wght)
            gx0, _, gx1, _ = g.bounds()
            return g.side(0.5) / (gx1 - gx0)

        g = um.shape(group_name, location, um.weight_for(thickness, stroke / tall))
        gx0, _, gx1, _ = g.bounds()
        return g.scaled(tall / (gx1 - gx0))

    group_regular = group_at({"wght": 400, "opsz": 14})
    g_upper, g_lower = stretch_cuts(group_regular)
    group_parts = [2 if y > g_upper else 0 if y < g_lower else 1 for _, y in group_regular.points]

    def lying(s: Shape) -> Shape:
        """Turned a quarter clockwise (its top to the right), its ink from the origin, on the baseline."""
        t = s.turned(-90)
        x0, y0, x1, _ = t.bounds()
        out = t.moved(-x0, -y0)
        out.advance = x1 - x0
        return out

    # over their content, where accents are over the x-height; under it, as far under the baseline (KaTeX's images
    # keep Inter's gap between lowercase and its accents on the content's side)
    accent_bottom = {w: vm.shape(icmap[ACCENT], {"wght": w, "opsz": 14}).bounds()[1] for w in WEIGHTS}
    accent_gap = {w: accent_bottom[w] - im.shape("x", {"wght": w, "opsz": 14}).bounds()[3] for w in WEIGHTS}

    def placed(s: Shape, w: int, under: bool) -> Shape:
        """A shape whose ink starts on the baseline, over the content (on its top) or under it (turned over)."""
        if not under:
            return s.moved(0, accent_bottom[w])
        _, y0, _, y1 = s.bounds()
        return flipped(s).moved(0, -accent_gap[w] - y1)

    for code, under_code, shape_at, parts, base in ((0x23DE, 0x23DF, lambda ms: um.shape(brace_name, ms), brace_parts, "uni23DE"),
                                                     (0x23DC, 0x23DD, group_at, group_parts, "uni23DC")):
        raw = {w: lying(shape_at({"wght": w, "opsz": 14})) for w in WEIGHTS}
        for c, name, flip in ((code, base, False), (under_code, f"uni{under_code:04X}", True)):
            shapes = {(w, 14): placed(raw[w], w, flip) for w in WEIGHTS}
            if flip:
                # a flip reverses each contour: so do its points' parts
                regular_over, flipped_parts, start = raw[400], [], 0
                for end in regular_over.ends:
                    flipped_parts += list(reversed(parts[start:end + 1]))
                    start = end + 1
                parts = flipped_parts
            glyphs.append(variable_glyph(name, shapes, space))
            mapped[c] = name
            # drawn out: its ends moved apart, the middle staying in the middle (KaTeX's images)
            chain = [name]
            widest = max(sh.advance for sh in shapes.values())
            widths = [k * OVER_STEP for k in range(1, int(OVER_LONGEST / OVER_STEP) + 1) if em(k * OVER_STEP) > widest]
            for i, width in enumerate(widths):
                drawn = {}
                for loc, sh in shapes.items():
                    reach = (em(width) - sh.advance) / 2
                    drawn[loc] = Shape([(x + (2 * reach if p == 2 else reach if p == 1 else 0), y) for (x, y), p in zip(sh.points, parts)],
                                       sh.on, sh.ends, sh.advance + 2 * reach)
                glyphs.append(variable_glyph(f"{name}.w{i}", drawn, space))
                chain.append(f"{name}.w{i}")
            horizontal[name] = chain
            pieces, assembly = parted_pieces(name, shapes, parts, space, katex_em)
            glyphs += pieces
            horizontal_assembly[name] = assembly

    # \overbracket \underbracket: a line as thick as Inter's underline, its ends upright towards the content
    for code, under in ((0x23B4, False), (0x23B5, True)):
        name = f"uni{code:04X}"
        shapes = {}
        for w in WEIGHTS:
            location = {"wght": w, "opsz": 14}
            line = [c for c in im.shape(line_name, location).contours() if c.bounds()[3] <= 0]
            t = max(c.bounds()[3] for c in line) - min(c.bounds()[1] for c in line)
            e, width = em(BRACKET_END), em(1.0)
            rects = [[(0, e), (0, e + t), (width, e + t), (width, e)], [(0, 0), (0, e + t), (t, e + t), (t, 0)],
                     [(width - t, 0), (width - t, e + t), (width, e + t), (width, 0)]]
            shapes[(w, 14)] = placed(Shape.join([Shape.polygon(clockwise(r)) for r in rects], width), w, under)
        glyphs.append(variable_glyph(name, shapes, space))
        mapped[code] = name
        horizontal[name] = [name]
        # its pieces: each end with the line's start, and the line between
        pieces, parts = stretched_pieces(name, shapes, space, katex_em)
        glyphs += pieces
        horizontal_assembly[name] = parts
    return glyphs, horizontal, horizontal_assembly, vertical_assembly, mapped, attachments


# bold: this much heavier than the weight, no heavier than Black (Inter's heaviest: drawn on past it, its counters close)
BOLD = 300


def bold_weight(w: float) -> float:
    return min(w + BOLD, 900)


# the weights a bold glyph is drawn at: the axis's ends and Regular, and where its bold reaches Black (outlines are
# linear in between, as Inter's are between its masters: off by a unit or two where the avar bends)
BOLD_WEIGHTS = sorted({100, 400, 900 - BOLD, 900})


def copied_glyphs(space, path: Path, names: dict[str, str]) -> list[NewGlyph]:
    """A font's glyphs as they are (its name → the math font's), flattened (Inter's composite Greek)."""
    from variable import Masters

    m = Masters(path, list(names))
    out = []
    for old, new in names.items():
        shapes = {(ms["wght"], ms["opsz"]): m.shape(old, ms) for ms in m.masters}
        out.append(variable_glyph(new, shapes, space))
    return out


def bold_glyphs(space, sources: list[tuple[Path, dict[str, str]]]) -> list[NewGlyph]:
    """Glyphs of fonts (their name → the math font's) drawn at each weight's bold (bold_weight())."""
    from variable import Masters

    out = []
    for path, names in sources:
        m = Masters(path, list(names))
        for old, new in names.items():
            # where the bold weight turns: the masters, and where it reaches Black
            shapes = {(w, o): m.shape(old, {"wght": w, "opsz": o}, wght=bold_weight(w)) for w in BOLD_WEIGHTS for o in (14, 32)}
            out.append(variable_glyph(new, shapes, space))
    return out
