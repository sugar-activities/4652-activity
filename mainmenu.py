#! /usr/bin/env python
# coding: ISO-8859-1
"""Skeleton project file mainloop for new OLPCGames users"""
import olpcgames, pygame, logging
from olpcgames import pausescreen
from connection import Connection
import time
import helpers
WindowHelper = helpers.WindowHelper
PosSprite = helpers.PosSprite
Button = helpers.Button
from carteando import Carteando
from card import CardData
from creditos import Creditos
from ayuda import Ayuda

log = logging.getLogger('Carteando')
log.setLevel(logging.DEBUG)

def main():
    mainmenu = MainMenu()
    mainmenu.run()

class MainMenu():
    
    # Colores
    GRAY = 0x888888
    RED  = 0xAA0000
    WHITE = 0xFFFFFF
    BLUE = 0x0000AA
    BLACK = 0x000000
    BACK_COLOR = BLACK
    COLOR_FONT = (255,255,255)
    
    def __init__(self):

        """The mainloop which is specified in the activity.py file
        
        "main" is the assumed function name
        """
        
        # Game state variables
        self.playing = False
        
        # Load Cards data
        self.card_data = CardData.load_data()        
        
        # Set screen
        #self.size = (800,426)
        self.size = (600,320)
        if olpcgames.ACTIVITY:
            self.size = olpcgames.ACTIVITY.game_size
        self.screen = pygame.display.set_mode(self.size)
        WindowHelper.set_size(self.size[0], self.size[1])
        # sugar-emulator gets:                800 546
        # sugar xo olidata (docentes) gets:   800 426
        # sugar xo (escuela) gets:            1200 825
        # sugar xo (magallanes) gets:         1200 825?
        
        self.window = pygame.Rect(0,0, self.screen.get_size()[0], self.screen.get_size()[1])
        log.debug("TAMANIO: "+str(self.window.width)+", "+str(self.window.height))
        # I don't use Non-ASCII characters because if I do so Log Activity is unable to open logfile
        
        #PYGAME INIT
        pygame.init()
        self.clock = pygame.time.Clock()
        
        self.clear_background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        self.clear_background.fill(self.BACK_COLOR)     # fill back color
        
        self.allsprites = pygame.sprite.LayeredDirty()
        self.allsprites.set_clip()
        
        self.background = PosSprite(300, 160, "mm_bg.png")
        self.allsprites.add(self.background, layer=1)        
        
        self.btn_jugar = Button(150, 68, ["mm_btn_jugar.png", "mm_btn_jugar_h.png"])
        self.allsprites.add(self.btn_jugar, layer=2)
        self.btn_jugar_mac = Button(150, 128, ["mm_btn_jugar_mac.png", "mm_btn_jugar_mac_h.png", "mm_btn_jugar_mac_d.png"])        
        #self.btn_jugar_mac.set_enabled(False)
        self.allsprites.add(self.btn_jugar_mac, layer=2)        
        self.btn_jugar_red = Button(150, 188, ["mm_btn_jugar_red.png", "mm_btn_jugar_red_h.png", "mm_btn_jugar_red_d.png"])
        self.btn_jugar_red.set_enabled(False)
        self.allsprites.add(self.btn_jugar_red, layer=2)        
        self.btn_salir = Button(150, 248, ["mm_btn_salir.png", "mm_btn_salir_h.png"])
        self.allsprites.add(self.btn_salir, layer=2)
        
        self.btn_creditos = Button( 484, 240, ["mm_btn_creditos.png", "mm_btn_creditos_h.png"], False)        
        self.allsprites.add(self.btn_creditos, layer=2)
        self.btn_ayuda = Button( 484, 203, ["mm_btn_ayuda.png", "mm_btn_ayuda_h.png"], False)
        self.allsprites.add(self.btn_ayuda, layer=2)
        
        self.show_fps = False
        if self.show_fps:
            self.fps_font = pygame.font.Font("img/gabriola.ttf", 28)
            self.fps_label = PosSprite(38, 15, self.fps_font.render("0 FPS", True, self.COLOR_FONT))
            self.allsprites.add(self.fps_label, layer=1000)
        
        self.conn = Connection()
        
    
    def run(self):
        self.running = True
        self.starting_game = False
        self.starting_net_game = False
        self.starting_mac_game = False
        self.starting_creditos = False
        self.starting_ayuda = False
        while self.running:
            # Parameter is maximum number of frames per second
            # Returns milliseconds from last tick            
            #seconds = self.clock.tick(300) / 1000.0      
            seconds = self.clock.tick(25) / 1000.0
            
            if self.show_fps:    
                self.fps_label.set_image(self.fps_font.render(int(self.clock.get_fps()).__str__() + " FPS", True, self.COLOR_FONT))
                      
            self.process_events()               
            if not self.running:
                break
                
            self.allsprites.clear(self.screen, self.clear_background)        
            if self.starting_game:
                # Start Game
                self.starting_game = False
                # It will stay in a loop here while in the game
                self.start_game()
                # When the Game is finished it returns here
            elif self.starting_mac_game:
                # Start Machine Game
                self.starting_mac_game = False
                # It will stay in a loop here while in the game
                self.start_mac_game()
                # When the Game is finished it returns here
            elif self.starting_net_game:
                # Start Net Game
                self.starting_net_game = False
                # It will stay in a loop here while in the game
                self.start_net_game()
                # When the Game is finished it returns here
            elif self.starting_creditos:
                self.starting_creditos = False
                self.start_creditos()            
            elif self.starting_ayuda:
                self.starting_ayuda = False
                self.start_ayuda()
            else:            
                # Process allsprites
                self.allsprites.update(seconds)
                self.allsprites.draw(self.screen)
                pygame.display.flip()
            
                          
    def process_events(self):
        #events = pygame.event.get()
        events = pausescreen.get_events()
        if events:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.btn_jugar.is_over():
                            self.starting_game = True
                        elif self.btn_jugar_mac.is_over():
                            self.starting_mac_game = True
                        elif self.btn_jugar_red.is_over():
                            self.starting_net_game = True
                        elif self.btn_salir.is_over():
                            self.running = False
                        elif self.btn_creditos.is_over():
                            self.starting_creditos = True
                        elif self.btn_ayuda.is_over():
                            self.starting_ayuda = True                    
                elif self.conn.process_event(event):
                    self.update_conn_dependents()
    
    
    def update_conn_dependents(self):
        # Enable Net Game button for Initiator after Friend is connected
        if self.conn.friend_connected and self.conn.initiator:                
            self.btn_jugar_red.set_enabled(True)
        else:
            self.btn_jugar_red.set_enabled(False)
        
        # Start Net game from Friend side (not Initiator)
        if self.conn.invitation_started:
            log.debug("Friend started Net Game: " + self.conn.initiator.__str__() + " : " + self.conn.friend_handle.__str__())
            self.start_net_game(self.conn.invitation_mazo)
            
    def back_on_top(self):
        self.allsprites.repaint_rect(self.window)
        self.update_conn_dependents()
            
    def start_game(self):        
        self.game = Carteando(self, self.screen, self.clock, self.conn, Carteando.VSOTHER, None, None, None)
        self.game.run()
        self.back_on_top()
    
    def start_mac_game(self):        
        self.game = Carteando(self, self.screen, self.clock, self.conn, Carteando.VSMACHINE, None, None, None)
        self.game.run()
        self.back_on_top()
    
    def start_net_game(self, mazo=None):        
        self.game = Carteando(self, self.screen, self.clock, self.conn, Carteando.VSNET, self.conn.initiator, self.conn.friend_handle, mazo)
        self.game.run()
        self.back_on_top()
    
    def start_creditos(self):        
        creditos = Creditos(self.screen, self.clock)
        creditos.run()
        self.back_on_top()        
            
    def start_ayuda(self):        
        ayuda = Ayuda(self.screen, self.clock)
        ayuda.run()
        self.back_on_top()
        
        
if __name__ == "__main__":
    logging.basicConfig()
    main()
    

