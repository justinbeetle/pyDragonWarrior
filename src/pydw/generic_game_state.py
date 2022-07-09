#!/usr/bin/env python

import pygame


class GenericGameState:
    def __init__(self, screen: pygame.surface.Surface) -> None:
        self.screen = screen
        self.is_running = True
