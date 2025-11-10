import math

user_window = False
user_window_update_interval = 0.1
user_window_dpi = 300 # increasing (decreasing) this makes the user window smaller (larger)

DEFAULT_DISPLAY_X_OFFSET = 1920*2
display_mode = (1440,1440) #(1920,1080)
monitor_number = 0

# px_per_m = dpi/25.4*1000.
# SCREEN_DISTANCE_M = 20.5*.0254
# m_per_deg = math.sin(1.0/180.0*math.pi)*self.screen_distance_m
# self.pixels_per_degree = px_per_m*m_per_deg
px_per_m = 250/25.4*1000
m_per_deg = math.sin(1.0/180.0*math.pi)*20.5*.0254
pixels_per_deg = px_per_m*m_per_deg #36

###external script
external_script_o = "C:\FDML_data\keyO_flash1_b1.py"
external_script_p = "C:\FDML_data\keyP_flash2_b2.py"

foreground_color = (255, 255, 255)
background_color = (0, 0, 0) #(0, 0, 0)

prompt_for_eye = False
default_eye = 'RE'

data_monitoring = True # save .looky 
data_monitoring_folder = r'C:\FDML_data'
data_monitoring_extensions = ['.oct']
auto_advance =  False  # automatically advance the script index when new data is detected
auto_advance_delay = 3.0

target_line_width = 5
target_radius = 0.5 #deg
target_step = 1
target_small_step = 0.25

target_type = 'star' # 'star' or 'bullseye' or 'ABC'
inset_type = 'checkerboard' # 'grating' or 'deadleaves' or 'checkerboard'

color_increment = 5
colors = [foreground_color,background_color]

origin_filename = 'origin.txt'
log_folder = 'logs'
data_folder = 'data'

text_color = (0,0,0)
text_font_size = 24
text_font = 'serif'

origin_color = (255,0,0)
origin_size_px = 50
origin_line_width = 2
origin_step_px = 5
origin_small_step_px = 1

inset_background_color = (0,0,0) #(127, 127, 127)


# A couple of ideas for configuring the stimulus inset can be found
# in /figures/configurations.pdf
inset_width_deg = 15.0#display_mode[0]/pixels_per_deg
inset_height_deg = 5.0#display_mode[1]/pixels_per_deg/2.0
# settings for control case, inset not overlapped with imaging area
# presuming that the scan length is 2.5 deg and inset_height = 5.0.
# place the fixation target at 1.25 deg inferior and a few degrees nasal.
inset_y_deg = 3.75
# settings for stimulus case, inset overlapped with imaging area
# presuming that the scan length is 2.5 deg and inset_height = 5.0.
# place the fixation target at 1.25 deg inferior and a few degrees nasal.
inset_x_deg = 0.0
inset_y_deg = -1.25

deadleaves_rad_mean_deg = 0.25
deadleaves_rad_std_deg = 0.2
deadleaves_n_ellipses = int(inset_width_deg*inset_height_deg/deadleaves_rad_mean_deg**2)
deadleaves_alpha = 0.5
deadleaves_gray_range = 255
deadleaves_gray_mean = 127
# The full cycle frequency is half the update frequency.
# In other words, if you want the full cycle to run at 7.5 Hz,
# write 15 Hz here.
deadleaves_frequency = 6
deadleaves_seed = 1234

grating_frequency_fps = 30
grating_period_deg = 1
grating_cycles_per_second = 5
grating_orientation = 'horizontal'

checkerboard_frequency = 5
checkerboard_n_cols = inset_width_deg
checkerboard_n_rows = inset_height_deg
checkerboard_bright = (255,255,255)
checkerboard_dark = (0,0,0)

# seconds to wait after moving the target before writing its location tot he log
logging_interval = 1

# preset G array to cycle in the backgorund color
cycleBgColor_flag = True #Enable background color cycling
AutoCycleBg = True #Automatically change background color when **_stimuli_**V.txt is detected
Garray_bgColor = [0, 128, 179, 244, 179, 128, 0] #±200% background contrast adaptation step
external_script_g = r"C:\FDML_data\keyG_flash_adjustCWlooky.py"