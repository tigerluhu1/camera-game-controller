# Camera Control Integration Design

**Date:** 2026-03-14

**Goal**

Extend the current preset editor into a camera-driven controller that can detect body and hand actions, then emit keyboard and mouse input for PC games and Android emulator games.

**Scope**

The first integrated version should:
- Open a webcam and show live preview in the desktop app.
- Detect a small set of body and hand actions.
- Map detected actions to keyboard and mouse output using the active preset.
- Gate all input behind explicit start and stop controls.
- Show recognition state and recent output events in the UI.

**Non-goals**

- Competitive-grade aim or precision camera tracking.
- Full replacement for keyboard and mouse.
- Advanced gesture recording or training.
- Automatic game-specific tuning.

**Recommended Approach**

Use:
- `OpenCV` for camera capture and frame conversion.
- `MediaPipe` for pose and hand landmarks.
- `pydirectinput` for keyboard and mouse events.
- The existing preset model and storage layer for action mappings.

This fits the current Python desktop app and lets recognition, mapping, and UI evolve independently.

**Alternatives Considered**

1. `OpenCV + MediaPipe + pydirectinput`
   Best compatibility for Windows games. Recommended.

2. `OpenCV + MediaPipe + pyautogui`
   Easier to prototype, but weaker game compatibility.

3. `OpenCV + custom recognition + pynput`
   More flexible, but slower to reach a stable playable result.

**Architecture**

Add five pieces:

1. `camera`
   Reads frames from the selected webcam.

2. `detection`
   Converts landmarks into normalized actions such as `lean_left`, `right_fist`, or `both_hands_up`.

3. `input_mapper`
   Resolves actions to keyboard and mouse commands using the active preset, including tap, hold, click, and relative mouse move.

4. `controller`
   Runs the capture -> detect -> map loop and enforces start/stop state plus safety gates.

5. `ui`
   Extends the existing window with camera preview, control buttons, recognition status, output log, and mouse tuning.

**Action Model**

The first version should support:
- `lean_left`
- `lean_right`
- `raise_left_hand`
- `raise_right_hand`
- `both_hands_up`
- `crouch`
- `left_fist`
- `right_fist`
- `left_open_palm`
- `right_open_palm`

Suggested defaults:
- Lean actions for movement
- Hand raises for skills
- Fists for click or attack
- Open palms for secondary actions

**Mouse Strategy**

The first version should support:
- Left click
- Right click
- Relative mouse move

Mouse movement should use body-center offset from the frame center, not direct hand-to-screen mapping. This is easier to stabilize and better for camera-based control.

**Safety And Reliability**

To reduce false inputs:
- Only send input when control mode is active.
- Require a short action stability window before firing.
- Add cooldowns for tap and click actions.
- Add deadzone and smoothing for mouse movement.
- Stop all output immediately when control mode is disabled.

**UI Changes**

The desktop window should gain:
- Camera preview panel
- `Start Control` and `Stop Control`
- Current camera status
- Current detected actions
- Recent output event log
- Mouse enable toggle
- Mouse sensitivity control

The preset editor remains the source of action bindings.

**Testing Strategy**

The implementation should verify:
- Detection rules from synthetic landmarks
- Mapping from actions to keyboard and mouse commands
- Controller does not emit input while stopped
- Controller emits expected commands while running
- UI state updates for camera and controller status

**Success Criteria**

The integration is successful when:
- The app shows a live camera preview
- At least 6 actions can be recognized
- Actions trigger mapped keyboard or mouse commands from the active preset
- Control can be started and stopped safely from the UI
