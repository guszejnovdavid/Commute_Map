#!/usr/bin/env python

### Utility functions and variables for Boston_Transit_Map.ipynb

import pickle
import bz2
import os
import shutil
import numpy as np

neighborhood_colors = {
    'East\nBoston': '#D54B40',
    'Revere': '#6FD488',
    'Chelsea': '#E649B3',
    'Everett': '#DCB857',
    'Malden': '#D45BC4',
    'Medford': '#76B8DB',
    'Arlington': '#27FC53',
    'Belmont': '#EBB613',
    'Watertown': '#CA5028',
    'Newton': '#BE6ECD',
    'Allston': '#73D680',
    'Brookline': '#9F7BCB',
    'Jamaica\nPlains': '#6BBBDD',
    'Dorchester': '#504CDD',
    'Hyde Park': '#C91870',
    'West Roxbury': '#1A17C0',
    'South Boston': '#3142D8',
    'Back Bay': '#EDB479',
    'Downtown': '#77E43F',
    'West\nEnd': '#E14AD1',
    'South\nEnd': '#D656C0',
    'Roxbury': '#D0A887',
    'Charlestown': '#D1B85E',
    'East\nCambridge': '#46DAE7',
    'Baldwin': '#E2E910',
    'Harvard': '#DA3EEC',
    'North\nCambridge': '#D8EF60',
    'West\nCambridge': '#DC4F3B',
    'East\nSomerville': '#6FD47E',
    'West\nSomerville': '#07D799',
    'Waltham': '#7ABBD8',
    'Neighborhood 9\n': '#54D9BD',
    'Spring\nHill': '#3CDAB9',
    'Davis Sq': '#D9188B',
    'Cambridgeport': '#8035C6',
    'Winter\nHill': '#CC15E3',
    'Tufts': '#A053D5',
    }

    
def pickle_dump(fname, var, use_bz2=False, make_backup=True):
    if make_backup:
        if os.path.exists(fname):
            shutil.copy(fname, fname+'.bak')
    if use_bz2:
        with bz2.BZ2File(fname, 'wb') as pickle_out:
            pickle.dump(var, pickle_out, protocol=2)    
    else:
        with open(fname,'wb') as pickle_out:
            pickle.dump(var, pickle_out)

def pickle_load(fname, use_bz2=False):
    if use_bz2:
        with bz2.BZ2File(fname, 'rb') as pickle_in:
            var = pickle.load(pickle_in, encoding='bytes')
    else:
        with open(fname,'rb') as pickle_in:
            var = pickle.load(pickle_in)
    return var

def pix_boundaries(x_coord,y_coord,orig_map):
    px_left = max(0,x_coord.min())
    px_right = min(orig_map.shape[1],x_coord.max())
    py_bottom = min(orig_map.shape[0],y_coord.max())
    py_top = max(0,y_coord.min())
    return px_left, px_right, py_bottom, py_top

def find_color_CoM_size(x,y,colors,target_color,weights=None):
    if weights is None: weights=np.ones_like(x)
    ind = (colors==target_color.lower())
    if np.any(ind):
        tot_weight = np.sum(weights[ind])
        return np.sum(x[ind]*weights[ind])/tot_weight, np.sum(y[ind]*weights[ind])/tot_weight, tot_weight
    else:
        return np.nan,np.nan,np.nan

def coord_to_pixel(dx,dy,dest_coord,pix_dx_km):
    x_coord = (dx/pix_dx_km) + dest_coord[0]
    y_coord = (-dy/pix_dx_km) + dest_coord[1]
    return x_coord.astype(int), y_coord.astype(int)

def pixel_to_coord(px,py,dest_coord,pix_dx_km):
    dx = (px-dest_coord[0])*pix_dx_km
    dy = -(py-dest_coord[1])*pix_dx_km
    return dx,dy
    
def segments(p):
    return zip(p, p[1:] + [p[0]])

def polygon_area(p):
    return 0.5 * abs(sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(p)))

def polygon_center(p):
    xc=0; yc=0
    for v in p:
        xc += v[0]
        yc += v[1]
    return xc/len(p), yc/len(p)