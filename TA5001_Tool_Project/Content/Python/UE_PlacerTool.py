import unreal


def GetSplinePath():
    #User Input Spline from within UE5 editor
    #Get Spline handles world position and rotation
    #Store world position and rotation
    #Extract path from Spline data
    pass

def SetAssetList():
    #User Input a list of Asset files
    #Check if inputted files are .uasset, .obj, .fbx
    #Store Asset file list
    pass

def SetParameters():
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

def Generate():
    #Get Spline Path
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

