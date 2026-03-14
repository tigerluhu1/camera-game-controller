# Camera Motion Game Controller Design

**Date:** 2026-03-14

**Goal**

Build a desktop application that uses a camera to detect body movements and hand gestures, then maps those detections to keyboard and mouse input for both PC games and Android emulator games.

**Scope**

The first version focuses on a playable prototype rather than full-body replacement for keyboard and mouse. It should:
- Capture live camera frames.
- Detect a small set of reliable body poses and hand gestures.
- Map detected actions to configurable keyboard output.
- Support multiple per-game profiles.
- Show a live preview and control status in a desktop UI.

**Non-goals**

- Full competitive-grade replacement for keyboard and mouse.
- Direct phone integration for mobile devices.
- Automatic per-game detection.
- Large action libraries in the first release.

**Recommended Approach**

Use a Python desktop app with:
- `OpenCV` for camera capture.
- `MediaPipe` for pose and hand landmark detection.
- `customtkinter` for a lightweight control UI.
- `pydirectinput` and `keyboard` for keyboard output.
- JSON profile files for per-game bindings.

This gives the fastest path to a working prototype while keeping the detection pipeline and game mapping logic separate.

**Alternatives Considered**

1. Browser-based prototype
   Good for fast UI iteration, but system-level keyboard injection is awkward and less reliable.

2. Python desktop app
   Best balance of speed, reliability, and access to camera plus keyboard simulation. Recommended.

3. Unity application
   Strong visual tooling, but too much overhead for a first playable version.

**Architecture**

The app is split into four layers:

1. `capture`
   Reads frames from the camera and provides them to the detection pipeline.

2. `detection`
   Converts pose and hand landmarks into normalized game actions such as `lean_left`, `raise_right_hand`, or `fist`.

3. `mapping`
   Resolves detected actions into keyboard events using the active game profile and debounce/cooldown rules.

4. `ui`
   Displays camera preview, current actions, active profile, and start/stop controls.

**Core Actions For V1**

The first version should support these actions:
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

This keeps the recognition set small enough to tune while still covering movement and skill triggers.

**Game Mapping Model**

Profiles should define:
- Profile name
- Target type: `pc` or `emulator`
- Action-to-key mapping
- Whether an action is hold-based or tap-based
- Cooldown and debounce settings

Example behavior:
- In a PC profile, `raise_right_hand` could trigger key `1`.
- In an emulator profile, the same action could trigger key `J`.

**User Experience**

The desktop window should include:
- Camera preview with optional landmark overlay
- Current recognition status
- Active profile selector
- Start/stop control toggle
- Calibration button
- Small event log for the last few triggers

Input should only be sent when control mode is active.

**Safety And Reliability**

To reduce accidental input:
- Require a short detection stability window before firing.
- Apply per-action cooldowns.
- Support a manual stop button.
- Ignore actions when pose confidence is below threshold.

**Testing Strategy**

The first release should validate:
- Camera access works.
- Landmarks are converted into expected actions from synthetic inputs.
- Mapper emits the right key events for tap and hold actions.
- Profiles load and switch correctly.
- UI can start and stop the controller loop safely.

**Success Criteria**

The prototype is successful when it:
- Recognizes at least 6 actions reliably.
- Loads and switches between at least 2 game profiles.
- Sends mapped keys into one PC game and one Android emulator.
- Feels responsive enough for casual play and experimentation.
