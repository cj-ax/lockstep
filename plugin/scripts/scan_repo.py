"""Stack discovery for lockstep:learn: read a front-end repository and describe its stack.

Reads files only. It never runs, builds or installs anything, and it skips node_modules,
build output and dot-folders. It writes two files:

  stack.json  what was found, where, and how sure the scan is
  STACK.md    a draft for a person to correct and confirm, ending with the questions only
              a person can answer

With no repository (--no-repo), it writes ARCHITECT-QUESTIONS.md instead: plain-words
questions for whoever knows the stack, with what the Figma side suggests as --hint lines.

Usage:
  python3 scan_repo.py <repo path> --out <folder>
  python3 scan_repo.py --no-repo --name <org or product> --out <folder> [--hint "..."]...
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

SKIP_DIRS = {"node_modules", "dist", "build", "out", "coverage", "vendor", "public", "storybook-static", ".next", ".nuxt", ".svelte-kit", ".output"}
MAX_FILE_BYTES = 400_000
MAX_FILES = 20_000
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}
STYLE_EXT = {".css", ".scss", ".sass", ".less", ".pcss"}

FRAMEWORKS = {
    "react": "React", "vue": "Vue", "@angular/core": "Angular", "svelte": "Svelte", "solid-js": "Solid",
    "lit": "Web Components (Lit)", "@stencil/core": "Web Components (Stencil)", "preact": "Preact",
    "next": "Next.js", "nuxt": "Nuxt", "@sveltejs/kit": "SvelteKit", "@remix-run/react": "Remix", "astro": "Astro",
}
UI_LIBRARIES = {
    "@mui/material": "MUI", "@material-ui/core": "MUI (v4)", "vuetify": "Vuetify", "@chakra-ui/react": "Chakra UI",
    "antd": "Ant Design", "ant-design-vue": "Ant Design Vue", "@mantine/core": "Mantine", "bootstrap": "Bootstrap",
    "react-bootstrap": "React Bootstrap", "@headlessui/react": "Headless UI", "@headlessui/vue": "Headless UI",
    "primevue": "PrimeVue", "primereact": "PrimeReact", "quasar": "Quasar", "element-plus": "Element Plus",
    "@angular/material": "Angular Material", "@carbon/react": "Carbon", "@fluentui/react-components": "Fluent UI",
}
RADIX = re.compile(r"^@radix-ui/react-")
STYLING = {
    "tailwindcss": "Tailwind CSS", "styled-components": "styled-components", "@emotion/react": "Emotion",
    "@emotion/styled": "Emotion", "@vanilla-extract/css": "Vanilla Extract", "sass": "Sass", "less": "Less",
    "@stitches/react": "Stitches", "@pandacss/dev": "Panda CSS", "style-dictionary": "Style Dictionary",
    "@tokens-studio/sd-transforms": "Tokens Studio",
}
BUILD_TOOLS = {"vite": "Vite", "webpack": "webpack", "parcel": "Parcel", "esbuild": "esbuild", "@angular/cli": "Angular CLI", "react-scripts": "Create React App", "rollup": "Rollup"}
THEME_CALLS = re.compile(r"\b(createTheme|extendTheme|createVuetify|createSystem|defineConfig|createStitches|createGlobalTheme|createThemeContract|MantineProvider|ThemeProvider)\s*[(<]")


def walk(root):
    count = 0
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir())
        except OSError:
            continue
        for p in entries:
            if p.is_dir():
                if p.name not in SKIP_DIRS and not (p.name.startswith(".") and p.name != ".storybook"):
                    stack.append(p)
            elif p.is_file():
                count += 1
                if count > MAX_FILES:
                    return
                yield p


def read(p):
    try:
        if p.stat().st_size > MAX_FILE_BYTES:
            return ""
        return p.read_text(errors="replace")
    except OSError:
        return ""


def matching(text, start, open_ch="{", close_ch="}"):
    """Index just past the bracket that closes the one at text[start]."""
    depth = 0
    i = start
    quote = None
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = None
        elif c in "'\"`":
            quote = c
        elif text.startswith("//", i):
            nl = text.find("\n", i)
            i = len(text) if nl < 0 else nl
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = len(text) if end < 0 else end + 2
            continue
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def strip_comments(s):
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", s, flags=re.S)


def split_top(body, seps=";,\n"):
    """Split a type or object literal body at top-level separators."""
    parts, depth, cur, quote = [], 0, "", None
    for c in body:
        if quote:
            cur += c
            if c == quote:
                quote = None
            continue
        if c in "'\"`":
            quote = c
        elif c in "{[(<":
            depth += 1
        elif c in "}])>":
            depth -= 1
        if depth == 0 and c in seps:
            if cur.strip():
                parts.append(cur.strip())
            cur = ""
        else:
            cur += c
    if cur.strip():
        parts.append(cur.strip())
    return parts


def type_members(body):
    """Props from a TS type literal body: [{name, type, optional}]."""
    props = []
    for part in split_top(strip_comments(body), ";\n,"):
        m = re.match(r"(?:readonly\s+)?['\"]?([A-Za-z_$][\w$-]*)['\"]?(\?)?\s*:\s*(.+)$", part, re.S)
        if m:
            props.append({"name": m.group(1), "type": " ".join(m.group(3).split()), "optional": bool(m.group(2))})
    return props


def object_members(body):
    """Props from a runtime declaration: defineProps({ a: String, b: { type: Number, default: 1 } }) or propTypes."""
    props = []
    for part in split_top(strip_comments(body), ",\n"):
        m = re.match(r"['\"]?([A-Za-z_$][\w$-]*)['\"]?\s*:\s*(.+)$", part, re.S)
        if not m:
            continue
        val = " ".join(m.group(2).split())
        t = re.search(r"type\s*:\s*([\w.\[\], ]+)", val)
        props.append({"name": m.group(1), "type": (t.group(1) if t else val).strip(" ,"), "optional": "required: true" not in val and ".isRequired" not in val})
    return props


def defaults_of(text, start):
    """withDefaults(defineProps<...>(), { a: 'x' }) -> {a: "'x'"}."""
    m = re.compile(r"\)\s*,\s*\{").search(text, start)
    if not m or m.start() - start > 4000:
        return {}
    b = m.end() - 1
    out = {}
    for part in split_top(strip_comments(text[b + 1:matching(text, b) - 1]), ",\n"):
        kv = re.match(r"['\"]?([\w$-]+)['\"]?\s*:\s*(.+)$", part, re.S)
        if kv:
            out[kv.group(1)] = " ".join(kv.group(2).split())[:60]
    return out


class Repo:
    def __init__(self, root):
        self.root = root
        self.files = list(walk(root))
        self._types = None

    def rel(self, p):
        return str(p.relative_to(self.root))

    def type_index(self):
        """name -> body or union string, from every `interface X {}` and `type X = ...` in the repo."""
        if self._types is None:
            self._types = {}
            for p in self.files:
                if p.suffix not in {".ts", ".tsx", ".vue", ".d.ts"}:
                    continue
                text = read(p)
                for m in re.finditer(r"\binterface\s+(\w+)(?:<[^>]*>)?(?:\s+extends\s+[^{]+)?\s*\{", text):
                    b = m.end() - 1
                    self._types.setdefault(m.group(1), ("object", text[b + 1:matching(text, b) - 1]))
                for m in re.finditer(r"\btype\s+(\w+)(?:<[^>]*>)?\s*=\s*", text):
                    rest = text[m.end():]
                    if rest.startswith("{"):
                        self._types.setdefault(m.group(1), ("object", rest[1:matching(rest, 0) - 1]))
                    else:
                        end = re.search(r";|\n\s*\n|\n(?=\s*(export|type|interface|const|function|import)\b)", rest)
                        self._types.setdefault(m.group(1), ("alias", " ".join(strip_comments(rest[:end.start() if end else 200]).split())))
        return self._types

    def enum_values(self, type_str):
        """'a' | 'b' literals, following one level of alias."""
        lits = re.findall(r"""^\s*['"]([^'"]+)['"]\s*$""", type_str.replace("|", "\n"), re.M)
        if lits and len(lits) == len([x for x in type_str.split("|") if x.strip()]):
            return lits
        name = type_str.strip()
        kind_body = self.type_index().get(name)
        if kind_body and kind_body[0] == "alias":
            return self.enum_values(kind_body[1]) if kind_body[1] != type_str else None
        return None

    def resolve_props(self, type_ref):
        kind_body = self.type_index().get(type_ref.strip())
        return type_members(kind_body[1]) if kind_body and kind_body[0] == "object" else None


def is_test(p):
    return bool({"__tests__", "test", "tests", "e2e", "__mocks__"} & set(p.parts)) or bool(re.search(r"\.(test|spec)\.|(^|/)setup(Tests)?\.[jt]s$", p.name))


def scan_packages(repo):
    pkgs = []
    for p in repo.files:
        if p.name == "package.json":
            try:
                data = json.loads(read(p) or "{}")
            except ValueError:
                continue
            pkgs.append((p, data))
    return pkgs


def deps_of(data):
    out = {}
    for field in ("dependencies", "devDependencies", "peerDependencies"):
        for k, v in (data.get(field) or {}).items():
            out.setdefault(k, (v, field))
    return out


def detect_stack(repo, pkgs):
    found = {"frameworks": [], "uiLibraries": [], "styling": [], "buildTools": []}
    seen = set()
    for p, data in pkgs:
        for dep, (ver, field) in deps_of(data).items():
            for table, key in ((FRAMEWORKS, "frameworks"), (UI_LIBRARIES, "uiLibraries"), (STYLING, "styling"), (BUILD_TOOLS, "buildTools")):
                name = table.get(dep)
                if name is None and key == "uiLibraries" and RADIX.match(dep):
                    name = "Radix UI"
                if name and (key, name) not in seen:
                    seen.add((key, name))
                    found[key].append({"name": name, "package": dep, "version": ver, "declaredIn": f"{repo.rel(p)} ({field})"})
    if (repo.root / "components.json").exists() and "shadcn" in read(repo.root / "components.json") + json.dumps([d for _, d in pkgs]):
        found["uiLibraries"].append({"name": "shadcn/ui", "package": None, "version": None, "declaredIn": "components.json"})
    elif (repo.root / "components.json").exists():
        found["uiLibraries"].append({"name": "shadcn/ui (probably)", "package": None, "version": None, "declaredIn": "components.json"})
    else:
        ui = [p for p in repo.files if p.parent.name == "ui" and p.suffix == ".tsx" and "cva(" in read(p)]
        if ui and any("class-variance-authority" in deps_of(d) for _, d in pkgs) or len(ui) >= 3:
            found["uiLibraries"].append({"name": "shadcn/ui (probably: copied in, no components.json)", "package": None, "version": None,
                                         "declaredIn": f"{len(ui)} cva components in {repo.rel(ui[0].parent)}"})
    locks = [n for n in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock") if (repo.root / n).exists()]
    found["packageManager"] = {"package-lock.json": "npm", "yarn.lock": "yarn", "pnpm-lock.yaml": "pnpm"}.get(locks[0], "bun") if locks else None
    return found


def detect_tokens(repo):
    sources = []
    for p in repo.files:
        ext = p.suffix
        if is_test(p):
            continue
        if ext in STYLE_EXT or ext in {".vue", ".svelte"}:
            text = read(p)
            props = re.findall(r"(?m)^\s*(--[\w-]+)\s*:\s*([^;]+);", text)
            if props:
                selectors = sorted(set(re.findall(r"(?m)^\s*([.:#\w\[\]=\"'-][^{\n]*?)\s*\{", text)))
                themed = [s for s in selectors if re.search(r"theme|dark|light|\[data-(mode|color-scheme)", s, re.I)]
                prefixes = {}
                for name, _ in props:
                    pre = re.match(r"--([a-z0-9]+)-", name)
                    if pre:
                        prefixes[pre.group(1)] = prefixes.get(pre.group(1), 0) + 1
                sources.append({"kind": "css-custom-properties", "file": repo.rel(p), "count": len(props), "unique": len({n for n, _ in props}),
                                "prefixes": dict(sorted(prefixes.items(), key=lambda kv: -kv[1])[:5]), "themeSelectors": themed[:8],
                                "sample": [f"{n}: {v.strip()}" for n, v in props[:6]]})
            if ext in {".scss", ".sass", ".less"}:
                var = r"(?m)^\s*\$([\w-]+)\s*:\s*([^;]+);" if ext != ".less" else r"(?m)^\s*@([\w-]+)\s*:\s*([^;]+);"
                svars = re.findall(var, text)
                maps = re.findall(r"(?m)^\s*\$([\w-]+)\s*:\s*\(", text)
                if svars or maps:
                    sources.append({"kind": "scss-variables" if ext != ".less" else "less-variables", "file": repo.rel(p), "count": len(svars),
                                    "maps": maps[:10], "sample": [f"${n}: {v.strip()}" for n, v in svars[:6]]})
        if re.match(r"tailwind\.config\.(js|cjs|mjs|ts)$", p.name):
            text = read(p)
            keys = re.findall(r"\b(colors|spacing|fontFamily|fontSize|borderRadius|boxShadow|screens)\s*:", text)
            sources.append({"kind": "tailwind-config", "file": repo.rel(p), "extends": "extend" in text, "sections": sorted(set(keys))})
        if ext in {".css"} and "@theme" in (text := read(p)):
            sources.append({"kind": "tailwind-v4-theme", "file": repo.rel(p), "count": len(re.findall(r"(?m)^\s*--[\w-]+\s*:", text))})
        if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs"}:
            text = read(p)
            calls = sorted(set(THEME_CALLS.findall(text)) - {"defineConfig"})
            typed = re.findall(r":\s*ThemeDefinition\s*=", text)
            if calls or typed:
                colors = len(re.findall(r"#[0-9a-fA-F]{3,8}\b", text))
                if colors or typed:
                    sources.append({"kind": "theme-object", "file": repo.rel(p), "calls": calls, "themes": re.findall(r"const\s+(\w+)\s*:\s*ThemeDefinition", text), "hexValues": colors})
        if ext == ".json" and p.name != "package.json" and "lock" not in p.name and not p.name.startswith("tsconfig"):
            text = read(p)
            if '"$value"' in text:
                sources.append({"kind": "dtcg-json", "file": repo.rel(p), "count": text.count('"$value"')})
            elif re.search(r'"value"\s*:', text) and re.search(r"token|theme|color|design", str(p), re.I):
                sources.append({"kind": "style-dictionary-json (probably)", "file": repo.rel(p), "count": len(re.findall(r'"value"\s*:', text))})
    return sources


def vue_props(repo, text):
    m = re.search(r"defineProps\s*(<)?", text)
    if not m:
        return None, "none"
    if m.group(1):
        g = m.end() - 1
        inner = text[g + 1:matching(text, g, "<", ">") - 1].strip()
        props = type_members(inner[1:-1]) if inner.startswith("{") else repo.resolve_props(inner)
        how = "defineProps<{...}>" if inner.startswith("{") else f"defineProps<{inner}>"
    else:
        b = text.find("(", m.start())
        arg = text[b + 1:matching(text, b, "(", ")") - 1].strip()
        if arg.startswith("["):
            props = [{"name": n, "type": None, "optional": True} for n in re.findall(r"['\"]([\w-]+)['\"]", arg)]
        elif arg.startswith("{"):
            props = object_members(arg[1:-1])
        else:
            props = None
        how = "defineProps({...})"
    if props is not None:
        defaults = defaults_of(text, m.start()) if re.search(r"withDefaults\s*\(\s*$", text[max(0, m.start() - 40):m.start()]) else {}
        for pr in props:
            if pr["name"] in defaults:
                pr["default"] = defaults[pr["name"]]
    return props, how


def tsx_props(repo, text, name):
    for cand in (f"{name}Props", "Props"):
        if re.search(rf"\b(interface|type)\s+{cand}\b", text):
            return repo.resolve_props(cand), f"{cand} type"
    native = re.search(r"ComponentProps(?:WithoutRef|WithRef)?<\s*(?:\"(\w+)\"|'(\w+)'|typeof\s+([\w.]+))", text)
    if native and re.search(rf"function\s+{name}\b|const\s+{name}\b", text):
        return [], f"native <{native.group(1) or native.group(2)}> props" if not native.group(3) else f"native props of {native.group(3)}"
    m = re.search(rf"{name}\.propTypes\s*=\s*\{{", text)
    if m:
        b = m.end() - 1
        return object_members(text[b + 1:matching(text, b) - 1]), "propTypes"
    m = re.search(rf"(?:function\s+{name}|const\s+{name}\s*(?::[^=]+)?=\s*(?:React\.)?(?:forwardRef|memo)?\s*\(?\s*(?:function)?)\s*\(\s*\{{([^}}]*)\}}\s*:\s*(\w+)", text)
    if m:
        return repo.resolve_props(m.group(2)), f"{m.group(2)} type"
    return None, "none"


def entry_exports(repo, pkgs):
    """Names exported from the package entry, if the repo is a library."""
    names, entry = [], None
    candidates = []
    for p, data in pkgs[:1]:
        for field in ("source", "module", "main", "types"):
            if isinstance(data.get(field), str):
                candidates.append(data[field])
    candidates += ["src/index.ts", "src/index.tsx", "src/index.js", "src/main.ts", "index.ts", "index.js"]
    for c in candidates:
        p = repo.root / c
        if p.suffix in {".ts", ".tsx", ".js", ".mjs"} and p.exists() and "dist" not in p.parts:
            text = read(p)
            found = re.findall(r"export\s*\{\s*default\s+as\s+(\w+)\s*\}\s*from\s*['\"]([^'\"]+)['\"]", text)
            found += [(n.strip().split(" as ")[-1], src) for grp, src in re.findall(r"export\s*\{([^}]*)\}\s*from\s*['\"]([^'\"]+)['\"]", text) for n in grp.split(",") if n.strip() and "default" not in n]
            found += [("*", src) for src in re.findall(r"export\s*\*\s*from\s*['\"]([^'\"]+)['\"]", text)]
            if found:
                return repo.rel(p), found
    return entry, names


def cva_variants(text):
    """class-variance-authority: cva("...", { variants: { size: { sm: "...", lg: "..." } } }) -> {size: [sm, lg]}."""
    out = {}
    for m in re.finditer(r"\bvariants\s*:\s*\{", text):
        b = m.end() - 1
        body = text[b + 1:matching(text, b) - 1]
        for km in re.finditer(r"(?m)^\s*(?:([\w-]+)|['\"]([\w-]+)['\"])\s*:\s*\{", body):
            if km.start() and body[:km.start()].count("{") != body[:km.start()].count("}"):
                continue
            vb = km.end() - 1
            inner = body[vb + 1:matching(body, vb) - 1]
            vals = [x.group(1) or x.group(2) for x in re.finditer(r"(?m)^\s*(?:([\w-]+)|['\"]([\w-]+)['\"])\s*:", inner)
                    if inner[:x.start()].count("{") == inner[:x.start()].count("}") and inner[:x.start()].count("[") == inner[:x.start()].count("]")]
            if vals:
                out[km.group(1) or km.group(2)] = vals
    return out


PRIMITIVE_DIRS = {"ui", "primitives", "atoms", "elements", "design-system", "ds"}


def detect_components(repo, pkgs):
    entry, exported = entry_exports(repo, pkgs)
    exported_names = {n for n, _ in exported if n != "*" and n[:1].isupper()}
    comps = []
    for p in repo.files:
        parts = set(x.lower() for x in p.parts)
        if is_test(p) or ".stories." in p.name or p.name.endswith(".d.ts"):
            continue
        name = p.stem if p.stem.lower() != "index" else p.parent.name
        primitive = bool(PRIMITIVE_DIRS & set(x.lower() for x in p.parent.relative_to(repo.root).parts))
        if not name[:1].isupper() and p.suffix in {".tsx", ".jsx"} and primitive:
            # shadcn-style lowercase files: name the component after the export matching the file
            pascal = "".join(w.capitalize() for w in re.split(r"[-_.]", p.stem))
            names = re.findall(r"export\s+(?:default\s+)?(?:function|const)\s+([A-Z]\w*)", read(p)) + \
                [n.strip() for grp in re.findall(r"export\s*\{([^}]*)\}", read(p)) for n in grp.split(",") if n.strip()[:1].isupper()]
            if not names:
                continue
            name = pascal if pascal in names else names[0]
        elif not name[:1].isupper() and p.suffix != ".svelte":
            continue
        in_component_dir = any(x in parts for x in ("components", "component", "ui", "primitives", "atoms", "molecules", "organisms", "elements"))
        if p.suffix == ".vue":
            text = read(p)
            props, how = vue_props(repo, text)
        elif p.suffix in {".tsx", ".jsx"}:
            text = read(p)
            if not re.search(r"return\s*\(?\s*<|=>\s*\(?\s*<", text):
                continue
            props, how = tsx_props(repo, text, name)
        elif p.suffix == ".svelte":
            text = read(p)
            props = [{"name": n, "type": t.strip() if t else None, "optional": bool(d)} for n, t, d in re.findall(r"export\s+let\s+(\w+)\s*(?::\s*([^=;]+))?(=)?", text)]
            how = "export let"
        else:
            continue
        if not (in_component_dir or name in exported_names):
            continue
        is_page = any(x in parts for x in ("pages", "views", "routes", "app", "screens")) and name not in exported_names
        for pr in props or []:
            vals = repo.enum_values(pr["type"]) if pr.get("type") else None
            if vals:
                pr["values"] = vals
        variants = cva_variants(text) if "cva(" in text or "tv(" in text else {}
        if variants:
            props = props or []
            for k, vals in variants.items():
                hit = next((pr for pr in props if pr["name"] == k), None)
                if hit:
                    hit["values"] = vals
                else:
                    props.append({"name": k, "type": "variant (cva)", "optional": True, "values": vals})
            how = how + " + cva variants" if how != "none" else "cva variants"
        slots = sorted(set(re.findall(r"<slot(?:\s+name=['\"]([\w-]+)['\"])?", text)))
        comps.append({"name": name, "file": repo.rel(p), "exported": name in exported_names, "page": is_page, "primitive": primitive, "propsFrom": how,
                      "props": props, "slots": [s or "default" for s in slots] if p.suffix in {".vue", ".svelte"} else None,
                      "children": ("children" in text and p.suffix in {".tsx", ".jsx"}) or None,
                      "wraps": sorted(set(re.findall(r"<(v-[a-z-]+|V[A-Z]\w+|Mui\w+)\b", text)))[:6] or None})
    comps.sort(key=lambda c: (not c["exported"], c["page"], not c["primitive"], c["name"]))
    return entry, sorted(exported_names), comps


def detect_storybook(repo):
    sb_dir = repo.root / ".storybook"
    stories = [p for p in repo.files if re.search(r"\.stories\.(js|jsx|ts|tsx|mdx|svelte|vue)$", p.name)]
    titles = []
    for p in stories[:200]:
        m = re.search(r"title\s*:\s*['\"]([^'\"]+)['\"]", read(p))
        titles.append(m.group(1) if m else p.name.split(".stories")[0])
    return {"configured": sb_dir.exists(), "stories": len(stories), "titles": titles[:60]}


def detect_docs(repo):
    hits = []
    for p in repo.files:
        if re.match(r"docusaurus\.config\.(js|ts)$", p.name):
            hits.append({"kind": "Docusaurus", "file": repo.rel(p)})
        elif ".vitepress" in p.parts and p.name.startswith("config."):
            hits.append({"kind": "VitePress", "file": repo.rel(p)})
        elif p.suffix == ".mdx" and "stories" not in p.name:
            hits.append({"kind": "MDX page", "file": repo.rel(p)})
    showcase = [repo.rel(p) for p in repo.files if re.search(r"(Showcase|Gallery|Playground|Demo)\.(vue|tsx|jsx|svelte)$", p.name)]
    if showcase:
        hits.append({"kind": "Showcase pages", "file": f"{len(showcase)} files, e.g. {showcase[0]}"})
    return hits[:20]


def classify(pkgs, comps, exported, tokens):
    data = pkgs[0][1] if pkgs else {}
    signals = []
    if exported:
        signals.append(f"the package entry exports {len(exported)} capitalised names")
    if data.get("peerDependencies"):
        signals.append("it declares peer dependencies")
    if data.get("private") is True:
        signals.append('package.json says "private": true')
    if data.get("exports") or data.get("files"):
        signals.append("package.json lists what it publishes")
    library = bool(exported) or (bool(data.get("peerDependencies")) and data.get("private") is not True)
    if library:
        return "component-library", "high" if exported else "medium", signals
    if [c for c in comps if not c["page"]]:
        return "app-with-components", "medium", signals
    return "app-without-component-layer", "medium" if pkgs else "low", signals


def questions(stack, tokens, comps, kind):
    q = []
    libs = [x["name"] for x in stack["uiLibraries"]]
    own = [c for c in comps if not c["page"]]
    if kind == "component-library":
        q.append("Is this the library product teams actually install, or a prototype? Which product repos consume it, and at what version?")
    else:
        q.append("Do your product teams use a shared component library from another repository or package? If so, where is it?")
    if libs and own:
        wrapped = [c["name"] for c in own if c.get("wraps")]
        q.append(f"Your components sit on top of {', '.join(libs)}. When a screen needs a control the library lacks, do people use the {libs[0]} one directly, or build a new component?" + (f" ({len(wrapped)} components wrap {libs[0]} parts, e.g. {', '.join(wrapped[:3])}.)" if wrapped else ""))
    if len({t['file'] for t in tokens if t['kind'].startswith(('css', 'scss', 'less'))}) > 1:
        files = sorted({t["file"] for t in tokens})[:4]
        q.append(f"Tokens appear in several places ({', '.join(files)}). Which is the source of truth, and which are generated or copies?")
    if not tokens:
        q.append("We found no design tokens (CSS variables, Sass variables or theme objects). Where do colours, spacing and type sizes come from: hard-coded values, a separate package, or the design files?")
    themes = {}
    for name in [s for t in tokens for s in t.get("themeSelectors", [])] + [th for t in tokens for th in t.get("themes", [])]:
        short = re.split(r"--|\.|\[|=", name.strip(".").strip())[-1].strip("\"'] ") or name
        themes.setdefault(short.lower(), short)
    themes = sorted(themes.values())
    if themes:
        q.append(f"We found these themes: {', '.join(themes[:6])}. Which ship to customers, and does Figma model each one as a variable mode?")
    if own:
        q.append(f"Does each Figma component name match a code component (for example Figma's \"Button\" and code's \"{next((c['name'] for c in own if 'button' in c['name'].lower()), own[0]['name'])}\")? Where don't they line up?")
        q.append("Which components are deprecated, or about to change?")
    else:
        q.append("This app builds its interface without a component layer we could find. Is a shared component library planned, and in which framework?")
    return q


def write_stack_md(out, s):
    L = []
    rel = lambda f: f"`{f}`"
    L.append(f"# Stack: {s['name']}")
    L.append("")
    L.append(f"A draft from `scan_repo.py`, run {s['scannedOn']} on `{s['repo']}`. The scan reads files only, so check each line. Fix what's wrong, answer the questions at the end, then fill in **Confirmed**.")
    L.append("")
    L.append(f"**Confirmed:** not yet (name and date when a person has checked this)")
    L.append("")
    L.append("## What this repository is")
    L.append("")
    L.append(f"**{s['kind']['label']}** ({s['kind']['confidence']} confidence). " + ("Evidence: " + "; ".join(s["kind"]["signals"]) + "." if s["kind"]["signals"] else ""))
    if s.get("description"):
        L.append("")
        L.append(f"package.json describes it as: {s['description']}")
    L.append("")
    L.append("## Frameworks and libraries")
    L.append("")
    rows = [(k, x) for k in ("frameworks", "uiLibraries", "styling", "buildTools") for x in s["stack"][k]]
    if not s["stack"]["frameworks"]:
        L.append("No UI framework: the interface is plain JavaScript, HTML and CSS." if s["stack"]["buildTools"] or rows else "No front-end framework found in package.json.")
        L.append("")
    if rows:
        L.append("| Kind | Name | Version | Declared in |")
        L.append("|---|---|---|---|")
        label = {"frameworks": "Framework", "uiLibraries": "UI library", "styling": "Styling", "buildTools": "Build tool"}
        for k, x in rows:
            L.append(f"| {label[k]} | {x['name']} | {x['version'] or ''} | {x['declaredIn']} |")
    if s["stack"].get("packageManager"):
        L.append("")
        L.append(f"Package manager: {s['stack']['packageManager']}.")
    L.append("")
    L.append("## Design tokens")
    L.append("")
    if s["tokens"]:
        for t in s["tokens"]:
            extra = []
            if t.get("count") is not None:
                extra.append(f"{t['count']} definitions" + (f" ({t['unique']} unique)" if t.get("unique") and t["unique"] != t["count"] else ""))
            if t.get("prefixes"):
                extra.append("prefixes " + ", ".join(f"`--{k}-`" for k in t["prefixes"]))
            if t.get("themeSelectors"):
                extra.append("themes " + ", ".join(f"`{x}`" for x in t["themeSelectors"][:4]))
            if t.get("themes"):
                extra.append("themes " + ", ".join(f"`{x}`" for x in t["themes"]))
            if t.get("maps"):
                extra.append("maps " + ", ".join(f"`${x}`" for x in t["maps"][:4]))
            if t.get("sections"):
                extra.append("sections " + ", ".join(t["sections"]))
            L.append(f"- **{t['kind']}** in {rel(t['file'])}" + (": " + "; ".join(extra) if extra else ""))
    else:
        L.append("None found.")
    L.append("")
    own = [c for c in s["components"] if not c["page"]]
    pages = [c for c in s["components"] if c["page"]]
    L.append(f"## Components ({len(own)})")
    L.append("")
    if s.get("entry"):
        names = {c["name"] for c in own}
        others = [n for n in s["exported"] if n not in names]
        L.append(f"Package entry: {rel(s['entry'])}. It exports {len(s['exported']) - len(others)} of these components" + (f", plus {', '.join(others[:5])}." if others else "."))
        L.append("")
    prims = [c for c in own if c.get("primitive")]
    if prims and len(prims) < len(own):
        L.append(f"{len(prims)} sit in a `ui` or primitives folder, which usually means the design-system layer; they're listed first. The other {len(own) - len(prims)} are feature components built from them.")
        L.append("")
    if own:
        L.append("| Component | File | Props | Variant-like props | Slots |")
        L.append("|---|---|---|---|---|")
        for c in own[:80]:
            props = c["props"] or []
            names = ", ".join(p["name"] for p in props[:10]) + (" …" if len(props) > 10 else "") if props else ("not found" if c["props"] is None else "none")
            if c["propsFrom"].startswith("native"):
                names = (names + ", plus " if props else "") + c["propsFrom"].split(" + ")[0]
            variants = "; ".join(f"{p['name']}: {' / '.join(p['values'])}" for p in props if p.get("values"))[:160]
            slots = ", ".join(c["slots"]) if c.get("slots") else ("children" if c.get("children") else "")
            L.append(f"| {c['name']}{'' if c['exported'] or not s.get('entry') else ' (not exported)'} | {rel(c['file'])} | {names} | {variants} | {slots} |")
        if len(own) > 80:
            L.append(f"| … {len(own) - 80} more in stack.json | | | | |")
    else:
        L.append("No reusable components found: no component folder and no package exports.")
    if pages:
        L.append("")
        L.append(f"Plus {len(pages)} page or demo components (in `pages`, `views` or similar), left out of the table.")
    L.append("")
    L.append("## Storybook and docs")
    L.append("")
    sb = s["storybook"]
    L.append(f"- Storybook: {'configured' if sb['configured'] else 'not configured'}, {sb['stories']} story files." + (f" Titles include {', '.join(sb['titles'][:6])}." if sb["titles"] else ""))
    for d in s["docs"]:
        L.append(f"- {d['kind']}: {rel(d['file'])}")
    L.append("")
    L.append(f"**Tier:** {s['tier']['tier']}. {s['tier']['why']}")
    L.append("")
    L.append("## Questions for whoever knows the stack")
    L.append("")
    for i, q in enumerate(s["questions"], 1):
        L.append(f"{i}. {q}")
        L.append("   - Answer:")
    L.append("")
    (out / "STACK.md").write_text("\n".join(L))


ARCHITECT_QUESTIONS = [
    ("What the product is built with", [
        "Which framework do the web front ends use: React, Vue, Angular, Svelte, something else, or several?",
        "Do they use a component library such as MUI, Vuetify, Chakra, Ant Design, Bootstrap or shadcn/ui? Which version?",
        "How are styles written: CSS or Sass files, Tailwind, CSS-in-JS (styled-components, Emotion), or something else?",
        "Are there native mobile apps too? If so, do they share anything with the web (tokens, naming)?",
    ]),
    ("Shared components", [
        "Is there a shared component library in code? Where does it live (repository, package name), and who owns it?",
        "Roughly how many components does it have, and do product teams install it or copy from it?",
        "Is there a Storybook or another place where the components are documented? Please share the link.",
    ]),
    ("Design tokens", [
        "Where do colours, spacing, type sizes and radii come from in code: a tokens file, a theme object, Sass variables, or hard-coded values?",
        "Are tokens generated from somewhere (Tokens Studio, Style Dictionary, a Figma export), or written by hand?",
        "Are there themes or brands (light and dark, white-label clients)? How does the code switch between them?",
    ]),
    ("Access", [
        "Can the design team get read access to the repository? If not, could you share the tokens file and a list of components with their props?",
        "Who should we ask when something in Figma and code disagree?",
    ]),
]


def write_questionnaire(out, name, hints):
    L = [f"# Questions about {name}'s front-end stack", ""]
    L.append(f"We're documenting {name}'s design system so the Figma library and the code can be matched up. "
             "There's no repository to read, so these questions go to whoever knows how the product is built. "
             "Short answers are fine, and \"I don't know\" is a useful answer too.")
    L.append("")
    if hints:
        L.append("## What the Figma files suggest")
        L.append("")
        L.append("Please confirm or correct each one.")
        L.append("")
        for h in hints:
            L.append(f"- {h}")
            L.append("  - Right? ")
        L.append("")
    n = 0
    for title, qs in ARCHITECT_QUESTIONS:
        L.append(f"## {title}")
        L.append("")
        for q in qs:
            n += 1
            L.append(f"{n}. {q}")
            L.append("   - Answer:")
        L.append("")
    L.append(f"Answered by: (name, role, date)")
    (out / "ARCHITECT-QUESTIONS.md").write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?")
    ap.add_argument("--out", required=True, help="folder for the output files (created if needed)")
    ap.add_argument("--no-repo", action="store_true", help="no repository: write ARCHITECT-QUESTIONS.md")
    ap.add_argument("--name", help="org or product name, for --no-repo")
    ap.add_argument("--hint", action="append", default=[], help="what the Figma side suggests, for --no-repo (repeatable)")
    a = ap.parse_args()
    out = Path(a.out).expanduser()
    if a.no_repo:
        out.mkdir(parents=True, exist_ok=True)
        name = a.name or "your product"
        write_questionnaire(out, name, a.hint)
        (out / "stack.json").write_text(json.dumps({"name": name, "repo": None, "scannedOn": date.today().isoformat(),
                                                     "pendingQuestionnaire": "ARCHITECT-QUESTIONS.md", "hints": a.hint, "confirmed": None}, indent=1))
        print(f"No repository: wrote {out / 'ARCHITECT-QUESTIONS.md'} for whoever knows {name}'s stack, and a stub {out / 'stack.json'}.")
        return
    if not a.repo:
        sys.exit("Pass the path to a checked-out repository, or --no-repo if there isn't one.")
    root = Path(a.repo).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"{root} isn't a folder. Pass the path to a checked-out repository, or --no-repo if there isn't one.")
    out.mkdir(parents=True, exist_ok=True)

    repo = Repo(root)
    pkgs = scan_packages(repo)
    pkgs.sort(key=lambda pd: len(pd[0].parts))
    stack = detect_stack(repo, pkgs)
    tokens = detect_tokens(repo)
    entry, exported, comps = detect_components(repo, pkgs)
    kind, confidence, signals = classify(pkgs, comps, exported, tokens)
    sb = detect_storybook(repo)
    own = [c for c in comps if not c["page"]]
    if own:
        tier = {"tier": "3", "why": "The repository has components with props, so learn can map code components to Figma ones."}
    elif sb["stories"]:
        tier = {"tier": "2", "why": "Storybook stories but no component source found."}
    else:
        tier = {"tier": "below 2", "why": "No component layer in code, so learn works from the Figma side and this file only records the stack."}
    labels = {"component-library": "A component library", "app-with-components": "An app with its own components", "app-without-component-layer": "An app with no component layer"}
    data = pkgs[0][1] if pkgs else {}
    result = {
        "name": data.get("name") or root.name, "repo": str(root), "scannedOn": date.today().isoformat(),
        "description": data.get("description"), "filesRead": len(repo.files),
        "kind": {"value": kind, "label": labels[kind], "confidence": confidence, "signals": signals},
        "stack": stack, "tokens": tokens, "entry": entry, "exported": exported, "components": comps,
        "storybook": sb, "docs": detect_docs(repo), "tier": tier,
        "questions": questions(stack, tokens, comps, kind), "confirmed": None,
    }
    (out / "stack.json").write_text(json.dumps(result, indent=1))
    write_stack_md(out, result)
    print(f"{result['name']}: {labels[kind].lower()}, {len(own)} components, {len(tokens)} token sources, tier {tier['tier']}.")
    print(f"Wrote {out / 'stack.json'} and {out / 'STACK.md'}.")


if __name__ == "__main__":
    main()
