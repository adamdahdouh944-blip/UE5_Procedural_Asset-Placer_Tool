import unreal

class AssetPlacerTool:
    def __init__(self):
        self.selected_spline_actor = None
        self.spline_path = None

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
                return
        
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

    def SetAssetList(self):
        #User Input a list of Asset files
        #Check if inputted files are .uasset, .obj, .fbx
        #Store Asset file list
        pass

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