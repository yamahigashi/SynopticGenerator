""" coding: utf-8 """


#import win32api as win
from win32com.client import constants as c
from win32com.client.dynamic import Dispatch as dynDispatch
import functools


#---------------------------------------------------------------------#
#------For Instantination---------------------------------------------#
#---------------------------------------------------------------------#
xsi = Application
log = xsi.LogMessage
FASTPLAYBACK_CACHESIZE = 9000  # kb/frame
KEYREPEAT_MARGIN = 0.5
GIZMO_RATE = 3

pc = lambda: xsi.Dictionary.GetObject("PlayControl")
greenkey = lambda: pc().Parameters("Key")


#---------------------------------------------------------------------#
def OneUndo(function):
    @functools.wraps(function)
    def _inner(*args, **kwargs):
        try:
            xsi.BeginUndo()
            f = function(*args, **kwargs)
        finally:
            xsi.EndUndo()
        return f
    return _inner


#---------------------------------------------------------------------#
#---------- Register XSI PluginManager--------------------------------#
#---------------------------------------------------------------------#
def XSILoadPlugin(in_reg):
    in_reg.Author = "MATSUMOTO Takayoshi"
    in_reg.Name = "synopticgenerator helper"
    in_reg.Email = "yamahigashi@gmail.com"
    in_reg.URL = ""
    in_reg.Major = 0
    in_reg.Minor = 1

    in_reg.RegisterCommand("gsx_capture_selected")
    in_reg.RegisterMenu(c.siMenuGSXID, "synoptic", False, False)

    return True


def XSIUnloadPlugin(in_reg):
    strPluginName = in_reg.Name
    Application.LogMessage(str(strPluginName) + str(" has been unloaded."))
    return True


###############################################################################
def synoptic_Init(ctxt):
    menu = ctxt.source
    util_menu = dynDispatch(menu.AddItem("synoptic", c.siMenuItemSubmenu))
    util_menu.AddCallBackItem("CaptureSelected", "gsx_capture_selected")


def gsx_capture_selected_Init(ctxt):
    cmd = ctxt.Source


def gsx_capture_selected_Execute(ctxt):
    # sort by object height
    #v = calc_cog_position(Application.Selection(0))
    x = sorted([x for x in Application.Selection],
        key=lambda x: calc_cog_global_position(x).y,
        reverse=True)

    # print results
    res = ""
    for hoge in x:
        res += "\n        - {name}: pos.y: {posy}".format(
            name=hoge.name, posy=str(calc_cog_global_position(hoge).y))

    log(res)
    capture_objects()


@OneUndo
def capture_objects(objects=None):
    if not objects:
        objects = Application.Selection

    if xsi.Capchan4:
        xsi.Capchan4()
        return

    store_vis = {}
    all = xsi.ActiveSceneRoot.FindChildren2("*", "","", True)
    for x in all:
        store_vis[x.ObjectID] = x.Properties("visibility").viewvis.Value
        x.Properties("visibility").viewvis.Value = False

    try:
        for o in objects:
            o.Properties("visibility").viewvis.Value = True

        sel = Application.Selection
        sel_str = sel.GetAsText()
        Application.DeselectAll()

        # capture
        xsi.CaptureViewport(2, 0)

    finally:
        # restroe
        for k, v in store_vis.iteritems():
            xsi.GetObjectFromID(k).Properties("visibility").viewvis.Value = v

    xsi.SelectObj(sel_str)


def calc_cog_global_position(obj):
    #x, y, z, b1, b2, b3 = Application.Selection(0).ActivePrimitive.Geometry.GetBoundingBox()
    #v = XSIMath.CreateVector3(x, y, z)
    if obj.ActivePrimitive.Geometry is not None:
        x = obj.ActivePrimitive.Geometry.Points
        v = XSIMath.CreateVector3()
        for p in x:
            v.Add(v, p.Position)
        v.Scale(1.0 / x.Count, v)
        res = XSIMath.MapObjectPositionToWorldSpace(
                obj.Kinematics.Global.Transform, v)

        return res

    else:
        t = obj.Kinematics.Global.Transform
        return XSIMath.CreateVector3(t.PosX, t.PosY, t.PosZ)
