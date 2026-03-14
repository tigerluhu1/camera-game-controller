from __future__ import annotations

from pathlib import Path

from app.profile_store import ProfileStore


def list_available_presets(root: Path | str) -> dict[str, dict[str, list[str]]]:
    store = ProfileStore(root)
    tree: dict[str, dict[str, list[str]]] = {}
    for game_name in store.list_games():
        tree[game_name] = {}
        for character_name in store.list_characters(game_name):
            tree[game_name][character_name] = store.list_presets(game_name, character_name)
    return tree
