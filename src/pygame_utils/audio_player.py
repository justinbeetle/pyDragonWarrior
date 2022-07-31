#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

import atexit
import concurrent.futures
import os.path
import pygame.mixer
import pygame.time
import threading

from generic_utils.download_file import download_file


class MusicTrack(NamedTuple):
    name: str
    file_path1: str
    file_path2: Optional[str] = None
    link1: Optional[str] = None
    link2: Optional[str] = None
    file_start1_sec: float = 0.0
    file_start2_sec: float = 0.0
    credits: str = 'Uncredited'
    package_name: Optional[str] = None
    package_link: Optional[str] = None

    def is_file1_present(self) -> bool:
        return os.path.exists(self.file_path1)

    def is_file2_present(self) -> bool:
        return self.file_path2 is None or os.path.exists(self.file_path2)

    def is_track_present(self) -> bool:
        return self.is_file1_present() and self.is_file2_present()

    def stage_track(self) -> bool:
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
                print(f'ERROR: Failed to stage {self.file_path1} and {self.file_path2}', flush=True)
            else:
                print(f'ERROR: Failed to stage {self.file_path1}', flush=True)
            return False
        elif not self.is_file2_present():
            print(f'ERROR: Failed to stage {self.file_path2}', flush=True)
            return False

        return True

    def get_required_download_info(self) -> Set[Tuple[str, str]]:
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
    name: str
    file_path: str
    link: Optional[str] = None
    credits: str = 'Uncredited'
    package_name: Optional[str] = None
    package_link: Optional[str] = None

    def is_track_present(self) -> bool:
        return os.path.exists(self.file_path)

    def stage_track(self) -> bool:
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
            return False

        return True

    def get_required_download_info(self) -> Set[Tuple[str, str]]:
        required_download_info = set()
        if not self.is_track_present():
            if self.link is not None:
                required_download_info.add((self.link, self.file_path))
            elif self.package_link is not None and self.package_name is not None:
                required_download_info.add((self.package_link, self.package_name))
        return required_download_info


class AudioPlayer:
    class __AudioPlayer:
        def __init__(self) -> None:
            # Choose a desired audio format
            pygame.mixer.init(11025)  # Raises exception on fail
            pygame.mixer.set_num_channels(32)

            self.music_path = './'
            self.name_to_music_track_mapping: Dict[str, List[MusicTrack]] = {}
            self.sound_path = './'
            self.name_to_sound_track_mapping: Dict[str, List[SoundTrack]] = {}
            self.music_rel_file_path1: Optional[str] = None
            self.music_rel_file_path2: Optional[str] = None
            self.music_file_start1_sec = 0.0
            self.music_file_start2_sec = 0.0
            self.running = True
            self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
            self.music_thread_lock = threading.RLock()
            self.music_thread = threading.Thread(target=self.__music_thread)
            self.music_thread.start()

        def __del__(self) -> None:
            self.terminate()

        def set_music_path(self, music_path: str) -> None:
            self.music_path = music_path

        def add_music_tracks(self, name_to_track_mapping: Dict[str, MusicTrack]) -> None:
            for name in name_to_track_mapping:
                if name not in self.name_to_music_track_mapping:
                    self.name_to_music_track_mapping[name] = []
                self.name_to_music_track_mapping[name].append(name_to_track_mapping[name])

        def set_sound_path(self, sound_path: str) -> None:
            self.sound_path = sound_path

        def add_sound_tracks(self, name_to_track_mapping: Dict[str, SoundTrack]) -> None:
            for name in name_to_track_mapping:
                if name not in self.name_to_sound_track_mapping:
                    self.name_to_sound_track_mapping[name] = []
                self.name_to_sound_track_mapping[name].append(name_to_track_mapping[name])

        def stage_music_track(self, track_name: str) -> Optional[MusicTrack]:
            if track_name not in self.name_to_music_track_mapping:
                return None
            tracks = self.name_to_music_track_mapping[track_name]
            for track in tracks[:]:
                if not track.stage_track():
                    tracks.remove(track)
                    continue
            if 0 == len(tracks):
                print(f'ERROR: Failed to stage all possible music tracks with name {track_name}', flush=True)
                return None
            return tracks[0]

        def stage_sound_track(self, track_name: str) -> Optional[SoundTrack]:
            if track_name not in self.name_to_sound_track_mapping:
                return None
            tracks = self.name_to_sound_track_mapping[track_name]
            for track in tracks[:]:
                if not track.stage_track():
                    tracks.remove(track)
                    continue
            if 0 == len(tracks):
                print(f'ERROR: Failed to stage all possible sound tracks with name {track_name}', flush=True)
                return None
            return tracks[0]

        def stage_all_tracks(self) -> None:
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

        def play_music(self,
                       music_rel_file_path1: str,
                       music_rel_file_path2: Optional[str] = None,
                       interrupt: bool = False,
                       music_file_start1_sec: float = 0.0,
                       music_file_start2_sec: float = 0.0) -> None:
            with self.music_thread_lock:
                music_track = self.stage_music_track(music_rel_file_path1)
                if music_track is not None:
                    self.music_rel_file_path1 = music_track.file_path1
                    self.music_file_start1_sec = music_track.file_start1_sec

                    if music_track.file_path2 is not None:
                        self.music_rel_file_path2 = music_track.file_path2
                        self.music_file_start2_sec = music_track.file_start2_sec
                    elif not interrupt:
                        self.music_rel_file_path2 = music_track.file_path1
                        self.music_file_start2_sec = music_track.file_start1_sec
                else:
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

        def __music_thread(self) -> None:
            first_time = True
            current_music_rel_file_path1: Optional[str] = None
            current_music_rel_file_path2: Optional[str] = None
            failed_to_play = set()
            while self.running:
                # TODO: Switch to a more responsive approach which is not polling based

                with self.music_thread_lock:
                    if (current_music_rel_file_path1 != self.music_rel_file_path1
                            or current_music_rel_file_path2 != self.music_rel_file_path2):
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
                            while (self.running
                                   and pygame.mixer.music.get_busy()
                                   and current_music_rel_file_path1 == self.music_rel_file_path1
                                   and current_music_rel_file_path2 == self.music_rel_file_path2):
                                # still playing and not changed
                                self.music_thread_lock.release()
                                pygame.time.wait(100)
                                self.music_thread_lock.acquire()

                            pygame.mixer.music.stop()
                        except Exception:
                            if self.music_rel_file_path1 not in failed_to_play:
                                print('ERROR: Failed to load', self.music_rel_file_path1, flush=True)
                                failed_to_play.add(self.music_rel_file_path1)
                                # import traceback
                                # traceback.print_exc()

                pygame.time.wait(100)

        def play_sound(self, sound_rel_file_path: str, from_music_tracks_first: bool = False) -> None:
            # Can play either a sound or music track as a sound track - it just won't loop.
            sound_track = self.stage_sound_track(sound_rel_file_path)
            music_track = self.stage_music_track(sound_rel_file_path)

            if (from_music_tracks_first or sound_track is None) and music_track is not None:
                sound_file_path = music_track.file_path1
            elif sound_track is not None:
                sound_file_path = sound_track.file_path
            else:
                sound_file_path = sound_rel_file_path
                if not os.path.exists(sound_file_path):
                    sound_file_path = os.path.join(self.sound_path, sound_file_path)

            sound_thread = threading.Thread(target=self.__sound_thread, args=[sound_file_path])
            sound_thread.start()

        def __sound_thread(self, sound_file_path: str) -> None:
            # Load the sound if not previously loaded
            if sound_file_path not in self.sounds:
                try:
                    self.sounds[sound_file_path] = pygame.mixer.Sound(sound_file_path)
                except Exception:
                    print('ERROR: Failed to load', sound_file_path, flush=True)
                    self.sounds[sound_file_path] = None
                    # import traceback
                    # traceback.print_exc()

            sound = self.sounds[sound_file_path]
            if sound is not None:
                sound.play()

        def stop_music(self) -> None:
            self.music_rel_file_path1 = self.music_rel_file_path2 = None

        def terminate(self) -> None:
            self.running = False
            self.music_thread.join()
            pygame.mixer.quit()

    instance: Optional[AudioPlayer.__AudioPlayer] = None

    def __init__(self) -> None:
        if not AudioPlayer.instance:
            AudioPlayer.instance = AudioPlayer.__AudioPlayer()
            atexit.register(AudioPlayer.instance.terminate)

    def set_music_path(self, music_path: str) -> None:
        if self.instance is not None:
            self.instance.set_music_path(music_path)

    def add_music_tracks(self, name_to_track_mapping: Dict[str, MusicTrack]) -> None:
        if self.instance is not None:
            self.instance.add_music_tracks(name_to_track_mapping)

    def get_music_tracks(self) -> Dict[str, List[MusicTrack]]:
        if self.instance is not None:
            return self.instance.name_to_music_track_mapping
        return {}

    def set_sound_path(self, sound_path: str) -> None:
        if self.instance is not None:
            self.instance.set_sound_path(sound_path)

    def add_sound_tracks(self, name_to_track_mapping: Dict[str, SoundTrack]) -> None:
        if self.instance is not None:
            self.instance.add_sound_tracks(name_to_track_mapping)

    def get_sound_tracks(self) -> Dict[str, List[SoundTrack]]:
        if self.instance is not None:
            return self.instance.name_to_sound_track_mapping
        return {}

    def stage_all_tracks(self) -> None:
        if self.instance is not None:
            self.instance.stage_all_tracks()

    # If interrupt is True, new music cuts in and then is replaced by the old music. This is only applicable when
    # music_file_path2 is not specified as it is implemented by leaving music_file_path2 unchanged.
    def play_music(self,
                   music_file_path1: str,
                   music_file_path2: Optional[str] = None,
                   interrupt: bool = False,
                   music_file_start1_sec: float = 0.0,
                   music_file_start2_sec: float = 0.0) -> None:
        if self.instance is not None:
            self.instance.play_music(music_file_path1,
                                     music_file_path2,
                                     interrupt,
                                     music_file_start1_sec,
                                     music_file_start2_sec)

    def play_sound(self, sound_file_path: str, from_music_tracks_first: bool = False) -> None:
        if self.instance is not None:
            self.instance.play_sound(sound_file_path, from_music_tracks_first)

    def stop_music(self) -> None:
        if self.instance is not None:
            self.instance.stop_music()

    def terminate(self) -> None:
        if self.instance is not None:
            self.instance.terminate()
            self.instance = None


def main() -> None:
    # Initialize the music player
    audio_player = AudioPlayer()
    base_path = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    audio_player.set_music_path(os.path.join(base_path, 'data', 'music', 'dw1'))
    audio_player.set_sound_path(os.path.join(base_path, 'data', 'sounds', 'dw1'))

    print('Play Overture...', flush=True)
    audio_player.play_music('01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg')
    pygame.time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (1).wav')
    pygame.time.wait(1000)

    print('Stop music...', flush=True)
    audio_player.stop_music()
    pygame.time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (1).wav')
    pygame.time.wait(1000)

    print('Play Overture...', flush=True)
    audio_player.play_music('01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg')
    pygame.time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('Dragon Warrior [Dragon Quest] SFX (1).wav')
    pygame.time.wait(1000)

    print('Terminate...', flush=True)
    audio_player.terminate()


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
