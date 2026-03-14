# Profile Editor Design

**Date:** 2026-03-14

**Goal**

Add persistent action-mapping management so users can save, load, edit, copy, rename, and delete mappings by game, character, and preset.

**Scope**

The feature should support:
- Multiple games.
- Multiple characters under each game.
- Multiple presets under each character.
- A form-based editor for action bindings.
- A future-friendly path for binding-record mode.

**Recommended Approach**

Store presets as individual JSON files in a directory tree:
- `profiles/<game>/<character>/<preset>.json`

Use `default` as the character folder when a preset is not tied to a specific role or hero.

This approach is simpler than a central database, easy to inspect by hand, and supports backup, sharing, import, and export later.

**Alternatives Considered**

1. Single JSON database
   Fastest to prototype, but hard to maintain as data grows.

2. Per-game and per-character file storage
   Best fit for the requested game and role organization. Recommended.

3. Indexed metadata plus separate preset files
   More extensible, but too heavy for the first version.

**Data Model**

Each preset stores:
- `game_name`
- `character_name`
- `preset_name`
- `notes`
- `updated_at`
- `bindings`

Each binding stores:
- `action_name`
- `input_type`
- `input_value`
- `trigger_mode`
- `cooldown_ms`
- `enabled`

The `bindings` collection is keyed by action name so the editor can load a stable row per supported action.

**UI Design**

The editor screen should include:
- A game selector
- A character selector
- A preset selector
- Buttons for `New`, `Copy`, `Rename`, `Delete`, and `Save`
- A table of supported actions
- Editable fields per row for enable state, target input, trigger mode, and cooldown

The first release uses a form-based editor because it is easier to validate and test. A future recording mode can sit beside the form and fill the same fields.

**Behavior**

On startup, the app scans the `profiles` directory and builds a navigation tree of games, characters, and presets.

When the user selects a preset:
- The binding table loads from disk.
- Unsaved changes are tracked in UI state.
- Switching away from a dirty preset should warn before discarding changes.

When the user saves:
- Only the current preset file is written.
- The `updated_at` timestamp is refreshed.
- Missing directories are created automatically.

When the user copies:
- The current preset is duplicated under a new preset name.

When the user renames:
- The underlying file is renamed.

When the user deletes:
- The file is removed only after confirmation.

**Validation And Error Handling**

Before save:
- `preset_name` must not be empty.
- `game_name` must not be empty.
- `action_name` values must stay unique.
- Enabled bindings must have an input value.

On load:
- Invalid or corrupted JSON should surface a friendly error.
- Unknown actions in older files should be preserved if possible, but ignored by the main table until supported.

**Testing Strategy**

The feature should be covered with tests for:
- Path generation from game, character, and preset names
- Scanning and listing available presets
- Loading and saving preset files
- Copy, rename, and delete operations
- Dirty-state handling in UI state

**Success Criteria**

The feature is successful when a user can:
- Create separate mappings for different games
- Save multiple role or hero specific mappings per game
- Edit mappings from the UI without hand-editing JSON
- Switch presets safely without losing unsaved changes
