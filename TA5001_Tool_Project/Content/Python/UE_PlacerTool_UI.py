# ============================
# Unreal Engine Python Imports
# ============================
import unreal

# ============================
# Standard Library Imports
# ============================
import sys
import copy
import random
import math

# ============================
# PySide6 (Qt for Unreal UI)
# ============================
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QDockWidget, 
    QMainWindow, QPushButton, QVBoxLayout, QListWidget, QLabel, 
    QFormLayout, QSpinBox, QDoubleSpinBox, QHBoxLayout, QCheckBox
    )

# ============================
# Python Tool Class
# ============================
class AssetPlacerToolWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ---- Data/state ----
        self._init_generation_data()
        self._init_asset_data()

        # ---- UI ----
        self._init_main_window()
        self._init_left_dock()      # Spline + Asset List + Generation Log
        self._init_param_dock()     # Parameters panel
        self._init_bottom_dock()    # Generate / Apply buttons

        # ---- Signals & defaults ----
        self._connect_signals()
        self._init_default_states()

    #------------------------------
    # Math / Vector Utility Functions
    #------------------------------
    def lerp(self, a: float, b: float, t: float) -> float:
        """
        Linearly interpolates between two scalar values.

        Args:
            a (float): Starting value.
            b (float): Target value.
            t (float): Interpolation factor between 0.0 and 1.0.

        Returns:
            float: The interpolated result between a and b.
        """
        return a + (b - a) * t
    
    def lerp_tuple(self, a: tuple, b: tuple, t: float) -> tuple:
        """
        Linearly interpolates between two 3D tuples.

        Args:
            a (tuple): Starting (x, y, z) values.
            b (tuple): Target (x, y, z) values.
            t (float): Interpolation factor between 0.0 and 1.0.

        Returns:
            tuple: Interpolated (x, y, z) values.
        """
        return (self.lerp(a[0], b[0], t),
                self.lerp(a[1], b[1], t),
                self.lerp(a[2], b[2], t))

    def sample_at_distance(self, distance: float, distances: list, positions: list, directions: list) -> tuple:
        """
        Samples a position and direction along the spline at a given distance.

        Performs linear interpolation between spline points to calculate the
        world-space location and normalized direction at the specified distance.

        Args:
            distance (float): The target distance along the spline.
            distances (list[float]): Cumulative distances of spline points.
            positions (list[tuple]): World positions of spline points.
            directions (list[tuple]): Tangent directions of spline segments.

        Returns:
            tuple: (position, direction) — both as 3D tuples.
        """
        if distance <= distances[0]:
            return positions[0], directions[0]
        if distance >= distances[-1]:
            return positions[-1], directions[-1]

        idx = 0
        while idx < len(distances) - 1 and not (distances[idx] <= distance <= distances[idx + 1]):
            idx += 1

        d0, d1 = distances[idx], distances[idx + 1]
        seg_len = d1 - d0 if (d1 - d0) != 0 else 1e-6
        t = (distance - d0) / seg_len

        pos = self.lerp_tuple(positions[idx], positions[idx + 1], t)
        dirv = self.lerp_tuple(directions[idx], directions[idx + 1], t)

        mag = math.sqrt(dirv[0]**2 + dirv[1]**2 + dirv[2]**2)
        if mag > 1e-6:
            dirv = (dirv[0]/mag, dirv[1]/mag, dirv[2]/mag)

        return pos, dirv

    def rotator_from_direction(self, dir_vec: tuple) -> unreal.Rotator:
        """
        Converts a 3D direction vector into an Unreal Rotator.

        Used to orient spawned assets so their forward axis follows
        the tangent of the spline at their placement point.

        Args:
            dir_vec (tuple): Normalized direction vector (x, y, z).

        Returns:
            unreal.Rotator: The corresponding pitch/yaw rotation.
        """
        x, y, z = dir_vec
        mag_xy = math.hypot(x, y)

        if mag_xy < 1e-6:
            yaw = 0.0
            pitch = 90.0 if z > 0 else -90.0
        else:
            yaw = math.degrees(math.atan2(y, x))
            pitch = math.degrees(math.atan2(z, mag_xy))

        return unreal.Rotator(pitch, yaw, 0.0)

    def to_vector(self, t: tuple) -> unreal.Vector:
        """
        Converts a (x, y, z) tuple into an Unreal Vector.

        Args:
            t (tuple): The source 3D tuple.

        Returns:
            unreal.Vector: The equivalent Unreal Engine vector.
        """
        return unreal.Vector(float(t[0]), float(t[1]), float(t[2]))

    # -----------------------------
    # Small UI utilities
    # -----------------------------
    def _setup_spinboxes(self, boxes, *, size=(50, 20), rng=None, value=None, no_buttons=True):
        """Batch-setup for QSpinBox/QDoubleSpinBox widgets."""
        for b in boxes:
            b.setFixedSize(*size)
            if no_buttons:
                b.setButtonSymbols(b.ButtonSymbols.NoButtons)
            if rng is not None:
                b.setRange(*rng)
            if value is not None:
                b.setValue(value)

    def _add_form_row(self, form_layout, label_text, widget_or_layout):
        """Add a labeled row to a QFormLayout from an existing widget or layout."""
        form_layout.addRow(label_text, widget_or_layout)

    # -----------------------------
    # Data/State Init
    # -----------------------------
    def _init_generation_data(self):
        """Initialize generation logs and counters."""
        self.Generation_Log = {}     # { "Generation N": {...} }
        self.Generation_Count = 0

    def _init_asset_data(self):
        """Initialize in-memory structures for assets and parameters."""
        self.Asset_File_Paths = {}   # { asset_name: asset_path }
        self.Asset_Parameters = {}   # { asset_name: {param:value,...} }
        self.Selected_Spline = None  # Level component reference
        self.Selected_Spline_Path = {}  # Serialized spline data

    # -----------------------------
    # Main Window
    # -----------------------------
    def _init_main_window(self):
        """Create main window host for the tool."""
        self.mainwindow = QMainWindow()
        self.mainwindow.setParent(self)
        self.mainwindow.setLayout(QVBoxLayout())
        self.mainwindow.setFixedSize(650, 550)

    # -----------------------------
    # Left Dock: Spline, Asset List, Generation Log
    # -----------------------------
    def _init_left_dock(self):
        """Build the left dock UI: Spline selector, Asset list + controls, Generation Log."""
        self.Left_Dock = QDockWidget(self)
        self.Left_Dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.Left_Dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # --- Spline header + button ---
        spline_header = QLabel("1. Current Spline:")
        spline_header.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 2px;")

        self.SplineButton = QPushButton("<none>")
        self.SplineButton.setStyleSheet("text-align: left; padding: 4px;")
        self.SplineButton.setToolTip("Select Spline in level and clicking button will use that spline")

        # --- Asset List header row (title + toggles) ---
        header_row = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        assetlist_header = QLabel("2. Asset List")
        assetlist_header.setStyleSheet("font-weight: bold; font-size:12pt; padding: 2px;")

        self.Random_Checkbox = QCheckBox("Random")
        self.Random_Checkbox.setToolTip("Generates Assets in a Randomised Order")

        self.InSequence_Checkbox = QCheckBox("Sequence")
        self.InSequence_Checkbox.setToolTip("Generates Assets in a Sequential Order to the Asset List")

        header_layout.addWidget(assetlist_header)
        header_layout.addStretch(1)
        header_layout.addWidget(self.Random_Checkbox)
        header_layout.addWidget(self.InSequence_Checkbox)
        header_row.setLayout(header_layout)

        # --- Asset list + +/- buttons ---
        asset_row = QWidget()
        asset_row_layout = QHBoxLayout()
        asset_row_layout.setContentsMargins(0, 0, 0, 0)
        asset_row_layout.setSpacing(6)

        self.AssetList_Widget = QListWidget()
        self.AssetList_Widget.setMinimumWidth(200)

        self.AddFileButton = QPushButton("+")
        self.AddFileButton.setFixedWidth(25)
        self.AddFileButton.setToolTip("Adds selected assets from content browser")

        self.RemoveFileButton = QPushButton("-")
        self.RemoveFileButton.setFixedWidth(25)
        self.RemoveFileButton.setToolTip("Removes asset from Asset List")
        self.RemoveFileButton.setVisible(False)

        # Right-side column with +/- buttons
        button_column = QVBoxLayout()
        button_column.addWidget(self.RemoveFileButton)
        button_column.addWidget(self.AddFileButton)
        button_column.addStretch(1)

        asset_row_layout.addWidget(self.AssetList_Widget)
        asset_row_layout.addLayout(button_column)
        asset_row.setLayout(asset_row_layout)

        # --- Generation Log (header + list + delete) ---
        self.GenerationLogHeader = QLabel("Generation Log")
        self.GenerationLogHeader.setStyleSheet("font-weight: bold; font-size: 10pt; padding: 1px;")
        self.GenerationLogHeader.setVisible(False)

        self.GenerationLogList = QListWidget()
        self.GenerationLogList.setFixedSize(270, 100)
        self.GenerationLogList.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.GenerationLogList.setToolTip("Hold CTRL and Click to de-select Log")
        self.GenerationLogList.setVisible(False)

        self.DeleteGeneration = QPushButton("Delete")
        self.DeleteGeneration.setFixedWidth(75)
        self.DeleteGeneration.setToolTip("Deletes in level generation and removes from log")
        self.DeleteGeneration.setVisible(False)

        self.GenerationLogLayout = QVBoxLayout()
        self.GenerationLogLayout.addWidget(self.GenerationLogHeader)
        self.GenerationLogLayout.addWidget(self.GenerationLogList)
        self.GenerationLogLayout.addWidget(self.DeleteGeneration)

        # --- Compose Left layout ---
        left_layout.addWidget(spline_header)
        left_layout.addWidget(self.SplineButton)
        left_layout.addWidget(header_row)
        left_layout.addWidget(asset_row)
        left_layout.addLayout(self.GenerationLogLayout)
        left_layout.addStretch(1)
        left_container.setLayout(left_layout)

        self.Left_Dock.setWidget(left_container)
        self.mainwindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.Left_Dock)

        # Hook up the random/sequence mutual exclusion (existing function you already have)
        self.ConnectRandomSequenceToggle()

    # -----------------------------
    # Right Dock: Parameters
    # -----------------------------
    def _init_param_dock(self):
        """Build the right-side parameter dock."""
        self.Param_Dock = QDockWidget("Parameters", self)
        self.Param_Dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.Param_Dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        self.Param_header = QLabel("3. Selected Asset: <none>")
        self.Param_header.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 2px;")
        self.Param_header.setFixedHeight(30)

        param_container = QWidget()
        form = QFormLayout()
        vbox = QVBoxLayout()

        # -------- Quantity --------
        self.Quantity_spin = QSpinBox()
        self.Quantity_spin_max = QSpinBox()
        self._setup_spinboxes(
            [self.Quantity_spin, self.Quantity_spin_max],
            rng=(0, 10000), value=0
        )
        self.Quantity_spin_max.setToolTip("Maximum Quantity in range")
        self.Quantity_spin_max.setVisible(False)

        self.Quantity_Range_Checkbox = QCheckBox("Range")
        self.Quantity_Range_Checkbox.setFixedHeight(20)
        self.Quantity_Range_Checkbox.setToolTip("Randomly assigns Quantity from given range")

        qty_row_w = QWidget()
        qty_row_l = QHBoxLayout()
        qty_row_l.setContentsMargins(0, 0, 0, 0)
        qty_row_l.setSpacing(6)
        for w in (self.Quantity_spin, self.Quantity_spin_max, self.Quantity_Range_Checkbox):
            qty_row_l.addWidget(w)
        qty_row_l.addStretch(1)
        qty_row_w.setLayout(qty_row_l)
        self._add_form_row(form, "Quantity:", qty_row_w)

        self.Quantity_Range_Checkbox.stateChanged.connect(
            lambda checked: self.Quantity_spin_max.setVisible(checked)
        )

        # -------- Spacing --------
        self.Spacing_double = QDoubleSpinBox()
        self.Spacing_double_max = QDoubleSpinBox()
        self._setup_spinboxes(
            [self.Spacing_double, self.Spacing_double_max],
            rng=(0.00, 10000.00), value=0.00
        )
        self.Spacing_double_max.setToolTip("Maximum Distance in range")
        self.Spacing_double_max.setVisible(False)

        self.Spacing_Range_Checkbox = QCheckBox("Range")
        self.Spacing_Range_Checkbox.setFixedHeight(20)
        self.Spacing_Range_Checkbox.setToolTip("Randomly assigns Spacing from given range")

        spacing_row_w = QWidget()
        spacing_row_l = QHBoxLayout()
        spacing_row_l.setContentsMargins(0, 0, 0, 0)
        spacing_row_l.setSpacing(6)
        for w in (self.Spacing_double, self.Spacing_double_max, self.Spacing_Range_Checkbox):
            spacing_row_l.addWidget(w)
        spacing_row_l.addStretch(1)
        spacing_row_w.setLayout(spacing_row_l)
        self._add_form_row(form, "Spacing (cm):", spacing_row_w)

        self.Spacing_Range_Checkbox.stateChanged.connect(
            lambda checked: self.Spacing_double_max.setVisible(checked)
        )

        # -------- Scale (XYZ + range) --------
        self.Scale_x = QDoubleSpinBox()
        self.Scale_y = QDoubleSpinBox()
        self.Scale_z = QDoubleSpinBox()
        self._setup_spinboxes(
            [self.Scale_x, self.Scale_y, self.Scale_z],
            rng=(0.01, 100.0), value=1.0
        )

        self.Scale_x_max = QDoubleSpinBox()
        self.Scale_y_max = QDoubleSpinBox()
        self.Scale_z_max = QDoubleSpinBox()
        self._setup_spinboxes(
            [self.Scale_x_max, self.Scale_y_max, self.Scale_z_max],
            rng=(0.01, 100.0), value=1.0
        )

        self.Scale_Range_Checkbox = QCheckBox("Range")
        self.Scale_Range_Checkbox.setFixedHeight(20)
        self.Scale_Range_Checkbox.setToolTip("Randomly assigns Scale from given range")

        scale_row = QWidget()
        scale_l = QHBoxLayout()
        scale_l.setContentsMargins(0, 0, 0, 0)
        scale_l.setSpacing(4)
        for w in (self.Scale_x, self.Scale_y, self.Scale_z, self.Scale_Range_Checkbox):
            scale_l.addWidget(w)
        scale_row.setLayout(scale_l)

        scale_max_row = QWidget()
        scale_max_l = QHBoxLayout()
        scale_max_l.setContentsMargins(0, 0, 61, 0)
        scale_max_l.setSpacing(4)
        for w in (self.Scale_x_max, self.Scale_y_max, self.Scale_z_max):
            scale_max_l.addWidget(w)
        scale_max_row.setLayout(scale_max_l)
        scale_max_row.setVisible(False)

        self.Scale_Range_Checkbox.stateChanged.connect(
            lambda checked: scale_max_row.setVisible(checked)
        )

        self._add_form_row(form, "Scale (X/Y/Z):", scale_row)
        self._add_form_row(form, "", scale_max_row)

        # -------- Rotation (XYZ + range) --------
        self.Rotation_x = QDoubleSpinBox()
        self.Rotation_y = QDoubleSpinBox()
        self.Rotation_z = QDoubleSpinBox()
        self._setup_spinboxes(
            [self.Rotation_x, self.Rotation_y, self.Rotation_z],
            rng=(-360.0, 360.0), value=0.0
        )

        self.Rotation_x_max = QDoubleSpinBox()
        self.Rotation_y_max = QDoubleSpinBox()
        self.Rotation_z_max = QDoubleSpinBox()
        self._setup_spinboxes(
            [self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max],
            rng=(-360.0, 360.0), value=0.0
        )

        self.Rotation_Range_Checkbox = QCheckBox("Range")
        self.Rotation_Range_Checkbox.setFixedHeight(20)
        self.Rotation_Range_Checkbox.setToolTip("Randomly assigns Rotation from given range")

        rotation_row = QWidget()
        rotation_l = QHBoxLayout()
        rotation_l.setContentsMargins(0, 0, 0, 0)
        rotation_l.setSpacing(4)
        for w in (self.Rotation_x, self.Rotation_y, self.Rotation_z, self.Rotation_Range_Checkbox):
            rotation_l.addWidget(w)
        rotation_row.setLayout(rotation_l)

        rotation_max_row = QWidget()
        rotation_max_l = QHBoxLayout()
        rotation_max_l.setContentsMargins(0, 0, 61, 0)
        rotation_max_l.setSpacing(4)
        for w in (self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max):
            rotation_max_l.addWidget(w)
        rotation_max_row.setLayout(rotation_max_l)
        rotation_max_row.setVisible(False)

        self.Rotation_Range_Checkbox.stateChanged.connect(
            lambda checked: rotation_max_row.setVisible(checked)
        )

        self._add_form_row(form, "Rotation (X/Y/Z):", rotation_row)
        self._add_form_row(form, "", rotation_max_row)

        # -------- Scatter --------
        self.Scatter_double = QDoubleSpinBox()
        self._setup_spinboxes([self.Scatter_double], rng=(0.0, 10000.0), value=0.0)
        self.Scatter_double.setToolTip("Applys Scatter in X and Y offset relative to spline")
        self._add_form_row(form, "Scatter (cm):", self.Scatter_double)

        # Compose dock
        vbox.addWidget(self.Param_header)
        vbox.addLayout(form)
        param_container.setLayout(vbox)
        self.Param_Dock.setWidget(param_container)
        self.mainwindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.Param_Dock)

    # -----------------------------
    # Bottom Dock: Buttons
    # -----------------------------
    def _init_bottom_dock(self):
        """Build the bottom bar with Generate/Apply buttons."""
        self.Bottom_Widget = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(8, 8, 8, 8)
        bottom_layout.addStretch(1)

        self.GenerateButton = QPushButton("Generate")
        self.GenerateButton.setToolTip("Generates assets in Asset List following parameters on the given Spline")

        self.ApplyButton = QPushButton("Apply")
        self.ApplyButton.setToolTip("Applies changes to Spline and Parameters (except Quantity) to selected generation")
        self.ApplyButton.setVisible(False)

        for b in (self.GenerateButton, self.ApplyButton):
            b.setFixedWidth(100)
            bottom_layout.addWidget(b)

        bottom_layout.addStretch(1)
        self.Bottom_Widget.setLayout(bottom_layout)

        bottom_dock = QDockWidget("", self)
        bottom_dock.setTitleBarWidget(QWidget())
        bottom_dock.setWidget(self.Bottom_Widget)
        bottom_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.mainwindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

    # -----------------------------
    # Signals / Slots
    # -----------------------------
    def _connect_signals(self):
        """Wire up all signal/slot connections."""
        # Spline selection
        self.SplineButton.clicked.connect(self.OnSelectSplineClick)
        self.SplineButton.clicked.connect(self.GetSplinePath)

        # Asset list
        self.AddFileButton.clicked.connect(self.OnAddFile)
        self.RemoveFileButton.clicked.connect(self.OnRemoveFile)
        self.AssetList_Widget.currentItemChanged.connect(self.OnAssetSelected)

        # Generation log
        self.GenerationLogList.itemSelectionChanged.connect(self.OnGenerationSelected)
        self.DeleteGeneration.clicked.connect(self.Delete)

        # Parameters change storage & tooltips
        for w in (
            self.Quantity_spin, self.Quantity_spin_max,
            self.Spacing_double, self.Spacing_double_max,
            self.Scale_x, self.Scale_y, self.Scale_z,
            self.Scale_x_max, self.Scale_y_max, self.Scale_z_max,
            self.Rotation_x, self.Rotation_y, self.Rotation_z,
            self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max,
            self.Scatter_double
        ):
            w.valueChanged.connect(self.OnParameterChanged)

        self.Quantity_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)
        self.Spacing_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)
        self.Scale_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)
        self.Rotation_Range_Checkbox.checkStateChanged.connect(self.OnParameterChanged)

        # Tooltip toggles (as you had)
        self.Quantity_Range_Checkbox.checkStateChanged.connect(self.ParametersToolTipToggle)
        self.Spacing_Range_Checkbox.checkStateChanged.connect(self.ParametersToolTipToggle)
        self.Scale_Range_Checkbox.checkStateChanged.connect(self.ParametersToolTipToggle)
        self.Rotation_Range_Checkbox.checkStateChanged.connect(self.ParametersToolTipToggle)

        # Bottom buttons
        self.GenerateButton.clicked.connect(self.Generate)
        self.ApplyButton.clicked.connect(self.Apply)

    # -----------------------------
    # Default Disabled (Greyed) State
    # -----------------------------
    def _init_default_states(self):
        """Disable parameter widgets until an asset is selected, and apply grey styling."""
        disabled_style = "color: gray; background-color: #2a2a2a;"
        to_disable = [self.Quantity_spin, self.Quantity_Range_Checkbox, self.Quantity_spin_max,
                    self.Spacing_double, self.Spacing_Range_Checkbox, self.Spacing_double_max,
                    self.Scale_x, self.Scale_y, self.Scale_z, self.Scale_Range_Checkbox,
                    self.Scale_x_max, self.Scale_y_max, self.Scale_z_max,
                    self.Rotation_x, self.Rotation_y, self.Rotation_z, self.Rotation_Range_Checkbox,
                    self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max,
                    self.Scatter_double, self.Scale_Range_Checkbox, self.ApplyButton
                    ]
        for w in to_disable:
            w.setEnabled(False)
            w.setStyleSheet(disabled_style)

    # -----------------------------
    # Spline Selection
    # -----------------------------
    def OnSelectSplineClick(self):
        """
        Called when the "Current Spline" button is clicked in the UI.

        This function retrieves the currently selected spline actor or component 
        in the Unreal level viewport and assigns it as the active spline 
        for generation. If no spline is selected or the selected object 
        is not a spline, it displays a warning in the Unreal Output Log.
        """
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

    # -----------------------------
    # Spline Path Data Retrieval
    # -----------------------------
    def GetSplinePath(self):
        """
        Extracts and stores detailed path data from the currently selected spline.

        This includes:
            - The world-space location and direction of each spline point.
            - The cumulative distance along the spline.
            - The total spline length.

        The data is stored in `self.Selected_Spline_Path` for use by 
        Generate() and Apply(), allowing precise placement of assets 
        along the spline's shape.
        """
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

    # -----------------------------
    # Random/Sequence Toggle Linking
    # -----------------------------
    def ConnectRandomSequenceToggle(self):
        """
        Ensures the 'Random' and 'Sequence' checkboxes are mutually exclusive.

        When one mode is checked, the other is automatically unchecked. 
        This prevents both random and sequential generation orders 
        from being active simultaneously.
        """

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

    # -----------------------------
    # Parameter Tooltip Updates
    # -----------------------------
    def ParametersToolTipToggle(self):
        """
        Updates tooltips dynamically based on range checkboxes.

        When a range option is enabled (e.g., Scale Range, Rotation Range),
        the corresponding tooltip is updated to reflect that random values
        will be selected within the specified range.
        """

        params = self.Asset_Parameters
        current_item = self.AssetList_Widget.currentItem()
        if not current_item: return
        asset_name = current_item.text()
        if not asset_name: return

        if params[asset_name]["quantity_range"]:
            self.Quantity_spin.setToolTip("Minimum Quantity in range")
        else:
            self.Quantity_spin.setToolTip("Number of this Asset generated")
        
        if params[asset_name]["spacing_range"]:
            self.Spacing_double.setToolTip("Minimum Distance in range")
        else:
            self.Spacing_double.setToolTip("Distance between these generated Assets")

        if params[asset_name]["scale_range"]:
            self.Scale_x.setToolTip("Minimum scale in X axis in range")
            self.Scale_y.setToolTip("Minimum scale in Y axis in range")
            self.Scale_z.setToolTip("Minimum scale in Z axis in range")
        else:
            self.Scale_x.setToolTip("Asset's scale in X axis")
            self.Scale_y.setToolTip("Asset's scale in Y axis")
            self.Scale_z.setToolTip("Asset's scale in Z axis")

        if params[asset_name]["rotation_range"]:
            self.Rotation_x.setToolTip("Minimum rotation in X axis in range")
            self.Rotation_y.setToolTip("Minimum rotation in Y axis in range")
            self.Rotation_z.setToolTip("Minimum rotation in Z axis in range")
        else:
            self.Rotation_x.setToolTip("Asset's rotation in X axis")
            self.Rotation_y.setToolTip("Asset's rotation in Y axis")
            self.Rotation_z.setToolTip("Asset's rotation in Z axis")      

    # -----------------------------
    # Asset Selection Handling
    # -----------------------------
    def OnAssetSelected(self, current, previous):
        """
        Triggered when an asset is selected from the Asset List.

        Updates the parameter panel to show and edit the settings
        for the selected asset. Enables parameter fields if this is 
        the first valid selection.
        """

        if not current:
            return

        boxes = [self.Quantity_spin, self.Quantity_Range_Checkbox, self.Quantity_spin_max,
                    self.Spacing_double, self.Spacing_Range_Checkbox, self.Spacing_double_max,
                    self.Scale_x, self.Scale_y, self.Scale_z, self.Scale_Range_Checkbox,
                    self.Scale_x_max, self.Scale_y_max, self.Scale_z_max,
                    self.Rotation_x, self.Rotation_y, self.Rotation_z, self.Rotation_Range_Checkbox,
                    self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max,
                    self.Scatter_double, self.Scale_Range_Checkbox]

        if current:
            for box in boxes:
                box.setEnabled(True)
                box.setStyleSheet("")

            # If any generation is selected, lock quantity controls
            gen_selected = False
            if hasattr(self, "GenerationLogList") and self.GenerationLogList is not None:
                gen_selected = len(self.GenerationLogList.selectedItems()) > 0

            if gen_selected:
                self.Quantity_spin.setEnabled(False)
                self.Quantity_spin.setStyleSheet("color: gray; background-color: #2a2a2a;")
                self.Quantity_Range_Checkbox.setEnabled(False)
                self.Quantity_Range_Checkbox.setStyleSheet("color: gray; background-color: #2a2a2a;")
            else:
                # ensure they’re enabled if no generation is selected
                self.Quantity_spin.setEnabled(True)
                self.Quantity_spin.setStyleSheet("")
                self.Quantity_Range_Checkbox.setEnabled(True)
                self.Quantity_Range_Checkbox.setStyleSheet("")
                self.Random_Checkbox.setEnabled(True)
                self.Random_Checkbox.setStyleSheet("")
                self.InSequence_Checkbox.setEnabled(True)
                self.InSequence_Checkbox.setStyleSheet("")
        else:
            for box in boxes:
                box.setEnabled(False)
            # keep the greyed look when disabled
            for box in boxes:
                box.setStyleSheet("color: gray; background-color: #2a2a2a;")


        asset_name = current.text()
        self.Param_header.setText(f"3. Selected Asset: {asset_name}")

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

    # -----------------------------
    # Parameter Value Synchronization
    # -----------------------------
    def OnParameterChanged(self):
        """
        Called whenever a parameter spinbox or checkbox changes.

        Synchronizes the updated values into the internal
        `self.Asset_Parameters` dictionary so they persist between 
        selections and are used by Generate() and Apply().
        """

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

    # -----------------------------
    # Asset List UI Refresh
    # -----------------------------
    def UpdateRemoveButtonVisibility(self):
        """
        Toggles the visibility of the 'Remove' button in the Asset List.

        The button is visible only when there is at least one asset 
        in the list. This provides a clean UI experience.
        """

        self.RemoveFileButton.setVisible(self.AssetList_Widget.count() > 0)

    # -----------------------------
    # Add Asset from Content Browser
    # -----------------------------
    def OnAddFile(self, selected_assets):
        """
        Adds selected assets from the Unreal Content Browser to the Asset List.

        Retrieves the selected assets using the Unreal Editor Utility subsystem, 
        adds them to the internal `Asset_File_Paths`, and creates UI entries 
        for each asset with default parameters.
        """

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

    # -----------------------------
    # Remove Asset from Asset List
    # -----------------------------
    def OnRemoveFile(self):
        """
        Removes the selected asset from the Asset List.

        Also deletes its entry in `self.Asset_File_Paths` 
        and `self.Asset_Parameters` to maintain consistency.
        """

        current = self.AssetList_Widget.currentItem()
        if current:
            self.AssetList_Widget.takeItem(self.AssetList_Widget.row(current))
        self.UpdateRemoveButtonVisibility()

        boxes = [self.Quantity_spin, self.Quantity_Range_Checkbox, self.Quantity_spin_max,
                    self.Spacing_double, self.Spacing_Range_Checkbox, self.Spacing_double_max,
                    self.Scale_x, self.Scale_y, self.Scale_z, self.Scale_Range_Checkbox,
                    self.Scale_x_max, self.Scale_y_max, self.Scale_z_max,
                    self.Rotation_x, self.Rotation_y, self.Rotation_z, self.Rotation_Range_Checkbox,
                    self.Rotation_x_max, self.Rotation_y_max, self.Rotation_z_max,
                    self.Scatter_double, self.Scale_Range_Checkbox]

        if not self.AssetList_Widget.count() > 0:
            self.Param_header.setText("3. Selected Asset: <none>")
            for box in boxes:
                box.setEnabled(False)
                box.setStyleSheet("color: gray; background-color: #2a2a2a;")

    # -----------------------------
    # Generation Log Management
    # -----------------------------
    def UpdateGenerationLog(self, spawned_actors, assets, asset_file_paths):
        """
        Logs all data from a completed generation into self.Generation_Log.
        Stores asset parameters, file paths, spawn locations, and level references.
        """
        # --- Safety Cleanup ---
        # Remove invalid or empty entries before logging a new generation
        invalid_gens = [k for k, v in self.Generation_Log.items() if not v or "Spawned Assets" not in v]
        for g in invalid_gens:
            del self.Generation_Log[g]

        # --- Unique Generation Naming ---
        base_name = "Generation"
        index = 1
        while f"{base_name} {index}" in self.Generation_Log:
            index += 1
        gen_name = f"{base_name} {index}"

        # --- Build Log Entry ---
        log_entry = {
            "Spline": None,
            "Asset List": {},
            "Parameters": {},
            "Spawned Assets": {},
            "Spawn Locations": {},
        }

        # --- Store spline data ---
        if hasattr(self, "Selected_Spline_Path") and self.Selected_Spline_Path:
            try:
                log_entry["Spline"] = copy.deepcopy(self.Selected_Spline_Path)
                unreal.log(f"[Generation Log] Stored spline data for {gen_name}.")
            except Exception as e:
                unreal.log_warning(f"[UpdateGenerationLog] Failed to store spline data: {e}")
        else:
            unreal.log_warning(f"[UpdateGenerationLog] No spline data found for {gen_name}.")

        # --- Asset List ---
        for asset in assets:
            asset_name = asset["name"]
            asset_path = asset_file_paths.get(asset_name, "Unknown Path")
            log_entry["Asset List"][asset_name] = asset_path

        # --- Parameters ---
        for asset in assets:
            asset_name = asset["name"]
            params = asset["params"].copy()
            log_entry["Parameters"][asset_name] = dict(params)

        # --- Spawned Actors ---
        for actor in spawned_actors:
            if not actor:
                continue
            try:
                actor_label = actor.get_actor_label()
                actor_path = actor.get_path_name()
                actor_loc = actor.get_actor_location()
                log_entry["Spawned Assets"][actor_label] = actor_path
                log_entry["Spawn Locations"][actor_label] = [actor_loc.x, actor_loc.y, actor_loc.z]
            except Exception as e:
                unreal.log_warning(f"[UpdateGenerationLog] Failed to log actor: {e}")

        # --- Spawn order & distances ---
        try:
            if hasattr(self, "_last_spawn_order"):
                log_entry["Spawn Order"] = list(self._last_spawn_order)
            else:
                log_entry["Spawn Order"] = [a.get_actor_label() for a in spawned_actors if unreal.Object.is_valid(a)]

            if hasattr(self, "_last_spawn_distances"):
                log_entry["Spawn Distances"] = dict(self._last_spawn_distances)
            else:
                log_entry["Spawn Distances"] = {}
        finally:
            if hasattr(self, "_last_spawn_order"):
                del self._last_spawn_order
            if hasattr(self, "_last_spawn_distances"):
                del self._last_spawn_distances

        # --- Add to dictionary ---
        self.Generation_Log[gen_name] = log_entry
        self.Generation_Count = len(self.Generation_Log)
        unreal.log(f"[Generation Log] Added {gen_name} with {len(spawned_actors)} spawned assets.")

        # --- Update UI ---
        if hasattr(self, "GenerationLogHeader") and hasattr(self, "GenerationLogList") and hasattr(self, "DeleteGeneration"):
            self.GenerationLogList.clear()
            for gen in self.Generation_Log.keys():
                self.GenerationLogList.addItem(gen)

            # Show or hide log UI dynamically
            has_logs = len(self.Generation_Log) > 0
            self.GenerationLogHeader.setVisible(has_logs)
            self.GenerationLogList.setVisible(has_logs)
            self.DeleteGeneration.setVisible(has_logs)
            self.ApplyButton.setVisible(has_logs)

    # -----------------------------
    # Generation Selection Handling
    # -----------------------------
    def OnGenerationSelected(self):
        """
        Called when a generation entry is selected in the Generation Log list.

        Highlights the corresponding actors in the viewport and 
        enables the Apply button so users can modify the selected generation.
        """

        disabled_style = "color: gray; background-color: #2a2a2a;"
        to_disable = [self.Quantity_spin, self.Quantity_Range_Checkbox, self.Quantity_spin_max,
                      self.Random_Checkbox, self.InSequence_Checkbox
                      ]

        selected_items = self.GenerationLogList.selectedItems()
        if not selected_items:
            for w in to_disable:
                w.setEnabled(True)
                w.setStyleSheet("")
            self.ApplyButton.setEnabled(False)
            self.ApplyButton.setStyleSheet(disabled_style)
            return
        
        gen_name = selected_items[0].text()
        gen_data = self.Generation_Log.get(gen_name, {})
        if not gen_data:
            unreal.log_warning(f"[Apply] no data found for {gen_name}")
            return
        
        #Restore spline (just visually or keep reference)
        self.Selected_Spline_Path = gen_data.get("Spline", None)

        #Repopulate asset list Widget
        self.AssetList_Widget.clear()
        for asset_name in gen_data["Asset List"].keys():
            self.AssetList_Widget.addItem(asset_name)

        #Restore Parameter dictionary
        self.Asset_Parameters = gen_data["Parameters"]

        #Disable Unapplicable Parameters
        for w in to_disable:
            w.setEnabled(False)
            w.setStyleSheet(disabled_style)
        
        self.ApplyButton.setEnabled(True)
        self.ApplyButton.setStyleSheet("")

        unreal.log(f"[Apply] Loaded parameters and assets for {gen_name}")
    # -----------------------------
    # Actor Retrieval Utility
    # -----------------------------
    def GetActorByPath(self, path_or_label: str):
        """
        Finds an actor in the current level by matching its label or path name.
        Safe replacement for deprecated get_actor_reference().
        """
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        all_actors = actor_subsystem.get_all_level_actors()

        # Try to match by exact path first
        for actor in all_actors:
            if actor.get_path_name() == path_or_label:
                return actor

        # Fallback: match by actor label
        for actor in all_actors:
            if actor.get_actor_label() == path_or_label:
                return actor

        unreal.log_warning(f"[GetActorByPath] Could not find actor for '{path_or_label}'")
        return None
    
    # -----------------------------
    # Asset Placement Calculation
    # -----------------------------
    def ComputePlacementAdvance(self, previous_actor, asset_obj, params):
        """
        Computes the appropriate spacing step between two placed assets.

        Combines the bounding-box size of the previous and next assets 
        with the user-defined spacing value. Used to ensure consistent 
        placement along the spline without unwanted overlap.

        Args:
            previous_actor (unreal.Actor): The last spawned actor (or None).
            next_asset (unreal.Object): The asset to be placed next.
            params (dict): The current asset's placement parameters.

        Returns:
            float: The distance step to advance along the spline.
        """

        try:
            if previous_actor:
                prev_origin, prev_extent = previous_actor.get_actor_bounds(True)
                prev_size = max(prev_extent.x, prev_extent.y, prev_extent.z)
            else:
                prev_size = 0.0

            est_curr_half = 0.0
            if asset_obj and hasattr(asset_obj, "get_bounds"):
                try:
                    bounds = asset_obj.get_bounds()
                    est_curr_half = max(bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z)
                except Exception:
                    pass

            user_spacing = float(params.get("spacing", 0.0))
            advance = prev_size + est_curr_half + user_spacing
            return advance
        except Exception as e:
            unreal.log_warning(f"[Advance] Failed to compute spacing: {e}")
            return 0.0

    # ------------------------------
    # Generation Deletion
    # ------------------------------
    def Delete(self):
        """
        Deletes the selected generation from both the scene and the log.

        Removes all spawned actors associated with the selected generation 
        from the level and clears their references from `self.Generation_Log`.
        Updates the Generation Log list to reflect the deletion.
        """

        if not self.Generation_Log:
            unreal.log_warning("[Delete] No generation log found — nothing to delete.")
            return

        if not hasattr(self, "GenerationLogList") or self.GenerationLogList.count() == 0:
            unreal.log_warning("[Delete] No generation list found or it's empty.")
            return

        selected_items = self.GenerationLogList.selectedItems()
        if not selected_items:
            unreal.log_warning("[Delete] No generation selected in the log list.")
            return

        selected_gen = selected_items[0].text()
        if selected_gen not in self.Generation_Log:
            unreal.log_warning(f"[Delete] {selected_gen} not found in Generation_Log.")
            return

        gen_data = self.Generation_Log[selected_gen]
        spawned_assets = gen_data.get("Spawned Assets", {})
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        destroyed_count = 0

        # --- Destroy all actors belonging to this generation ---
        for label, path in spawned_assets.items():
            try:
                all_actors = actor_subsystem.get_all_level_actors()
                target = next((a for a in all_actors if a.get_actor_label() == label or a.get_path_name() == path), None)

                if target:
                    actor_subsystem.destroy_actor(target)
                    destroyed_count += 1
                else:
                    unreal.log_warning(f"[Delete] Actor '{label}' not found in level.")
            except Exception as e:
                unreal.log_warning(f"[Delete] Failed to destroy '{label}': {e}")

        # --- Remove generation from dictionary ---
        if selected_gen in self.Generation_Log:
            del self.Generation_Log[selected_gen]

        # --- Update generation count and refresh UI ---
        self.Generation_Count = len(self.Generation_Log)
        self.GenerationLogList.clear()

        for gen in self.Generation_Log.keys():
            self.GenerationLogList.addItem(gen)

        # --- Hide UI if no generations remain ---
        has_logs = len(self.Generation_Log) > 0
        self.GenerationLogHeader.setVisible(has_logs)
        self.GenerationLogList.setVisible(has_logs)
        self.DeleteGeneration.setVisible(has_logs)
        self.ApplyButton.setVisible(has_logs)

        unreal.log(f"[Delete] Deleted {destroyed_count} actors from {selected_gen}. Remaining generations: {len(self.Generation_Log)}.")

    # ------------------------------
    # Apply Updated Parameters
    # ------------------------------
    def Apply(self):
        """
        Reapplies modified parameters to an existing generation.

        Updates transforms, scales, rotations, scatter, and spacing.
        Keeps actor alignment stable across multiple applies.
        """

        selected_items = self.GenerationLogList.selectedItems()
        if not selected_items:
            unreal.log_warning("[Apply] No generation selected to update.")
            return

        gen_name = selected_items[0].text()
        gen_data = self.Generation_Log.get(gen_name)
        if not gen_data:
            unreal.log_warning(f"[Apply] No data found for {gen_name}")
            return

        new_params = copy.deepcopy(self.Asset_Parameters)
        gen_data["Spline"] = self.Selected_Spline_Path
        spline_data = gen_data["Spline"]

        if not spline_data or not spline_data.get("Point Data"):
            unreal.log_warning("[Apply] Missing spline or point data.")
            return

        # --- Extract spline data ---
        point_data = spline_data["Point Data"]
        distances = [float(p["Distance Along Spline"]) for p in point_data]
        positions = [p["World Location"] for p in point_data]
        directions = [p["Direction"] for p in point_data]
        total_length = float(spline_data.get("Total Spline Length", distances[-1] if distances else 0.0))

        # --- Detect spacing change robustly ---
        old_params = gen_data.get("Parameters", {})
        spacing_changed = False
        for asset_name, new_p in new_params.items():
            old_p = old_params.get(asset_name, {})
            if abs(float(new_p.get("spacing", 0.0)) - float(old_p.get("spacing", 0.0))) > 0.001:
                spacing_changed = True
                break

        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        spawned_assets = gen_data.get("Spawned Assets", {})
        asset_list = gen_data.get("Asset List", {})
        spawn_order = gen_data.get("Spawn Order", list(spawned_assets.keys()))
        spawn_dist = gen_data.get("Spawn Distances", {})

        current_distance = 0.0
        previous_actor = None
        EPS = 0.1

        for actor_label in spawn_order:
            actor_path = spawned_assets.get(actor_label)
            if not actor_path:
                continue

            actor = self.GetActorByPath(actor_path)
            if not actor:
                continue

            # Determine asset type
            asset_name = next((n for n in asset_list if actor_label.startswith(n)), None)
            params = new_params.get(asset_name, {})

            # --- Base parameter fetch ---
            spacing = float(params.get("spacing", 0.0))
            scale = params.get("scale", [1, 1, 1])
            rotation = params.get("rotation", None)
            scatter = float(params.get("scatter", 0.0))

            # --- Handle range parameters ---
            if hasattr(self, "Spacing_Range_Checkbox") and self.Spacing_Range_Checkbox.isChecked():
                spacing_max = params.get("spacing_max", None)
                if spacing_max is not None and spacing_max > spacing:
                    spacing = random.uniform(spacing, float(spacing_max))

            if hasattr(self, "Scale_Range_Checkbox") and self.Scale_Range_Checkbox.isChecked():
                scale_max = params.get("scale_max", None)
                if scale_max:
                    sx = random.uniform(float(scale[0]), float(scale_max[0]))
                    sy = random.uniform(float(scale[1]), float(scale_max[1]))
                    sz = random.uniform(float(scale[2]), float(scale_max[2]))
                    scale = [sx, sy, sz]

            if hasattr(self, "Rotation_Range_Checkbox") and self.Rotation_Range_Checkbox.isChecked():
                rot_max = params.get("rotation_max", None)
                if rotation and rot_max:
                    rx = random.uniform(float(rotation[0]), float(rot_max[0]))
                    ry = random.uniform(float(rotation[1]), float(rot_max[1]))
                    rz = random.uniform(float(rotation[2]), float(rot_max[2]))
                    rotation = [rx, ry, rz]

            # --- Compute distance ---
            if not spacing_changed and actor_label in spawn_dist:
                distance = float(spawn_dist[actor_label])
            else:
                if previous_actor:
                    prev_origin, prev_extent = previous_actor.get_actor_bounds(True)
                    prev_half = max(prev_extent.x, prev_extent.y, prev_extent.z)
                else:
                    prev_half = 0.0

                asset_obj = unreal.load_asset(asset_list.get(asset_name))
                curr_half = 0.0
                if asset_obj and hasattr(asset_obj, "get_bounds"):
                    try:
                        bounds = asset_obj.get_bounds()
                        curr_half = max(bounds.box_extent.x, bounds.box_extent.y, bounds.box_extent.z)
                    except Exception:
                        pass

                advance = prev_half + curr_half + spacing + EPS
                current_distance += advance
                current_distance = max(0.0, min(total_length, current_distance))
                distance = round(current_distance, 4)

            pos_tuple, dir_vec = self.sample_at_distance(distance, distances, positions, directions)
            new_loc = self.to_vector(pos_tuple)

            # --- Scatter offset (XY only, no Z) ---
            if scatter != 0.0:
                right = (-dir_vec[1], dir_vec[0], 0.0)
                rmag = math.sqrt(sum(c * c for c in right))
                if rmag > 1e-6:
                    right = tuple(c / rmag for c in right)
                else:
                    right = (1, 0, 0)

                off_r = random.uniform(-scatter, scatter)
                new_loc.x += right[0] * off_r
                new_loc.y += right[1] * off_r

            # --- Rotation and scale ---
            if rotation:
                try:
                    new_rot = unreal.Rotator(float(rotation[0]), float(rotation[1]), float(rotation[2]))
                except Exception:
                    new_rot = self.rotator_from_direction(dir_vec)
            else:
                new_rot = self.rotator_from_direction(dir_vec)

            new_scale = unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2]))
            actor.set_actor_transform(unreal.Transform(new_loc, new_rot, new_scale), False, False)
            previous_actor = actor

            spawn_dist[actor_label] = distance

        gen_data["Parameters"] = copy.deepcopy(new_params)
        gen_data["Spawn Distances"] = spawn_dist
        self.Generation_Log[gen_name] = gen_data

        unreal.log(f"[Apply] Completed Apply for '{gen_name}'. Spacing changed: {spacing_changed}")

    # ------------------------------
    # Primary Generation Routine
    # ------------------------------
    def Generate(self):
        """
        Main asset generation function.

        Uses the currently selected spline and asset parameters to 
        procedurally spawn actors along the spline's path.

        Features:
            - Supports sequential or randomized asset order.
            - Calculates spacing using bounding boxes to avoid overlap.
            - Handles scatter offsets, scaling, rotation, and range values.
            - Logs each generation in `self.Generation_Log` for later reuse.

        Output:
            - Spawns actors directly into the Unreal level.
            - Updates the Generation Log and enables Apply/Delete controls.
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

        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

        # -------------------------
        # Section 2: Build asset working list
        # -------------------------
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

        random_mode = getattr(self, "Random_Checkbox", None) and self.Random_Checkbox.isChecked()
        in_sequence = getattr(self, "InSequence_Checkbox", None) and self.InSequence_Checkbox.isChecked()

        if in_sequence:
            spawn_sequence = [a["name"] for a in assets]
            max_quantity = max(a["qty"] for a in assets)
            new_sequence = []
            for i in range(max_quantity):
                for asset_name in spawn_sequence:
                    asset_data = next((a for a in assets if a["name"] == asset_name), None)
                    if asset_data and asset_data["qty"] > i:
                        new_sequence.append(asset_data)
            sequence_index = 0
            total_sequence = len(new_sequence)
            unreal.log("InSequence mode active — alternating assets in sequence along spline.")
        else:
            unreal.log("Standard mode — spawning one asset type at a time.")

        # -------------------------
        # Section 3: Spline helpers
        # -------------------------
        spline = self.Selected_Spline_Path
        point_data = spline.get("Point Data", [])
        if not point_data:
            unreal.log_warning("[Generate] Selected_Spline_Path contains no 'Point Data'.")
            return

        distances = [float(p["Distance Along Spline"]) for p in point_data]
        positions = [p["World Location"] for p in point_data]
        directions = [p["Direction"] for p in point_data]
        total_length = float(spline.get("Total Spline Length", distances[-1] if distances else 0.0))

        # -------------------------
        # Section 4: Main generation loop
        # -------------------------
        total_to_spawn = sum(a["qty"] for a in assets)
        total_remaining = total_to_spawn
        if total_remaining <= 0:
            unreal.log_warning("[Generate] Total quantity is 0. Nothing to do.")
            return

        spawned_actors = []
        teleport = False
        current_distance = 0.0
        previous_actor = None
        spawn_attempts = 0
        MAX_ATTEMPTS = total_remaining * 20 + 1000

        while total_remaining > 0 and spawn_attempts < MAX_ATTEMPTS:
            spawn_attempts += 1

            # Choose asset
            if in_sequence:
                if sequence_index >= total_sequence:
                    unreal.log("[Generate] Completed all sequence assets.")
                    break
                chosen = new_sequence[sequence_index]
                sequence_index += 1
            elif random_mode:
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

            # --- Parameter sampling ---
            spacing = float(params.get("spacing", 0.0))
            if self.Spacing_Range_Checkbox.isChecked():
                if params.get("spacing_max") is not None and params.get("spacing_max") > spacing:
                    spacing = random.uniform(spacing, float(params["spacing_max"]))

            default_scale = params.get("scale", [1.0, 1.0, 1.0])
            scale_max = params.get("scale_max")
            if self.Scale_Range_Checkbox.isChecked() and scale_max:
                sx = random.uniform(float(default_scale[0]), float(scale_max[0]))
                sy = random.uniform(float(default_scale[1]), float(scale_max[1]))
                sz = random.uniform(float(default_scale[2]), float(scale_max[2]))
            else:
                sx, sy, sz = float(default_scale[0]), float(default_scale[1]), float(default_scale[2])

            rot_default = params.get("rotation", None)
            rot_max = params.get("rotation_max", None)
            use_user_rotation = bool(rot_default is not None)
            if self.Rotation_Range_Checkbox.isChecked() and rot_max:
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

            scatter = float(params.get("scatter", 0.0))

            # --- Unified advance (edge-to-edge when spacing==0) ---
            EPS = 0.1
            try:
                if previous_actor:
                    prev_origin, prev_extent = previous_actor.get_actor_bounds(True)
                    prev_half = max(prev_extent.x, prev_extent.y, prev_extent.z)
                else:
                    prev_half = 0.0

                est_curr_half = 0.0
                asset_path = self.Asset_File_Paths.get(name)
                if asset_path:
                    asset_obj = unreal.load_asset(asset_path)
                    if asset_obj and hasattr(asset_obj, "get_bounds"):
                        try:
                            bounds = asset_obj.get_bounds()
                            box_extent = bounds.box_extent
                            est_curr_half = max(box_extent.x, box_extent.y, box_extent.z)
                        except Exception:
                            pass

                user_spacing = float(params.get("spacing", 0.0))
                advance = prev_half + est_curr_half + user_spacing + EPS
                current_distance += advance

                unreal.log(f"[Advance] +{advance:.1f} (prev_half={prev_half:.1f}, curr_half≈{est_curr_half:.1f}, spacing={user_spacing:.1f})")
            except Exception as e:
                unreal.log_warning(f"[Advance] Failed: {e}")

            # --- Spawn transform ---
            pos_tuple, dir_vec = self.sample_at_distance(current_distance, distances, positions, directions)
            candidate_loc = self.to_vector(pos_tuple)
            base_rot = user_rotator if use_user_rotation else self.rotator_from_direction(dir_vec)
            spawn_transform = unreal.Transform(candidate_loc, base_rot, unreal.Vector(sx, sy, sz))

            # --- Overlap avoidance ---
            trial_attempts = 0
            MAX_TRIALS = 25
            spawned_success = False
            asset_path = self.Asset_File_Paths.get(name)
            unreal.log_warning(asset_path)
            if not asset_path:
                unreal.log_warning(f"[Generate] Missing path for asset '{name}'. Skipping this asset.")
                continue

            asset_obj = unreal.load_asset(asset_path)
            if not asset_obj:
                unreal.log_warning(f"[Generate] Failed to load asset at '{asset_path}'. Skipping.")
                continue

            while trial_attempts < MAX_TRIALS:
                trial_attempts += 1
                scattered_loc = unreal.Vector(candidate_loc.x, candidate_loc.y, candidate_loc.z)
                if scatter != 0.0:
                    right = (-dir_vec[1], dir_vec[0], 0.0)
                    rmag = math.sqrt(right[0] ** 2 + right[1] ** 2 + right[2] ** 2)
                    if rmag > 1e-6:
                        right = (right[0] / rmag, right[1] / rmag, right[2] / rmag)
                    else:
                        right = (1.0, 0.0, 0.0)
                    up = (0.0, 0.0, 1.0)
                    off_r = random.uniform(-scatter, scatter)
                    off_u = random.uniform(-scatter, scatter)
                    scattered_loc.x += right[0] * off_r + up[0] * off_u
                    scattered_loc.y += right[1] * off_r + up[1] * off_u

                try:
                    trial_actor = actor_subsystem.spawn_actor_from_object(asset_obj, scattered_loc)
                except Exception as e:
                    unreal.log_warning(f"[Generate] spawn_actor_from_object failed for '{name}': {e}")
                    break

                try:
                    trial_transform = unreal.Transform(scattered_loc, base_rot, unreal.Vector(sx, sy, sz))
                    trial_actor.set_actor_transform(trial_transform, False, teleport)
                except Exception:
                    try:
                        trial_actor.set_actor_location_and_rotation(scattered_loc, base_rot, False, unreal.TeleportType.NONE)
                        trial_actor.set_actor_scale3d(unreal.Vector(sx, sy, sz))
                    except Exception:
                        try:
                            actor_subsystem.destroy_actor(trial_actor)
                        except Exception:
                            pass
                        break

                try:
                    bbox = trial_actor.get_components_bounding_box(True)
                    center = bbox.get_center()
                    extent = bbox.get_extent()
                    trial_radius = max(extent.x, extent.y, extent.z)
                except Exception:
                    center = trial_actor.get_actor_location()
                    trial_radius = 50.0

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
                    dvec = center - ocenter
                    dist = math.sqrt(dvec.x ** 2 + dvec.y ** 2 + dvec.z ** 2)
                    if dist < (trial_radius + other_radius + 2.0):
                        overlap = True
                        break

                if not overlap:
                    spawned_actors.append(trial_actor)
                    spawned_success = True
                    break

                try:
                    actor_subsystem.destroy_actor(trial_actor)
                except Exception:
                    pass
                step_forward = max(spacing * 0.5, 10.0)
                current_distance += step_forward
                if current_distance > total_length:
                    break
                pos_tuple, dir_vec = self.sample_at_distance(current_distance, distances, positions, directions)
                candidate_loc = self.to_vector(pos_tuple)
                if not use_user_rotation:
                    base_rot = self.rotator_from_direction(dir_vec)

            if spawned_success:
                previous_actor = trial_actor
            else:
                unreal.log_warning(f"[Generate] Could not find non-overlapping spot for '{name}' after {trial_attempts} trials. Skipping this spawn.")

            chosen["qty"] -= 1
            total_remaining -= 1
            if current_distance > total_length:
                unreal.log("[Generate] Reached end of spline - stopping generation.")
                break

            try:
                actor_label = trial_actor.get_actor_label()
            except Exception:
                actor_label = f"{name}_{len(spawned_actors)}"

            if not hasattr(self, "_last_spawn_order"):
                self._last_spawn_order = []
            if not hasattr(self, "_last_spawn_distances"):
                self._last_spawn_distances = {}

            self._last_spawn_order.append(actor_label)
            self._last_spawn_distances[actor_label] = float(current_distance)

        # -------------------------
        # Folder Grouping
        # -------------------------
        try:
            # Create a folder in the World Outliner matching the generation log name
            generation_name = f"Generation_{len(self.Generation_Log) + 1}"
            for actor in spawned_actors:
                try:
                    actor.set_folder_path(generation_name)
                except Exception:
                    pass

            # Update Generation Log with folder name
            self.UpdateGenerationLog(spawned_actors, assets, self.Asset_File_Paths)
            if generation_name in self.Generation_Log:
                self.Generation_Log[generation_name]["FolderName"] = generation_name

            unreal.log(f"[Generate] Completed generation '{generation_name}' with {len(spawned_actors)} actors.")
        except Exception as e:
            unreal.log_warning(f"[Generate] Folder assignment failed: {e}")


# ============================
# Python Tool UI Palette/Style
# ============================
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

# ============================
# Launch Python Tool Function
# ============================
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