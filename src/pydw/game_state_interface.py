# Imports to support type annotations
from abc import ABC, abstractmethod
from typing import Optional

import pygame

from generic_utils.point import Point
from pydw.dialog_manager import DialogManager
from pydw.game_info import GameInfo
from pydw.game_map_interface import GameMapInterface
from pydw.game_mode import GameMode
from pydw.game_types import (
    DialogReplacementVariables,
    DialogType,
    MapDecoration,
    MonsterInfo,
    SpecialMonster,
    Tile,
)
from pydw.generic_game_state import GenericGameState
from pydw.hero_party import HeroParty
from pydw.map_character_state import MapCharacterState


class GameStateInterface(ABC, GenericGameState):
    def __init__(self, screen: pygame.surface.Surface) -> None:
        super().__init__(screen)

    @abstractmethod
    def archive_saved_game_file(self, save_game_file_path: str, archive_dir_name: str = "archive") -> None:
        """Archived an existing saved game file to have a backup to potentially revert to a prior save."""

    @abstractmethod
    def load(self, pc_name_or_file_name: Optional[str] = None) -> None:
        """Load the game state for the specified player character name or filename.  Saved game
        files can be renamed, but on a saved they are saved as <player character name>.xml."""

    @abstractmethod
    def get_game_info(self) -> GameInfo:
        """Get the static game info"""

    @abstractmethod
    def get_game_map(self) -> GameMapInterface:
        """Get the game map"""

    @abstractmethod
    def get_pending_dialog(self) -> Optional[DialogType]:
        """Get pending dialog"""

    @abstractmethod
    def clear_pending_dialog(self) -> None:
        """Clear pending dialog"""

    @abstractmethod
    def get_tile_monsters(self, tile: Optional[Point] = None) -> list[str]:
        """Get the list of monster names which may spawn at the specified position, or if not specified, the location
        of the player character."""

    @abstractmethod
    def get_special_monster(self, tile: Optional[Point] = None) -> Optional[SpecialMonster]:
        """Get the special monster at the specified position, or if not specified, the location of the player
        character."""

    @abstractmethod
    def get_tile_info(self, tile: Optional[Point]) -> Tile:
        """Get the tile info for the specified position, or if not specified, the location of the player character."""

    @abstractmethod
    def get_image_pad_tiles(self) -> Point:
        """Get a point where the width and height indicate how many times to repeat the outermost tiles so that the
        maps extend to the edge of the screen."""

    @abstractmethod
    def get_hero_party(self) -> HeroParty:
        """Get the hero party."""

    @abstractmethod
    def check_progress_markers(self, progress_marker: Optional[str], inverse_progress_marker: Optional[str]) -> bool:
        """Return True if the progress marker conditions are met.  Else return False."""

    @abstractmethod
    def get_dialog_replacement_variables(self) -> DialogReplacementVariables:
        """Get the dialog replacement variables used based on the current game state."""

    @abstractmethod
    def is_outside(self) -> bool:
        """Return True if the player character is outside a dungeon where the outside spell cannot be used and the
        return spell can be used.  Else return False.  This is the negation of is_inside."""

    @abstractmethod
    def is_inside(self) -> bool:
        """Return True if the player character is inside a dungeon where the outside spell can be used and the return.
        spell cannot be used.  Else return False.  This is the negation of is_outside."""

    @abstractmethod
    def is_in_combat(self) -> bool:
        """Return True if the player character is in combat.  Else return False."""

    @abstractmethod
    def is_combat_allowed(self) -> bool:
        """Return True if the player character is in a location where a combat encounter could start.
        Else return False."""

    @abstractmethod
    def is_light_restricted(self) -> bool:
        """Return True if the entire map is not lit.  Else return False."""

    # TODO: Move this into the HeroParty
    @abstractmethod
    def get_map_name(self) -> str:
        """Get the name of the current map."""

    @abstractmethod
    def set_map(
        self,
        new_map_name: str,
        one_time_decorations: Optional[list[MapDecoration]] = None,
        respawn_decorations: bool = False,
    ) -> None:
        """Set to a new map."""

    @abstractmethod
    def is_facing_locked_item(self) -> bool:
        """Return True is the player character is standing on or looking at (next tile over in the direction they are
        facing) a locked item (ie a locked door or chest which requires a key to open).  Else return False."""

    @abstractmethod
    def is_facing_openable_item(self) -> bool:
        """Return True is the player character is standing on or looking at (next tile over in the direction they are
        facing) a locked or unlocked item (ie any door or chest).  Else return False."""

    @abstractmethod
    def open_locked_item(self) -> Optional[MapDecoration]:
        pass

    @abstractmethod
    def remove_decoration(self, decoration: MapDecoration) -> None:
        pass

    @abstractmethod
    def get_npc_by_name(self, name: str) -> Optional[MapCharacterState]:
        pass

    @abstractmethod
    def save(self, quick_save: bool = False) -> None:
        """Save the state of the game to the filesystem.  If the save not associated dialog on load,
        set quick_save to true."""

    @abstractmethod
    def get_win_size_pixels(self) -> Point:
        pass

    @abstractmethod
    def initiate_encounter(
        self,
        monster_info: Optional[MonsterInfo] = None,
        approach_dialog: Optional[DialogType] = None,
        victory_dialog: Optional[DialogType] = None,
        run_away_dialog: Optional[DialogType] = None,
        encounter_music: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def handle_death(self) -> None:
        pass

    @abstractmethod
    def handle_quit(self, force: bool = False) -> None:
        pass

    @abstractmethod
    def should_add_math_problems_in_combat(self) -> bool:
        """Return flag indicating if combat is in math mode."""
        pass

    @abstractmethod
    def toggle_should_add_math_problems_in_combat(self) -> None:
        """Toggle the flag indicating if combat is in math mode."""
        pass

    @abstractmethod
    def get_dialog_manager(self) -> DialogManager:
        """Get the dialog manager."""

    @abstractmethod
    def get_game_mode(self) -> GameMode:
        """Get the game mode."""

    @abstractmethod
    def set_game_mode(self, game_mode: GameMode) -> None:
        """Set the game mode."""
