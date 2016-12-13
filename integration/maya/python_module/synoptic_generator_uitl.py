# -*- coding: utf-8 -*-

import maya.cmds as cmds


def cap(filename, width=300, height=550):
    cmds.playblast(
        filename=filename,
        viewer=False,
        showOrnaments=False,
        forceOverwrite=True,
        clearCache=True,
        percent=100,
        frame=0,
        format="image",
        compression="png",
        width=width,
        height=height
    )


def set_child_visibility(parent, flag):
    kids = cmds.listRelatives(parent, children=True)
    restore = []
    for kid in kids:
        if parent in kid:
            print "continue", kid
            continue

        if flag:
            print "show", kid
            cmds.showHidden(kid)
        else:
            print "hide", kid
            if cmds.getAttr("{}.visibility".format(kid)):
                restore.append(kid)
            cmds.hide(kid)

    return restore


def capture_selection(basedir, width, height):
    selection = cmds.ls(sl=True)
    cmds.select(clear=True)
    for s in selection:
        cmds.select(s)
        kids_restore = set_child_visibility(s, False)
        cmds.isolateSelect("modelPanel4", addSelected=True)
        cmds.isolateSelect("modelPanel4", update=True)
        cmds.isolateSelect("modelPanel4", state=1)
        cmds.select(clear=True)
        fname = "D:\\{}".format(s)
        cap(fname, width, height)
        cmds.showHidden(kids_restore)
        cmds.select(s)
        cmds.isolateSelect("modelPanel4", removeSelected=True)
        # cmds.select(clear=True)

    cmds.isolateSelect("modelPanel4", state=0)
    cmds.select(selection)


if __name__ == '__main__':
    capture_selection(r"D:\\", 300, 550)
