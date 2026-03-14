# Body Offset Mouse Control Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Let body anchor offsets (shoulders or head) drive relative mouse deltas with the existing runtime tuning controls.

**Architecture:** Introduce a focused `BodyMouseMapper` that consumes landmark data, computes offsets against the chosen anchor, applies deadzone/smoothing/sensitivity, and sends mouse `move` events through `InputMapper`. Extend runtime tuning to include a persisted anchor choice so the UI and control loop share the same selection.

**Tech Stack:** Python dataclasses, OpenCV/MediaPipe landmarks, Tkinter UI, `pytest` for TDD.

---

### Task 1: BodyMouseMapper delta math

**Files:**
- Create: `app/body_mouse_mapper.py`
- Test: `tests/test_body_mouse_mapper.py`

**Step 1: Write the failing test**

```python
def test_mapper_computes_offset_based_on_shoulder_anchor():
    mapper = BodyMouseMapper(anchor="shoulders")
    landmarks = {"left_shoulder": (0.4, 0.5), "right_shoulder": (0.6, 0.5)}
    delta = mapper.compute_mouse_delta(landmarks, frame_size=(640, 480))
    assert delta != (0, 0)
```

**Step 2: Run test**

`pytest tests/test_body_mouse_mapper.py -v`
Expect: FAIL (module/class missing)

**Step 3: Implement BodyMouseMapper**

```python
class BodyMouseMapper:
    def __init__(self, anchor: str = "shoulders"):
        ...
    def compute_mouse_delta(self, landmarks, frame_size):
        # compute normalized anchor point, subtract center, apply deadzone/smoothing/sensitivity
```

**Step 4: Run test**

`pytest tests/test_body_mouse_mapper.py::test_mapper_computes_offset_based_on_shoulder_anchor -v`
Expect: PASS

**Step 5: Commit**

`git add app/body_mouse_mapper.py tests/test_body_mouse_mapper.py`
`git commit -m "feat: add body mouse mapper"`

### Task 2: Persist anchor choice in runtime settings and UI

**Files:**
- Modify: `app/runtime_settings.py`
- Modify: `app/main.py: build preview column and runtime helpers`
- Test: `tests/test_control_ui.py`

**Step 1: Write failing test**

Add test verifying `ProfileEditorApp` exposes `mouse_anchor_var` defaulting to `shoulders`, saves selection to runtime defaults, and loads source label accordingly.

**Step 2: Run test**

`pytest tests/test_control_ui.py::test_runtime_anchor_defaults -v`
Expect: FAIL (missing anchor handling)

**Step 3: Implement UI changes**

Update runtime settings to include `mouse_anchor` with default `"shoulders"`, add `StringVar` + dropdown in preview panel, load/save logic, and show anchor source in `runtime_source_var`.

**Step 4: Run test**

`pytest tests/test_control_ui.py::test_runtime_anchor_defaults -v`
Expect: PASS

**Step 5: Commit**

`git add app/runtime_settings.py app/main.py tests/test_control_ui.py`
`git commit -m "feat: persist anchor selection"`

### Task 3: Hook mapper into control loop

**Files:**
- Modify: `app/main.py: process_current_frame`
- Modify: `app/controller.py` or new helper to pass landmarks to mapper
- Test: `tests/test_controller.py`

**Step 1: Write failing test**

```
def test_controller_triggers_mouse_delta_with_anchor():
    mapper = BodyMouseMapper(...)
    controller = Controller(...)
    # simulate landmarks, ensure mapper called via InputMapper
```
```

**Step 2: Run test**

`pytest tests/test_controller.py::test_controller_triggers_mouse_delta_with_anchor -v`
Expect: FAIL

**Step 3: Implement integration**

Instantiate `BodyMouseMapper` in `ProfileEditorApp`, update `_apply_actions` or `process_current_frame` to call `mapper.apply_mouse_movement` with landmarks and input mapper.

**Step 4: Run test**

`pytest tests/test_controller.py -v`
Expect: PASS

**Step 5: Commit**

`git add app/main.py app/controller.py app/body_mouse_mapper.py tests/test_controller.py`
`git commit -m "feat: map body offset to mouse"`
