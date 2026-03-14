# Profile Editor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add persistent game, character, and preset management with editable action mappings in the desktop controller app.

**Architecture:** Presets are stored as JSON files under a `profiles/<game>/<character>/<preset>.json` tree. A storage layer handles file operations, the UI state layer tracks selection and unsaved changes, and the editor view binds rows of supported actions to the active preset.

**Tech Stack:** Python 3, pytest, pathlib, json, customtkinter

---

### Task 1: Define Preset Models

**Files:**
- Create: `app/profile_models.py`
- Create: `tests/test_profile_models.py`

**Step 1: Write the failing test**

```python
from app.profile_models import Binding, Preset


def test_preset_defaults_character_to_default():
    preset = Preset(game_name="wow", preset_name="pve")
    assert preset.character_name == "default"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_profile_models.py -v`
Expected: FAIL because the module does not exist.

**Step 3: Write minimal implementation**

Add dataclasses for `Binding` and `Preset`, plus helper methods for JSON serialization.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_profile_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/profile_models.py tests/test_profile_models.py
git commit -m "feat: add preset models"
```

### Task 2: Add Preset Storage Layer

**Files:**
- Create: `app/profile_store.py`
- Create: `tests/test_profile_store.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from app.profile_models import Preset
from app.profile_store import ProfileStore


def test_save_preset_writes_nested_path(tmp_path: Path):
    store = ProfileStore(tmp_path)
    preset = Preset(game_name="wow", character_name="mage", preset_name="pve")

    path = store.save_preset(preset)

    assert path == tmp_path / "wow" / "mage" / "pve.json"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_profile_store.py -v`
Expected: FAIL because storage layer is missing.

**Step 3: Write minimal implementation**

Implement:
- path normalization
- list games
- list characters
- list presets
- load preset
- save preset
- copy preset
- rename preset
- delete preset

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_profile_store.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/profile_store.py tests/test_profile_store.py
git commit -m "feat: add preset storage layer"
```

### Task 3: Wire Store Into Existing Profile Logic

**Files:**
- Modify: `app/config.py`
- Modify: `app/profiles.py`
- Create: `tests/test_profiles_integration.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from app.profiles import list_available_presets


def test_list_available_presets_groups_by_game_and_character(tmp_path: Path):
    (tmp_path / "wow" / "mage").mkdir(parents=True)
    (tmp_path / "wow" / "mage" / "pve.json").write_text("{}", encoding="utf-8")

    tree = list_available_presets(tmp_path)

    assert tree["wow"]["mage"] == ["pve"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_profiles_integration.py -v`
Expected: FAIL because listing helper does not exist.

**Step 3: Write minimal implementation**

Connect existing profile-loading code to the new preset store and expose helpers used by the UI.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_profiles_integration.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/config.py app/profiles.py tests/test_profiles_integration.py
git commit -m "feat: integrate preset store with profile loading"
```

### Task 4: Add Editor State

**Files:**
- Create: `app/editor_state.py`
- Create: `tests/test_editor_state.py`

**Step 1: Write the failing test**

```python
from app.editor_state import EditorState


def test_mark_dirty_when_binding_changes():
    state = EditorState()
    state.set_binding_value("raise_right_hand", "1")
    assert state.is_dirty is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_editor_state.py -v`
Expected: FAIL because editor state module is missing.

**Step 3: Write minimal implementation**

Implement state for:
- current game
- current character
- current preset
- binding rows
- dirty flag
- save/discard workflow

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_editor_state.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/editor_state.py tests/test_editor_state.py
git commit -m "feat: add editor state"
```

### Task 5: Add Profile Editor UI

**Files:**
- Modify: `app/ui.py`
- Create: `tests/test_profile_editor_ui.py`

**Step 1: Write the failing test**

```python
from app.ui import build_editor_rows


def test_build_editor_rows_contains_supported_actions():
    rows = build_editor_rows()
    assert "raise_right_hand" in rows
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_profile_editor_ui.py -v`
Expected: FAIL because the helper does not exist.

**Step 3: Write minimal implementation**

Update the UI so it can:
- select game, character, and preset
- edit rows in a form table
- save, copy, rename, and delete presets
- show dirty state and load errors

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_profile_editor_ui.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/ui.py tests/test_profile_editor_ui.py
git commit -m "feat: add profile editor ui"
```

### Task 6: Document Preset Workflow

**Files:**
- Modify: `README.md`

**Step 1: Write the failing test**

There is no automated test for documentation. Add a short preset management section before updating the app behavior.

**Step 2: Run test to verify it fails**

Run: `python -m app.main`
Expected: Manual check reveals whether preset creation, editing, and switching are understandable in the UI.

**Step 3: Write minimal implementation**

Document:
- preset directory structure
- how to create a game
- how to create a character preset
- how save/copy/rename/delete behave

**Step 4: Run test to verify it passes**

Run: `python -m app.main`
Expected: Manual flow is understandable and the docs match actual behavior.

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add preset editor usage"
```
