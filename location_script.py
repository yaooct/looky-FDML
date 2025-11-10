import math

# Locations can also be created programmatically, e.g. 10 locations in a semicircle in the temporal retina, with radius 4 deg:

nasal = False # for normals we use the temporal side

location_script = []
radius_array = [2,4,6,8,10,12]

y_coordinates = [-2,-1,0,1,2]

# for radius in radius_array:
#     for y in y_coordinates:
#         x = math.sqrt(radius**2-y**2)
#         x = round(x,3)
#         if nasal:
#             x = -x
#         location_script.append((x,y))


location_script = [(-3,4), (-2,2), (-5,5)] # RE:3N4S