# Example file showing a circle moving on screen
import pygame
import config as cfg
import sys,os,glob,math,random,logging,time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
import re

# prompt for eye; set cfg.prompt_for_eye to False to stop this behavior
eyes = ['RE','LE']
if cfg.prompt_for_eye:
    eye = input('Eye: RE or LE? (%s) '%cfg.default_eye).upper()
else:
    eye = cfg.default_eye

if eye=='':
    eye = cfg.default_eye
    
try:
    assert eye in eyes
except AssertionError as ae:
    print('%s is not in %s, setting to default %s'%(eye,eyes,cfg.default_eye))
    eye = cfg.default_eye

eye_index = eyes.index(eye)



# load location script
try:
    from location_script import location_script
except ImportError:
    location_script = [(0.0,0.0)]
    
pygame.init()
pygame.font.init() 

named_tuple = time.localtime()
date_string = time.strftime("%Y%m%d", named_tuple)
log_filename = date_string+'.log'
log_path = os.path.join(cfg.log_folder,log_filename)
os.makedirs(cfg.log_folder,exist_ok=True)
os.makedirs(cfg.data_folder,exist_ok=True)

logger = logging.getLogger(__name__)
logging.basicConfig(filename=log_path, encoding='utf-8', level=logging.INFO)


with open(os.path.join(cfg.data_folder,'fonts_available.log'),'w') as fid:
    font_list = sorted(pygame.font.get_fonts())
    for item in font_list:
        fid.write('%s\n'%item)

def log(message):
    named_tuple = time.localtime()
    formatted_time = time.strftime("%Y.%m.%d.%H.%M.%S", named_tuple)
    logger.info('%s: %s'%(formatted_time,message))

my_font = pygame.font.SysFont(cfg.text_font, cfg.text_font_size)

# pygame setup
try:
    sdl_x = cfg.DEFAULT_DISPLAY_X_OFFSET
except Exception as e:
    sdl_x = 0
sdl_y = 0
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{sdl_x},{sdl_y}"

screen = pygame.display.set_mode(cfg.display_mode,display=cfg.monitor_number)
clock = pygame.time.Clock()
running = True
dt = 0

global bgc
bgc = cfg.background_color

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)


class ObserverHandler(FileSystemEventHandler):
    def __init__(self,target):
        super().__init__()
        self.target = target
    def on_created(self,event):
        filename = event.src_path
        ext = os.path.splitext(filename)[-1]
        if ext.lower() in cfg.data_monitoring_extensions:
            outfn = filename.replace(ext,'')+'_'+tar.ecc()+'.looky'
            outstr = '%s: %s'%(eye,self.target.ecc())
            with open(outfn,'w') as fid:
                fid.write(outstr)
            try:
                assert os.path.exists(outfn)
            except AssertionError:
                sys.exit('ObserverHandler failed to write .looky file.')
            if cfg.auto_advance:
                time.sleep(cfg.auto_advance_delay)
                self.target.next()
            log('%s file found at %s, eccentricity written to %s'%(ext,filename,outfn))
            log('Auto-advance to %s'%self.target.ecc())            
        
        if re.search(r'.*_stimuli_.*V_adjustCWlooky.txt', filename) and cfg.cycleBgColor_flag and cfg.AutoCycleBg:
           self.target.cyclebg()
           
            
            
            
            
                
class Target:
    def __str__(self):
        return '%0.2f,%0.2f'%(self.position_vector.x/cfg.pixels_per_deg,
                              self.position_vector.y/cfg.pixels_per_deg)
    
    def __init__(self,step=None,small_step=None):
        self.location_index = 0
        x,y = [k*cfg.pixels_per_deg for k in location_script[self.location_index]]
        #x,y = 0.0,0.0
        
        self.position_vector = pygame.Vector2(x,y)
        if step is None:
            self.step = cfg.target_step*cfg.pixels_per_deg
        else:
            self.step = step
            
        if small_step is None:
            self.small_step = cfg.target_small_step*cfg.pixels_per_deg
        else:
            self.small_step = small_step

        self.age = 0.0
        self.logged = False
        self.radius = cfg.target_radius*cfg.pixels_per_deg
        self.foreground_color = cfg.foreground_color
        self.background_color = cfg.background_color
        self.bgindex = 0

    def next(self):
        self.location_index = (self.location_index+1)%len(location_script)
        x,y = [k*cfg.pixels_per_deg for k in location_script[self.location_index]]
        self.move(x,y,absolute=True)
        
    def previous(self):
        self.location_index = (self.location_index-1)%len(location_script)
        x,y = [k*cfg.pixels_per_deg for k in location_script[self.location_index]]
        self.move(x,y,absolute=True)
        
        
    def move(self,dx,dy,absolute=False):
        if absolute:
            self.position_vector.x = dx
            self.position_vector.y = dy
        else:
            self.position_vector.x+=dx
            self.position_vector.y+=dy
        self.logged = False
        self.age = 0.0

    def left(self,fine=False):
        if fine:
            self.move(-self.small_step,0)
        else:
            self.move(-self.step,0)

    def right(self,fine=False):
        if fine:
            self.move(self.small_step,0)
        else:
            self.move(self.step,0)
            
    def up(self,fine=False):
        if fine:
            self.move(0,-self.small_step)
        else:
            self.move(0,-self.step)
            
    def down(self,fine=False):
        if fine:
            self.move(0,self.small_step)
        else:
            self.move(0,self.step)

    def ecc(self):
        x = self.position_vector.x/cfg.pixels_per_deg
        y = self.position_vector.y/cfg.pixels_per_deg
        if eye=='RE':
            if x>0:
                h = 'T'
            elif x<0:
                h = 'N'
            else:
                h = 'C'
        else:
            if x>0:
                h = 'N'
            elif x<0:
                h = 'T'
            else:
                h = 'C'
        if y>0:
            v = 'S'
        elif y<0:
            v = 'I'
        else:
            v = 'C'
        return '%0.0f%s_%0.0f%s'%(abs(x),h,abs(y),v)

    def brightenfg(self):
        newcolor = [np.clip(c+cfg.color_increment,0,255).astype(int) for c in self.foreground_color]
        self.foreground_color = tuple(newcolor)

    def darkenfg(self):
        newcolor = [np.clip(c-cfg.color_increment,0,255).astype(int) for c in self.foreground_color]
        self.foreground_color = tuple(newcolor)

    def brightenbg(self):       
        newcolor = [np.clip(c+cfg.color_increment,0,255).astype(int) for c in self.background_color]
        self.background_color = tuple(newcolor)
        print(f'############\n background:{self.background_color} \n##################\n')
        

    def darkenbg(self):
        if cfg.cycleBgColor_flag:
            self.cyclebg()
        else:    
            newcolor = [np.clip(c-cfg.color_increment,0,255).astype(int) for c in self.background_color]
            self.background_color = tuple(newcolor)
            print(f'############\n background:{self.background_color} \n##################\n')
        
            
    def cyclebg(self):
        global bgc
        self.bgindex = (self.bgindex+1)%len(cfg.Garray_bgColor)
        Garray = np.array(cfg.Garray_bgColor)
        try:
            # find largest element strictly smaller than Gset
            Gnew = Garray[self.bgindex]
            if Gnew is not None:
                newcolor = (self.background_color[0], int(Gnew), self.background_color[2])
            else:
                newcolor = self.background_color
        except Exception as e:
            print(f"Error while setting new background: {e}")
            newcolor = self.background_color    

        self.background_color = tuple(newcolor)
        bgc = self.background_color
        print(f'############\n background:{self.background_color} \n##################\n')
        # Save new bg to text file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_bg_R{self.background_color[0]}G{self.background_color[1]}B{self.background_color[2]}.txt"
        bgsavepath = os.path.join(cfg.data_monitoring_folder, filename)
        with open(bgsavepath, "w") as f:
            f.write(str(self.background_color))
            print('saved!')
        
    
import subprocess
def run_external_script(script):
    """Run single_flash_labjack.py in background, open empty console, and run cycle_background after closing it."""
    try:
        # Start single_flash_labjack.py normally in background
        subprocess.Popen([sys.executable, script])
        print(f"{script} started.")
        # # Path to the temporary text file
        # txt_path = r"C:\FDML_data\temp_console.txt"
        # # Create the text file if it doesn't exist
        # if not os.path.exists(txt_path):
        #     with open(txt_path, "w") as f:
        #         f.write("Close this file to continue...")
        # # Open the text file using default application (Notepad)
        # process = subprocess.Popen(["notepad.exe", txt_path])
        # # Wait for the user to close Notepad
        # process.wait()
        # print("Text file closed. Running cycle_background_colors...")     
        # #########this is for light adaptation
        # #cycle_background_colors()  # change the fixation screen color   

    except Exception as e:
        print('Error running %s: %s'%(script,e))    

class Origin(Target):
    
    def __init__(self):
        super().__init__(step=cfg.origin_step_px,small_step=cfg.origin_small_step_px)
        try:
            with open(os.path.join(cfg.data_folder,cfg.origin_filename),'r') as fid:
                origin_x,origin_y = [float(k) for k in fid.read().split(',')]
        except FileNotFoundError:
            origin_x,origin_y = [k/2.0 for k in cfg.display_mode]

        self.position_vector = pygame.Vector2(origin_x,origin_y)
            
        self.size = cfg.origin_size_px
        self.foreground_color = cfg.origin_color
        self.linewidth = cfg.origin_line_width

    def move(self,dx,dy):
        super().move(dx,dy)
        with open(os.path.join(cfg.data_folder,cfg.origin_filename),'w') as fid:
            x = self.position_vector.x
            y = self.position_vector.y
            fid.write('%0.1f,%01.f'%(x,y))
        
    def draw(self,screen):
        pygame.draw.line(screen,self.foreground_color,pygame.Vector2(self.position_vector.x-self.size,self.position_vector.y),pygame.Vector2(self.position_vector.x+self.size,self.position_vector.y),self.linewidth)
        pygame.draw.line(screen,self.foreground_color,pygame.Vector2(self.position_vector.x,self.position_vector.y-self.size),pygame.Vector2(self.position_vector.x,self.position_vector.y+self.size),self.linewidth)
                         
class Star(Target):

    def __init__(self):
        super().__init__()
        self.thetas = [k*math.pi/4.0 for k in range(8)]
        self.linewidth = cfg.target_line_width

    def draw(self, screen, origin=None):
        if origin is None:
            xoff = 0.0
            yoff = 0.0
        else:
            xoff = origin.position_vector.x
            yoff = origin.position_vector.y

        x0 = self.position_vector.x+xoff
        y0 = self.position_vector.y+yoff
        
        for theta in self.thetas:
            x1 = math.sin(theta)*self.radius+x0
            y1 = math.cos(theta)*self.radius+y0
            
            pygame.draw.line(screen, self.foreground_color, pygame.Vector2(x0,y0), pygame.Vector2(x1,y1), self.linewidth)

class Bullseye(Target):

    def __init__(self):
        super().__init__()
        self.linewidth = cfg.target_line_width
        self.radii = [k*self.radius/8.0 for k in range(8,0,-1)]
        self.radii.append(0.25*self.radius/8.0)
        self.ring_colors = []
        for idx in range(len(self.radii)):
            self.ring_colors.append(cfg.colors[idx%2])
            
    def draw(self, screen, origin=None):
        if origin is None:
            xoff = 0.0
            yoff = 0.0
        else:
            xoff = origin.position_vector.x
            yoff = origin.position_vector.y

        x0 = self.position_vector.x+xoff
        y0 = self.position_vector.y+yoff

        for radius,color in zip(self.radii,self.ring_colors):
            pygame.draw.circle(screen, color, pygame.Vector2(x0,y0), radius)


class ABC(Target):

    def __init__(self):
        super().__init__()
        
    def draw(self, screen, origin=None):
        if origin is None:
            xoff = 0.0
            yoff = 0.0
        else:
            xoff = origin.position_vector.x
            yoff = origin.position_vector.y

        x = self.position_vector.x+xoff
        y = self.position_vector.y+yoff
        
        pygame.draw.circle(screen, self.foreground_color, pygame.Vector2(x,y),self.radius)
        bar_width = self.radius/4.0
        b1x = x-self.radius
        b1y = y-bar_width/2.0
        b1w = self.radius*2
        b1h = bar_width
        b2x = x-bar_width/2.0
        b2y = y-self.radius
        b2w = bar_width
        b2h = self.radius*2
        r1 = pygame.Rect(b1x,b1y,b1w,b1h)
        r2 = pygame.Rect(b2x,b2y,b2w,b2h)
        pygame.draw.rect(screen,self.background_color,r1)
        pygame.draw.rect(screen,self.background_color,r2)
        pygame.draw.circle(screen,self.foreground_color,pygame.Vector2(x,y),bar_width/2.0)

            
class Inset:
    visible = False
    def __init__(self, width, height, x, y, update_frequency=5.0):
        self.width = int(round(width))
        self.height = int(round(height))
        self.x = x-width/2.0
        self.y = y-height/2.0
        self.update_frequency = update_frequency
        
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(cfg.inset_background_color)
        self.clock = pygame.time.Clock()
        self.last_update_time = 0.0
        #self.visible = False

    def toggle(self):
        self.visible = not self.visible
        
    def draw(self, screen, origin = None):
        if origin is None:
            xoff = 0.0
            yoff = 0.0
        else:
            xoff = origin.position_vector.x
            yoff = origin.position_vector.y
            
        dt = self.clock.tick()*1e-3
        self.last_update_time = self.last_update_time + dt
        if self.last_update_time>=1/self.update_frequency:
            self.update()
            self.last_update_time = 0.0
        screen.blit(self.surface, (self.x+xoff, self.y+yoff))
        
    def update(self):
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        self.surface.fill((r,g,b))


class DeadLeaves(Inset):

    def __init__(self):
        xoff = origin.position_vector.x
        yoff = origin.position_vector.y
        
        super().__init__(cfg.inset_width_deg*cfg.pixels_per_deg,
                         cfg.inset_height_deg*cfg.pixels_per_deg,
                         cfg.inset_x_deg*cfg.pixels_per_deg,
                         cfg.inset_y_deg*cfg.pixels_per_deg,
                         cfg.deadleaves_frequency)
        self.s1 = pygame.Surface((self.width,self.height))
        self.s2 = pygame.Surface((self.width,self.height))
        g = cfg.deadleaves_gray_mean
        self.s1.fill((g,g,g))
        self.s2.fill((g,g,g))
        n_ellipses = cfg.deadleaves_n_ellipses
        mu = cfg.deadleaves_rad_mean_deg*2*cfg.pixels_per_deg
        sigma = cfg.deadleaves_rad_std_deg*2*cfg.pixels_per_deg
        self.counter = 0
        self.surfaces = [self.s1,self.s2]
        random.seed(cfg.deadleaves_seed)
        for k in range(n_ellipses):
            width = random.gauss(mu,sigma)
            height = random.gauss(mu,sigma)

            left = random.randint(0,int(self.width))-width//2
            top = random.randint(0,int(self.height))-height//2
            rect = pygame.Rect(left,top,width,height)
            
            gray_shift = random.randint(0,cfg.deadleaves_gray_range)-cfg.deadleaves_gray_range//2#+cfg.deadleaves_gray_mean
            gray1 = cfg.deadleaves_gray_mean+gray_shift
            gray2 = cfg.deadleaves_gray_mean-gray_shift
            
            gray1 = max(0,gray1)
            gray1 = min(gray1,255)
            gray2 = max(0,gray2)
            gray2 = min(gray2,255)
            
            alpha = cfg.deadleaves_alpha
            pygame.draw.ellipse(self.s1,(gray1,gray1,gray1,alpha),rect)
            pygame.draw.ellipse(self.s2,(gray2,gray2,gray2,alpha),rect)
        pygame.image.save(self.s1,os.path.join(cfg.data_folder,'deadleaves_1.png'))
        pygame.image.save(self.s2,os.path.join(cfg.data_folder,'deadleaves_2.png'))

    def update(self):
        self.surface = self.surfaces[self.counter]
        self.counter = (self.counter+1)%2

class CheckerBoard(Inset):

    def __init__(self):
        xoff = origin.position_vector.x
        yoff = origin.position_vector.y
        
        super().__init__(cfg.inset_width_deg*cfg.pixels_per_deg,
                         cfg.inset_height_deg*cfg.pixels_per_deg,
                         cfg.inset_x_deg*cfg.pixels_per_deg,
                         cfg.inset_y_deg*cfg.pixels_per_deg,
                         cfg.checkerboard_frequency)
        self.s1 = pygame.Surface((self.width,self.height))
        self.s2 = pygame.Surface((self.width,self.height))
        self.s1.fill((0,0,0))
        self.s2.fill((0,0,0))

        self.counter = 0
        
        rheight = self.height/cfg.checkerboard_n_rows
        rwidth = self.width/cfg.checkerboard_n_cols

        ry = 0

        colors = [cfg.checkerboard_bright,cfg.checkerboard_dark]
        for row in range(int(cfg.checkerboard_n_rows)):
            rx = 0
            for col in range(int(cfg.checkerboard_n_cols)):
                rect = pygame.Rect(rx,ry,rwidth,rheight)
                pygame.draw.rect(self.s1,colors[(row+col)%2],rect)
                pygame.draw.rect(self.s2,colors[(row+col+1)%2],rect)
                rx = rx + rwidth
            ry = ry + rheight
                
        pygame.image.save(self.s1,os.path.join(cfg.data_folder,'checkerboard_1.png'))
        pygame.image.save(self.s2,os.path.join(cfg.data_folder,'checkerboard_2.png'))
        self.surfaces = [self.s1,self.s2]
        
    def update(self):
        self.surface = self.surfaces[self.counter]
        self.counter = (self.counter+1)%2

        

class Grating(Inset):

    def __init__(self):
        xoff = origin.position_vector.x
        yoff = origin.position_vector.y
        
        super().__init__(cfg.inset_width_deg*cfg.pixels_per_deg,
                         cfg.inset_height_deg*cfg.pixels_per_deg,
                         cfg.inset_x_deg*cfg.pixels_per_deg,
                         cfg.inset_y_deg*cfg.pixels_per_deg,
                         cfg.grating_frequency_fps)

        self.orientation = cfg.grating_orientation
        sc = 3
        self.grating = np.zeros((self.width,self.height),dtype=np.uint8)

        if self.orientation=='vertical':
            n_cycles = cfg.inset_width_deg/cfg.grating_period_deg
        else:
            n_cycles = cfg.inset_height_deg/cfg.grating_period_deg
        
        XX,YY = np.meshgrid(np.arange(self.height),np.arange(self.width))
        YY = YY/self.width*2*np.pi*n_cycles
        XX = XX/self.height*2*np.pi*n_cycles
        
        if self.orientation=='vertical':
            basis = YY
            npix = self.width
        else:
            basis = XX
            npix = self.height

        self.grating = np.round(127.5*(1+np.sin(basis))).astype(np.uint8)
        self.grating3 = np.transpose(np.array([self.grating]*3),(1,2,0))
        self.surface = pygame.surfarray.make_surface(self.grating3)
        
        px_per_cycle = npix/n_cycles
        self.nroll = int(round(cfg.grating_cycles_per_second*px_per_cycle/cfg.grating_frequency_fps))
        
    def update(self):
        if self.orientation=='vertical':
            self.grating3 = np.roll(self.grating3,self.nroll,axis=0)
        else:
            self.grating3 = np.roll(self.grating3,self.nroll,axis=1)
            
        self.surface = pygame.surfarray.make_surface(self.grating3)
        

class UserWindow:

    def __init__(self):
        dpi = cfg.user_window_dpi
        sxpx,sypx = cfg.display_mode
        sxin,syin = sxpx/dpi,sypx/dpi
        xborder = sxpx*0.01
        yborder = sypx*0.01
        plt.ion()
        self.fig = plt.figure(figsize=(sxin,syin))
        self.ax = self.fig.add_axes([0,0,1,1])
        self.ax.set_xlim((0,sxpx))
        self.ax.set_ylim((sypx,0))
        self.ohandle = plt.plot(0,0,'r+',markersize=12)[0]
        self.thandle = plt.plot(0,0,'ko',markersize=12)[0]
        self.mhandle = plt.text(xborder,yborder,'foo',ha='left',va='top')
        self.age = 0.0
        self.fig.show()
    def update(self,origin,target,message):
        self.age = 0.0
        self.ohandle.set_xdata([origin.position_vector.x])
        self.ohandle.set_ydata([origin.position_vector.y])
        self.thandle.set_xdata([origin.position_vector.x+target.position_vector.x])
        self.thandle.set_ydata([origin.position_vector.y+target.position_vector.y])

        self.mhandle.set_text(message)
        self.fig.canvas.flush_events()
        
# if cfg.target_type=='bullseye':
#     tar = Bullseye()
# elif cfg.target_type=='star':
#     tar = Star()
# elif cfg.target_type=='ABC':
#     tar = ABC()
# else:
#     sys.exit('%s is an invalid target_type in config.py')

tar_dict = {'bullseye':Bullseye,
            'star':Star,
            'ABC':ABC}
try:
    tar = tar_dict[cfg.target_type]()
except KeyError as ke:
    print('KeyError: '+ke)
    sys.exit('config.%s is not a valid target type'%cfg.target_type)
    
tar_keys = list(tar_dict.keys())
n_tars = len(tar_keys)
tar_index = tar_keys.index(cfg.target_type)

origin = Origin()
    
step = cfg.target_step*cfg.pixels_per_deg
small_step = cfg.target_small_step*cfg.pixels_per_deg

inset_dict = {'deadleaves':DeadLeaves,
              'grating':Grating,
              'checkerboard':CheckerBoard}

inset = inset_dict[cfg.inset_type]()
inset_keys = list(inset_dict.keys())
n_insets = len(inset_keys)
inset_index = inset_keys.index(cfg.inset_type)


if cfg.data_monitoring:
    try:
        path = cfg.data_monitoring_folder
        event_handler = ObserverHandler(tar)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
    except AttributeError as ae:
        print('data_monitoring_folder not set in config.py. Proceeding without data monitoring.')
        pass
    except FileNotFoundError as fnfe:
        print('data_monitoring_folder %s not found. Please edit config.py as required.'%cfg.data_monitoring_folder)
        sys.exit()


def close_match(tup,tup_list,tolerance=0.01):
    out = -1
    x0,y0 = tup
    for idx,(x,y) in enumerate(tup_list):
        d = math.sqrt((y0-y)**2+(x0-x)**2)
        if d<tolerance:
            out = idx
            break
    return out

def write_test_file():
    basefn = '%d%s'%(random.randint(0,int(1e15)),cfg.data_monitoring_extensions[0])
    outfn = os.path.join(cfg.data_monitoring_folder,basefn)
    with open(outfn,'w') as fid:
        fid.write('0')

if cfg.user_window:
    uwin = UserWindow()
    



while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False

        mods = pygame.key.get_mods()
        
        origin_mode = mods & pygame.KMOD_ALT
        fine_mode = mods & pygame.KMOD_SHIFT
        
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                if origin_mode:
                    origin.left(fine_mode)
                else:
                    tar.left(fine_mode)
                    
            if event.key == pygame.K_RIGHT:
                if origin_mode:
                    origin.right(fine_mode)
                else:
                    tar.right(fine_mode)
                    
            if event.key == pygame.K_UP:
                if origin_mode:
                    origin.up(fine_mode)
                else:
                    tar.up(fine_mode)
                    
            if event.key == pygame.K_DOWN:
                if origin_mode:
                    origin.down(fine_mode)
                else:
                    tar.down(fine_mode)


            if event.key == pygame.K_PAGEUP:
                if origin_mode:
                    pass
                else:
                    tar.previous()

            if event.key == pygame.K_PAGEDOWN:
                if origin_mode:
                    pass
                else:
                    tar.next()

            if event.key == pygame.K_i:
                if mods & pygame.KMOD_CTRL:
                    inset_index = (inset_index+1)%n_insets
                    visibility = inset.visible
                    inset = inset_dict[inset_keys[inset_index]]()
                    inset.visible = visibility
                else:
                    inset.toggle()
                    
            if event.key == pygame.K_t:
                if mods & pygame.KMOD_CTRL:
                    tar_index = (tar_index+1)%n_tars
                    pv = tar.position_vector
                    tar = tar_dict[tar_keys[tar_index]]()
                    tar.position_vector = pv
                
            if event.key in [pygame.K_ESCAPE,pygame.K_q]:
                running = False

            if event.key == pygame.K_w:
                write_test_file()

            if event.key == pygame.K_SPACE:
                eye_index = (eye_index + 1)%2
                eye = eyes[eye_index]


            if event.key == pygame.K_f:
                if mods & pygame.KMOD_SHIFT:
                    tar.brightenfg()
                else:
                    tar.darkenfg()
                    
            if event.key == pygame.K_b:
                if mods & pygame.KMOD_SHIFT:
                    tar.brightenbg()
                    bgc = tar.background_color
                else:
                    tar.darkenbg()
                    bgc = tar.background_color
            
            if event.key == pygame.K_o:
                run_external_script(cfg.external_script_o)

            if event.key == pygame.K_p:
                run_external_script(cfg.external_script_p)
                
            if event.key == pygame.K_g:
                run_external_script(cfg.external_script_g)
                
    # fill the screen with a color to wipe away anything from last frame
    screen.fill(bgc)

    if inset.visible:
        inset.draw(screen,origin)
        
    if origin_mode:
        origin.draw(screen)
    else:
        tar.draw(screen,origin)

    dt = clock.tick() / 1000

    tar.age = tar.age + dt

    x_deg = tar.position_vector.x/cfg.pixels_per_deg
    y_deg = tar.position_vector.y/cfg.pixels_per_deg
    try:
        lidx = close_match((x_deg,y_deg),location_script)
    except Exception as e:
        print(e)
        lidx = -1

    if len(location_script)>1:
        script_message = 'off script'
    else:
        script_message = 'no script'
        
    if lidx>-1:
        message = '%s: %s (loc %d)'%(eye,tar.ecc(),lidx)
    else:
        message = '%s: %s (%s)'%(eye,tar.ecc(),script_message)
        
    if origin_mode:
        ox_px = origin.position_vector.x
        oy_px = origin.position_vector.y
        message = message + ' origin x = %d, y = %d'%(ox_px,oy_px)
    
    text_surface = my_font.render(message, False, cfg.text_color)
    screen.blit(text_surface,(0,0))
    
    if tar.age > cfg.logging_interval and not tar.logged:
        log(message)
        print(message)
        tar.logged = True
    
    if cfg.user_window:
        uwin.age = uwin.age + dt
        if uwin.age > cfg.user_window_update_interval:
            uwin.update(origin,tar,message)
            
    # flip() the display to put your work on screen
    pygame.display.flip()


pygame.quit()
