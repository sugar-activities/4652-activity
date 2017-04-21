import pygame
import os
import logging

log = logging.getLogger('Carteando')
log.setLevel(logging.DEBUG)

class ResourceManager():
    
    #images = dict()
    scaled_images = dict()
    
    @staticmethod
    def load_image(imagefile):
        file = os.path.join("img",imagefile)    
        try:        
            return pygame.image.load(file).convert_alpha()
        except:
            raise UserWarning, "FAIL load image: " + file
    
    @staticmethod
    def check_image(imagefile):
        if imagefile not in ResourceManager.scaled_images:
            image = ResourceManager.load_image(imagefile)
            #ResourceManager.images[imagefile] = image            
            
            if WindowHelper.actual_scale_x()==1 and WindowHelper.actual_scale_y()==1:
                log.debug("Scaled image: " + imagefile + " : Scale1x")
                ResourceManager.scaled_images[imagefile] = image
            elif WindowHelper.actual_scale_x()==2 and WindowHelper.actual_scale_y()==2:
                log.debug("Scaled image: " + imagefile + " : Scale2x")
                ResourceManager.scaled_images[imagefile] = pygame.transform.scale2x(image)
            else:
                log.debug("Scaled image: " + imagefile + " : SmoothScale " + WindowHelper.actual_scale_x().__str__() + "x")
                scaled_x = int(image.get_width() * WindowHelper.actual_scale_x())
                scaled_y = int(image.get_height() * WindowHelper.actual_scale_y())
                ResourceManager.scaled_images[imagefile] = pygame.transform.smoothscale(image, (scaled_x, scaled_y))
    
    @staticmethod
    def get_image(imagefile):
        #ResourceManager.check_image(imagefile)        
        #return ResourceManager.images[imagefile]
    
        return ResourceManager.load_image(imagefile)
    
    @staticmethod
    def get_scaled_image(imagefile):
        ResourceManager.check_image(imagefile)        
        return ResourceManager.scaled_images[imagefile]
        

class WindowHelper():
    
    REFERENCE_COORDINATE_SYSTEM_X = float(600.0)
    REFERENCE_COORDINATE_SYSTEM_Y = float(320.0)
    size = (REFERENCE_COORDINATE_SYSTEM_X, REFERENCE_COORDINATE_SYSTEM_Y)
    scale_x = float(1)
    scale_y = float(1)
    offset_x = float(0)
    offset_y = float(0) 
    
    @staticmethod
    def set_size(x,y):
        WindowHelper.size = (x,y)
        WindowHelper.scale_x = WindowHelper.size[0]/WindowHelper.REFERENCE_COORDINATE_SYSTEM_X
        WindowHelper.scale_y = WindowHelper.size[1]/WindowHelper.REFERENCE_COORDINATE_SYSTEM_Y
        if WindowHelper.scale_y > WindowHelper.scale_x:            
            WindowHelper.scale_y = WindowHelper.scale_x
            WindowHelper.offset_y = abs(WindowHelper.size[1] - WindowHelper.REFERENCE_COORDINATE_SYSTEM_Y*WindowHelper.scale_y)/2.0
            WindowHelper.offset_x = float(0)
        elif WindowHelper.scale_x > WindowHelper.scale_y:            
            WindowHelper.scale_x = WindowHelper.scale_y
            WindowHelper.offset_x = abs(WindowHelper.size[0] - WindowHelper.REFERENCE_COORDINATE_SYSTEM_X*WindowHelper.scale_x)/2.0
            WindowHelper.offset_y = float(0)        
        
        log.debug("WindowHelper Actual scale: " + WindowHelper.actual_scale_x().__str__() + " - " + WindowHelper.actual_scale_y().__str__())
        log.debug("WindowHelper Virtual scale: " + WindowHelper.virtual_scale_x().__str__() + " - " + WindowHelper.virtual_scale_y().__str__())
        log.debug("WindowHelper Offset: " + WindowHelper.offset_x.__str__() + " - " + WindowHelper.offset_y.__str__())
    
    @staticmethod
    def actual_scale_x():        
        return WindowHelper.scale_x
    @staticmethod
    def actual_scale_y():
        return WindowHelper.scale_y
    
    @staticmethod
    def virtual_scale_x():
        return 1 / WindowHelper.scale_x
    @staticmethod
    def virtual_scale_y():
        return 1 / WindowHelper.scale_y
    
        
    @staticmethod
    def to_actual_pos(x, y):
        """ Get position for actual screen resolution, passed an 800x600 based one 
        """
        newX = WindowHelper.offset_x + x * WindowHelper.actual_scale_x()
        newY = WindowHelper.offset_y + y * WindowHelper.actual_scale_y()
        return newX, newY    
    @staticmethod
    def to_actual_x(x):
        """ Get position for actual screen resolution, passed an 800x600 based one 
        """
        newX = WindowHelper.offset_x + x * WindowHelper.actual_scale_x()
        #log.debug("relative_x: size-" + WindowHelper.size.__str__() + " input-" + x.__str__() + " output-" + newX.__str__())
        return newX    
    @staticmethod
    def to_actual_y(y):
        """ Get position for actual screen resolution, passed an 800x600 based one 
        """
        newY = WindowHelper.offset_y + y * WindowHelper.actual_scale_y()
        #log.debug("relative_y: size-" + WindowHelper.size.__str__() + " input-" + y.__str__() + " output-" + newY.__str__())
        return newY
    
    @staticmethod
    def to_virtual_pos(x, y):
        """ Get position for virtual 800x600 screen resolution, passed actual one 
        """
        newX = (x - WindowHelper.offset_x) * WindowHelper.virtual_scale_x()
        newY = (y - WindowHelper.offset_y) * WindowHelper.virtual_scale_y()
        return newX, newY    
    @staticmethod
    def to_virtual_x(x):
        """ Get position for virtual 800x600 screen resolution, passed actual one 
        """
        newX = (x - WindowHelper.offset_x) * WindowHelper.virtual_scale_x()
        #log.debug("relative_x: size-" + WindowHelper.size.__str__() + " input-" + x.__str__() + " output-" + newX.__str__())
        return newX    
    @staticmethod
    def to_virtual_y(y):
        """ Get position for virtual 800x600 screen resolution, passed actual one 
        """
        newY = (y - WindowHelper.offset_y) * WindowHelper.virtual_scale_y()
        #log.debug("relative_y: size-" + WindowHelper.size.__str__() + " input-" + y.__str__() + " output-" + newY.__str__())
        return newY


class PosSprite(pygame.sprite.DirtySprite):
    """ pygame.sprite.DirtySprite with Position and Scale.
    Position from outside, i.e. set_pos() and get_pos() function calls, are based in the 800x600 coordinate system.
    Actual positions, i.e. x and y attributes, are automatically calculated to actual screen.
    Scale is automatically calculated to actual screen to.
    Rect is always in actual coordinate system.
    """
   
    def __init__(self, x, y, image):
        pygame.sprite.DirtySprite.__init__(self)
        self.x = WindowHelper.to_actual_x(x)
        self.y = WindowHelper.to_actual_y(y)
        self.scale_x = WindowHelper.actual_scale_x()
        self.scale_y = WindowHelper.actual_scale_y()
        self.image = None        
        if isinstance(image, basestring):
            self.imagefile = image            
            self.set_image(ResourceManager.get_scaled_image(image))
        else:
            self.imagefile = None
            self.set_image(image)
        self.controllers = []
    
    def set_image(self, image):
        #self.image = pygame.transform.scale(image, (int(image.get_width() * self.scale_x), int(image.get_height() * self.scale_y)))
        #self.image = pygame.transform.smoothscale(image, (int(image.get_width() * self.scale_x), int(image.get_height() * self.scale_y)))
        self.image = image
        self.rect = self.image.get_rect()                        
        self.rect.centerx = self.x
        self.rect.centery = self.y
        # For next draw() in LayeredDirty to draw it
        if self.dirty==0:
            self.dirty = 1
            
    def set_pos(self, x, y):
        self.x = WindowHelper.to_actual_x(x)
        self.y = WindowHelper.to_actual_y(y)
        self.rect.centerx = self.x
        self.rect.centery = self.y
        # For next draw() in LayeredDirty to draw it
        if self.dirty==0:
            self.dirty = 1

    def get_pos(self):
        return (WindowHelper.to_virtual_x(self.x), WindowHelper.to_virtual_y(self.y))

    def set_scale(self, scale_x, scale_y):
        old_scale_x = self.scale_x
        old_scale_y = self.scale_y
        
        self.scale_x = scale_x
        self.scale_y = scale_y
        if self.imagefile==None:
            #self.set_image(pygame.transform.scale(self.image, (int(self.image.get_widht() * 1/old_scale_x), int(self.image.get_height() * 1/old_scale_y))))
            self.set_image(pygame.transform.smoothscale(self.image, (int(self.image.get_widht() * 1/old_scale_x), int(self.image.get_height() * 1/old_scale_y))))
        else:
            image = ResourceManager.get_image(self.imagefile)
            self.set_image(pygame.transform.smoothscale(image, (int(self.scale_x), int(self.scale_y))))
        
    def get_scale(self):
        return self.scale_x, self.scale_y

    def is_over(self):
        if not self._visible:
            return False
            
        if hasattr(self, "mask"):
            mask_coords = (pygame.mouse.get_pos()[0] - self.rect.left, pygame.mouse.get_pos()[1] - self.rect.top)
            if (mask_coords[0] < 0 or mask_coords[0] >= self.mask.get_size()[0] or 
                mask_coords[1] < 0 or mask_coords[1] >= self.mask.get_size()[1]):                
                return False
            else:
                return self.mask.get_at(mask_coords)
        else:
            return self.rect.collidepoint(pygame.mouse.get_pos()) 
    
    # Defining set_visible and get_visible to outside
    # Using _set_visible and _get_visible from DirtySprite
    def set_visible(self, value):
        self._set_visible(value)        
    def get_visible(self):
        return self._get_visible()
    
    def add_controller(self, controller):
        self.controllers.append(controller)
        controller.on_added(self)
    
    def get_controllers(self):
        return self.controllers
    
    def update(self, seconds):
        sclist = self.controllers
        for controller in sclist:            
            if controller.update(seconds):
                self.controllers.remove(controller)
                
    def finish_controllers(self):
        sclist = self.controllers
        for controller in sclist:            
            controller.finish()
            self.controllers.remove(controller)
    
    

class StatesSprite(PosSprite):
    
    def __init__(self, x, y, imagefiles):
        PosSprite.__init__(self, x, y, imagefiles[0])
        self.images = map(ResourceManager.get_scaled_image, imagefiles)
        self.imagefiles = imagefiles
        self.state_idx = 0        
        
    def set_state(self, state_idx):
        self.imagefile = self.imagefiles[state_idx]
        self.set_image(self.images[state_idx])
        self.state_idx = state_idx
        
    def get_state(self):
        return self.state_idx
    
    def get_states_quantity(self):
        return len(self.images)


class Button(PosSprite):
    
    def __init__(self, x, y, imagefiles, use_mask=True):
        self.use_mask = use_mask
        PosSprite.__init__(self, x, y, imagefiles[0])
        
        self.imagefile_normal = imagefiles[0]
        self.image_normal = ResourceManager.get_scaled_image(imagefiles[0])
        self.imagefile_highlighted = imagefiles[1]
        self.image_highlighted = ResourceManager.get_scaled_image(imagefiles[1])
        
        if len(imagefiles) > 2:
            self.imagefile_disabled = imagefiles[2]
            self.image_disabled = ResourceManager.get_scaled_image(imagefiles[2])
        else:
            self.imagefile_disabled = imagefiles[0]
            self.image_disabled = self.image_normal
        self.enabled = True        
        
    def set_image(self, image):
        PosSprite.set_image(self, image)
        if self.use_mask:
            self.mask = pygame.mask.from_surface(self.image, 127)        
        
    def set_enabled(self, enabled):
        self.enabled = enabled
        if self.enabled:
            self.imagefile = self.imagefile_normal
            self.set_image(self.image_normal)
        else:
            self.imagefile = self.imagefile_disabled
            self.set_image(self.image_disabled)    
            
    def is_over(self):
        return self.enabled and PosSprite.is_over(self)
    
    def update(self, seconds):   
        PosSprite.update(self, seconds)
        if self.enabled:
            if self.is_over():
                self.imagefile = self.imagefile_highlighted
                self.set_image(self.image_highlighted)
            else:
                self.imagefile = self.imagefile_normal
                self.set_image(self.image_normal)
                
                
class PosLayeredDirty(pygame.sprite.LayeredDirty):
    """PosLayeredDirty pygame.sprite.LayeredDirty handles sprite movements
    (if sprites are PosSprite) using initial sprite offsets    
    """
    
    
    def __init__(self, x, y):
        pygame.sprite.LayeredDirty.__init__(self)        
        self.x = WindowHelper.to_actual_x(x)
        self.y = WindowHelper.to_actual_y(y)
        self.controllers = []
        
    def set_pos(self, x, y):
        dx = x - WindowHelper.to_virtual_x(self.x)
        dy = y - WindowHelper.to_virtual_y(self.y)
        for sprite in self.sprites():
            if isinstance(sprite, PosSprite):
                sprite.set_pos(sprite.get_pos()[0] + dx, sprite.get_pos()[1] + dy)
        self.x = WindowHelper.to_actual_x(x)
        self.y = WindowHelper.to_actual_y(y)
    
    def get_pos(self):
        return (WindowHelper.to_virtual_x(self.x), WindowHelper.to_virtual_y(self.y))
    
    def is_over(self):
        for sprite in self.sprites():
            if isinstance(sprite, PosSprite) and sprite.is_over():
                return True
        return False
    
    def add_controller(self, controller):
        self.controllers.append(controller)
        controller.on_added(self)
    
    def get_controllers(self):
        return self.controllers
    
    def update(self, seconds):
        sclist = self.controllers
        for controller in sclist:            
            if controller.update(seconds):
                self.controllers.remove(controller)
                
    def finish_controllers(self):
        sclist = self.controllers
        for controller in sclist:            
            controller.finish()
            self.controllers.remove(controller)
