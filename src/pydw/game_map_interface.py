#!/usr/bin/env python

import abc
from heapq import heappop, heappush
from typing import Callable, Optional

import pygame

from generic_utils.point import Point
from pydw.game_types import (
    Direction,
    MapDecoration,
    Tile,
)
from pydw.npc_state import NpcState


class GameMapInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def size(self, with_padding: bool = False) -> Point:
        pass

    @abc.abstractmethod
    def update(self) -> None:
        pass

    @abc.abstractmethod
    def set_lighting_mode(self, is_day: bool) -> None:
        """Set state for the map's lighting mode."""
        # TODO: Consider how this should work.  Maybe we really want to do it by time of day so it can change
        #       gradually instead of just being a day/night toggle.

    @abc.abstractmethod
    def draw(self, surface: Optional[pygame.surface.Surface] = None) -> None:
        pass

    @abc.abstractmethod
    def draw_character_sprites(self) -> None:
        pass

    @abc.abstractmethod
    def get_tile_info(self, tile: Optional[Point] = None) -> Tile:
        pass

    @abc.abstractmethod
    def get_decorations(
        self,
        tile: Optional[Point] = None,
        decoration_filter: Optional[Callable[[MapDecoration], bool]] = None,
        stop_after_first: bool = False,
    ) -> list[MapDecoration]:
        pass

    @abc.abstractmethod
    def get_decoration_for_interaction(
        self,
        pos_dat_tile: Optional[Point] = None,
        decoration_filter: Optional[Callable[[MapDecoration], bool]] = None,
    ) -> Optional[MapDecoration]:
        pass

    @abc.abstractmethod
    def get_npc_to_talk_to(self) -> Optional[NpcState]:
        pass

    @abc.abstractmethod
    def can_move_to_tile(
        self,
        tile: Point,
        enforce_npc_hp_penalty_limit: bool = False,
        enforce_npc_dof_limit: bool = False,
        is_npc: bool = False,
        prev_tile: Optional[Point] = None,
    ) -> bool:
        pass

    def can_npc_move_to_tile(
        self,
        tile: Point,
        enforce_npc_hp_penalty_limit: bool = True,
        enforce_npc_dof_limit: bool = True,
        prev_tile: Optional[Point] = None,
    ) -> bool:
        return self.can_move_to_tile(tile, enforce_npc_hp_penalty_limit, enforce_npc_dof_limit, True, prev_tile)

    def compute_npc_path(self, start: Point, goal: Point, verbose: bool = False) -> Optional[list[Point]]:
        """Compute a path from start to goal for an NPC using A* search"""
        if verbose:
            print(f"in compute_npc_path; start={start}; goal={goal}", flush=True)

        def h(n: Point) -> float:
            return abs(goal.x - n.x) + abs(goal.y - n.y)

        open_set: list[tuple[float, Point]] = []
        heappush(open_set, (h(start), start))
        came_from: dict[Point, Point] = {}
        g_score: dict[Point, float] = {start: 0.0}
        f_score: dict[Point, float] = {start: h(start)}
        while 0 < len(open_set):
            queued_f_score, current = heappop(open_set)
            if queued_f_score != f_score[current]:
                if verbose:
                    print(
                        f"\tin compute_npc_path; ignoring current={current}; open_set={open_set}",
                        flush=True,
                    )
                continue
            if verbose:
                print(
                    f"\tin compute_npc_path; current={current}; open_set={open_set}",
                    flush=True,
                )
            if current == goal:
                break

            for direction in Direction:
                neighbor = current + direction.get_vector()
                if verbose:
                    print(f"\t\tin compute_npc_path; neighbor={neighbor}", flush=True)
                if not self.can_npc_move_to_tile(neighbor, enforce_npc_dof_limit=False, prev_tile=current):
                    if verbose:
                        print(
                            f"\t\t\tin compute_npc_path; cannot move to tile",
                            flush=True,
                        )
                    continue
                neighbor_tile = self.get_tile_info(neighbor)
                tile_score = (1.0 if neighbor_tile.name == "path" else 3.0) / neighbor_tile.movement_speed_factor
                tentative_g_score = g_score[current] + tile_score
                if verbose:
                    print(
                        f"\t\t\tin compute_npc_path; tentative_g_score={tentative_g_score}",
                        flush=True,
                    )
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    tentative_f_score = tentative_g_score + h(neighbor)
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_f_score
                    heappush(open_set, (tentative_f_score, neighbor))

        if goal in came_from:
            # Reconstruct the path
            reverse_path = []
            while goal != start:
                reverse_path.append(goal)
                goal = came_from[goal]
            return list(reversed(reverse_path))
        elif verbose:
            print(f"in compute_npc_path; goal is not in came_from={came_from}", flush=True)

        # No path exists
        return None
