"""
The arrows Inter lacks, drawn from Inter Math's own (build/operators.py:
Inter's, as heavy as the letters, on the axis, their heads smaller and their
shafts drawn out).

- ↦ ⟼: → and ⟶ from a bar at the tail, as thick as their shaft and as tall
  as their head;
- ⇀ ⇁ ↼ ↽: → keeping one barb: the shaft's other edge runs on straight to the
  barb's outer edge, the new point; turned and mirrored for the others;
- ⇌: ⇀ over ↽, their shafts as far apart as ='s bars (and ⇒'s);
- ⇑ ⇓ ⇕: ⇒ and ⇔ turned upright (Inter's ↑ is its → turned), centred like
  Inter's ↑ and ↕ (↕ raised as its case forms are: build/operators.py);
- ↩ ↪: Inter's, their shaft on the axis as its → is, the hook drawn
  in to the head's height (Inter's rises above it, as a return key's): its
  stroke kept, its radii shortened alike.
"""

from operators import ARROW_HEAD, OFFSET, about_axis, arrow_growth, axis_drop, case_rise, drawn_out, even_bars, gap, scaled_weight, shaft_length, sign
from variable import Masters, NewGlyph, Shape

SOURCES = [
    "arrowright", "arrowleft", "arrowboth", "uni27F5", "uni27F6", "uni27F7", "arrowdblright", "arrowdblboth", "arrowup",
    "arrowupdn", "uni21AA", "minus", "equal", "one",
]
# what each is drawn from (the workbench shows it, /dev/symbols): code point → (how, Inter's glyphs)
DRAWN_FROM = {
    0x21A6: ("→ from a bar", "arrowright"),
    0x27FC: ("⟶ from a bar", "uni27F6"),
    0x21C0: ("→ keeping its upper barb", "arrowright"),
    0x21C1: ("→ keeping its lower barb", "arrowright"),
    0x21BC: ("← keeping its upper barb", "arrowright"),
    0x21BD: ("← keeping its lower barb", "arrowright"),
    0x21CC: ("⇀ over ↽", "arrowright"),
    0x21D1: ("⇒ turned upright", "arrowdblright"),
    0x21D3: ("⇒ turned down", "arrowdblright"),
    0x21D5: ("⇔ drawn in to ↕'s height, turned upright", "arrowdblboth"),
    0x21AA: ("its hook drawn in to the head's height", "uni21AA"),
    0x21A9: ("↪ mirrored", "uni21AA"),
}


def flipped(shape: Shape, y: float) -> Shape:
    """Upside down about height y (contours reversed: a flip turns their direction)."""
    out = []
    for c in shape.contours():
        pts = [(px, 2 * y - py) for px, py in reversed(c.points)]
        out.append(Shape(pts, list(reversed(c.on)), c.ends, shape.advance))
    return Shape.join(out, shape.advance)


def reversed_in_place(shape: Shape) -> Shape:
    """
    An arrow pointing the other way over the same ink (mirrored about its ink's middle): mirrored within its advance,
    the side bearings swap, and a pair's two arrows no longer end together (⇌'s lower harpoon sat 0.06 em to the left).
    """
    x0, _, x1, _ = shape.bounds()
    out = shape.mirrored()
    mx0, _, _, _ = out.bounds()
    return out.moved(x0 - mx0, 0)


def turned_up(shape: Shape, centre: tuple[float, float]) -> Shape:
    """A quarter turn anticlockwise (a right-pointing arrow then points up), its ink centred on `centre`."""
    x0, y0, x1, y1 = shape.bounds()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return shape.map(lambda x, y: (centre[0] - (y - cy), centre[1] + (x - cx)))


def harpoon(arrow: Shape) -> Shape:
    """A right-pointing arrow (one contour) keeping its upper barb."""
    pts, on = list(arrow.points), list(arrow.on)
    left = min(x for x, _ in pts)
    tails = sorted((i for i, (x, _) in enumerate(pts) if abs(x - left) < 0.5), key=lambda i: pts[i][1])
    bottom, top = tails[0], tails[-1]
    n = len(pts)
    if abs(pts[(top + 1) % n][1] - pts[top][1]) > 0.5:  # walk from the tail's top along the shaft's top edge
        pts, on = pts[::-1], on[::-1]
        return harpoon(Shape(pts, on, [n - 1], arrow.advance))
    tip = max(range(n), key=lambda i: pts[i][0])
    path = [(top + k) % n for k in range((tip - top) % n)]  # top of the tail … the upper barb's outer end
    barb = pts[path[-1]]
    shaft = pts[bottom][1]
    # the barb's outer edge, from its end to the tip, meets the shaft's lower edge
    tx, ty = pts[tip]
    point = (barb[0] + (tx - barb[0]) * (barb[1] - shaft) / (barb[1] - ty), shaft)
    ring = [pts[bottom], *(pts[i] for i in path), point]
    flags = [True, *(on[i] for i in path), True]
    return Shape(ring, flags, [len(ring) - 1], arrow.advance)


def hooked(arrow: Shape) -> Shape:
    """
    Inter's ↪ (its hook a half ring at the tail, rising from the shaft) with
    the hook's top down to the head's: both radii of the ring shortened by as
    much, the shaft, the head and the hook's end kept.
    """
    pts = arrow.points
    top = max(y for _, y in pts)
    # the ring's centre is over the shaft's end, where the hook's top starts; the hook ends a little further
    x_join = min(x for (x, y), on in zip(pts, arrow.on) if on and abs(y - top) < 0.5)
    x_end = max(x for x, y in pts if abs(y - top) < 0.5)
    bottom = min(y for x, y in pts if abs(x - x_join) < 0.5)
    centre = (top + bottom) / 2
    inner_top = min(y for x, y in pts if x_join + 0.5 < x < x_end + 0.5 and y > centre)
    head = max(y for x, y in pts if x > x_end + 0.5)
    outer, inner = top - centre, inner_top - centre
    cut = (top - head) / 2
    k_outer, k_inner = (outer - cut) / outer, (inner - cut) / inner

    def moved(x: float, y: float) -> tuple[float, float]:
        if x > x_join + 0.5:
            if x > x_end + 0.5 or y < centre:
                return (x, y)  # the shaft and the head
            # the hook's end: its outer and inner edges
            return (x, centre - cut + (y - centre) * (k_outer if y > (top + inner_top) / 2 else k_inner))
        dx, dy = x - x_join, y - centre
        k = k_outer if (dx * dx + dy * dy) ** 0.5 > (outer + inner) / 2 else k_inner
        return (x_join + dx * k, centre - cut + dy * k)

    return arrow.map(moved)


def arrow_glyphs(path) -> list[NewGlyph]:
    m = Masters(path, [n for name in SOURCES for n in (name, f"{name}.case")])
    shapes: dict[int, list[Shape]] = {}
    for design in m.masters:
        master = m.lighter(design, OFFSET)
        right = even_bars(m, "arrowright", master)
        long = even_bars(m, "uni27F6", master)
        x0, y0, _, y1 = right.bounds()
        # the shaft's edges, at the tail
        tail = [y for x, y in right.points if abs(x - x0) < 0.5]
        s0, s1 = min(tail), max(tail)

        # ↦ ⟼: a bar at the tail, as thick as the shaft, as tall as the head
        bar = Shape.polygon([(x0, y0), (x0, y1), (x0 + (s1 - s0), y1), (x0 + (s1 - s0), y0)])
        mapsto, longmapsto = right + bar, long + bar

        # harpoons
        up_right = harpoon(right)
        centre = (s0 + s1) / 2
        down_right = flipped(up_right, centre)
        up_left, down_left = up_right.mirrored(), down_right.mirrored()

        # ⇌: ⇀ over ↽, their shafts as far apart as ='s bars (and ⇒'s), both over the same ink (their ends together)
        double = even_bars(m, "arrowdblright", master)
        pitch = gap(m, master) + (s1 - s0)
        harpoons = Shape.join([up_right.moved(0, pitch / 2), reversed_in_place(down_right).moved(0, -pitch / 2)], right.advance)

        # ⇑ ⇓ ⇕: ⇒ and ⇔ turned upright, centred like ↑ and ↕
        up, updown = even_bars(m, "arrowup", master), even_bars(m, "arrowupdn", master)

        def upright(shape: Shape, like: Shape) -> Shape:
            lx0, ly0, lx1, ly1 = like.bounds()
            out = turned_up(shape, ((lx0 + lx1) / 2, (ly0 + ly1) / 2))
            out.advance = like.advance
            return out

        dbl_up = upright(double, up)
        dbl_down = flipped(dbl_up, (up.bounds()[1] + up.bounds()[3]) / 2)
        # ⇕: ⇔ drawn in to ↕'s height before it is turned (Inter's ⇔ is much longer than its ↕; TeX's ⇕ is as tall as
        # ↕); past Regular drawn longer again to keep the shaft it has at Regular between its heads, longer than ↕'s
        def drawn_to_updown(location: dict) -> Shape:
            both = even_bars(m, "arrowdblboth", location)
            bx0, _, bx1, _ = both.bounds()
            _, uy0, _, uy1 = even_bars(m, "arrowupdn", location).bounds()
            return drawn_out(both, (1, 0), (uy1 - uy0) - (bx1 - bx0), True)

        dbl = drawn_to_updown(master)
        regular = m.axes["wght"].defaultValue
        if master["wght"] > regular:
            short = shaft_length(drawn_to_updown({**master, "wght": regular}), (1, 0)) - shaft_length(dbl, (1, 0))
            if short > 0:
                dbl = drawn_out(dbl, (1, 0), short, True)
        dbl_updown = upright(dbl, updown)

        # ↪ ↩: the hook down to the head's top, the shaft on the axis
        inter_hook = m.shape("uni21AA", master)
        hx0, _, hx1, _ = inter_hook.bounds()
        rise = case_rise(m, master)
        drawn = hooked(m.shape("uni21AA", master, scaled_weight(m, master, ARROW_HEAD))).moved(0, rise)
        hook = about_axis(m, master, drawn, hooked(inter_hook).moved(0, rise), ARROW_HEAD).moved(0, -axis_drop(m, master))
        # its shaft drawn out as →'s is, between the hook's end and the head
        hx0_, _, hx1_, top = hook.bounds()
        # the hook's end: at its top (as high as the head), in the hook's half
        hook_end = max(x for x, y in hook.points if y > top - 1 and x < (hx0_ + hx1_) / 2)
        hook = drawn_out(hook, (1, 0), arrow_growth(m, "arrowright", master, sign(m, "arrowright", master)), cut=hook_end + 1)
        hook = hook.spaced((hx0 + inter_hook.advance - hx1) / 2)

        for cp, s in {
            0x21A6: mapsto, 0x27FC: longmapsto,
            0x21C0: up_right, 0x21C1: down_right, 0x21BC: up_left, 0x21BD: down_left, 0x21CC: harpoons,
            0x21D1: dbl_up, 0x21D3: dbl_down, 0x21D5: dbl_updown,
            0x21AA: hook, 0x21A9: hook.mirrored(),
        }.items():
            shapes.setdefault(cp, []).append(s)
    # named apart from Inter's own glyphs (↩ ↪ replace Inter's)
    taken = set(m.font.getGlyphOrder())
    names = {cp: f"uni{cp:04X}" + (".math" if f"uni{cp:04X}" in taken else "") for cp in shapes}
    return [m.glyph(names[cp], s, cp) for cp, s in shapes.items()]
