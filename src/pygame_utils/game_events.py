#!/usr/bin/env python

"""Module defining methods wrapping pygame.event and pygame.joystick"""

import logging
from typing import Callable, Optional

import pygame

logger = logging.getLogger(__name__)

# Mapping from unique instance IDs to initialized joysticks/gamepads
joysticks: dict[int, pygame.joystick.JoystickType] = {}

# Optional event handlers
focus_gain_handler: Optional[Callable[[], None]] = None
window_resize_handler: Optional[Callable[[], None]] = None


def is_pygame_ce() -> bool:
    """Return true if running in pygame-ce, else false if running in pygame."""
    return getattr(pygame, "IS_CE", False)


def setup_joystick() -> bool:
    """Detect joysticks/gamepads as they become available and configure them for use

    :return: Flag indicating if any joysticks are available
    """

    if pygame.joystick.get_count() != len(joysticks):
        logger.debug("pygame.joystick.get_count() = %s", pygame.joystick.get_count())

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
            logger.debug("Joystick %s was uninitialized", instance_id)
            joystick.quit()
            del joysticks[instance_id]

    # Add new joysticks
    for joystick_id in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(joystick_id)
        instance_id = joystick.get_instance_id()

        # Skip previously initialized joysticks
        if instance_id in joysticks:
            continue

        logger.debug("joystick.get_instance_id() = %s", instance_id)
        logger.debug("joystick.get_id() = %s", joystick.get_id())
        logger.debug("joystick.get_name() = %s", joystick.get_name())
        logger.debug("Initializing joystick...")
        joystick.init()
        joysticks[instance_id] = joystick

    return len(joysticks) > 0


def set_focus_gain_handler(handler_method: Optional[Callable[[], None]]) -> None:
    """Set (or unset) the optional focus gain handler."""
    # pygame-ce appears to have fixed this issue, so disabling this handler for the time being
    if not is_pygame_ce():
        global focus_gain_handler
        focus_gain_handler = handler_method


def set_window_resize_handler(handler_method: Optional[Callable[[], None]]) -> None:
    """Set (or unset) the optional window resize handler."""
    # pygame-ce appears to have fixed this issue, so disabling this handler for the time being
    if not is_pygame_ce():
        global window_resize_handler
        window_resize_handler = handler_method


def get_events(
    add_keydown_events_for_pressed_uldr_keys: bool = False,
    translate_wasd_to_uldr: bool = True,
    translate_e_to_enter: bool = True,
) -> list[pygame.event.Event]:
    """Wrapper for pygame.event.get() translating keyboard and joystick/gamepad events into a reduced set of events.

    :param add_keydown_events_for_pressed_uldr_keys: If true, disable key repeat in favor of adding keydown events
        for pressed keys which should be translated to the UP/LEFT/DOWN/RIGHT keys.

    :param translate_wasd_to_uldr: If true, translate events on the WASD keys to events on the UP/LEFT/DOWN/RIGHT keys.

    :param translate_e_to_enter: If true, translate events on the E key to events on the ENTER key.

    :return: list of events
    """

    # Allow joysticks to be rediscovered if they get uninitialized.
    setup_joystick()

    # Determine desired key repeat settings and set them if changed
    if add_keydown_events_for_pressed_uldr_keys:
        desired_key_repeat_delay_ms = 0
        desired_key_repeat_interval_ms = 0
    else:
        desired_key_repeat_delay_ms = 500
        desired_key_repeat_interval_ms = 33
    key_repeat_delay_ms, key_repeat_interval_ms = pygame.key.get_repeat()
    if desired_key_repeat_delay_ms != key_repeat_delay_ms or desired_key_repeat_interval_ms != key_repeat_interval_ms:
        logger.debug(
            "Changing repeat_delay_ms from %s to %s; key_repeat_interval_ms from %s to %s",
            key_repeat_delay_ms,
            desired_key_repeat_delay_ms,
            key_repeat_interval_ms,
            desired_key_repeat_interval_ms,
        )
        pygame.key.set_repeat(desired_key_repeat_delay_ms, desired_key_repeat_interval_ms)

    events: list[pygame.event.Event] = []
    for event in pygame.event.get():
        # Drop mouse events
        if event.type in [
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEWHEEL,
        ]:
            continue

        # Drop key up events
        if event.type in [pygame.KEYUP]:
            continue

        # Optionally handle focus gained events
        if event.type == pygame.ACTIVEEVENT and "gain" in event.__dict__ and event.gain:
            # logging.debug("Detected gain focus event")
            if focus_gain_handler:
                focus_gain_handler()

        # Optionally window size changed events
        if event.type == pygame.WINDOWSIZECHANGED:
            # logging.debug("Detected window size changed event")
            if window_resize_handler:
                window_resize_handler()

        # logging.debug("event before remapping: %s", event)

        # Remap keyboard events
        remapped_event = _remap_keyboard_event(translate_wasd_to_uldr, translate_e_to_enter, event)

        # Remap joystick/gamepad events
        if remapped_event is not None:
            remapped_event = _remap_joystick_event(remapped_event)

        # logging.debug("event after remapping: %s", remapped_event)

        if remapped_event is not None:
            _add_event_if_not_duplicate(events, remapped_event)

    if add_keydown_events_for_pressed_uldr_keys:
        # Generate key down events for pressed keys
        _add_keyboard_keydown_events_for_pressed_uldr_keys(translate_wasd_to_uldr, events)

        # Generate key down events for joystick/gamepad hat
        _add_joystick_keydown_events_for_pressed_hat(events)

    return events


def clear_events() -> None:
    """Clear the event queue"""
    pygame.event.get()


def _remap_keyboard_event(
    translate_wasd_to_uldr: bool, translate_e_to_enter: bool, event: pygame.event.Event
) -> Optional[pygame.event.Event]:
    """Perform remapping of keydown events to change which key is pressed to support multiple keys for the same actions

    FUTURE: Potentially implement keybinding support here
    """

    if pygame.KEYDOWN == event.type:
        if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
            # Optionally convert WASD events to arrow key events
            if translate_wasd_to_uldr:
                _remap_keyboard_wasd_event_to_uldr(event)
        elif event.key in [
            pygame.K_KP0,
            pygame.K_KP1,
            pygame.K_KP2,
            pygame.K_KP3,
            pygame.K_KP4,
            pygame.K_KP5,
            pygame.K_KP6,
            pygame.K_KP7,
            pygame.K_KP8,
            pygame.K_KP9,
        ]:
            # Convert number pad events to either regular number keys (with num lock) or arrow keys
            _remap_keyboard_numpad_event(event)
        elif pygame.K_KP_ENTER == event.key:
            event.__dict__["key"] = pygame.K_RETURN
        elif pygame.K_e == event.key:
            if translate_e_to_enter:
                event.__dict__["key"] = pygame.K_RETURN
        elif pygame.K_q == event.key:
            event.__dict__["key"] = pygame.K_SPACE

    return event


def _remap_keyboard_wasd_event_to_uldr(event: pygame.event.Event) -> None:
    """Convert WASD key events to arrow key events"""
    if pygame.K_w == event.key:
        event.__dict__["key"] = pygame.K_UP
    elif pygame.K_a == event.key:
        event.__dict__["key"] = pygame.K_LEFT
    elif pygame.K_s == event.key:
        event.__dict__["key"] = pygame.K_DOWN
    elif pygame.K_d == event.key:
        event.__dict__["key"] = pygame.K_RIGHT


def _remap_keyboard_numpad_event(event: pygame.event.Event) -> None:
    """Convert numpad key events to arrow or number key events"""
    num_lock = pygame.key.get_mods() & pygame.KMOD_NUM
    if num_lock:
        _remap_keyboard_numpad_event_to_numbers(event)
    else:
        _remap_keyboard_numpad_event_to_uldr(event)


def _remap_keyboard_numpad_event_to_uldr(event: pygame.event.Event) -> None:
    """Convert numpad key events to arrow key events"""
    if pygame.K_KP8 == event.key:
        event.__dict__["key"] = pygame.K_UP
    if pygame.K_KP4 == event.key:
        event.__dict__["key"] = pygame.K_LEFT
    if pygame.K_KP2 == event.key:
        event.__dict__["key"] = pygame.K_DOWN
    if pygame.K_KP6 == event.key:
        event.__dict__["key"] = pygame.K_RIGHT


def _remap_keyboard_numpad_event_to_numbers(event: pygame.event.Event) -> None:
    """Convert numpad key events to number key events"""
    if pygame.K_KP0 == event.key:
        event.__dict__["key"] = pygame.K_0
    elif pygame.K_KP1 == event.key:
        event.__dict__["key"] = pygame.K_1
    elif pygame.K_KP2 == event.key:
        event.__dict__["key"] = pygame.K_2
    elif pygame.K_KP3 == event.key:
        event.__dict__["key"] = pygame.K_3
    elif pygame.K_KP4 == event.key:
        event.__dict__["key"] = pygame.K_4
    elif pygame.K_KP5 == event.key:
        event.__dict__["key"] = pygame.K_5
    elif pygame.K_KP6 == event.key:
        event.__dict__["key"] = pygame.K_6
    elif pygame.K_KP7 == event.key:
        event.__dict__["key"] = pygame.K_7
    elif pygame.K_KP8 == event.key:
        event.__dict__["key"] = pygame.K_8
    elif pygame.K_KP9 == event.key:
        event.__dict__["key"] = pygame.K_9


def _remap_joystick_event(event: pygame.event.Event) -> Optional[pygame.event.Event]:
    """Translate joystick events to keyboard events"""
    remapped_event: Optional[pygame.event.Event] = event
    if pygame.JOYBUTTONDOWN == event.type:
        if event.button == 0:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN, "from_joystick": True})
        elif event.button == 1:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
        elif event.button == 6:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        elif event.button == 7:
            remapped_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_F1})
        else:
            remapped_event = None
    elif pygame.JOYHATMOTION == event.type:
        remapped_event = _get_event_for_joystick_hat_position(event.value)
    elif event.type in [pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYBUTTONUP]:
        remapped_event = None

    return remapped_event


def _add_keyboard_keydown_events_for_pressed_uldr_keys(
    translate_wasd_to_uldr: bool, events: list[pygame.event.Event]
) -> None:
    """Generate up, left, down, right key down events from pressed arrow keys, WASD keys when
    they should be translated to the arrow keys, or the keypad keys when numlock is off."""
    pressed = pygame.key.get_pressed()
    not_num_lock = not pygame.key.get_mods() & pygame.KMOD_NUM
    if (
        pressed[pygame.K_UP]
        or (translate_wasd_to_uldr and pressed[pygame.K_w])
        or (not_num_lock and pressed[pygame.K_KP8])
    ):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP}))
    elif (
        pressed[pygame.K_DOWN]
        or (translate_wasd_to_uldr and pressed[pygame.K_s])
        or (not_num_lock and pressed[pygame.K_KP2])
    ):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN}))
    if (
        pressed[pygame.K_LEFT]
        or (translate_wasd_to_uldr and pressed[pygame.K_a])
        or (not_num_lock and pressed[pygame.K_KP4])
    ):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT}))
    elif (
        pressed[pygame.K_RIGHT]
        or (translate_wasd_to_uldr and pressed[pygame.K_d])
        or (not_num_lock and pressed[pygame.K_KP6])
    ):
        _add_event_if_not_duplicate(events, pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT}))


def _add_joystick_keydown_events_for_pressed_hat(events: list[pygame.event.Event]) -> None:
    """Generate key down events from pressed joystick hat"""
    for joystick_id in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(joystick_id)
        if not joystick.get_init():
            continue
        for hat_id in range(joystick.get_numhats()):
            event = _get_event_for_joystick_hat_position(joystick.get_hat(hat_id))
            if event:
                _add_event_if_not_duplicate(events, event)


def _add_event_if_not_duplicate(events: list[pygame.event.Event], event: pygame.event.Event) -> None:
    """Append event to events unless doing so would result in multiple KEYDOWN events for a single key"""
    if pygame.KEYDOWN == event.type:
        for existing_event in events:
            if pygame.KEYDOWN == existing_event.type and existing_event.key == event.key:
                return
    events.append(event)


def _get_event_for_joystick_hat_position(
    hat_position: tuple[float, float],
) -> Optional[pygame.event.Event]:
    """Generate key down events from pressed joystick hat - doesn't support one event becoming multiple events"""
    event = None
    if hat_position == (0, -1):
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN})
    elif hat_position == (0, 1):
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP})
    elif hat_position == (-1, 0):
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
    elif hat_position == (1, 0):
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})

    # if event is not None:
    #    logging.debug("Adding KEYDOWN event for joystick %s", pygame.key.name(event.key))

    return event


def main() -> None:
    # TODO: Convert to example program

    import sys

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s.%(msecs)d %(levelname)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",  # ISO-8601
    )

    # Initialize pygame
    logger.info("Initialize pygame...")
    pygame.init()
    setup_joystick()

    # Setup display
    logger.info("Setup to display to allow for cursor event...")
    win_size_pixels = (250, 250)
    pygame.display.set_mode(win_size_pixels, pygame.SRCALPHA | pygame.HWSURFACE)

    logger.debug("pygame.display.Info() = %s", str(pygame.display.Info()))
    logger.debug("pygame.display.get_wm_info() = %s", pygame.display.get_wm_info())

    is_running = True
    while is_running:
        # Process events
        logger.info("Getting events...")
        events = get_events(True, translate_wasd_to_uldr=True)

        for event in events:
            logger.info("   event = %s", event)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                is_running = False

        pygame.time.wait(200)

    # Exit the game
    pygame.joystick.quit()
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
