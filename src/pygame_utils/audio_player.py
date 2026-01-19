#!/usr/bin/env python

"""Module defining AudioPlayer utility for playing music and sound tracks."""

import atexit
import concurrent.futures
import logging
import os.path
import threading
from typing import NamedTuple, Optional, Union

import pygame.mixer
import pygame.time

from generic_utils.download_file import download_file
from pygame_utils import game_events

logger = logging.getLogger(__name__)


class MusicTrack(NamedTuple):
    """Data type defining a music track, how it should be played, and where it can be found.

    The music defaults to be played from the start but file_start1_sec can specify an initial
    time offset into the track to start playing the music (only applicable if played as music,
    not as a sound).

    The music can be played differently between the first and subsequent loops.  Where desired,
    file_path2 and file_start2_sec specify how the music is played in subsequent loops while
    file_path1 and file_start1_sec apply to the first loop."""

    name: str
    file_path1: str
    file_path2: Optional[str] = None
    link1: Optional[str] = None
    link2: Optional[str] = None
    file_start1_sec: float = 0.0
    file_start2_sec: float = 0.0
    credits: str = "Uncredited"
    package_name: Optional[str] = None
    package_link: Optional[str] = None

    def is_file1_present(self) -> bool:
        """Return flag indicating if file1 is present."""
        return os.path.exists(self.file_path1)

    def is_file2_present(self) -> bool:
        """Return flag indicating if file2 is present."""
        return self.file_path2 is None or os.path.exists(self.file_path2)

    def is_track_present(self) -> bool:
        """Return flag indicating if the track is present."""
        return self.is_file1_present() and self.is_file2_present()

    def stage_track(self) -> bool:
        """Attempt to download a track if it is not available.  Return a flag indicating if the track is present."""
        if self.is_track_present():
            return True

        # Try to download the track
        if not self.is_file1_present() and self.link1 is not None:
            download_file(self.link1, self.file_path1)
        if not self.is_file2_present() and self.link2 is not None and self.file_path2 is not None:
            download_file(self.link2, self.file_path2)

        if self.is_track_present():
            return True

        # Try to download the package of tracks
        if self.package_name is not None and self.package_link is not None:
            download_file(self.package_link, self.package_name)

        if not self.is_file1_present():
            if not self.is_file2_present():
                logger.error("Failed to stage %s and %s", self.file_path1, self.file_path2)
            else:
                logger.error("Failed to stage %s", self.file_path1)
            return False
        if not self.is_file2_present():
            logger.error("Failed to stage %s", self.file_path2)
            return False

        return True

    def get_required_download_info(self) -> set[tuple[str, str]]:
        """Get a set of tuples of source URL and destination filepath for the files to download for this track."""
        required_download_info = set()
        if not self.is_file1_present():
            if self.link1 is not None:
                required_download_info.add((self.link1, self.file_path1))
            elif self.package_link is not None and self.package_name is not None:
                required_download_info.add((self.package_link, self.package_name))
        if not self.is_file2_present():
            if self.link2 is not None and self.file_path2 is not None:
                required_download_info.add((self.link2, self.file_path2))
            elif self.package_link is not None and self.package_name is not None:
                required_download_info.add((self.package_link, self.package_name))
        return required_download_info


class SoundTrack(NamedTuple):
    """Data type defining a sound track and where it can be found."""

    name: str
    file_path: str
    link: Optional[str] = None
    credits: str = "Uncredited"
    package_name: Optional[str] = None
    package_link: Optional[str] = None

    def is_track_present(self) -> bool:
        """Return flag indicating if the track is present."""
        return os.path.exists(self.file_path)

    def stage_track(self) -> bool:
        """Attempt to download a track if it is not available.  Return a flag indicating if the track is present."""
        if self.is_track_present():
            return True

        # Try to download the track
        if self.link is not None:
            download_file(self.link, self.file_path)

        if self.is_track_present():
            return True

        # Try to download the package of tracks
        if self.package_name is not None and self.package_link is not None:
            download_file(self.package_link, self.package_name)

        if not self.is_track_present():
            logger.error("Failed to stage %s", self.file_path)
            return False

        return True

    def get_required_download_info(self) -> set[tuple[str, str]]:
        """Get a set of tuples of source URL and destination filepath for the files to download for this track."""
        required_download_info = set()
        if not self.is_track_present():
            if self.link is not None:
                required_download_info.add((self.link, self.file_path))
            elif self.package_link is not None and self.package_name is not None:
                required_download_info.add((self.package_link, self.package_name))
        return required_download_info


class AudioPlayer:
    """Multi-threaded singleton utility for playing music and sound tracks."""

    _instance: Optional["AudioPlayer"] = None

    def __new__(cls) -> "AudioPlayer":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            atexit.register(cls._instance.terminate)
        return cls._instance

    def __init__(self) -> None:
        # Choose a desired audio format
        pygame.mixer.init(11025)  # Raises exception on fail
        pygame.mixer.set_num_channels(32)

        self.music_path = "./"
        self.name_to_music_track_mapping: dict[str, list[MusicTrack]] = {}
        self.sound_path = "./"
        self.name_to_sound_track_mapping: dict[str, list[SoundTrack]] = {}
        self.music_rel_file_path1: Optional[str] = None
        self.music_rel_file_path2: Optional[str] = None
        self.music_file_start1_sec = 0.0
        self.music_file_start2_sec = 0.0
        self.running = True
        self.sounds: dict[str, Optional[pygame.mixer.Sound]] = {}
        self.music_thread_lock = threading.RLock()
        self.music_thread = threading.Thread(target=self.__music_thread)
        self.music_thread.start()
        self.channel_end_event_type = pygame.event.custom_type()

    def set_music_path(self, music_path: str) -> None:
        """Set the base path for music files."""
        self.music_path = music_path

    def add_music_tracks(self, name_to_track_mapping: dict[str, MusicTrack]) -> None:
        """Add music tracks to the player."""
        for name in name_to_track_mapping:
            if name not in self.name_to_music_track_mapping:
                self.name_to_music_track_mapping[name] = []
            self.name_to_music_track_mapping[name].append(name_to_track_mapping[name])

    def get_music_tracks(self) -> dict[str, list[MusicTrack]]:
        """Get the music trasks added to the player."""
        return self.name_to_music_track_mapping

    def set_sound_path(self, sound_path: str) -> None:
        """Set the base path for sound files."""
        self.sound_path = sound_path

    def add_sound_tracks(self, name_to_track_mapping: dict[str, SoundTrack]) -> None:
        """Add sound tracks to the player."""
        for name in name_to_track_mapping:
            if name not in self.name_to_sound_track_mapping:
                self.name_to_sound_track_mapping[name] = []
            self.name_to_sound_track_mapping[name].append(name_to_track_mapping[name])

    def get_sound_tracks(self) -> dict[str, list[SoundTrack]]:
        """Get the sound trasks added to the player."""
        return self.name_to_sound_track_mapping

    def stage_music_track(self, track_name: str) -> Optional[MusicTrack]:
        """Stage a music track so it is ready to be played.  This includes downloading the track if needed.
        On success, return the track.  Else remove it from the internal map."""
        if track_name not in self.name_to_music_track_mapping:
            return None
        tracks = self.name_to_music_track_mapping[track_name]
        for track in tracks[:]:
            if not track.stage_track():
                tracks.remove(track)
                continue
        if not tracks:
            logger.error("Failed to stage all possible music tracks with name %s", track_name)
            return None
        return tracks[0]

    def stage_sound_track(self, track_name: str) -> Optional[SoundTrack]:
        """Stage a sound track so it is ready to be played.  This includes downloading the track if needed.
        On success, return the track.  Else remove it from the internal map."""
        if track_name not in self.name_to_sound_track_mapping:
            return None
        tracks = self.name_to_sound_track_mapping[track_name]
        for track in tracks[:]:
            if not track.stage_track():
                tracks.remove(track)
                continue
        if not tracks:
            logger.error("Failed to stage all possible music tracks with name %s", track_name)
            return None
        return tracks[0]

    def stage_all_tracks(self) -> None:
        """Stage all sound and music tracks so they are ready to be played.  This work is down on thread
        pools to speed the intial loading time."""
        # First determine everything that needs to be downloaded.  Use a set to avoid duplicate downloads
        required_download_info = set()
        for music_track_mapping in self.name_to_music_track_mapping.values():
            for music_track in music_track_mapping:
                required_download_info |= music_track.get_required_download_info()
        for sound_track_mapping in self.name_to_sound_track_mapping.values():
            for sound_track in sound_track_mapping:
                required_download_info |= sound_track.get_required_download_info()

        # Perform all the downloads using a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for url, filepath in required_download_info:
                executor.submit(download_file, url, filepath)

        # After the downloads, cleanup the name to track mappings
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for track_name in self.name_to_music_track_mapping:
                self.stage_music_track(track_name)
            for track_name in self.name_to_sound_track_mapping:
                self.stage_sound_track(track_name)

    def play_music(self, track: Union[MusicTrack, str], interrupt: bool = False) -> None:
        """Play a music track on a persistent background music thread.  The music is played
        via pygame.mixer.music, which can stream a single music file at a time.  Nominally
        (when interrupt is false) the music loops until stop_music is terminate  is called
        or play_music is called again to play different music.  If interrupt is true and the
        music track doesn't set both file paths, the new music will interrupt the playing
        music and play one time and then the original music will resume."""
        if isinstance(track, str):
            music_track = self.stage_music_track(track)
        else:
            music_track = track

        if music_track:
            self.play_music_from_filepath(
                music_track.file_path1,
                music_track.file_path2,
                interrupt,
                music_track.file_start1_sec,
                music_track.file_start2_sec,
            )

    def play_music_from_filepath(
        self,
        music_rel_file_path1: str,
        music_rel_file_path2: Optional[str] = None,
        interrupt: bool = False,
        music_file_start1_sec: float = 0.0,
        music_file_start2_sec: float = 0.0,
    ) -> None:
        """Same as play_music, but plays from filepaths instead of a music track."""
        with self.music_thread_lock:
            self.music_rel_file_path1 = music_rel_file_path1
            self.music_file_start1_sec = music_file_start1_sec
            if music_rel_file_path2 is not None:
                self.music_rel_file_path2 = music_rel_file_path2
                self.music_file_start2_sec = music_file_start2_sec
            elif not interrupt:
                self.music_rel_file_path2 = music_rel_file_path1
                self.music_file_start2_sec = music_file_start1_sec

            if self.music_rel_file_path1 is not None and not os.path.exists(self.music_rel_file_path1):
                self.music_rel_file_path1 = os.path.join(self.music_path, self.music_rel_file_path1)

            if self.music_rel_file_path2 is not None and not os.path.exists(self.music_rel_file_path2):
                self.music_rel_file_path2 = os.path.join(self.music_path, self.music_rel_file_path2)

    def stop_music(self) -> None:
        """Stop the currently playing music, if any."""
        self.music_rel_file_path1 = self.music_rel_file_path2 = None

    def __music_thread(self) -> None:
        """Entry point for the persistent background music thread which plays the current
        music track, if any, until the the player is terminated."""
        first_time = True
        current_music_rel_file_path1: Optional[str] = None
        current_music_rel_file_path2: Optional[str] = None
        failed_to_play = set()
        while self.running:
            # TODO: Switch to a more responsive approach which is not polling based

            with self.music_thread_lock:
                if (
                    current_music_rel_file_path1 != self.music_rel_file_path1
                    or current_music_rel_file_path2 != self.music_rel_file_path2
                ):
                    current_music_rel_file_path1 = self.music_rel_file_path1
                    current_music_rel_file_path2 = self.music_rel_file_path2
                    first_time = True

                if self.music_rel_file_path1 is not None and self.music_rel_file_path2 is not None:
                    # load the music
                    if first_time:
                        first_time = False
                    else:
                        self.music_rel_file_path1 = self.music_rel_file_path2
                        self.music_file_start1_sec = self.music_file_start2_sec

                    try:
                        pygame.mixer.music.load(self.music_rel_file_path1)

                        # start playing
                        pygame.mixer.music.play(start=self.music_file_start1_sec)

                        # poll until finished
                        while (
                            self.running
                            and pygame.mixer.music.get_busy()
                            and current_music_rel_file_path1 == self.music_rel_file_path1
                            and current_music_rel_file_path2 == self.music_rel_file_path2
                        ):
                            # still playing and not changed
                            self.music_thread_lock.release()
                            pygame.time.wait(100)
                            self.music_thread_lock.acquire()

                        pygame.mixer.music.stop()
                    except Exception:
                        if self.music_rel_file_path1 not in failed_to_play:
                            logger.exception("Failed to load %s", self.music_rel_file_path1)
                            failed_to_play.add(self.music_rel_file_path1)

            pygame.time.wait(100)

    def play_sound(
        self,
        track: Union[MusicTrack, SoundTrack, str],
        from_music_tracks_first: bool = False,
        is_blocking: bool = False,
    ) -> None:
        """Play a sound or music track once.  The file is played via pygame.mixer.Sound,
        where the entire file needs to be loaded into memory as opposed to being streamed
        like by pygame.mixer.music used for play_music, but multipe sounds can be played
        concurrently.  The sound is played on a transient background sound thread when
        is_blocking is false and on the current thread when is_blocking is true.  When
        playing a music track, the attributes file_path2, file_start1_sec, and file_start2_sec
        of the music track are ignored as they are only supported for the play_music method."""
        # Can play either a sound or music track as a sound track - it just won't loop.
        file_path = None
        if isinstance(track, SoundTrack):
            file_path = track.file_path
        elif isinstance(track, MusicTrack):
            file_path = track.file_path1
        else:
            if from_music_tracks_first:
                music_track = self.stage_music_track(track)
                if music_track is not None:
                    file_path = music_track.file_path1
            else:
                sound_track = self.stage_sound_track(track)
                if sound_track is not None:
                    file_path = sound_track.file_path

            if file_path is None:
                if from_music_tracks_first:
                    sound_track = self.stage_sound_track(track)
                    if sound_track is not None:
                        file_path = sound_track.file_path
                else:
                    music_track = self.stage_music_track(track)
                    if music_track is not None:
                        file_path = music_track.file_path1

        if file_path is not None:
            self.play_sound_from_filepath(file_path, is_blocking=is_blocking)

    def play_sound_from_filepath(
        self,
        file_path: str,
        is_blocking: bool = False,
    ) -> None:
        """Same as play_music, but plays from filepaths instead of a sound or music track."""
        if not os.path.exists(file_path):
            file_path = os.path.join(self.sound_path, file_path)

        if is_blocking:
            self.__sound_thread(file_path, is_blocking)
        else:
            sound_thread = threading.Thread(target=self.__sound_thread, args=[file_path])
            sound_thread.start()

    def __sound_thread(self, sound_file_path: str, is_blocking: bool = False) -> None:
        """Entry point for the transient background sound threads which play a sound
        file one time."""
        # Load the sound if not previously loaded
        if sound_file_path not in self.sounds:
            try:
                self.sounds[sound_file_path] = pygame.mixer.Sound(sound_file_path)
            except Exception:
                logger.exception("Failed to load %s", sound_file_path)
                self.sounds[sound_file_path] = None

        # Play the sound if loaded
        sound = self.sounds[sound_file_path]
        if sound is not None:
            channel = sound.play()

            # Optionally wait for the sound to complete
            if is_blocking:
                channel.set_endevent(self.channel_end_event_type)
                end_event_received = False
                while channel.get_busy() and not end_event_received:
                    for event in game_events.get_events():
                        if self.channel_end_event_type == event.type:
                            end_event_received = True
                            break
                    if channel.get_busy() and not end_event_received:
                        pygame.time.wait(50)
                channel.set_endevent()

    def terminate(self) -> None:
        """Terminate the audio player, which stops and joins with the persistent
        background thread for playing music."""
        if self.running:
            self.running = False
            self.music_thread.join()
            pygame.mixer.quit()


def main() -> None:
    """Entry point for simple AudioPlayer demo program."""

    # Initialize the music player
    audio_player = AudioPlayer()
    base_path = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    audio_player.set_music_path(os.path.join(base_path, "data", "music", "dw1"))
    audio_player.set_sound_path(os.path.join(base_path, "data", "sounds", "dw1"))

    print("Play Overture...", flush=True)
    audio_player.play_music_from_filepath("01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg")
    pygame.time.wait(1000)
    print("Play sound...", flush=True)
    audio_player.play_sound_from_filepath("Dragon Warrior [Dragon Quest] SFX (1).wav")
    pygame.time.wait(1000)

    print("Stop music...", flush=True)
    audio_player.stop_music()
    pygame.time.wait(1000)
    print("Play sound...", flush=True)
    audio_player.play_sound_from_filepath("Dragon Warrior [Dragon Quest] SFX (1).wav")
    pygame.time.wait(1000)

    print("Play Overture...", flush=True)
    audio_player.play_music_from_filepath("01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg")
    pygame.time.wait(1000)
    print("Play sound...", flush=True)
    audio_player.play_sound_from_filepath("Dragon Warrior [Dragon Quest] SFX (1).wav")
    pygame.time.wait(1000)

    print("Terminate...", flush=True)
    audio_player.terminate()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import sys
        import traceback

        print(
            traceback.format_exception(None, e, e.__traceback__),  # <- type(e) by docs, but ignored
            file=sys.stderr,
            flush=True,
        )
