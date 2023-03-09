import requests
import numpy as np
from utility_functions import pickle_dump



def grid_norm_points_1D(N_tot, L_highres, N_highres):
    x_high = np.linspace(-1,1,N_highres)*L_highres/2 
    N_low1 = (N_tot-N_highres)//2
    N_low2 = N_tot-N_highres-N_low1
    x_low1 = (np.linspace(0,1,N_low1)*(1-L_highres-2*L_highres/N_highres) + (L_highres + 2*L_highres/N_highres))/2
    x_low2 = (np.linspace(-1,0,N_low2)*(1-L_highres-2*L_highres/N_highres) - (L_highres + 2*L_highres/N_highres))/2
    
    return np.sort(np.concatenate([x_low1,x_low2,x_high]))

    
def Earth_radius_km (latitude):
    B=latitude/180*np.pi #converting into radians
    a = 6378.137  #Radius at sea level at equator
    b = 6356.752  #Radius at poles
    c = (a**2*np.cos(B))**2
    d = (b**2*np.sin(B))**2
    e = (a*np.cos(B))**2
    f = (b*np.sin(B))**2
    R = np.sqrt((c+d)/(e+f))
    return R

api_key = ""
destination = [42.38152864747116, -71.12790258598837]
target_time = 1677679200 #(Should be March 1 2023 p AM EST)
target_time_shifts = [0, -7*60, -15*60]
N1D = 94
N_highres_1D = 69
box_size_km = 25
max_shift_km=1
hi_res_box_size = 15
max_per_request=25
R = Earth_radius_km(destination[0])
box_lat_size = box_size_km/R * 180/np.pi
box_long_size = box_lat_size/np.cos(destination[0]/180*np.pi)

norm_points = grid_norm_points_1D(N1D, hi_res_box_size/box_size_km, N_highres_1D)
y_v, x_v = np.meshgrid(norm_points*box_size_km, norm_points*box_size_km)
lat_v, long_v = np.meshgrid(destination[0] + norm_points*box_lat_size, destination[1] + norm_points*box_long_size)
lat_v_flat = lat_v.flatten()+1e-5; long_v_flat = long_v.flatten()


N_pairs_tot = lat_v.size
base_url = "https://maps.googleapis.com/maps/api/distancematrix/json?destinations={}%2C{}&origins=".format(destination[0], destination[1]) #base
vals = []; url = base_url; L = 0
for i in range(N_pairs_tot):
    url += "{}%2C{}%7C".format(lat_v_flat[i],long_v_flat[i])
    L += 1
    if (L==max_per_request) or (i==(N_pairs_tot-1)):
        response_vals = []
        for dt in target_time_shifts:
            url_to_call = url[:-3] + "&mode=transit&arrival_time={}&key=".format(target_time+int(dt)) + api_key
            response = requests.request("GET", url_to_call, headers={}, data={})
            durations = [f['elements'][0]['duration']['value'] if (f['elements'][0]['status']=='OK') else np.nan for f in response.json()['rows']]
            # #Check addresses, adds more calls but we can remove places where Google Maps "snaps" to a point far away from our coordinates
            # if dt==target_time_shifts[0]:
            #     for j, addr in enumerate(response.json()['origin_addresses']):
            #         time.sleep(1)
            #         g = geocoder.osm(addr).json
            #         ind = i-L+1+j
            #         d_lat = lat_v_flat[ind] - g['lat']
            #         d_long = long_v_flat[ind] - g['lng']
            #         d = np.linalg.norm([d_lat*np.pi/180*R,d_lat*np.pi/180*R*np.cos(destination[0]/180*np.pi)])
            #         durations[j] += d/5*3600 #assume 5 km/h walking speed
            #         if d>max_shift_km:
            #             durations[j] = np.nan
            if not len(response_vals):
                response_vals = np.array(durations)
            else:
                response_vals = np.vstack( (response_vals, durations) )
        #vals += list(response_vals/len(target_time_shifts))
        vals += list(np.min(response_vals,axis=0))
        L=0; url = base_url
vals = np.array(vals)/60
pickle_dump('transit_times.p', [x_v,y_v,vals], use_bz2=False, make_backup=True)




