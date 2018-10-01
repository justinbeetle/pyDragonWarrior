#!/usr/bin/env python

# Imports to support type annotations
from __future__ import annotations
from typing import Dict, Optional

import os.path, sys, threading
import pygame.mixer, pygame.time
mixer = pygame.mixer
time = pygame.time

class AudioPlayer:
   class __AudioPlayer:
      def __init__(self) -> None:
         #print ('in AudioPlayer::__AudioPlayer::__init__', flush=True)

         #choose a desired audio format
         mixer.init(11025) #raises exception on fail
         mixer.set_num_channels(32)
         
         self.musicPath = './'
         self.soundPath = './'
         self.musicRelFilePath1: Optional[str] = None
         self.musicRelFilePath2: Optional[str] = None
         self.running = True
         self.sounds: Dict[str, pygame.mixer.Sound] = {}
         self.musicThread = threading.Thread(target=self.__musicThread)
         self.musicThread.start()
         
      def __del__(self) -> None:
         #print ('in AudioPlayer::__AudioPlayer::__del__', flush=True)
         self.terminate()
         self.musicThread.join()
         mixer.quit()
         
      def setMusicPath(self, musicPath: str) -> None:
         #print ('in AudioPlayer::__AudioPlayer::setMusicPath', flush=True)
         self.musicPath = musicPath
         
      def setSoundPath(self, soundPath: str) -> None:
         #print ('in AudioPlayer::__AudioPlayer::setSoundPath', flush=True)
         self.soundPath = soundPath
         
      def playMusic(self, musicRelFilePath1: str, musicRelFilePath2: Optional[str] = None) -> None:
         #print ('in AudioPlayer::__AudioPlayer::playMusic', flush=True)
         self.musicRelFilePath1 = self.musicRelFilePath2 = musicRelFilePath1
         if musicRelFilePath2 is not None:
            self.musicRelFilePath2 = musicRelFilePath2
         
      def __musicThread(self) -> None:
         #print ('in AudioPlayer::__AudioPlayer::__musicThread', flush=True)
         firstTime = True
         currentMusicRelFilePath1: Optional[str] = None
         currentMusicRelFilePath2: Optional[str] = None
         while self.running:
            # TODO: Switch to a more responsive approach which is not polling based
   
            if ( currentMusicRelFilePath1 != self.musicRelFilePath1 or
                 currentMusicRelFilePath2 != self.musicRelFilePath2 ):
               currentMusicRelFilePath1 = self.musicRelFilePath1
               currentMusicRelFilePath2 = self.musicRelFilePath2
               firstTime = True
               
            if self.musicRelFilePath1 is not None and self.musicRelFilePath2 is not None:
               #load the music
               if firstTime:
                  mixer.music.load( os.path.join(self.musicPath, self.musicRelFilePath1) )
               else:
                  mixer.music.load( os.path.join(self.musicPath, self.musicRelFilePath2) )
               firstTime = False

               #start playing
               #print ('Playing Music...', flush=True)
               mixer.music.play()

               #poll until finished
               while ( self.running and
                       mixer.music.get_busy() and
                       currentMusicRelFilePath1 == self.musicRelFilePath1 and
                       currentMusicRelFilePath2 == self.musicRelFilePath2 ): #still playing and not changed
                  #print ('  ...still going...', flush=True)
                  time.wait(100)
               #print ('Stopping Music...', flush=True)
               mixer.music.stop()

               #print ('...Finished', flush=True)

            time.wait(100)
         #print ('exitted AudioPlayer::__AudioPlayer::__musicThread', flush=True)
         
      def playSound(self, soundRelFilePath: str) -> None:
         #print ('in AudioPlayer::__AudioPlayer::playSound', flush=True)
         soundThread = threading.Thread( target=self.__soundThread, args=[soundRelFilePath] )
         soundThread.start()
         
      def __soundThread(self, soundRelFilePath: str) -> None:
         #print ('in AudioPlayer::__AudioPlayer::__soundThread', flush=True)
         # Load the sound if not previously loaded
         if not soundRelFilePath in self.sounds:
            #print ('Loading sound ', soundRelFilePath, flush=True)
            self.sounds[soundRelFilePath] =  mixer.Sound( os.path.join(self.soundPath, soundRelFilePath) )

         channel = self.sounds[soundRelFilePath].play()
         while self.running and channel.get_busy():
            time.wait(10)
         #print ('exitted AudioPlayer::__AudioPlayer::__soundThread', flush=True)
            
      def stopMusic(self) -> None:
         #print ('in AudioPlayer::__AudioPlayer::stopMusic', flush=True)
         self.musicRelFilePath1 = self.musicRelFilePath2 = None
         
      def terminate(self) -> None:
         #print ('in AudioPlayer::__AudioPlayer::terminate', flush=True)
         self.running = False
            
   instance: Optional[AudioPlayer.__AudioPlayer] = None
   def __init__(self) -> None:
      if not AudioPlayer.instance:
         AudioPlayer.instance = AudioPlayer.__AudioPlayer()
         
   def setMusicPath(self, musicPath: str) -> None:
      if self.instance is not None:
         self.instance.setMusicPath(musicPath)
      
   def setSoundPath(self, soundPath: str) -> None:
      if self.instance is not None:
         self.instance.setSoundPath(soundPath)
      
   def playMusic(self, musicFilePath1: str, musicFilePath2: Optional[str] = None) -> None:
      if self.instance is not None:
         self.instance.playMusic(musicFilePath1, musicFilePath2)
      
   def playSound(self, soundFilePath: str) -> None:
      if self.instance is not None:
         self.instance.playSound(soundFilePath)
      
   def stopMusic(self) -> None:
      if self.instance is not None:
         self.instance.stopMusic()
      
   def terminate(self) -> None:
      if self.instance is not None:
         self.instance.terminate()
         self.instance.__del__()
         self.instance = None

def main() -> None:
   
   # Initialize the music player
   audioPlayer = AudioPlayer()
   basePath = os.path.split(os.path.abspath(__file__))[0]
   audioPlayer.setMusicPath( os.path.join(basePath, 'data', 'music') )
   audioPlayer.setSoundPath( os.path.join(basePath, 'data', 'sounds') )

   print ('Play Overture...', flush=True)
   audioPlayer.playMusic( '01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg' )
   time.wait(1000)
   print ('Play sound...', flush=True)
   audioPlayer.playSound( 'walking.wav' )
   time.wait(1000)

   print ('Stop music...', flush=True)
   audioPlayer.stopMusic()
   time.wait(1000)
   print ('Play sound...', flush=True)
   audioPlayer.playSound( 'walking.wav' )
   time.wait(1000)

   print ('Play Overture...', flush=True)
   audioPlayer.playMusic( '01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg' )
   time.wait(1000)
   print ('Play sound...', flush=True)
   audioPlayer.playSound( 'walking.wav' )
   time.wait(1000)

   print ('Terminate...', flush=True)
   audioPlayer.terminate()

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
