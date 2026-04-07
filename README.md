# Hugrell

Hugrell is a local-first web GUI for editing Hugo site files directly.

The project is intended to showcase:

- idiomatic MakrellPy application code
- MRON as a practical configuration and content format
- HTMX-driven interactivity without depending on external services
- strong support for Hugo front matter and Hugo-oriented content workflows

## Current bootstrap

The repo now includes a small runnable bootstrap:

- `run_dev.py`
  - tiny Python compatibility shim
- `run_dev.mrpy`
  - MakrellPy dev server entry point
- `app/dev_server.mrpy`
  - actual MakrellPy server logic
- `app/views.mrpy`
  - MakrellPy page and fragment rendering
- `hugrell.mron`
  - local app configuration in MRON
- `samples/site/`
  - a tiny Hugo-like fixture tree used by the bootstrap

Run it from this directory:

```bash
python run_dev.py --check
python run_dev.py
```

Then open `http://127.0.0.1:8096`.

This first scaffold is intentionally modest:

- the actual dev server entry point now lives under `app/`
- `run_dev.py` remains as a tiny compatibility shim so the old `python run_dev.py` workflow still works
- `run_dev.mrpy` is the only root-level MakrellPy entry point
- config loading and page rendering are already in MakrellPy
- MRON is already used as application config and sample site data
- fragment routes and `hx-*` hooks are present, but HTMX itself is not yet vendored locally
- app code now lives under `app/`, with only one `.mrpy` launcher left at repo root

## Product direction

The first deliverable should focus on a useful local editing experience for a
single Hugo site on one server or workstation.

Key goals:

- browse and edit Hugo content, data, layouts, and configuration files
- provide a strong MRON editing experience with validation and preview support
- make Hugo front matter pleasant to inspect and edit
- keep the system self-contained, with no dependency on other network services
- include a simple built-in logon system with roles

Out of scope for the first deliverable:

- git actions and source control workflows
- deployment pipelines
- multi-node or cloud-distributed architecture
- real-time collaborative editing

## Proposed shape

The application can be built as a MakrellPy server-rendered web app with HTMX
for incremental updates.

Main areas:

- `app/`
  - MakrellPy application code, including server logic and page rendering
- `app/templates/`
  - HTML templates and HTMX partials
- `app/static/`
  - CSS, JavaScript helpers, editor assets, and syntax-highlighting resources
- `docs/`
  - architecture notes, feature plans, and design decisions
- `samples/`
  - example MRON content and small Hugo site fixtures

## Suggested MVP

The MVP should support:

- opening a configured Hugo project root
- browsing content files and selected Hugo support files
- editing text files in the browser
- specialised forms for Hugo front matter
- MRON syntax highlighting and validation
- server-side preview rendering for selected file types
- basic user logon with at least `admin` and `editor` roles
- an audit-style activity log stored locally

## Important design choices

- local-first deployment, likely one process and one local database
- filesystem access restricted to configured Hugo roots
- explicit role checks around editing, publishing-related actions, and settings
- preview and validation as first-class features rather than add-ons
- progressive enhancement through HTMX instead of a heavy SPA

## Next docs

See:

- `docs/solution-outline.md`
- `docs/implementation-plan.md`
