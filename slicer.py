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
          
# ---------------------------------------------------------------
         
axial = vtk.vtkMatrix4x4()
axial.DeepCopy((1, 0, 0, center[0],
                0, 1, 0, center[1],
                0, 0, 1, center[2],
                0, 0, 0, 1))

coronal = vtk.vtkMatrix4x4()  # x axis
coronal.DeepCopy((1, 0, 0, center[0],
                  0, 0, 1, center[1],
                  0,-1, 0, center[2],
                  0, 0, 0, 1))

sagittal = vtk.vtkMatrix4x4()
sagittal.DeepCopy((0, 0,-1, center[0],
                   1, 0, 0, center[1],
                   0,-1, 0, center[2],
                   0, 0, 0, 1))          
          
#-------------

# Extract a slice in the desired orientation
reslice_axial = vtk.vtkImageReslice()
reslice_axial.SetInputConnection(reader.GetOutputPort())
reslice_axial.SetOutputDimensionality(2)
reslice_axial.SetResliceAxes(axial)
reslice_axial.SetInterpolationModeToLinear()

# Extract a slice in the desired orientation
reslice_coronal = vtk.vtkImageReslice()
reslice_coronal.SetInputConnection(reader.GetOutputPort())
reslice_coronal.SetOutputDimensionality(2)
reslice_coronal.SetResliceAxes(coronal)
reslice_coronal.SetInterpolationModeToLinear()

# Extract a slice in the desired orientation
reslice_sagittal = vtk.vtkImageReslice()
reslice_sagittal.SetInputConnection(reader.GetOutputPort())
reslice_sagittal.SetOutputDimensionality(2)
reslice_sagittal.SetResliceAxes(sagittal)
reslice_sagittal.SetInterpolationModeToLinear()
          
          
# Create a greyscale lookup table
table = vtk.vtkLookupTable()
table.SetRange(0, 2000) # image intensity range
table.SetValueRange(0.0, 1.0) # from black to white
table.SetSaturationRange(0.0, 0)
table.SetRampToLinear()
table.Build()


# Map the image through the lookup table
color_axial = vtk.vtkImageMapToColors()
color_axial.SetLookupTable(table)
color_axial.SetInputConnection(reslice_axial.GetOutputPort())

# Display the image
actor_axial = vtk.vtkImageActor()
actor_axial.SetInput(color_axial.GetOutput())


# Map the image through the lookup table
color_coronal = vtk.vtkImageMapToColors()
color_coronal.SetLookupTable(table)
color_coronal.SetInputConnection(reslice_coronal.GetOutputPort())

# Display the image
actor_coronal = vtk.vtkImageActor()
actor_coronal.SetInput(color_coronal.GetOutput())

# Map the image through the lookup table
color_sagittal = vtk.vtkImageMapToColors()
color_sagittal.SetLookupTable(table)
color_sagittal.SetInputConnection(reslice_sagittal.GetOutputPort())

# Display the image
actor_sagittal = vtk.vtkImageActor()
actor_sagittal.SetInput(color_sagittal.GetOutput())



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
	#	print "D: ",distance[i],"A: ", angle[i]

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
    
# Set up the interaction
interactorStyle = vtk.vtkInteractorStyleImage()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(interactorStyle)
rw.SetInteractor(interactor)

# --------- another window() ------------
mpr_rw = vtk.vtkRenderWindow()    
mpr_iren = vtk.vtkRenderWindowInteractor()
mpr_iren.SetInteractorStyle(MyInteractorStyle())
mpr_iren.SetRenderWindow(mpr_rw)
    

# Create callbacks for slicing the image
actions = {}
actions["Slicing"] = 0
mode = 4

def ButtonCallback(obj, event):
	
    if event == "LeftButtonPressEvent":
        actions["Slicing"] = 1
    else:
        actions["Slicing"] = 0

	x, y  = obj.GetInteractor().GetEventPosition()
	
	global mode
	if x < 300 and y < 300:
		mode = 0 #"SAGITTAL"
	elif x < 600 and y < 300:
		mode = 1 #"AXIAL"
	elif x > 300 and y > 300:
		mode = 3 #"CORONAL"
	else:
		mode = 4
			
def MouseMoveCallback(obj, event):
    (lastX, lastY) = interactor.GetLastEventPosition()
    (mouseX, mouseY) = interactor.GetEventPosition()
    if actions["Slicing"] == 1:
		deltaY = mouseY - lastY
	
		if mode ==  3: 		#"CORONAL":
			reslice_coronal.Update()
			sliceSpacing = reslice_coronal.GetOutput().GetSpacing()[2]
			matrix = reslice_coronal.GetResliceAxes()			
		elif mode == 1: 	#"AXIAL":
			reslice_axial.Update()
			sliceSpacing = reslice_axial.GetOutput().GetSpacing()[2]
			matrix = reslice_axial.GetResliceAxes()
		elif mode == 0: 	#"SAGITTAL":
			reslice_sagittal.Update()
			sliceSpacing = reslice_sagittal.GetOutput().GetSpacing()[2]
			matrix = reslice_sagittal.GetResliceAxes()	
		else:
		#	print " -- 3d model clicked -- "
			return;
			
		# move the center point that we are slicing through
		center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
		matrix.SetElement(0, 3, center[0])
		matrix.SetElement(1, 3, center[1])
		matrix.SetElement(2, 3, center[2])
		rw.Render()        
		rw.Render()        
    else:
        interactorStyle.OnMouseMove()


interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)    
        
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

renderer = vtk.vtkRenderer()

for i in range(0, numberOfSlices):
	renderer.AddActor2D(actor[i])            

mpr_rw.AddRenderer(renderer)	
'''	
points =[[20,30,47],[30,20,47],[40,30,47]]
angle = [90,0,-90]
extentLength = [[64,94],[64,94],[64,94]]
setLocation = [0,0,0]

computeMPR(points, angle, extentLength, setLocation)
'''



ren[2].AddActor2D(actor[0])
ren[2].AddViewProp(slicer2.volume)
camera = ren[2].GetActiveCamera()
c = slicer2.volume.GetCenter()
camera.SetFocalPoint(c[0], c[1], c[2])
camera.SetPosition(c[0] + 400, c[1], c[2])
camera.SetViewUp(0, 0, -1)


ren[1].AddActor2D(actor_axial)
ren[3].AddActor2D(actor_coronal)
ren[0].AddActor2D(actor_sagittal)

for i in range(0,4):
	rw.AddRenderer(ren[i])

rw.SetSize(600, 600)
rw.Render()
mpr_rw.Render()

#iren.Initialize()
#iren.Start() 

interactor.Start()

#  renderer 0: BOTTOM LEFT
#  renderer 1: BOTTOM RIGHT
#  renderer 2: TOP LEFT
#  renderer 3: TOP RIGHT

