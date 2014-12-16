Multi-Planar-Reconstruction-using-VTK
=====================================

Generate Multi Planar Reconstruction from CT scan data using VTK-PYTHON.

In medical imaging computed tomography (CT) and magnetic resonance imaging (MRI) provide three-dimensional volumetric data sets of the human body, which contain these objects of interest. The data gained from CT and MRI, however, contain many objects of less or no interest. This makes volume-rendering without preprocessing often impossible or inac-
curate. Furthermore the objects of interest are hardly located entirely within a single plane. One way to display tubular structures for diagnostic purposes is to generate longitudinal 
cross-sections in order to show lumen, wall, and surrounding tissue in a curved plane. This process is sometimes referred to as Multi Planar Reformation (MPR).

On linux machine install python-vtk and python:

$sudo apt-get install python
$sudo apt-get install libvtk5-dev python-vtk

To test if python-vtk is correctly installed, the following command should start python-
vtk interpreter.
$python-vtk

If still unable to run python-vtk interpreter, then
$sudo apt-get update
will resolve any dependencies.

After installation, move to folder containing the source code.
$python slicer.py

On any plane in the multiplanar viewer window using mouse, pick points.

To render, press ”R” or ”r”

To clear MPR, press ”C” or ”c”

Left mouse button down, and move the curser to get desired orientation.

Click on the desired plane, and use scroll to traverse up or down.
