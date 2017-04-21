import os, logging, codecs
import olpcgames, pygame
from helpers import PosSprite, StatesSprite, Button, PosLayeredDirty
from controllers import *

log = logging.getLogger('Carteando')
log.setLevel(logging.DEBUG)

class CardData():
    
    @staticmethod
    def load_data():
        list_data = []
        filepath = os.path.join("img","values.cfg")
        f = codecs.open(filepath, "r", "utf_8")
        lines = f.readlines()        
        for line in lines:
            if not line.startswith("#"):
                tokens = line.split("\t")
                tokens = filter(None, tokens)
                if len(tokens)==7:
                    a_card = CardData()
                    a_card.id = tokens[0]
                    a_card.text = tokens[1]
                    a_card.values = []
                    for token in tokens[2:7]:
                        a_card.values.append(float(token)) 
                    list_data.append(a_card)
                else:
                    log.debug("LOAD DATA Line not length 7 - " + len(tokens).__str__() + " instead : " + line)
        return list_data
    
    def __init__(self):
        self.id = None
        self.text = None
        self.values = []

class Card(PosLayeredDirty):
    
    #Colors
    COLOR_FONT_NAME = (94,31,0)
    COLOR_FONT_ATTR_VALUE = (142,42,0)
    COLOR_FONT_ATTR_VALUE_H = (255,82,0)
    COLOR_BG = (255,255,255)
    
    def __init__(self, x, y, card_data):
        PosLayeredDirty.__init__(self, x, y)
        
        self.chosen_attribute = None
        self.data = card_data
        
        layer = 1

        ## IMAGES        
        # Front bg
        self.sprite_bg = PosSprite(x,y, "card_front_bg.png")
        self.add(self.sprite_bg, layer=layer)
        layer += 1        
        # Use all cards photos        
        self.sprite_photo = PosSprite(x+1,y-62, "card_photo_" + self.data.id + ".png")        
        self.add(self.sprite_photo, layer=layer)        
        layer += 1
        
        ySep = 19
        
        ## BUTTONS
        atrs = ["cadena", "tamanio", "velocidad", "poblacion", "reproduccion"]
        yBtn = y+28
        self.btn_atrs = []        
        for atr in atrs:
            btn = Button(x+3, yBtn, ["card_btn_" + atr +".png", "card_btn_" + atr + "_h.png"], False)
            self.btn_atrs.append(btn)
            self.add(btn, layer=layer)
            layer += 1
            yBtn += ySep        
        
        ## LABELS
        font = pygame.font.Font("img/gabriola.ttf", 32)
        #font.set_bold(True)                      
        self.label_name = PosSprite(x,y, font.render(self.data.text, True, self.COLOR_FONT_NAME))
        self.add(self.label_name, layer=layer)
        layer += 1
                
        font = pygame.font.Font("img/gabriola.ttf", 26)
        font.set_bold(True)
        self.values = self.data.values
        self.label_atrs = []
        yLbl = y+27
        for value in self.values:
            label = PosSprite(x+50,yLbl, font.render(int(value).__str__(), True, self.COLOR_FONT_ATTR_VALUE))
            self.label_atrs.append(label)
            self.add(label, layer=layer)
            layer += 1
            yLbl += ySep
            
        # BACKFACE IMAGE
        self.sprite_backface = PosSprite(x,y, "card_bg.png")        
        self.add(self.sprite_backface, layer=layer)
        layer += 1
        self.set_backface(False)
        
            
    def set_backface(self, value):
         self.backfaced = value
         self.sprite_backface.set_visible(value)
    
    
    def mouse_button_up(self):
        for btn in self.btn_atrs:
            if btn.is_over():
                self.choose_attribute(self.btn_atrs.index(btn))                
                return True
        return False
        
    def choose_attribute(self, idx):        
        self.disable_buttons()
        self.chosen_attribute = idx
        self.btn_atrs[idx].set_image(self.btn_atrs[idx].image_highlighted)
        
    def get_chosen_value(self):
        if self.chosen_attribute==None:
            return None
        else:
            return self.values[self.chosen_attribute]
    
    def disable_buttons(self):
        for btn in self.btn_atrs:
            btn.set_enabled(False)

    def move_from_mazo(self, sprite_mazo, end_point, callback):
        scq = SCQueue()
        scq.add(SCLinearPath(sprite_mazo.get_pos(), end_point, 0.5))
        scq.add(SCCallback(callback))
        self.add_controller(scq)
        
    def move_to_mazo(self, sprite_mazo, callback):
        scq = SCQueue()
        scq.add(SCLinearPath(self.get_pos(), sprite_mazo.get_pos(), 0.5))
        scq.add(SCCallback(callback))
        self.add_controller(scq)