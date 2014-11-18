import vtk
import math
#import slicer2
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
#reader.SetDataSpacing(3.2, 3.2, 1.5) - check it out.

reader.SetDataSpacing(1, 1, 1)
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
          
# Create a greyscale lookup table
table = vtk.vtkLookupTable()
table.SetRange(0, 2000) # image intensity range
table.SetValueRange(0.0, 1.0) # from black to white
table.SetSaturationRange(0.0, 0)
table.SetRampToLinear()
table.Build()


def computeMPR(points, angle, extentLength, setLocation):

	for i in range(0,numberOfSlices):
		
		aslice[i] = vtk.vtkImageReslice()
		aslice[i].SetInputConnection(reader.GetOutputPort())
		aslice[i].SetOutputDimensionality(2)  
		aslice[i].SetResliceAxesOrigin(points[i][0], points[i][1], points[i][2])
		aslice[i].SetResliceAxesDirectionCosines(1, 0,  0, 
											0, math.cos(math.radians(angle[i])),  -math.sin(math.radians(angle[i])),
											0, math.sin(math.radians(angle[i])),  math.cos(math.radians(angle[i])) )
		
		aslice[i].SetInterpolationModeToLinear()		
		aslice[i].SetOutputExtent(0,extentLength[i][0],0,extentLength[i][1],0,0)
		
		color[i] = vtk.vtkImageMapToColors()
		color[i].SetLookupTable(table)
		color[i].SetInputConnection(aslice[i].GetOutputPort())
		
		actor[i] = vtk.vtkImageActor()
		actor[i].SetInput(color[i].GetOutput())
		actor[i].SetPosition(0,setLocation[i],0)


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
for i in range(0, 4):	
	ren[i] = vtk.vtkRenderer()
	ren[i].SetViewport(xmins[i],ymins[i],xmaxs[i],ymaxs[i])

numberOfSlices = 3
aslice = range(numberOfSlices)
color = range(numberOfSlices)
actor = range(numberOfSlices)

points =[[30,30,47],[30,10,47],[30,50,47]]
angle = [0,90,270]
extentLength = [[64, 25],[64, 15],[64, 15]]
setLocation = [0,22,-22]

computeMPR(points, angle, extentLength, setLocation)
for i in range(0, numberOfSlices):
	ren[1].AddActor2D(actor[i])


points =[[30,30,47],[30,10,47],[30,50,47]]
angle = [0,90,270]
extentLength = [[64,94],[64,94],[64,94]]
setLocation = [0,0,0]

computeMPR(points, angle, extentLength, setLocation)
ren[0].AddActor2D(actor[0])
ren[2].AddActor2D(actor[1])
ren[3].AddActor2D(actor[2])

for i in range(0,4):
	rw.AddRenderer(ren[i])

rw.SetSize(600, 600)
rw.Render()
iren.Initialize()
iren.Start()


										

'''
ren0.AddViewProp(slicer2.volume)
camera = ren0.GetActiveCamera()
c = slicer2.volume.GetCenter()
camera.SetFocalPoint(c[0], c[1], c[2])
camera.SetPosition(c[0] + 400, c[1], c[2])
camera.SetViewUp(0, 0, -1)
'''	

#  renderer 0: BOTTOM LEFT
#  renderer 1: BOTTOM RIGHT
#  renderer 2: TOP LEFT
#  renderer 3: TOP RIGHT

