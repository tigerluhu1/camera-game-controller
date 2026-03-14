# Camera Game Controller

A Python desktop prototype for managing camera-driven game control presets.

## Install

```bash
pip install -r requirements.txt
```

## Current Features

- Save presets under `profiles/<game>/<character>/<preset>.json`
- Load presets by game, character, and preset name
- Edit supported actions in a desktop form
- Create, copy, rename, and delete presets from the desktop toolbar
- Track unsaved changes in editor state
- Start and stop a camera-control loop safely
- Process frames through a controller pipeline and route mapped key or mouse events

## Supported Actions

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

## Run

```bash
python -m app.main
```

Use the top toolbar to enter `Game`, `Character`, and `Preset`, then:
- `New` clears the form for a new preset name
- `Copy` saves the current form as a different preset
- `Rename` renames the current preset file
- `Delete` removes the current preset after confirmation
- `Load` and `Save` read and write the selected preset
- `Start Control` opens the camera backend and enables mapped input
- `Stop Control` stops the controller loop and closes the camera backend

## Test

```bash
pytest -v
```

## Manual Verification

1. Install dependencies with `pip install -r requirements.txt`
2. Run `python -m app.main`
3. Create or load a preset with at least one key binding, such as `raise_right_hand -> 1`
4. Click `Start Control`
5. Confirm the camera status changes from idle to running, or shows a clear backend error
6. Confirm the app updates detected actions when frames are processed
7. Confirm no input is sent before `Start Control`
8. Confirm `Stop Control` halts control and closes the camera backend

## Preset Layout

```text
profiles/
  world_of_warcraft/
    mage/
      pve.json
  honor_of_kings/
    default/
      default.json
```

## Next Steps

- Replace placeholder frame detection with real OpenCV + MediaPipe landmark extraction
- Feed live camera frames into the preview area
- Add mouse sensitivity, deadzone, and smoothing controls
- Route real keyboard and mouse events through `pydirectinput`
