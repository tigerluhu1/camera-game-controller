# Chinese UI Translation Design

> **For Claude:** This plan captures the decision-making before translating the Tkinter UI into Chinese. No implementation skill should run until this design is approved.

**Goal:** Translate every user-facing label, button, status line, and section header in the Camera Game Controller window into Chinese to give a localized experience.

**Architecture:** The UI strings are defined directly inside `app/main.py` (toolbar labels, status fields, runtime controls) and also appear in a few helper modules such as `app/preview.py`. We will replace each English literal with the appropriate Chinese text without introducing runtime localization layers, because the requirement is fixed and limited.

**Tech Stack:** Python/Tkinter for the UI, PIL for preview rendering, existing `app.runtime_settings` & controller logic remain unchanged.

---

### Task 1: Toolbar and status texts

Translate all labels in the toolbar (Game/Character/Preset), status lines, and error messages that appear in `ProfileEditorApp.load_preset`, `save_preset`, etc.

### Task 2: Runtime panel labels

Translate the preview section title, camera device label, mouse sliders, runtime buttons, and runtime source text. Ensure the mouse anchor combobox shows Chinese options.

### Task 3: Preview and supporting helpers

Translate the `Camera Preview` label in `app/preview.py` if any, plus any new messages that surface (e.g., `Status: ...`).
