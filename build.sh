#!/bin/sh
# buid the resource file and gui
pyrcc4 -py3 qtDesigner/resources.qrc -o resources_rc.py
py3uic4 qtDesigner/MainWindow.ui -o ui_MainWindow.py
