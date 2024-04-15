import maya.cmds as cmds
class Joint:
  JOINT_TYPE = "type"
  ERROR1 = "Input must be an integer"
  
  def _init_(self, radius):
    self._radius = radius
    
  @property
  def radius(self):
    return self._radius

  @radius.setter
  def radius(self, value):
    if isinstance(value, int):
      self._radius = value
    else:
      raise ValueError(self.ERROR1)
class Volume(Joint):
  JOINT_TYPE = "volume_type"
  
  def attr_volume_joint(self):
    axis = ["X", "Y", "Z"]  
    select_joint = cmds.ls("*Volume*JA_JNT")  
    
    for a in select_joint:
        cmds.select(a)
        cmds.addAttr(longName = ("push_offset"), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 0.7, keyable = True)
        cmds.addAttr(longName = ("scale_offset"), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 1, keyable = True)
        cmds.addAttr(longName = ("min_scale"), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 0.1, keyable = True)
        cmds.addAttr(longName = ("max_scale"), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 5, keyable = True)
        cmds.addAttr(longName = ("push_interpolation"), attributeType = "enum", enumName = "none:linear:smooth:spline", keyable = True)
      
        for r in axis:       
             cmds.addAttr(longName = ("pre_multi_"+r), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 1, keyable = True)  
             cmds.addAttr(longName = ("push_pos_"+r), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 1, keyable = True)
             cmds.addAttr(longName = ("push_neg_"+r), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 1, keyable = True)
             #cmds.addAttr(longName = ("current_value_"+r), attributeType = "float", minValue = -100, maxValue = 100, defaultValue = 0, keyable = True)
             
  
