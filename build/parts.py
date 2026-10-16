"""
What each of Inter Math's glyphs is built on, and what is built on it: the
reference to read before drawing (build/parts.md: which part to start
from, what a change touches), written by build.py from the build's own
descriptions (each family's DRAWN_FROM: how a glyph is drawn, from which of
Inter's glyphs) and from the provenance it measures (which glyphs are still
Inter's). KaTeX's images Inter Math draws (SVG_FROM) are parts too, by their
first command, and so are the macros it sets one of its glyphs with (MACROS
in src/index.ts).

A glyph is built on the glyphs its description names, Inter Math's or Inter's:
⊈, "⊆ crossed by ≠'s slash", is built on ⊆ and Inter's ≠, ⊆ on ⊂ and ≤, ⊂ on
U. The first one named is the part it is mainly built on. The code shares
those parts, so a change to ⊂ reaches ⊆ and ⊈. Names are characters, letters
standing alone ("U in ⊂'s box", "Inter's U turned") and a few words for the
operators' parts (WORDS); "TeX's ⎰" compares, and so do asides in brackets,
"(as ⊲ is ◁)": those don't count.
"""

import re
import unicodedata
from pathlib import Path

# words that name a part of one of Inter Math's glyphs, or one of KaTeX's images it draws (by its first command)
WORDS = {"plus's": "+", "minus's": "−", "the middle dot": "⋅", "the underline": "\\underline", "the wide tilde": "\\widetilde",
         "the vector arrow": "\\vec"}
# ASCII signs that are glyphs when they stand alone in a description ("[ keeping its top arm", "='s gap"), not
# when they are text ("(TeX's", "(\\smallsetminus)", "and/or")
ASCII_GLYPHS = set("=<>+|[](){}#/\\~^*")
BEFORE = " ("
AFTER = " ',;:.)"
# letters standing alone that are words, not glyphs
NOT_LETTERS = {"a"}
# punctuation that is text in a description
TEXT = set("’‘“”–—…")
# a glyph named after these is another font's, compared with
COMPARED = ("TeX's ", "KaTeX's ", "STIX's ", "Computer Modern's ")
FONT_TITLES = {"Upright": "the upright font", "Italic": "the italic font", "AMS": "the AMS font", "Blackboard": "blackboard bold"}


def mentioned(how: str, own: str) -> list[str]:
    """The glyphs a description names, in order: not `own`, nor another font's, nor asides."""
    out: list[str] = []
    aside = 0
    for i, ch in enumerate(how):
        before, after = how[:i], how[i + 1:i + 2] or " "
        alone = (before[-1:] or " ") in BEFORE and after in AFTER
        if ch == "(" and not alone:
            aside += 1
            continue
        if ch == ")" and not alone and aside:
            aside -= 1
            continue
        if aside or before.endswith(COMPARED):
            continue
        word = next((w for w in WORDS if how.startswith(w, i) and (before[-1:] or " ") in BEFORE), None)
        if word:
            glyph = WORDS[word]
        elif ch.isascii():
            if not alone or not (ch in ASCII_GLYPHS or ch.isalpha() and ch not in NOT_LETTERS):
                continue
            glyph = ch
        else:
            kind = unicodedata.category(ch)[0]
            if ch in TEXT or kind not in "SPL" or kind == "L" and not alone:
                continue
            glyph = ch
        if glyph != own and glyph not in out:
            out.append(glyph)
    return out


def katex_commands(katex: Path) -> dict[int, str]:
    """KaTeX's commands for its private-use code points (U+E010: \\nleqslant), from its symbol table."""
    names: dict[int, str] = {}
    for hexa, name in re.findall(r'defineSymbol\([^)]*?"\\u(e[0-9a-f]{3})", "\\\\@?(\w+)"', (katex / "dist" / "katex.mjs").read_text()):
        names.setdefault(int(hexa, 16), "\\" + name)
    return names


def macros(index_ts: Path) -> list[tuple[str, str, str]]:
    """
    The macros Inter Math sets one of its glyphs with (MACROS in src/index.ts):
    (command, the glyph, KaTeX's own construction, as it lays it out).
    """
    out = []
    pattern = r'"\\\\(\w+)": \{\s*classic: "((?:[^"\\]|\\.)*)",\s*inter: "((?:[^"\\]|\\.)*)"'
    for name, classic, inter in re.findall(pattern, index_ts.read_text()):
        char = re.search(r"\\\\char`(\\u[0-9a-fA-F]{4}|.)", inter).group(1)
        char = chr(int(char[2:], 16)) if char.startswith("\\u") else char
        # \html@mathml{its layout}{its MathML}: the layout, its TeX unescaped
        layout = classic.replace("\\\\", "\\")
        if layout.startswith("\\html@mathml{"):
            depth, i = 0, len("\\html@mathml")
            for j, ch in enumerate(layout[i:], i):
                if layout[j - 1] != "\\":  # \{ and \} are braces set, not groups
                    depth += {"{": 1, "}": -1}.get(ch, 0)
                if depth == 0:
                    layout = layout[i + 1:j]
                    break
        out.append(("\\" + name, char, layout))
    return out


def fonts(roles: list[str]) -> str:
    """Inter Math's fonts, short: "Upright, Size1–4"."""
    sizes = [int(r.removeprefix("Size")) for r in roles if r.startswith("Size")]
    named = [r for r in roles if not r.startswith("Size")]
    runs: list[list[int]] = []
    for n in sizes:
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    return ", ".join(named + [f"Size{a}" if a == b else f"Size{a}–{b}" for a, b in runs])


def source(g: dict) -> str:
    return ("italic " if g.get("italic") else "") + g["text"] + (f" ({g['features']})" if g.get("features") else "")


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def command(how: str) -> str | None:
    """The TeX command a description ends on, as "(\\nshortmid)"."""
    if how.endswith(")") and "(\\" in how:
        name = how[how.rindex("(\\") + 1:-1]
        return name if " " not in name else None
    return None


class Row:
    """A glyph Inter Math draws, in one or more of its fonts (a delimiter's sizes, say): how, from what, on what."""

    def __init__(self, cp: int, entries: list[tuple[str, dict]], names: dict[int, str]):
        self.cp, self.char = cp, chr(cp)
        self.roles = [role for role, _ in entries]
        role, d = entries[0]
        how = d.get("how", "")
        if not how or how.startswith("KaTeX's size"):
            how = (f"Inter's alternate ({d['from'][0].get('features', '')})" if d["kind"] == "alternate"
                   else "Inter's, resized or drawn out" if d.get("kept") else "Inter's, reshaped")
        self.how = how
        # an AMS variant is built on Main's glyph at its code point ("∼, its wave heavier")
        self.ams = role == "AMS"
        self.on = mentioned(d.get("how", ""), "" if self.ams else self.char)
        self.sources = list(dict.fromkeys(source(g) for _, e in entries for g in e["from"]))
        own = [r for r, e in entries if e["kind"] == "alternate" or e.get("kept")]
        self.own = "✓" if len(own) == len(entries) else fonts(own) if own else ""
        # as a reader finds it: its character, or its TeX command where it is private-use or an AMS variant
        name = names.get(cp) or command(how)
        self.label = (f"`{name}`" if name else f"U+{cp:04X}") if 0xE000 <= cp <= 0xF8FF or self.ams else self.char


class ImageRow:
    """One of KaTeX's images (or lines) Inter Math draws, by the commands that use it: a part, named by the first."""

    def __init__(self, commands: list[str], how: str, sources: str):
        self.char, self.how, self.sources, self.ams = commands[0], how, sources, False
        self.label = " ".join(f"`{c}`" for c in commands)
        self.on = mentioned(how, commands[0])


def family_rows(drawn: dict, roles: tuple[str, ...], cps: set[int] | None, names: dict[int, str], placed: set) -> list[Row]:
    """A family's glyphs, one row per code point across `roles` (all of their glyphs when `cps` is None)."""
    found: dict[int, list[tuple[str, dict]]] = {}
    for role in roles:
        for key, d in drawn.get(role, {}).items():
            cp = int(key)
            if (cps is None or cp in cps) and (role, cp) not in placed:
                found.setdefault(cp, []).append((role, d))
    for cp, entries in found.items():
        placed.update((role, cp) for role, _ in entries)
    return [Row(cp, entries, names) for cp, entries in sorted(found.items())]


def tree(part: str, built_on: dict[str, list], path: tuple[str, ...], shown: set[str], lines: list[str], depth: int) -> None:
    """
    What is built on `part`, nested: each glyph's own tree under the part it is
    mainly built on; on a last line, the glyphs also built on it (once a tree).
    """
    rows = [row for row in built_on.get(part, []) if row.char not in path or row.ams]
    for row in rows:
        if row.on[0] == part:
            lines.append(f"{'  ' * depth}- {row.label}: {row.how}")
            shown.add(row.label)
            if not row.ams:
                tree(row.char, built_on, path + (row.char,), shown, lines, depth + 1)
    others = [row.label for row in rows if row.on[0] != part and row.label not in shown]
    shown.update(others)
    if others:
        lines.append(f"{'  ' * depth}- and, under the part each is mainly built on: {' '.join(others)}")


def reference(data: dict, families: list[tuple[str, str, tuple[str, ...], set[int] | None]], names: dict[int, str],
              macro_list: list[tuple[str, str, str]] = ()) -> str:
    """
    The reference, in Markdown: what is built on what (trees from the parts
    built on no other), Inter's glyphs most drawn from, then every glyph Inter
    Math draws, family by family, KaTeX's images Inter Math draws and those it
    doesn't yet, and the macros it sets its glyphs with.
    `families`: (title, module, fonts, code points: None for all of the fonts'),
    in order; a glyph goes to the first that has it, the rest under its font.
    `names`: TeX's commands for private-use code points (katex_commands).
    `macro_list`: (command, glyph, KaTeX's construction) (macros()).
    """
    drawn, coverage = data["drawn"], data["coverage"]
    known = {chr(cp) for cps in coverage.values() for cp in cps}
    placed: set[tuple[str, int]] = set()
    sections = [(f"{title} (`{module}`)", family_rows(drawn, roles, cps, names, placed)) for title, module, roles, cps in families]
    sections += [(f"Also in {FONT_TITLES.get(role, f'the {role} font')}", family_rows(drawn, (role,), None, names, placed)) for role in drawn]
    rows = [row for _, items in sections for row in items]
    # the trees: the math fonts' glyphs, and the AMS variants built on them (the italic and blackboard letters
    # are letters: they hold no parts)
    math = [row for row in rows if row.roles[0] not in ("Italic", "Blackboard")]
    # KaTeX's images, one part per description (the commands sharing it)
    grouped: dict[tuple[str, str], list[str]] = {}
    for cmd, d in data["svg"].items():
        grouped.setdefault((d["how"], ", ".join(source(g) for g in d["from"])), []).append(cmd)
    images = [ImageRow(cmds, how, sources) for (how, sources), cmds in grouped.items()]

    built_on: dict[str, list] = {}
    for row in [*math, *images]:
        for part in row.on:
            built_on.setdefault(part, []).append(row)
    drawn_from: dict[str, list[str]] = {}
    for row in rows:
        for s in row.sources:
            if row.label not in drawn_from.setdefault(s, []):
                drawn_from[s].append(row.label)

    # the trees' order: the parts with the most built on them (through the parts mainly built on them) first
    def reach(part: str, seen: set[str]) -> int:
        for row in built_on.get(part, []):
            if row.on[0] == part and row.char not in seen:
                seen.add(row.char)
                if not row.ams:
                    reach(row.char, seen)
        return len(seen)

    on_something = {row.char for row in [*math, *images] if row.on and not row.ams}
    roots = sorted((p for p in built_on if p not in on_something), key=lambda p: (-reach(p, set()), -len(built_on[p]), p))
    heads = {row.char: row for row in [*math, *images] if not row.ams}

    lines = [
        "# Inter Math's parts: what each glyph is built on",
        "",
        "GENERATED by `build/build.py` (`build/parts.py`) from each family's `DRAWN_FROM` and",
        "`src/provenance.ts`, at every `pnpm font:build`. Do not edit: change a description in",
        "`build/` and rebuild.",
        "",
        "- **Built on**: the glyphs a glyph's description names, Inter Math's or Inter's: the",
        "  parts it is built from, or the glyphs it takes a size from (\"as tall as ⊂\"). The first",
        "  is the part it is mainly built on. The code shares them: change one, and check what is",
        "  built on it.",
        "- **From Inter**: the Inter glyphs the build draws it from (`italic`: Inter's italic; a",
        "  feature in brackets: that alternate).",
        "- **Inter's**: ✓ when the glyph is still Inter's (an alternate, or only resized, moved,",
        "  turned or drawn out: `kept`, blue in the workbench), blank when it is drawn for Inter",
        "  Math, or the fonts where it is still Inter's. Inter's own glyphs, kept as they are,",
        "  aren't listed.",
        "- AMS variants (InterMath-AMS: the AMS designs at code points Main has) and private-use",
        "  glyphs go by their TeX command.",
        "",
        "## What is built on what",
        "",
        "One tree per part that is built on no other (Inter's glyphs), the parts with the most",
        "built on them first. A glyph's own tree is under the part it is mainly built on; the",
        "parts it is also built on list it on their last line. KaTeX's images Inter Math draws",
        "are parts too, by their commands (`\\overbrace` under {, ≀ under `\\widetilde`).",
        "",
    ]
    for root in roots:
        head = heads.get(root)
        what = head.how if head else "Inter's, as it is" if root in known else "Inter's (not in Inter Math)"
        lines.append(f"- **{cell(head.label if head else root)}**: {cell(what)}")
        sub: list[str] = []
        tree(root, built_on, (root,), set(), sub, 1)
        lines += [cell(s) for s in sub]

    lines += ["", "## Inter's glyphs most drawn from", "", "| Inter's | Inter Math's glyphs drawn from it |", "|---|---|"]
    for s, labels in sorted(drawn_from.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(labels) >= 3:
            lines.append(f"| {cell(s)} | {cell(' '.join(labels))} ({len(labels)}) |")

    lines += ["", "## Glyph by glyph", ""]
    for title, items in sections:
        if items:
            lines += [f"### {title}", "", "| Glyph | Code point | Fonts | Built on | From Inter | How | Inter's |", "|---|---|---|---|---|---|---|"]
            lines += [f"| {cell(r.label)} | U+{r.cp:04X} | {fonts(r.roles)} | {cell(' '.join(r.on))} | {cell(', '.join(r.sources))} | {cell(r.how)} | {r.own} |"
                      for r in items]
            lines.append("")

    lines += ["### KaTeX's images (`src/surd.ts`, `src/svg.ts`, data from `build.py`)", "",
              "| Commands | Built on | From Inter | How |", "|---|---|---|---|"]
    lines += [f"| {cell(image.label)} | {cell(' '.join(image.on))} | {cell(image.sources)} | {cell(image.how)} |" for image in images]
    still = data.get("svgKatex", [])
    if still:
        lines += ["", "Still KaTeX's (Computer Modern's images, at every weight: `SVG_KATEX`): "
                  + " ".join(f"`{c}`" for c in still) + ", and the CD environment's `@=`."]
    if macro_list:
        lines += ["", "### KaTeX's macros Inter Math sets one glyph with (`MACROS` in `src/index.ts`)", "",
                  "| Command | Inter Math's glyph | KaTeX's own (in its fonts) |", "|---|---|---|"]
        lines += [f"| `{name}` | {cell(char)} | `{cell(layout)}` |" for name, char, layout in macro_list]
    return "\n".join(lines).rstrip() + "\n"
