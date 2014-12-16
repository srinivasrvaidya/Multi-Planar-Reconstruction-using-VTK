import vtk
import math
import numpy
import slicer_read_Dataset
from vtk.util.misc import vtkGetDataRoot
VTK_DATA_ROOT = vtkGetDataRoot()

DEBUG_MODE = 0

#-------- Initialization ------------------

worldPicker = vtk.vtkWorldPointPicker()
clickPointsList = []
renderer = vtk.vtkRenderer()
aslice = range(10)
color = range(10)
actor = range(10)
mpv_renderer = range(4)


# Start by loading some data.
reader = vtk.vtkImageReader2()
reader.SetFilePrefix("../Dataset/quarter")
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

if DEBUG_MODE:          
	print "Center: ", center
	print "(xMin, xMax, yMin, yMax, zMin, zMax)", xMin, xMax, yMin, yMax, zMin, zMax          
          
# ------------- Basic Planes ------------------------------
         
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

#Oblique slice.
obliqueSlice = vtk.vtkImageReslice()
obliqueSlice.SetInputConnection(reader.GetOutputPort())
obliqueSlice.SetOutputDimensionality(2)            

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

#ObliqueSlice
obliqueSlice.SetResliceAxesOrigin(center[0], center[1], center[2])
		
obliqueSlice.SetResliceAxesDirectionCosines(1, 0,  0, 
										0, math.cos(math.radians(45)),  -math.sin(math.radians(45)),
										0, math.sin(math.radians(45)),  math.cos(math.radians(45)) )
obliqueSlice.SetInterpolationModeToLinear()

color_oblique = vtk.vtkImageMapToColors()
color_oblique.SetLookupTable(table)
color_oblique.SetInputConnection(obliqueSlice.GetOutputPort())
		
		
actor_oblique = vtk.vtkImageActor()
actor_oblique.SetInput(color_oblique.GetOutput())
#actor[i].SetPosition(setLocation[i],0,0)


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
	

def computeMPR(endPoints, plane, planeAngle):

	numberOfSlices = len(endPoints)-1
	points = [[0 for x in range(3)] for x in range(len(endPoints)-1)]

	angle = range(numberOfSlices)

	extentLength = [[0 for x in range(len(endPoints))] for x in range(len(endPoints))]

	setLocation = range(numberOfSlices)
	distance = range(numberOfSlices)

	print "-", planeAngle

	for i in range(0, numberOfSlices):	
		for j in range(0,3):
			points[i][j] = (endPoints[i][j] + endPoints[i+1][j]) * 0.5
			
			if DEBUG_MODE:
				print "Mid Point:: [",i,",],[",j,"] :: ",points[i][j]
			
	for i in range(0, numberOfSlices):	
		distance[i] = findDistanceBetweenTwoPoints(endPoints[i], endPoints[i+1])	
		angle[i] = findAngleBetweenTwoPoints(endPoints[i], endPoints[i+1])

		if DEBUG_MODE:
			print "For the points:: ",endPoints[i]," and ", endPoints[i+1]
			print "Distance: ",distance[i],"Angle: ", angle[i]

	temp = -40

	for i in range(0, numberOfSlices):
		extentLength[i][0] =  distance[i] #* 0.95 
		extentLength[i][1] = 94 
		temp += distance[i]
		setLocation[i] = temp  #* 0.05
		
	for i in range(0, numberOfSlices):
		
		aslice[i] = vtk.vtkImageReslice()
		aslice[i].SetInputConnection(reader.GetOutputPort())
		aslice[i].SetOutputDimensionality(2)  
		aslice[i].SetResliceAxesOrigin(points[i][0] * aslice[i].GetOutput().GetSpacing()[0], 
										points[i][1] * aslice[i].GetOutput().GetSpacing()[1], 
										points[i][2] * aslice[i].GetOutput().GetSpacing()[2])
		
		aslice[i].SetResliceAxesDirectionCosines(1, 0,  0, 
												0, math.cos(math.radians( float(planeAngle) )),  -math.sin(math.radians( float(planeAngle)) ),
												0, math.sin(math.radians( float(planeAngle) )),  math.cos(math.radians( float(planeAngle) )) ) 
		aslice[i].SetInterpolationModeToLinear()
		
		transform = vtk.vtkTransform() # rotate about the center of the image
	
		transform.Translate(center[0], center[1], center[2] )
		transform.RotateZ(angle[i])
		transform.Translate(-center[0], -center[1], -center[2] )
	
		transform.Translate(center[0]-points[i][0], center[1]-points[i][1], center[2]-points[i][2]) # -10, 0, 0
		
		aslice[i].SetResliceTransform(transform)

		aslice[i].SetOutputExtent(0,extentLength[i][0],0,extentLength[i][1],0,0)
		
		color[i] = vtk.vtkImageMapToColors()
		color[i].SetLookupTable(table)
		color[i].SetInputConnection(aslice[i].GetOutputPort())
		
		
		actor[i] = vtk.vtkImageActor()
		actor[i].SetInput(color[i].GetOutput())
		actor[i].SetPosition(setLocation[i],0,0)
		
	#	renderer.AddActor2D(actor[i])
		
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
		mode = 0 				#"SAGITTAL"
	elif x < 600 and y < 300:
		mode = 1 				#"AXIAL"
	elif x > 300 and y > 300:
		mode = 3 				#"CORONAL"
	else:
		mode = 4
			
			
def MouseMoveCallback(obj, event):
    (lastX, lastY) = interactor.GetLastEventPosition()
    (mouseX, mouseY) = interactor.GetEventPosition()
    if actions["Slicing"] == 1:
		deltaY = mouseY - lastY
		
		if deltaY > 0:
			deltaY = 5
		else:
			deltaY = -5
	
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
        

      
def LeftButtonPressEvent(obj,event):
		
		global ren, smart, mode , clickPoints, polygonActor, polygon, polygonMapper, renderer
		
		points = vtk.vtkPoints()
		points.SetNumberOfPoints(6)
		
		
		x, y  = obj.GetInteractor().GetEventPosition()
		worldPicker.Pick(x,y,0,mpv_renderer[1])
		worldPos = worldPicker.GetPickPosition()
		singleClickedPoint = [worldPos[0]+center[0], worldPos[1]+center[1], worldPos[2]+center[2]]		
		
		clickPointsList.append(singleClickedPoint)
		
		displayClickPoints(clickPointsList)
		
		if DEBUG_MODE:
			print "Screen Coordinates:: ", x, y	
			print "Mode:: ",mode
			print "Real world co-ordinates:: ",worldPos[0]+center[0], worldPos[1]+center[1], worldPos[2]+center[2]		
			print "ClickPoints:: "
			print " ",clickPointsList
			#	obj.OnLeftButtonDown()
		return        

def displayClickPoints(clickPoints):
	
	points = vtk.vtkPoints()
	lines = vtk.vtkCellArray()
	polygon = vtk.vtkPolyData()
	polygonMapper = vtk.vtkPolyDataMapper()
	polygonActor = vtk.vtkActor()
		
	points.SetNumberOfPoints(4)
	points.SetPoint(0, 0.0, -1.0, 0.0)
	points.SetPoint(1, -0.7, -0.5, 0.0)
	points.SetPoint(2,   0.7,  0.5, 0.0)
	points.SetPoint(3, 0.0,  -1.0, 0.0)

		
	lines.InsertNextCell(4)
	lines.InsertCellPoint(0)
	lines.InsertCellPoint(1)
	lines.InsertCellPoint(2)
	lines.InsertCellPoint(3)
		
	polygon.SetPoints(points)
	polygon.SetLines(lines)
		
	polygonMapper.SetInputConnection(polygon.GetProducerPort())
	polygonActor.SetMapper(polygonMapper)	
	
	mpv_renderer[1].ResetCamera()
	mpv_renderer[1].AddActor(polygonActor)
	rw.Render()
		

def KeyPressEvent(obj, event):

	global actor, mpr_rw, renderer, singleClickedPoint, points

	keyCode = obj.GetKeyCode()

	if DEBUG_MODE:
		print "Key Pressed: ",obj.GetKeyCode()
		
	if keyCode in ['r', 'R']:   # Render_Mode
		
	#	computeMPR(clickPointsList, "Axial", 90)
		computeMPR(clickPointsList, "Axial", 90)
		renderer.ResetCamera()		
		
		for i in range(0, len(clickPointsList) - 1):
			renderer.AddActor2D(actor[i])    
		
		mpr_rw.AddRenderer(renderer)
		mpr_rw.Render()	

	if keyCode in ['c','C']:    # ViewPort Clear Mode & Reset
		
		for i in range(0, len(clickPointsList) - 1):
			renderer.RemoveActor2D(actor[i])
		
		mpr_rw.AddRenderer(renderer)
		mpr_rw.Render()
				
		del clickPointsList[:]

#------ CALL BACK REGISTRATION --------------

interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", LeftButtonPressEvent)
interactor.AddObserver("KeyPressEvent", KeyPressEvent)
        
#------ Define viewport ranges ---------------

xmins=[0, .5 , 0, .5]
xmaxs=[0.5, 1, 0.5, 1]
ymins=[0, 0 ,.5, .5]
ymaxs=[0.5, 0.5 ,1 ,1]

points = [[20,60,47],[20,20,47],[40,20,47],[60,60,47]] 

numberOfSlices = len(points) - 1

for i in range(0, 4):	
	mpv_renderer[i] = vtk.vtkRenderer()
	mpv_renderer[i].SetViewport(xmins[i],ymins[i],xmaxs[i],ymaxs[i])

mpv_renderer[1].SetUseDepthPeeling(1)
mpv_renderer[1].SetOcclusionRatio(0.5)


mpv_renderer[2].AddViewProp(slicer_read_Dataset.volume)
camera = mpv_renderer[2].GetActiveCamera()
c = slicer_read_Dataset.volume.GetCenter()
camera.SetFocalPoint(c[0], c[1], c[2])
camera.SetPosition(c[0] + 400, c[1], c[2])
camera.SetViewUp(0, 0, -1)


displayClickPoints(clickPointsList)
mpv_renderer[1].AddActor2D(actor_axial)
mpv_renderer[3].AddActor2D(actor_oblique)
mpv_renderer[0].AddActor2D(actor_sagittal)

for i in range(0,4):
	rw.AddRenderer(mpv_renderer[i])

rw.SetWindowName("Multi Planar Viewer Window")
rw.SetSize(600, 600)
rw.Render()

mpr_rw.SetWindowName("Multi Planar Reconstruction Window")
mpr_rw.SetSize(600, 300)
mpr_rw.Render()

interactor.Start()

#--------- Renderer numbering ------------

#  renderer 0: BOTTOM LEFT
#  renderer 1: BOTTOM RIGHT
#  renderer 2: TOP LEFT
#  renderer 3: TOP RIGHT



