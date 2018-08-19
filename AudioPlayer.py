#!/usr/bin/env python

"""extremely simple demonstration playing a soundfile
and waiting for it to finish. you'll need the pygame.mixer
module for this to work. Note how in this simple example we
don't even bother loading all of the pygame package. Just
pick the mixer for sound and time for the delay function.

Optional command line argument:
  the name of an audio file.
  

"""

import os.path, sys, threading
import pygame.mixer, pygame.time
mixer = pygame.mixer
time = pygame.time

class AudioPlayer:
   class __AudioPlayer:
      def __init__(self):
         #print ('in AudioPlayer::__AudioPlayer::__init__')

         #choose a desired audio format
         mixer.init(11025) #raises exception on fail
         mixer.set_num_channels(32)
         
         self.musicPath = None
         self.soundPath = None
         self.musicRelFilePath1 = None
         self.musicRelFilePath2 = None
         self.running = True
         self.sounds = {}
         self.musicThread = threading.Thread(target=self.__musicThread)
         self.musicThread.start()
         
      def __del__(self):
         #print ('in AudioPlayer::__AudioPlayer::__del__')
         self.terminate()
         self.musicThread.join()
         mixer.quit()
         
      def setMusicPath(self, musicPath):
         #print ('in AudioPlayer::__AudioPlayer::setMusicPath')
         self.musicPath = musicPath
         
      def setSoundPath(self, soundPath):
         #print ('in AudioPlayer::__AudioPlayer::setSoundPath')
         self.soundPath = soundPath
         
      def playMusic(self, musicRelFilePath1, musicRelFilePath2 = None):
         #print ('in AudioPlayer::__AudioPlayer::playMusic')
         self.musicRelFilePath1 = self.musicRelFilePath2 = musicRelFilePath1
         if musicRelFilePath2 is not None:
            self.musicRelFilePath2 = musicRelFilePath2
         
      def __musicThread(self):
         #print ('in AudioPlayer::__AudioPlayer::__musicThread')
         firstTime = True
         currentMusicRelFilePath1 = None
         currentMusicRelFilePath2 = None
         while self.running:
            # TODO: Switch to a more responsive approach which is not polling based
   
            if ( currentMusicRelFilePath1 != self.musicRelFilePath1 or
                 currentMusicRelFilePath2 != self.musicRelFilePath2 ):
               currentMusicRelFilePath1 = self.musicRelFilePath1
               currentMusicRelFilePath2 = self.musicRelFilePath2
               firstTime = True
            if self.musicRelFilePath1 != None and self.musicRelFilePath2 != None:

               '''
               #load the sound
               if firstTime:
                  sound = mixer.Sound( os.path.join(self.musicPath, self.musicRelFilePath1) )
               else:
                  sound = mixer.Sound( os.path.join(self.musicPath, self.musicRelFilePath2) )
               firstTime = False

               #start playing
               #print ('Playing Sound...')
               channel = sound.play()

               #poll until finished
               while ( self.running and
                       channel.get_busy() and
                       currentMusicRelFilePath1 == self.musicRelFilePath1 and
                       currentMusicRelFilePath2 == self.musicRelFilePath2 ): #still playing and not changed
                  #print ('  ...still going...')
                  time.wait(100)
               #print ('Stopping Sound...')
               channel.stop()'''

               #load the music
               if firstTime:
                  mixer.music.load( os.path.join(self.musicPath, self.musicRelFilePath1) )
               else:
                  mixer.music.load( os.path.join(self.musicPath, self.musicRelFilePath2) )
               firstTime = False

               #start playing
               #print ('Playing Music...')
               mixer.music.play()

               #poll until finished
               while ( self.running and
                       mixer.music.get_busy() and
                       currentMusicRelFilePath1 == self.musicRelFilePath1 and
                       currentMusicRelFilePath2 == self.musicRelFilePath2 ): #still playing and not changed
                  #print ('  ...still going...')
                  time.wait(100)
               #print ('Stopping Music...')
               mixer.music.stop()

               #print ('...Finished')

            time.wait(100)
         #print ('exitted AudioPlayer::__AudioPlayer::__musicThread')
         
      def playSound(self, soundRelFilePath):
         #print ('in AudioPlayer::__AudioPlayer::playSound')
         soundThread = threading.Thread( target=self.__soundThread, args=[soundRelFilePath] )
         soundThread.start()
         
      def __soundThread(self, soundRelFilePath):
         #print ('in AudioPlayer::__AudioPlayer::__soundThread')
         # Load the sound if not previously loaded
         if not soundRelFilePath in self.sounds:
            #print ('Loading sound ', soundRelFilePath)
            self.sounds[soundRelFilePath] =  mixer.Sound( os.path.join(self.soundPath, soundRelFilePath) )

         channel = self.sounds[soundRelFilePath].play()
         while self.running and channel.get_busy():
            time.wait(10)
         #print ('exitted AudioPlayer::__AudioPlayer::__soundThread')
            
      def stopMusic(self):
         #print ('in AudioPlayer::__AudioPlayer::stopMusic')
         self.musicRelFilePath1 = self.musicRelFilePath2 = None
         
      def terminate(self):
         #print ('in AudioPlayer::__AudioPlayer::terminate')
         self.running = False
            
   instance = None
   def __init__(self):
      if not AudioPlayer.instance:
         AudioPlayer.instance = AudioPlayer.__AudioPlayer()
         
   def setMusicPath(self, musicPath):
      self.instance.setMusicPath(musicPath)
      
   def setSoundPath(self, soundPath):
      self.instance.setSoundPath(soundPath)
      
   def playMusic(self, musicFilePath1, musicFilePath2 = None):
      self.instance.playMusic(musicFilePath1, musicFilePath2)
      
   def playSound(self, soundFilePath):
      self.instance.playSound(soundFilePath)
      
   def stopMusic(self):
      self.instance.stopMusic()
      
   def terminate(self):
      self.instance.terminate()
      self.instance.__del__()
      self.instance = None

      


def main():
   
   # Initialize the music player
   audioPlayer = AudioPlayer()
   basePath = os.path.split(os.path.abspath(__file__))[0]
   audioPlayer.setMusicPath( os.path.join(basePath, 'data', 'music') )
   audioPlayer.setSoundPath( os.path.join(basePath, 'data', 'sounds') )

   print ('Play Overture...')
   audioPlayer.playMusic( '01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg' )
   time.wait(1000)
   print ('Play sound...')
   audioPlayer.playSound( 'walking.wav' )
   time.wait(1000)

   print ('Stop music...')
   audioPlayer.stopMusic()
   time.wait(1000)
   print ('Play sound...')
   audioPlayer.playSound( 'walking.wav' )
   time.wait(1000)

   print ('Play Overture...')
   audioPlayer.playMusic( '01_-_Dragon_Warrior_-_NES_-_Overture_March.ogg' )
   time.wait(1000)
   print ('Play sound...')
   audioPlayer.playSound( 'walking.wav' )
   time.wait(1000)

   print ('Terminate...')
   audioPlayer.terminate()

if __name__ == '__main__':
   main()
