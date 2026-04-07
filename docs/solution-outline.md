# Solution outline

## Summary

Hugrell should be a local-first web application for editing Hugo sites directly
from the browser, with MakrellPy as the main implementation language and MRON as
an important showcase format.

The core idea is:

- MakrellPy on the server for application logic and HTML rendering
- HTMX for partial page updates and interactive workflows
- direct access to files in a configured Hugo site root
- specialised tooling for MRON and Hugo front matter
- no dependency on external network services

## Primary users

- `admin`
  - configures site roots, users, and editor capabilities
- `editor`
  - edits content, data, and selected site files
- `viewer`
  - can browse and preview content without changing it

## Core capabilities

### 1. Hugo-aware file management

The app should understand common Hugo project areas:

- `content/`
- `data/`
- `layouts/`
- `static/`
- `assets/`
- site config files

This does not need full Hugo semantic understanding on day one, but the UI
should already distinguish content types and offer context-sensitive actions.

### 2. MRON editing

MRON should be treated as a first-class format rather than plain text.

Desired features:

- syntax highlighting
- parse and validation feedback
- structural error display near the editor
- formatted view and raw source view
- preview of rendered or interpreted output where relevant

### 3. Hugo front matter tooling

This should be one of the signature features.

Ideas:

- split view with front matter form and body editor
- support for MRON-backed front matter workflows where appropriate
- field templates for common Hugo metadata
- schema-like validation for required and expected fields
- helpers for tags, categories, dates, slugs, drafts, menus, and multilingual fields
- conversion helpers between raw front matter text and structured editing views

### 4. Preview workflows

There are several useful preview levels:

- parsed MRON preview
- front matter summary preview
- Markdown or rich content preview
- rendered page preview from the Hugo output pipeline

For the first deliverable, it may be enough to support:

- content-body preview
- front matter preview
- a hook for Hugo rendering when Hugo is installed locally

If Hugo CLI integration is not ready immediately, the UI can still support a
preview panel with placeholder adapters and partial rendering.

### 5. Authentication and roles

Keep this intentionally simple for the first version:

- local user table
- password hashing
- session cookies
- role-based permissions
- optional per-site access restrictions later

No external OAuth or external identity providers should be required.

## Proposed architecture

## 1. Application style

A server-rendered HTMX application is a strong fit because:

- file editing workflows benefit from small partial updates
- role checks are simpler on the server
- the architecture remains easy to deploy locally
- MakrellPy can stay central rather than being hidden behind a large JS frontend

The browser should still use a small amount of JavaScript where needed for:

- code editor integration
- syntax highlighting
- keyboard shortcuts
- unsaved-change warnings
- split-pane resizing

## 2. Backend modules

Suggested backend areas:

- `auth`
  - users, roles, sessions, password hashing
- `sites`
  - registered Hugo roots and access policy
- `files`
  - safe filesystem browsing and file operations
- `editor`
  - open/save/version stamps/conflict checks
- `mron`
  - parse, validation, diagnostics, formatting hooks
- `frontmatter`
  - parse, structured edit model, conversions
- `preview`
  - content preview and optional Hugo rendering bridge
- `audit`
  - local logging of logon and edit actions

## 3. Data storage

A local SQLite database is probably enough for:

- users
- sessions
- configured sites
- editor settings
- audit records
- cached parse or preview metadata if useful

The Hugo content itself should remain on the filesystem.

## 4. Safe filesystem model

This part matters a lot.

The server should never allow arbitrary path access. It should:

- resolve every requested path against an allowed site root
- reject escapes outside the configured root
- separate read, write, rename, and delete permissions
- limit destructive operations in the first deliverable

For the MVP, it may be wise to support:

- browse
- open
- edit
- save
- create new file

and defer rename/move/delete until the permission model is well tested.

## UI ideas

## Main layout

A pragmatic three-pane layout would work well:

- left: site tree and filters
- centre: active editor tabs
- right: preview, diagnostics, front matter tools, or file metadata

This fits Hugo work especially well because users often move between content,
front matter, and preview continuously.

## Editor modes

Different file types can open with different affordances:

- MRON editor
  - structure-aware tools and validation
- Markdown content editor
  - front matter + body split
- template/config editor
  - plain text with syntax highlighting
- asset viewer
  - metadata or preview, with editing where sensible

## HTMX interaction patterns

Good HTMX candidates:

- file tree expansion
- loading editor tabs
- validation refresh
- preview refresh
- front matter field editor fragments
- login/logout and session refresh
- audit log filtering

## MakrellPy showcase opportunities

To make the project a real showcase rather than just "Python in Makrell syntax",
it should lean into MakrellPy strengths:

- clear declarative routing helpers
- concise HTML/template generation where it fits
- MRON-driven configuration and UI definitions
- compile-time helpers or macros for repetitive UI patterns if they genuinely
  improve readability
- typed or structured transformation pipelines for front matter processing

The code should stay idiomatic and readable, not macro-heavy for its own sake.

## Open design questions

- Which server stack should be the base host for MakrellPy?
- Should syntax highlighting come from shared assets already used in
  `vscode-makrell`, or from a lighter standalone browser component?
- Should the first front matter form model support YAML/TOML only, or also
  encourage MRON-centred workflows from the beginning?
- How tightly should Hugo CLI preview be integrated in the first deliverable?
- Do we want one configured Hugo site at first, or multiple selectable site roots?

## Recommended first slice

The most sensible first slice is:

- one local Hugo site root
- one built-in admin user created during setup
- browse and open files
- edit and save text files
- special handling for content files with front matter split
- MRON validation panel
- simple preview panel
- local SQLite-backed auth and audit log

That would already produce a convincing end-to-end demo.
