import pygame
from helpers import PosSprite
import os, logging

log = logging.getLogger('Carteando')
log.setLevel(logging.DEBUG)


class SpriteController:
    
    def __init__(self):
        self._object = None
    
    def on_added(self, controlled_object):
        self._object = controlled_object
        
    def finish(self):
        pass
    
class SCQueue(SpriteController):
    
    def __init__(self):
        SpriteController.__init__(self)
        self._queue = []
        self._idx = 0
        
    def on_added(self, controlled_object):
        SpriteController.on_added(self, controlled_object)
        for controller in self._queue:
            controller.on_added(controlled_object)
        
    def add(self, controller):
        self._queue.append(controller)    
            
    def update(self, seconds):
        if self._idx < len(self._queue):
            if self._queue[self._idx].update(seconds):
                self._idx +=1
                if self._idx >= len(self._queue):
                    self._idx = 0
                    return True
            return False
        else:
            return True
        
    def finish(self):
        while self._idx < len(self._queue):
            self._queue[self._idx].finish()
            self._idx +=1
        self._idx = 0


class SCCallback(SpriteController):
    
    def __init__(self, callback_function):
        SpriteController.__init__(self)
        self._callback_function = callback_function
        
    def update(self, seconds):
        self._callback_function()
        return True  
    
    def finish(self):
        self.update(0)
            

class SCLinearPath(SpriteController):
    
    def __init__(self, start_point, end_point, time):
        SpriteController.__init__(self)
        self._start = start_point
        self._end = end_point
        self._total_time = time
        self._elapsed_time = 0
        
    def update(self, seconds):
        self._elapsed_time += seconds      
        fraction = self._elapsed_time / self._total_time
        if fraction > 1:
            fraction = 1        
        posx = self._start[0] + (self._end[0]-self._start[0])*fraction
        posy = self._start[1] + (self._end[1]-self._start[1])*fraction       
                
        self._object.set_pos(posx, posy)
                     
        return self._elapsed_time >= self._total_time
    
    def finish(self):
        self.update(self._total_time)
