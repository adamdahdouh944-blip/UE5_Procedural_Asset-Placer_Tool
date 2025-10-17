import unreal 
import sys
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
            self.mainwindow.setFixedSize(600, 500)

            # --- LEFT DOCK ---
            self.Left_Dock = QDockWidget(self)
            self.Left_Dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
            self.Left_Dock.setFeatures(self.Left_Dock.DockWidgetFeature.NoDockWidgetFeatures)

            Left_Container = QWidget()
            Left_Layout = QVBoxLayout()
            Left_Layout.setContentsMargins(0, 0, 0, 0)
            Left_Layout.setSpacing(6)

            # --- LEFT DOCK LAYOUT (SPLINE & ASSET LIST) ---
            #Spline Widget Header
            SplineWidget_header = QLabel("Current Spline:")
            SplineWidget_header.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 2px;")

            #Selected Spline Button
            self.SplineButton = QPushButton("<none>")
            self.SplineButton.setStyleSheet("text-align: left; padding: 4px;")
            self.SplineButton.clicked.connect(self.OnSelectSplineClick)

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

            # ---- BOTTOM DOCK ----
            #Generate, Apply and Cancel Button
            self.Bottom_Widget = QWidget()
            bottom_layout = QHBoxLayout()
            bottom_layout.setContentsMargins(8, 8, 8, 8)
            bottom_layout.addStretch(1)

            self.GenerateButton = QPushButton("Generate")
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
                self.SplineButton.setText(f"{actor.get_name()}")
        
        unreal.log("Spline Select Button Clicked!")

    def OnAssetSelected(self, current, previous):
        if current:
            asset_name = current.text()
            self.Param_header.setText(f"Selected Asset: {asset_name}")

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

            if asset_name in existing_assets:
                unreal.log_warning(f"Asset {asset_name} Already in Asset List")
                continue
            else:
                self.AssetList_Widget.addItem(asset_name)
                self.UpdateRemoveButtonVisibility()

    def OnRemoveFile(self):
        current = self.AssetList_Widget.currentItem()
        if current:
            self.AssetList_Widget.takeItem(self.AssetList_Widget.row(current))
        self.UpdateRemoveButtonVisibility()

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