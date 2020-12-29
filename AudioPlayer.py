#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, Optional

import os.path
import pygame.mixer
import pygame.time
import threading


class AudioPlayer:
    class __AudioPlayer:
        def __init__(self) -> None:
            # Choose a desired audio format
            pygame.mixer.init(11025)  # Raises exception on fail
            pygame.mixer.set_num_channels(32)
         
            self.music_path = './'
            self.sound_path = './'
            self.music_rel_file_path1: Optional[str] = None
            self.music_rel_file_path2: Optional[str] = None
            self.music_file_start1 = 0.0
            self.music_file_start2 = 0.0
            self.running = True
            self.sounds: Dict[str, pygame.mixer.Sound] = {}
            self.music_thread_lock = threading.RLock()
            self.music_thread = threading.Thread(target=self.__music_thread)
            self.music_thread.start()
         
        def __del__(self) -> None:
            self.terminate()
            self.music_thread.join()
            pygame.mixer.quit()
         
        def set_music_path(self, music_path: str) -> None:
            self.music_path = music_path
         
        def set_sound_path(self, sound_path: str) -> None:
            self.sound_path = sound_path
         
        def play_music(self,
                       music_rel_file_path1: str,
                       music_rel_file_path2: Optional[str] = None,
                       interrupt: bool = False,
                       music_file_start1: float = 0.0,
                       music_file_start2: float = 0.0) -> None:
            self.music_thread_lock.acquire()
            self.music_rel_file_path1 = music_rel_file_path1
            self.music_file_start1 = music_file_start1
            if music_rel_file_path2 is not None:
                self.music_rel_file_path2 = music_rel_file_path2
                self.music_file_start2 = music_file_start2
            elif not interrupt:
                self.music_rel_file_path2 = music_rel_file_path1
                self.music_file_start2 = music_file_start1
            self.music_thread_lock.release()

        def __music_thread(self) -> None:
            first_time = True
            current_music_rel_file_path1: Optional[str] = None
            current_music_rel_file_path2: Optional[str] = None
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
                        self.music_file_start1 = self.music_file_start2
                    pygame.mixer.music.load(os.path.join(self.music_path, self.music_rel_file_path1))

                    # start playing
                    pygame.mixer.music.play(start=self.music_file_start1)

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

                self.music_thread_lock.release()
                pygame.time.wait(100)

        def play_sound(self, sound_rel_file_path: str) -> None:
            sound_thread = threading.Thread(target=self.__sound_thread, args=[sound_rel_file_path])
            sound_thread.start()

        def __sound_thread(self, sound_rel_file_path: str) -> None:
            # Load the sound if not previously loaded
            if sound_rel_file_path not in self.sounds:
                self.sounds[sound_rel_file_path] = pygame.mixer.Sound(
                    os.path.join(self.sound_path, sound_rel_file_path))

            channel = self.sounds[sound_rel_file_path].play()
            while self.running and channel.get_busy():
                pygame.time.wait(10)

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

    def set_sound_path(self, sound_path: str) -> None:
        if self.instance is not None:
            self.instance.set_sound_path(sound_path)

    # If interrupt is True, new music cuts in and then is replaced by the old music. This is only applicable when
    # music_file_path2 is not specified as it is implemented by leaving music_file_path2 unchanged.
    def play_music(self,
                   music_file_path1: str,
                   music_file_path2: Optional[str] = None,
                   interrupt: bool = False,
                   music_file_start1: float = 0.0,
                   music_file_start2: float = 0.0) -> None:
        if self.instance is not None:
            self.instance.play_music(music_file_path1,
                                     music_file_path2,
                                     interrupt,
                                     music_file_start1,
                                     music_file_start2)

    def play_sound(self, sound_file_path: str) -> None:
        if self.instance is not None:
            self.instance.play_sound(sound_file_path)

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
    audio_player.set_music_path(os.path.join(base_path, 'data', 'music'))
    audio_player.set_sound_path(os.path.join(base_path, 'data', 'sounds'))

    print('Play Overture...', flush=True)
    audio_player.play_music('01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg')
    pygame.time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('walking.wav')
    pygame.time.wait(1000)

    print('Stop music...', flush=True)
    audio_player.stop_music()
    pygame.time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('walking.wav')
    pygame.time.wait(1000)

    print('Play Overture...', flush=True)
    audio_player.play_music('01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg')
    pygame.time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('walking.wav')
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
