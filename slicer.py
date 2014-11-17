import vtk
import math
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
          
axial = vtk.vtkMatrix4x4()
axial.DeepCopy((1, 0, 0, center[0],
                0, 1, 0, center[1],
                0, 0, 1, center[2],
                0, 0, 0, 1))
          
axial2 = vtk.vtkMatrix4x4()
axial2.DeepCopy((1, 0, 0, center[0],
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

oblique = vtk.vtkMatrix4x4()
oblique.DeepCopy((1, 0, 0, center[0],
				  0, 1, 0.707, center[1],
				  0, -0.707, 1, center[2],
				  0, 0, 0, 1))

# Extract a slice in the desired orientation
reslice1 = vtk.vtkImageReslice()
reslice1.SetInputConnection(reader.GetOutputPort())
reslice1.SetOutputDimensionality(2)  # to get 2d image

print "Center ", center

reslice1.SetResliceAxesOrigin(30, 20, 47)
reslice1.SetResliceAxesDirectionCosines(1, 0,  0, 
										0, math.cos(math.radians(90)),  -math.sin(math.radians(90)),
										0, math.sin(math.radians(90)),  math.cos(math.radians(90)) )


reslice1a = vtk.vtkImageReslice()
reslice1a.SetInputConnection(reader.GetOutputPort())
reslice1a.SetOutputDimensionality(2)

#reslice1a.SetResliceAxesOrigin(center[0], center[1], center[2])
reslice1a.SetResliceAxesOrigin(30, 20, 47)
reslice1a.SetResliceAxesDirectionCosines(1, 0,  0, 
										0, math.cos(math.radians(90)),  -math.sin(math.radians(90)),
										0, math.sin(math.radians(90)),  math.cos(math.radians(90)) )

										 

reslice2 = vtk.vtkImageReslice()
reslice2.SetInputConnection(reader.GetOutputPort())
reslice2.SetOutputDimensionality(2)

reslice2.SetResliceAxesOrigin(20, 30, 47)
reslice2.SetResliceAxesDirectionCosines(1, 0,  0, 
										0, math.cos(math.radians(90)),  -math.sin(math.radians(90)),
										0, math.sin(math.radians(90)),  math.cos(math.radians(90)) )


reslice2a = vtk.vtkImageReslice()
reslice2a.SetInputConnection(reader.GetOutputPort())

reslice2a.SetOutputDimensionality(2)
#reslice2a.SetResliceAxesOrigin(center[0]+10, center[1], center[2])
reslice2a.SetResliceAxesOrigin(20, 30, 47)
reslice2a.SetResliceAxesDirectionCosines(1, 0,  0, 
										0, math.cos(math.radians(90)),  -math.sin(math.radians(90)),
										0, math.sin(math.radians(90)),  math.cos(math.radians(90)) )

reslice3 = vtk.vtkImageReslice()
reslice3.SetInputConnection(reader.GetOutputPort())
reslice3.SetOutputDimensionality(2)
reslice3.SetResliceAxesOrigin(40, 30, 47)
#reslice1.SetResliceAxesOrigin(33,33,33)
# x axis

reslice3.SetResliceAxesDirectionCosines(1, 0,  0, 
										0, math.cos(math.radians(90)),  -math.sin(math.radians(90)),
										0, math.sin(math.radians(90)),  math.cos(math.radians(90)) )


reslice3a = vtk.vtkImageReslice()
reslice3a.SetInputConnection(reader.GetOutputPort())
reslice3a.SetOutputDimensionality(2)
reslice3a.SetResliceAxesOrigin(40, 30, 47)
#reslice1.SetResliceAxesOrigin(33,33,33)
# x axis

reslice3a.SetResliceAxesDirectionCosines(1, 0,  0, 
										0, math.cos(math.radians(90)),  -math.sin(math.radians(90)),
										0, math.sin(math.radians(90)),  math.cos(math.radians(90)) )




reslice1.SetInterpolationModeToLinear()
reslice2.SetInterpolationModeToLinear()
reslice1a.SetInterpolationModeToLinear()
reslice2a.SetInterpolationModeToLinear()
reslice3.SetInterpolationModeToLinear()
reslice3a.SetInterpolationModeToLinear()

transform1 = vtk.vtkTransform() # rotate about the center of the image
transform1.Translate(center[0], center[1], center[2] )
transform1.RotateZ(0)
transform1.Translate(-center[0], -center[1], -center[2] )
transform1.Translate(0,0,0) # -10, 0, 0
#transform1.Scale(2,1,1)


transform2 = vtk.vtkTransform() # rotate about the center of the image
transform2.Translate(center[0], center[1], center[2] )
transform2.RotateZ(99)
transform2.Translate(-center[0], -center[1], -center[2] )


transform3 = vtk.vtkTransform() # rotate about the center of the image
transform3.Translate(center[0], center[1], center[2] )
transform3.RotateZ(270)
transform3.Translate(-center[0], -center[1], -center[2] )
transform3.Translate(0,0,0) # -10, 0, 0

reslice2.SetResliceTransform(transform2)
reslice2a.SetResliceTransform(transform2)
reslice3.SetResliceTransform(transform3)
reslice3a.SetResliceTransform(transform3)

reslice1.SetOutputExtent(0,63,0,94,0,0)
reslice2.SetOutputExtent(0,63,0,94,0,0)
reslice3.SetOutputExtent(0,63,0,94,0,0)

reslice1a.SetOutputExtent(0,15,0,94,0,0)
reslice2a.SetOutputExtent(0,15,0,94,0,0)
reslice3a.SetOutputExtent(0,15,0,94,0,0)

# Create a greyscale lookup table
table = vtk.vtkLookupTable()
table.SetRange(0, 2000) # image intensity range
table.SetValueRange(0.0, 1.0) # from black to white
table.SetSaturationRange(0.0, 0)
table.SetRampToLinear()
table.Build()

# Map the image through the lookup table == 1
color1 = vtk.vtkImageMapToColors()
color1.SetLookupTable(table)
color1.SetInputConnection(reslice1.GetOutputPort())

# Map the image through the lookup table  == 2
color2 = vtk.vtkImageMapToColors()
color2.SetLookupTable(table)
color2.SetInputConnection(reslice2.GetOutputPort())

color1a = vtk.vtkImageMapToColors()
color1a.SetLookupTable(table)
color1a.SetInputConnection(reslice1a.GetOutputPort())

color2a = vtk.vtkImageMapToColors()
color2a.SetLookupTable(table)
color2a.SetInputConnection(reslice2a.GetOutputPort())

color3 = vtk.vtkImageMapToColors()
color3.SetLookupTable(table)
color3.SetInputConnection(reslice3.GetOutputPort())

color3a = vtk.vtkImageMapToColors()
color3a.SetLookupTable(table)
color3a.SetInputConnection(reslice3a.GetOutputPort())

# Display the image == 1
actor1 = vtk.vtkImageActor()
actor1.SetInput(color1.GetOutput())

# Display the image == 2
actor2 = vtk.vtkImageActor()
actor2.SetInput(color2.GetOutput())

# Display image == 3
actor3 = vtk.vtkImageActor()
actor3.SetInput(color3.GetOutput())


# Display the image MPR == 1
actor1a = vtk.vtkImageActor()
actor1a.SetInput(color1a.GetOutput())
actor1a.SetPosition(0,0,0)
#actor1a.RotateZ(90)
	
# Display the image MPR == 2
actor2a = vtk.vtkImageActor()
actor2a.SetInput(color2a.GetOutput())
actor2a.SetPosition(12,0,0)
#actor2a.RotateZ(90)

# Display the image MPR == 2
actor3a = vtk.vtkImageActor()
actor3a.SetInput(color3a.GetOutput())
actor3a.SetPosition(-12,0,0)



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

# volume renderer 0 : TOP LEFT
ren0 = vtk.vtkRenderer()

ren0.SetViewport(xmins[2],ymins[2],xmaxs[2],ymaxs[2])
ren0.AddActor2D(actor1)

'''
ren0.AddViewProp(slicer2.volume)
camera = ren0.GetActiveCamera()
c = slicer2.volume.GetCenter()
camera.SetFocalPoint(c[0], c[1], c[2])
camera.SetPosition(c[0] + 400, c[1], c[2])
camera.SetViewUp(0, 0, -1)
'''

#  renderer 1 BOTTOM LEFT
ren1 = vtk.vtkRenderer()
ren1.SetViewport(xmins[0],ymins[0],xmaxs[0],ymaxs[0])
ren1.AddActor2D(actor3)


#  renderer 2 TOP RIGHT
ren2 = vtk.vtkRenderer()
ren2.SetViewport(xmins[3],ymins[3],xmaxs[3],ymaxs[3])
ren2.AddActor2D(actor2)

# renderer 3 BOTTOM RIGHT
ren3 = vtk.vtkRenderer()
ren3.SetViewport(0.5,0,1,0.5)

ren3.AddActor2D(actor1a)
ren3.AddActor2D(actor2a)
ren3.AddActor2D(actor3a)

rw.AddRenderer(ren0)
rw.AddRenderer(ren1)
rw.AddRenderer(ren2)
rw.AddRenderer(ren3)
rw.SetSize(600, 600)
rw.Render()


iren.Initialize()
iren.Start()

'''


reslice2.SetResliceAxesDirectionCosines(math.cos(math.radians(150)),  -math.sin(math.radians(150)) , 0 ,
										math.sin(math.radians(150)),   math.cos(math.radians(150)) , 0 , 
										      0     ,	   0         , 1 )


reslice2.SetResliceAxesDirectionCosines(math.cos(20),   0, math.sin(20),
												   0,   1,       0,
										-math.sin(20),   0,  math.cos(20) )


table1 = vtk.vtkLookupTable()
table1.SetRange(0, 2000) # image intensity range
table1.SetValueRange(0.0, 1.0) # from black to white
table1.SetSaturationRange(0.0, .30)
table1.SetRampToLinear()
table1.Build()

table2 = vtk.vtkLookupTable()
table2.SetRange(0, 2000) # image intensity range
table2.SetValueRange(0.0, 1.0) # from black to white
table2.SetSaturationRange(0.0, 1.0)
table2.SetRampToLinear()
table2.Build()


#reslice.SetResliceAxes(oblique) #The ResliceAxes are used most often to permute the data, e.g. to extract ZY or XZ slices of a volume as 2D XY images. 
#reslice1.SetResliceAxes(sagittal)
#reslice1.SetResliceAxes(coronal)
#reslice2.SetResliceAxes(axial)
#reslice1a.SetResliceAxes(sagittal)
#reslice2a.SetResliceAxes(axial)
'''

										


