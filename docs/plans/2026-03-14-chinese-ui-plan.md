# Chinese UI Translation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace every user-facing English string in the Tkinter window with Chinese equivalents.

**Architecture:** Work entirely inside `app/main.py` (toolbar/status panel/runtime controls) and `app/preview.py` (preview label) because the UI text is hard-coded there.

**Tech Stack:** Python 3.12, Tkinter widgets, `pytest` for regression.

---

### Task 1: Toolbar and status labels

**Files:**
- Modify: `app/main.py: toolbar creation + status label sections`
- Test: `tests/test_control_ui.py`

**Step 1: Write failing test**

```python
def test_toolbar_labels_are_chinese(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    assert "游戏" in app.status_var.get()
```

**Step 2: Run test**

`pytest tests/test_control_ui.py::test_toolbar_labels_are_chinese -v` (expect FAIL)

**Step 3: Implement changes**

Update `app/main.py` so toolbar buttons/labels use Chinese text. Adjust status messages accordingly.

**Step 4: Run test**

`pytest tests/test_control_ui.py::test_toolbar_labels_are_chinese -v` (expect PASS)

**Step 5: Commit**

`git add app/main.py tests/test_control_ui.py && git commit -m "feat: translate toolbar text"`

### Task 2: Runtime panel translation

**Files:**
- Modify: `app/main.py: preview panel construction`
- Test: `tests/test_control_ui.py`

**Step 1: Write failing test**

```python
def test_runtime_panel_labels_are_chinese(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    assert "摄像头预览" in app.preview_label.cget("text")
```

**Step 2: Run test**

`pytest tests/test_control_ui.py::test_runtime_panel_labels_are_chinese -v` (expect FAIL)

**Step 3: Implement changes**

Translate preview label, sliders, buttons in Chinese text; ensure status line `runtime_source_var` uses Chinese.

**Step 4: Run test**

`pytest tests/test_control_ui.py::test_runtime_panel_labels_are_chinese -v` (expect PASS)

**Step 5: Commit**

`git add app/main.py && git commit -m "feat: translate runtime panel"`

### Task 3: Preview helper wording

**Files:**
- Modify: `app/preview.py`
- Test: none (manual verification)

**Step 1:** Replace `Camera Preview` string and any status text with Chinese.

**Step 2:** Run smoke test `pytest -k preview -v`

**Step 3:** Commit with message `feat: translate preview labels`
