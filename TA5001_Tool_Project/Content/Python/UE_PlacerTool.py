import unreal
from UE_PlacerTool_UI import AssetPlacerToolWindow
import os 

class AssetPlacerTool:
    def __init__(self):
        self.selected_spline_actor = None
        self.spline_path = None
        self.asset_list = [None]


    def SelectSpline(self):
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
                self.selected_spline_actor = actor
                unreal.log(f"Stored SplineComponent: {actor.get_name()}")
                return actor
        
        # If none matched
        unreal.log_warning("No SplineComponent found among selected actors.")


    def GetSplinePath(self):
        '''
        Returns the world-space points of the first SplineComponent
        in the selected actor as a list of Vector objects
        '''

        if not self.selected_spline_actor:
            unreal.log_warning("no spline actor selected.")
            return []
        
        # Get the first SplineComponent
        spline_component = self.selected_spline_actor.get_components_by_class(unreal.SplineComponent)[0]

        # Collect all spline points in world space
        num_points = spline_component.get_number_of_spline_points()
        spline_path = []

        # Get the location of all the spline points 
        for i in range(num_points):
            location = spline_component.get_location_at_spline_point(i, unreal.SplineCoordinateSpace.WORLD)
            spline_path.append(location)
        
        return spline_path

    def AddAssetsFromContent(self):
        # --- User Input a list of Asset files
        # --- Check if inputted files are .uasset, .obj, .fbx
        # --- Store Asset file list

        # From Content Browser
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()

        if not selected_assets:
            unreal.log_warning("no asset selected in content browser")
            return
            
        for asset in selected_assets:
            self.asset_list.append(asset)
            unreal.log(f"Added Asset: {asset.get_name()}")
        
        unreal.log(f"Total Assets in List: {len(self.asset_list)}")

    '''def AddAssetsFromDisk(self, destination_path = "/Game/ImportedAssets"):
        
        Opens an import file dialog (system dialog) and imports picked files into 'destination_path'.
        yje function uses AssetTools.import_assets_with_dialog(...) and returns the
        imported Uobject assets which are appended to self.asset_list.

        destination_path: package path in the Content Browser
        '''



        

    def SetParameters(self):
        #For each Asset in Asset List
            #User Input Quantity (Integer)
                #Check if Range is True
                    #if True: User Inputs Minimum and Maximum Quantity
                    #if False: Continue/Do nothing

            #User Input Spacing (Float)
                #Check if Range is True
                    #if True: User Inputs Minimum and Maximum Spacing
                    #if False: Continue/Do nothing

            #User Input Scale (3D Vector)
                #Check if Range is True
                    #if True: User Inputs Minimum and Maximum Scale
                    #if False: Continue/Do nothing

            #User Input Rotation (3D Vector)
                #Check if Range is True
                    #if True: User Inputs Minimum and Maximum Rotation
                    #if False: Continue/Do nothing

            #User Input Scatter (Float: Max Distance)
        pass

    def Generate(self):
        #Get Spline Path
        '''
        Useful Functions for Spline Shape & Data path:
            Number of Points = self.selected_spline_actor.get_number_of_spline_points()
            Number of Segments = self.selected_spline_actor.get_number_of_spline_segments()
            Location Along Path = self.selected_spline_actor.get_location_at_distance_along_spline(distance, coordinate_space)
            Tangent Direction = self.selected_spline_actor.get_tangent_at_distance_along_spline(distance, coordinate_space)
            Rotation Along Path = self.selected_spline_actor.get_rotation_at_distance_along_spline(distance, coordinate_space)

        Useful Functions for Spline Orientation & Local Space Data:
            Up Vector = self.selected_spline_actor.get_up_vector_at_distance_along_spline(distance, coordinate_space)
            Right Vector = self.selected_spline_actor.get_right_vector_at_distance_along_spline(distance, coordinate_space)
        
        Useful Functions for Spline Length & Sampling:
            Total Spline Length = self.selected_spline_actor.get_spline_length()
            Distance Per Control Point = self.selected_spline_actor.get_distance_along_spline_at_spline_point(point_index)
        
        Useful Function for Spline Curvature, Roll & Transform:
            Full Transform = self.selected_spline_actor.get_transform_at_distance_along_spline(distance, coordinate_space, use_scale)

        Optional Utilities Functions:
            Spline Point Location & Tangent = self.selected_spline_actor.get_location_and_tangent_at_spline_point(point_index, coordinate_space)
            Spline Point Local Location & Tangent = self.selected_spline_actor.get_local_location_and_tangent_at_spline_point()
            Does Spline Loop? = self.selected_spline_actor.is_closed_loop()
        '''
        #Get Asset List
            #Check if Random is True

                #if Random is True:
                    #For the Sum of Quantity of each Asset in Asset List
                        #Randomly Select Asset in Asset List
                        #Get selected Asset's Quantity
                        #while Asset's Quantity >= 0
                            #True:
                                #if Asset_Spawned > 0:
                                    #Get Asset's Spacing
                                        #if Range is True:
                                            #Randomly Select Value from Minimum and Maximum
                                            #Set Randomly Selected Value as Asset's Spacing 
                                        #if Range is False:
                                            #Get Spacing Value from Parameters
                                    #Add Spacing to Asset1 Position on Spline Path and set it as new position
                                    #if Scatter is True:
                                        #Randomly select Value from Scatter Max Distance to -(Scatter Max Distance)
                                        #With 0 being on the Spline Path Line, add randomly selected scatter value to new position on the axis vertical to the path
                                        #Set as new position
                                    #if Scatter is False:
                                        #Continue
                                    #Spawn Asset in new position on Spline Path

                                #Else:
                                    #Spawn Asset at the start of the Splne Path
                            
                                #Get Asset's Scale
                                    #if Range is True:
                                        #Randomly Select Number from Minumum and Maximum
                                    #if Range is False:
                                        #Get Scale Value from Parameters

                                #Get Asset's Rotation
                                    #if Range is True:
                                        #Randomly Select Number from Minumum and Maximum
                                    #if Range is False: 
                                        #Get Rotation Value from Parameters
                            
                                #Quantity--
                                #Asset_Spawned++

                #if Random is False:
                    #For Assets in Asset List
                        #Get Asset[i]'s Quantity
                        #while Asset[i]'s Quantity >= 0
                            #True:
                                #if Asset_Spawned > 0:
                                    #Get Asset[i]'s Spacing
                                        #if Range is True:
                                            #Randomly Select Value from Minimum and Maximum
                                            #Set Randomly Selected Value as Asset[i]'s Spacing 
                                        #if Range is False:
                                            #Get Spacing Value from Parameters
                                    #Add Spacing to Asset1 Position on Spline Path and set it as new position
                                    #if Scatter is True:
                                        #Randomly select Value from Scatter Max Distance to -(Scatter Max Distance)
                                        #With 0 being on the Spline Path Line, add randomly selected scatter value to new position on the axis vertical to the path
                                        #Set as new position
                                    #if Scatter is False:
                                        #Continue
                                    #Spawn Asset in new position on Spline Path

                                #Else:
                                    #Spawn Asset[i] at the start of the Splne Path
                            
                                #Get Asset[i]'s Scale
                                    #if Range is True:
                                        #Randomly Select Number from Minumum and Maximum
                                    #if Range is False:
                                        #Get Scale Value from Parameters

                                #Get Asset[i]'s Rotation
                                    #if Range is True:
                                        #Randomly Select Number from Minumum and Maximum
                                    #if Range is False: 
                                        #Get Rotation Value from Parameters
                            
                                #Quantity--
                                #Asset_Spawned++
        pass

Tool = AssetPlacerTool()
Tool.SelectSpline()
Tool.spline_path = Tool.GetSplinePath()

for point in Tool.spline_path:
    unreal.log(str(point))

Tool.AddAssetsFromContent()

    '''def Generate(self):
        """
        Generate assets along the spline using stored data dictionaries:
        - self.Asset_Parameters
        - self.Asset_File_Paths
        - self.Selected_Spline_Path
        Adds overlap avoidance and instanced static mesh optimization.
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

        # -------------------------
        # Section 3: Spline data helpers
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

        def lerp(a, b, t):
            return a + (b - a) * t

        def lerp_tuple(a, b, t):
            return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))

        def sample_at_distance(distance):
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
            pos = lerp_tuple(positions[idx], positions[idx + 1], t)
            dirv = lerp_tuple(directions[idx], directions[idx + 1], t)
            mag = math.sqrt(dirv[0]**2 + dirv[1]**2 + dirv[2]**2)
            if mag > 1e-6:
                dirv = (dirv[0]/mag, dirv[1]/mag, dirv[2]/mag)
            return pos, dirv

        def to_vector(t):
            return unreal.Vector(float(t[0]), float(t[1]), float(t[2]))

        def rotator_from_direction(dir_vec):
            x, y, z = dir_vec
            mag_xy = math.hypot(x, y)
            if mag_xy < 1e-6:
                yaw = 0.0
                pitch = 90.0 if z > 0 else -90.0
            else:
                yaw = math.degrees(math.atan2(y, x))
                pitch = math.degrees(math.atan2(z, mag_xy))
            return unreal.Rotator(pitch, yaw, 0.0)

        # -------------------------
        # Section 4: Optimized Spawn loop (Instancing + InSequence)
        # -------------------------
        total_to_spawn = sum(a["qty"] for a in assets)
        total_remaining = total_to_spawn
        if total_remaining <= 0:
            unreal.log_warning("[Generate] Total quantity is 0. Nothing to do.")
            return

        teleport = False
        current_distance = 0.0
        spawn_attempts = 0
        MAX_ATTEMPTS = total_remaining * 20 + 1000

        # Instancing setup
        instanced_map = {}

        # --- START OF INTEGRATED FIX ---
        # SubobjectDataSubsystem is an ENGINE subsystem, not an EDITOR subsystem.
        subobject_subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

        # We wrap this setup in a transaction so it can be undone
        with unreal.ScopedEditorTransaction("Generate Instanced Assets") as trans:
            for asset in assets:
                name = asset["name"]
                asset_path = self.Asset_File_Paths.get(name)
                if not asset_path:
                    unreal.log_warning(f"[Generate] Missing path for asset '{name}', skipping instancing.")
                    continue
                
                asset_obj = unreal.load_asset(asset_path)
                if not asset_obj or not isinstance(asset_obj, unreal.StaticMesh):
                    unreal.log_warning(f"[Generate] Failed to load asset as StaticMesh for '{name}'. Skipping.")
                    continue
                
                # 1. Spawn a host Actor at (0,0,0) to own the component
                ism_actor = actor_subsystem.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
                if not ism_actor:
                    unreal.log_warning(f"[Generate] Failed to spawn host actor for '{name}'.")
                    continue
                
                # Give it a useful name in the World Outliner
                ism_actor.set_actor_label(f"ISM_Host_{name}")

                # 2. Add an InstancedStaticMeshComponent to the actor instance
                
                # 2a. Get the root subobject handle for the actor instance
                subobject_handles = subobject_subsystem.k2_gather_subobject_data_for_instance(ism_actor)
                if not subobject_handles:
                    unreal.log_warning(f"[Generate] Could not get subobject data for host actor '{name}'. Cleaning up.")
                    actor_subsystem.destroy_actor(ism_actor)
                    continue
                
                # Get the handle for the actor's root (the DefaultSceneRoot)
                root_handle = subobject_handles[0]

                # 2b. Define the parameters for the new component
                add_params = unreal.AddNewSubobjectParams()
                add_params.parent_handle = root_handle
                add_params.new_class = unreal.InstancedStaticMeshComponent
                add_params.blueprint_context = None 
                
                # 2c. Add the new subobject (component)
                new_subobject_tuple = subobject_subsystem.add_new_subobject(add_params)
                
                # We must use the SubobjectDataBlueprintFunctionLibrary to check if the handle is valid
                sdb_lib = unreal.SubobjectDataBlueprintFunctionLibrary
                handle_to_check = new_subobject_tuple[0] if new_subobject_tuple else None

                if not handle_to_check or not sdb_lib.is_handle_valid(handle_to_check):
                    fail_reason = new_subobject_tuple[1].text if (new_subobject_tuple and new_subobject_tuple[1]) else "Unknown"
                    unreal.log_warning(f"[Generate] Failed to add subobject component for '{name}'. Reason: {fail_reason}. Cleaning up.")
                    actor_subsystem.destroy_actor(ism_actor)
                    continue

                new_handle = new_subobject_tuple[0]

                # 2d. Get the actual component object from its handle
                # We also need the function library for this
                ism_component_data = sdb_lib.get_data(new_handle)
                ism_component = sdb_lib.get_object(ism_component_data)

                if not ism_component or not isinstance(ism_component, unreal.InstancedStaticMeshComponent):
                    unreal.log_warning(f"[Generate] Failed to retrieve component from handle for '{name}'. Cleaning up.")
                    actor_subsystem.destroy_actor(ism_actor)
                    continue

                # 5. Assign the static mesh to the component
                ism_component.set_static_mesh(asset_obj)
                
                # 6. Store the component (not the actor) in our map
                instanced_map[name] = ism_component
        # --- END OF INTEGRATED FIX ---


        # InSequence + Random mode setup
        in_sequence = getattr(self, "InSequence_Checkbox", None) and self.InSequence_Checkbox.isChecked()
        random_mode = getattr(self, "Random_Checkbox", None) and self.Random_Checkbox.isChecked()

        if in_sequence:
            sequence_assets = [a for a in assets if a["qty"] > 0]
            if not sequence_assets:
                unreal.log_warning("[Generate] InSequence mode selected, but no assets have quantity > 0.")
                return
            max_qty = max(a["qty"] for a in sequence_assets)
            spawn_sequence = []
            for i in range(max_qty):
                for a in sequence_assets:
                    if a["qty"] > i:
                        spawn_sequence.append(a)
            unreal.log("InSequence mode active — alternating assets in sequence along spline.")
        else:
            spawn_sequence = assets
            unreal.log("Standard or Random mode active — spawning one asset type at a time.")

        sequence_index = 0

        # --- Main Spawn Loop ---
        # We wrap the actual spawning in a transaction as well
        with unreal.ScopedEditorTransaction("Add Instances") as trans:
            while total_remaining > 0 and spawn_attempts < MAX_ATTEMPTS:
                spawn_attempts += 1

                # Select asset
                if in_sequence:
                    if not spawn_sequence:
                        unreal.log_warning("[Generate] Spawn sequence is empty.")
                        break
                    chosen = spawn_sequence[sequence_index % len(spawn_sequence)]
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

                # Spacing
                spacing = float(params.get("spacing", 0.0))
                if hasattr(self, "Spacing_Range_Checkbox") and self.Spacing_Range_Checkbox.isChecked():
                    if params.get("spacing_max") is not None and float(params.get("spacing_max")) > spacing:
                        spacing = random.uniform(spacing, float(params["spacing_max"]))

                # Scale
                default_scale = params.get("scale", [1.0, 1.0, 1.0])
                scale_max = params.get("scale_max")
                if hasattr(self, "Scale_Range_Checkbox") and self.Scale_Range_Checkbox.isChecked() and scale_max:
                    sx = random.uniform(float(default_scale[0]), float(scale_max[0]))
                    sy = random.uniform(float(default_scale[1]), float(scale_max[1]))
                    sz = random.uniform(float(default_scale[2]), float(scale_max[2]))
                else:
                    sx, sy, sz = float(default_scale[0]), float(default_scale[1]), float(default_scale[2])

                # Rotation
                rot_default = params.get("rotation", None)
                rot_max = params.get("rotation_max", None)
                use_user_rotation = bool(rot_default is not None)
                if hasattr(self, "Rotation_Range_Checkbox") and self.Rotation_Range_Checkbox.isChecked() and rot_max and rot_default:
                    rx = random.uniform(float(rot_default[0]), float(rot_max[0]))
                    ry = random.uniform(float(rot_default[1]), float(rot_max[1]))
                    rz = random.uniform(float(rot_default[2]), float(rot_max[2]))
                    user_rotator = unreal.Rotator(rx, ry, rz)
                    use_user_rotation = True
                elif rot_default:
                    user_rotator = unreal.Rotator(float(rot_default[0]), float(rot_default[1]), float(rot_default[2]))
                else:
                    user_rotator = None
                    use_user_rotation = False

                scatter = float(params.get("scatter", 0.0))

                pos_tuple, dir_vec = sample_at_distance(current_distance)
                candidate_loc = to_vector(pos_tuple)
                base_rot = user_rotator if use_user_rotation else rotator_from_direction(dir_vec)

                # Scatter offset
                scattered_loc = unreal.Vector(candidate_loc.x, candidate_loc.y, candidate_loc.z)
                if scatter != 0.0:
                    right = (-dir_vec[1], dir_vec[0], 0.0)
                    rmag = math.sqrt(right[0]**2 + right[1]**2 + right[2]**2)
                    if rmag > 1e-6:
                        right = (right[0]/rmag, right[1]/rmag, right[2]/rmag)
                    else:
                        right = (1.0, 0.0, 0.0) # Fallback if direction is vertical
                        
                    up = (0.0, 0.0, 1.0) # Using world up for scatter
                    
                    off_r = random.uniform(-scatter, scatter) # Offset along right vector
                    off_u = random.uniform(-scatter, scatter) # Offset along up vector

                    # Apply scatter relative to spline direction (on XY plane) and world up
                    scattered_loc.x += right[0]*off_r
                    scattered_loc.y += right[1]*off_r
                    scattered_loc.z += up[2]*off_u # Only apply up offset to Z

                spawn_transform = unreal.Transform(scattered_loc, base_rot, unreal.Vector(sx, sy, sz))

                # Add instance to ISM instead of spawning separate actor
                ism_component = instanced_map.get(name)
                if ism_component:
                    ism_component.add_instance(spawn_transform, True)
                else:
                    unreal.log_warning(f"[Generate] Missing ISM component for '{name}', skipping instancing.")

                # Advance spline
                chosen["qty"] -= 1
                total_remaining -= 1
                current_distance += spacing

                if current_distance > total_length:
                    unreal.log("[Generate] Reached end of spline - stopping generation.")
                    break

        unreal.log(f"[Generate] Completed generation with instancing. Remaining total: {total_remaining}")
        if spawn_attempts >= MAX_ATTEMPTS:
            unreal.log_warning(f"[Generate] Hit max spawn attempts ({MAX_ATTEMPTS}). Generation may be incomplete.")'''