# -*- coding: utf-8 -*-
"""
Created on Thursday June 23 14:42:21 2016

tracks a moving object using method of cross-correlation to find the shift
between successive images in video from a hand-held infrared camera

@author: foresterd
"""

from sys import path as spath
spath.append('/home/foresterd/drfpy/plotting')
import show_plots
spath.append('/home/foresterd/drfpy/grave_IO')
import read_grave as rg
spath.append('/home/foresterd/drfpy/bad_pixels')
import get_superPix_locs as gspl

import pickle
import numpy as np
from skimage.feature import register_translation
from scipy.ndimage.interpolation import shift
import cv2
from scipy.misc import bytescale
from skimage.morphology import binary_opening
from scipy import ndimage
from skimage.color import gray2rgb

#------------------------------------------------------------------------------
nFramesToRead = -1 # any positive number, or -1 to read all frames in file
fgbg = cv2.createBackgroundSubtractorMOG2() # Adaptive Background Subtractor
showPlots = True
infile = 'drone_movie.raw'
outdir = 'outmovie'
zrpad = 10
zcpad = 10

# mark bad pixels (overperforming or underperforming) for this sensor
ylst = [248,238,251,283,286,305,405,448,117,398,348]
xlst = [197,301,309,309,425,432,377,587,497,239,63]
badPixels = (np.array(ylst, dtype=np.uint16), # y (rows)
             np.array(xlst, dtype=np.uint16)) # x (cols)
badSuperPix = gspl.get_superPix_locs(badPixels)
#------------------------------------------------------------------------------

if showPlots:
    plt, fig, ax = show_plots.getFig(1,1)

# READ THE LWIR CAMERA DATA
frameList, frameHdrList = rg.read_grave(infile, nFramesToRead)
rows, cols = frameList[0].shape

# frames subset
ijump = 120
nskip = 1
frameList = frameList[ijump+nskip:] # start after frame ijump
iframeList = [ii for ii in range(len(frameList)) if ii%nskip==0] # skip every nskip-th frame

icount = 0
for iframe in iframeList[:-1]:
    Img = frameList[iframe].copy()
    Img[badSuperPix] = np.mean(Img) # zero-out the 4-block bad super-pixel
    #if showPlots: show_plots.showPlot(Img, iframe, ax, wait=True)
    print('frame '+str(icount))

    #print frame.dtype, np.max(frame), np.shape(frame)
    tframe = np.left_shift(Img, 4) # 16-bit to 12-bit (camera bit depth)
    tframe = bytescale(tframe) # convert to 8-bit image
    #if showPlots: show_plots.showPlot(tframe, iframe, ax, wait=True)

    if icount > 0:
        # use phase correlation for image registration
        #http://scikit-image.org/docs/dev/auto_examples/plot_register_translation.html
        shft, error, diffphase = register_translation(tframePrev, tframe, 100)
        if len(shft)!=0:
            shifted = shift(tframe, shft)

            diff = tframePrev - shifted
            fgmask = fgbg.apply(diff)

            fgmask[:,0:zcpad] = 0 # left side
            fgmask[:,cols-zcpad:cols] = 0 # right side
            fgmask[0:zrpad,:] = 0 # top
            fgmask[rows-zrpad:rows,:] = 0 # bottom

            if shft[1]>0:
                fgmask[:,0:+shft[1]] = 0 # left side
            else:
                fgmask[:,cols+shft[1]:cols] = 0 # right side

            cImg = np.zeros((rows,cols), np.bool)
            cImg[fgmask>0] = 1
            cImg = binary_opening(cImg)
            #if showPlots: show_plots.showPlot(cImg, iframe, ax, wait=True)
            Idisp = np.zeros((rows, cols, 3), np.uint8)
            idx = np.where(cImg)
            Idisp = gray2rgb(bytescale(Img))
            Idisp[:,:,:][idx] = 0
            Idisp[:,:,0][idx] = 255
            #Idisp[:,:,0] = rimg
            if showPlots: show_plots.showPlot(Idisp, iframe, ax, wait=False)
        else:
            print('Shift Not Found.')

    icount += 1
    tframePrev = tframe # save previous frame
