"""
The letter-like symbols KaTeX sets from its AMS font (\\varkappa \\digamma
\\Game \\mho \\circledR \\circledS; \\Finv \\eth \\yen are Inter's own, KEPT),
drawn from Inter's letters, at the letters' weight. (\\imath \\jmath are
Inter's italic ı ȷ, mapped to the code points KaTeX uses: build.py.)

- ϰ ϝ: Inter's italic ϰ ϝ: TeX's are italic, as its math letters (they go in
  the upright font, as ℏ does: build/symbol_glyphs.py);
- ⅁: Inter's G mirrored, its bar at the lower left and its opening at the
  top left, as KaTeX's (TeX's \\Game; a half turn put the bar up, upside
  down from TeX's);
- ℧: Inter's Ω given a half turn in its advance, the flat side on the cap
  height and the round one overshooting the baseline;
- ® Ⓢ: drawn as Inter draws its Ⓡ Ⓢ (its ® is a small mark, raised): its
  ◯, as heavy as Inter draws it in text, around R or S, as large as TeX's (the
  circle CIRCLED times the cap height across, the letter LETTER of it tall),
  centred on the math axis; the letter as heavy as the ring, as in the
  circled operators (Inter's letters are heavier at Black: at their stroke,
  drawn smaller, the letter would fill the ring).

Fraktur ℜ ℑ, Weierstrass's ℘ and the Hebrew ℵ ℶ ℷ ℸ stay KaTeX's: Inter has
no letters of those scripts to draw them from.
"""

from operators import math_axis
from variable import Masters, NewGlyph, Shape

# the circled letters' circle against the cap height, their letter against the circle (TeX's ® Ⓢ: 884 to 683, 542 to 884)
CIRCLED = 884 / 683
LETTER = 542 / 884
# Inter's own, as it draws them (AMS symbols the build keeps from Inter: build.py)
KEPT = {0x2132, 0x00F0, 0x00A5}
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x03F0: ("Inter's italic ϰ", "italic:kappa1"),
    0x03DD: ("Inter's italic ϝ", "italic:uni03DD"),
    0x2141: ("G mirrored, as TeX's", "G"),
    0x2127: ("Ω turned", "uni03A9"),
    0x00AE: ("◯ around R, as Inter's Ⓡ, as large as TeX's ®", "uni25EF R"),
    0x24C8: ("◯ around S, as Inter's Ⓢ, as large as TeX's", "uni25EF S"),
}


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def circled(m: Masters, design: dict, letter: str, cap: float, axis: float) -> Shape:
    """
    A circled capital at a master: ◯ CIRCLED times the cap height across, as
    heavy as Inter draws it at the text optical size (its display ◯ is
    heavier, as for the circled operators), the letter LETTER of it tall and
    as heavy, centred in it on the axis.
    """
    stroke = m.shape("uni25EF", {**design, "opsz": m.axes["opsz"].defaultValue}).side()
    ring = m.fitted("uni25EF", design, CIRCLED * cap / height(m.shape("uni25EF", design)), stroke).centred(axis)
    k = LETTER * height(ring) / height(m.shape(letter, design))
    inside = m.shape(letter, design, m.weight_for(lambda w: m.stem(w, design["opsz"]) * k, stroke)).scaled(k)
    rx0, ry0, rx1, ry1 = ring.bounds()
    ix0, iy0, ix1, iy1 = inside.bounds()
    return Shape.join([ring, inside.moved((rx0 + rx1 - ix0 - ix1) / 2, (ry0 + ry1 - iy0 - iy1) / 2)], ring.advance)


def turned(shape: Shape, cap: float) -> Shape:
    """A half turn in the advance, about half the cap height (a flat side on the baseline goes to the cap height)."""
    return shape.map(lambda x, y: (shape.advance - x, cap - y))


def letter_glyphs(path, italic_path) -> list[NewGlyph]:
    m = Masters(path, ["G", "uni03A9", "H", "uni25EF", "R", "S", "minus", "minus.case", "one"])
    mi = Masters(italic_path, ["kappa1", "uni03DD", "one"])
    shapes: dict[int, list[Shape]] = {}
    for design, italic in zip(m.masters, mi.masters):
        cap = m.shape("H", design).bounds()[3]
        axis = math_axis(m, design)
        drawn = {
            0x03F0: mi.shape("kappa1", italic),
            0x03DD: mi.shape("uni03DD", italic),
            0x2141: m.shape("G", design).mirrored(),
            0x2127: turned(m.shape("uni03A9", design), cap),
        }
        drawn[0x00AE] = circled(m, design, "R", cap, axis)
        drawn[0x24C8] = circled(m, design, "S", cap, axis)
        for cp, s in drawn.items():
            shapes.setdefault(cp, []).append(s)
    return [m.glyph(f"uni{cp:04X}.math", s, cp) for cp, s in shapes.items()]
