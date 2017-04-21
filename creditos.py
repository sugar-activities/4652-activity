# coding: ISO-8859-1
import logging
import olpcgames, pygame
from helpers import PosSprite, Button

log = logging.getLogger('Carteando')
log.setLevel(logging.DEBUG)

class Creditos():
    
    # TEXTS
    
    
    # LAYERS
    LAYER_BG = 1
    LAYER_TEXT = 2    
    LAYER_BTN = 4
    
    # COLORS
    GRAY = 0x888888
    RED  = 0xAA0000
    WHITE = 0xFFFFFF
    BLUE = 0x0000AA
    BLACK = 0x000000
    BACK_COLOR = BLACK
    
    
    def __init__(self, screen, clock):
                
        self.screen = screen
        self.window = screen.get_size()
        self.clock = clock
        
        self.clear_background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        self.clear_background.fill(self.BACK_COLOR)     # fill back color
                
        self.allsprites = pygame.sprite.LayeredUpdates();
        self.allsprites.clear(self.screen, self.clear_background)
                
        self.background = PosSprite(300, 160, "credits_bg.png")
        self.allsprites.add(self.background, layer=1)
        
        # Add image with all texts...
        #self.background = PosSprite(self.centerx, self.centery, "mm_bg.png")
        #self.allsprites.add(self.background, layer=1)
        
        self.btn_salir = Button( 70, 285, ["btn_volver.png", "btn_volver_h.png"], False)
        self.allsprites.add(self.btn_salir, layer=2)
    
    
    def end(self):
        self.running = False
    
        
    def run(self):
        self.running = True
        while self.running:
            # Parameter is maximum number of frames per second
            # Returns milliseconds from last tick
            seconds = self.clock.tick(25) / 1000.0
                   
            self.process_events()
            if not self.running:
                break
                    
            # Process allsprites            
            self.allsprites.update(seconds)
            self.allsprites.draw(self.screen)
                        
            pygame.display.flip()       
            
            
    def process_events(self):
        events = pygame.event.get()
        for event in events:
            #log.debug("Event: %s", event)
            if event.type == pygame.QUIT:
                self.end()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.end()
            elif event.type==pygame.MOUSEBUTTONUP:
                if event.button==1:
                    if self.btn_salir.is_over():
                        self.end()
    