import vtk
import math
import numpy
import slicer2
from vtk.util.misc import vtkGetDataRoot
VTK_DATA_ROOT = vtkGetDataRoot()

class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
 
    global worldPicker, ren0

    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
 
    def leftButtonPressEvent(self,obj,event):
		
		x, y  = self.GetInteractor().GetEventPosition()
		print "Screen Coordinates", x, y
		worldPicker.Pick(x,y,0,ren0)	
		worldPos = worldPicker.GetPickPosition()
		print worldPos
		self.OnLeftButtonDown()

		return


worldPicker = vtk.vtkWorldPointPicker()

# Start by loading some data.
reader = vtk.vtkImageReader2()
reader.SetFilePrefix("/home/vaidya/code/CurvedMPR/quarter/quarter")
reader.SetDataExtent(0, 63, 0, 63, 1, 93)
reader.SetDataSpacing(1, 1, 1)
#reader.SetDataSpacing(3.2, 3.2, 1.5)
reader.SetDataOrigin(0.0, 0.0, 0.0)
reader.SetDataScalarTypeToUnsignedShort()
reader.UpdateWholeExtent()

# Calculate the center of the volume
reader.GetOutput().UpdateInformation()
(xMin, xMax, yMin, yMax, zMin, zMax) = reader.GetOutput().GetWholeExtent()
(xSpacing, ySpacing, zSpacing) = reader.GetOutput().GetSpacing()
(x0, y0, z0) = reader.GetOutput().GetOrigin()

center = [x0 + xSpacing * 0.5 * (xMin + xMax),
          y0 + ySpacing * 0.5 * (yMin + yMax),
          z0 + zSpacing * 0.5 * (zMin + zMax)]
          
print "Center: ", center
print "(xMin, xMax, yMin, yMax, zMin, zMax)", xMin, xMax, yMin, yMax, zMin, zMax          
          
# Create a greyscale lookup table
table = vtk.vtkLookupTable()
table.SetRange(0, 2000) # image intensity range
table.SetValueRange(0.0, 1.0) # from black to white
table.SetSaturationRange(0.0, 0)
table.SetRampToLinear()
table.Build()

#-----------------------------------------------------------------

def findDistanceBetweenTwoPoints(startPoint, endPoint):
	
	dist = 0.0
	for i in range(0,3):
		dist += math.pow((endPoint[i] - startPoint[i]),2)	
		
	return math.sqrt(dist)

def findAngleBetweenTwoPoints(startPoint, endPoint):
	
	delY = endPoint[1] - startPoint[1]
	delX = endPoint[0] - startPoint[0]
		
	if delX == 0 and delY >= 0:
		return math.degrees(numpy.arctan(-float('inf')))
	elif delX == 0 and delY < 0:
		return math.degrees(numpy.arctan(float('inf')))
	else:
		return math.degrees(numpy.arctan( delY / delX ))
	

def computeMPR(endPoints):

	numberOfSlices = len(endPoints)-1
	points = [[0 for x in range(len(endPoints)-1)] for x in range(len(endPoints)-1)]

	angle = range(numberOfSlices)
	#extentLength = range(numberOfSlices)
	extentLength = [[0 for x in range(len(endPoints)-1)] for x in range(len(endPoints)-1)]

	setLocation = range(numberOfSlices)
	distance = range(numberOfSlices)

	for i in range(0, len(endPoints)-1):	
		for j in range(0,3):
			points[i][j] = (endPoints[i][j] + endPoints[i+1][j]) * 0.5


	for i in range(0, len(endPoints)-1):	
		distance[i] = findDistanceBetweenTwoPoints(endPoints[i], endPoints[i+1])	
		angle[i] = findAngleBetweenTwoPoints(endPoints[i], endPoints[i+1])
		print "D: ",distance[i],"A: ", angle[i]

	temp = -20

	for i in range(0, len(endPoints)-1):
				
		extentLength[i][0] = ( distance[i] )# * 0.75 )
		print "Distance :: ",extentLength[i][0]
		extentLength[i][1] = 94 
		temp -= distance[i]
		setLocation[i] = temp #* 0.25
		print "setLocation ::",setLocation[i]
	
	#extentLength = [[15,94],[18,94],[15,94]]
	#setLocation = [0,0,0]

	for i in range(0,numberOfSlices):
		
		aslice[i] = vtk.vtkImageReslice()
		aslice[i].SetInputConnection(reader.GetOutputPort())
		aslice[i].SetOutputDimensionality(2)  
		aslice[i].SetResliceAxesOrigin(points[i][0], points[i][1], points[i][2])
		aslice[i].SetResliceAxesDirectionCosines(1, 0,  0, 
											0, math.cos(math.radians(90)),  -math.sin(math.radians(90)),
											0, math.sin(math.radians(90)),  math.cos(math.radians(90)) )
		aslice[i].SetInterpolationModeToLinear()

		transform = vtk.vtkTransform() # rotate about the center of the image
		transform.Translate(center[0], center[1], center[2] )
		transform.RotateZ(angle[i])
		transform.Translate(-center[0], -center[1], -center[2] )
		transform.Translate(0,0,0) # -10, 0, 0
		
		aslice[i].SetResliceTransform(transform)

		aslice[i].SetOutputExtent(0,extentLength[i][0],0,extentLength[i][1],0,0)
		
		color[i] = vtk.vtkImageMapToColors()
		color[i].SetLookupTable(table)
		color[i].SetInputConnection(aslice[i].GetOutputPort())
		
		
		actor[i] = vtk.vtkImageActor()
		actor[i].SetInput(color[i].GetOutput())
		actor[i].SetPosition(setLocation[i],0,0)


#----------------------------------------------------------------------------------

# --- multi-view ---
rw = vtk.vtkRenderWindow()
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(MyInteractorStyle())
iren.SetRenderWindow(rw)
    
# Define viewport ranges
xmins=[0, .5 , 0, .5]
xmaxs=[0.5, 1, 0.5, 1]
ymins=[0, 0 ,.5, .5]
ymaxs=[0.5, 0.5 ,1 ,1]

ren = range(4)

numberOfSlices = 3
aslice = range(numberOfSlices)
color = range(numberOfSlices)
actor = range(numberOfSlices)

points = [[20,40,47],[20,20,47],[40,20,47],[40,40,47]]
#points = [[20*3.2, 40*3.2, 47*1.5],[20*3.2 , 20*3.2, 47*1.5],[40*3.2, 20*3.2, 47*1.5],[40*3.2, 40*3.2, 47*1.5]]
#points =[[20,30,47],[30,20,47],[40,30,47], [60, 40, 47]]
#points = [[0,60,47],[20,20,47],[40,20,47],[60,20,47]]
computeMPR(points)

'''
angle = [0, 90,0,-90, 0]
extentLength = [[25,94],[15,94],[15,94],[15,94],[25, 94]]
setLocation = [20,10,0,-10,-20]

computeMPR(points, angle, extentLength, setLocation)
'''

for i in range(0, 4):	
	ren[i] = vtk.vtkRenderer()
	ren[i].SetViewport(xmins[i],ymins[i],xmaxs[i],ymaxs[i])


for i in range(0, numberOfSlices):
	ren[1].AddActor2D(actor[i])

'''
points =[[20,30,47],[30,20,47],[40,30,47]]
angle = [90,0,-90]
extentLength = [[64,94],[64,94],[64,94]]
setLocation = [0,0,0]

computeMPR(points, angle, extentLength, setLocation)

ren[0].AddActor2D(actor[0])
'''

'''
ren[0].AddViewProp(slicer2.volume)
camera = ren[0].GetActiveCamera()
c = slicer2.volume.GetCenter()
camera.SetFocalPoint(c[0], c[1], c[2])
camera.SetPosition(c[0] + 400, c[1], c[2])
camera.SetViewUp(0, 0, -1)
'''


ren[2].AddActor2D(actor[1])
ren[3].AddActor2D(actor[2])

for i in range(0,4):
	rw.AddRenderer(ren[i])

rw.SetSize(600, 600)
rw.Render()
iren.Initialize()
iren.Start()

#  renderer 0: BOTTOM LEFT
#  renderer 1: BOTTOM RIGHT
#  renderer 2: TOP LEFT
#  renderer 3: TOP RIGHT

