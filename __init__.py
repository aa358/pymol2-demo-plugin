'''
PyMOL Demo Plugin

The plugin resembles the old "Rendering Plugin" from Michael Lerner, which
was written with Tkinter instead of PyQt.

(c) Schrodinger, Inc.

License: BSD-2-Clause
'''

from __future__ import absolute_import
from __future__ import print_function

# Avoid importing "expensive" modules here (e.g. scipy), since this code is
# executed on PyMOL's startup. Only import such modules inside functions.

import os
import pymol

def set_bg_color(r, g, b):
    try:
        color = [int(r * 255), int(g * 255), int(b * 255)]
        pymol.cmd.set_color("custom_bg_color", color)
        pymol.cmd.bg_color("custom_bg_color")
    except pymol.CmdException as e:
        print(f"Error: {e}")

def __init_plugin__(app=None):
    '''
    Add an entry to the PyMOL "Plugin" menu
    '''
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('Demo "Render" Plugin', run_plugin_gui)


# global reference to avoid garbage collection of our dialog
dialog = None


def run_plugin_gui():
    '''
    Open our custom dialog
    '''
    global dialog

    if dialog is None:
        dialog = make_dialog()

    dialog.show()


def make_dialog():
    # entry point to PyMOL's API
    from pymol import cmd

    # pymol.Qt provides the PyQt5 interface, but may support PyQt4
    # and/or PySide as well
    from pymol.Qt import QtWidgets
    from pymol.Qt.utils import loadUi
    from pymol.Qt.utils import getSaveFileNameWithExt

    # create a new Window
    dialog = QtWidgets.QDialog()

    # populate the Window from our *.ui file which was created with the Qt Designer
    uifile = os.path.join(os.path.dirname(__file__), 'demowidget.ui')
    form = loadUi(uifile, dialog)

    # callback for the "Ray" button
    def run():
        # get form data
        height = form.input_height.value()
        width = form.input_width.value()
        dpi = form.input_dpi.value()
        filename = form.input_filename.text()
        units = form.input_units.currentText()

        # calculate dots per centimeter or inch
        if units == 'cm':
            dots_per_unit = dpi * 2.54
        else:
            dots_per_unit = dpi

        # convert image size to pixels
        width *= dots_per_unit
        height *= dots_per_unit

        # render the image
        if filename:
            cmd.png(filename, width, height, dpi=dpi, ray=1, quiet=0)
        else:
            cmd.ray(width, height, quiet=0)
            print('No filename selected, only rendering on display')

    # callback for the "Browse" button
    def browse_filename():
        filename = getSaveFileNameWithExt(
            dialog, 'Save As...', filter='PNG File (*.png)')
        if filename:
            form.input_filename.setText(filename)

    # callback for the "Set Background Color" button
    def set_background_color():
        r = form.input_bg_color_r.value() / 255.0
        g = form.input_bg_color_g.value() / 255.0
        b = form.input_bg_color_b.value() / 255.0
        set_bg_color(r, g, b)

    # hook up button callbacks
    form.button_ray.clicked.connect(run)
    form.button_browse.clicked.connect(browse_filename)
    form.button_set_bg_color.clicked.connect(set_background_color)
    form.button_close.clicked.connect(dialog.close)

    return dialog
