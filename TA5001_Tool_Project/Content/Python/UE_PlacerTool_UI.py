import unreal 
import sys
from functools import partial
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QWidget, QDockWidget, QMainWindow, QPushButton, QVBoxLayout, QListWidget

class AssetPlacerToolWindow(QWidget):
    def __init__(self, parent = None):
            super(AssetPlacerToolWindow, self).__init__(parent)
            
            #Main Window
            self.mainwindow = QMainWindow()
            self.mainwindow.setParent(self)
            self.mainwindow.setLayout(QVBoxLayout())
            self.mainwindow.setFixedSize(500, 500)

            #AssetList Window
            self.asset_list_window = QDockWidget("Asset List", self)
            self.asset_list_window.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
            self.asset_list_window.setFeatures(self.asset_list_window.DockWidgetFeature.NoDockWidgetFeatures)

            self.List_Widget = QListWidget()
            self.List_Widget.addItems(["Asset A", "Asset B", "Asset C"])
            self.asset_list_window.setWidget(self.List_Widget)

            #Add File Button 

            #Parameters Window

            #Generate Button
        
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
    AssetPlacerToolWindow.window.setObjectName("oolWindow")
    unreal.parent_external_window_to_slate(AssetPlacerToolWindow.window.winId())

launchWindow()