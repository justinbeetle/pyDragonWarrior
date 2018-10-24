#!/usr/bin/env python

from MapCharacterState import *
from GameTypes import NpcInfo

class NpcState(MapCharacterState):
   def __init__(self, npcInfo: NpcInfo ) -> None:
      super(NpcState, self).__init__( typeName=npcInfo.type,
                                      pos_datTile=npcInfo.point,
                                      dir=npcInfo.dir )
      self.npcInfo = npcInfo

   def __str__( self ) -> str:
      return "%s(%s, %s)" % (
         self.__class__.__name__,
         super(NpcState, self).__str__(),
         self.npcInfo)

   def __repr__( self ) -> str:
      return "%s(%r, %r)" % (
         self.__class__.__name__,
         super(NpcState, self).__repr__(),
         self.npcInfo)

def main() -> None:
   # Test out character states
   npcInfo = NpcInfo( type = 'myType',
                      point = Point(5,6),
                      dir = Direction.SOUTH,
                      walking = False )
   npcState = NpcState( npcInfo )
   print( npcState, flush=True )
   npcState.dir = Direction.WEST
   print( npcState, flush=True )

if __name__ == '__main__':
   try:
      main()
   except Exception:
      import traceback
      traceback.print_exc()
