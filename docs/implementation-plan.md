# Implementation plan

## Phase 0: repo bootstrap

- create the MakrellPy app skeleton
- define the package/module layout
- add a development entry point
- add initial template and static asset structure
- add a sample Hugo fixture site for testing

## Phase 1: local app shell

- add app config loading
- add SQLite setup and migrations strategy
- add session handling
- add login and logout pages
- add base layout, navigation, and error pages

Deliverable:

- local app starts
- admin can log in
- empty dashboard works

## Phase 2: Hugo site registration and safe browsing

- register one Hugo root directory
- implement path resolution and safety checks
- build the file tree UI
- add file metadata panel
- add file open flow

Deliverable:

- browse a configured Hugo site safely from the web UI

## Phase 3: text editing and save flow

- add editor tabs
- load and save text files
- track unsaved state
- add optimistic conflict detection using modified timestamps or hashes
- add local audit entries for edits

Deliverable:

- edit and save Hugo files through the browser

## Phase 4: Hugo content and front matter support

- detect content files with front matter
- split front matter from body in the editor
- show structured front matter form controls
- add field validation and helpful defaults
- support raw view and structured view switching

Deliverable:

- Hugo content editing feels materially better than plain text editing

## Phase 5: MRON-first features

- integrate MRON parsing and diagnostics
- add MRON syntax highlighting
- add structured error display
- add formatting or normalisation helpers if available
- add preview or rendered data view for MRON documents

Deliverable:

- MRON becomes a headline feature of the application

## Phase 6: preview workflows

- add body preview for Markdown-like content
- add front matter summary preview
- add adapter boundary for Hugo CLI rendering
- optionally add rendered page preview when local Hugo is available

Deliverable:

- editors can validate content changes quickly inside the app

## Phase 7: permissions and hardening

- refine role checks
- lock down destructive operations
- improve audit log views
- add CSRF protection and secure cookie settings
- add file-type and site-scope policies

Deliverable:

- app is suitable for cautious internal use

## First deliverable definition

The first meaningful deliverable should include:

- local login
- one configured Hugo site
- safe file browsing
- text editing and save
- Hugo front matter support
- MRON diagnostics
- preview panel

It should explicitly not block on:

- git integration
- deployment automation
- multi-user collaboration
- external auth providers

## Suggested technical principles

- keep the core app server-rendered
- use HTMX for targeted interactions
- use SQLite until proven insufficient
- keep filesystem operations explicit and auditable
- prefer a plugin-like boundary for preview/render adapters
- keep the code pleasant to read as MakrellPy showcase material
