#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, NamedTuple, Optional

import os.path
import pygame.mixer
import pygame.time
import threading


class MusicTrack(NamedTuple):
    name: str
    file_path1: str
    file_path2: Optional[str] = None
    file_start1_sec: float = 0.0
    file_start2_sec: float = 0.0
    credits: str = 'Uncredited'


class SoundTrack(NamedTuple):
    name: str
    file_path: str
    credits: str = 'Uncredited'


class AudioPlayer:
    class __AudioPlayer:
        def __init__(self) -> None:
            # Choose a desired audio format
            pygame.mixer.init(11025)  # Raises exception on fail
            pygame.mixer.set_num_channels(32)
         
            self.music_path = './'
            self.name_to_music_track_mapping: Dict[str, MusicTrack] = {}
            self.sound_path = './'
            self.name_to_sound_track_mapping: Dict[str, SoundTrack] = {}
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
            self.music_thread.join()
            pygame.mixer.quit()
         
        def set_music_path(self, music_path: str) -> None:
            self.music_path = music_path

        def add_music_tracks(self, name_to_track_mapping: Dict[str, MusicTrack]) -> None:
            for name in name_to_track_mapping:
                if name in self.name_to_music_track_mapping:
                    # In case of duplicate names, give preference to the first one successfully added
                    continue

                # Validate the paths
                path = os.path.join(self.music_path, name_to_track_mapping[name].file_path1)
                if not os.path.exists(path):
                    print(f'ERROR: Failed to add music track {name} because {path} does not exist', flush=True)
                    continue
                file_path2 = name_to_track_mapping[name].file_path2
                if file_path2 is not None:
                    path = os.path.join(self.music_path, file_path2)
                    if not os.path.exists(path):
                        print(f'ERROR: Failed to add music track {name} because {path} does not exist', flush=True)
                        continue

                self.name_to_music_track_mapping[name] = name_to_track_mapping[name]

        def set_sound_path(self, sound_path: str) -> None:
            self.sound_path = sound_path

        def add_sound_tracks(self, name_to_track_mapping: Dict[str, SoundTrack]) -> None:
            for name in name_to_track_mapping:
                if name in self.name_to_sound_track_mapping:
                    # In case of duplicate names, give preference to the first one successfully added
                    continue

                # Validate the path
                path = os.path.join(self.sound_path, name_to_track_mapping[name].file_path)
                if not os.path.exists(path):
                    print(f'ERROR: Failed to add sound track {name} because {path} does not exist', flush=True)
                    continue

                self.name_to_sound_track_mapping[name] = name_to_track_mapping[name]
         
        def play_music(self,
                       music_rel_file_path1: str,
                       music_rel_file_path2: Optional[str] = None,
                       interrupt: bool = False,
                       music_file_start1_sec: float = 0.0,
                       music_file_start2_sec: float = 0.0) -> None:
            self.music_thread_lock.acquire()
            if music_rel_file_path1 in self.name_to_music_track_mapping:
                track = self.name_to_music_track_mapping[music_rel_file_path1]
                self.music_rel_file_path1 = track.file_path1
                self.music_file_start1_sec = track.file_start1_sec
                if track.file_path2 is not None:
                    self.music_rel_file_path2 = track.file_path2
                    self.music_file_start2_sec = track.file_start2_sec
                elif not interrupt:
                    self.music_rel_file_path2 = track.file_path1
                    self.music_file_start2_sec = track.file_start1_sec
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

            self.music_thread_lock.release()

        def __music_thread(self) -> None:
            first_time = True
            current_music_rel_file_path1: Optional[str] = None
            current_music_rel_file_path2: Optional[str] = None
            failed_to_play = set()
            while self.running:
                # TODO: Switch to a more responsive approach which is not polling based

                self.music_thread_lock.acquire()
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
                    except:
                        if self.music_rel_file_path1 not in failed_to_play:
                            print('ERROR: Failed to load', self.music_rel_file_path1, flush=True)
                            failed_to_play.add(self.music_rel_file_path1)

                self.music_thread_lock.release()
                pygame.time.wait(100)

        def play_sound(self, sound_rel_file_path: str, from_music_tracks_first: bool = False) -> None:
            # Can play either a sound or music track as a sound track - it just won't loop.

            if from_music_tracks_first and sound_rel_file_path in self.name_to_music_track_mapping:
                sound_file_path = self.name_to_music_track_mapping[sound_rel_file_path].file_path1
            elif sound_rel_file_path in self.name_to_sound_track_mapping:
                sound_file_path = self.name_to_sound_track_mapping[sound_rel_file_path].file_path
            elif sound_rel_file_path in self.name_to_music_track_mapping:
                sound_file_path = self.name_to_music_track_mapping[sound_rel_file_path].file_path1
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
                except:
                    print('ERROR: Failed to load', sound_file_path, flush=True)
                    self.sounds[sound_file_path] = None

            sound = self.sounds[sound_file_path]
            if sound is not None:
                channel = sound.play()

        def stop_music(self) -> None:
            self.music_rel_file_path1 = self.music_rel_file_path2 = None

        def terminate(self) -> None:
            self.running = False

    instance: Optional[AudioPlayer.__AudioPlayer] = None

    def __init__(self) -> None:
        if not AudioPlayer.instance:
            AudioPlayer.instance = AudioPlayer.__AudioPlayer()

    def set_music_path(self, music_path: str) -> None:
        if self.instance is not None:
            self.instance.set_music_path(music_path)

    def add_music_tracks(self, name_to_track_mapping: Dict[str, MusicTrack]) -> None:
        if self.instance is not None:
            self.instance.add_music_tracks(name_to_track_mapping)

    def get_music_tracks(self) -> Dict[str, MusicTrack]:
        if self.instance is not None:
            return self.instance.name_to_music_track_mapping
        return {}

    def set_sound_path(self, sound_path: str) -> None:
        if self.instance is not None:
            self.instance.set_sound_path(sound_path)

    def add_sound_tracks(self, name_to_track_mapping: Dict[str, SoundTrack]) -> None:
        if self.instance is not None:
            self.instance.add_sound_tracks(name_to_track_mapping)

    def get_sound_tracks(self) -> Dict[str, SoundTrack]:
        if self.instance is not None:
            return self.instance.name_to_sound_track_mapping
        return {}

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
            self.instance.__del__()
            self.instance = None


def main() -> None:
    # Initialize the music player
    audio_player = AudioPlayer()
    base_path = os.path.split(os.path.abspath(__file__))[0]
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
