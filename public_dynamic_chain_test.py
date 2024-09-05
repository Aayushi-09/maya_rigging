
import maya.cmds as cmds


class delayAnimation():

    def __init__(self):

        self.myWindow = "delayAnimationWin"
        self.clusters = []
        self.controllers = []
        self.controllers_grp = []

        

    def query(self):

        #===================================================================================
        #declaring variable for all the field text and querying out the text entered
        jnts = cmds.textScrollList('jointList', q=1, allItems=True)
        return jnts

    def create_clusters_on_curve(self, *args):

        #====================================================================================
        # Get the selected curve
        selected_curve = "curve1"
    
        # Get the number of CVs (control vertices) on the curve
        num_cvs = cmds.getAttr(selected_curve + ".spans") + cmds.getAttr(selected_curve + ".degree")
    
        # Create a cluster for each CV
        self.clusters = []
        for i in range(num_cvs):
            cv = '{}.cv[{}]'.format(selected_curve , i)
            cluster_name = 'cluster_{}'.format(i + 1)
            cluster, handle = cmds.cluster(cv, name=cluster_name)
            self.clusters.append(cluster)
        
            # Optionally, you can group the cluster handle for better organization
            #cmds.group(handle, name=cluster_name + '_grp')
        
        cmds.select(clear=True)
        print("Created {} clusters on the curve.".format(len(self.clusters)))
        

        
    def create_controllers_for_selected_joints(self, *args):

        #====================================================================================
        # Get the selected joints
        jnts= self.query()
        
        # Convert Unicode strings to regular strings
        jnts = [str(item) for item in jnts]
        selected_jnts = jnts
  
        self.controllers = []
        self.controllers_grp = []
    
        for joint in jnts:
        
            # Create a NURBS circle controller
            ctrl_name = joint + "_ctrl"
            controller = cmds.circle(name=ctrl_name, normal=[1, 0, 0], radius=1)[0]
        
            cmds.delete(cmds.parentConstraint(joint, controller, mo = False))
        
            # Freeze transformations on the controller
            cmds.makeIdentity(controller, apply=True, translate=True, rotate=True, scale=True)
        
            # Create a group for the controller
            ctrl_group = cmds.group(controller, name=ctrl_name + "_grp")

            #delete controllers history
            cmds.delete(controller, ch = True)
            
            self.controllers_grp.append(ctrl_group)
            self.controllers.append(controller)

            
          

    def parent_clusters_to_controllers(self, *args):

        #======================================================       
        # String to add
        suffix = "Handle"

        # Add the string to each element
        self.clusters = [item + suffix for item in self.clusters]

        # Convert Unicode strings to regular strings
        self.clusters = [str(item) for item in self.clusters]
        
        # Convert Unicode strings to regular strings
        self.controllers = [str(item) for item in self.controllers]

        print (self.controllers)
        print (self.clusters)
        
    
        num_clusters = len(self.clusters)
        num_controllers = len(self.controllers)
    
    
        # Parent the first two clusters to the first controller
        for i in range(2):
            if i < num_clusters:
                cmds.parent(self.clusters[i], self.controllers[0])
    
        # Parent the last two clusters to the last controller
        for i in range(-2, 0):
            if num_clusters + i >= 0:
                cmds.parent(self.clusters[i], self.controllers[-1])
    
        # Parent the remaining clusters to the remaining controllers
        remaining_clusters = self.clusters[2:-2]
        remaining_controllers = self.controllers[1:-1]
    
        for i in range(len(remaining_clusters)):
            if i < len(remaining_controllers):
                cmds.parent(remaining_clusters[i], remaining_controllers[i])
    
        print("Parenting complete.")


    
    def create_sine_deformer(self, *args):

        #=================================================================================
        # Create a sine deformer on the curve
        sine_deformer = cmds.nonLinear("curve1", type='sine', name='sineDeformer')
        sine_handle = sine_deformer[0]  # The handle of the sine deformer
        
        # Convert Unicode strings to regular strings
        controllers = [str(item) for item in self.controllers]

        # Connect the controllers to the sine deformer
        for i, ctrl in enumerate(controllers):

            # Add attributes to the controller for sine wave manipulation
            if not cmds.attributeQuery('sineAmplitude', node=ctrl, exists=True):
                cmds.addAttr(ctrl, longName='sineAmplitude', attributeType='double', keyable=True, defaultValue=1.0)
            if not cmds.attributeQuery('sineWavelength', node=ctrl, exists=True):
                cmds.addAttr(ctrl, longName='sineWavelength', attributeType='double', keyable=True, defaultValue=2.0)
            if not cmds.attributeQuery('sineOffset', node=ctrl, exists=True):
                cmds.addAttr(ctrl, longName='sineOffset', attributeType='double', keyable=True, defaultValue=0.0)

        for ctrl in controllers:      
            # Connect the controller attributes to the sine deformer attributes
            cmds.connectAttr(sine_handle + ".amplitude", ctrl + ".sineAmplitude")
            cmds.connectAttr(sine_handle + ".wavelength", ctrl + ".sineWavelength")
            cmds.connectAttr(sine_handle + ".offset", ctrl + ".sineOffset")

        main_ctrl= cmds.nurbsSquare(name="main_controller")
        cmds.addAttr(main_ctrl, longName="delay", attributeType="double", keyable=True, defaultValue=0.0)
        cmds.addAttr(main_ctrl, longName="amplitude", attributeType="double", keyable=True, defaultValue=0.0)

        cmds.connectAttr("main_controller.delay", sine_handle + ".offset")
        cmds.connectAttr("main_controller.amplitude", sine_handle + ".amplitude")
        
        controllers_grp = [str(item) for item in self.controllers_grp]
        
        for controller_grp in controllers_grp:
            cmds.parent(controller_grp,main_ctrl)

        cmds.parent("sine1Handle","curve1","ikHandle1", main_ctrl)
    
        print("Sine deformer created and connected to controllers.")
    
    
    def create_ik_spline(self, *args):

        #===================================================================================
        #create curve and joints to give reference 

        jnts = self.query()
        firstJnt = jnts[0]
        lastJnt = jnts[len(jnts) - 1]

        cmds.ikHandle(sj = firstJnt, ee = lastJnt, sol = "ikSplineSolver", pcv = False,  ccv = True, scv = False)

        
        self.create_clusters_on_curve()
        self.create_controllers_for_selected_joints()
        self.parent_clusters_to_controllers()
        self.create_sine_deformer()

    def handle_one_axis(self, axis_states):

        # Identify which axis is checked and handle it
        if axis_states[0]:  # X axis
             cmds.xform("sine1Handle", rotation = [90,0,0])   
            # Handle X axis condition

        elif axis_states[1]:  # Y axis
            cmds.xform("sine1Handle", rotation = [0,90,0])
            # Handle Y axis condition

        elif axis_states[2]:  # Z axis
            cmds.xform("sine1Handle", rotation = [0,0,90])
            # Handle Z axis condition

    def handle_two_axes(self, axis_states):

        # Identify which axes are checked and handle them
        if axis_states[0] and axis_states[1]:  # X and Y
             cmds.xform("sine1Handle", rotation = [90,90,0])
            # Handle X and Y axes condition

        elif axis_states[0] and axis_states[2]:  # X and Z          
             cmds.xform("sine1Handle", rotation = [90,0,90])
           # Handle X and Z axes condition

        elif axis_states[1] and axis_states[2]:  # Y and Z           
             cmds.xform("sine1Handle", rotation = [0,90,90])
            # Handle Y and Z axes condition

    def handle_three_axes(self):

        # All three axes are checked              
         cmds.xform("sine1Handle", rotation = [90,90,90])     
        # Handle the condition for all three axes

    def load_joint_chain(*args):

        # Clear the text scroll list
        cmds.textScrollList('jointList', edit=True, removeAll=True)

        # Get the selected joint chain
        selection = cmds.ls(selection=True, type='joint')
        if not selection:
            cmds.warning("Please select a joint chain.")
            return

        # Get all joints in the chain
        joint_chain = cmds.listRelatives(selection[0], allDescendents=True, type='joint')
        joint_chain.append(selection[0])
        new_joint_chain = joint_chain.reverse()
        #new_joint_chain = [selection[0]] + new_joint_chain if new_joint_chain else [selection[0]]

        # Populate the text scroll list with the joint names
        for joint in joint_chain:
            cmds.textScrollList('jointList', edit=True, append=joint)

    def apply_toggle(self, *args):

        # Get the state of the checkboxes
        axis_states = cmds.checkBoxGrp(self.axis_checkboxes, query=True, valueArray3=True)

        # Count how many axes are checked
        num_checked = sum(axis_states)

        # Handle different conditions based on the number of axes checked
        if num_checked == 1:
            self.handle_one_axis(axis_states)
        elif num_checked == 2:
            self.handle_two_axes(axis_states)
        elif num_checked == 3:
            self.handle_three_axes()
        else:
            print("No axis selected.")
        
    def showUI(self):    

        #close old window with the instance name myWindow
        if cmds.window(self.myWindow, exists = True):
            cmds.deleteUI(self.myWindow, window=True)

        #create a new window with instance myWindow
        self.myWindow = cmds.window(self.myWindow, title ="delayed animation", widthHeight = (300,300))
        cmds.columnLayout(adjustableColumn=True)

        cmds.separator(height = 10, style = "in")
        cmds.separator(height = 10, style = "out")

        # Create the button
        cmds.button(label="Load Joint Chain", command=self.load_joint_chain)
    
        # Create the text scroll list to display the joints
        cmds.textScrollList('jointList', numberOfRows=8, allowMultiSelection=False)

        self.layout = cmds.columnLayout(adjustableColumn=True)

        # Checkboxes for X, Y, Z axes
        self.axis_checkboxes = cmds.checkBoxGrp(label="Axes", numberOfCheckBoxes=3, labelArray3=["X", "Y", "Z"], valueArray3=[True, True, True])
        
        # Create the button
        cmds.button(label="Run", command=lambda x: (self.create_ik_spline(), self.apply_toggle()))

        cmds.showWindow(self.myWindow)

x=delayAnimation()
x.showUI()
