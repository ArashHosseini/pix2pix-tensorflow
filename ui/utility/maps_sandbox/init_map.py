def init_map_in_maya(curves_data):

    import maya.cmds as mc

    curves = []
    for k, v in curves_data.items():
        curve_object = mc.curve(degree=1, point=(v[0], v[1]))
        curves.append(curve_object)

    mc.select(curves)
    mc.createDisplayLayer( name='street_layer' )
    mc.setAttr("street_layer.color", 16)
    mc.select(None)