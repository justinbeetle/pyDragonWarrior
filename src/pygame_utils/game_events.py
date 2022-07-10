#!/usr/bin/env python

from typing import Dict, List, Optional, Tuple

import pygame

# Mapping from unique instance IDs to initialized joysticks/gamepads
joysticks: Dict[int, pygame.joystick.Joystick] = {}


def setup_joystick() -> bool:
    """ Detect joysticks/gamepads as they become available and configure them for use

    :return: Flag indicating if any joysticks are available
    """

    if pygame.joystick.get_count() != len(joysticks):
        print('pygame.joystick.get_count() =', pygame.joystick.get_count(), flush=True)

    # Remove uninitialized joysticks
    for instance_id, joystick in joysticks.copy().items():
        # Determine if the joystick is still present
        found_joystick = False
        for joystick_id in range(pygame.joystick.get_count()):
            if pygame.joystick.Joystick(joystick_id).get_instance_id() == instance_id:
                found_joystick = True
                break

        # Remove uninitialized joysticks
        if not found_joystick:
            print(f'Joystick {instance_id} was uninitialized', flush=True)
            joystick.quit()
            del joysticks[instance_id]

    # Add new joysticks
    for joystick_id in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(joystick_id)
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


def get_events(is_keyboard_repeat_enabled: bool = False,
               translate_wasd_to_uldr: bool = True,
               translate_e_to_enter: bool = True) -> List[pygame.event.Event]:
    """ Translate both keyboard and joystick/gamepad events into a reduced set of events.

    :param is_keyboard_repeat_enabled: Allow a held key to continue generating events, defaults to False

    :param translate_wasd_to_uldr: translate events on the WASD keys to events on the UP/LEFT/DOWN/RIGHT keys, defaults
        to True

    :param translate_e_to_enter: translate events on the E key to events on the ENTER key, defaults to True

    :return: List of events
    """

    # Allow joysticks to be rediscovered if they get uninitialized.
    setup_joystick()

    events: List[pygame.event.Event] = []
    for event in pygame.event.get():
        # if event.type == pygame.ACTIVEEVENT and 'gain' in event.__dict__ and event.gain:
        #     print('Detected gain focus event', flush=True)

        # Drop mouse events
        if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]:
            continue

        # Remap keyboard events
        event = _remap_keyboard_event(translate_wasd_to_uldr, translate_e_to_enter, event)

        # Remap joystick/gamepad events
        remapped_event = _remap_joystick_event(event)

        if remapped_event is not None:
            _add_event_if_not_duplicate(events, remapped_event)

    if is_keyboard_repeat_enabled:
        # Generate key down events for pressed keys
        _add_keyboard_keydown_events(translate_wasd_to_uldr, events)

        # Generate key down events for joystick/gamepad hat
        _add_joystick_keydown_events(events)

    return events


def clear_events() -> None:
    """ Clear the event queue
    """

    # Allow joysticks to be rediscovered if they get uninitialized.
    setup_joystick()

    pygame.event.clear()


def _remap_keyboard_event(translate_wasd_to_uldr: bool,
                          translate_e_to_enter: bool,
                          event: pygame.event.Event) -> pygame.event.Event:
    """ Perform remapping of keydown events to change which key is pressed to support multiple keys for the same actions

    FUTURE: Potentially implement keybinding support here
    """

    # Sometimes the KEYDOWN events seems to stop while TEXTINPUT events continue.  Translate TEXTINPUT event to KEYDOWN
    # events where possible to better handle instances of missing KEYDOWN events.
    if pygame.TEXTINPUT == event.type:
        try:
            # orig_event = event
            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.key.key_code(event.text), 'unicode': event.text})
            # print(f'Translated {orig_event} to {event}', flush=True)
        except:
            print(f'Failed to translate {event} to a KEYDOWN event', flush=True)

    if pygame.KEYDOWN == event.type:
        if translate_wasd_to_uldr:
            # Convert WASD to Up/Left/Down/Right
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
        elif pygame.K_e == event.key:
            if translate_e_to_enter:
                event.__dict__['key'] = pygame.K_RETURN
        elif pygame.K_q == event.key:
            event.__dict__['key'] = pygame.K_SPACE

    return event


def _remap_joystick_event(event: pygame.event.Event) -> Optional[pygame.event.Event]:
    """ Translate joystick events to keyboard events
    """
    remapped_event: Optional[pygame.event.Event] = event
    if pygame.JOYBUTTONDOWN == event.type:
        if event.button == 0:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        elif event.button == 1:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
        elif event.button == 6:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        elif event.button == 7:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_F1})
        else:
            remapped_event = None
    elif pygame.JOYHATMOTION == event.type:
        remapped_event = _get_event_for_joystick_hat_position(event.value)
    elif event.type in [pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYBUTTONUP]:
        remapped_event = None

    return remapped_event


def _add_keyboard_keydown_events(translate_wasd_to_uldr: bool, events: List[pygame.event.Event]) -> None:
    """ Generate key down events from pressed keys
    """
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP] or (translate_wasd_to_uldr and pressed[pygame.K_w]):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}))
    elif pressed[pygame.K_DOWN] or (translate_wasd_to_uldr and pressed[pygame.K_s]):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}))
    if pressed[pygame.K_LEFT] or (translate_wasd_to_uldr and pressed[pygame.K_a]):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}))
    elif pressed[pygame.K_RIGHT] or (translate_wasd_to_uldr and pressed[pygame.K_d]):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}))


def _add_joystick_keydown_events(events: List[pygame.event.Event]) -> None:
    """ Generate key down events from pressed joystick hat
    """
    for joystick_id in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(joystick_id)
        if not joystick.get_init():
            continue
        for hat_id in range(joystick.get_numhats()):
            hat_position = joystick.get_hat(hat_id)
            if -1 == hat_position[0]:
                _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}))
            elif 1 == hat_position[0]:
                _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}))

            if -1 == hat_position[1]:
                _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}))
            elif 1 == hat_position[1]:
                _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}))


def _add_event_if_not_duplicate(events: List[pygame.event.Event], event: pygame.event.Event) -> None:
    """ Append event to events unless doing so would result in multiple KEYDOWN events for a single key
    """
    if pygame.KEYDOWN == event.type:
        for existing_event in events:
            if pygame.KEYDOWN == existing_event.type and existing_event.key == event.key:
                # A KEYDOWN event of this type is already in events
                # print('Not adding event as a duplicate is already present:', event, flush=True)
                return
    events.append(event)


def _get_event_for_joystick_hat_position(hat_position: Tuple[float, float]) -> Optional[pygame.event.Event]:
    """ Generate key down events from pressed joystick hat - doesn't support one event becoming multiple events
    """
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

    # Setup display
    print('Setup to display to allow for cursor event...', flush=True)
    win_size_pixels = (250, 250)
    pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)

    print('pygame.display.Info() =', pygame.display.Info(), flush=True)
    print('pygame.display.get_wm_info() =', pygame.display.get_wm_info(), flush=True)

    is_running = True
    while is_running:
        # Process events
        print('Getting events...', flush=True)
        events = get_events(True)

        for event in events:
            print('event =', event, flush=True)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                is_running = False

        pygame.time.wait(200)

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
