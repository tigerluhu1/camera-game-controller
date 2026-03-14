# Camera Control Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add webcam capture, MediaPipe-based action recognition, and keyboard plus mouse output to the existing preset-driven desktop app.

**Architecture:** The app keeps preset management as-is, then layers a camera pipeline, rule-based action detection, and an input mapper on top. A controller loop coordinates capture, detection, mapping, and UI status while explicit start/stop gating prevents unintended input.

**Tech Stack:** Python 3, pytest, OpenCV, MediaPipe, Pillow, tkinter, pydirectinput

---

### Task 1: Add Detection Models And Rules

**Files:**
- Create: `app/detection.py`
- Create: `tests/test_detection.py`

**Step 1: Write the failing test**

```python
from app.detection import LandmarkPoint, detect_actions


def test_detect_actions_detects_raise_right_hand():
    landmarks = {
        "right_wrist": LandmarkPoint(x=0.7, y=0.2),
        "right_shoulder": LandmarkPoint(x=0.7, y=0.45),
    }

    actions = detect_actions(landmarks, hand_states={})

    assert "raise_right_hand" in actions
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_detection.py::test_detect_actions_detects_raise_right_hand -v`
Expected: FAIL because `app.detection` does not exist.

**Step 3: Write minimal implementation**

Add:
- `LandmarkPoint` dataclass
- `detect_actions(landmarks, hand_states)`
- simple rules for lean, hand raise, both hands up, crouch, fist, and open palm

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_detection.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/detection.py tests/test_detection.py
git commit -m "feat: add action detection rules"
```

### Task 2: Add Keyboard And Mouse Mapping

**Files:**
- Create: `app/input_mapper.py`
- Create: `tests/test_input_mapper.py`

**Step 1: Write the failing test**

```python
from app.input_mapper import InputMapper
from app.profile_models import Binding, Preset


def test_mapper_emits_keyboard_and_mouse_commands():
    events = []

    def sender(event_type, value, mode):
        events.append((event_type, value, mode))

    preset = Preset(
        game_name="wow",
        preset_name="pve",
        bindings={
            "raise_right_hand": Binding(action_name="raise_right_hand", input_value="1"),
            "right_fist": Binding(action_name="right_fist", input_type="mouse", input_value="left_click"),
        },
    )

    mapper = InputMapper(sender=sender)
    mapper.apply_actions({"raise_right_hand", "right_fist"}, preset)

    assert ("key", "1", "tap") in events
    assert ("mouse", "left_click", "tap") in events
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_input_mapper.py::test_mapper_emits_keyboard_and_mouse_commands -v`
Expected: FAIL because mapper module does not exist.

**Step 3: Write minimal implementation**

Implement:
- keyboard tap handling
- mouse click handling
- relative mouse move handling
- cooldown and hold bookkeeping

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_input_mapper.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/input_mapper.py tests/test_input_mapper.py
git commit -m "feat: add keyboard and mouse mapper"
```

### Task 3: Add Camera Backend Abstraction

**Files:**
- Create: `app/camera.py`
- Create: `tests/test_camera.py`

**Step 1: Write the failing test**

```python
from app.camera import CameraStatus


def test_camera_status_defaults_to_stopped():
    status = CameraStatus()
    assert status.running is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_camera.py::test_camera_status_defaults_to_stopped -v`
Expected: FAIL because camera module does not exist.

**Step 3: Write minimal implementation**

Add:
- `CameraStatus`
- a thin camera wrapper for open/read/close
- frame conversion helper for UI consumption

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_camera.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/camera.py tests/test_camera.py
git commit -m "feat: add camera backend"
```

### Task 4: Add Controller Loop

**Files:**
- Create: `app/controller.py`
- Create: `tests/test_controller.py`

**Step 1: Write the failing test**

```python
from app.controller import Controller


def test_controller_does_not_emit_events_when_stopped():
    emitted = []
    controller = Controller(
        detector=lambda frame: {"actions": {"raise_right_hand"}},
        mapper=lambda actions, preset: emitted.append((actions, preset)),
    )

    controller.process_frame(frame=None, preset=None)

    assert emitted == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_controller.py::test_controller_does_not_emit_events_when_stopped -v`
Expected: FAIL because controller module does not exist.

**Step 3: Write minimal implementation**

Implement:
- running state
- start and stop methods
- per-frame processing that only emits while running
- controller status snapshot for UI

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_controller.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/controller.py tests/test_controller.py
git commit -m "feat: add controller loop"
```

### Task 5: Add MediaPipe Integration Layer

**Files:**
- Create: `app/vision_backend.py`
- Modify: `app/controller.py`
- Create: `tests/test_vision_backend.py`

**Step 1: Write the failing test**

```python
from app.vision_backend import normalize_result


def test_normalize_result_handles_empty_values():
    result = normalize_result(None, None)
    assert result.landmarks == {}
    assert result.hand_states == {}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_vision_backend.py::test_normalize_result_handles_empty_values -v`
Expected: FAIL because backend module does not exist.

**Step 3: Write minimal implementation**

Wrap MediaPipe outputs behind a normalization layer so controller logic only sees plain landmarks and hand states.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_vision_backend.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/vision_backend.py app/controller.py tests/test_vision_backend.py
git commit -m "feat: add mediapipe normalization layer"
```

### Task 6: Extend UI With Camera And Control State

**Files:**
- Modify: `app/main.py`
- Modify: `app/ui.py`
- Create: `tests/test_control_ui.py`

**Step 1: Write the failing test**

```python
from app.config import AppConfig
from app.main import create_app


def test_app_has_control_buttons_and_status(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    assert hasattr(app, "start_control")
    assert hasattr(app, "stop_control")
    app.root.destroy()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_control_ui.py::test_app_has_control_buttons_and_status -v`
Expected: FAIL because the UI does not expose control methods yet.

**Step 3: Write minimal implementation**

Update the window with:
- camera preview area
- start and stop control methods
- camera status label
- detected actions label
- event log area
- mouse sensitivity control

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_control_ui.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/main.py app/ui.py tests/test_control_ui.py
git commit -m "feat: add camera control ui"
```

### Task 7: Wire Live Input Dispatch

**Files:**
- Modify: `app/main.py`
- Modify: `app/input_mapper.py`
- Modify: `README.md`

**Step 1: Write the failing test**

There is no safe end-to-end automated test for live keyboard and mouse dispatch. First add a manual verification checklist to `README.md`.

**Step 2: Run test to verify it fails**

Run: `python -m app.main`
Expected: The app starts, but manual validation reveals any missing pieces in preview, start/stop gating, or action-to-input dispatch.

**Step 3: Write minimal implementation**

Wire the live loop so:
- camera preview updates while the app runs
- detected actions update in the UI
- input dispatch only occurs after `Start Control`
- `Stop Control` halts further input immediately

**Step 4: Run test to verify it passes**

Run: `python -m app.main`
Expected: Manual check confirms preview, recognition state, and gated input dispatch.

**Step 5: Commit**

```bash
git add app/main.py app/input_mapper.py README.md
git commit -m "feat: wire live camera control loop"
```
