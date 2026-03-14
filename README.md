# Camera Game Controller

A Python desktop prototype for managing camera-driven game control presets.

## Current Features

- Save presets under `profiles/<game>/<character>/<preset>.json`
- Load presets by game, character, and preset name
- Edit supported actions in a desktop form
- Create, copy, rename, and delete presets from the desktop toolbar
- Track unsaved changes in editor state

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

## Test

```bash
pytest -v
```

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

- Add camera capture and action recognition
- Add preset creation helpers in the UI
- Add copy, rename, and delete buttons to the desktop shell
- Add keyboard injection for live gameplay
