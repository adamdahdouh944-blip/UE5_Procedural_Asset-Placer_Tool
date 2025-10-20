import unreal 
import sys
import random
import math
#from UE_PlacerTool import AssetPlacerTool
from functools import partial
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (QApplication, QWidget, QDockWidget, 
    QMainWindow, QPushButton, QVBoxLayout, QListWidget, QLabel, 
    QFormLayout, QSpinBox, QDoubleSpinBox, QHBoxLayout, QCheckBox)

class AssetPlacerToolWindow(QWidget):
    def __init__(self, parent = None):
            super(AssetPlacerToolWindow, self).__init__(parent)
            
            # --- MAIN WINDOW ---
            self.mainwindow = QMainWindow()
            self.mainwindow.setParent(self)
            self.mainwindow.setLayout(QVBoxLayout())
            self.mainwindow.setFixedSize(650, 550)

            # --- LEFT DOCK ---
            self.Left_Dock = QDockWidget(self)
            self.Left_Dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
            self.Left_Dock.setFeatures(self.Left_Dock.DockWidgetFeature.NoDockWidgetFeatures)

            Left_Container = QWidget()
            Left_Layout = QVBoxLayout()
            Left_Layout.setContentsMargins(0, 0, 0, 0)
            Left_Layout.setSpacing(6)

            # --- LEFT DOCK LAYOUT (SPLINE & ASSET LIST) ---

            # --- SPLINE ---
            #Spline Widget Header
            SplineWidget_header = QLabel("Current Spline:")
            SplineWidget_header.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 2px;")

            #Selected Spline Button
            self.SplineButton = QPushButton("<none>")
            self.SplineButton.setStyleSheet("text-align: left; padding: 4px;")
            self.SplineButton.clicked.connect(self.OnSelectSplineClick) #Gets Spline in level
            self.SplineButton.clicked.connect(self.GetSplinePath) #Gets the spline's path data

            #Selected Spline Component
            self.Selected_Spline = None

            #Selected Spline Path data 
            self.Selected_Spline_Path = {}


            # --- ASSET LIST ---
            #Left Dock Layout
            header_row = QWidget()
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(6)

            AssetList_header = QLabel("Asset List") #AssetList  Header
            AssetList_header.setStyleSheet("font-weight: bold; font-size:12pt; padding: 2px;")
            self.Random_Checkbox = QCheckBox("Random") #Random Checkbox
            self.InSequence_Checkbox = QCheckBox("Sequence") #Sequence Checkbox
            self.ConnectRandomSequenceToggle()
            header_layout.addWidget(AssetList_header)
            header_layout.addStretch(1)
            header_layout.addWidget(self.Random_Checkbox)
            header_layout.addWidget(self.InSequence_Checkbox)
            header_row.setLayout(header_layout)

            #Asset List and Add/Remove buttons Row
            Asset_row = QWidget()
            Asset_row_layout = QHBoxLayout()
            Asset_row_layout.setContentsMargins(0, 0, 0, 0)
            Asset_row_layout.setSpacing(6)

            #Asset List Widget
            self.AssetList_Widget = QListWidget()
            self.AssetList_Widget.setMinimumWidth(200)

            #Asset File Paths
            self.Asset_File_Paths = {} # {asset_name : asset_path}

            #Add File Button
            self.AddFileButton = QPushButton("+")
            self.AddFileButton.setFixedWidth(25)
            self.AddFileButton.clicked.connect(self.OnAddFile)

            #Remove File Button
            self.RemoveFileButton = QPushButton("-")
            self.RemoveFileButton.setFixedWidth(25)
            self.RemoveFileButton.setVisible(False)
            self.RemoveFileButton.clicked.connect(self.OnRemoveFile)

            #Right Side Button Column
            button_column = QVBoxLayout()
            button_column.addWidget(self.RemoveFileButton)
            button_column.addWidget(self.AddFileButton)
            button_column.addStretch(1)

            Asset_row_layout.addWidget(self.AssetList_Widget)
            Asset_row_layout.addLayout(button_column)
            Asset_row.setLayout(Asset_row_layout)

            #Add to Asset List, Spline Info and Random Checkbox to Layout
            Left_Layout.addWidget(SplineWidget_header)
            Left_Layout.addWidget(self.SplineButton)
            Left_Layout.addWidget(header_row)
            Left_Layout.addWidget(Asset_row)
            Left_Layout.addStretch(1)
            Left_Container.setLayout(Left_Layout)

            self.Left_Dock.setWidget(Left_Container)
            self.mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.Left_Dock)

            # --- PARAMETERS ---
            #Parameters Window
            self.Param_Dock = QDockWidget("Parameters", self)
            self.Param_Dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
            self.Param_Dock.setFeatures(self.Param_Dock.DockWidgetFeature.NoDockWidgetFeatures)

            self.Param_header = QLabel("Selected Asset: <none>")
            self.Param_header.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 2px;")
            self.Param_header.setFixedHeight(30)

            Param_Container = QWidget()
            Form = QFormLayout()
            qvbox = QVBoxLayout()

            # --- PARAMETER PRESETS ----

            #Store Parameters for each asset
            self.Asset_Parameters = {}

            #Quantity
            self.Quantity_spin = QSpinBox()
            self.Quantity_spin.setFixedSize(50, 20)
            self.Quantity_spin.setButtonSymbols(self.Quantity_spin.ButtonSymbols.NoButtons)
            self.Quantity_spin.setRange(0, 10000)

            #Quantity - Secondary "Max" box (hidden until range checked)
            self.Quantity_spin_max = QSpinBox()
            self.Quantity_spin_max.setFixedSize(50, 20)
            self.Quantity_spin_max.setButtonSymbols(self.Quantity_spin_max.ButtonSymbols.NoButtons)
            self.Quantity_spin_max.setVisible(False)

            #Quantity - Range CheckBox
            self.Quantity_Range_Checkbox = QCheckBox("Range")
            self.Quantity_Range_Checkbox.setFixedHeight(20)

            #Layout for Quantity Row
            Quantity_row = QWidget()
            Quantity_layout = QHBoxLayout()
            Quantity_layout.setContentsMargins(0, 0, 0, 0)
            Quantity_layout.setSpacing(6)

            Quantity_layout.addWidget(self.Quantity_spin)
            Quantity_layout.addWidget(self.Quantity_spin_max)
            Quantity_layout.addWidget(self.Quantity_Range_Checkbox)
            Quantity_layout.addStretch(1)
            Quantity_row.setLayout(Quantity_layout)

            #Connect Quantity Range checkbox toggle
            self.Quantity_Range_Checkbox.stateChanged.connect(
                lambda checked: self.Quantity_spin_max.setVisible(checked)
            )

            #Add Quantity to Parameters Format
            Form.addRow("Quantity:", Quantity_row)

            #Spacing
            self.Spacing_double = QDoubleSpinBox()
            self.Spacing_double.setFixedSize(50, 20)
            self.Spacing_double.setButtonSymbols(self.Spacing_double.ButtonSymbols.NoButtons)
            self.Spacing_double.setRange(0.00, 10000)

            #Spacing - Secondary "Max" box (hidden until Range checked)
            self.Spacing_double_max = QDoubleSpinBox()
            self.Spacing_double_max.setFixedSize(50, 20)
            self.Spacing_double_max.setButtonSymbols(self.Spacing_double_max.ButtonSymbols.NoButtons)
            self.Spacing_double_max.setVisible(False)

            #Spacing - Range Checkbox
            self.Spacing_Range_Checkbox = QCheckBox("Range")
            self.Spacing_Range_Checkbox.setFixedHeight(20)

            #Layout for Spacing row
            Spacing_Row = QWidget()
            Spacing_Layout = QHBoxLayout()
            Spacing_Layout.setContentsMargins(0, 0, 0, 0)
            Spacing_Layout.setSpacing(6)

            Spacing_Layout.addWidget(self.Spacing_double)
            Spacing_Layout.addWidget(self.Spacing_double_max)
            Spacing_Layout.addWidget(self.Spacing_Range_Checkbox)
            Spacing_Layout.addStretch(1)
            Spacing_Row.setLayout(Spacing_Layout)

            #Connect Spacing Range checkbox toggle
            self.Spacing_Range_Checkbox.stateChanged.connect(
                lambda checked: self.Spacing_double_max.setVisible(checked)
            )

            #Add Spacing to Parameters Format
            Form.addRow("Spacing:", Spacing_Row)

            #Scale (X, Y, Z)
            self.Scale_x = QDoubleSpinBox()
            self.Scale_y = QDoubleSpinBox()
            self.Scale_z = QDoubleSpinBox()
            for s in [self.Scale_x, self.Scale_y, self.Scale_z]:
                s.setFixedSize(50, 20)
                s.setButtonSymbols(s.ButtonSymbols.NoButtons)
                s.setRange(0.01, 100)
                s.setValue(1.0)

            #Scale Max (hidden until Range checked)
            self.Scale_x_max = QDoubleSpinBox()
            self.Scale_y_max = QDoubleSpinBox()
            self.Scale_z_max = QDoubleSpinBox()
            for s in [self.Scale_x_max, self.Scale_y_max, self.Scale_z_max]:
                s.setFixedSize(50, 20)
                s.setButtonSymbols(s.ButtonSymbols.NoButtons)
                s.setRange(0.01, 100)
                s.setValue(1.0)

            #Scale Range Checkbox
            self.Scale_Range_Checkbox = QCheckBox("Range")
            self.Scale_Range_Checkbox.setFixedHeight(20)

            #Scale Row (Always Visible)
            Scale_Row = QWidget()
            Scale_Layout = QHBoxLayout()
            Scale_Layout.setContentsMargins(0, 0, 0, 0)
            Scale_Layout.setSpacing(4)
            for s in [self.Scale_x, self.Scale_y, self.Scale_z, self.Scale_Range_Checkbox]:
                 Scale_Layout.addWidget(s)
            Scale_Row.setLayout(Scale_Layout)

            #Scale Max Row (Hidden Until Range Checked)
            Scale_max_row = QWidget()
            Scale_max_layout = QHBoxLayout()
            Scale_max_layout.setContentsMargins(0, 0, 61, 0)
            Scale_max_layout.setSpacing(4)
            for s in [self.Scale_x_max, self.Scale_y_max, self.Scale_z_max]:
                Scale_max_layout.addWidget(s)
            Scale_max_row.setLayout(Scale_max_layout)
            Scale_max_row.setVisible(False)

            #Connect Scale Range Checkbox Toggle
            self.Scale_Range_Checkbox.stateChanged.connect(
                lambda checked: Scale_max_row.setVisible(checked)
            )

            #Add both Scale rows to the form
            Form.addRow("Scale (X/Y/Z):", Scale_Row)
            Form.addRow("", Scale_max_row)

            #Rotation (X, Y, Z)
            self.Rotation_x = QDoubleSpinBox()
            self.Rotation_y = QDoubleSpinBox()
            self.Rotation_z = QDoubleSpinBox()
            for r in [self.Rotation_x, self.Rotation_y, self.Rotation_z]:
                r.setFixedSize(50, 20)
                r.setButtonSymbols(r.ButtonSymbols.NoButtons)
                r.setRange(-360, 360)
                r.setValue(0)
            
            #Rotation Max (hidden until Range Checked)
            self.Rotation_x_max = QDoubleSpinBox()
            self.Rotation_y_max = QDoubleSpinBox()
            self.Rotation_z_max = QDoubleSpinBox()
            for r in [self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max]:
                r.setFixedSize(50, 20)
                r.setButtonSymbols(r.ButtonSymbols.NoButtons)
                r.setRange(-360, 360)
                r.setValue(0)

            #Range Checkbox
            self.Rotation_Range_Checkbox = QCheckBox("Range")
            self.Rotation_Range_Checkbox.setFixedHeight(20)

            #Rotation Row (Always Visible)
            Rotation_Row = QWidget()
            Rotation_Layout = QHBoxLayout()
            Rotation_Layout.setContentsMargins(0, 0, 0, 0)
            Rotation_Layout.setSpacing(4)
            for r in [self.Rotation_x, self.Rotation_y, self.Rotation_z, self.Rotation_Range_Checkbox]:
                 Rotation_Layout.addWidget(r)
            Rotation_Row.setLayout(Rotation_Layout)

            #Rotation Max Row (Hidden Until Range Checked)
            Rotation_max_row = QWidget()
            Rotation_max_layout = QHBoxLayout()
            Rotation_max_layout.setContentsMargins(0, 0, 61, 0)
            Rotation_max_layout.setSpacing(4)
            for r in [self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max]:
                Rotation_max_layout.addWidget(r)
            Rotation_max_row.setLayout(Rotation_max_layout)
            Rotation_max_row.setVisible(False)

            #Connect Rotation Range Checkbox Toggle
            self.Rotation_Range_Checkbox.stateChanged.connect(
                lambda checked: Rotation_max_row.setVisible(checked)
            )

            #Add Both Rotation Rows to the Form
            Form.addRow("Rotation (X/Y/Z):", Rotation_Row)
            Form.addRow("", Rotation_max_row)

            #Scatter
            self.Scatter_double = QDoubleSpinBox()
            self.Scatter_double.setFixedSize(50, 20)
            self.Scatter_double.setButtonSymbols(self.Scatter_double.ButtonSymbols.NoButtons)
            Form.addRow("Scatter:", self.Scatter_double)

            #Dock Parameter 
            qvbox.addWidget(self.Param_header)
            qvbox.addLayout(Form)
            Param_Container.setLayout(qvbox)
            self.Param_Dock.setWidget(Param_Container)
            self.mainwindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.Param_Dock)

            #Connect Signals: When an Asset is Clicked in Asset List, Update Parameter List
            #Store and save parameters for each asset
            #Switch from Random to InSequence
            self.AssetList_Widget.currentItemChanged.connect(self.OnAssetSelected)

            self.Quantity_spin.valueChanged.connect(self.OnParameterChanged)
            self.Quantity_spin_max.valueChanged.connect(self.OnParameterChanged)
            self.Quantity_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)

            self.Spacing_double.valueChanged.connect(self.OnParameterChanged)
            self.Spacing_double_max.valueChanged.connect(self.OnParameterChanged)
            self.Spacing_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)

            self.Scale_x.valueChanged.connect(self.OnParameterChanged)
            self.Scale_y.valueChanged.connect(self.OnParameterChanged)
            self.Scale_z.valueChanged.connect(self.OnParameterChanged)
            self.Scale_x_max.valueChanged.connect(self.OnParameterChanged)
            self.Scale_y_max.valueChanged.connect(self.OnParameterChanged)
            self.Scale_z_max.valueChanged.connect(self.OnParameterChanged)
            self.Scale_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)

            self.Rotation_x.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_y.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_z.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_x_max.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_y_max.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_z_max.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)

            self.Scatter_double.valueChanged.connect(self.OnParameterChanged)

            # ---- BOTTOM DOCK ----
            #Generate, Apply and Cancel Button
            self.Bottom_Widget = QWidget()
            bottom_layout = QHBoxLayout()
            bottom_layout.setContentsMargins(8, 8, 8, 8)
            bottom_layout.addStretch(1)

            self.GenerateButton = QPushButton("Generate")
            self.GenerateButton.clicked.connect(self.Generate)
            self.ApplyButton = QPushButton("Apply")
            self.CancelButton = QPushButton("Cancel")

            for button in [self.GenerateButton, self.ApplyButton, self.CancelButton]:
                button.setFixedWidth(100)
                bottom_layout.addWidget(button)

            bottom_layout.addStretch(1)
            self.Bottom_Widget.setLayout(bottom_layout)

            bottom_dock = QDockWidget("", self)
            bottom_dock.setTitleBarWidget(QWidget())
            bottom_dock.setWidget(self.Bottom_Widget)
            bottom_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
            self.mainwindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

    def OnSelectSplineClick(self):
        # Get the editor actor subsystem
        editorActorSubsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actors = editorActorSubsystem.get_selected_level_actors()

        #If no Actor is selected
        if not actors:
            unreal.log_warning("no actors selected in the editor.")
            return
        
        # Loop Through selected actors
        for actor in actors:
            # Check if Actor has SplineComponent
            spline_components = actor.get_components_by_class(unreal.SplineComponent)
            if spline_components:
                self.Selected_Spline = actor
                self.SplineButton.setText(f"{actor.get_name()}")
        
        unreal.log("Spline Select Button Clicked!")

    def GetSplinePath(self):
        #Ensure we have a spline actor selected
        if not self.Selected_Spline:
            unreal.log_warning("No spline actor selected")
            return
        
        #Get spline component (Draw Spline Tool actors use SplineComponent)
        spline_components = self.Selected_Spline.get_components_by_class(unreal.SplineComponent)
        if not spline_components:
            unreal.log_warning("Selected Actor has no SplineComponent")
            return
        
        spline = spline_components[0] #Use the first spline component found

        num_points = spline.get_number_of_spline_points()
        num_segments = num_points - 1
        total_length = spline.get_spline_length()

        spline_data = {
            "Actor Name": self.Selected_Spline.get_name(),
            "Number of Points": num_points,
            "Number of Segments": num_segments,
            "Total Spline Length":total_length,
            "Point Data": [] # Will hold dictionaries per spline point
        }

        for i in range(num_points):
            #World-space location of this spline point
            location = spline.get_location_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
            rotation = spline.get_rotation_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
            tangent = spline.get_tangent_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)

            #Distance along spline to this point
            distance = spline.get_distance_along_spline_at_spline_point(i)

            #Direction (normalised forward vector)
            direction = spline.get_direction_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)

            #Store in structured format
            spline_data["Point Data"].append({
                "index": i,
                "Distance Along Spline": distance,
                "World Location": (location.x, location.y, location.z),
                "Rotation": (rotation.roll, rotation.pitch, rotation.yaw),
                "Tangent": (tangent.x, tangent.y, tangent.z),
                "Direction": (direction.x, direction.y, direction.z)
            })

        #Procedural Spacing calculations (e.g., every X units)
        step = total_length / max(num_segments * 10, 1) #adjustable density
        sampled_positions = []
        sampled_rotations = []

        d = 0.0
        while d <= total_length:
            pos = spline.get_location_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
            rot = spline.get_rotation_at_distance_along_spline(d, unreal.SplineCoordinateSpace.WORLD)
            sampled_positions.append((pos.x, pos.y, pos.z))
            sampled_rotations.append((rot.roll, rot.pitch, rot.yaw))
            d += step

        spline_data["Sampled Locations"] = sampled_positions
        spline_data["Sampled Rotations"] = sampled_rotations

        #Store it 
        self.Selected_Spline_Path = spline_data
        
        unreal.log(f"Spline Data Cached for {spline_data['Actor Name']}: {num_points} points, {num_segments} segments, length {total_length:.2f}")

        return spline_data

    def ConnectRandomSequenceToggle(self):
        '''Ensures Random and InSequence checkboxes are mutually exclusive.'''

        def onRandomToggled(checked):
                if checked and self.InSequence_Checkbox.isChecked():
                    self.InSequence_Checkbox.setChecked(False)
                    unreal.log("Disabled InSequence since Random was enabled")

        def onInSequenceToggled(checked):
                if checked and self.Random_Checkbox.isChecked():
                    self.Random_Checkbox.setChecked(False)
                    unreal.log("Disabled Random since InSequence was enabled")

        # Connect Checkbox Change Events
        self.Random_Checkbox.checkStateChanged.connect(onRandomToggled)
        self.InSequence_Checkbox.checkStateChanged.connect(onInSequenceToggled)

    def OnAssetSelected(self, current, previous):
        if not current:
            return

        asset_name = current.text()
        self.Param_header.setText(f"Selected Asset: {asset_name}")

        #Initialise Asset Parameters if new
        if asset_name not in self.Asset_Parameters:
            self.Asset_Parameters[asset_name] = {
                "quantity" : self.Quantity_spin.value(),
                "quantity_max" : self.Quantity_spin_max.value(),
                "quantity_range" :self.Quantity_Range_Checkbox.isChecked(),
                "spacing" : self.Spacing_double.value(),
                "spacing_max": self.Spacing_double_max.value(),
                "spacing_range" : self.Scale_Range_Checkbox.isChecked(),
                "scale" : [self.Scale_x.value(), self.Scale_y.value(), self.Scale_z.value()],
                "scale_max" : [self.Scale_x_max.value(), self.Scale_y_max.value(), self.Scale_z_max.value()],
                "scale_range" : self.Scale_Range_Checkbox.isChecked(),
                "rotation" : [self.Rotation_x.value(), self.Rotation_y.value(), self.Rotation_z.value()],
                "rotation_max" : [self.Rotation_x_max.value(), self.Rotation_y_max.value(), self.Rotation_z_max.value()],
                "rotation_range" : self.Rotation_Range_Checkbox.isChecked(),
                "scatter" : self.Scatter_double.value()
            }
        
        #Load stored parameters into the UI
        params = self.Asset_Parameters[asset_name]

        self.Quantity_spin.setValue(params["quantity"])
        self.Quantity_spin_max.setValue(params["quantity_max"])
        self.Quantity_Range_Checkbox.setChecked(params["quantity_range"])

        self.Spacing_double.setValue(params["spacing"])
        self.Spacing_double_max.setValue(params["spacing_max"])
        self.Spacing_Range_Checkbox.setChecked(params["spacing_range"])

        self.Scale_x.setValue(params["scale"][0])
        self.Scale_y.setValue(params["scale"][1])
        self.Scale_z.setValue(params["scale"][2])

        self.Scale_x_max.setValue(params["scale_max"][0])
        self.Scale_y_max.setValue(params["scale_max"][1])
        self.Scale_z_max.setValue(params["scale_max"][2])

        self.Scale_Range_Checkbox.setChecked(params["scale_range"])

        self.Rotation_x.setValue(params["rotation"][0])
        self.Rotation_y.setValue(params["rotation"][1])
        self.Rotation_z.setValue(params["rotation"][2])

        self.Rotation_x_max.setValue(params["rotation_max"][0])
        self.Rotation_y_max.setValue(params["rotation_max"][1])
        self.Rotation_z_max.setValue(params["rotation_max"][2])

        self.Rotation_Range_Checkbox.setChecked(params["rotation_range"])

        self.Scatter_double.setValue(params["scatter"])

    def OnParameterChanged(self):
        current_item = self.AssetList_Widget.currentItem()
        if not current_item:
            return
        
        asset_name = current_item.text()
        if asset_name not in self.Asset_Parameters:
            return
        
        self.Asset_Parameters[asset_name] = {
            "quantity" : self.Quantity_spin.value(),
            "quantity_max" : self.Quantity_spin_max.value(),
            "quantity_range" : self.Quantity_Range_Checkbox.isChecked(),
            "spacing" : self.Spacing_double.value(),
            "spacing_max" : self.Spacing_double_max.value(),
            "spacing_range" : self.Spacing_Range_Checkbox.isChecked(),
            "scale" : [self.Scale_x.value(), self.Scale_y.value(), self.Scale_z.value()],
            "scale_max" : [self.Scale_x_max.value(), self.Scale_y_max.value(), self.Scale_z_max.value()],
            "scale_range" : self.Scale_Range_Checkbox.isChecked(),
            "rotation" : [self.Rotation_x.value(), self.Rotation_y.value(), self.Rotation_z.value()],
            "rotation_max" : [self.Rotation_x_max.value(), self.Rotation_y_max.value(), self.Rotation_z_max.value()],
            "rotation_range" : self.Rotation_Range_Checkbox.isChecked(),
            "scatter" : self.Scatter_double.value()
        }

    def UpdateRemoveButtonVisibility(self):
        self.RemoveFileButton.setVisible(self.AssetList_Widget.count() > 0)

    def OnAddFile(self, selected_assets):
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()

        if not selected_assets:
            unreal.log_warning("No Asset Selected")
            return
        
        existing_assets = [self.AssetList_Widget.item(i).text() for i in range(self.AssetList_Widget.count())]

        for asset in selected_assets:
            asset_name = asset.get_name()
            asset_path = asset.get_path_name()

            if asset_name in existing_assets:
                unreal.log_warning(f"Asset {asset_name} Already in Asset List")
                continue
            else:
                #Add to List Widget
                self.AssetList_Widget.addItem(asset_name)
                #Store Path in Dictionary
                self.Asset_File_Paths[asset_name] = asset_path
                self.UpdateRemoveButtonVisibility()
        #TODO: When new Asset is added, parameters default 0 (except scale defaults to 1)

    def OnRemoveFile(self):
        current = self.AssetList_Widget.currentItem()
        if current:
            self.AssetList_Widget.takeItem(self.AssetList_Widget.row(current))
        self.UpdateRemoveButtonVisibility()

    def Generate(self):
        """
        Generate assets along the spline using stored data dictionaries:
        - self.Asset_Parameters
        - self.Asset_File_Paths
        - self.Selected_Spline_Path
        Adds overlap avoidance by trial-spawning and destroying colliding actors, then moving forward.
        """

        # -------------------------
        # Section 1: Validation / Safety
        # -------------------------
        if not hasattr(self, "Asset_Parameters") or not self.Asset_Parameters:
            unreal.log_warning("[Generate] No Asset_Parameters found.")
            return

        if not hasattr(self, "Asset_File_Paths") or not self.Asset_File_Paths:
            unreal.log_warning("[Generate] No Asset_File_Paths found.")
            return

        if not hasattr(self, "Selected_Spline_Path") or not self.Selected_Spline_Path:
            unreal.log_warning("[Generate] No Selected_Spline_Path found.")
            return

        if not hasattr(self, "AssetList_Widget") or self.AssetList_Widget.count() == 0:
            unreal.log_warning("[Generate] Asset list is empty.")
            return

        # Editor actor subsystem for spawning/destroying
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

        # -------------------------
        # Section 2: Build asset working list
        # -------------------------
        # Preserve order from the AssetList_Widget
        asset_order = [self.AssetList_Widget.item(i).text() for i in range(self.AssetList_Widget.count())]

        assets = []
        for name in asset_order:
            params = self.Asset_Parameters.get(name)
            if not params:
                unreal.log_warning(f"[Generate] Missing parameters for '{name}', skipping.")
                continue

            qty = int(params.get("quantity", 0))

            if hasattr(self, "Quantity_Range_Checkbox") and self.Quantity_Range_Checkbox.isChecked():
                qty_min = int(params.get("quantity", 0))
                qty_max = int(params.get("quantity_max", qty_min))
                if qty_max > qty_min:
                    qty = random.randint(qty_min, qty_max)

            if qty <= 0:
                continue

            assets.append({"name": name, "qty": qty, "params": params})

        if not assets:
            unreal.log_warning("[Generate] No spawnable assets (quantity <= 0).")
            return

        # Random or sequential mode
        random_mode = getattr(self, "Random_Checkbox", None) and self.Random_Checkbox.isChecked()

        #TODO In-Sequence Spawning ---
        '''in_sequence = getattr(self, "InSequence_Checkbox", None) and self.InSequence_Checkbox.isChecked()
        if in_sequence:
            # Create a sequence like Asset1, Asset2, Asset1, Asset2, etc.
            max_quantity = max(self.Asset_Parameters[a]["quantity"] for a in spawn_sequence)
            new_sequence = []
            for i in range(max_quantity):
                for asset in spawn_sequence:
                    if self.Asset_Parameters[asset]["quantity"] > i:
                        new_sequence.append(asset)
            spawn_sequence = new_sequence
            unreal.log("InSequence mode active — alternating assets in sequence along spline.")
        else:
            unreal.log("Standard mode — spawning one asset type at a time.")'''

        # -------------------------
        # Section 3: Spline data helpers (use your Selected_Spline_Path structure)
        # -------------------------
        spline = self.Selected_Spline_Path
        point_data = spline.get("Point Data", [])
        if not point_data:
            unreal.log_warning("[Generate] Selected_Spline_Path contains no 'Point Data'.")
            return

        # Distances and positions arrays for interpolation
        distances = [float(p["Distance Along Spline"]) for p in point_data]
        positions = [p["World Location"] for p in point_data]     # tuples (x,y,z)
        directions = [p["Direction"] for p in point_data]         # tuples (x,y,z)

        total_length = float(spline.get("Total Spline Length", distances[-1] if distances else 0.0))

        # Linear interpolation helper
        def lerp(a, b, t):
            return a + (b - a) * t

        def lerp_tuple(a, b, t):
            return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))

        # Sample position and direction at arbitrary distance along spline using linear interpolation between point_data
        def sample_at_distance(distance):
            # clamp
            if distance <= distances[0]:
                return positions[0], directions[0]
            if distance >= distances[-1]:
                return positions[-1], directions[-1]

            # find segment
            idx = 0
            while idx < len(distances) - 1 and not (distances[idx] <= distance <= distances[idx + 1]):
                idx += 1

            d0, d1 = distances[idx], distances[idx + 1]
            seg_len = d1 - d0 if (d1 - d0) != 0 else 1e-6
            t = (distance - d0) / seg_len
            pos = lerp_tuple(positions[idx], positions[idx + 1], t)
            dirv = lerp_tuple(directions[idx], directions[idx + 1], t)
            # normalize direction
            mag = math.sqrt(dirv[0]**2 + dirv[1]**2 + dirv[2]**2)
            if mag > 1e-6:
                dirv = (dirv[0]/mag, dirv[1]/mag, dirv[2]/mag)
            return pos, dirv

        # Helper: convert tuple to unreal.Vector
        def to_vector(t):
            return unreal.Vector(float(t[0]), float(t[1]), float(t[2]))

        # Helper: rotator from direction vector (forward)
        def rotator_from_direction(dir_vec):
            x, y, z = dir_vec
            mag_xy = math.hypot(x, y)
            if mag_xy < 1e-6:
                yaw = 0.0
                pitch = 90.0 if z > 0 else -90.0
            else:
                yaw = math.degrees(math.atan2(y, x))
                pitch = math.degrees(math.atan2(z, mag_xy))
            return unreal.Rotator(pitch, yaw, 0.0)  # roll = 0

        # -------------------------
        # Section 4: Spawn loop with overlap avoidance
        # -------------------------
        total_to_spawn = sum(a["qty"] for a in assets)
        total_remaining = total_to_spawn
        if total_remaining <= 0:
            unreal.log_warning("[Generate] Total quantity is 0. Nothing to do.")
            return

        # Keep track of spawned actors to check overlap against
        spawned_actors = []

        #unreal.set_actor_transform() argument 'teleport' is false
        teleport = False

        # Starting distance: spawn first at start of spline (0.0)
        current_distance = 0.0

        # Safety counters
        spawn_attempts = 0
        MAX_ATTEMPTS = total_remaining * 20 + 1000

        # Main generation loop: continue until no remaining or run out of spline
        while total_remaining > 0 and spawn_attempts < MAX_ATTEMPTS:
            spawn_attempts += 1

            # Choose an asset (random or sequential)
            if random_mode:
                choices = [a for a in assets if a["qty"] > 0]
                if not choices:
                    break
                chosen = random.choice(choices)
            else:
                chosen = next((a for a in assets if a["qty"] > 0), None)
                if not chosen:
                    break

            name = chosen["name"]
            params = chosen["params"]

            # --- Sample parameters (default = min, optional _max = max) ---
            # Spacing
            spacing = float(params.get("spacing", 0.0))
            if self.Spacing_Range_Checkbox.isChecked():
                if params.get("spacing_max") is not None and params.get("spacing_max") > spacing:
                    spacing = random.uniform(spacing, float(params["spacing_max"]))

            # Scale (per-axis)
            default_scale = params.get("scale", [1.0, 1.0, 1.0])
            scale_max = params.get("scale_max")
            if self.Scale_Range_Checkbox.isChecked():
                if scale_max:
                    sx = random.uniform(float(default_scale[0]), float(scale_max[0]))
                    sy = random.uniform(float(default_scale[1]), float(scale_max[1]))
                    sz = random.uniform(float(default_scale[2]), float(scale_max[2]))
            else:
                sx, sy, sz = float(default_scale[0]), float(default_scale[1]), float(default_scale[2])

            # Rotation (per-axis Euler). If rotation_max present, random between default and max; otherwise will use spline rot
            rot_default = params.get("rotation", None)
            rot_max = params.get("rotation_max", None)
            use_user_rotation = bool(rot_default is not None)
            if self.Rotation_Range_Checkbox.isChecked():
                if rot_max:
                    rx = random.uniform(float(rot_default[0]), float(rot_max[0]))
                    ry = random.uniform(float(rot_default[1]), float(rot_max[1]))
                    rz = random.uniform(float(rot_default[2]), float(rot_max[2]))
                    user_rotator = unreal.Rotator(rx, ry, rz)
                    use_user_rotation = True
            elif rot_default:
                user_rotator = unreal.Rotator(float(rot_default[0]), float(rot_default[1]), float(rot_default[2]))
                use_user_rotation = True
            else:
                user_rotator = None
                use_user_rotation = False

            # Scatter (single float)
            scatter = float(params.get("scatter", 0.0))

            # --- Determine candidate spawn location & rotation by sampling spline at current_distance ---
            pos_tuple, dir_vec = sample_at_distance(current_distance)
            candidate_loc = to_vector(pos_tuple)
            # base rotation: from user rot if provided, otherwise from spline direction
            if use_user_rotation:
                base_rot = user_rotator
            else:
                base_rot = rotator_from_direction(dir_vec)

            # Build spawn transform
            spawn_transform = unreal.Transform(candidate_loc, base_rot, unreal.Vector(sx, sy, sz))

            # --- Overlap avoidance: try spawn, check overlap, if overlap destroy and step forward ---
            # We'll attempt a limited number of trial spawns for this chosen asset.
            trial_attempts = 0
            MAX_TRIALS = 25
            spawned_success = False

            # Obtain asset UObject path and asset_obj
            asset_path = self.Asset_File_Paths.get(name)
            if not asset_path:
                unreal.log_warning(f"[Generate] Missing path for asset '{name}'. Skipping this asset.")
                # Do not decrement qty to allow the user to correct path and regenerate
                # If nothing is spawnable, outer loop will abort later
                continue

            asset_obj = unreal.load_asset(asset_path)
            if not asset_obj:
                unreal.log_warning(f"[Generate] Failed to load asset at '{asset_path}'. Skipping.")
                continue

            while trial_attempts < MAX_TRIALS:
                trial_attempts += 1

                # Apply scatter as a random offset around the candidate location (local right & up)
                scattered_loc = unreal.Vector(candidate_loc.x, candidate_loc.y, candidate_loc.z)
                if scatter != 0.0:
                    # compute local right from dir_vec
                    right = (-dir_vec[1], dir_vec[0], 0.0)
                    rmag = math.sqrt(right[0]**2 + right[1]**2 + right[2]**2)
                    if rmag > 1e-6:
                        right = (right[0]/rmag, right[1]/rmag, right[2]/rmag)
                    else:
                        right = (1.0, 0.0, 0.0)
                    up = (0.0, 0.0, 1.0)
                    off_r = random.uniform(-scatter, scatter)
                    off_u = random.uniform(-scatter, scatter)
                    scattered_loc.x += right[0] * off_r + up[0] * off_u
                    scattered_loc.y += right[1] * off_r + up[1] * off_u
                    scattered_loc.z += right[2] * off_r + up[2] * off_u

                # Spawn a trial actor at scattered_loc (we'll destroy it if overlapping)
                try:
                    trial_actor = actor_subsystem.spawn_actor_from_object(asset_obj, scattered_loc)
                except Exception as e:
                    unreal.log_warning(f"[Generate] spawn_actor_from_object failed for '{name}': {e}")
                    break

                # Immediately set full transform (with scale & rotation)
                try:
                    trial_transform = unreal.Transform(scattered_loc, base_rot, unreal.Vector(sx, sy, sz))
                    # Use the two-arg form (transform, sweep) because some builds require only two args
                    trial_actor.set_actor_transform(trial_transform, False, teleport)
                except Exception:
                    # Fallback: set location/rotation/scale separately (safer)
                    try:
                        trial_actor.set_actor_location_and_rotation(scattered_loc, base_rot, False, unreal.TeleportType.NONE)
                        trial_actor.set_actor_scale3d(unreal.Vector(sx, sy, sz))
                    except Exception:
                        # if setting transform fails, destroy trial and abort this trial
                        try:
                            actor_subsystem.destroy_actor(trial_actor)
                        except Exception:
                            pass
                        break

                # Compute bounding box center and radius for this trial actor
                try:
                    bbox = trial_actor.get_components_bounding_box(True)  # True = only colliding components?
                    center = bbox.get_center()
                    extent = bbox.get_extent()  # box half-size (Vector)
                    trial_radius = max(extent.x, extent.y, extent.z)
                except Exception:
                    # if bounding box retrieval fails, use a small conservative radius
                    center = trial_actor.get_actor_location()
                    trial_radius = 50.0

                # Check overlap against already spawned actors' bounding boxes
                overlap = False
                for other in spawned_actors:
                    if not other or not hasattr(other, "get_actor_location"):
                        continue
                    try:
                        obox = other.get_components_bounding_box(True)
                        ocenter = obox.get_center()
                        oextent = obox.get_extent()
                        other_radius = max(oextent.x, oextent.y, oextent.z)
                    except Exception:
                        ocenter = other.get_actor_location()
                        other_radius = 50.0

                    # distance between centers
                    dvec = center - ocenter
                    dist = math.sqrt(dvec.x**2 + dvec.y**2 + dvec.z**2)
                    # if distance less than sum of radii plus a small buffer, it's overlapping
                    buffer = 2.0  # small slack
                    if dist < (trial_radius + other_radius + buffer):
                        overlap = True
                        break

                if not overlap:
                    # Found a safe placement
                    spawned_actors.append(trial_actor)
                    spawned_success = True
                    break
                else:
                    # Overlap found: destroy trial actor and step forward along spline by a small step and retry
                    try:
                        actor_subsystem.destroy_actor(trial_actor)
                    except Exception:
                        pass
                    # increment current_distance by a small step (half-spacing or a small amount)
                    # prefer at least a small move so we can escape local congestion
                    step_forward = max(spacing * 0.5, 10.0)
                    current_distance += step_forward
                    # if moved beyond spline end, abort trials
                    if current_distance > total_length:
                        break
                    # update candidate position and dir for next trial
                    pos_tuple, dir_vec = sample_at_distance(current_distance)
                    candidate_loc = unreal.Vector(pos_tuple[0], pos_tuple[1], pos_tuple[2])
                    # update base rotation if using spline direction
                    if not use_user_rotation:
                        base_rot = rotator_from_direction(dir_vec)
                    # continue while trial_attempts loop

            # End trial attempts

            if not spawned_success:
                unreal.log_warning(f"[Generate] Could not find non-overlapping spot for '{name}' after {trial_attempts} trials. Skipping this spawn.")
                # We choose to decrement qty so we don't loop forever on impossible placements; adjust if you prefer
                chosen["qty"] -= 1
                total_remaining -= 1
                # Move forward by spacing anyway to progress along spline
                current_distance += spacing
                if current_distance > total_length:
                    unreal.log("[Generate] Reached end of spline during overlap resolution.")
                    break
                continue

            # If spawned_success is True, we have appended the trial actor to spawned_actors already
            # Decrement counts
            chosen["qty"] -= 1
            total_remaining -= 1

            # Advance current_distance by spacing for the next spawn center
            current_distance += spacing
            if current_distance > total_length:
                unreal.log("[Generate] Reached end of spline - stopping generation.")
                break

        # End main spawn while loop
        unreal.log(f"[Generate] Completed generation. Remaining total: {total_remaining}")



    

def apply_unreal_palette(app):
    palette = QPalette()

    # Base background colors
    palette.setColor(QPalette.ColorRole.Window, QColor(36, 36, 36))
    palette.setColor(QPalette.ColorRole.Base, QColor(24, 24, 24))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(42, 42, 42))

    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(230, 230, 230))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(128, 128, 128))

    # Buttons & highlights
    palette.setColor(QPalette.ColorRole.Button, QColor(48, 48, 48))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))  # UE Blue
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    # Borders & disabled states
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(90, 90, 90))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(90, 90, 90))

    app.setPalette(palette)
     
def apply_unreal_stylesheet(app):
    qss = """
    QWidget {
        background-color: #242424;
        color: #E0E0E0;
        font-family: 'Segoe UI';
        font-size: 10pt;
    }
    QPushButton {
        background-color: #2A2A2A;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 4px 10px;
    }
    QPushButton:hover {
        background-color: #0078D7;
        color: white;
    }
    QLineEdit, QSpinBox, QDoubleSpinBox, QListWidget {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 4px;
        padding: 2px;
    }
    """
    app.setStyleSheet(qss)

def launchWindow():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    else:
        # Id any current instances of tool and destroy
        for win in (QApplication.allWindows()):
            if 'toolWindow' in win.objectName(): # update this name to match name below
                win.destroy()
    
    apply_unreal_palette(app)
    apply_unreal_stylesheet(app)
 
    AssetPlacerToolWindow.window = AssetPlacerToolWindow()
    AssetPlacerToolWindow.window.show()
    AssetPlacerToolWindow.window.setWindowTitle("Procedural Asset Placer Tool")
    AssetPlacerToolWindow.window.setObjectName("ToolWindow")
    unreal.parent_external_window_to_slate(AssetPlacerToolWindow.window.winId())

launchWindow()