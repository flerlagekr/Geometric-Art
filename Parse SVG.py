#  This code will take an SVG created by the Geometrize web demo (https://www.samcodes.co.uk/project/geometrize-haxe-web/) 
#  Then extract each component object, writing a csv of polygon data which can be visualized in Tableau.
#  The program will also write a csv with Tableau color palette information.
#
#  Written by Ken Flerlage, November, 2017
#  This is my first ever Python program, so be easy on me!!
#
#  Instructions:
#
#  This code is in the public domain

from xml.dom import minidom
from base64 import b16encode
import math
import sys
import os
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
 
# Prompt for the input file.
def get_file():
    root = Tk()
    root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select File",filetypes = (("Scalable Vector Graphic","*.svg"),("All Files","*.*")))
    root.withdraw()

    return root.filename 

# Convert RGB Color Values to Hex.
def convertRGBtoHex (Red, Green, Blue):
    triplet = (Red, Green, Blue)
    colorHex = b'#'+ b16encode(bytes(triplet))
    colorHex = str(colorHex)
    colorHex = colorHex[2:len(colorHex)-1]
    
    return colorHex;

# Get the Hex color from the fill color string for the svg object.
def getColorHex (RGBString):
    RGBString = RGBString[4:len(RGBString)-1]
    rgbList = RGBString.split(',')
    Red = int(rgbList[0])
    Green = int(rgbList[1])
    Blue = int(rgbList[2])
    colorHex = str(convertRGBtoHex(Red, Green, Blue))
    
    return colorHex;

# Use parametric equations to generate 100 points for an ellipse.
def buildEllipsePoints (shapeType, shapeCounter, colorHex, centerX, centerY, radiusA, radiusB, rotation):
    rotationRad = math.radians(rotation)
    for i in range(100):
        # t range will be 0 to 2 Pi.
        t = i * 2 * math.pi / 100
        x = centerX + (radiusA*math.cos(t)*math.cos(rotationRad)) - (radiusB*math.sin(t)*math.sin(rotationRad))
        y = centerY + (radiusA*math.cos(t)*math.sin(rotationRad)) + (radiusB*math.sin(t)*math.cos(rotationRad))

        outString = shapeType + ',' + str(shapeCounter) + ',' + str(i+1) + ',' + str(x) + ',' + str(y) + ',' + colorHex
        out.write (outString)
        out.write('\n')

    return '';

# Process a Circle Object.
def processCircleObject (xmlString, shapeCounter):
    xmldoc = minidom.parseString(xmlString + '>')
    itemlist = xmldoc.getElementsByTagName('circle')
    s = itemlist[0]

    colorHex = getColorHex(s.attributes['fill'].value)
    outString = 'Circle,' + str(shapeCounter) + ',' + colorHex + ','+ '<color>' + colorHex + '</color>'
    outColor.write (outString)
    outColor.write('\n')

    # Get all the values we need.
    centerX = int(s.attributes['cx'].value)
    centerY = int(s.attributes['cy'].value)
    radiusA = int(s.attributes['r'].value)
    radiusB = radiusA
    rotation = 0
    buildEllipsePoints ('Circle', shapeCounter, colorHex, centerX, centerY, radiusA, radiusB, rotation)

    return '';

# Process a Rectangle Object
def processRectangleObject (xmlString, shapeCounter):
    xmldoc = minidom.parseString(xmlString + '>')
    itemlist = xmldoc.getElementsByTagName('rect')
    s = itemlist[0]

    colorHex = getColorHex(s.attributes['fill'].value)
    outString = 'Rectangle,' + str(shapeCounter) + ',' + colorHex + ','+ '<color>' + colorHex + '</color>'
    outColor.write (outString)
    outColor.write('\n')

    # Get x & y which will give us the first point (top left).
    # Then get height and width which will give us the rest of the points.
    x = int(s.attributes['x'].value)
    y = int(s.attributes['y'].value)
    height = int(s.attributes['height'].value)
    width = int(s.attributes['width'].value)

    # Write point # 1
    outString = 'Rectangle,' + str(shapeCounter) + ',1,' + str(x) + ',' + str(y) + ',' + colorHex
    out.write (outString)
    out.write('\n')

    # Write point # 2
    outString = 'Rectangle,' + str(shapeCounter) + ',2,' + str(x+width) + ',' + str(y) + ',' + colorHex
    out.write (outString)
    out.write('\n')

    # Write point # 3
    outString = 'Rectangle,' + str(shapeCounter) + ',3,' + str(x+width) + ',' + str(y+height) + ',' + colorHex
    out.write (outString)
    out.write('\n')

    # Write point # 4
    outString = 'Rectangle,' + str(shapeCounter) + ',4,' + str(x) + ',' + str(y+height) + ',' + colorHex
    out.write (outString)
    out.write('\n')

    return '';

# Process a Regular Ellipse Object (one with no rotation.)
def processRegularEllipseObject (xmlString, shapeCounter):
    xmldoc = minidom.parseString(xmlString + '>')
    itemlist = xmldoc.getElementsByTagName('ellipse')
    s = itemlist[0]

    colorHex = getColorHex(s.attributes['fill'].value)
    outString = 'Ellipse,' + str(shapeCounter) + ',' + colorHex + ','+ '<color>' + colorHex + '</color>'
    outColor.write (outString)
    outColor.write('\n')

    # Get all the values we need.
    centerX = int(s.attributes['cx'].value)
    centerY = int(s.attributes['cy'].value)
    radiusA = int(s.attributes['rx'].value)
    radiusB = int(s.attributes['ry'].value)
    rotation = 0
    buildEllipsePoints ('Circle', shapeCounter, colorHex, centerX, centerY, radiusA, radiusB, rotation)

    return '';

# Process a transformed ellipse (one with rotation).
def processEllipseObject (xmlString, shapeCounter):
    xmldoc = minidom.parseString(xmlString + '>')

    # Get transformation details first.
    itemlist = xmldoc.getElementsByTagName('g')
    s = itemlist[0]
    transform = s.attributes['transform'].value

    # Initialize variables.
    transX = 0
    transY = 0
    rotation = 0
    scaleX = 1
    scaleY = 1

    pos = transform.find('translate')
    if pos >=0:
        # Get Translation Details (this will give us an adjusted center point)
        translation = transform[pos+10:]
        pos2 = translation.find(')')
        translation = translation[:pos2]
        transList = translation.split(' ')
        transX = int(transList[0])
        transY = int(transList[1])

    pos = transform.find('rotate')
    if pos >=0:
        # Process Rotation
        rotation = transform[pos+7:]
        pos2 = rotation.find(')')
        rotation = int(rotation[:pos2])

    pos = transform.find('scale')
    if pos >=0:
        # Process Scale (this will give us adjusted radiuses)
        scale = transform[pos+6:]
        pos2 = scale.find(')')
        scale = scale[:pos2]
        scaleList = scale.split(' ')
        scaleX = int(scaleList[0])
        scaleY = int(scaleList[1])

    # Now get ellipse details.
    itemlist = xmldoc.getElementsByTagName('ellipse')
    s = itemlist[0]

    colorHex = getColorHex(s.attributes['fill'].value)
    outString = 'Ellipse,' + str(shapeCounter) + ',' + colorHex + ','+ '<color>' + colorHex + '</color>'
    outColor.write (outString)
    outColor.write('\n')

    centerX = int(s.attributes['cx'].value)
    centerY = int(s.attributes['cy'].value)
    radiusA = int(s.attributes['rx'].value)
    radiusB = int(s.attributes['ry'].value)
    buildEllipsePoints ('Ellipse', shapeCounter, colorHex, centerX+transX, centerY+transY, radiusA*scaleX, radiusB*scaleY, rotation)

    return '';

# Process a polygon object (could be rotated rectangles or triangles)
def processPolygonObject (xmlString, shapeCounter):
    xmldoc = minidom.parseString(xmlString + '>')
    itemlist = xmldoc.getElementsByTagName('polygon')
    s = itemlist[0]

    colorHex = getColorHex(s.attributes['fill'].value)
    outString = 'Polygon,' + str(shapeCounter) + ',' + colorHex + ','+ '<color>' + colorHex + '</color>'
    outColor.write (outString)
    outColor.write('\n')

    # Get and parse the points. Some objects separate x and y with space and others with comma, so we'll make them consistent.
    points = s.attributes['points'].value 
    points = points.replace(',',' ')
    pointList = points.split(' ')

    # Loop through all the points in the polygon.
    pointCounter = 1
    pointIsX = True
    for p in pointList:
        if pointIsX == True:
            x = p
            pointIsX = False
        else:
            y = p
            pointIsX = True
        
            outString = 'Polygon,' + str(shapeCounter) + ',' + str(pointCounter) + ',' + str(x) + ',' + str(y) + ',' + colorHex
            out.write (outString)
            out.write('\n')
        
            pointCounter += 1

    return '';

# Main processing routine.
# Prompt for SVG file.
xmlin = get_file()
if xmlin == "":
    messagebox.showinfo("Error", "No file selected. Program will now quit.")
    sys.exit()

# Set output files to write to the same folder.
filepath = os.path.dirname(xmlin)
if filepath[-1:] != "/":
    filepath += "/"

outFile = filepath + 'Polygon.csv'
colorFile = filepath + 'Colors.csv'

out = open(outFile,'w') 
outColor = open(colorFile,'w') 

# Write header of the polygon csv file.
outString = 'Shape,Polygon ID,Point ID,X,Y,Color Hex'
out.write (outString)
out.write('\n')

# Write header of the color csv file.
outString = 'Shape,Polygon ID,Color Hex,Palette'
outColor.write (outString)
outColor.write('\n')

xmldoc = minidom.parse(xmlin)
shapeNum = 1

# Loop through each line of the file and parse it into xml components
with open(xmlin) as f:
    lines = f.readlines()

for  line in lines:
    linesplit = line.split('>,')
    for linex in linesplit:
        linex = linex.replace('>]</svg>','')

        # If the first character is [, remove it (this is the first line of the file)
        if linex[0:1]=='[':
            linex=linex[1:]
            
        # This is a circle. 
        if linex[0:7]=='<circle':
            processCircleObject(linex, shapeNum)
            shapeNum += 1

        # This is a rectangle
        if linex[0:5]=='<rect':
            processRectangleObject(linex, shapeNum)
            shapeNum += 1

        # This is a transformed ellipse.
        if linex[0:12]=='<g transform':
            processEllipseObject(linex, shapeNum)
            shapeNum += 1

        # This is a regular, non-transformed ellipse.
        if linex[0:8]=='<ellipse':
            processRegularEllipseObject(linex, shapeNum)
            shapeNum += 1

        # This is a triangle or rotated rectangle.
        if linex[0:8]=='<polygon':
            processPolygonObject(linex, shapeNum)
            shapeNum += 1

out.close()
outColor.close()
f.close

messagebox.showinfo('Complete', 'Output files, polygon.csv and colors.csv have been written to the following directory: ' + filepath)
