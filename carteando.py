# coding: ISO-8859-1
import logging
import random
import time
import olpcgames, pygame
from olpcgames import pausescreen
from connection import Connection
from helpers import PosSprite, StatesSprite, Button
from card import Card

log = logging.getLogger('Carteando')
log.setLevel(logging.DEBUG)

class Carteando():
    
    # TEXTS
    YOUR_TURN_TEXT = "Tu turno"
    MACHINE_TURN_TEXT = "Turno de la máquina"
    NET_TURN_TEXT = "Turno del amigo"
    PLAYER_WINS_TEXT = "Ganaste!!!"
    MACHINE_WINS_TEXT = "Ganó la maquina!"
    NET_WINS_TEXT = "Ganó el amigo!"
    
    # GAMETYPES    
    VSMACHINE = 0
    VSOTHER = 1
    VSNET = 2    
    
    # COLORS
    GRAY = 0x888888
    RED  = 0xAA0000
    WHITE = 0xFFFFFF
    BLUE = 0x0000AA
    BLACK = 0x000000
    BACK_COLOR = BLACK
    COLOR_FONT = (255,255,255)
    COLOR_FONT_ABOVE_LINE = (255,255,255)
    
    # LAYERS
    LAYER_BG = 1
    LAYER_BARRA = 2    
    LAYER_MAZO = 4
    LAYER_CARD = 5
    LAYER_MAZO_UP = 5+100
    LAYER_BTN_SALIR = LAYER_MAZO_UP+1
    
    # TIMER IDS
    TIMER_SHOW_CARDS_EVENT = pygame.USEREVENT +1
    TIMER_SHOW_CARDS_MIN_EVENT = pygame.USEREVENT +2
    TIMER_MACHINE_OPEN_CARDS_EVENT = pygame.USEREVENT +3
    TIMER_MACHINE_SELECT_ATTRIBUTE_EVENT = pygame.USEREVENT +4
    TIMER_SHOW_WINNER_EVENT = pygame.USEREVENT +5
    
    # TIMES
    TIME_SHOW_CARDS = 4000
    TIME_SHOW_CARDS_MIN = 1000
    TIME_MACHINE_OPEN_CARDS = 1000
    TIME_MACHINE_SELECT_ATTRIBUTE = 1000
    TIME_SHOW_WINNER = 3000
    
    
    def __init__(self, mainmenu, screen, clock, connection, gametype, initiator, friend_handle, mazo):
                
        self.mainmenu = mainmenu
        
        self.screen = screen
        self.clock = clock
        
        self.gametype = gametype
        
        self.clear_background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        self.clear_background.fill(self.BACK_COLOR)     # fill back color
        
        self.allsprites = pygame.sprite.LayeredDirty();
        self.allsprites.set_clip()
        #self.allsprites = pygame.sprite.LayeredUpdates();
        self.allsprites.clear(self.screen, self.clear_background)
        
        
        self.background = PosSprite(300, 160, "play_bg.png")
        self.allsprites.add(self.background, layer=self.LAYER_BG)
        
        self.line_left = StatesSprite(150, 38, ["play_barra.png", "play_barra_h.png"])        
        self.allsprites.add(self.line_left, layer=self.LAYER_BARRA)
        font = pygame.font.Font("img/gabriola.ttf", 28)
        font.set_bold(True)                      
        self.turn_left = PosSprite(45, 26, font.render(self.YOUR_TURN_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
        self.turn_left.set_pos(45+self.turn_left.rect.width/2.0, 26)
        self.turn_left.set_visible(False)
        self.allsprites.add(self.turn_left, layer=self.LAYER_BARRA)
        
        self.line_right = StatesSprite(450, 38, ["play_barra.png", "play_barra_h.png"])
        self.allsprites.add(self.line_right, layer=self.LAYER_BARRA)        
        if self.gametype==self.VSOTHER:
            self.turn_right = PosSprite(555,26, font.render(self.YOUR_TURN_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
        elif self.gametype==self.VSMACHINE:
            self.turn_right = PosSprite(555,26, font.render(self.MACHINE_TURN_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
        elif self.gametype==self.VSNET:
            self.turn_right = PosSprite(555,26, font.render(self.NET_TURN_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
        self.turn_right.set_pos(555-self.turn_right.rect.width/2.0, 26)
        self.turn_right.set_visible(False)
        self.allsprites.add(self.turn_right, layer=self.LAYER_BARRA)
                
        self.sprite_mazo = StatesSprite( 98, 173, ["empty.png", "play_mazo_0.png", "play_mazo_1.png", "play_mazo_2.png", "play_mazo_3.png", "play_mazo_4.png"])        
        self.allsprites.add(self.sprite_mazo, layer=self.LAYER_MAZO)
        
        self.sprite_op_mazo = StatesSprite( 503, 173, ["empty.png", "play_mazo_0.png", "play_mazo_1.png", "play_mazo_2.png", "play_mazo_3.png", "play_mazo_4.png"])
        self.allsprites.add(self.sprite_op_mazo, layer=self.LAYER_MAZO)
        
        self.btn_salir = Button( 300, 293, ["play_btn_volver.png", "play_btn_volver_h.png"], False)
        self.allsprites.add(self.btn_salir, layer=self.LAYER_BTN_SALIR)        
        
        self.card_data = self.mainmenu.card_data
        self.card = None
        self.op_card = None
        self._card_moving = False        
        self._card_mvmt_done = False
        self._op_card_mvmt_done = False        
        self._battle_won = False
        self._rand_mine_first = False
        self._showing_cards = False
        self._showing_cards_min = False
        self._finished = False
                
        self.conn = connection
        self.conn.set_playing_game(self)
        
        if self.gametype==self.VSOTHER:        
            # Me against other in same machine      
            # Sort mazos
            self.sort_mazos()
            self.my_move = True
        elif self.gametype==self.VSMACHINE:
            # Me against machine      
            # Sort mazos
            self.sort_mazos() 
            self.my_move = True
        elif self.gametype==self.VSNET:
            # Me against other in the mesh
            if initiator:
                # I am server                
                # Sort mazos
                self.sort_mazos()
                self.my_move = True
                # Send Mesh message with sorted cards
                self.conn.start_net_game(self.op_mazo + self.mazo)
            else:
                # I am client, mazo is passed from MainMenu (received in startedGame message)
                self.sort_mazos(mazo)
                self.my_move = False
        else:
            log.debug("ERROR. Gametype not valid.")
        
        self.update_turn_indicators()
        
        self.show_fps = False
        if self.show_fps:
            self.fps_font = pygame.font.Font("img/gabriola.ttf", 28)
            self.fps_label = PosSprite(38, 15, self.fps_font.render("0 FPS", True, self.COLOR_FONT))
            self.allsprites.add(self.fps_label, layer=3)
            
    
    def stop(self, net_commanded=False):
        self.running = False
        self.conn.set_playing_game(None)
        # Send mesh message to stop game if VSNET
        if self.gametype==self.VSNET and not net_commanded:
            self.conn.stop()
    
    
    def end(self):
        self.running = False
        self.conn.set_playing_game(None)
        
    
    def sort_mazos(self, mazo=None):
        if mazo==None:
            card_idcs = range(len(self.card_data))
            random.shuffle(card_idcs)
        else:
            card_idcs = mazo        
              
        self.mazo = card_idcs[:len(card_idcs)/2]
        self.op_mazo = card_idcs[len(card_idcs)/2:]
        
        log.debug("sorted: " + self.mazo.__str__() + " - " + self.op_mazo.__str__())
        self.update_mazos()
        
        
    def update_mazos(self, leftQty=None, rightQty=None):
                
        if leftQty<>None:
            lQty = leftQty
        else:
            lQty = len(self.mazo)
        if rightQty<>None:
            rQty = rightQty
        else:
            rQty = len(self.op_mazo)
        
        log.debug("Mazos: " + lQty.__str__() + " - " + rQty.__str__())
        
        # Show mazos states according card quantities
        new_state = lQty / float(len(self.card_data)) * (self.sprite_mazo.get_states_quantity()-1)
        new_state = int(round(new_state))
        if lQty>0 and new_state==0:
            new_state = 1
        #log.debug("Mazo set state: " + new_state.__str__())
        self.sprite_mazo.set_state(new_state)        
        
        new_state = rQty / float(len(self.card_data)) * (self.sprite_op_mazo.get_states_quantity()-1)
        new_state = int(round(new_state))
        if rQty>0 and new_state==0:
            new_state = 1
        #log.debug("Op Mazo set state: " + new_state.__str__())
        self.sprite_op_mazo.set_state(new_state)        
    
    
    def update_turn_indicators(self, offAll=False):
        if offAll:
            self.line_left.set_state(0)
            self.turn_left.set_visible(False)
            self.line_right.set_state(0)
            self.turn_right.set_visible(False)
        else:
            if self.my_move:
                self.line_left.set_state(1)
                self.turn_left.set_visible(True)
                self.line_right.set_state(0)
                self.turn_right.set_visible(False)
            else:
                self.line_left.set_state(0)
                self.turn_left.set_visible(False)                
                self.line_right.set_state(1)
                self.turn_right.set_visible(True)
        
    def run(self):
        self.running = True
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
                    
            # Process group updates
            if self.card != None:
                self.card.update(seconds)
            if self.op_card != None:
                self.op_card.update(seconds)
            
            # Process allsprites            
            self.allsprites.update(seconds)
            self.allsprites.draw(self.screen)
                        
            pygame.display.flip()       
            
            
    def process_events(self):
        #events = pygame.event.get()
        events = pausescreen.get_events()
        for event in events:
            #log.debug("Event: %s", event)
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop()
            elif event.type==pygame.MOUSEBUTTONUP:
                if event.button==1:
                    self.mouse_button_up()               
            elif event.type==self.TIMER_SHOW_CARDS_MIN_EVENT:
                pygame.time.set_timer(self.TIMER_SHOW_CARDS_MIN_EVENT, 0)
                self._showing_cards_min = True
            elif event.type==self.TIMER_SHOW_CARDS_EVENT:
                pygame.time.set_timer(self.TIMER_SHOW_CARDS_EVENT, 0)
                self.finish_show_cards()
            elif event.type==self.TIMER_MACHINE_OPEN_CARDS_EVENT:
                pygame.time.set_timer(self.TIMER_MACHINE_OPEN_CARDS_EVENT, 0)
                
                ## Machine open cards
                self.open_cards()
                #Timer callback for computer player to choose attribute
                pygame.time.set_timer(self.TIMER_MACHINE_SELECT_ATTRIBUTE_EVENT, self.TIME_MACHINE_SELECT_ATTRIBUTE)
            elif event.type==self.TIMER_MACHINE_SELECT_ATTRIBUTE_EVENT:
                pygame.time.set_timer(self.TIMER_MACHINE_SELECT_ATTRIBUTE_EVENT, 0)     
                
                ## Machine select attribute
                self.op_card.choose_attribute(random.randint(0,len(self.op_card.btn_atrs)-1))
                self.attribute_selected(self.op_card.chosen_attribute)
            elif event.type==self.TIMER_SHOW_WINNER_EVENT:
                pygame.time.set_timer(self.TIMER_SHOW_WINNER_EVENT, 0)
                self.end()
            elif self.conn.process_event(event):
                self.update_conn_dependents()
    
    
    def update_conn_dependents(self):
        pass
            
    
    def finish_show_cards(self, net_commanded=False, insertion_order=None):
        self._showing_cards = False
        self._showing_cards_min = False
        self._card_moving = True
               
        if net_commanded:
            # Get insertion order of cards
            self._rand_mine_first = insertion_order
        else:
            # Sort insertion order of cards
            self._rand_mine_first = random.randint(0,1)==0        
                
        #log.debug("Finish show cards")
        if self.gametype==self.VSNET and not net_commanded:
            # Send Mesh message to finish showing cards
            self.conn.finish_show_cards(not self._rand_mine_first)
        
        ## After shown cards with selected attribute
        if self._battle_won:
            self.allsprites.change_layer(self.sprite_mazo, self.LAYER_MAZO_UP)
            self.card.move_to_mazo(self.sprite_mazo, self.card_mvmt_done)
            self.op_card.move_to_mazo(self.sprite_mazo, self.op_card_mvmt_done)                    
        else:
            self.allsprites.change_layer(self.sprite_op_mazo, self.LAYER_MAZO_UP)                    
            self.card.move_to_mazo(self.sprite_op_mazo, self.card_mvmt_done)
            self.op_card.move_to_mazo(self.sprite_op_mazo, self.op_card_mvmt_done)
        
    
    def mouse_button_up(self):
        if self._finished:
            return
        
        if self.btn_salir.is_over():
            self.stop()            
        elif self.my_move and self.card==None and self.sprite_mazo.is_over():
                        
            self.open_cards()
            
        elif self.gametype==self.VSOTHER and not self.my_move and self.op_card==None and self.sprite_op_mazo.is_over():
            
            self.open_cards()
                
        elif self.my_move and self.card!=None and not self._card_moving and self.card.get_chosen_value()==None:            
            if self.card.mouse_button_up():
    
                self.attribute_selected(self.card.chosen_attribute)        

        elif self.gametype==self.VSOTHER and not self.my_move and self.op_card!=None and not self._card_moving and self.op_card.get_chosen_value()==None:            
            if self.op_card.mouse_button_up():
                    
                self.attribute_selected(self.op_card.chosen_attribute)
                
        elif self._showing_cards and (self.gametype<>self.VSNET or (self._battle_won and self._showing_cards_min)):
            # After attribute been selected, while seeing cards, a click anywhere finishes showing them
            # In VSNET mode, only winner's side is valid  
            log.debug("Btn_up while showing cards")
            pygame.time.set_timer(self.TIMER_SHOW_CARDS_MIN_EVENT, 0)
            pygame.time.set_timer(self.TIMER_SHOW_CARDS_EVENT, 0)
            self.finish_show_cards()
                
                
    def open_cards(self, net_commanded=False):
                
        # Check if still showing old cards, can happen when net_commanded
        if self._showing_cards:
            log.debug("open_cards while showing cards!")
            pygame.time.set_timer(self.TIMER_SHOW_CARDS_MIN_EVENT, 0)
            pygame.time.set_timer(self.TIMER_SHOW_CARDS_EVENT, 0)
            self.finish_show_cards()                       
        # Check if cards are moving, then finish movement
        if self._card_moving:
            log.debug("open_cards aborted card movements!")
            self.card.finish_controllers()
            self.op_card.finish_controllers()
            
        if self.gametype==self.VSNET and self.my_move:            
            # Send Mesh message to show next cards
            self.conn.open_cards()
        if net_commanded and self.my_move:
            log.error("openCards net commanded and I have my move to do!!!")        
        
        self._card_mvmt_done = False
        self._op_card_mvmt_done = False
        self._card_moving = True
                    
        # Get new card from mazo
        self.card_idx = self.mazo.pop(0)
        # Create card
        start = self.sprite_mazo.get_pos()
        end = (218, 135)
        self.card = Card(start[0], start[1], self.card_data[self.card_idx])
        if (self.gametype==self.VSOTHER or self.gametype==self.VSMACHINE) and not self.my_move:
            self.card.set_backface(True)
        if self.gametype==self.VSNET and not self.my_move:
            self.card.disable_buttons()
        cardLayer=self.LAYER_CARD
        for sprite in self.card.sprites():
            self.allsprites.add(sprite, layer=cardLayer)
            cardLayer += 1        
        self.card.move_from_mazo(self.sprite_mazo, end, self.card_appear_done)
        
        # Get new card from op mazo            
        self.op_card_idx = self.op_mazo.pop(0)
        # Create oponent card (back faced)
        start = self.sprite_op_mazo.get_pos()
        end = (383, 135)
        self.op_card = Card(start[0], start[1], self.card_data[self.op_card_idx])
        if not ((self.gametype==self.VSOTHER or self.gametype==self.VSMACHINE) and not self.my_move):
            self.op_card.set_backface(True)
        if self.gametype==self.VSNET and self.my_move:
            self.op_card.disable_buttons()
        for sprite in self.op_card.sprites():
            self.allsprites.add(sprite, layer=cardLayer)
            cardLayer += 1
        self.op_card.move_from_mazo(self.sprite_op_mazo, end, self.op_card_appear_done)        
    
        log.debug("opened cards: " + self.card_idx.__repr__() + " - " + self.op_card_idx.__repr__())
    
        # Show mazos states according sizes
        self.update_mazos()        
    
    def card_appear_done(self):
        self._card_mvmt_done = True
        if self._card_mvmt_done and self._op_card_mvmt_done:
            self.cards_appear_done()
    def op_card_appear_done(self):
        self._op_card_mvmt_done = True
        if self._card_mvmt_done and self._op_card_mvmt_done:
            self.cards_appear_done()
    def cards_appear_done(self):
        self._card_moving = False
    
    
    def attribute_selected(self, chosen_attribute, net_commanded=False):
        ## Attribute Selected in one of the cards
        ## Resolve Battle
        
        if net_commanded and self.card==None:
            log.error("attributeSelected net commanded and I have no cards!!!")
        if net_commanded and self.my_move:
            log.error("attributeSelected net commanded and I have my move to do!!!")
            
        # Check if cards are moving (can happen when still opening and it is net_commanded)
        # Then finish movement
        if self._card_moving:
            log.debug("attribute selected aborted card movements!")
            self.card.finish_controllers()
            self.op_card.finish_controllers()
            
        if not net_commanded:
            log.debug("Attribute selected: " + chosen_attribute.__str__())
        
        self.card.disable_buttons()
        self.card.choose_attribute(chosen_attribute)
        self.card.set_backface(False)
        
        self.op_card.disable_buttons()
        self.op_card.choose_attribute(chosen_attribute)
        self.op_card.set_backface(False)
        
        self._card_mvmt_done = False
        self._op_card_mvmt_done = False
        self._card_moving = False
        
        if self.my_move:
            self._battle_won = self.card.get_chosen_value() > self.op_card.get_chosen_value()
        else:
            self._battle_won = self.card.get_chosen_value() >= self.op_card.get_chosen_value()
            
        if self.gametype==self.VSNET and self.my_move:
            # Send Mesh message with selected attribute for the other to show cards and selected attribute
            self.conn.attribute_selected(chosen_attribute)
        
        self._showing_cards = True
        self._showing_cards_min = False        
        # Show cards Timer, in VSNET mode is triggered only at winner's side
        if self.gametype<>self.VSNET or self._battle_won:
            pygame.time.set_timer(self.TIMER_SHOW_CARDS_MIN_EVENT, self.TIME_SHOW_CARDS_MIN)
            pygame.time.set_timer(self.TIMER_SHOW_CARDS_EVENT, self.TIME_SHOW_CARDS)            
        self.update_turn_indicators(True)
    
    
    def card_mvmt_done(self):
        self._card_mvmt_done = True
        if self._card_mvmt_done and self._op_card_mvmt_done:
            self.cards_mvmt_done()        
    def op_card_mvmt_done(self):
        self._op_card_mvmt_done = True
        if self._card_mvmt_done and self._op_card_mvmt_done:
            self.cards_mvmt_done()
    def cards_mvmt_done(self):
        self._card_moving = False
        
        if self._battle_won:
            # I won the cards (in random order)
            if self._rand_mine_first:
                self.mazo.append(self.card_idx)
                self.mazo.append(self.op_card_idx)
            else:                        
                self.mazo.append(self.op_card_idx)
                self.mazo.append(self.card_idx)
            self.my_move = True
        else:
            # Oponent won the cards (in random order)
            if self._rand_mine_first:
                self.op_mazo.append(self.card_idx)
                self.op_mazo.append(self.op_card_idx)
            else:                        
                self.op_mazo.append(self.op_card_idx)
                self.op_mazo.append(self.card_idx)
            self.my_move = False
            if self.gametype==self.VSMACHINE:
                #Timer callback for computer player to open cards
                pygame.time.set_timer(self.TIMER_MACHINE_OPEN_CARDS_EVENT, self.TIME_MACHINE_OPEN_CARDS)
        self.update_mazos()
        self.update_turn_indicators()
        
        # clear after movement
        self.allsprites.remove(self.card)
        self.card = None
        self.allsprites.remove(self.op_card)
        self.op_card = None
        
        self.allsprites.change_layer(self.sprite_mazo, self.LAYER_MAZO)
        self.allsprites.change_layer(self.sprite_op_mazo, self.LAYER_MAZO)
                
        if len(self.mazo)==0:
            # Oponent won the game
            # Lose effect
            self.update_turn_indicators(True)
            
            font = pygame.font.Font("img/gabriola.ttf", 28)
            font.set_bold(True)
            if self.gametype==self.VSOTHER:
                self.turn_right.set_image(font.render(self.PLAYER_WINS_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
            elif self.gametype==self.VSMACHINE:
                self.turn_right.set_image(font.render(self.MACHINE_WINS_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
            elif self.gametype==self.VSNET:
                self.turn_right.set_image(font.render(self.NET_WINS_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
            self.turn_right.set_pos(555-self.turn_right.rect.width/2.0, 26)
            self.turn_right.set_visible(True)
            
            self._finished = True
            pygame.time.set_timer(self.TIMER_SHOW_WINNER_EVENT, self.TIME_SHOW_WINNER)
        elif len(self.op_mazo)==0:
            # I won the game
            # Win effect
            self.update_turn_indicators(True)
            
            font = pygame.font.Font("img/gabriola.ttf", 28)
            font.set_bold(True)
            self.turn_left.set_image(font.render(self.PLAYER_WINS_TEXT, True, self.COLOR_FONT_ABOVE_LINE))
            self.turn_left.set_pos(45+self.turn_left.rect.width/2.0, 26) 
            self.turn_left.set_visible(True)         
            
            self._finished = True
            pygame.time.set_timer(self.TIMER_SHOW_WINNER_EVENT, self.TIME_SHOW_WINNER)