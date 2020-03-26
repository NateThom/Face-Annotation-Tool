#!/usr/bin/env python
"""
Facial landmark annotation tool

This program expects either a single image as an argument, or a directory
with many images, and a number n of images to be processed in that directory.
In this last case, names are sorted, and images at positions 0, floor(N/n),
floor(2N/n), ... floor((n - 1)N/n) are selected.

Output is to stdout and follows a csv format:
  'image_fname,' +
  'leye_x,leye_y,reye_x,reye_y,nose_x,nose_y, ' +
  'lmouth_x,lmouth_y,rmouth_x,rmouth_y,' +
  'rect_top_x,rect_top_y,rect_width,rect_height'

It is not necessary to annotate all points, and images can be skipped when
in multiple image mode.

Run without arguments for usage information.
"""
from __future__ import print_function
from __future__ import division
import os
import argparse
import warnings

import cv2
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
import matplotlib.cbook

warnings.filterwarnings('ignore', category=matplotlib.cbook.mplDeprecation)


def enum(**enums):
    return type('Enum', (), enums)


class InteractiveViewer(object):
    """
    InteractiveViewer - Class

    The InteractiveViewer class functions as the "driver" for the Face-Annotation-Tool. This class
    contains all of the variables related to labeling.

    Functions:
    __init__: Requires input of img_path, which is the path to the images that you wish to generate
    labels for. Also Initializes all variables to obvious starting values.

    redraw_annotations: Clones the current input image and displays current landmarks/bounding box for
    user's benefit. This function is used by: on_click, on_mouse_move, and button_event.

    update_button_labels: Updates the button label (in the UI). This function is only called when a button is
    clicked by the user. Currently, it resets the button name to default of "<BUTTON_LABEL>?". This function
    is used by: button_event and init_subplots.

    on_click: Is run when the user clicks their mouse. If the user's click is not within the display image
    then the functions returns without doing anything. Otherwise the function sets the InteractiveViewer state
    correctly and records the appropriate label based on current state.

    If the current state is GET_RECT, then the user must place their mouse within the input image, click, and
    hold. Then the "on_mouse_move" and "on_release" functions will be used to record the label and advance the
    program to its next state.

    Alternatively, if the current state is set to any other attribute state, then the user must place their
    mouse within the display and click the spot that they want to place the label. The state will be advanced.

    Used by: this function is called when the user clicks their mouse.

    on_release: Is run when the user releases their mouse button. If the current state is not GET_RECT
    or the mouse is outside of the input image, then this functions returns nothing. If the current state is
    GET_RECT, then the function records the user defined bounding box, updates the label display, and
    advances.

    Used by: this function is called when the user releases their mouse.

    on_key_press: This function records the keys pressed and sets the key_pressed event flag to True. Currently,
    this function is used to check if the user pressed the q key. If they do then the program immediately exits
    without saving.

    Used by: this function is called when the user presses a key on their keyboard.

    on_mouse_move: This function is called when the user moves their mouse. If the current state is not
    GET_RECT then the functions returns nothing, immediately. Otherwise, the position of the mouse is recorded
    for the bounding box label and the label display is updated.

    Used by: this function is called when the user moves the mouse.

    connect:

    button_event: Defines what should occur when a given button is clicked by the user.

    Used by: init_subplots

    init_subplots: Creates the display window and buttons.

    Used by: run

    save_annotations: Write the labels to stdout and output file.

    Used by: run

    run: Initializes the UI and runs the "connect" function. Then, continues looping pauses to allow the UI
    to update labels and the label display. Also manages exiting the program or skipping some image.
    """

    def __init__(self, img_path):

        self.img_path = img_path
        self.key_pressed = False
        self.key_event = None

        self.coords_list = [None for i in range(69)]
        self.coords_list[0] = [(0, 0), (0, 0)]

        # self.coords_1 = None
        # self.coords_2 = None
        # self.coords_3 = None
        # self.coords_4 = None
        # self.coords_5 = None

        self.image = cv2.imread(img_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.clone = self.image.copy()

        self.fig = None
        self.im_ax = None

        # self.button_rect = None

        self.button_list = [None for i in range(69)]

        # self.button_1 = None
        # self.button_2 = None
        # self.button_3 = None
        # self.button_4 = None
        # self.button_5 = None

        self.attr_state_counter = 1

        self.button_done = None
        self.button_skip = None

        self.is_finished = False
        self.is_skipped = False

        self.States = enum(GET_RECT=0,
                           GET_1=1,
                           GET_2=2,
                           GET_3=3,
                           GET_4=4,
                           GET_5=5,
                           GET_6=6,
                           GET_7=7,
                           GET_8=8,
                           GET_9=9,
                           GET_10=10,
                           GET_11=11,
                           GET_12=12,
                           GET_13=13,
                           GET_14=14,
                           GET_15=15,
                           GET_16=16,
                           GET_17=17,
                           GET_18=18,
                           GET_19=19,
                           GET_20=20,
                           GET_21=21,
                           GET_22=22,
                           GET_23=23,
                           GET_24=24,
                           GET_25=25,
                           GET_26=26,
                           GET_27=27,
                           GET_28=28,
                           GET_29=29,
                           GET_30=30,
                           GET_31=31,
                           GET_32=32,
                           GET_33=33,
                           GET_34=34,
                           GET_35=35,
                           GET_36=36,
                           GET_37=37,
                           GET_38=38,
                           GET_39=39,
                           GET_40=40,
                           GET_41=41,
                           GET_42=42,
                           GET_43=43,
                           GET_44=44,
                           GET_45=45,
                           GET_46=46,
                           GET_47=47,
                           GET_48=48,
                           GET_49=49,
                           GET_50=50,
                           GET_51=51,
                           GET_52=52,
                           GET_53=53,
                           GET_54=54,
                           GET_55=55,
                           GET_56=56,
                           GET_57=57,
                           GET_58=58,
                           GET_59=59,
                           GET_60=60,
                           GET_61=61,
                           GET_62=62,
                           GET_63=63,
                           GET_64=64,
                           GET_65=65,
                           GET_66=66,
                           GET_67=67,
                           GET_68=68)

        self.number_of_attributes = 68

        self.curr_state = eval(f"self.States.GET_{self.attr_state_counter}")

    def redraw_annotations(self):
        self.image = self.clone.copy()

        if self.coords_list[0] is not None:
            cv2.rectangle(self.image, self.coords_list[0][0], self.coords_list[0][1],
                          (0, 255, 0), 5)
        if self.coords_list[1] is not None:
            cv2.circle(self.image, self.coords_list[1], 1, (255, 0, 0), -1)
        if self.coords_list[2] is not None:
            cv2.circle(self.image, self.coords_list[2], 1, (255, 0, 0), -1)
        if self.coords_list[3] is not None:
            cv2.circle(self.image, self.coords_list[3], 1, (255, 0, 0), -1)
        if self.coords_list[4] is not None:
            cv2.circle(self.image, self.coords_list[4], 1, (255, 0, 0), -1)
        if self.coords_list[5] is not None:
            cv2.circle(self.image, self.coords_list[5], 1, (255, 0, 0), -1)
        if self.coords_list[6] is not None:
            cv2.circle(self.image, self.coords_list[6], 1, (255, 0, 0), -1)
        if self.coords_list[7] is not None:
            cv2.circle(self.image, self.coords_list[7], 1, (255, 0, 0), -1)
        if self.coords_list[8] is not None:
            cv2.circle(self.image, self.coords_list[8], 1, (255, 0, 0), -1)
        if self.coords_list[9] is not None:
            cv2.circle(self.image, self.coords_list[9], 1, (255, 0, 0), -1)
        if self.coords_list[10] is not None:
            cv2.circle(self.image, self.coords_list[10], 1, (255, 0, 0), -1)
        if self.coords_list[11] is not None:
            cv2.circle(self.image, self.coords_list[11], 1, (255, 0, 0), -1)
        if self.coords_list[12] is not None:
            cv2.circle(self.image, self.coords_list[12], 1, (255, 0, 0), -1)
        if self.coords_list[13] is not None:
            cv2.circle(self.image, self.coords_list[13], 1, (255, 0, 0), -1)
        if self.coords_list[14] is not None:
            cv2.circle(self.image, self.coords_list[14], 1, (255, 0, 0), -1)
        if self.coords_list[15] is not None:
            cv2.circle(self.image, self.coords_list[15], 1, (255, 0, 0), -1)
        if self.coords_list[16] is not None:
            cv2.circle(self.image, self.coords_list[16], 1, (255, 0, 0), -1)
        if self.coords_list[17] is not None:
            cv2.circle(self.image, self.coords_list[17], 1, (255, 0, 0), -1)
        if self.coords_list[18] is not None:
            cv2.circle(self.image, self.coords_list[18], 1, (255, 0, 0), -1)
        if self.coords_list[19] is not None:
            cv2.circle(self.image, self.coords_list[19], 1, (255, 0, 0), -1)
        if self.coords_list[20] is not None:
            cv2.circle(self.image, self.coords_list[20], 1, (255, 0, 0), -1)
        if self.coords_list[21] is not None:
            cv2.circle(self.image, self.coords_list[21], 1, (255, 0, 0), -1)
        if self.coords_list[22] is not None:
            cv2.circle(self.image, self.coords_list[22], 1, (255, 0, 0), -1)
        if self.coords_list[23] is not None:
            cv2.circle(self.image, self.coords_list[23], 1, (255, 0, 0), -1)
        if self.coords_list[24] is not None:
            cv2.circle(self.image, self.coords_list[24], 1, (255, 0, 0), -1)
        if self.coords_list[25] is not None:
            cv2.circle(self.image, self.coords_list[25], 1, (255, 0, 0), -1)
        if self.coords_list[26] is not None:
            cv2.circle(self.image, self.coords_list[26], 1, (255, 0, 0), -1)
        if self.coords_list[27] is not None:
            cv2.circle(self.image, self.coords_list[27], 1, (255, 0, 0), -1)
        if self.coords_list[28]is not None:
            cv2.circle(self.image, self.coords_list[28], 1, (255, 0, 0), -1)
        if self.coords_list[29] is not None:
            cv2.circle(self.image, self.coords_list[29], 1, (255, 0, 0), -1)
        if self.coords_list[30] is not None:
            cv2.circle(self.image, self.coords_list[30], 1, (255, 0, 0), -1)
        if self.coords_list[31] is not None:
            cv2.circle(self.image, self.coords_list[31], 1, (255, 0, 0), -1)
        if self.coords_list[32] is not None:
            cv2.circle(self.image, self.coords_list[32], 1, (255, 0, 0), -1)
        if self.coords_list[33] is not None:
            cv2.circle(self.image, self.coords_list[33], 1, (255, 0, 0), -1)
        if self.coords_list[34] is not None:
            cv2.circle(self.image, self.coords_list[34], 1, (255, 0, 0), -1)
        if self.coords_list[35] is not None:
            cv2.circle(self.image, self.coords_list[35], 1, (255, 0, 0), -1)
        if self.coords_list[36] is not None:
            cv2.circle(self.image, self.coords_list[36], 1, (255, 0, 0), -1)
        if self.coords_list[37] is not None:
            cv2.circle(self.image, self.coords_list[37], 1, (255, 0, 0), -1)
        if self.coords_list[38] is not None:
            cv2.circle(self.image, self.coords_list[38], 1, (255, 0, 0), -1)
        if self.coords_list[39] is not None:
            cv2.circle(self.image, self.coords_list[39], 1, (255, 0, 0), -1)
        if self.coords_list[40] is not None:
            cv2.circle(self.image, self.coords_list[40], 1, (255, 0, 0), -1)
        if self.coords_list[41] is not None:
            cv2.circle(self.image, self.coords_list[41], 1, (255, 0, 0), -1)
        if self.coords_list[42] is not None:
            cv2.circle(self.image, self.coords_list[42], 1, (255, 0, 0), -1)
        if self.coords_list[43] is not None:
            cv2.circle(self.image, self.coords_list[43], 1, (255, 0, 0), -1)
        if self.coords_list[44] is not None:
            cv2.circle(self.image, self.coords_list[44], 1, (255, 0, 0), -1)
        if self.coords_list[45] is not None:
            cv2.circle(self.image, self.coords_list[45], 1, (255, 0, 0), -1)
        if self.coords_list[46] is not None:
            cv2.circle(self.image, self.coords_list[46], 1, (255, 0, 0), -1)
        if self.coords_list[47] is not None:
            cv2.circle(self.image, self.coords_list[47], 1, (255, 0, 0), -1)
        if self.coords_list[48] is not None:
            cv2.circle(self.image, self.coords_list[48], 1, (255, 0, 0), -1)
        if self.coords_list[49] is not None:
            cv2.circle(self.image, self.coords_list[49], 1, (255, 0, 0), -1)
        if self.coords_list[50] is not None:
            cv2.circle(self.image, self.coords_list[50], 1, (255, 0, 0), -1)
        if self.coords_list[51] is not None:
            cv2.circle(self.image, self.coords_list[51], 1, (255, 0, 0), -1)
        if self.coords_list[52] is not None:
            cv2.circle(self.image, self.coords_list[52], 1, (255, 0, 0), -1)
        if self.coords_list[53] is not None:
            cv2.circle(self.image, self.coords_list[53], 1, (255, 0, 0), -1)
        if self.coords_list[54] is not None:
            cv2.circle(self.image, self.coords_list[54], 1, (255, 0, 0), -1)
        if self.coords_list[55] is not None:
            cv2.circle(self.image, self.coords_list[55], 1, (255, 0, 0), -1)
        if self.coords_list[56] is not None:
            cv2.circle(self.image, self.coords_list[56], 1, (255, 0, 0), -1)
        if self.coords_list[57] is not None:
            cv2.circle(self.image, self.coords_list[57], 1, (255, 0, 0), -1)
        if self.coords_list[58] is not None:
            cv2.circle(self.image, self.coords_list[58], 1, (255, 0, 0), -1)
        if self.coords_list[59] is not None:
            cv2.circle(self.image, self.coords_list[59], 1, (255, 0, 0), -1)
        if self.coords_list[60] is not None:
            cv2.circle(self.image, self.coords_list[60], 1, (255, 0, 0), -1)
        if self.coords_list[61] is not None:
            cv2.circle(self.image, self.coords_list[61], 1, (255, 0, 0), -1)
        if self.coords_list[62] is not None:
            cv2.circle(self.image, self.coords_list[62], 1, (255, 0, 0), -1)
        if self.coords_list[63] is not None:
            cv2.circle(self.image, self.coords_list[63], 1, (255, 0, 0), -1)
        if self.coords_list[64] is not None:
            cv2.circle(self.image, self.coords_list[64], 1, (255, 0, 0), -1)
        if self.coords_list[65] is not None:
            cv2.circle(self.image, self.coords_list[65], 1, (255, 0, 0), -1)
        if self.coords_list[66] is not None:
            cv2.circle(self.image, self.coords_list[66], 1, (255, 0, 0), -1)
        if self.coords_list[67] is not None:
            cv2.circle(self.image, self.coords_list[67], 1, (255, 0, 0), -1)
        if self.coords_list[68] is not None:
            cv2.circle(self.image, self.coords_list[68], 1, (255, 0, 0), -1)

        self.im_ax.imshow(self.image)

    def update_button_labels(self):
        if self.curr_state == self.States.GET_RECT:
            self.button_list[0].label.set_text('Rect?')
        else:
            eval(f"self.button_list[{self.attr_state_counter}].label.set_text('{self.attr_state_counter}?')")

    def on_click(self, event):
        if event.inaxes != self.im_ax:
            return

        if self.curr_state == self.States.GET_RECT:
            self.coords_list[0][0] = (int(event.xdata), int(event.ydata))
        else:
            self.curr_state = eval(f"self.States.GET_{self.attr_state_counter}")
            exec(f"self.coords_list[{self.attr_state_counter}] = (int(event.xdata), int(event.ydata))")
            eval(f"self.button_list[{self.attr_state_counter}].label.set_text(str(self.attr_state_counter))")
            if self.attr_state_counter < self.number_of_attributes:
                self.attr_state_counter = self.attr_state_counter + 1
            else:
                self.attr_state_counter = 1

        self.redraw_annotations()

    def on_release(self, event):
        if event.inaxes != self.im_ax:
            return

        if self.curr_state == self.States.GET_RECT:
            self.coords_list[0][1] = (int(event.xdata), int(event.ydata))

            cv2.rectangle(self.image, self.coords_list[0][0],
                          self.coords_list[0][1],
                          (0, 255, 0), 5)

            self.button_list[0].label.set_text('Rect')

            self.im_ax.imshow(self.image)

            self.attr_state_counter = 1
            self.curr_state = eval(f"self.States.GET_{self.attr_state_counter}")

    def on_key_press(self, event):
        self.key_event = event
        self.key_pressed = True

    def on_mouse_move(self, event):
        if self.curr_state != self.States.GET_RECT or event.inaxes != self.im_ax:
            return
        else:
            self.coords_list[0][1] = (int(event.xdata), int(event.ydata))
            self.redraw_annotations()

    def connect(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def button_event(self, event):
        self.key_pressed = False

        if event.inaxes == self.button_list[1].ax:
            self.coords_list[1] = None
            self.attr_state_counter = 1
            self.curr_state = self.States.GET_1

        elif event.inaxes == self.button_list[2].ax:
            self.coords_list[2] = None
            self.attr_state_counter = 2
            self.curr_state = self.States.GET_2

        elif event.inaxes == self.button_list[3].ax:
            self.coords_list[3] = None
            self.attr_state_counter = 3
            self.curr_state = self.States.GET_3

        elif event.inaxes == self.button_list[4].ax:
            self.coords_list[4] = None
            self.attr_state_counter = 4
            self.curr_state = self.States.GET_4

        elif event.inaxes == self.button_list[5].ax:
            self.coords_list[5] = None
            self.attr_state_counter = 5
            self.curr_state = self.States.GET_5

        elif event.inaxes == self.button_list[6].ax:
            self.coords_list[6] = None
            self.attr_state_counter = 6
            self.curr_state = self.States.GET_6

        elif event.inaxes == self.button_list[7].ax:
            self.coords_list[7] = None
            self.attr_state_counter = 7
            self.curr_state = self.States.GET_7

        elif event.inaxes == self.button_list[8].ax:
            self.coords_list[8] = None
            self.attr_state_counter = 8
            self.curr_state = self.States.GET_8

        elif event.inaxes == self.button_list[9].ax:
            self.coords_list[9] = None
            self.attr_state_counter = 9
            self.curr_state = self.States.GET_9

        elif event.inaxes == self.button_list[10].ax:
            self.coords_list[10] = None
            self.attr_state_counter = 10
            self.curr_state = self.States.GET_10

        elif event.inaxes == self.button_list[11].ax:
            self.coords_list[11] = None
            self.attr_state_counter = 11
            self.curr_state = self.States.GET_11

        elif event.inaxes == self.button_list[12].ax:
            self.coords_list[12] = None
            self.attr_state_counter = 12
            self.curr_state = self.States.GET_12

        elif event.inaxes == self.button_list[13].ax:
            self.coords_list[13] = None
            self.attr_state_counter = 13
            self.curr_state = self.States.GET_13

        elif event.inaxes == self.button_list[14].ax:
            self.coords_list[14] = None
            self.attr_state_counter = 14
            self.curr_state = self.States.GET_14

        elif event.inaxes == self.button_list[15].ax:
            self.coords_list[15] = None
            self.attr_state_counter = 15
            self.curr_state = self.States.GET_15

        elif event.inaxes == self.button_list[16].ax:
            self.coords_list[16] = None
            self.attr_state_counter = 16
            self.curr_state = self.States.GET_16

        elif event.inaxes == self.button_list[17].ax:
            self.coords_list[17] = None
            self.attr_state_counter = 17
            self.curr_state = self.States.GET_17

        elif event.inaxes == self.button_list[18].ax:
            self.coords_list[18] = None
            self.attr_state_counter = 18
            self.curr_state = self.States.GET_18

        elif event.inaxes == self.button_list[19].ax:
            self.coords_list[19] = None
            self.attr_state_counter = 19
            self.curr_state = self.States.GET_19

        elif event.inaxes == self.button_list[20].ax:
            self.coords_list[20] = None
            self.attr_state_counter = 20
            self.curr_state = self.States.GET_20

        elif event.inaxes == self.button_list[21].ax:
            self.coords_list[21] = None
            self.attr_state_counter = 21
            self.curr_state = self.States.GET_21

        elif event.inaxes == self.button_list[22].ax:
            self.coords_list[22] = None
            self.attr_state_counter = 22
            self.curr_state = self.States.GET_22

        elif event.inaxes == self.button_list[23].ax:
            self.coords_list[23] = None
            self.attr_state_counter = 23
            self.curr_state = self.States.GET_23

        elif event.inaxes == self.button_list[24].ax:
            self.coords_list[24] = None
            self.attr_state_counter = 24
            self.curr_state = self.States.GET_24

        elif event.inaxes == self.button_list[25].ax:
            self.coords_list[25] = None
            self.attr_state_counter = 25
            self.curr_state = self.States.GET_25

        elif event.inaxes == self.button_list[26].ax:
            self.coords_list[26] = None
            self.attr_state_counter = 26
            self.curr_state = self.States.GET_26

        elif event.inaxes == self.button_list[27].ax:
            self.coords_list[27] = None
            self.attr_state_counter = 27
            self.curr_state = self.States.GET_27

        elif event.inaxes == self.button_list[28].ax:
            self.coords_list[28] = None
            self.attr_state_counter = 28
            self.curr_state = self.States.GET_28

        elif event.inaxes == self.button_list[29].ax:
            self.coords_list[29] = None
            self.attr_state_counter = 29
            self.curr_state = self.States.GET_29

        elif event.inaxes == self.button_list[30].ax:
            self.coords_list[30] = None
            self.attr_state_counter = 30
            self.curr_state = self.States.GET_30

        elif event.inaxes == self.button_list[31].ax:
            self.coords_list[31] = None
            self.attr_state_counter = 31
            self.curr_state = self.States.GET_31

        elif event.inaxes == self.button_list[32].ax:
            self.coords_list[32] = None
            self.attr_state_counter = 32
            self.curr_state = self.States.GET_32

        elif event.inaxes == self.button_list[33].ax:
            self.coords_list[33] = None
            self.attr_state_counter = 33
            self.curr_state = self.States.GET_33

        elif event.inaxes == self.button_list[34].ax:
            self.coords_list[34] = None
            self.attr_state_counter = 34
            self.curr_state = self.States.GET_34

        elif event.inaxes == self.button_list[35].ax:
            self.coords_list[35] = None
            self.attr_state_counter = 35
            self.curr_state = self.States.GET_35

        elif event.inaxes == self.button_list[36].ax:
            self.coords_list[36] = None
            self.attr_state_counter = 36
            self.curr_state = self.States.GET_36

        elif event.inaxes == self.button_list[37].ax:
            self.coords_list[37] = None
            self.attr_state_counter = 37
            self.curr_state = self.States.GET_37

        elif event.inaxes == self.button_list[38].ax:
            self.coords_list[38] = None
            self.attr_state_counter = 38
            self.curr_state = self.States.GET_38

        elif event.inaxes == self.button_list[39].ax:
            self.coords_list[39] = None
            self.attr_state_counter = 39
            self.curr_state = self.States.GET_39

        elif event.inaxes == self.button_list[40].ax:
            self.coords_list[40] = None
            self.attr_state_counter = 40
            self.curr_state = self.States.GET_40

        elif event.inaxes == self.button_list[41].ax:
            self.coords_list[41] = None
            self.attr_state_counter = 41
            self.curr_state = self.States.GET_41

        elif event.inaxes == self.button_list[42].ax:
            self.coords_list[42] = None
            self.attr_state_counter = 42
            self.curr_state = self.States.GET_42

        elif event.inaxes == self.button_list[43].ax:
            self.coords_list[43] = None
            self.attr_state_counter = 43
            self.curr_state = self.States.GET_43

        elif event.inaxes == self.button_list[44].ax:
            self.coords_list[44] = None
            self.attr_state_counter = 44
            self.curr_state = self.States.GET_44

        elif event.inaxes == self.button_list[45].ax:
            self.coords_list[45] = None
            self.attr_state_counter = 45
            self.curr_state = self.States.GET_45

        elif event.inaxes == self.button_list[46].ax:
            self.coords_list[46] = None
            self.attr_state_counter = 46
            self.curr_state = self.States.GET_46

        elif event.inaxes == self.button_list[47].ax:
            self.coords_list[47] = None
            self.attr_state_counter = 47
            self.curr_state = self.States.GET_47

        elif event.inaxes == self.button_list[48].ax:
            self.coords_list[48] = None
            self.attr_state_counter = 48
            self.curr_state = self.States.GET_48

        elif event.inaxes == self.button_list[49].ax:
            self.coords_list[49] = None
            self.attr_state_counter = 49
            self.curr_state = self.States.GET_49

        elif event.inaxes == self.button_list[50].ax:
            self.coords_list[50] = None
            self.attr_state_counter = 50
            self.curr_state = self.States.GET_50

        elif event.inaxes == self.button_list[51].ax:
            self.coords_list[51] = None
            self.attr_state_counter = 51
            self.curr_state = self.States.GET_51

        elif event.inaxes == self.button_list[52].ax:
            self.coords_list[52] = None
            self.attr_state_counter = 52
            self.curr_state = self.States.GET_52

        elif event.inaxes == self.button_list[53].ax:
            self.coords_list[53] = None
            self.attr_state_counter = 53
            self.curr_state = self.States.GET_53

        elif event.inaxes == self.button_list[54].ax:
            self.coords_list[54] = None
            self.attr_state_counter = 54
            self.curr_state = self.States.GET_54

        elif event.inaxes == self.button_list[55].ax:
            self.coords_list[55] = None
            self.attr_state_counter = 55
            self.curr_state = self.States.GET_55

        elif event.inaxes == self.button_list[56].ax:
            self.coords_list[56] = None
            self.attr_state_counter = 56
            self.curr_state = self.States.GET_56

        elif event.inaxes == self.button_list[57].ax:
            self.coords_list[57] = None
            self.attr_state_counter = 57
            self.curr_state = self.States.GET_57

        elif event.inaxes == self.button_list[58].ax:
            self.coords_list[58] = None
            self.attr_state_counter = 58
            self.curr_state = self.States.GET_58

        elif event.inaxes == self.button_list[59].ax:
            self.coords_list[59] = None
            self.attr_state_counter = 59
            self.curr_state = self.States.GET_59

        elif event.inaxes == self.button_list[60].ax:
            self.coords_list[60] = None
            self.attr_state_counter = 60
            self.curr_state = self.States.GET_60

        elif event.inaxes == self.button_list[61].ax:
            self.coords_list[61] = None
            self.attr_state_counter = 61
            self.curr_state = self.States.GET_61

        elif event.inaxes == self.button_list[62].ax:
            self.coords_list[62] = None
            self.attr_state_counter = 62
            self.curr_state = self.States.GET_62

        elif event.inaxes == self.button_list[63].ax:
            self.coords_list[63] = None
            self.attr_state_counter = 63
            self.curr_state = self.States.GET_63

        elif event.inaxes == self.button_list[64].ax:
            self.coords_list[64] = None
            self.attr_state_counter = 64
            self.curr_state = self.States.GET_64

        elif event.inaxes == self.button_list[65].ax:
            self.coords_list[65] = None
            self.attr_state_counter = 65
            self.curr_state = self.States.GET_65

        elif event.inaxes == self.button_list[66].ax:
            self.coords_list[66] = None
            self.attr_state_counter = 66
            self.curr_state = self.States.GET_66

        elif event.inaxes == self.button_list[67].ax:
            self.coords_list[67] = None
            self.attr_state_counter = 67
            self.curr_state = self.States.GET_67

        elif event.inaxes == self.button_list[68].ax:
            self.coords_list[68] = None
            self.attr_state_counter = 68
            self.curr_state = self.States.GET_68

        elif event.inaxes == self.button_done.ax:
            self.is_finished = True

        elif event.inaxes == self.button_skip.ax:
            self.is_skipped = True

        elif event.inaxes == self.button_list[0].ax:
            self.coords_list[0] = [(0, 0), (0, 0)]
            self.curr_state = self.States.GET_RECT

        self.redraw_annotations()
        self.update_button_labels()

    def init_subplots(self):
        self.fig = plt.figure(os.path.basename(self.img_path))

        self.im_ax = self.fig.add_subplot(1, 2, 1)
        self.im_ax.set_title('Input')
        self.im_ax.imshow(self.image, interpolation='nearest')

        self.button_list[0] = Button(plt.axes([0.5, 0.82, 0.06, 0.06]), 'Rect?')

        self.button_list[0].on_clicked(self.button_event)

        self.button_list[1] = Button(plt.axes([0.5, 0.75, 0.06, 0.06]),
                               '1?')
        self.button_list[1].on_clicked(self.button_event)

        self.button_list[2] = Button(plt.axes([0.5, 0.68, 0.06, 0.06]),
                               '2?')
        self.button_list[2].on_clicked(self.button_event)

        self.button_list[3] = Button(plt.axes([0.5, 0.61, 0.06, 0.06]),
                               '3?')
        self.button_list[3].on_clicked(self.button_event)

        self.button_list[4] = Button(plt.axes([0.5, 0.54, 0.06, 0.06]),
                               '4?')
        self.button_list[4].on_clicked(self.button_event)

        self.button_list[5] = Button(plt.axes([0.5, 0.47, 0.06, 0.06]),
                               '5?')
        self.button_list[5].on_clicked(self.button_event)

        self.button_list[6] = Button(plt.axes([0.5, 0.40, 0.06, 0.06]),
                               '6?')
        self.button_list[6].on_clicked(self.button_event)

        self.button_list[7] = Button(plt.axes([0.5, 0.33, 0.06, 0.06]),
                               '7?')
        self.button_list[7].on_clicked(self.button_event)

        self.button_list[8] = Button(plt.axes([0.5, 0.26, 0.06, 0.06]),
                               '8?')
        self.button_list[8].on_clicked(self.button_event)

        self.button_list[9] = Button(plt.axes([0.5, 0.19, 0.06, 0.06]),
                               '9?')
        self.button_list[9].on_clicked(self.button_event)

        self.button_list[10] = Button(plt.axes([0.57, 0.82, 0.06, 0.06]),
                                '10?')
        self.button_list[10].on_clicked(self.button_event)

        self.button_list[11] = Button(plt.axes([0.57, 0.75, 0.06, 0.06]),
                                '11?')
        self.button_list[11].on_clicked(self.button_event)

        self.button_list[12] = Button(plt.axes([0.57, 0.68, 0.06, 0.06]),
                                '12?')
        self.button_list[12].on_clicked(self.button_event)

        self.button_list[13] = Button(plt.axes([0.57, 0.61, 0.06, 0.06]),
                                '13?')
        self.button_list[13].on_clicked(self.button_event)

        self.button_list[14] = Button(plt.axes([0.57, 0.54, 0.06, 0.06]),
                                '14?')
        self.button_list[14].on_clicked(self.button_event)

        self.button_list[15] = Button(plt.axes([0.57, 0.47, 0.06, 0.06]),
                                '15?')
        self.button_list[15].on_clicked(self.button_event)

        self.button_list[16] = Button(plt.axes([0.57, 0.40, 0.06, 0.06]),
                                '16?')
        self.button_list[16].on_clicked(self.button_event)

        self.button_list[17] = Button(plt.axes([0.57, 0.33, 0.06, 0.06]),
                                '17?')
        self.button_list[17].on_clicked(self.button_event)

        self.button_list[18] = Button(plt.axes([0.57, 0.26, 0.06, 0.06]),
                                '18?')
        self.button_list[18].on_clicked(self.button_event)

        self.button_list[19] = Button(plt.axes([0.57, 0.19, 0.06, 0.06]),
                                '19?')
        self.button_list[19].on_clicked(self.button_event)

        self.button_list[20] = Button(plt.axes([0.64, 0.82, 0.06, 0.06]),
                                '20?')
        self.button_list[20].on_clicked(self.button_event)

        self.button_list[21] = Button(plt.axes([0.64, 0.75, 0.06, 0.06]),
                                '21?')
        self.button_list[21].on_clicked(self.button_event)

        self.button_list[22] = Button(plt.axes([0.64, 0.68, 0.06, 0.06]),
                                '22?')
        self.button_list[22].on_clicked(self.button_event)

        self.button_list[23] = Button(plt.axes([0.64, 0.61, 0.06, 0.06]),
                                '23?')
        self.button_list[23].on_clicked(self.button_event)

        self.button_list[24] = Button(plt.axes([0.64, 0.54, 0.06, 0.06]),
                                '24?')
        self.button_list[24].on_clicked(self.button_event)

        self.button_list[25] = Button(plt.axes([0.64, 0.47, 0.06, 0.06]),
                                '25?')
        self.button_list[25].on_clicked(self.button_event)

        self.button_list[26] = Button(plt.axes([0.64, 0.40, 0.06, 0.06]),
                                '26?')
        self.button_list[26].on_clicked(self.button_event)

        self.button_list[27] = Button(plt.axes([0.64, 0.33, 0.06, 0.06]),
                                '27?')
        self.button_list[27].on_clicked(self.button_event)

        self.button_list[28] = Button(plt.axes([0.64, 0.26, 0.06, 0.06]),
                                '28?')
        self.button_list[28].on_clicked(self.button_event)

        self.button_list[29] = Button(plt.axes([0.64, 0.19, 0.06, 0.06]),
                                '29?')
        self.button_list[29].on_clicked(self.button_event)

        self.button_list[30] = Button(plt.axes([0.71, 0.82, 0.06, 0.06]),
                                '30?')
        self.button_list[30].on_clicked(self.button_event)

        self.button_list[31] = Button(plt.axes([0.71, 0.75, 0.06, 0.06]),
                                '31?')
        self.button_list[31].on_clicked(self.button_event)

        self.button_list[32] = Button(plt.axes([0.71, 0.68, 0.06, 0.06]),
                                '32?')
        self.button_list[32].on_clicked(self.button_event)

        self.button_list[33] = Button(plt.axes([0.71, 0.61, 0.06, 0.06]),
                                '33?')
        self.button_list[33].on_clicked(self.button_event)

        self.button_list[34] = Button(plt.axes([0.71, 0.54, 0.06, 0.06]),
                                '34?')
        self.button_list[34].on_clicked(self.button_event)

        self.button_list[35] = Button(plt.axes([0.71, 0.47, 0.06, 0.06]),
                                '35?')
        self.button_list[35].on_clicked(self.button_event)

        self.button_list[36] = Button(plt.axes([0.71, 0.40, 0.06, 0.06]),
                                '36?')
        self.button_list[36].on_clicked(self.button_event)

        self.button_list[37] = Button(plt.axes([0.71, 0.33, 0.06, 0.06]),
                                '37?')
        self.button_list[37].on_clicked(self.button_event)

        self.button_list[38] = Button(plt.axes([0.71, 0.26, 0.06, 0.06]),
                                '38?')
        self.button_list[38].on_clicked(self.button_event)

        self.button_list[39] = Button(plt.axes([0.71, 0.19, 0.06, 0.06]),
                                '39?')
        self.button_list[39].on_clicked(self.button_event)

        self.button_list[40] = Button(plt.axes([0.78, 0.82, 0.06, 0.06]),
                                '40?')
        self.button_list[40].on_clicked(self.button_event)

        self.button_list[41] = Button(plt.axes([0.78, 0.75, 0.06, 0.06]),
                                '41?')
        self.button_list[41].on_clicked(self.button_event)

        self.button_list[42] = Button(plt.axes([0.78, 0.68, 0.06, 0.06]),
                                '42?')
        self.button_list[42].on_clicked(self.button_event)

        self.button_list[43] = Button(plt.axes([0.78, 0.61, 0.06, 0.06]),
                                '43?')
        self.button_list[43].on_clicked(self.button_event)

        self.button_list[44] = Button(plt.axes([0.78, 0.54, 0.06, 0.06]),
                                '44?')
        self.button_list[44].on_clicked(self.button_event)

        self.button_list[45] = Button(plt.axes([0.78, 0.47, 0.06, 0.06]),
                                '45?')
        self.button_list[45].on_clicked(self.button_event)

        self.button_list[46] = Button(plt.axes([0.78, 0.40, 0.06, 0.06]),
                                '46?')
        self.button_list[46].on_clicked(self.button_event)

        self.button_list[47] = Button(plt.axes([0.78, 0.33, 0.06, 0.06]),
                                '47?')
        self.button_list[47].on_clicked(self.button_event)

        self.button_list[48] = Button(plt.axes([0.78, 0.26, 0.06, 0.06]),
                                '48?')
        self.button_list[48].on_clicked(self.button_event)

        self.button_list[49] = Button(plt.axes([0.78, 0.19, 0.06, 0.06]),
                                '49?')
        self.button_list[49].on_clicked(self.button_event)

        self.button_list[50] = Button(plt.axes([0.85, 0.82, 0.06, 0.06]),
                                '50?')
        self.button_list[50].on_clicked(self.button_event)

        self.button_list[51] = Button(plt.axes([0.85, 0.75, 0.06, 0.06]),
                                '51?')
        self.button_list[51].on_clicked(self.button_event)

        self.button_list[52] = Button(plt.axes([0.85, 0.68, 0.06, 0.06]),
                                '52?')
        self.button_list[52].on_clicked(self.button_event)

        self.button_list[53] = Button(plt.axes([0.85, 0.61, 0.06, 0.06]),
                                '53?')
        self.button_list[53].on_clicked(self.button_event)

        self.button_list[54] = Button(plt.axes([0.85, 0.54, 0.06, 0.06]),
                                '54?')
        self.button_list[54].on_clicked(self.button_event)

        self.button_list[55] = Button(plt.axes([0.85, 0.47, 0.06, 0.06]),
                                '55?')
        self.button_list[55].on_clicked(self.button_event)

        self.button_list[56] = Button(plt.axes([0.85, 0.40, 0.06, 0.06]),
                                '56?')
        self.button_list[56].on_clicked(self.button_event)

        self.button_list[57] = Button(plt.axes([0.85, 0.33, 0.06, 0.06]),
                                '57?')
        self.button_list[57].on_clicked(self.button_event)

        self.button_list[58] = Button(plt.axes([0.85, 0.26, 0.06, 0.06]),
                                '58?')
        self.button_list[58].on_clicked(self.button_event)

        self.button_list[59] = Button(plt.axes([0.85, 0.19, 0.06, 0.06]),
                                '59?')
        self.button_list[59].on_clicked(self.button_event)

        self.button_list[60] = Button(plt.axes([0.92, 0.82, 0.06, 0.06]),
                                '60?')
        self.button_list[60].on_clicked(self.button_event)

        self.button_list[61] = Button(plt.axes([0.92, 0.75, 0.06, 0.06]),
                                '61?')
        self.button_list[61].on_clicked(self.button_event)

        self.button_list[62] = Button(plt.axes([0.92, 0.68, 0.06, 0.06]),
                                '62?')
        self.button_list[62].on_clicked(self.button_event)

        self.button_list[63] = Button(plt.axes([0.92, 0.61, 0.06, 0.06]),
                                '63?')
        self.button_list[63].on_clicked(self.button_event)

        self.button_list[64] = Button(plt.axes([0.92, 0.54, 0.06, 0.06]),
                                '64?')
        self.button_list[64].on_clicked(self.button_event)

        self.button_list[65] = Button(plt.axes([0.92, 0.47, 0.06, 0.06]),
                                '65?')
        self.button_list[65].on_clicked(self.button_event)

        self.button_list[66] = Button(plt.axes([0.92, 0.40, 0.06, 0.06]),
                                '66?')
        self.button_list[66].on_clicked(self.button_event)

        self.button_list[67] = Button(plt.axes([0.92, 0.33, 0.06, 0.06]),
                                '67?')
        self.button_list[67].on_clicked(self.button_event)

        self.button_list[68] = Button(plt.axes([0.92, 0.26, 0.06, 0.06]),
                                '68?')
        self.button_list[68].on_clicked(self.button_event)

        self.button_done = Button(plt.axes([0.5, 0.13, 0.45, 0.05]),
                                  'Done')
        self.button_done.on_clicked(self.button_event)

        self.button_skip = Button(plt.axes([0.5, 0.07, 0.45, 0.05]),
                                  'Skip')
        self.button_skip.on_clicked(self.button_event)

        self.update_button_labels()

    def save_annotations(self):

        print('image_name,x_0,x_1,x_2,x_3,x_4,x_5,x_6,x_7,x_8,x_9,x_10,x_11,x_12,'
              'x_13,x_14,x_15,x_16,x_17,x_18,x_19,x_20,x_21,x_22,x_23,x_24,'
              'x_25,x_26,x_27,x_28,x_29,x_30,x_31,x_32,x_33,x_34,x_35,x_36,'
              'x_37,x_38,x_39,x_40,x_41,x_42,x_43,x_44,x_45,x_46,x_47,x_48,'
              'x_49,x_50,x_51,x_52,x_53,x_54,x_55,x_56,x_57,x_58,x_59,x_60,'
              'x_61,x_62,x_63,x_64,x_65,x_66,x_67,y_0,y_1,y_2,y_3,y_4,'
              'y_5,y_6,y_7,y_8,y_9,y_10,y_11,y_12,y_13,y_14,y_15,y_16,'
              'y_17,y_18,y_19,y_20,y_21,y_22,y_23,y_24,y_25,y_26,y_27,'
              'y_28,y_29,y_30,y_31,y_32,y_33,y_34,y_35,y_36,y_37,y_38,'
              'y_39,y_40,y_41,y_42,y_43,y_44,y_45,y_46,y_47,y_48,y_49,'
              'y_50,y_51,y_52,y_53,y_54,y_55,y_56,y_57,y_58,y_59,y_60,'
              'y_61,y_62,y_63,y_64,y_65,y_66,y_67')

        f_winner.write('image_name,x_0,x_1,x_2,x_3,x_4,x_5,x_6,x_7,x_8,x_9,x_10,x_11,x_12,'
              'x_13,x_14,x_15,x_16,x_17,x_18,x_19,x_20,x_21,x_22,x_23,x_24,'
              'x_25,x_26,x_27,x_28,x_29,x_30,x_31,x_32,x_33,x_34,x_35,x_36,'
              'x_37,x_38,x_39,x_40,x_41,x_42,x_43,x_44,x_45,x_46,x_47,x_48,'
              'x_49,x_50,x_51,x_52,x_53,x_54,x_55,x_56,x_57,x_58,x_59,x_60,'
              'x_61,x_62,x_63,x_64,x_65,x_66,x_67,y_0,y_1,y_2,y_3,y_4,'
              'y_5,y_6,y_7,y_8,y_9,y_10,y_11,y_12,y_13,y_14,y_15,y_16,'
              'y_17,y_18,y_19,y_20,y_21,y_22,y_23,y_24,y_25,y_26,y_27,'
              'y_28,y_29,y_30,y_31,y_32,y_33,y_34,y_35,y_36,y_37,y_38,'
              'y_39,y_40,y_41,y_42,y_43,y_44,y_45,y_46,y_47,y_48,y_49,'
              'y_50,y_51,y_52,y_53,y_54,y_55,y_56,y_57,y_58,y_59,y_60,'
              'y_61,y_62,y_63,y_64,y_65,y_66,y_67\n')

        print(self.img_path, end="")
        f_winner.write(f"{self.img_path}")
        for i in range(69):
            for j in range(2):
                try:
                    if i > 0:
                        print(f",{self.coords_list[i][j]}", end="")
                        f_winner.write(f",{self.coords_list[i][j]}")
                    # elif self.bounding_box is True:
                    #     print(f",{self.coords_list[i][j]}",end="")
                    #     f_winner.write(f",{self.coords_list[i][j]}")
                except:
                    if i > 0:
                        print(",(-1,-1)", end="")
                        f_winner.write(",(-1,-1)")
                    # elif self.bounding_box is True:
                    #     print(",(-1,-1)", end="")
                    #     f_winner.write(",(-1,-1)")

        print()
        f_winner.write("\n")

    def run(self):
        self.init_subplots()
        self.connect()

        while True:
            # Wait for output, and 'update' figure
            plt.pause(0.01)

            # Exit
            if (self.is_finished
                    or (self.key_pressed and self.key_event.key == 'q')
                    or self.is_skipped):
                break

        plt.close()

        if self.is_finished:
            self.save_annotations()
            return 0  # finished normally
        elif self.is_skipped:
            return 0
        else:
            return 1  # aborted (pressed 'q')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Annotate one or more face images. Output to stdout.')
    base_group = parser.add_mutually_exclusive_group()
    base_group.add_argument('-d', '--dirimgs', type=str,
                            help='dir with images')
    base_group.add_argument('-i', '--img', type=str,
                            help='single image')
    # base_group.add_argument('-b', '--bounding_box')
    parser.add_argument('-n', '--nimgs', type=int,
                        help='number of images for -d mode', default=1)

    args = parser.parse_args()
    if args.dirimgs is None and args.img is None:
        parser.print_help()

    return args


def main(args):
    if args.dirimgs is not None:
        flist = sorted(os.listdir(args.dirimgs))
        for curr_file in flist:  # [::len(flist) // args.nimgs][:args.nimgs]:
            img_path = os.path.join(args.dirimgs, curr_file)
            viewer = InteractiveViewer(img_path)
            if viewer.run() == 1:
                break
            else:
                continue

        img_path = args.img
        viewer = InteractiveViewer(img_path)
        viewer.run()


if __name__ == '__main__':
    f_winner = open('landmark_output.txt', 'a')
    main(parse_arguments())
    f_winner.close()
