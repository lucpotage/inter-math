"""
The miscellaneous symbols KaTeX sets from its AMS font (\\blacktriangle
\\blacktriangledown \\blacktriangleleft \\blacktriangleright \\lozenge
\\Diamond \\blacklozenge \\bigstar \\diagup \\diagdown \\backprime
\\maltese) and from Main (the suits \\spadesuit \\heartsuit \\diamondsuit
\\clubsuit, the music signs \\flat \\natural \\sharp), drawn from Inter's
shapes, with the minus sign's side bearings unless said:

- ▶ ◀: Inter's, as tall as ⊂ (TeX's are its ⊳ ⊲ filled, and Inter Math's
  ⊳ is Inter's ▷ that tall: build/binary_glyphs.py), centred on the axis;
- ▲ ▼: Inter's, SMALL_TRIANGLE times as tall as ⊂ (TeX's), on the
  baseline, ▼ in ▲'s box (as TeX's);
- ◊: Inter's, LOZENGE times the cap height tall (TeX's), at the weight that
  keeps its stroke, centred on the axis; ⧫: ◊'s outline filled, its ends
  pointed (as Inter's ◆ is ◇'s outer square), in ◊'s box;
- ★: Inter's, STAR times the cap height tall (TeX's), centred on the axis;
- ╱ ╲: a stroke as thick across as Inter's /, its ends cut level as the
  slash's, from the descender to the ascender (TeX's), as wide against its
  height as TeX's (DIAGONAL), with the slash's side bearings;
- ‵: Inter's ‵, as Inter Math's ′ is drawn from Inter's ′
  (build/symbol_glyphs.py: larger by the inverse of KaTeX's script size, on
  the baseline, as wide as the marks of Inter's ″ are apart);
- ✠: four of Inter's ▲ pointing at the centre (each crossing it so that the
  arms meet WAIST of the cross wide, TeX's), MALTESE times the cap height
  across (TeX's), centred on the capitals (as TeX's);
- the suits, all with ♡'s advance (TeX's share theirs), hanging from its
  top (TeX's do): ♡ is Inter's own; ♠: Inter's ♥ upside down in ♡'s box,
  on a foot of Inter's ▲ (its point up in the cleft between the lobes,
  where it is JOIN of the suit wide; its base FOOT of ♡'s height under it,
  TeX's); ♣: three circles of Inter's ●, laid out as TeX's lobes in ♡'s
  height (CLUB), joined by the triangle between their centres, on the same
  foot (circles as large as ♥'s lobes, in a trefoil, merge into a blob);
  ♢: Inter's ◇ narrowed to TeX's (SUIT_DIAMOND: as wide as ♡, it reads as
  ◇), its sides as thick across as ◇'s;
- ♭: Inter's superior b (its small b drawn for the size, heavier) on the
  baseline, its stem drawn up to FLAT times the cap height (TeX's);
- ♯ ♮: Inter's # turned into TeX's signs: upright strokes as thick across
  as #'s slanted ones, bars rising (SLOPE, TeX's) as thick across as its
  flat ones, as far apart as TeX's (BARS, of their height: SHARP and
  NATURAL times the cap height); the white between the upright strokes
  #'s between its own, by TeX's (SHARP_WHITE, NATURAL_WHITE: it shrinks
  with the weight as #'s does); ♯'s bars past its strokes OVERHANG of that
  white (TeX's), ♮'s between its strokes; centred on the axis (as TeX's),
  turned about their centre into themselves (♮'s left stroke from its lower
  bar up, its right one from the bottom up to its upper bar).
"""

import math

from geometry_glyphs import SOURCES as GEOMETRY_SOURCES, subsets
from operators import OFFSET, sign
from symbol_glyphs import SCRIPT
from variable import Masters, NewGlyph, Shape

SOURCES = [
    *GEOMETRY_SOURCES, "p", "triagup", "triagdn", "triagrt", "uni25C0", "lozenge", "uni2605", "slash", "primerev",
    "doubleprime", "uni2661", "heart", "circleblack", "diamondwhite", "b.sups", "numbersign",
]
# TeX's: ▲ against ⊂ (595 to 580); ◊, ★ and ✠ against the cap height (848, 805, 738 to 683)
SMALL_TRIANGLE = 595 / 580
LOZENGE = 848 / 683
STAR = 805 / 683
MALTESE = 738 / 683
# ✠: its arms' width where they meet, against the cross (TeX's: 23 of 738)
WAIST = 23 / 738
# ╱ ╲: their width against their height (TeX's: 860 to 888)
DIAGONAL = 860 / 888
# the suits (TeX's): ♢'s height against ♡'s (889 to 750) and its width against its height (668 to 889); ♣'s side
# lobes' radius, its top lobe's and how far apart the side ones are, against its body's height (195, 176, 332 of
# 748); the foot's base under the body (♠'s and ♣'s, 109 of ♡'s 750), and the foot as wide as the stem TeX sets the
# body on (42 of 668) where it meets the cleft
SUIT_DIAMOND = (889 / 750, 668 / 889)
CLUB = (195 / 748, 176 / 748, 332 / 748)
FOOT = 109 / 750
JOIN = 42 / 668
# the music signs (TeX's): ♭'s top against the cap height (750 to 683), ♯'s and ♮'s height (945, 953); their bars'
# rise (47 over 126) and pitch (431, of their height); the white between their upright strokes against #'s (126 and
# 180 to 189); how far ♯'s bars pass its strokes, a share of that white (36 of 126)
FLAT = 750 / 683
SHARP = 945 / 683
NATURAL = 953 / 683
SLOPE = 47 / 126
BARS = 431 / 945
SHARP_WHITE = 126 / 189
NATURAL_WHITE = 180 / 189
OVERHANG = 36 / 126
# the ones KaTeX sets from its AMS font (the rest from Main)
AMS = {0x25B2, 0x25BC, 0x25C0, 0x25B6, 0x25CA, 0x29EB, 0x2605, 0x2571, 0x2572, 0x2035, 0x2720}
# what each is drawn from (the workbench shows it): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x25B6: ("Inter's ▶, as tall as ⊂ (as ⊳ is ▷)", "triagrt"),
    0x25C0: ("Inter's ◀, as tall as ⊂ (as ⊲ is ◁)", "uni25C0"),
    0x25B2: ("Inter's ▲, as tall against ⊂ as TeX's, on the baseline", "triagup"),
    0x25BC: ("Inter's ▼, in ▲'s box", "triagdn"),
    0x25CA: ("Inter's ◊, larger, as heavy", "lozenge"),
    0x29EB: ("◊ filled, its ends pointed", "lozenge"),
    0x2605: ("Inter's ★, larger, on the axis", "uni2605"),
    0x2571: ("a stroke as thick as the slash, from the descender to the ascender", "slash"),
    0x2572: ("╱ mirrored", "slash"),
    0x2035: ("Inter's ‵ on the baseline, larger, as ′ is", "primerev doubleprime"),
    0x2720: ("four of Inter's ▲ pointing at the centre", "triagup"),
    0x2660: ("♥ upside down on a foot of ▲", "heart triagup"),
    0x2663: ("three of ●'s circles, as large as ♥'s lobes, on ♠'s foot", "circleblack heart triagup"),
    0x2662: ("◇ as wide as ♡, taller, as heavy", "diamondwhite uni2661"),
    0x266D: ("the superior b on the baseline, its stem drawn up", "b.sups"),
    0x266F: ("#'s strokes upright, its bars rising", "numbersign"),
    0x266E: ("♯'s strokes and bars, cut", "numbersign"),
}


def height(shape: Shape) -> float:
    _, y0, _, y1 = shape.bounds()
    return y1 - y0


def width(shape: Shape) -> float:
    x0, _, x1, _ = shape.bounds()
    return x1 - x0


def clockwise(points: list[tuple[float, float]]) -> Shape:
    """A polygon, clockwise (TrueType's outer contours)."""
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]))
    return Shape.polygon(points if area < 0 else points[::-1])


def stroke_across(m: Masters, master: dict, bottom: float, top: float, wide: float) -> Shape:
    """
    A stroke rising from x = 0 at `bottom` to `wide` across at `top`, as
    thick across as Inter's / at a master and cut level as it is.
    """
    slash = m.shape("slash", master)
    x0, y0, x1, y1 = slash.bounds()
    (r0, r1), = slash.runs((y0 + y1) / 2)
    run = r1 - r0
    thick = run / math.hypot(1, (x1 - x0 - run) / (y1 - y0))
    tall = top - bottom
    # its level ends as wide as a stroke `thick` across, leaning (wide - end) over its height
    end = thick
    for _ in range(20):
        end = thick * math.hypot(1, (wide - end) / tall)
    return clockwise([(0, bottom), (wide - end, top), (wide, top), (end, bottom)])


def diagonal(m: Masters, design: dict, master: dict) -> Shape:
    """╱ at a master: from the descender to the ascender, as thick across as Inter's / and cut level as it is."""
    slash = m.shape("slash", master)
    x0, _, x1, _ = slash.bounds()
    bottom = m.shape("p", design).bounds()[1]
    top = m.section("one", design["wght"], design["opsz"])[2]
    stroke = stroke_across(m, master, bottom, top, DIAGONAL * (top - bottom))
    return stroke.spaced((x0 + slash.advance - x1) / 2)


def maltese(m: Masters, master: dict, across: float) -> Shape:
    """✠ at a master, `across` wide and tall, centred on the origin: four of Inter's ▲ pointing at its centre."""
    tri = m.shape("triagup", master)
    tx0, ty0, tx1, ty1 = tri.bounds()
    half = (tx1 - tx0) / 2 / (ty1 - ty0)  # the tangent of half its point's angle
    # each arm crosses the centre by `past`, where it is WAIST of the cross wide
    past = WAIST * across / 2 / half
    arm = tri.scaled((across / 2 + past) / (ty1 - ty0))
    ax0, ay0, ax1, _ = arm.bounds()
    # the lower arm: its base at the bottom, its point past the centre
    arm = arm.moved(-(ax0 + ax1) / 2, -across / 2 - ay0)
    return Shape.join([arm.turned(a, (0, 0)) for a in (0, 90, 180, 270)], 0)


def suits(m: Masters, master: dict) -> dict[int, Shape]:
    """♠ ♣ ♢ at a master, with ♡'s advance (Inter's ♡ is kept as it is)."""
    shapes: dict[int, Shape] = {}
    white = m.shape("uni2661", master)
    hx0, hy0, hx1, hy1 = white.bounds()
    tall, middle = hy1 - hy0, (hx0 + hx1) / 2

    def placed(s: Shape) -> Shape:
        """Centred in ♡'s advance."""
        x0, _, x1, _ = s.bounds()
        out = s.moved(middle - (x0 + x1) / 2, 0)
        out.advance = white.advance
        return out

    # ♠: ♥ upside down (in its own box: ♡'s); the cleft between its lobes, now at the bottom
    heart = m.shape("heart", master)
    body = heart.rotated()
    bx0, by0, bx1, by1 = body.bounds()
    centre = (bx0 + bx1) / 2
    cleft = max((p for p, on in zip(body.points, body.on) if on and abs(p[0] - centre) < 0.05 * (bx1 - bx0) and p[1] < (by0 + by1) / 2), key=lambda p: p[1])
    # the foot: Inter's ▲, its base FOOT of ♡'s height under the body, its point up in the cleft, where it is JOIN of
    # the suit wide
    tri = m.shape("triagup", master)
    tx0, ty0, tx1, ty1 = tri.bounds()
    half = (tx1 - tx0) / 2 / (ty1 - ty0)
    base = by0 - FOOT * tall
    point = cleft[1] + JOIN * (bx1 - bx0) / 2 / half
    foot = tri.scaled((point - base) / (ty1 - ty0))
    fx0, fy0, fx1, _ = foot.bounds()
    foot = foot.moved(centre - (fx0 + fx1) / 2, base - fy0)
    shapes[0x2660] = placed(Shape.join([body, foot], 0))

    # ♣: three of ●'s circles and the triangle between their centres, laid out as TeX's in ♡'s height (CLUB), on ♠'s
    # foot
    side_r, top_r, apart = (k * tall for k in CLUB)
    disc = m.shape("circleblack", master)
    dx0, dy0, dx1, dy1 = disc.bounds()

    def lobe(x: float, y: float, r: float) -> Shape:
        return disc.moved(-(dx0 + dx1) / 2, -(dy0 + dy1) / 2).scaled(2 * r / (dx1 - dx0)).moved(x, y)

    low, high = hy0 + side_r, hy1 - top_r
    lobes = [lobe(centre, high, top_r), lobe(centre - apart / 2, low, side_r), lobe(centre + apart / 2, low, side_r)]
    # the side lobes meet over the foot's point
    assert low - math.sqrt(side_r**2 - (apart / 2) ** 2) < point, "♣'s foot misses its lobes"
    shapes[0x2663] = placed(Shape.join([*lobes, clockwise([(centre - apart / 2, low), (centre, high), (centre + apart / 2, low)]), foot], 0))

    # ♢: ◇ narrowed to TeX's (SUIT_DIAMOND: as tall against ♡, as wide against its height), hanging from ♡'s top; its
    # sides as thick across as ◇'s (the inner rhombus drawn in from the outer one by that much)
    diamond = m.shape("diamondwhite", master)
    outer, inner = sorted(diamond.contours(), key=width, reverse=True)
    stroke = (inner.bounds()[0] - outer.bounds()[0]) / math.sqrt(2)
    b = SUIT_DIAMOND[0] * tall / 2
    a = SUIT_DIAMOND[1] * b
    inward = 1 - stroke * math.hypot(a, b) / (a * b)
    cy = hy1 - b

    def rhombus(k: float, reverse: bool) -> Shape:
        pts = [(middle - a * k, cy), (middle, cy + b * k), (middle + a * k, cy), (middle, cy - b * k)]
        return Shape.polygon(pts[::-1] if reverse else pts)

    shapes[0x2662] = placed(Shape.join([rhombus(1, False), rhombus(inward, True)], 0))
    return shapes


def music(m: Masters, design: dict, axis: float) -> dict[int, Shape]:
    """♭ ♯ ♮ at a master (the letters' weight), their ink from x = 0."""
    shapes: dict[int, Shape] = {}
    cap = m.section("one", design["wght"], design["opsz"])[2]

    # ♭: the superior b, its stem's foot on the baseline, the stem drawn up
    sup = m.shape("b.sups", design)
    stem_x = sup.bounds()[0]
    foot = min(y for (x, y), on in zip(sup.points, sup.on) if on and abs(x - stem_x) < 0.5)
    sup = sup.moved(0, -foot)
    top = sup.bounds()[3]
    shapes[0x266D] = sup.map(lambda x, y: (x, FLAT * cap if abs(y - top) < 0.5 else y))

    # ♯ ♮: #'s strokes (its two slanted uprights, its two flat bars)
    hash_ = m.shape("numbersign", design)
    uprights = sorted((c for c in hash_.contours() if height(c) > width(c)), key=lambda c: c.bounds()[0])
    bars = [c for c in hash_.contours() if width(c) >= height(c)]
    u = uprights[0]
    ux0, uy0, ux1, uy1 = u.bounds()
    middle = (uy0 + uy1) / 2
    (r0, r1), = u.runs(middle)
    upright = (r1 - r0) / math.hypot(1, (ux1 - ux0 - (r1 - r0)) / (uy1 - uy0))
    bar = height(bars[0]) * math.hypot(1, SLOPE)  # its flat bars' thickness, across a rising one
    # the white between its uprights, at mid-height
    (_, a1), = uprights[0].runs(middle)
    (b0, _), = uprights[1].runs(middle)
    white = b0 - a1

    def sign_(tall: float, inner: float, overhang: float, natural: bool) -> Shape:
        """♯ (or ♮) centred on the origin: uprights `inner` apart, bars rising across them."""
        x = inner / 2 + upright  # the uprights' outer edges, at ±x
        pitch = BARS * tall
        reach = x + overhang

        def band(y: float) -> Shape:
            """A bar whose middle line rises through (0, y), cut upright at ±reach."""
            return clockwise([(-reach, y - SLOPE * reach - bar / 2), (-reach, y - SLOPE * reach + bar / 2),
                         (reach, y + SLOPE * reach + bar / 2), (reach, y + SLOPE * reach - bar / 2)])

        if natural:
            # the left upright from the lower bar's bottom (at its outer edge) up, the right one turned
            low = -pitch / 2 - SLOPE * x - bar / 2
            left = clockwise([(-x, low), (-x, tall / 2), (-x + upright, tall / 2), (-x + upright, low)])
        else:
            # both as long, the right one raised by the bars' rise
            rise = SLOPE * (inner + upright)
            left = clockwise([(-x, -tall / 2), (-x, tall / 2 - rise), (-x + upright, tall / 2 - rise), (-x + upright, -tall / 2)])
        right = left.map(lambda px, py: (-px, -py))
        return Shape.join([left, right, band(-pitch / 2), band(pitch / 2)], 0)

    sharp = sign_(SHARP * cap, SHARP_WHITE * white, OVERHANG * SHARP_WHITE * white, False)
    natural = sign_(NATURAL * cap, NATURAL_WHITE * white, 0, True)
    shapes[0x266F] = sharp.moved(0, axis)
    shapes[0x266E] = natural.moved(0, axis)
    return shapes


def misc_shapes(m: Masters, design: dict, master: dict) -> dict[int, Shape]:
    """The family at a master: code point → shape."""
    shapes: dict[int, Shape] = {}
    minus = sign(m, "minus", master)
    mx0, my0, mx1, my1 = minus.bounds()
    axis = (my0 + my1) / 2
    side = (mx0 + minus.advance - mx1) / 2
    cap = m.section("one", design["wght"], design["opsz"])[2]
    _, subset, _ = subsets(m, master)
    tall = height(subset)

    # ▶ ◀: as tall as ⊂, on the axis
    for cp, name in {0x25B6: "triagrt", 0x25C0: "uni25C0"}.items():
        tri = m.shape(name, master)
        shapes[cp] = tri.scaled(tall / height(tri)).centred(axis).spaced(side)

    # ▲ ▼: SMALL_TRIANGLE times as tall as ⊂, on the baseline, ▼ in ▲'s box
    up = m.shape("triagup", master)
    k = SMALL_TRIANGLE * tall / height(up)
    for cp, name in {0x25B2: "triagup", 0x25BC: "triagdn"}.items():
        tri = m.shape(name, master).scaled(k)
        shapes[cp] = tri.moved(0, -tri.bounds()[1]).spaced(side)

    # ◊ ⧫: Inter's ◊ larger, as heavy (its chevrons as wide across at mid-height as Inter's at the master), on the axis
    own = m.shape("lozenge", master)
    lozenge = m.fitted("lozenge", master, LOZENGE * cap / height(own), own.side()).centred(axis).spaced(side)
    shapes[0x25CA] = lozenge
    lx0, ly0, lx1, ly1 = lozenge.bounds()
    ends = sorted((p for p in lozenge.points if abs(p[0] - lx0) < 0.5), key=lambda p: p[1])
    shapes[0x29EB] = Shape.polygon([ends[0], ((lx0 + lx1) / 2, ly1), (lx1, ends[0][1]), ((lx0 + lx1) / 2, ly0)], lozenge.advance)

    # ★: larger, on the axis
    star = m.shape("uni2605", master)
    shapes[0x2605] = star.scaled(STAR * cap / height(star)).centred(axis).spaced(side)

    # ╱ ╲
    up_stroke = diagonal(m, design, master)
    shapes[0x2571] = up_stroke
    shapes[0x2572] = up_stroke.mirrored()

    # ‵: Inter's ‵ as KaTeX's superscript, as Inter Math's ′ (build/symbol_glyphs.py)
    k = 1 / SCRIPT
    mark = m.shape("primerev", design, m.heavier(design, k)).scaled(k)
    first, second = sorted(c.bounds()[0] for c in m.shape("doubleprime", design).contours())
    mark = mark.moved(0, -mark.bounds()[1])
    mark.advance = (second - first) * k
    shapes[0x2035] = mark

    # ✠: centred on the capitals
    shapes[0x2720] = maltese(m, master, MALTESE * cap).moved(0, cap / 2).spaced(side)

    shapes.update(suits(m, master))
    for cp, s in music(m, design, axis).items():
        shapes[cp] = s.spaced(side)
    return shapes


def misc_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, SOURCES)
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        for cp, s in misc_shapes(m, design, m.lighter(design, OFFSET)).items():
            shapes.setdefault(cp, []).append(s)
    taken = set(m.font.getGlyphOrder())
    return [m.glyph(f"uni{cp:04X}" + (".math" if f"uni{cp:04X}" in taken else ""), s, cp) for cp, s in shapes.items()]
