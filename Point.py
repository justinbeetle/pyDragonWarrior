#!/usr/bin/env python

import math
import operator

class Point(tuple):
   def __new__(self, x=0, y=0):
      if isinstance( x, tuple ):
         return tuple.__new__(Point, (x[0], x[1]))
      return tuple.__new__(Point, (x, y))
   
   def __add__( self, p ):
      return Point( self.x + p[0], self.y + p[1] )

   def __radd__( self, p ):
      return self + p;

   def __sub__( self, p ):
      return Point( self.x - p[0], self.y - p[1] )

   def __rsub__( self, p ):
      if isinstance( p, tuple ):
         return Point(p) / self;
      return NotImplemented;

   def __mul__( self, p ):
      if isinstance( p, tuple ):
         return Point( self.x * p[0], self.y * p[1])
      return Point( self.x * p, self.y * p )

   def __rmul__( self, p ):
      return self * p;

   def __truediv__( self, p ):
      if isinstance( p, tuple ):
         return Point( self.x / p[0], self.y / p[1])
      return Point( self.x / p, self.y / p )

   def __rtruediv__( self, p ):
      if isinstance( p, tuple ):
         return Point(p) / self;
      return NotImplemented

   def __floordiv__( self, p ):
      if isinstance( p, tuple ):
         return Point( self.x // p[0], self.y // p[1])
      return Point( self.x // p, self.y // p )

   def __rfloordiv__( self, p ):
      if isinstance( p, tuple ):
         return Point(p) / self;
      return NotImplemented

   def floor( self ):
      return Point( math.floor( self.x ), math.floor( self.y ) )

   def ceil( self ):
      return Point( math.ceil( self.x ), math.ceil( self.y ) )

   def __str__( self ):
      return "(%s, %s)" % (self.x, self.y)

   def __repr__( self ):
      return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)
   
Point.x = property(operator.itemgetter(0))
Point.w = property(operator.itemgetter(0))
Point.y = property(operator.itemgetter(1))
Point.h = property(operator.itemgetter(1))

def main():
   p1 = Point()
   p2 = Point( 1, 4 )
   p3 = Point( 2, 7 )
   p4 = ( 2, 2 )
   p5 = Point( p4 )
   p6 = Point( 2, 2 )
   p7 = Point( Point(2, 2) )
   
   print( 'p1 =', p1, flush=True )
   print( 'p2 =', p2, flush=True )
   print( 'p3 =', p3, flush=True )
   print( 'p4 =', p4, flush=True )
   print( 'p5 =', p5, flush=True )
   print( 'p6 =', p6, flush=True )
   print( 'p7 =', p7, flush=True )
   print( 'p5 == p3', p5 == p3, flush=True )
   print( 'p5 == p4', p5 == p4, flush=True )
   print( 'p4 == p5', p4 == p5, flush=True )
   print( 'p5 == p5', p5 == p5, flush=True )
   print( 'p5 == p6', p5 == p6, flush=True )
   print( 'p5 == p7', p5 == p7, flush=True )
   
   print( 'p1.x =', p1.x, flush=True )
   print( 'p1.y =', p1.y, flush=True )
   print( 'p1[0] =', p1[0], flush=True )
   print( 'p1[1] =', p1[1], flush=True )
   
   print( 'p4[0] =', p4[0], flush=True )
   print( 'p4[1] =', p4[1], flush=True )

   print( 'p1[0] =', p1[0], flush=True )
   print( 'p1[1] =', p1[1], flush=True )
   print( 'p4[0] =', p4[0], flush=True )
   print( 'p4[1] =', p4[1], flush=True )
   
   print( 'p2 + p3 =', p2 + p3, flush=True )
   print( 'p2 + p4 =', p2 + p4, flush=True )
   print( 'p4 + p2 =', p4 + p2, flush=True )
   
   print( 'p2 - p3 =', p2 - p3, flush=True )
   print( 'p2 - p4 =', p2 - p4, flush=True )
   print( 'p4 - p2 =', p4 - p2, flush=True )
   
   print( 'p2 * p3 =', p2 * p3, flush=True )
   print( 'p2 * p4 =', p2 * p4, flush=True )
   print( 'p4 * p2 =', p4 * p2, flush=True )
   print( 'p2 * 5 =', p2 * 5, flush=True )
   
   print( 'p3 / p2 =', p3 / p2, flush=True )
   print( 'p3 / p4 =', p3 / p4, flush=True )
   print( 'p4 / p3 =', p4 / p3, flush=True )
   print( 'p3 / 2 =', p3 / 2, flush=True )
   
   print( 'p3 // p2 =', p3 // p2, flush=True )
   print( 'p3 // p4 =', p3 // p4, flush=True )
   print( 'p4 // p3 =', p4 // p3, flush=True )
   print( 'p3 // 2 =', p3 // 2, flush=True )
   
   print( '(p3 / p2).ceil() =', (p3 / p2).ceil(), flush=True )
   print( '(p3 / p4).ceil() =', (p3 / p4).ceil(), flush=True )
   print( '(p4 / p3).ceil() =', (p4 / p3).ceil(), flush=True )
   print( '(p3 / 2).ceil() =', (p3 / 2).ceil(), flush=True )

if __name__ == '__main__':
   main()
