import logging
import olpcgames.mesh as mesh

log = logging.getLogger('Carteando')
log.setLevel(logging.DEBUG)

class Connection():
       
    def __init__(self):
        # Connection state variables
        self.initiator = False
        self.connected = False
        self.friend_connected = False        
        self.friend_handle = None
        
        self.invitation_started = False
        self.invitation_mazo = []
        
    
    def process_event(self, event):
        if event.type==mesh.CONNECT:
            log.debug("CONNECT")
            self.connected = True
            if mesh.is_initiating():
                self.initiator = True
        elif event.type==mesh.PARTICIPANT_ADD:
            log.debug("PARTICIPANT_ADD")
            # If participant added to the application, not me
            if event.handle <> mesh.my_handle():
                self.friend_connected = True
                self.friend_handle = event.handle                
        elif event.type==mesh.PARTICIPANT_REMOVE:
            log.debug("PARTICIPANT_REMOVE")
            # If friend I am playing with stopped
            if event.handle == self.friend_handle:
                self.friend_connected = False
                self.friend_handle = None
                if self.game<>None:
                    self.game.stop()               
        elif event.type==mesh.MESSAGE_MULTI:
            log.debug("MESSAGE_MULTI")
        elif event.type==mesh.MESSAGE_UNI:
            log.debug("MESSAGE_UNI: " + event.content)
            toks = event.content.split(':')
            if toks[0]<>'startedGame' and self.game==None:
                log.error("Message received without Game opened")
            # startedGame Message
            elif toks[0]=='startedGame':            
                if self.initiator:
                    log.error("startedGame from other not initiator")
                else:
                    # Start game at receiving friend side
                    self.invitation_started = True
                    # Receive sorted cards                    
                    mazo = eval(toks[1])     
                    self.invitation_mazo = mazo
            # openCards Message
            elif toks[0]=='openCards':
                self.game.open_cards(True)
            # attributeSelected Message
            elif toks[0]=='attributeSelected':
                attr = eval(toks[1])                    
                self.game.attribute_selected(attr, True)
            # stop Message
            elif toks[0]=='stop':
                self.game.stop(True)
            # finishShowingCards Message
            elif toks[0]=='finishShowCards':
                insertion_order = eval(toks[1])
                self.game.finish_show_cards(True, insertion_order)
        else:
            return False
        return True                    

    
    def set_playing_game(self, game):
        # Game==None means back to MM
        self.game = game
        if game==None:
            self.invitation_started = False
            self.invitation_mazo = []
    
    
    # To Send Messages through Mesh
    
    def start_net_game(self, mazo):        
        mesh.send_to(self.friend_handle, "startedGame:" + mazo.__str__())
    
    def open_cards(self):
        mesh.send_to(self.friend_handle, "openCards:")
        
    def attribute_selected(self, chosen_attribute):
        mesh.send_to(self.friend_handle, "attributeSelected:" + chosen_attribute.__str__())
        
    def finish_show_cards(self, insertion_order):
        mesh.send_to(self.friend_handle, "finishShowCards:" + insertion_order.__str__())
        
    def stop(self):
        mesh.send_to(self.friend_handle, "stop:")
    