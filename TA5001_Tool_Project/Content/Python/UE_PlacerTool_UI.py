import unreal 
import sys
from functools import partial
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
            self.mainwindow.setFixedSize(500, 500)

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
            #self.SplineButton.clicked.connect(self.OnSelectSplineClick())

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
            self.AssetList_Widget.addItem("Add Asset File...")

            #Add File Button
            self.AddFileButton = QPushButton("+")
            self.AddFileButton.setFixedWidth(25)
            #self.AddFileButton.clicked.connect(self.OnAddFile)

            #Remove File Button
            self.RemoveFileButton = QPushButton("-")
            self.RemoveFileButton.setFixedWidth(25)
            self.RemoveFileButton.setVisible(False)
            #self.RemoveFileButton.clicked.connect(self.OnRemoveFile)

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
            Form.addRow("Quantity:", self.Quantity_spin)

            #Spacing
            self.Spacing_double = QDoubleSpinBox()
            self.Spacing_double.setFixedSize(50, 20)
            self.Spacing_double.setButtonSymbols(self.Spacing_double.ButtonSymbols.NoButtons)
            self.Spacing_double.setRange(0.00, 10000)

            #Secondary "Max" box (hidden until Range checked)
            self.Spacing_double_max = QDoubleSpinBox()
            self.Spacing_double_max.setFixedSize(50, 20)
            self.Spacing_double_max.setButtonSymbols(self.Spacing_double_max.ButtonSymbols.NoButtons)
            self.Spacing_double_max.setVisible(False)

            #Range Checkbox
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

            #Connect Range checkbox toggle
            self.Spacing_Range_Checkbox.stateChanged.connect(
                lambda checked: self.Spacing_double_max.setVisible(checked)
            )

            #Add Spacing to Parameters Format
            Form.addRow("Spacing:", Spacing_Row)

            #Scale (X, Y, Z)
            self.Scale_x = QDoubleSpinBox()
            self.Scale_x.setFixedSize(50, 20)
            self.Scale_x.setButtonSymbols(self.Scale_x.ButtonSymbols.NoButtons)

            self.Scale_y = QDoubleSpinBox()
            self.Scale_y.setFixedSize(50, 20)
            self.Scale_y.setButtonSymbols(self.Scale_y.ButtonSymbols.NoButtons)

            self.Scale_z = QDoubleSpinBox()
            self.Scale_z.setFixedSize(50, 20)
            self.Scale_z.setButtonSymbols(self.Scale_z.ButtonSymbols.NoButtons)

            Scale_Row = QWidget()
            Scale_Layout = QHBoxLayout()
            Scale_Layout.setContentsMargins(0, 0, 0, 0)

            for s in [self.Scale_x, self.Scale_y, self.Scale_z]:
                 s.setRange(0.01, 100)
                 s.setValue(1.0)
                 Scale_Layout.addWidget(s)
            
            
            Scale_Row.setLayout(Scale_Layout)
            Form.addRow("Scale (X/Y/Z):", Scale_Row)

            #Rotation (X, Y, Z)
            self.Rotation_x = QDoubleSpinBox()
            self.Rotation_x.setFixedSize(50, 20)
            self.Rotation_x.setButtonSymbols(self.Rotation_x.ButtonSymbols.NoButtons)

            self.Rotation_y = QDoubleSpinBox()
            self.Rotation_y.setFixedSize(50, 20)
            self.Rotation_y.setButtonSymbols(self.Rotation_y.ButtonSymbols.NoButtons)

            self.Rotation_z = QDoubleSpinBox()
            self.Rotation_z.setFixedSize(50, 20)
            self.Rotation_z.setButtonSymbols(self.Rotation_z.ButtonSymbols.NoButtons)

            Rotation_Row = QWidget()
            Rotation_Layout = QHBoxLayout()
            Rotation_Layout.setContentsMargins(0, 0, 0, 0)

            for r in [self.Rotation_x, self.Rotation_y, self.Rotation_z]:
                 r.setRange(-360, 360)
                 Rotation_Layout.addWidget(r)

            Rotation_Row.setLayout(Rotation_Layout)
            Form.addRow("Rotation (X/Y/Z):", Rotation_Row)

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
            #self.AssetList_Widget.currentItemChanged.connect(self.OnAssetSelected(self, self.AssetList_Widget.currentItem))

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
        unreal.log("Spline Select Button Clicked!")
        #TODO: Trigger Spline selection or display info

    def OnAssetSelected(self, current, previous):
        if current:
            asset_name = current.text()
            self.Param_header.setText(f"Selected Asset: {asset_name}")

    def UpdateRemoveButtonVisibility(self):
        self.RemoveFileButton.setVisible(self.AssetList_Widget.count() > 0)

    def OnAddFile(self, asset):
        self.AssetList_Widget.addItem(f"{asset}")
        self.UpdateRemoveButtonVisibility()

    def OnRemoveFile(self):
        current = self.AssetList_Widget.currentItem()
        if current:
            self.AssetList_Widget.takeItem(self.AssetList_Widget.row(current))
        self.UpdateRemoveButtonVisibility()


         
        
def launchWindow():
    if QApplication.instance():
        # Id any current instances of tool and destroy
        for win in (QApplication.allWindows()):
            if 'toolWindow' in win.objectName(): # update this name to match name below
                win.destroy()
    else:
        QApplication(sys.argv)

    AssetPlacerToolWindow.window = AssetPlacerToolWindow()
    AssetPlacerToolWindow.window.show()
    AssetPlacerToolWindow.window.setWindowTitle("Procedural Asset Placer Tool")
    AssetPlacerToolWindow.window.setObjectName("ToolWindow")
    unreal.parent_external_window_to_slate(AssetPlacerToolWindow.window.winId())

launchWindow()