# Camera Motion Game Controller Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python desktop prototype that detects body and hand actions from a webcam and maps them to keyboard input for PC and emulator games.

**Architecture:** The app is organized into camera capture, action detection, profile-based input mapping, and a lightweight desktop UI. Detection and mapping stay independent so the same recognized actions can drive different games through configuration.

**Tech Stack:** Python 3, pytest, OpenCV, MediaPipe, customtkinter, Pillow, pydirectinput, keyboard, JSON

---

### Task 1: Project Scaffold And Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/config.py`
- Create: `tests/test_smoke.py`

**Step 1: Write the failing test**

```python
from app.config import AppConfig


def test_default_config_contains_profiles_dir():
    config = AppConfig()
    assert config.profiles_dir.name == "profiles"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL with import error because `app.config` does not exist yet.

**Step 3: Write minimal implementation**

Create `AppConfig` with a default `profiles_dir` pointing to `profiles`, add the package scaffold, and add a minimal `main.py` entrypoint.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add requirements.txt README.md app/__init__.py app/main.py app/config.py tests/test_smoke.py
git commit -m "feat: scaffold camera controller project"
```

### Task 2: Profile Loading

**Files:**
- Create: `profiles/wow.json`
- Create: `profiles/wzry_emulator.json`
- Create: `app/profiles.py`
- Create: `tests/test_profiles.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from app.profiles import load_profile


def test_load_profile_reads_action_bindings(tmp_path: Path):
    profile_path = tmp_path / "sample.json"
    profile_path.write_text(
        '{"name":"sample","bindings":{"raise_right_hand":{"key":"1","mode":"tap"}}}',
        encoding="utf-8",
    )

    profile = load_profile(profile_path)

    assert profile.name == "sample"
    assert profile.bindings["raise_right_hand"].key == "1"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_profiles.py -v`
Expected: FAIL with missing module or function.

**Step 3: Write minimal implementation**

Implement profile dataclasses and JSON loading with validation for `name`, `bindings`, `key`, and `mode`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_profiles.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add profiles/wow.json profiles/wzry_emulator.json app/profiles.py tests/test_profiles.py
git commit -m "feat: add game profiles"
```

### Task 3: Action Detection Rules

**Files:**
- Create: `app/detection.py`
- Create: `tests/test_detection.py`

**Step 1: Write the failing test**

```python
from app.detection import detect_actions, LandmarkPoint


def test_detects_raise_right_hand():
    landmarks = {
        "right_wrist": LandmarkPoint(x=0.7, y=0.2),
        "right_shoulder": LandmarkPoint(x=0.7, y=0.45),
        "left_wrist": LandmarkPoint(x=0.3, y=0.6),
        "left_shoulder": LandmarkPoint(x=0.3, y=0.45),
    }

    actions = detect_actions(landmarks)

    assert "raise_right_hand" in actions
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_detection.py -v`
Expected: FAIL because `detect_actions` is not implemented.

**Step 3: Write minimal implementation**

Implement simple rule-based detection for:
- left/right lean
- left/right hand raise
- both hands up
- crouch
- fist/open palm placeholders with hand-state input

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_detection.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/detection.py tests/test_detection.py
git commit -m "feat: add rule-based action detection"
```

### Task 4: Input Mapping Engine

**Files:**
- Create: `app/input_mapper.py`
- Create: `tests/test_input_mapper.py`

**Step 1: Write the failing test**

```python
from app.input_mapper import InputMapper
from app.profiles import ActionBinding, GameProfile


def test_tap_action_triggers_bound_key():
    sent = []

    def sender(key: str, mode: str) -> None:
        sent.append((key, mode))

    profile = GameProfile(
        name="sample",
        target="pc",
        bindings={"raise_right_hand": ActionBinding(key="1", mode="tap")},
    )

    mapper = InputMapper(sender=sender)
    mapper.apply_actions({"raise_right_hand"}, profile)

    assert sent == [("1", "tap")]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_input_mapper.py -v`
Expected: FAIL because mapper does not exist.

**Step 3: Write minimal implementation**

Implement action-to-binding resolution with support for:
- tap events
- hold begin
- hold release
- cooldown/debounce bookkeeping

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_input_mapper.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/input_mapper.py tests/test_input_mapper.py
git commit -m "feat: add input mapping engine"
```

### Task 5: Camera And Landmark Pipeline

**Files:**
- Create: `app/camera.py`
- Create: `app/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
from app.pipeline import ControllerPipeline


def test_pipeline_returns_empty_actions_when_no_landmarks():
    pipeline = ControllerPipeline(detector=lambda frame: {})
    result = pipeline.process(frame=None)
    assert result.actions == set()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL because pipeline classes do not exist.

**Step 3: Write minimal implementation**

Implement a pipeline result object that takes a frame, runs a detector callback, converts landmarks into actions, and returns both landmarks and actions.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/camera.py app/pipeline.py tests/test_pipeline.py
git commit -m "feat: add camera processing pipeline"
```

### Task 6: UI State And Controller Loop

**Files:**
- Create: `app/ui.py`
- Create: `tests/test_ui_state.py`

**Step 1: Write the failing test**

```python
from app.ui import ControllerState


def test_controller_state_starts_inactive():
    state = ControllerState()
    assert state.running is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui_state.py -v`
Expected: FAIL because UI state is missing.

**Step 3: Write minimal implementation**

Implement controller state and a minimal UI shell that can:
- select a profile
- start/stop control mode
- show latest actions
- display a camera preview placeholder

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui_state.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/ui.py tests/test_ui_state.py
git commit -m "feat: add ui state and shell"
```

### Task 7: MediaPipe Integration

**Files:**
- Modify: `app/pipeline.py`
- Create: `app/mediapipe_backend.py`
- Create: `tests/test_mediapipe_backend.py`

**Step 1: Write the failing test**

```python
from app.mediapipe_backend import normalize_empty_result


def test_normalize_empty_result_returns_empty_dicts():
    pose, hands = normalize_empty_result(None)
    assert pose == {}
    assert hands == {}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_mediapipe_backend.py -v`
Expected: FAIL because backend module does not exist.

**Step 3: Write minimal implementation**

Wrap MediaPipe pose and hand outputs behind a normalization layer so the rest of the app only deals with simplified landmark dictionaries.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_mediapipe_backend.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/pipeline.py app/mediapipe_backend.py tests/test_mediapipe_backend.py
git commit -m "feat: integrate mediapipe backend"
```

### Task 8: End-To-End Manual Validation

**Files:**
- Modify: `README.md`

**Step 1: Write the failing test**

There is no automated end-to-end camera test for this step. Instead, add a manual verification checklist to the README before running the app.

**Step 2: Run test to verify it fails**

Run: `python -m app.main`
Expected: The app launches but manual validation reveals any missing behavior in profile switching, action display, or input dispatch.

**Step 3: Write minimal implementation**

Fix any discovered integration issues and document:
- install steps
- launch command
- supported actions
- profile format
- safety notes

**Step 4: Run test to verify it passes**

Run: `python -m app.main`
Expected: App launches, camera preview updates, actions appear, and mapped keys send only while control mode is enabled.

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add run and validation guide"
```
