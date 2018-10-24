#!/usr/bin/env python

from Point import Point
from GameTypes import Direction

class MapCharacterState:
   def __init__(self, typeName: str, pos_datTile: Point, dir: Direction ) -> None:
      self.typeName = typeName
      self.currPos_datTile = Point( pos_datTile )
      self.destPos_datTile = Point( pos_datTile )
      self.currPosOffset_imgPx = Point( 0, 0 )
      self.dir = dir

   def __str__( self ) -> str:
      return "%s(%s, %s, %s, %s, %s)" % (
         self.__class__.__name__,
         self.typeName,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

   def __repr__( self ) -> str:
      return "%s(%r, %r, %r, %r, %r)" % (
         self.__class__.__name__,
         self.typeName,
         self.currPos_datTile,
         self.destPos_datTile,
         self.currPosOffset_imgPx,
         self.dir)

def main() -> None:
   # Test out character states
   mapCharacterState = MapCharacterState( 'myType', Point(5,6), Direction.SOUTH )
   print( mapCharacterState, flush=True )
   mapCharacterState.dir = Direction.WEST
   print( mapCharacterState, flush=True )

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
