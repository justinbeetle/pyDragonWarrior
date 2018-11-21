#!/usr/bin/env python

from typing import List, Optional, Tuple

import pygame


def get_events() -> List[pygame.event.Event]:
    # Translate joystick events to keyboard events
    events: List[pygame.event.Event] = pygame.event.get()

    # Process joystick taking into account keyboard repeat settings
    is_keyboard_repeat_enabled = pygame.key.get_repeat() != (0, 0)

    # Generate key down events from a joystick hat for the case were repeats are enabled
    if is_keyboard_repeat_enabled:
        for joystick_id in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(joystick_id)
            if not joystick.get_init():
                continue
            for hat_id in range(joystick.get_numhats()):
                event = get_event_for_joystick_hat_position(joystick.get_hat(hat_id))
                if event is not None:
                    events.append(event)

    # Translate joystick events to keyboard events
    for e in events:
        event = None
        event_dict = {}
        if e.type == pygame.JOYBUTTONDOWN:
            if e.button == 0:
                event_dict['key'] = pygame.K_RETURN
                event = pygame.event.Event(pygame.KEYDOWN, event_dict)
            elif e.button == 1:
                event_dict['key'] = pygame.K_SPACE
                event = pygame.event.Event(pygame.KEYDOWN, event_dict)
        elif e.type == pygame.JOYHATMOTION and not is_keyboard_repeat_enabled:
            event = get_event_for_joystick_hat_position(e.value)
        if event is not None:
            events.append(event)

    return events


def get_event_for_joystick_hat_position(hat_position: Tuple[int, int]) -> Optional[pygame.event.Event]:
    event = None
    event_dict = {}
    if hat_position == (0, -1):
        event_dict['key'] = pygame.K_DOWN
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
    elif hat_position == (0, 1):
        event_dict['key'] = pygame.K_UP
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
    elif hat_position == (-1, 0):
        event_dict['key'] = pygame.K_LEFT
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
    elif hat_position == (1, 0):
        event_dict['key'] = pygame.K_RIGHT
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
    return event
