"""
Glyphs for KaTeX's scripts: exponents, indices, limits.

KaTeX sets scripts at 70% of the text (\\scriptstyle) and second-level ones at
50% (\\scriptscriptstyle) by scaling the text font down: everything gets thin
and tight. Inter draws figures and signs for fractions (.dnom, the
denominators: 54% of a digit), relatively heavier and looser than the text
ones. In scripts:

- digits and + − = ( ) , . are those, brought back to a digit's height (KaTeX
  scales them down again), the signs centred where the text ones are (Inter
  centres its fraction signs on the small digits, math on its axis), + − = as
  much larger as the operators, and as heavy (build/operators.py);
- letters, which Inter doesn't draw small, follow the same design: the text
  letter at a heavier weight, spaced like the fraction figures; ! ? too
  (Inter has no fraction forms of them either).

The stroke for a size comes from Inter's own design, linearly between the
text figures (100%, full stroke) and the fraction figures (54%, their
stroke); the weight that gives it is found on the weight axis. Every master
gets its own (build/variable.py), so script glyphs still follow the weight
and optical size.

They are reached through stylistic sets that the CSS turns on in KaTeX's
smaller sizes: ss19 for scripts, ss20 for second-level scripts (letters reuse
their script forms there).
"""

from operators import OFFSET, SCALE, axis_drop, case
from variable import STEM, Masters, NewGlyph, Shape

DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
SIGNS = ["plus", "minus", "equal", "parenleft", "parenright", "comma", "period"]
OPERATOR_SIGNS = {"plus", "minus", "equal"}
# stylistic set → (glyph suffix, size relative to the text): \scriptstyle, \scriptscriptstyle
SIZES = {"ss19": ("script", 0.7), "ss20": ("scriptscript", 0.5)}
LETTER_FEATURE = "ss19"
FRACTION_STEM = f"{STEM}.dnom"


def script_glyphs(
    path, letters: list[str], figures: bool, bases: dict[str, str] | None = None
) -> tuple[list[NewGlyph], dict[str, list[tuple[str, str]]]]:
    """
    Script forms for the letters named (glyph names in the font) and, with
    `figures`, the digits and signs: the new glyphs, and the substitutions of
    each stylistic set (base glyph → script glyph). `bases` names the glyph the
    font maps a sign to, when it isn't Inter's (the math operators).
    """
    bases = bases or {}
    small = DIGITS + SIGNS if figures else []
    # the fraction digits give the spacing of the script letters too
    m = Masters(path, [*letters, *DIGITS, *small, *(f"{n}.case" for n in small), *(f"{n}.dnom" for n in DIGITS + small), FRACTION_STEM])
    default = m.masters[m.default]

    # how much looser Inter spaces its fraction figures than its text ones (relative to their height)
    def spacing(names: list[str]) -> float:
        inst = m.instance(default["wght"], default["opsz"])
        _, bottom, top = m.section(names[0], default["wght"], default["opsz"])
        total = 0
        for n in names:
            s = Shape.of(inst, n)
            x0, _, x1, _ = s.bounds()
            total += (s.advance - (x1 - x0)) / (top - bottom)
        return total

    loosen = spacing([FRACTION_STEM, *(f"{d}.dnom" for d in DIGITS if d != "one")]) / spacing([STEM, *(d for d in DIGITS if d != "one")])

    new: list[NewGlyph] = []
    features: dict[str, list[tuple[str, str]]] = {tag: [] for tag in SIZES}
    for tag, (suffix, size) in SIZES.items():
        drawn: dict[str, list[Shape]] = {}
        for master in m.masters:
            w, o = master["wght"], master["opsz"]
            text_stem, text_bottom, text_top = m.section(STEM, w, o)
            frac_stem, frac_bottom, frac_top = m.section(FRACTION_STEM, w, o)
            # Inter's stroke at this size: linear from the text figures (1, 1) to the fraction figures
            frac_size = (frac_top - frac_bottom) / (text_top - text_bottom)
            stroke = 1 - (1 - size) * (1 - frac_stem / text_stem) / (1 - frac_size)
            target = stroke * text_stem

            if figures:
                # the fraction figures' weight whose stem, at a digit's height then scaled to the size, is the target
                def effective(x: int) -> float:
                    stem, bottom, top = m.section(FRACTION_STEM, x, o)
                    return stem * (text_top - text_bottom) / (top - bottom) * size

                wf = min(m.weights, key=lambda x: abs(effective(x) - target))
                _, bottom, top = m.section(FRACTION_STEM, wf, o)
                k = (text_top - text_bottom) / (top - bottom)
                # + − =: as heavy as the operators, and as much larger (SCALE: drawn lighter to keep the stroke)
                thick = lambda x: (lambda b: b[3] - b[1])(m.shape("minus.dnom", master, x).bounds())  # noqa: E731
                light = max(m.weights[0], wf - OFFSET)
                grown = m.weight_for(lambda x: thick(x) * SCALE, thick(light))

                def larger(shape: Shape) -> Shape:
                    """SCALE times as large about its ink's middle, its side bearings kept."""
                    x0, y0, x1, y1 = shape.bounds()
                    cy = (y0 + y1) / 2
                    out = shape.map(lambda x, y: (x0 + (x - x0) * SCALE, cy + (y - cy) * SCALE))
                    out.advance = shape.advance + (x1 - x0) * (SCALE - 1)
                    return out

                bar = larger(m.shape("minus.dnom", master, grown).moved(0, -bottom).scaled(k))
                bx0, by0, bx1, by1 = bar.bounds()
                for n in DIGITS + SIGNS:
                    if n == "equal":
                        # = drawn out to the bar's width, not scaled: its gap kept (as in the text, build/operators.py)
                        s = m.shape(f"{n}.dnom", master, light).moved(0, -bottom).scaled(k)
                        s = s.bars_to(bx0, bx1)
                        s.advance = bar.advance
                    elif n in OPERATOR_SIGNS:
                        s = larger(m.shape(f"{n}.dnom", master, grown).moved(0, -bottom).scaled(k))
                        # bars as wide as the minus sign's, + square (as in the text, build/operators.py)
                        s = s.bars_to(bx0, bx1, (by0 + by1) / 2 if n == "plus" else None)
                    else:
                        s = m.shape(f"{n}.dnom", master, wf).moved(0, -bottom).scaled(k)
                    if n in SIGNS:
                        # where the text sign is in math: its case form (see build/operators.py)
                        _, y0, _, y1 = m.shape(case(m, n), master).bounds()
                        s = s.centred((y0 + y1) / 2 - (axis_drop(m, master) if case(m, n) != n else 0))
                    drawn.setdefault(f"{n}.{suffix}", []).append(s)
                print(f"  {suffix} figures, {master}: fraction figures at weight {wf} (stroke {stroke:.2f} of the text's)")

            if letters and tag == LETTER_FEATURE:
                # the text letters' weight whose stem, scaled to the size, is the target
                wl = min(m.weights, key=lambda x: abs(m.stem(x, o) * size - target))
                for n in letters:
                    s = m.shape(n, master, wl)
                    x0, _, x1, _ = s.bounds() if s.points else (0, 0, 0, 0)
                    lsb, rsb = max(x0, 0), max(s.advance - x1, 0)
                    spaced = s.moved((loosen - 1) * lsb, 0)
                    spaced.advance = s.advance + (loosen - 1) * (lsb + rsb)
                    drawn.setdefault(f"{n}.{suffix}", []).append(spaced)
                print(f"  {suffix} letters, {master}: text letters at weight {wl}, spaced {loosen:.2f}×")

        for name, shapes in drawn.items():
            new.append(m.glyph(name, shapes))
            source = name.rsplit(".", 1)[0]
            features[tag].append((bases.get(source, source), name))
        if letters and tag != LETTER_FEATURE:
            features[tag] += [(n, f"{n}.{SIZES[LETTER_FEATURE][0]}") for n in letters]
    return new, features
