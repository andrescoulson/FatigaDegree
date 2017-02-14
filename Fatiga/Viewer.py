#!/usr/bin/env python
 
import vtk

#reate a rendering window and renderer
ren = vtk.vtkRenderer();
renWin = vtk.vtkRenderWindow();
renWin.AddRenderer(ren);

#create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor();
iren.SetRenderWindow(renWin);

#crea mapa de color para las celdas
lut = vtk.vtkLookupTable();
lut.SetNumberOfColors(10);
lut.SetHueRange(0.667,0.0);
lut.Build();

#Lee archivo de datos con formato VTK
reader = vtk.vtkDataSetReader();
reader.SetFileName("modelo.vwr");
reader.SetScalarsName("Von_Mises");
reader.Update();

#crear mapper
mapper = vtk.vtkDataSetMapper();
mapper.SetInputConnection(reader.GetOutputPort());
reader.Update();		#necessary for GetScalarRange()
mapper.SetScalarRange(reader.GetOutput().GetScalarRange());
mapper.SetLookupTable(lut);

#crear color legend
scalarBar = vtk.vtkScalarBarActor();
scalarBar.SetLookupTable(mapper.GetLookupTable());
scalarBar.SetTitle(reader.GetScalarsName());
scalarBar.SetNumberOfLabels(11);

#configure the legend font
scalarBar.GetTitleTextProperty().SetColor(0,0,0);
scalarBar.GetLabelTextProperty().SetColor(0,0,0);
scalarBar.GetLabelTextProperty().BoldOff();

#configure position, orientation and size
scalarBar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport();
scalarBar.GetPositionCoordinate().SetValue(0.88,0.05);
scalarBar.SetOrientationToVertical();
scalarBar.SetWidth(0.08);
scalarBar.SetHeight(0.5);
#scalarBar.SetDrawFrame().Show(true)

#Generate data arrays containing point and cell ids
ids = vtk.vtkIdFilter();
ids.SetInputConnection(reader.GetOutputPort());
ids.PointIdsOn();
ids.CellIdsOn();
ids.FieldDataOn();

#Create labels for points
visPts =  vtk.vtkSelectVisiblePoints();
visPts.SetInputConnection(ids.GetOutputPort());
visPts.SetRenderer(ren);

#Create the mapper to display the point ids.  Specify the format to
#use for the labels.  Also create the associated actor.
ldm = vtk.vtkLabeledDataMapper();
#ldm.SetLabelFormat("%g");
ldm.SetInputConnection(visPts.GetOutputPort());
ldm.SetLabelModeToLabelFieldData();
ldm.GetLabelTextProperty().SetColor(0, 0, 0);
ldm.GetLabelTextProperty().BoldOff ();
ldm.GetLabelTextProperty().ShadowOff();
pointLabels = vtk.vtkActor2D();
pointLabels.SetMapper(ldm);

#Create labels for cells
cc = vtk.vtkCellCenters();
cc.SetInputConnection(ids.GetOutputPort());
visCells = vtk.vtkSelectVisiblePoints();
visCells.SetInputConnection(cc.GetOutputPort());
visCells.SetRenderer(ren);

# Create the mapper to display the cell ids.  Specify the format to
# use for the labels.  Also create the associated actor.
cellMapper = vtk.vtkLabeledDataMapper();
cellMapper.SetInputConnection(visCells.GetOutputPort());
# cellMapper.SetLabelFormat("%g")
cellMapper.SetLabelModeToLabelFieldData();
cellMapper.GetLabelTextProperty().SetColor(0, 0, 0);
cellMapper.GetLabelTextProperty().BoldOff();
cellMapper.GetLabelTextProperty().ShadowOff();
cellLabels = vtk.vtkActor2D();
cellLabels.SetMapper(cellMapper);

#ejes coordenados
axes = vtk.vtkAxesActor();
axes.AxisLabelsOn();
axes.SetShaftTypeToCylinder();
axes.SetCylinderRadius(0.04);
axes.SetConeRadius(0.46);
axes.SetTotalLength(0.25,0.25,0.25);
# place at lower left corner
AxesWidget = vtk.vtkOrientationMarkerWidget();
AxesWidget.SetViewport( 0.0, 0.0, 0.25, 0.25 );
AxesWidget.SetOrientationMarker(axes);
AxesWidget.KeyPressActivationOff();


#Create a vtkCamera, and set the camera parameters.
camera = vtk.vtkCamera();
#camera.SetClippingRange(1, -1);
#camera.SetFocalPoint(0.0,0.0,0.0);
camera.SetPosition(1.0,1.0,1.0);
camera.SetViewUp(0.0,1.0,0.0);
camera.ParallelProjectionOn();

#define actores
cells = vtk.vtkActor();
cells.SetMapper(mapper);
cells.GetProperty().EdgeVisibilityOn();
cells.GetProperty().SetEdgeColor(0,0,0);
#cells.GetProperty().SetColor(0,0,1);

#assign actor to the renderer
ren.AddActor(cells);				#celdas
ren.AddActor2D(scalarBar);			#colorbar
ren.AddActor(axes);				#ejes coordenados
#ren.AddActor2D(pointLabels); 			#numeracion de puntos
#ren.AddActor2D(cellLabels);			#numeracion de celdas
ren.SetBackground(1,1,1);			#fondo blanco
ren.SetActiveCamera(camera);
ren.ResetCamera();

#enable user interface interactor

iren.Initialize();
renWin.SetSize(1150,650);
renWin.Render();
iren.Start();
