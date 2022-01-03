#!/usr/bin/env python

from typing import Dict, List, Optional, Tuple

import pygame

# Mapping from unique instance IDs to initialized joysticks/gamepads
joysticks: Dict[int, pygame.joystick.Joystick] = {}


def setup_joystick() -> bool:
    if pygame.joystick.get_count() != len(joysticks):
        print('pygame.joystick.get_count() =', pygame.joystick.get_count(), flush=True)

    # Remove uninitialized joysticks
    for instance_id, joystick in joysticks.copy().items():
        # Determine if the joystick is still present
        found_joystick = False
        for joystickId in range(pygame.joystick.get_count()):
            if pygame.joystick.Joystick(joystickId).get_instance_id() == instance_id:
                found_joystick = True
                break

        # Remove uninitialized joysticks
        if not found_joystick:
            print(f'Joystick {instance_id} was uninitialized', flush=True)
            joystick.quit()
            del joysticks[instance_id]

    # Add new joysticks
    for joystickId in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(joystickId)
        instance_id = joystick.get_instance_id()

        # Skip previously initialized joysticks
        if instance_id in joysticks:
            continue

        print('joystick.get_instance_id() =', instance_id, flush=True)
        print('joystick.get_id() =', joystick.get_id(), flush=True)
        print('joystick.get_name() =', joystick.get_name(), flush=True)
        # if joystick.get_name() == 'Controller (Xbox One For Windows)':
        print('Initializing joystick...', flush=True)
        joystick.init()
        joysticks[instance_id] = joystick

    return len(joysticks) > 0


def get_events(is_keyboard_repeat_enabled: bool=False, translate_wasd_to_uldr: bool=True) -> List[pygame.event.Event]:
    # Allow joysticks to be rediscovered if they get uninitialized.
    setup_joystick()

    events: List[pygame.event.Event] = []
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            # Convert WASD to Up/Left/Down/Right
            if translate_wasd_to_uldr:
                if pygame.K_w == event.key:
                    event.__dict__['key'] = pygame.K_UP
                elif pygame.K_a == event.key:
                    event.__dict__['key'] = pygame.K_LEFT
                elif pygame.K_s == event.key:
                    event.__dict__['key'] = pygame.K_DOWN
                elif pygame.K_d == event.key:
                    event.__dict__['key'] = pygame.K_RIGHT
            if pygame.K_KP_ENTER == event.key:
                event.__dict__['key'] = pygame.K_RETURN

        elif event.type == pygame.ACTIVEEVENT and 'gain' in event.__dict__ and event.gain:
            print('Detected gain focus event', flush=True)

        # Translate joystick events to keyboard events
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
            elif event.button == 1:
                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            elif event.button == 6:
                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
            elif event.button == 7:
                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_F1})
            else:
                # Map all other buttons to an unused key
                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_F15})

        elif event.type == pygame.JOYHATMOTION:
            joystick_hat_event = get_event_for_joystick_hat_position(event.value)
            if joystick_hat_event is None:
                continue
            event = joystick_hat_event

        events.append(event)

    if is_keyboard_repeat_enabled:
        # Generate key down events from a joystick hat for the case where repeats are enabled
        for joystick_id in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(joystick_id)
            if not joystick.get_init():
                continue
            for hat_id in range(joystick.get_numhats()):
                joystick_hat_event = get_event_for_joystick_hat_position(joystick.get_hat(hat_id))
                if joystick_hat_event is not None:
                    add_event_if_not_duplicate(events, joystick_hat_event)

        # Generate key down events for pressed keys
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP] or (translate_wasd_to_uldr and pressed[pygame.K_w]):
            add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}))
        elif pressed[pygame.K_DOWN] or (translate_wasd_to_uldr and pressed[pygame.K_s]):
            add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}))
        if pressed[pygame.K_LEFT] or (translate_wasd_to_uldr and pressed[pygame.K_a]):
            add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}))
        elif pressed[pygame.K_RIGHT] or (translate_wasd_to_uldr and pressed[pygame.K_d]):
            add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}))

    return events


def add_event_if_not_duplicate(events: List[pygame.event.Event], event: pygame.event.Event) -> None:
    if pygame.KEYDOWN == event.type:
        for existing_event in events:
            if pygame.KEYDOWN == existing_event.type and existing_event.key == event.key:
                # A KEYDOWN event of this type is already in events
                # print("Not adding event as a duplicate is already present", event, flush=True)
                return
    events.append(event)


def clear_events() -> None:
    get_events()


def get_event_for_joystick_hat_position(hat_position: Tuple[float, float]) -> Optional[pygame.event.Event]:
    event = None
    if hat_position == (0, -1):
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})
    elif hat_position == (0, 1):
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})
    elif hat_position == (-1, 0):
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
    elif hat_position == (1, 0):
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT})

    # if event is not None:
    #    print("Adding KEYDOWN event for joystick", pygame.key.name(event.key), flush=True)

    return event


def main() -> None:
    # Initialize pygame
    print('Initialize pygame...', flush=True)
    pygame.init()
    setup_joystick()

    # Setup to draw maps
    print('Setup to draw maps...', flush=True)
    win_size_pixels = (250, 250)
    pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)

    print('pygame.display.Info() =', pygame.display.Info(), flush=True)
    print('pygame.display.get_wm_info() =', pygame.display.get_wm_info(), flush=True)

    # Iterate through and render the different maps
    is_running = True
    while is_running:
        # Process events
        print('Getting events...', flush=True)
        events = get_events(True)

        for event in events:
            print('event =', event, flush=True)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                is_running = False

        pygame.time.Clock().tick(5)

    # Exit the game
    pygame.joystick.quit()
    pygame.quit()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import sys
        import traceback
        print(traceback.format_exception(None,  # <- type(e) by docs, but ignored
                                         e,
                                         e.__traceback__),
              file=sys.stderr, flush=True)
        traceback.print_exc()