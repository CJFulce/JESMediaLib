# Media interface for JES-emulator, a Python3 implementation of JES,
# the Jython Environment for Students, that does not require Jython.
#
# This file is a heavily modified version of jes/python/media.py from the
# JES distribution:
#     # Media Wrappers for "Introduction to Media Computation"
#     # Started: Mark Guzdial, 2 July 2002
#
#
"""
This file was pulled from from https://github.com/gordon-cs/JES4py on August 7, 2024,
and modified by Santos Pena & Dave Largent (dllargent@bsu.edu) from Ball State University.

The following modificaitons were made:
-- Added imports to support added/changed code
    -- matplotlib
    -- pygame
    -- time
    -- tkinter
Modified or added the following functions:
-- openSoundTool()   (explore(sound) uses this function)
-- playNote()
-- requestInteger()
-- requestIntegerInRange()
-- requestNumber()
-- requestString()
-- showError()
-- showInformation()
-- showWarning()
"""

import sys
import os
import math
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import font
import matplotlib.pyplot as plt
import pygame.midi
import time
from jes4py.Picture import Picture
from jes4py.PixelColor import Pixel, Color
from jes4py.Sound import Sound
from jes4py.Sample import Sample
from jes4py.Samples import Samples
from jes4py import FileChooser
import random
from jes4py import Config

mediaFolder = os.getcwd() + os.sep

_lastFilePath = ""

true = 1
false = 0

def setMediaPath(file=None):
    global mediaFolder
    if(file == None):
        FileChooser.pickMediaPath()
    else:
        FileChooser.setMediaPath(file)
    mediaFolder = getMediaPath()
    return mediaFolder


def getMediaPath(filename=""):
    return str(FileChooser.getMediaPath(filename))


def setMediaFolder(file=None):
    return setMediaPath(file)


def setTestMediaFolder():
    global mediaFolder
    mediaFolder = os.getcwd() + os.sep


def getMediaFolder(filename=""):
    return str(getMediaPath(filename))


def showMediaFolder():
    global mediaFolder
    print("The media path is currently: ", mediaFolder)


def getShortPath(filename):
    dirs = filename.split(os.sep)
    if len(dirs) < 1:
        return "."
    elif len(dirs) == 1:
        return str(dirs[0])
    else:
        return str(dirs[len(dirs) - 2] + os.sep + dirs[len(dirs) - 1])


def addLibPath(directory=None):
    if directory is None:
        directory = pickAFolder()

    if os.path.isdir(directory):
        sys.path.insert(0, directory)
    elif directory is not None:
        raise ValueError("There is no directory at " + directory)

    return directory

setLibPath = addLibPath


##
# Global sound functions
##

def samplesToSound(samples, maxIndex=100):
    maxIndex = max([getIndex(s) for s in samples])
    newSound = makeEmptySound(maxIndex + 1,
                              int(getSamplingRate(samples[0].getSound())))
    for s in samples:
        x = getIndex(s)
        setSampleValueAt(newSound, x, getSampleValue(s))
    return newSound


def makeSound(filename, maxIndex=100):
    global mediaFolder
    if not isinstance(filename, str):
        return samplesToSound(filename, maxIndex=maxIndex)
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not os.path.isfile(filename):
        print("There is no file at " + filename)
        raise ValueError
    return Sound(filename)


def makeEmptySound(numSamples, samplingRate=Sound.SAMPLE_RATE):
    numSamples = int(numSamples)
    if numSamples <= 0 or samplingRate <= 0:
        print("makeEmptySound(numSamples[, samplingRate]): numSamples and samplingRate must each be greater than 0")
        raise ValueError
    if (numSamples / samplingRate) > 600:
        print("makeEmptySound(numSamples[, samplingRate]): Created sound must be less than 600 seconds")
        raise ValueError
    return Sound(numSamples, samplingRate)

def makeEmptySoundBySeconds(seconds, samplingRate=Sound.SAMPLE_RATE):
    if seconds <= 0 or samplingRate <= 0:
        print("makeEmptySoundBySeconds(numSamples[, samplingRate]): numSamples and samplingRate must each be greater than 0")
        raise ValueError
    if seconds > 600:
        print("makeEmptySoundBySeconds(numSamples[, samplingRate]): Created sound must be less than 600 seconds")
        raise ValueError
    return Sound(seconds * samplingRate, samplingRate)


def duplicateSound(sound):
    if not isinstance(sound, Sound):
        print("duplicateSound(sound): Input is not a sound")
        raise ValueError
    return Sound(sound)


def getSamples(sound):
    if not isinstance(sound, Sound):
        print("getSamples(sound): Input is not a sound")
        raise ValueError
    return Samples.getSamples(sound)


def play(sound):
    if not isinstance(sound, Sound):
        print("play(sound): Input is not a sound")
        raise ValueError
    sound.play()


def blockingPlay(sound):
    if not isinstance(sound, Sound):
        print("blockingPlay(sound): Input is not a sound")
        raise ValueError
    sound.blockingPlay()


def stopPlaying(sound):
    if not isinstance(sound, Sound):
        print("stopPlaying(sound): Input is not a sound")
        raise ValueError
    sound.stopPlaying()


def playAtRate(sound, rate):
    if not isinstance(sound, Sound):
        print("playAtRate(sound,rate): First input is not a sound")
        raise ValueError
    sound.playAtRateDur(rate, sound.getLength())


def playAtRateDur(sound, rate, dur):
    if not isinstance(sound, Sound):
        print("playAtRateDur(sound,rate,dur): First input is not a sound")
        raise ValueError
    sound.playAtRateDur(rate, dur)



def playInRange(sound, start, stop):
    if not isinstance(sound, Sound):
        print("playInRange(sound,start,stop): First input is not a sound")
        raise ValueError
    sound.playAtRateInRange(
        1, start - Sound._SoundIndexOffset, stop - Sound._SoundIndexOffset)


def blockingPlayInRange(sound, start, stop):
    if not isinstance(sound, Sound):
        print("blockingPlayInRange(sound,start,stop): First input is not a sound")
        raise ValueError
    sound.blockingPlayAtRateInRange(
        1, start - Sound._SoundIndexOffset, stop - Sound._SoundIndexOffset)


def playAtRateInRange(sound, rate, start, stop):
    if not isinstance(sound, Sound):
        print("playAtRateInRAnge(sound,rate,start,stop): First input is not a sound")
        raise ValueError
    sound.playAtRateInRange(
        rate, start - Sound._SoundIndexOffset, stop - Sound._SoundIndexOffset)


def blockingPlayAtRateInRange(sound, rate, start, stop):
    if not isinstance(sound, Sound):
        print("blockingPlayAtRateInRange(sound,rate,start,stop): First input is not a sound")
        raise ValueError
    sound.blockingPlayAtRateInRange(
        rate, start - Sound._SoundIndexOffset, stop - Sound._SoundIndexOffset)


def getSamplingRate(sound):
    if not isinstance(sound, Sound):
        print("getSamplingRate(sound): Input is not a sound")
        raise ValueError
    return sound.getSamplingRate()


def setSampleValueAt(sound, index, value):
    if not isinstance(sound, Sound):
        print("setSampleValueAt(sound,index,value): First input is not a sound")
        raise ValueError
    if index < Sound._SoundIndexOffset:
        print("You asked for the sample at index: " + str(index) + ".  This number is less than " + str(Sound._SoundIndexOffset) + ".  Please try" + " again using an index in the range [" + str(Sound._SoundIndexOffset) + "," + str(getLength(sound) - 1 + Sound._SoundIndexOffset) + "].")
        raise ValueError
    if index > getLength(sound) - 1 + Sound._SoundIndexOffset:
        print("You are trying to access the sample at index: " + str(index) + ", but the last valid index is at " + str(getLength(sound) - 1 + Sound._SoundIndexOffset))
        raise ValueError
    sound.setSampleValue(index - Sound._SoundIndexOffset, int(value))


def getSampleValueAt(sound, index):
    if not isinstance(sound, Sound):
        print("getSampleValueAt(sound,index): First input is not a sound")
        raise ValueError
    if index < Sound._SoundIndexOffset:
        print("You asked for the sample at index: " + str(index) + ".  This number is less than " + str(Sound._SoundIndexOffset) + ".  Please try" + " again using an index in the range [" + str(Sound._SoundIndexOffset) + "," + str(getLength(sound) - 1 + Sound._SoundIndexOffset) + "].")
        raise ValueError
    if index > getLength(sound) - 1 + Sound._SoundIndexOffset:
        print("You are trying to access the sample at index: " + str(index) + ", but the last valid index is at " + str(getLength(sound) - 1 + Sound._SoundIndexOffset))
        raise ValueError
    return sound.getSampleValue(index - Sound._SoundIndexOffset)


def getSampleObjectAt(sound, index):
    if not isinstance(sound, Sound):
        print("getSampleObjectAt(sound,index): First input is not a sound")
        raise ValueError
    if index < Sound._SoundIndexOffset:
        print("You asked for the sample at index: " + str(index) + ".  This number is less than " + str(Sound._SoundIndexOffset) + ".  Please try" + " again using an index in the range [" + str(Sound._SoundIndexOffset) + "," + str(getLength(sound) - 1 + Sound._SoundIndexOffset) + "].")
        raise ValueError
    if index > getLength(sound) - 1 + Sound._SoundIndexOffset:
        print("You are trying to access the sample at index: " + str(index) + ", but the last valid index is at " + str(getLength(sound) - 1 + Sound._SoundIndexOffset))
        raise ValueError
    return Sample(sound, index - Sound._SoundIndexOffset)


def setSample(sample, value):
    if not isinstance(sample, Sample):
        print("setSample(sample,value): First input is not a sample")
        raise ValueError
    if value > 32767:
        value = 32767
    elif value < -32768:
        value = -32768
    return sample.setValue(int(value))


def setSampleValue(sample, value):
    setSample(sample, value)


def getSample(sample):
    if not isinstance(sample, Sample):
        print("getSample(sample): Input is not a sample")
        raise ValueError
    return sample.getValue()

def getSampleValue(sample):
    return getSample(sample)


def getSound(sample):
    if not isinstance(sample, Sample):
        print("getSound(sample): Input is not a sample")
        raise ValueError
    return sample.getSound()


def getLength(sound):
    if not isinstance(sound, Sound):
        print("getLength(sound): Input is not a sound")
        raise ValueError
    return sound.getLength()


def getNumSamples(sound):
    return getLength(sound)


def getDuration(sound):
    if not isinstance(sound, Sound):
        print("getDuration(sound): Input is not a sound")
        raise ValueError
    return sound.getLength() / sound.getSamplingRate()


def writeSoundTo(sound, filename):
    global mediaFolder
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not isinstance(sound, Sound):
        print("writeSoundTo(sound,filename): First input is not a sound")
        raise ValueError
    sound.writeToFile(filename)


def randomSamples(someSound, number):
    samplelist = []
    samples = getSamples(someSound)
    for count in range(number):
        samplelist.append(random.choice(samples))
    explore(samplesToSound(samplelist))


def getIndex(sample):
    return int(str(sample).split()[2])

##
# Global color functions
##

def setColorWrapAround(setting):
    Pixel.setWrapLevels(bool(setting))

def getColorWrapAround():
    return Pixel.getWrapLevels()

def pickAColor():
    return Color.pickAColor()

# Constants
black = Color(0, 0, 0)
white = Color(255, 255, 255)
blue = Color(0, 0, 255)
red = Color(255, 0, 0)
green = Color(0, 255, 0)
gray = Color(128, 128, 128)
darkGray = Color(64, 64, 64)
lightGray = Color(192, 192, 192)
yellow = Color(255, 255, 0)
orange = Color(255, 200, 0)
pink = Color(255, 175, 175)
magenta = Color(255, 0, 255)
cyan = Color(0, 255, 255)

##
# Global picture functions
##


def randomPixels(somePic, number):
    pixellist = []
    pixels = getPixels(somePic)
    for count in range(number):
        pixellist.append(random.choice(pixels))
    explore(pixelsToPicture(pixellist))


def pixelsToPicture(pixels, defaultColor=white, maxX=100, maxY=100):
    maxX = max([getX(p) for p in pixels])
    maxY = max([getY(p) for p in pixels])
    newpic = makeEmptyPicture(maxX + 1, maxY + 1, defaultColor)
    for pixel in pixels:
        x = getX(pixel)
        y = getY(pixel)
        setColor(getPixel(newpic, x, y), getColor(pixel))
    return newpic


def makePicture(filename, defaultColor=white):
    global mediaFolder
    if not isinstance(filename, str):
        return pixelsToPicture(filename, defaultColor=defaultColor)
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not os.path.isfile(filename):
        print("makePicture(filename): There is no file at " + filename)
        raise ValueError
    picture = Picture()
    picture.loadOrFail(filename)
    return picture


def makeEmptyPicture(width, height, acolor=white):
    if width > 10000 or height > 10000:
        print("makeEmptyPicture(width, height[, acolor]): height and width must be less than 10000 each")
        raise ValueError
    if width <= 0 or height <= 0:
        print("makeEmptyPicture(width, height[, acolor]): height and width must be greater than 0 each")
        raise ValueError
    picture = Picture(width, height, acolor)
    return picture


def getPixels(picture):
    if not isinstance(picture, Picture):
        print("getPixels(picture): Input is not a picture")
        raise ValueError
    return picture.getPixels()


def getAllPixels(picture):
    return getPixels(picture)


def getWidth(picture):
    if not isinstance(picture, Picture):
        print("getWidth(picture): Input is not a picture")
        raise ValueError
    return picture.getWidth()


def getHeight(picture):
    if not isinstance(picture, Picture):
        print("getHeight(picture): Input is not a picture")
        raise ValueError
    return picture.getHeight()


def show(picture, title=None):
    if not isinstance(picture, Picture):
        print("show(picture): Input is not a picture")
        raise ValueError
    picture.show()

def repaint(picture):
    if not isinstance(picture, Picture):
        print("repaint(picture): Input is not a picture")
        raise ValueError
    picture.repaint()


def addLine(picture, x1, y1, x2, y2, acolor=black):
    if not isinstance(picture, Picture):
        print("addLine(picture, x1, y1, x2, y2[, color]): First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addLine(picture, x1, y1, x2, y2[, color]): Last input is not a color")
        raise ValueError
    picture.addLine(acolor, x1, y1, x2, y2)


def addText(picture, x, y, string, acolor=black):
    if not isinstance(picture, Picture):
        print("addText(picture, x, y, string[, color]): First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addText(picture, x, y, string[, color]): Last input is not a color")
        raise ValueError
    
    picture.addText(acolor, x, y, string)


def addRect(picture, x, y, w, h, acolor=black):
    if not isinstance(picture, Picture):
        print("addRect(picture, x, y, w, h[, color]): First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addRect(picture, x, y, w, h[, color]): Last input is not a color")
        raise ValueError
    picture.addRect(acolor, x, y, w, h)


def addRectFilled(picture, x, y, w, h, acolor=black):
    if not isinstance(picture, Picture):
        print("addRectFilled(picture, x, y, w, h[, color]): First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addRectFilled(picture, x, y, w, h[, color]): Last input is not a color")
        raise ValueError
    picture.addRectFilled(acolor, x, y, w, h)


def addOval(picture, x, y, w, h, acolor=black):
    if not isinstance(picture, Picture):
        print("addOval(picture, x, y, w, h[, color]): First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addOval(picture, x, y, w, h[, color]): Last input is not a color")
        raise ValueError
    picture.addOval(acolor, x, y, w, h)


def addOvalFilled(picture, x, y, w, h, acolor=black):
    if not isinstance(picture, Picture):
        print("addOvalFilled(picture, x, y, w, h[, color]): First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addOvalFilled(picture, x, y, w, h[, color]): Last input is not a color")
        raise ValueError
    picture.addOvalFilled(acolor, x, y, w, h)


def addArc(picture, x, y, w, h, start, angle, acolor=black):
    if not isinstance(picture, Picture):
        print("addArc(picture, x, y, w, h, start, angle[, color]): First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addArc(picture, x, y, w, h, start, angle[, color]): Last input is not a color")
        raise ValueError
    picture.addArc(acolor, x, y, w, h, start, angle)


def addArcFilled(picture, x, y, w, h, start, angle, acolor=black):
    if not isinstance(picture, Picture):
        print("addArcFilled(picture, x, y, w, h[, color]): First First input is not a picture")
        raise ValueError
    if not isinstance(acolor, Color):
        print("addArcFilled(picture, x, y, w, h, start, angle[, color]): Last input is not a color")
        raise ValueError
    picture.addArcFilled(acolor, x, y, w, h, start, angle)


def getPixel(picture, x, y):
    if not isinstance(picture, Picture):
        print("getPixel(picture,x,y): First input is not a picture")
        raise ValueError
    if (x < Picture._PictureIndexOffset) or (x > getWidth(picture) - 1 + Picture._PictureIndexOffset):
        print("getPixel(picture,x,y): x (= {}) is less than {} or bigger than the width (= {})".format(x, Picture._PictureIndexOffset, getWidth(picture) - 1 + Picture._PictureIndexOffset))
        raise ValueError
    if (y < Picture._PictureIndexOffset) or (y > getHeight(picture) - 1 + Picture._PictureIndexOffset):
        print("getPixel(picture,x,y): y (= {}) is less than {} or bigger than the height (= {})".format(y, Picture._PictureIndexOffset, getHeight(picture) - 1 + Picture._PictureIndexOffset))
        raise ValueError

    return picture.getPixel(x - Picture._PictureIndexOffset, y - Picture._PictureIndexOffset)


def getPixelAt(picture, x, y):
    return getPixel(picture, x, y)


def setRed(pixel, value):
    value = Pixel.correctLevel(value)
    if not isinstance(pixel, Pixel):
        print("setRed(pixel,value): Input is not a pixel")
        raise ValueError
    pixel.setRed(value)


def getRed(pixel):
    if not isinstance(pixel, Pixel):
        print("getRed(pixel): Input is not a pixel")
        raise ValueError
    return pixel.getRed()


def setBlue(pixel, value):
    value = Pixel.correctLevel(value)
    if not isinstance(pixel, Pixel):
        print("setBlue(pixel,value): Input is not a pixel")
        raise ValueError
    pixel.setBlue(value)


def getBlue(pixel):
    if not isinstance(pixel, Pixel):
        print("getBlue(pixel): Input is not a pixel")
        raise ValueError
    return pixel.getBlue()


def setGreen(pixel, value):
    value = Pixel.correctLevel(value)
    if not isinstance(pixel, Pixel):
        print("setGreen(pixel,value): Input is not a pixel")
        raise ValueError
    pixel.setGreen(value)


def getGreen(pixel):
    if not isinstance(pixel, Pixel):
        print("getGreen(pixel): Input is not a pixel")
        raise ValueError
    return pixel.getGreen()


def getColor(pixel):
    if not isinstance(pixel, Pixel):
        print("getColor(pixel): Input is not a pixel")
        raise ValueError
    return Color(pixel.getColor())


def setColor(pixel, color):
    if not isinstance(pixel, Pixel):
        print("setColor(pixel,color): First input is not a pixel")
        raise ValueError
    if not isinstance(color, Color):
        print("setColor(pixel,color): Second input is not a color")
        raise ValueError
    pixel.setColor(color)


def getX(pixel):
    if not isinstance(pixel, Pixel):
        print("getX(pixel): Input is not a pixel")
        raise ValueError
    return pixel.getX() + Picture._PictureIndexOffset


def getY(pixel):
    if not isinstance(pixel, Pixel):
        print("getY(pixel): Input is not a pixel")
        raise ValueError
    return pixel.getY() + Picture._PictureIndexOffset


def distance(c1, c2):
    if not isinstance(c1, Color):
        print("distance(c1,c2): First input is not a color")
        raise ValueError
    if not isinstance(c2, Color):
        print("distance(c1,c2): Second input is not a color")
        raise ValueError
    return c1.distance(c2)


def writePictureTo(picture, filename):
    global mediaFolder
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not isinstance(picture, Picture):
        print("writePictureTo(picture,filename): First input is not a picture")
        raise ValueError
    picture.writeOrFail(filename)

def _setColorTo(color, other):
    color.setRGB(other.getRed(), other.getGreen(), other.getBlue())
    return color


def makeDarker(color):
    if not isinstance(color, Color):
        print("makeDarker(color): Input is not a color")
        raise ValueError
    return Color(color.makeDarker())


def makeLighter(color):
    if not isinstance(color, Color):
        print("makeLighter(color): Input is not a color")
        raise ValueError
    return Color(color.makeLighter())


def makeBrighter(color):  
    if not isinstance(color, Color):
        print("makeBrighter(color): Input is not a color")
        raise ValueError
    return Color(color.makeLighter())


def makeColor(red, green=None, blue=None):
    return Color(red, green, blue)


def setAllPixelsToAColor(picture, color):
    if not isinstance(picture, Picture):
        print("setAllPixelsToAColor(picture,color): First input is not a picture")
        raise ValueError
    if not isinstance(color, Color):
        print("setAllPixelsToAColor(picture,color): Second input is not a color")
        raise ValueError
    picture.setAllPixelsToAColor(color)


def copyInto(origPict, destPict, upperLeftX, upperLeftY):
 if not isinstance(origPict, Picture):
   print("copyInto(origPict, destPict, upperLeftX, upperLeftY): First parameter is not a picture")
   raise ValueError
 if not isinstance(destPict, Picture):
   print("copyInto(origPict, destPict, upperLeftX, upperLeftY): Second parameter is not a picture")
   raise ValueError
 if upperLeftX < 0 or upperLeftX > getWidth(destPict):
   print("copyInto(origPict, destPict, upperLeftX, upperLeftY): upperLeftX must be within the destPict")
   raise ValueError
 if upperLeftY < 0 or upperLeftY > getHeight(destPict):
   print("copyInto(origPict, destPict, upperLeftX, upperLeftY): upperLeftY must be within the destPict")
   raise ValueError
 return origPict.copyInto(destPict, upperLeftX-1, upperLeftY-1)


def duplicatePicture(picture):
    """returns a copy of the picture"""
    if not isinstance(picture, Picture):
        print("duplicatePicture(picture): Input is not a picture")
        raise ValueError
    return Picture(picture)

def cropPicture(picture, upperLeftX, upperLeftY, width, height):
 if not isinstance(picture, Picture):
   print("crop(picture, upperLeftX, upperLeftY, width, height): First parameter is not a picture")
   raise ValueError
 if upperLeftX < 1 or upperLeftX > getWidth(pic):
   print("crop(picture, upperLeftX, upperLeftY, width, height): upperLeftX must be within the picture")
   raise ValueError
 if upperLeftY < 1 or upperLeftY > getHeight(pic):
   print("crop(picture, upperLeftX, upperLeftY, width, height): upperLeftY must be within the picture")
   raise ValueError
 return picture.crop(upperLeftX-1, upperLeftY-1, width, height)


def calculateNeededFiller(message, width=100):
    fillerNeeded = width - len(message)
    if fillerNeeded < 0:
        fillerNeeded = 0
    return fillerNeeded * " "


def requestNumber(message):
    root = tk.Tk()
    root.withdraw()
    filler = calculateNeededFiller(message, 60)    
    userInput = simpledialog.askfloat("Enter a number", message + filler)
    root.destroy()
    return userInput


def requestInteger(message):
    root = tk.Tk()
    root.withdraw()
    filler = calculateNeededFiller(message, 60)   
    userInput = simpledialog.askinteger("Enter an integer", message + filler)
    root.destroy()
    return userInput


def requestIntegerInRange(message, min, max):

    if min >= max:
        print("requestIntegerInRange(message, min, max): min >= max not allowed")
        raise ValueError
    root = tk.Tk()
    root.withdraw()
    filler = calculateNeededFiller(message, 80)    
    userInput = simpledialog.askinteger("Enter an integer in a range", message + filler, minvalue=min, maxvalue=max)
    root.destroy()
    return userInput


def requestString(message):
    root = tk.Tk()
    root.withdraw()
    filler = calculateNeededFiller(message)    
    userInput = simpledialog.askstring("Enter a string", message + filler)
    root.destroy()
    return userInput


def showWarning(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("Warning",message)


def showInformation(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Information",message)


def showError(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error",message)


##
# Java Music Interface
##

def playNote(note, duration, intensity=64):
    if not (0 <= note <= 127):
        raise ValueError("playNote(): Note must be between 0 and 127.")
    if not (0 <= intensity <= 127):
        raise ValueError("playNote(): Intensity must be between 0 and 127.")
    pygame.midi.init()	
    try:
        port = pygame.midi.get_default_output_id()	
        midi_out = pygame.midi.Output(port)
        midi_out.note_on(note, intensity)	
        time.sleep(duration / 1000.0)	
        midi_out.note_off(note, intensity)	
    finally:
        del midi_out	
        pygame.midi.quit()

##
# General user tools
#

def pickAFile():
    return str(FileChooser.pickAFile())


def pickAFolder():
    dir = FileChooser.pickADirectory()
    if (dir != None):
        return str(dir + os.sep)
    return None


def quit():
    sys.exit(0)

##
# MediaTools interface
#
# TODO modify viewer.changeToBaseOne


def openPictureTool(picture):
    picture.pictureTool()


def openFrameSequencerTool(movie):
    FrameSequencerTool(movie)


def openSoundTool(sound):
    samplesList = list(map(getSampleValue,getSamples(sound)))
    try:
        fileName = getShortPath(sound.getFileName())
        if fileName == "":
            fileName = "No file name"
    except:
        fileName = "No file name"
    plt.figure(num=fileName)
    samplingRate = int(getSamplingRate(sound))
    plotTitle = fileName + "  (" + str(samplingRate) + " samples/second)"
    plt.title(plotTitle)
    plt.subplots_adjust(left=0.15, bottom=.15)
    plt.plot(range(1,1+len(samplesList)),samplesList)
    plt.axline((0,0),slope=0, color='k')
    plt.xlabel("Sample index (time)")
    plt.ylabel("Sample value (volume)")
    plt.show(block=False)
    
        
def explore(someMedia):
    if isinstance(someMedia, Picture):
        openPictureTool(someMedia)
    elif isinstance(someMedia, Sound):
        openSoundTool(someMedia)
    elif isinstance(someMedia, Movie):
        openFrameSequencerTool(someMedia)
    else:
        print("explore(someMedia): Input is not a Picture, Sound, or Movie")
        raise ValueError

# let's try the turtles...
# import Turtle
# import World


def turn(turtle, degrees=90):
    if not isinstance(turtle, Turtle):
        print("turn(turtle[, degrees]): Input is not a turtle")
        raise ValueError
    else:
        turtle.turn(degrees)


def turnRight(turtle):
    if not isinstance(turtle, Turtle):
        print("turnRight(turtle): Input is not a turtle")
        raise ValueError
    else:
        turtle.turnRight()


def turnToFace(turtle, x, y=None):
    if y == None:
        if not (isinstance(turtle, Turtle) and isinstance(x, Turtle)):
            print("turnToFace(turtle, turtle): First input is not a turtle")
            raise ValueError
        else:
            turtle.turnToFace(x)
    else:
        if not isinstance(turtle, Turtle):
            print("turnToFace(turtle, x, y): Input is not a turtle")
            raise ValueError
        else:
            turtle.turnToFace(x, y)


def turnLeft(turtle):
    if not isinstance(turtle, Turtle):
        print("turnLeft(turtle): Input is not a turtle")
        raise ValueError
    else:
        turtle.turnLeft()


def forward(turtle, pixels=100):
    if not isinstance(turtle, Turtle):
        print("forward(turtle[, pixels]): Input is not a turtle")
        raise ValueError
    else:
        turtle.forward(pixels)


def backward(turtle, pixels=100):
    if not isinstance(turtle, Turtle):
        print("backward(turtle[, pixels]): Input is not a turtle")
        raise ValueError
    if (None == pixels):
        turtle.backward()
    else:
        turtle.backward(pixels)


def moveTo(turtle, x, y):
    if not isinstance(turtle, Turtle):
        print("moveTo(turtle, x, y): Input is not a turtle")
        raise ValueError
    turtle.moveTo(x, y)


def makeTurtle(world):
    if not (isinstance(world, World) or isinstance(world, Picture)):
        print("makeTurtle(world): Input is not a world or picture")
        raise ValueError
    turtle = Turtle(world)
    return turtle


def penUp(turtle):
    if not isinstance(turtle, Turtle):
        print("penUp(turtle): Input is not a turtle")
        raise ValueError
    turtle.penUp()


def penDown(turtle):
    if not isinstance(turtle, Turtle):
        print("penDown(turtle): Input is not a turtle")
        raise ValueError
    turtle.penDown()


def drop(turtle, picture):
    if not isinstance(turtle, Turtle):
        print("drop(turtle, picture): First input is not a turtle")
        raise ValueError
    if not isinstance(picture, Picture):
        print("drop(turtle, picture): Second input is not a picture")
        raise ValueError
    turtle.drop(picture)


def getXPos(turtle):
    if not isinstance(turtle, Turtle):
        print("getXPos(turtle): Input is not a turtle")
        raise ValueError
    return turtle.getXPos()


def getYPos(turtle):
    if not isinstance(turtle, Turtle):
        print("getYPos(turtle): Input is not a turtle")
        raise ValueError
    return turtle.getYPos()


def getHeading(turtle):
    if not isinstance(turtle, Turtle):
        print("getHeading(turtle): Input is not a turtle")
        raise ValueError
    return turtle.getHeading()

# add these things: turnToFace(turtle, another turtle)
## getHeading, getXPos, getYPos

# world methods


def makeWorld(width=None, height=None):
    if(width and height):
        w = World(width, height)
    else:
        w = World()
    return w


def getTurtleList(world):
    if not isinstance(world, World):
        print("getTurtleList(world): Input is not a world")
        raise ValueError
    return world.getTurtleList()

# end of stuff imported for worlds and turtles

# used in the book


def printNow(text):
    print(text)


class Movie(object):
    def __init__(self):  # frames are filenames
        self.frames = []
        self.dir = None

    def addFrame(self, frame):
        self.frames.append(frame)
        self.dir = None

    def __len__(self):
        return len(self.frames)

    def __str__(self):
        return "Movie, frames: " + str(len(self))

    def __repr__(self):
        return "Movie, frames: " + str(len(self))

    def __getitem__(self, item):
        return self.frames[item]

    def writeFramesToDirectory(self, directory):
        import FrameSequencer
        fs = FrameSequencer(directory)
        for frameindex in range(0, len(self.frames)):
            fs.addFrame(Picture(self.frames[frameindex]))
        self.dir = directory

    def play(self):
        import java.util.ArrayList as ArrayList
        list = ArrayList()
        for f in self.frames:
            list.add(makePicture(f))
        MoviePlayer(list).playMovie()


def playMovie(movie):
    if isinstance(movie, Movie):
        movie.play()
    else:
        print("playMovie( movie ): Input is not a Movie")
        raise ValueError


def writeQuicktime(movie, destPath, framesPerSec=16):
    if not (isinstance(movie, Movie)):
        print("writeQuicktime(movie, path[, framesPerSec]): First input is not a Movie")
        raise ValueError
    if framesPerSec <= 0:
        print("writeQuicktime(movie, path[, framesPerSec]): Frame rate must be a positive number")
        raise ValueError
    movie.writeQuicktime(destPath, framesPerSec)


def writeAVI(movie, destPath, framesPerSec=16):
    if not (isinstance(movie, Movie)):
        print("writeAVI(movie, path[, framesPerSec]): First input is not a Movie")
        raise ValueError
    if framesPerSec <= 0:
        print("writeAVI(movie, path[, framesPerSec]): Frame rate must be a positive number")
        raise ValueError
    movie.writeAVI(destPath, framesPerSec)


def makeMovie():
    return Movie()


def makeMovieFromInitialFile(filename):
    import re
    movie = Movie()
    filename = filename.replace('/', os.sep)
    sep_location = filename.rfind(os.sep)
    if(-1 == sep_location):
        filename = mediaFolder + filename

    movie.directory = filename[:(filename.rfind(os.sep))]
    movie.init_file = filename[(filename.rfind(os.sep)) + 1:]
    regex = re.compile('[0-9]+')
    file_regex = regex.sub('.*', movie.init_file)

    for item in sorted(os.listdir(movie.directory)):
        if re.match(file_regex, item):
            movie.addFrame(movie.directory + os.sep + item)

    return movie


def addFrameToMovie(a, b):
    frame = None
    movie = None
    if a.__class__ == Movie:
        movie = a
        frame = b
    else:
        movie = b
        frame = a

    if not (isinstance(movie, Movie) and isinstance(frame, String)):
        print("addFrameToMovie(frame, movie): frame is not a string or movie is not a Movie object")
        raise ValueError

    movie.addFrame(frame)


def writeFramesToDirectory(movie, directory=None):
    if not isinstance(movie, Movie):
        print("writeFramesToDirectory(movie[, directory]): movie is not a Movie object")
        raise ValueError

    if directory == None:
        directory = user.home

    movie.writeFramesToDirectory(directory)