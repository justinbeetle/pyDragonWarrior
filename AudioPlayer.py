#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, Optional

import os.path
import threading

import pygame
mixer = pygame.mixer
time = pygame.time


class AudioPlayer:
    class __AudioPlayer:
        def __init__(self) -> None:
            # Choose a desired audio format
            mixer.init(11025)  # Raises exception on fail
            mixer.set_num_channels(32)
         
            self.music_path = './'
            self.sound_path = './'
            self.music_rel_file_path1: Optional[str] = None
            self.music_rel_file_path2: Optional[str] = None
            self.running = True
            self.sounds: Dict[str, pygame.mixer.Sound] = {}
            self.music_thread = threading.Thread(target=self.__music_thread)
            self.music_thread.start()
         
        def __del__(self) -> None:
            self.terminate()
            self.music_thread.join()
            mixer.quit()
         
        def set_music_path(self, music_path: str) -> None:
            self.music_path = music_path
         
        def set_sound_path(self, sound_path: str) -> None:
            self.sound_path = sound_path
         
        def play_music(self, music_rel_file_path1: str, music_rel_file_path2: Optional[str] = None) -> None:
            self.music_rel_file_path1 = self.music_rel_file_path2 = music_rel_file_path1
            if music_rel_file_path2 is not None:
                self.music_rel_file_path2 = music_rel_file_path2
         
        def __music_thread(self) -> None:
            first_time = True
            current_music_rel_file_path1: Optional[str] = None
            current_music_rel_file_path2: Optional[str] = None
            while self.running:
                # TODO: Switch to a more responsive approach which is not polling based
   
                if (current_music_rel_file_path1 != self.music_rel_file_path1
                    or current_music_rel_file_path2 != self.music_rel_file_path2):
                    current_music_rel_file_path1 = self.music_rel_file_path1
                    current_music_rel_file_path2 = self.music_rel_file_path2
                    first_time = True
               
                if self.music_rel_file_path1 is not None and self.music_rel_file_path2 is not None:
                    # load the music
                    if first_time:
                        mixer.music.load(os.path.join(self.music_path, self.music_rel_file_path1))
                        first_time = False
                    else:
                        mixer.music.load(os.path.join(self.music_path, self.music_rel_file_path2))

                    # start playing
                    mixer.music.play()

                    # poll until finished
                    while (self.running
                           and mixer.music.get_busy()
                           and current_music_rel_file_path1 == self.music_rel_file_path1
                           and current_music_rel_file_path2 == self.music_rel_file_path2):
                        # still playing and not changed
                        time.wait(100)
                    mixer.music.stop()

                time.wait(100)
         
        def play_sound(self, sound_rel_file_path: str) -> None:
            sound_thread = threading.Thread(target=self.__sound_thread, args=[sound_rel_file_path])
            sound_thread.start()
         
        def __sound_thread(self, sound_rel_file_path: str) -> None:
            # Load the sound if not previously loaded
            if sound_rel_file_path not in self.sounds:
                self.sounds[sound_rel_file_path] = mixer.Sound(os.path.join(self.sound_path, sound_rel_file_path))

            channel = self.sounds[sound_rel_file_path].play()
            while self.running and channel.get_busy():
                time.wait(10)
            
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
      
    def play_music(self, music_file_path1: str, music_file_path2: Optional[str] = None) -> None:
        if self.instance is not None:
            self.instance.play_music(music_file_path1, music_file_path2)
      
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
    time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('walking.wav')
    time.wait(1000)

    print('Stop music...', flush=True)
    audio_player.stop_music()
    time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('walking.wav')
    time.wait(1000)

    print('Play Overture...', flush=True)
    audio_player.play_music('01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg')
    time.wait(1000)
    print('Play sound...', flush=True)
    audio_player.play_sound('walking.wav')
    time.wait(1000)

    print('Terminate...', flush=True)
    audio_player.terminate()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
