import unreal 
import sys
import random
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
            header_layout.addWidget(AssetList_header)
            header_layout.addStretch(1)
            header_layout.addWidget(self.Random_Checkbox)
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
            self.AssetList_Widget.currentItemChanged.connect(self.OnAssetSelected)

            self.Quantity_spin.valueChanged.connect(self.OnParameterChanged)
            self.Spacing_double.valueChanged.connect(self.OnParameterChanged)
            self.Scale_x.valueChanged.connect(self.OnParameterChanged)
            self.Scale_y.valueChanged.connect(self.OnParameterChanged)
            self.Scale_z.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_x.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_y.valueChanged.connect(self.OnParameterChanged)
            self.Rotation_z.valueChanged.connect(self.OnParameterChanged)
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
                "spacing" : self.Spacing_double.value(),
                "spacing_max": self.Spacing_double_max.value(),
                "scale" : [self.Scale_x.value(), self.Scale_y.value(), self.Scale_z.value()],
                "scale_max" : [self.Scale_x_max.value(), self.Scale_y_max.value(), self.Scale_z_max.value()],
                "rotation" : [self.Rotation_x.value(), self.Rotation_y.value(), self.Rotation_z.value()],
                "rotation_max" : [self.Rotation_x_max.value(), self.Rotation_y_max.value(), self.Rotation_z_max.value()],
                "scatter" : self.Scatter_double.value()
            }
        
        #Load stored parameters into the UI
        params = self.Asset_Parameters[asset_name]

        self.Quantity_spin.setValue(params["quantity"])

        self.Quantity_spin_max.setValue(params["quantity_max"])

        self.Spacing_double.setValue(params["spacing"])

        self.Spacing_double_max.setValue(params["spacing_max"])

        self.Scale_x.setValue(params["scale"][0])
        self.Scale_y.setValue(params["scale"][1])
        self.Scale_z.setValue(params["scale"][2])

        self.Scale_x_max.setValue(params["scale_max"][0])
        self.Scale_y_max.setValue(params["scale_max"][1])
        self.Scale_z_max.setValue(params["scale_max"][2])

        self.Rotation_x.setValue(params["rotation"][0])
        self.Rotation_y.setValue(params["rotation"][1])
        self.Rotation_z.setValue(params["rotation"][2])

        self.Rotation_x_max.setValue(params["rotation_max"][0])
        self.Rotation_y_max.setValue(params["rotation_max"][1])
        self.Rotation_z_max.setValue(params["rotation_max"][2])

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
            "spacing" : self.Spacing_double.value(),
            "spacing_max" : self.Spacing_double_max.value(),
            "scale" : [self.Scale_x.value(), self.Scale_y.value(), self.Scale_z.value()],
            "scale_max" : [self.Scale_x_max.value(), self.Scale_y_max.value(), self.Scale_z_max.value()],
            "rotation" : [self.Rotation_x.value(), self.Rotation_y.value(), self.Rotation_z.value()],
            "rotation_max" : [self.Rotation_x_max.value(), self.Rotation_y_max.value(), self.Rotation_z_max.value()],
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
        # Safety checks
        if not self.AssetList_Widget.count():
            unreal.log_warning("No assets in the Asset List.")
            return

        if not self.Selected_Spline_Path:
            unreal.log_warning("No spline selected. Please select a spline first.")
            return

        editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        random_order = self.Random_Checkbox.isChecked()

        # Build asset list with remaining quantities
        assets = []
        for idx in range(self.AssetList_Widget.count()):
            asset_name = self.AssetList_Widget.item(idx).text()
            qty = self.Asset_Parameters[asset_name]["quantity"]
            if qty > 0:
                assets.append({"name": asset_name, "qty": qty})

        if not assets:
            unreal.log_warning("No assets with quantity > 0")
            return

        # Use sampled positions/rotations from spline path
        sampled_positions = self.Selected_Spline_Path["Sampled Locations"]
        sampled_rotations = self.Selected_Spline_Path["Sampled Rotations"]
        total_points = len(sampled_positions)

        # Total assets to spawn
        total_to_spawn = sum([a["qty"] for a in assets])
        current_idx = 0  # Index into sampled_positions

        for i in range(total_to_spawn):
            # Pick asset
            if random_order:
                asset = random.choice([a for a in assets if a["qty"] > 0])
            else:
                asset = next((a for a in assets if a["qty"] > 0), None)
                if not asset:
                    break

            asset_name = asset["name"]
            params = self.Asset_Parameters[asset_name]

            # Determine scale
            if self.Scale_Range_Checkbox.isChecked:
                scl_x = random.uniform(params["ScaleX"], params["ScaleX_max"])
                scl_y = random.uniform(params["ScaleY"], params["ScaleY_max"])
                scl_z = random.uniform(params["ScaleZ"], params["ScaleZ_max"])
            else:
                scl_x, scl_y, scl_z = params["ScaleX"], params["ScaleY"], params["ScaleZ"]

            # Determine rotation
            if self.Rotation_Range_Checkbox.isChecked():
                rot_x = random.uniform(params["RotationX"], params["RotationX_max"])
                rot_y = random.uniform(params["RotationY"], params["RotationY_max"])
                rot_z = random.uniform(params["RotationZ"], params["RotationZ_max"])
                rot = unreal.Rotator(rot_x, rot_y, rot_z)
            else:
                r = sampled_rotations[current_idx]
                rot = unreal.Rotator(r[0], r[1], r[2])

            # Get location from spline
            loc_tuple = sampled_positions[current_idx]
            loc = unreal.Vector(loc_tuple[0], loc_tuple[1], loc_tuple[2])

            # Build transform
            spawn_transform = unreal.Transform(
                rot,
                loc,
                unreal.Vector(scl_x, scl_y, scl_z)
            )

            # Load asset
            asset_path = self.Asset_File_Paths.get(asset_name)
            if not asset_path:
                unreal.log_warning(f"Asset path not found for: {asset_name}")
                continue
            asset_obj = unreal.load_asset(asset_path)
            if not asset_obj:
                unreal.log_warning(f"Failed to load asset: {asset_path}")
                continue

            # Spawn actor
            spawned_actor = editor_actor_subsystem.spawn_actor_from_object(asset_obj, loc)
            spawned_actor.set_actor_transform(spawn_transform, False)

            # Decrement quantity
            asset["qty"] -= 1

            # Advance along spline
            current_idx += 1
            if current_idx >= total_points:
                current_idx = total_points - 1  # Clamp to last point


    

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