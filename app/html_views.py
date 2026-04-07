from __future__ import annotations

from html import escape


def _h(value) -> str:
    if value is None:
        return ""
    return escape(str(value))


def _join(parts) -> str:
    return "".join(part for part in parts if part is not None)


def _attrs(**attrs) -> str:
    rendered = []
    for key, value in attrs.items():
        if value is None:
            continue
        if value is False:
            continue
        name = key.rstrip("_").replace("_", "-")
        if value is True:
            rendered.append(f" {name}")
            continue
        rendered.append(f' {name}="{_h(value)}"')
    return "".join(rendered)


def _tag(tag_name: str, content: str = "", **attrs) -> str:
    return f"<{tag_name}{_attrs(**attrs)}>{content}</{tag_name}>"


def _icon_class(kind: str, extra_class: str = "") -> str:
    class_name = f"icon-shell icon-{kind}"
    if extra_class:
        return f"{class_name} {extra_class}"
    return class_name


def _icon(kind: str, extra_class: str = "") -> str:
    return _tag("span", "", class_=_icon_class(kind, extra_class), aria_hidden="true")


def _file_icon_kind(kind: str) -> str:
    if kind == "content":
        return "content_file"
    if kind == "data":
        return "data"
    if kind == "layout":
        return "layout"
    if kind == "media":
        return "media_file"
    if kind == "dir":
        return "dir"
    return "file"


def _selected_preview_text(selected: dict | None) -> str:
    if not selected:
        return ""
    return selected.get("preview", "")


def _selected_rel_path(selected: dict | None) -> str:
    if not selected:
        return ""
    return selected.get("rel_path", "")


def _selected_suffix(selected: dict | None) -> str:
    if not selected:
        return ""
    return selected.get("suffix", "").lower()


def _selected_mode(selected: dict | None) -> str:
    rel_path = _selected_rel_path(selected)
    suffix = _selected_suffix(selected)
    if rel_path.startswith("content/"):
        return "content"
    if rel_path.startswith("data/") or suffix in {".mron", ".json", ".yaml", ".yml", ".toml"}:
        return "mron"
    if rel_path.startswith("layouts/") or suffix in {".html", ".css", ".js", ".ts", ".scss"}:
        return "template"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}:
        return "asset"
    return "text"


def _split_front_matter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {"has_front_matter": False, "front_matter": "", "body": text}
    closing = text.find("\n---\n", 4)
    if closing == -1:
        return {"has_front_matter": False, "front_matter": "", "body": text}
    return {
        "has_front_matter": True,
        "front_matter": text[4:closing],
        "body": text[closing + 5 :],
    }


def _front_matter_field_pairs(front_matter_text: str) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = []
    for raw_line in front_matter_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key:
            fields.append((key, value))
    return fields


def _summary_title(selected: dict | None) -> str:
    mode = _selected_mode(selected)
    if mode == "content":
        return "Hugo content editor"
    if mode == "mron":
        return "Data workspace"
    if mode == "template":
        return "Template workspace"
    if mode == "asset":
        return "Asset preview"
    return "Text workspace"


def _summary_copy(selected: dict | None) -> str:
    mode = _selected_mode(selected)
    if mode == "content":
        return "Front matter and body stay side by side, with preview and metadata close at hand."
    if mode == "mron":
        return "Data files stay readable and Hugo-aware rather than feel like anonymous text blobs."
    if mode == "template":
        return "Template and asset support should stay readable and Hugo-aware, with metadata close to the file."
    if mode == "asset":
        return "Static files surface metadata and preview affordances before richer editing flows land."
    return "Plain text files still open in the main editor surface with contextual metadata."


def _field_row(label: str, value: str) -> str:
    return _tag(
        "div",
        _tag("span", _h(label), class_="field-label")
        + _tag("span", _h(value), class_="field-value"),
        class_="field-row",
    )


def _front_matter_grid(pairs: list[tuple[str, str]]) -> str:
    rows = [
        _tag(
            "div",
            _tag("span", _h(key), class_="field-label")
            + _tag("span", _h(value), class_="field-value"),
            class_="field-row",
        )
        for key, value in pairs
    ]
    return _tag("div", _join(rows), class_="field-grid")


def _markdown_preview_html(text: str) -> str:
    parts: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            parts.append(_tag("p", _h(" ".join(paragraph_lines)), class_="markdown-paragraph"))
            paragraph_lines = []

    def flush_list():
        nonlocal list_items
        if list_items:
            items = "".join(_tag("li", _h(item)) for item in list_items)
            parts.append(_tag("ul", items, class_="markdown-list"))
            list_items = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:].strip())
            continue
        heading_level = len(stripped) - len(stripped.lstrip("#"))
        if 1 <= heading_level <= 6 and stripped[heading_level : heading_level + 1] == " ":
            flush_paragraph()
            flush_list()
            heading_text = stripped[heading_level + 1 :].strip()
            parts.append(
                _tag(
                    f"h{heading_level}",
                    _h(heading_text),
                    class_=f"markdown-heading markdown-heading-{heading_level}",
                )
            )
            continue
        flush_list()
        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    return _join(parts)


def _nav_item(href: str, label: str, kicker: str, icon_kind: str, active: bool) -> str:
    class_name = "nav-item nav-item-active" if active else "nav-item"
    return _tag(
        "a",
        _icon(icon_kind, "nav-icon")
        + _tag("span", _h(label), class_="nav-label")
        + _tag("span", _h(kicker), class_="nav-kicker"),
        href=href,
        class_=class_name,
    )


def _metric_card(section: dict) -> str:
    kind = section.get("kind", "file")
    return _tag(
        "article",
        _icon(_file_icon_kind(kind), "metric-icon")
        + _tag("p", _h(section.get("label", "")), class_="meta-label")
        + _tag("p", _h(section.get("count", 0)), class_="metric-value")
        + _tag("p", _h(section.get("description", "")), class_="metric-copy")
        + _tag("p", _h(section.get("path", "")), class_="metric-path"),
        class_=f"metric-card metric-card-{kind}",
    )


def _recent_file_row(entry: dict) -> str:
    kind = entry.get("kind", "")
    return _tag(
        "a",
        _icon(_file_icon_kind(kind), "recent-icon")
        + _tag(
            "div",
            _tag("p", _h(entry.get("name", "")), class_="recent-name")
            + _tag("p", _h(entry.get("rel_path", "")), class_="recent-path"),
            class_="recent-main",
        )
        + _tag(
            "div",
            _tag("span", _h(kind), class_="data-chip")
            + _tag("span", _h(entry.get("modified_text", "")), class_="recent-time")
            + _tag("span", _h(entry.get("size_text", "")), class_="recent-size"),
            class_="recent-meta",
        ),
        href=entry.get("href", "#"),
        class_="recent-row",
    )


def _browser_entry(entry: dict) -> str:
    kind = entry.get("kind", "file")
    indent = f"padding-left: {entry.get('depth', 0) + 1}rem"
    classes = ["explorer-entry"]
    classes.append("explorer-entry-dir" if kind == "dir" else "explorer-entry-file")
    if entry.get("is_selected", False):
        classes.append("explorer-entry-selected")
    icon_kind = _file_icon_kind("dir" if kind == "dir" else kind)
    return _tag(
        "li",
        _tag(
            "a",
            _icon(icon_kind, "explorer-icon")
            + _tag("span", _h(entry.get("rel_path", "")), class_="explorer-entry-name"),
            href=entry.get("href", "#"),
            class_=" ".join(classes),
            style=indent,
        ),
    )


def _diagnostic_items(selected: dict | None) -> list[str]:
    mode = _selected_mode(selected)
    text = _selected_preview_text(selected)
    front_matter = _split_front_matter(text)
    front_matter_rows = _front_matter_field_pairs(front_matter.get("front_matter", ""))
    if mode == "content":
        return [
            "Front matter detected and separated from body preview."
            if front_matter.get("has_front_matter", False)
            else "No front matter block detected yet; content editing should highlight this.",
            f"Parsed {len(front_matter_rows)} top-level front matter field(s)."
            if front_matter.get("has_front_matter", False)
            else "Content file is currently body-only.",
        ]
    if mode == "mron":
        return ["Data file detected. Hugo sites usually prefer YAML, TOML, or JSON data files here."]
    if mode == "template":
        return ["Template-like file detected. Keep syntax support and Hugo context visible in the side panel."]
    return ["Read-only bootstrap mode is active. Save flow, validation, and richer preview come next."]


def _flash_banner(flash: dict | None) -> str:
    if not flash:
        return ""
    kind = flash.get("kind", "info")
    return _tag(
        "section",
        _tag("p", _h(kind), class_="meta-label")
        + _tag("p", _h(flash.get("message", ""))),
        class_=f"flash-banner flash-banner-{kind}",
    )


def _content_edit_form(rel_path: str, selected: dict, front_matter: dict, body_text: str) -> str:
    pairs = _front_matter_field_pairs(front_matter.get("front_matter", ""))
    front_matter_text = front_matter.get("front_matter", "")
    grid = _front_matter_grid(pairs) if pairs else ""
    return _tag(
        "form",
        _tag("input", "", type="hidden", name="path", value=rel_path)
        + _tag("input", "", type="hidden", name="expected_modified", value=selected.get("modified", ""))
        + _tag("input", "", type="hidden", name="save_mode", value="content_split")
        + _tag(
            "div",
            _tag(
                "section",
                _tag(
                    "div",
                    _tag("p", "Front matter", class_="meta-label")
                    + _tag(
                        "span",
                        "detected" if front_matter.get("has_front_matter", False) else "new",
                        class_="data-chip",
                    ),
                    class_="subpanel-head",
                )
                + grid
                + _tag("label", "Front matter source", class_="editor-label", for_="editor-front-matter")
                + _tag(
                    "textarea",
                    _h(front_matter_text),
                    id="editor-front-matter",
                    class_="editor-textarea editor-textarea-short",
                    name="front_matter",
                ),
                class_="editor-subpanel",
            )
            + _tag(
                "section",
                _tag(
                    "div",
                    _tag("p", "Body", class_="meta-label") + _tag("span", "markdown", class_="data-chip"),
                    class_="subpanel-head",
                )
                + _tag("label", "Body source", class_="editor-label", for_="editor-body")
                + _tag(
                    "textarea",
                    _h(body_text),
                    id="editor-body",
                    class_="editor-textarea",
                    name="body",
                ),
                class_="editor-subpanel",
            ),
            class_="editor-split",
        )
        + _tag(
            "div",
            _tag("button", _icon("save", "button-icon") + "Save content", type="submit", class_="primary-button")
            + _tag(
                "p",
                "Front matter and body are saved back as one ordinary Hugo content file.",
                class_="muted",
            ),
            class_="editor-actions",
        ),
        class_="editor-form",
        method="post",
        action="/save",
    )


def _text_edit_form(rel_path: str, selected: dict, content_text: str) -> str:
    return _tag(
        "form",
        _tag("input", "", type="hidden", name="path", value=rel_path)
        + _tag("input", "", type="hidden", name="expected_modified", value=selected.get("modified", ""))
        + _tag("label", "Document source", class_="editor-label", for_="editor-content")
        + _tag(
            "textarea",
            _h(content_text),
            id="editor-content",
            class_="editor-textarea",
            name="content",
        )
        + _tag(
            "div",
            _tag("button", _icon("save", "button-icon") + "Save file", type="submit", class_="primary-button")
            + _tag(
                "p",
                "This first save flow writes directly to the local Hugo workspace and blocks conflicting older edits.",
                class_="muted",
            ),
            class_="editor-actions",
        ),
        class_="editor-form",
        method="post",
        action="/save",
    )


def _content_preview(front_matter: dict, body_text: str) -> str:
    pairs = _front_matter_field_pairs(front_matter.get("front_matter", ""))
    front_block = _front_matter_grid(pairs) if pairs else _tag(
        "pre", _h(front_matter.get("front_matter", "")), class_="editor-preview editor-preview-short"
    )
    return _tag(
        "div",
        _tag(
            "section",
            _tag(
                "div",
                _tag("p", "Front matter", class_="meta-label")
                + _tag(
                    "span",
                    "detected" if front_matter.get("has_front_matter", False) else "pending",
                    class_="data-chip",
                ),
                class_="subpanel-head",
            )
            + front_block,
            class_="editor-subpanel",
        )
        + _tag(
            "section",
            _tag(
                "div",
                _tag("p", "Body preview", class_="meta-label") + _tag("span", "markdown", class_="data-chip"),
                class_="subpanel-head",
            )
            + _tag("div", _markdown_preview_html(body_text), class_="editor-preview editor-preview-prose"),
            class_="editor-subpanel",
        ),
        class_="editor-split",
    )


def _selected_file_panel(state: dict) -> str:
    selected = state.get("selected_file")
    rel_path = state.get("selected_rel_path", "")
    if not selected:
        return _tag(
            "section",
            _tag(
                "div",
                _tag("div", _tag("p", "Editor", class_="meta-label") + _tag("h3", "Choose a file to inspect"))
                + _tag("span", "read-only", class_="data-chip"),
                class_="editor-panel-head",
            )
            + _tag(
                "div",
                _tag("p", "Open a Hugo content file, data document, or template from the explorer to inspect it here.")
                + _tag(
                    "p",
                    "This central pane is reserved for the editor surface, with context and preview information pushed to the right-hand inspector.",
                    class_="muted",
                ),
                class_="editor-note",
            ),
            class_="editor-panel",
        )
    if selected.get("error"):
        return _tag(
            "section",
            _tag(
                "div",
                _tag("div", _tag("p", "Editor", class_="meta-label") + _tag("h3", _h(rel_path)))
                + _tag("span", "error", class_="data-chip data-chip-warn"),
                class_="editor-panel-head",
            )
            + _tag("p", _h(selected.get("error", "")), class_="muted"),
            class_="editor-panel",
        )
    if selected.get("kind") == "dir":
        return _tag(
            "section",
            _tag(
                "div",
                _tag("div", _tag("p", "Directory", class_="meta-label") + _tag("h3", _h(selected.get("name", ""))))
                + _tag("span", "folder", class_="data-chip"),
                class_="editor-panel-head",
            )
            + _tag("p", _h(selected.get("rel_path", "")), class_="editor-path")
            + _tag("p", "This path is a directory. Pick a file entry to inspect text content and metadata.", class_="muted"),
            class_="editor-panel",
        )

    mode = _selected_mode(selected)
    content_text = selected.get("content", _selected_preview_text(selected))
    front_matter = _split_front_matter(content_text)
    body_text = front_matter.get("body", content_text)
    editable = selected.get("editable", False)
    edit_form = ""
    if editable:
        edit_form = (
            _content_edit_form(rel_path, selected, front_matter, body_text)
            if mode == "content"
            else _text_edit_form(rel_path, selected, content_text)
        )
    preview = _content_preview(front_matter, body_text) if mode == "content" else _tag("pre", _h(_selected_preview_text(selected)), class_="editor-preview")
    return _tag(
        "section",
        _tag(
            "div",
            _tag("div", _tag("p", _h(_summary_title(selected)), class_="meta-label") + _tag("h3", _h(selected.get("name", ""))))
            + _tag("span", _h(mode if editable else "read-only"), class_="data-chip"),
            class_="editor-panel-head",
        )
        + _tag(
            "div",
            _tag("span", _icon("content", "toolbar-icon") + "editor", class_="toolbar-pill")
            + _tag("span", _icon("preview", "toolbar-icon") + "preview", class_="toolbar-pill")
            + _tag("span", _icon("diagnostics", "toolbar-icon") + "diagnostics", class_="toolbar-pill")
            + _tag("span", _icon("save", "toolbar-icon") + ("save enabled" if editable else "read-only"), class_="toolbar-pill toolbar-pill-strong"),
            class_="editor-toolbar",
        )
        + _tag(
            "div",
            _tag("p", _tag("span", "Path", class_="meta-label") + _tag("span", _h(selected.get("rel_path", "")), class_="editor-path"))
            + _tag("p", _tag("span", "Size", class_="meta-label") + _tag("span", f"{selected.get('size', 0)} bytes"))
            + _tag("p", _tag("span", "Modified", class_="meta-label") + _tag("span", _h(selected.get("modified", "")), class_="editor-path")),
            class_="editor-meta",
        )
        + edit_form
        + preview,
        class_="editor-panel",
    )


def _selected_context_panel(state: dict) -> str:
    selected = state.get("selected_file")
    if not selected:
        return _tag(
            "aside",
            _tag(
                "div",
                _tag("div", _tag("p", "Context", class_="meta-label") + _tag("h2", "Inspector"))
                + _tag("span", "workspace", class_="data-chip"),
                class_="section-head",
            )
            + _tag(
                "div",
                _tag("p", "Pick a file from the explorer to inspect front matter, preview notes, and implementation cues.", class_="section-copy")
                + _tag(
                    "div",
                    _field_row("Focus", "Three-pane Hugo editing")
                    + _field_row("Data", "Hugo-native")
                    + _field_row("Preview", "Local-first"),
                    class_="field-grid",
                ),
                class_="context-stack",
            ),
            class_="surface-panel context-panel",
        )

    rel_path = state.get("selected_rel_path", "")
    if selected.get("error"):
        return _tag(
            "aside",
            _tag(
                "div",
                _tag("div", _tag("p", "Context", class_="meta-label") + _tag("h2", "Inspector"))
                + _tag("span", "error", class_="data-chip data-chip-warn"),
                class_="section-head",
            )
            + _tag("div", _tag("p", _h(selected.get("error", "")), class_="section-copy"), class_="context-stack"),
            class_="surface-panel context-panel",
        )

    if selected.get("kind") == "dir":
        return _tag(
            "aside",
            _tag(
                "div",
                _tag("div", _tag("p", "Context", class_="meta-label") + _tag("h2", "Inspector"))
                + _tag("span", "dir", class_="data-chip"),
                class_="section-head",
            )
            + _tag(
                "div",
                _tag("p", "Directories should drive navigation, filters, and creation actions rather than occupy the main editor pane.", class_="section-copy")
                + _tag("div", _field_row("Directory", selected.get("name", "")) + _field_row("Path", rel_path), class_="field-grid"),
                class_="context-stack",
            ),
            class_="surface-panel context-panel",
        )

    text = _selected_preview_text(selected)
    front_matter = _split_front_matter(text)
    front_matter_rows = _front_matter_field_pairs(front_matter.get("front_matter", ""))
    mode = _selected_mode(selected)
    diagnostics = _diagnostic_items(selected)
    cards = [
        _tag(
            "div",
            _tag("p", "Editing mode", class_="meta-label")
            + _tag("h3", _h(_summary_title(selected)))
            + _tag("p", _h(_summary_copy(selected)), class_="section-copy"),
            class_="context-card",
        ),
        _tag(
            "div",
            _tag("p", "File facts", class_="meta-label")
            + _tag(
                "div",
                _field_row("Path", rel_path)
                + _field_row("Suffix", selected.get("suffix", ""))
                + _field_row("Size", f"{selected.get('size', 0)} bytes"),
                class_="field-grid",
            ),
            class_="context-card",
        ),
        _tag(
            "div",
            _tag("p", "Diagnostics", class_="meta-label")
            + _tag(
                "ul",
                "".join(
                    _tag("li", _tag("span", "•", class_="context-dot") + _tag("span", _h(item)), class_="context-item")
                    for item in diagnostics
                ),
                class_="context-list",
            ),
            class_="context-card",
        ),
    ]
    if mode == "content":
        cards.append(
            _tag(
                "div",
                _tag("p", "Front matter", class_="meta-label")
                + (
                    _tag("pre", _h(front_matter.get("front_matter", "")), class_="context-preview")
                    if front_matter.get("has_front_matter", False)
                    else _tag("p", "No front matter preview available for this content file.", class_="section-copy")
                ),
                class_="context-card",
            )
        )
        cards.append(
            _tag(
                "div",
                _tag("p", "Front matter fields", class_="meta-label")
                + (
                    _front_matter_grid(front_matter_rows)
                    if front_matter_rows
                    else _tag("p", "No simple top-level key: value fields were extracted from the current front matter block.", class_="section-copy")
                ),
                class_="context-card",
            )
        )
    if mode == "mron":
        cards.append(
            _tag(
                "div",
                _tag("p", "Data preview", class_="meta-label")
                + _tag("pre", _h(text), class_="context-preview"),
                class_="context-card",
            )
        )
    return _tag(
        "aside",
        _tag(
            "div",
            _tag("div", _tag("p", "Context", class_="meta-label") + _tag("h2", "Inspector"))
            + _tag("span", _h(mode), class_="data-chip"),
            class_="section-head",
        )
        + _tag("div", _join(cards), class_="context-stack"),
        class_="surface-panel context-panel",
    )


def render_overview_fragment(state: dict) -> str:
    build_status = state.get("build_status", {})
    return _tag(
        "section",
        _tag(
            "section",
            _tag(
                "div",
                _tag("p", "Overview", class_="meta-label")
                + _tag("h2", _h(state.get("site_name", "")))
                + _tag("p", "Local-first Hugo workspace, tuned for fast editing.", class_="hero-lede"),
                class_="hero-copy",
            )
            + _tag(
                "div",
                _tag("span", _h(build_status.get("label", "")), class_="data-chip data-chip-strong")
                + _tag("span", _h(build_status.get("detail", "")), class_="data-chip"),
                class_="hero-chip-stack",
            ),
            class_="hero-ledger hero-ledger-fragment",
        )
        + _tag("div", "".join(_metric_card(section) for section in state.get("sections", [])), class_="metric-grid"),
        class_="overview-stack",
        id="overview",
    )


def render_browser_fragment(state: dict) -> str:
    return _tag(
        "section",
        _tag(
            "section",
            _tag(
                "div",
                _tag("div", _tag("p", "Explorer", class_="meta-label") + _tag("h2", "Site tree"))
                + _tag("span", f"{state.get('total_files', 0)} files", class_="data-chip"),
                class_="section-head",
            )
            + _tag("ul", "".join(_browser_entry(entry) for entry in state.get("browser_entries", [])), class_="explorer-list"),
            class_="surface-panel explorer-panel",
        )
        + _selected_file_panel(state)
        + _selected_context_panel(state),
        class_="studio-grid",
        id="browser",
    )


def render_home_page(state: dict) -> str:
    build_status = state.get("build_status", {})
    build_label = f"Build {build_status.get('last_build', '')}"
    nav = "".join(
        [
            _nav_item("#overview", "Dashboard", "01", "dashboard", True),
            _nav_item("#browser", "Explorer", "02", "explorer", False),
            _nav_item("#content", "Content", "03", "content", False),
            _nav_item("#media", "Media", "04", "media", False),
            _nav_item("#deploy", "Deployment", "05", "deploy", False),
        ]
    )
    recent = "".join(_recent_file_row(entry) for entry in state.get("recent_files", []))
    steps = "".join(
        _tag("li", _tag("span", "•", class_="step-bullet") + _tag("span", _h(step)), class_="step-item")
        for step in state.get("next_steps", [])
    )
    overview = _tag(
        "section",
        _tag(
            "section",
            _tag(
                "div",
                _tag("p", "Architectural ledger", class_="meta-label")
                + _tag("h1", _h(state.get("app_title", "Hugrell")))
                + _tag("p", _h(state.get("tagline", "")), class_="hero-lede"),
                class_="hero-copy",
            )
            + _tag(
                "div",
                _tag("span", _h(state.get("site_name", "")), class_="data-chip data-chip-strong")
                + _tag("span", _h(build_status.get("health", "Ready")), class_="data-chip")
                + _tag("span", _h(state.get("total_storage_text", "0 B")), class_="data-chip"),
                class_="hero-chip-stack",
            )
            + _tag("p", "Built as a local-first MakrellPy showcase with Hugo-safe file access.", class_="muted"),
            class_="hero-ledger",
        )
        + _tag(
            "section",
            _tag("div", _tag("p", "Total files", class_="meta-label") + _tag("p", _h(state.get("total_files", 0)), class_="summary-value"), class_="summary-stat")
            + _tag("div", _tag("p", "Storage", class_="meta-label") + _tag("p", _h(state.get("total_storage_text", "0 B")), class_="summary-value"), class_="summary-stat")
            + _tag("div", _tag("p", "Media", class_="meta-label") + _tag("p", _h(state.get("media_count", 0)), class_="summary-value"), class_="summary-stat")
            + _tag("div", _tag("p", "Layouts", class_="meta-label") + _tag("p", _h(state.get("layout_count", 0)), class_="summary-value"), class_="summary-stat"),
            class_="summary-band",
        )
        + _tag("div", "".join(_metric_card(section) for section in state.get("sections", [])), class_="metric-grid"),
        class_="overview-stack",
        id="overview",
    )
    body = (
        _tag(
            "aside",
            _tag("div", _tag("p", "Hugrell", class_="brand-mark") + _tag("p", "Static editing ledger", class_="brand-subline"), class_="brand-block")
            + _tag("nav", nav, class_="nav-list")
            + _tag(
                "div",
                _tag("a", "Open sample post", href="/?path=content/posts/hello.md", class_="primary-button")
                + _tag("p", "No network services required. All state stays on this machine.", class_="side-note"),
                class_="side-cta",
            ),
            class_="side-nav",
        )
        + _tag(
            "div",
            _tag(
                "header",
                _tag(
                    "div",
                    _icon("search", "topbar-icon")
                    + _tag(
                        "div",
                        _tag("p", "Search workspace", class_="meta-label")
                        + _tag("p", "Files, front matter, and templates", class_="topbar-value"),
                        class_="topbar-search-copy",
                    ),
                    class_="topbar-search",
                )
                + _tag(
                    "div",
                    _tag(
                        "div",
                        _tag("p", "Site root", class_="meta-label")
                        + _tag("p", _h(state.get("site_root", "")), class_="topbar-value"),
                        class_="topbar-site",
                    )
                    + _tag("span", _h(build_label), class_="data-chip")
                    + _tag("button", _icon("notifications", "topbar-action-icon"), type="button", class_="topbar-action", title="Notifications")
                    + _tag("button", _icon("settings", "topbar-action-icon"), type="button", class_="topbar-action", title="Settings")
                    + _tag("a", _icon("deploy", "button-icon") + "Deploy", href="#deploy", class_="deploy-button"),
                    class_="topbar-block topbar-block-right",
                ),
                class_="topbar",
            )
            + _tag(
                "main",
                _flash_banner(state.get("flash"))
                + overview
                + render_browser_fragment(state)
                + _tag(
                    "section",
                    _tag(
                        "section",
                        _tag(
                            "div",
                            _tag("div", _tag("p", "Recent files", class_="meta-label") + _tag("h2", "Editing cadence"))
                            + _tag("span", _icon("info", "chip-icon") + f"{len(state.get('recent_files', []))} tracked", class_="data-chip"),
                            class_="section-head",
                        )
                        + _tag("div", recent, class_="recent-list"),
                        class_="surface-panel",
                    )
                    + _tag(
                        "section",
                        _tag(
                            "div",
                            _tag("div", _tag("p", "Implementation track", class_="meta-label") + _tag("h2", "Next slices"))
                            + _tag("span", _icon("spark", "chip-icon") + _h(build_status.get("health", "")), class_="data-chip data-chip-strong"),
                            class_="section-head",
                        )
                        + _tag("p", _h(build_status.get("detail", "")), class_="section-copy")
                        + _tag("ul", steps, class_="step-list"),
                        class_="surface-panel",
                        id="deploy",
                    ),
                    class_="supplement-grid",
                ),
                class_="workspace-main",
            ),
            class_="workspace-shell",
        )
    )
    return (
        "<!doctype html>"
        + _tag(
            "html",
            _tag(
                "head",
                '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
                + _tag("title", _h(state.get("app_title", "Hugrell")))
                + '<link rel="stylesheet" href="/static/styles.css">',
            )
            + _tag("body", _tag("div", body, class_="app-shell")),
            lang="en",
        )
    )
