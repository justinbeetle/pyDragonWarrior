#!/usr/bin/env python

from Point import Point
from GameTypes import *

class MapCharacter:
   def __init__(self, typeName: str, pos_datTile: Point, dir: Direction ) -> None:
      self.typeName: str = typeName
      self.currPos_datTile: Point = Point( pos_datTile )
      self.destPos_datTile: Point = Point( pos_datTile )
      self.currPosOffset_imgPx: Point = Point( 0, 0 )
      self.dir: Direction = dir

   def __str__( self ):
      return "%s(%s, %s, %s, %s, %s)" % (
         self.__class__.__name__,
         self.typeName,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

   def __repr__( self ):
      return "%s(%r, %r, %r, %r, %r)" % (
         self.__class__.__name__,
         self.typeName,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

def main():
   # Test out character states
   mapCharacter = MapCharacter( 5, Point(5,6), Direction.SOUTH )
   print( mapCharacter, flush=True )
   mapCharacter.dir = Direction.WEST
   print( mapCharacter, flush=True )

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
