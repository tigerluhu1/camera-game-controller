# Camera Game Controller

A Python desktop prototype for managing camera-driven game control presets.

## Current Features

- Save presets under `profiles/<game>/<character>/<preset>.json`
- Load presets by game, character, and preset name
- Edit supported actions in a desktop form
- Copy, rename, and delete presets through the storage layer
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
