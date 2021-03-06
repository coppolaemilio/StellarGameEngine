#!/usr/bin/env python2

# Stellarly-Encompassing Level Editor
# Copyright (C) 2013 Julian Marchant <onpon4@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
SELE: Stellarly-Encompassing Level Editor
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os

import sge
import stj

DIRNAME = os.path.dirname(__file__)

SCREEN_SIZE = (1280, 960)

CURSOR_SIZE = (24, 34)
CURSOR_ORIGIN = (1, 0)

SIDE_BAR_SIZE = (74, 960)
TOP_BAR_SIZE = (1280, 74)
BAR_Z = 0

ICON_SIZE = (36, 36)
ICON_POS = (6, 6)
TEXT_SIZE = (22, 16)
TEXT_POS = (5, 5)

BUTTON_SIZE = (48, 48)
BUTTON_Z = 5
BUTTON_SAVE_POS = (8, 8)
BUTTON_SAVE_ALL_POS = (64, 8)
BUTTON_LOAD_POS = (120, 8)
BUTTON_GRID_POS = (232, 8)
BUTTON_SHIFT_POS = (552, 8)
BUTTON_RELOAD_RESOURCES_POS = (608, 8)
BUTTON_BACKGROUND_POS = (664, 8)
BUTTON_VIEWS_POS = (720, 8)
BUTTON_SETTINGS_POS = (776, 8)
BUTTON_ZOOM_RESET_POS = (888, 8)
BUTTON_ZOOM_OUT_POS = (944, 8)
BUTTON_ZOOM_IN_POS = (1000, 8)
BUTTON_PREVIOUS_ROOM_POS = (1112, 8)
BUTTON_NEXT_ROOM_POS = (1168, 8)
BUTTON_CLOSE_ROOM_POS = (1224, 8)
BUTTON_TOOL_POS = (8, 120)
BUTTON_CLASS_POS = (8, 232)
BUTTON_IMAGE_INDEX_POS = (8, 288)
BUTTON_IMAGE_ALPHA_POS = (8, 624)
BUTTON_IMAGE_BLEND_POS = (8, 680)
BUTTON_VISIBLE_POS = (8, 736)
BUTTON_ACTIVE_POS = (8, 798)
BUTTON_DETECTS_COLLISIONS_POS = (8, 848)
BUTTON_ARGS_POS = (8, 904)

TEXTBOX_SIZE = (60, 48)
TEXTBOX_GRID_XSIZE_POS = (288, 8)
TEXTBOX_GRID_YSIZE_POS = (388, 8)
TEXTBOX_Z_POS = (2, 344)
TEXTBOX_IMAGE_FPS_POS = (2, 400)
TEXTBOX_IMAGE_XSCALE_POS = (2, 456)
TEXTBOX_IMAGE_YSCALE_POS = (2, 512)
TEXTBOX_IMAGE_ANGLE_POS = (2, 568)

CHECKBOX_SIZE = (32, 32)
CHECKBOX_GRID_SNAP_POS = (464, 24)

GRID_NONE = 0
GRID_RECTANGULAR = 1
GRID_ISOMETRIC = 2
GRID_NUMKINDS = 3
GRID_DEFAULT = GRID_RECTANGULAR
ZOOM_DEFAULT = 2
TOOL_DEFAULT = 'pointer'

sge.image_directories.append(os.path.join(DIRNAME, 'Sprites'))
sge.image_directories.append(os.path.join(DIRNAME, 'Backgrounds'))
sge.image_directories.append(os.path.join(DIRNAME, 'editor_data'))
sge.font_directories.append(os.path.join(DIRNAME, 'editor_data'))


class glob(object):

    game_file = None
    game_globals = {}

    button_sprites = {}
    text_entry_font = None
    tooltip_font = None
    tooltip_sprite = None

    sprites = []
    defaults = {}


class Game(sge.Game):

    def event_game_start(self):
        self.events_active = True
        self.will_exit = False
        self.scale = 0

    def event_key_press(self, key):
        if self.events_active:
            if key == 'escape':
                self.close()

    def event_mouse_move(self, x, y):
        if not self.mouse.collides(TooltipShower):
            set_tooltip("")

    def event_close(self):
        if self.events_active:
            self.close()

    def close(self):
        self.will_exit = True
        for room in self.rooms:
            if self.will_exit:
                room.close()
            else:
                break

        if self.will_exit:
            self.end()

    def room_goto_next(self):
        i = sge.game.current_room.room_number
        selected = False

        while not selected:
            i = (i + 1) % len(sge.game.rooms)
            if isinstance(sge.game.rooms[i], Room):
                selected = True

        sge.game.rooms[i].resume()

    def room_goto_previous(self):
        i = sge.game.current_room.room_number
        selected = False

        while not selected:
            i = (i - 1) % len(sge.game.rooms)
            if isinstance(sge.game.rooms[i], Room):
                selected = True

        sge.game.rooms[i].resume()


class TooltipShower(sge.StellarClass):

    tooltip = ""

    def event_mouse_move(self, x, y):
        if self.collides(sge.game.mouse):
            set_tooltip(self.tooltip)


class Object(sge.StellarClass):

    def __init__(self, cls, args, kwargs):
        self.cls = cls
        self.args = list(args)
        self.kwargs = kwargs
        self.defaults = glob.defaults.setdefault(cls, {})

        x = self.get_x()
        y = self.get_y()
        z = self.get_z()
        sprite = self.get_sprite()
        visible = self.get_visible()
        image_index = self.get_image_index()
        image_fps = self.get_image_fps()
        image_xscale = self.get_image_xscale()
        image_yscale = self.get_image_yscale()
        image_rotation = self.get_image_rotation()
        image_alpha = self.get_image_alpha()
        image_blend = self.get_image_blend()

        super(Object, self).__init__(
            x, y, z, sprite=sprite, active=False, detects_collisions=False,
            visible=visible, image_index=image_index, image_fps=image_fps,
            image_xscale=image_xscale, image_yscale=image_yscale,
            image_rotation=image_rotation, image_alpha=image_alpha,
            image_blend=image_blend)

    def refresh(self):
        self.x = self.get_x()
        self.y = self.get_y()
        self.z = self.get_z()
        self.sprite = self.get_sprite()
        self.image_index = self.get_image_index()
        self.image_fps = self.get_image_fps()
        self.image_xscale = self.get_image_xscale()
        self.image_yscale = self.get_image_yscale()
        self.image_rotation = self.get_image_rotation()
        self.image_alpha = self.get_image_alpha()
        self.image_blend = self.get_image_blend()

        if not self.get_visible():
            self.image_blend = 'black'
            self.image_alpha = 128

    def get_x(self):
        if len(self.args) >= 1:
            return (eval(str(self.args[0]), glob.game_globals) *
                    sge.game.current_room.zoom)
        else:
            return 0

    def get_y(self):
        if len(self.args) >= 2:
            return (eval(str(self.args[1]), glob.game_globals) *
                    sge.game.current_room.zoom)
        else:
            return 0

    def get_z(self):
        if 'z' in self.kwargs:
            return eval(str(self.kwargs['z']), glob.game_globals)
        elif 'z' in self.defaults:
            return eval(str(self.defaults['z']), glob.game_globals)
        else:
            return 0

    def get_sprite(self):
        if 'sprite' in self.kwargs:
            return eval(str(self.kwargs['sprite']), glob.game_globals)
        elif 'sprite' in self.defaults:
            return eval(str(self.defaults['sprite']), glob.game_globals)
        else:
            return 'stellar_room_editor_nosprite'

    def get_visible(self):
        if 'visible' in self.kwargs:
            return eval(str(self.kwargs['visible']), glob.game_globals)
        elif 'visible' in self.defaults:
            return eval(str(self.defaults['visible']), glob.game_globals)
        else:
            return True

    def get_image_index(self):
        if 'image_index' in self.kwargs:
            return eval(str(self.kwargs['image_index']), glob.game_globals)
        elif 'image_index' in self.defaults:
            return eval(str(self.defaults['image_index']), glob.game_globals)
        else:
            return 0

    def get_image_fps(self):
        if 'image_fps' in self.kwargs:
            return eval(str(self.kwargs['image_fps']), glob.game_globals)
        elif 'image_fps' in self.defaults:
            return eval(str(self.defaults['image_fps']), glob.game_globals)
        else:
            return None

    def get_image_xscale(self):
        zoom = sge.game.current_room.zoom
        if 'image_xscale' in self.kwargs:
            return eval(str(self.kwargs['image_xscale']),
                        glob.game_globals) * zoom
        elif 'image_xscale' in self.defaults:
            return eval(str(self.defaults['image_xscale']),
                        glob.game_globals) * zoom
        else:
            return zoom

    def get_image_yscale(self):
        zoom = sge.game.current_room.zoom
        if 'image_yscale' in self.kwargs:
            return eval(str(self.kwargs['image_yscale']),
                        glob.game_globals) * zoom
        elif 'image_yscale' in self.defaults:
            return eval(str(self.defaults['image_yscale']),
                        glob.game_globals) * zoom
        else:
            return zoom

    def get_image_rotation(self):
        if 'image_rotation' in self.kwargs:
            return eval(str(self.kwargs['image_rotation']), glob.game_globals)
        elif 'image_rotation' in self.defaults:
            return eval(str(self.defaults['image_rotation']),
                        glob.game_globals)
        else:
            return 0

    def get_image_alpha(self):
        if 'image_alpha' in self.kwargs:
            return eval(str(self.kwargs['image_alpha']), glob.game_globals)
        elif 'image_alpha' in self.defaults:
            return eval(str(self.defaults['image_alpha']), glob.game_globals)
        else:
            return 255

    def get_image_blend(self):
        if 'image_blend' in self.kwargs:
            return eval(str(self.kwargs['image_blend']), glob.game_globals)
        elif 'image_blend' in self.defaults:
            return eval(str(self.defaults['image_blend']), glob.game_globals)
        else:
            return None


class Button(TooltipShower):

    icon = 'stellar_room_editor_unknown'
    tooltip = "Button"

    def __init__(self, x, y):
        super(Button, self).__init__(x, y, BUTTON_Z,
                                     sprite='stellar_room_editor_button',
                                     collision_precise=True)

    def do_effect(self):
        """Do the effect of pressing this button."""
        pass

    def event_create(self):
        self.pressed = False
        self.icon_object = sge.StellarClass.create(
            self.x + ICON_POS[0], self.y + ICON_POS[1], self.z + 1,
            sprite=self.icon)

    def event_step(self, time_passed):
        if self.pressed and self.collides(sge.game.mouse):
            self.image_index = 1
        else:
            self.image_index = 0

        self.icon_object.sprite = self.icon

    def event_mouse_button_press(self, button):
        if button == 'left' and self.collides(sge.game.mouse):
            self.pressed = True

    def event_mouse_button_release(self, button):
        if button == 'left' and self.collides(sge.game.mouse):
            self.do_effect()


class SaveButton(Button):

    icon = 'stellar_room_editor_icon_save'
    tooltip = 'Save the current room.'

    def do_effect(self):
        sge.game.current_room.save()


class SaveAllButton(Button):

    icon = 'stellar_room_editor_icon_save_all'
    tooltip = 'Save all rooms.'

    def do_effect(self):
        for room in sge.game.rooms:
            room.save()


class LoadButton(Button):

    icon = 'stellar_room_editor_icon_load'
    tooltip = 'Load a room from a file.'

    def do_effect(self):
        # TODO: File selection dialog to make this better.
        m = "Please enter the name of the file to load."
        d = os.path.normpath(os.path.realpath(os.path.join(
            DIRNAME, "data", "rooms", "*.rmj")))
        entry = sge.get_text_entry(m, d)
        if entry is not None:
            room = Room.load(entry)
            room.resume()


class GridTypeButton(Button):

    def __init__(self, *args, **kwargs):
        self.set_icon()
        super(GridTypeButton, self).__init__(*args, **kwargs)

    def set_icon(self):
        if sge.game.current_room.grid == GRID_NONE:
            self.icon = None
            self.tooltip = 'Grid type: None'
        elif sge.game.current_room.grid == GRID_RECTANGULAR:
            self.icon = 'stellar_room_editor_icon_grid'
            self.tooltip = 'Grid type: Rectangular'
        elif sge.game.current_room.grid == GRID_ISOMETRIC:
            self.icon = 'stellar_room_editor_icon_grid_isometric'
            self.tooltip = 'Grid type: Isometric'
        else:
            self.icon = self.__class__.icon
            self.tooltip = self.__class__.tooltip

    def do_effect(self):
        sge.game.current_room.grid += 1
        sge.game.current_room.grid %= GRID_NUMKINDS
        self.set_icon()


class ShiftButton(Button):

    icon = 'stellar_room_editor_icon_shift'
    tooltip = "Shift all objects' positions by a given amount."

    def do_effect(self):
        m = "Enter the horizontal shift amount (in pixels)."
        hshift = sge.get_text_entry(m)

        if hshift is not None:
            m = "Enter the vertical shift amount (in pixels)."
            vshift = sge.get_text_entry(m)

            if vshift is not None:
                try:
                    hshift = float(hshift)
                except ValueError:
                    hshift = 0

                try:
                    vshift = float(vshift)
                except ValueError:
                    vshift = 0

                for obj in sge.game.current_room.real_objects:
                    if len(obj.args) > 0:
                        obj.args[0] += hshift
                        if len(obj.args) > 1:
                            obj.args[1] += vshift


class ReloadResourcesButton(Button):

    icon = 'stellar_room_editor_icon_reload_resources'
    tooltip = "Reload the game's resources (sprites, objects, etc)."

    def do_effect(self):
        load_resources()


class BackgroundButton(Button):

    icon = 'stellar_room_editor_icon_background'
    tooltip = "Change the background used with this room."

    def do_effect(self):
        # TODO
        pass


class ViewsButton(Button):

    icon = 'stellar_room_editor_icon_views'
    tooltip = "Change the views in this room."

    def do_effect(self):
        # TODO
        pass


class SettingsButton(Button):

    icon = 'stellar_room_editor_icon_settings'
    tooltip = "Configure various settings for the room."

    def do_effect(self):
        # TODO: Probably via a special "settings" room
        pass


class ZoomResetButton(Button):

    icon = 'stellar_room_editor_icon_zoom_reset'
    tooltip = "Reset the zoom level to 100%."

    def do_effect(self):
        sge.game.current_room.zoom_reset()


class ZoomOutButton(Button):

    icon = 'stellar_room_editor_icon_zoom_out'
    tooltip = "Zoom out."

    def do_effect(self):
        sge.game.current_room.zoom_out()


class ZoomInButton(Button):

    icon = 'stellar_room_editor_icon_zoom_in'
    tooltip = "Zoom in."

    def do_effect(self):
        sge.game.current_room.zoom_in()


class PreviousRoomButton(Button):

    icon = 'stellar_room_editor_icon_room_previous'
    tooltip = "Go to the previous room."

    def do_effect(self):
        sge.game.room_goto_previous()


class NextRoomButton(Button):

    icon = 'stellar_room_editor_icon_room_next'
    tooltip = "Go to the next room."

    def do_effect(self):
        sge.game.room_goto_next()


class CloseRoomButton(Button):

    icon = 'stellar_room_editor_icon_close'
    tooltip = "Close the current room."

    def do_effect(self):
        sge.game.current_room.close()


class ToolButton(Button):

    tooltip_base = "Tool selected: {0}"

    def do_effect(self):
        # TODO
        pass


class ObjectClassButton(Button):

    tooltip_base = "Object class: {0}"

    def do_effect(self):
        # TODO
        pass


class ObjectImageIndexButton(Button):

    tooltip_base = "Object image index: {0}"

    def do_effect(self):
        # TODO
        pass


class ObjectImageAlphaButton(Button):

    icon_base = 'stellar_room_editor_icon_image_settings'
    tooltip_base = "Object image alpha: {0}%"

    def do_effect(self):
        # TODO
        pass


class ObjectImageBlendButton(Button):

    icon_base = 'stellar_room_editor_icon_image_settings'
    tooltip_base = "Object image blend: Red {0}, Green {1}, Blue {2}"

    def do_effect(self):
        # TODO
        pass


class ObjectVisibleButton(Button):

    icon_true = 'stellar_room_editor_icon_image_settings'
    icon_false = None
    tooltip_true = "Object is visible."
    tooltip_false = "Object is invisible."

    def do_effect(self):
        # TODO
        pass


class ObjectActiveButton(Button):

    icon_true = 'stellar_room_editor_icon_active'
    icon_false = 'stellar_room_editor_icon_inactive'
    tooltip_true = "Object is active."
    tooltip_false = "Object is inactive."

    def do_effect(self):
        # TODO
        pass


class ObjectDetectsCollisionsButton(Button):

    icon_true = 'stellar_room_editor_icon_solid'
    icon_false = 'stellar_room_editor_icon_unsolid'
    tooltip_true = "Object detects collisions."
    tooltip_false = "Object does not detect collisions."

    def do_effect(self):
        # TODO
        pass


class ObjectArgsButton(Button):

    icon = 'stellar_room_editor_icon_args'
    tooltip = "Specify the arguments for the object manually."

    def do_effect(self):
        # TODO
        pass


class Textbox(TooltipShower):

    tooltip = "Textbox"

    def __init__(self, text=""):
        self.text = text
        self.cursor_position = 0
        super(Textbox, self).__init__(x, y, BUTTON_Z,
                                      sprite='stellar_room_editor_textbox',
                                      collision_precise=True)

    def redraw_text(self):
        self.text_sprite.draw_clear()
        self.text_sprite.draw_text(glob.text_entry_font, self.text,
                                   self.text_sprite.width / 2,
                                   self.text_sprite.height / 2,
                                   halign=sge.ALIGN_CENTER,
                                   valign=sge.ALIGN_MIDDLE)

    def event_create(self):
        self.selected = False
        self.text_sprite = sge.Sprite(width=TEXT_SIZE[0], height=TEXT_SIZE[1])
        self.text_object = sge.StellarClass.create(
            self.x + TEXT_POS[0], self.y + TEXT_POS[1], self.z + 1,
            sprite=self.text_sprite)

    def event_mouse_button_press(self, button):
        if button == "left" and self.collides(sge.game.mouse):
            self.selected = True
            # TODO: Set cursor position based on location of click
        else:
            self.selected = False

    def event_key_press(self, key, char):
        if self.selected:
            if key == "left":
                if self.cursor_position > 0:
                    self.cursor_position -= 1
            elif key == "right":
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
            elif key == "backspace":
                if self.cursor_position > 0:
                    text_list = list(self.text)
                    del text_list[self.cursor_position - 1]
                    self.text = ''.join(text_list)
            elif key == "delete":
                if self.cursor_position < len(text_entered):
                    text_list = list(self.text)
                    del text_list[self.cursor_position]
                    self.text = ''.join(text_list)
            elif key in ("enter", "kp_enter"):
                self.selected = False
            elif char:
                text_list = list(self.text)
                text_list.insert(self.cursor_position, char)
                self.text = ''.join(text_list)
                self.cursor_position += 1
                self.redraw_text()


class GridWidthTextbox(Textbox):

    tooltip = "Grid Width"


class GridHeightTextbox(Textbox):

    tooltip = "Grid Height"


class ObjectZTextbox(Textbox):

    tooltip = "Z-Axis"


class ObjectImageFPSTextbox(Textbox):

    tooltip = "Image FPS"


class ObjectImageXScaleTextbox(Textbox):

    tooltip = "Image X Scale"


class ObjectImageYScaleTextbox(Textbox):

    tooltip = "Image Y Scale"


class ObjectImageAngleTextbox(Textbox):

    tooltip = "Image Angle"


class Checkbox(TooltipShower):

    tooltip = "Checkbox"

    def __init__(self, x, y, checked=False):
        self.checked = checked
        super(Button, self).__init__(x, y, BUTTON_Z,
                                     sprite='stellar_room_editor_checkbox',
                                     collision_precise=True)

    # TODO: Mouse events


class GridSnapCheckbox(Checkbox):

    tooltip = "Snap to Grid"


class Tooltip(sge.StellarClass):

    def __init__(self):
        super(Tooltip, self).__init__(0, 0, sprite=glob.tooltip_sprite)

    def event_step(self, time_passed):
        view = sge.game.current_room.views[0]
        self.bbox_right = view.x + view.width
        self.bbox_bottom = view.y + view.height

        if self.collides(sge.game.mouse):
            self.bbox_left = view.x


class Room(sge.Room):

    def __init__(self, objects=(), width=None, height=None, views=None,
                 background=None, background_x=0, background_y=0):
        self.fname = None
        self.empty = True
        self.unchanged = True
        self.opened = True
        self.name = ""
        self.cls = "sge.Room"
        self.real_objects = objects
        self.real_width = width if width is not None else 640
        self.real_height = height if height is not None else 480
        self.real_views = views

        self.grid = GRID_DEFAULT
        self.zoom = ZOOM_DEFAULT
        self.tool = TOOL_DEFAULT

        # TODO: Create buttons and other GUI elements

        w = self.get_width()
        h = self.get_height()

        width = w + SIDE_BAR_SIZE[0]
        height = h + TOP_BAR_SIZE[1]

        main_view = sge.View(0, 0, SIDE_BAR_SIZE[0], TOP_BAR_SIZE[1])
        sidebar_view = sge.View(self.get_width(), TOP_BAR_SIZE[1], 0,
                                TOP_BAR_SIZE[1], SIDE_BAR_SIZE[0],
                                SIDE_BAR_SIZE[1] - TOP_BAR_SIZE[1])
        topbar_view = sge.View(0, self.get_height(), 0, 0, *TOP_BAR_SIZE)
        views = [main_view, sidebar_view, topbar_view]

        super(Room, self).__init__(objects, width, height, views, background,
                                   background_x, background_y)

        obj = SaveButton(w + BUTTON_SAVE_POS[0], h + BUTTON_SAVE_POS[1])
        self.add(obj)
        obj = SaveAllButton(w + BUTTON_SAVE_ALL_POS[0],
                            h + BUTTON_SAVE_ALL_POS[1])
        self.add(obj)
        obj = LoadButton(w + BUTTON_LOAD_POS[0], h + BUTTON_LOAD_POS[1])
        self.add(obj)
        obj = GridTypeButton(w + BUTTON_GRID_POS[0], h + BUTTON_GRID_POS[1])
        self.add(obj)
        obj = ShiftButton(w + BUTTON_SHIFT_POS[0], h + BUTTON_SHIFT_POS[1])
        self.add(obj)
        obj = ReloadResourcesButton(w + BUTTON_RELOAD_RESOURCES_POS[0],
                                    h + BUTTON_RELOAD_RESOURCES_POS[1])
        self.add(obj)
        obj = BackgroundButton(w + BUTTON_BACKGROUND_POS[0],
                               h + BUTTON_BACKGROUND_POS[1])
        self.add(obj)
        obj = ViewsButton(w + BUTTON_VIEWS_POS[0], h + BUTTON_VIEWS_POS[1])
        self.add(obj)
        obj = SettingsButton(w + BUTTON_SETTINGS_POS[0],
                             h + BUTTON_SETTINGS_POS[1])
        self.add(obj)
        obj = ZoomResetButton(w + BUTTON_ZOOM_RESET_POS[0],
                              h + BUTTON_ZOOM_RESET_POS[1])
        self.add(obj)
        obj = ZoomOutButton(w + BUTTON_ZOOM_OUT_POS[0],
                            h + BUTTON_ZOOM_OUT_POS[1])
        self.add(obj)
        obj = ZoomInButton(w + BUTTON_ZOOM_IN_POS[0],
                           h + BUTTON_ZOOM_IN_POS[1])
        self.add(obj)
        obj = PreviousRoomButton(w + BUTTON_PREVIOUS_ROOM_POS[0],
                                 h + BUTTON_PREVIOUS_ROOM_POS[1])
        self.add(obj)
        obj = NextRoomButton(w + BUTTON_NEXT_ROOM_POS[0],
                             h + BUTTON_NEXT_ROOM_POS[1])
        self.add(obj)
        obj = CloseRoomButton(w + BUTTON_CLOSE_ROOM_POS[0],
                              h + BUTTON_CLOSE_ROOM_POS[1])
        self.add(obj)
        obj = ToolButton(w + BUTTON_TOOL_POS[0], h + BUTTON_TOOL_POS[1])
        self.add(obj)
        obj = ObjectClassButton(w + BUTTON_CLASS_POS[0],
                                h + BUTTON_CLASS_POS[1])
        self.add(obj)
        obj = ObjectImageIndexButton(w + BUTTON_IMAGE_INDEX_POS[0],
                                     h + BUTTON_IMAGE_INDEX_POS[1])
        self.add(obj)
        obj = ObjectImageAlphaButton(w + BUTTON_IMAGE_ALPHA_POS[0],
                                     h + BUTTON_IMAGE_ALPHA_POS[1])
        self.add(obj)
        obj = ObjectImageBlendButton(w + BUTTON_IMAGE_BLEND_POS[0],
                                     h + BUTTON_IMAGE_BLEND_POS[1])
        self.add(obj)
        obj = ObjectVisibleButton(w + BUTTON_VISIBLE_POS[0],
                                  h + BUTTON_VISIBLE_POS[1])
        self.add(obj)
        obj = ObjectActiveButton(w + BUTTON_ACTIVE_POS[0],
                                 h + BUTTON_ACTIVE_POS[1])
        self.add(obj)
        obj = ObjectDetectsCollisionsButton(
            w + BUTTON_DETECTS_COLLISIONS_POS[0],
            h + BUTTON_DETECTS_COLLISIONS_POS[1])
        self.add(obj)
        obj = ObjectArgsButton(w + BUTTON_ARGS_POS[0], h + BUTTON_ARGS_POS[1])
        self.add(obj)

    def get_width(self):
        return self.real_width * self.zoom

    def get_height(self):
        return self.real_height * self.zoom

    def save(self, fname=None):
        """Save settings to a file."""
        if fname is None:
            if self.fname is not None:
                fname = self.fname
            else:
                # TODO: Create a file selection dialog for this.
                m = "Please enter the name of the file to save to."
                d = os.path.normpath(os.path.realpath(os.path.join(
                    DIRNAME, "data", "rooms", "*.rmj")))
                entry = sge.get_text_entry(m, d)
                if entry is not None:
                    fname = entry
                else:
                    return
        elif os.path.exists(fname):
            m = "{0} already exists. Overwrite?".format(fname)
            if not sge.show_message(m, ("No", "Yes")):
                return

        config = {'views': [], 'objects': []}
        config['class'] = self.cls
        config['width'] = self.width
        config['height'] = self.height
        config['background'] = self.background.id
        config['background_x'] = self.background_x
        config['background_y'] = self.background_y

        for view in self.views:
            config['views'].append(
                {'x': view.x, 'y': view.y, 'xport': view.xport,
                 'yport': view.yport, 'width': view.width,
                 'height': view.height})

        for obj in self.objects:
            config['objects'].append(
                {'class': obj.cls, 'x': obj.x, 'y': obj.y, 'z': obj.z,
                 'args': obj.args, 'kwargs': obj.kwargs})

        with open(fname, 'w') as f:
            json.dump(config, f, indent=4, sort_keys=True)

        self.unchanged = True

    def close(self):
        if self.unchanged:
            self.opened = False
            sge.game.room_goto_next()
        else:
            m = "Save changes to {0} before closing?".format(self.name)
            answer = sge.show_message(m, ("Cancel", "No", "Yes"), 2)
            if answer != 0:
                if answer == 2:
                    self.save(None)

                self.opened = False
                sge.game.room_goto_next()

    def zoom_reset(self):
        # TODO
        pass

    def zoom_out(self):
        # TODO
        pass

    def zoom_in(self):
        # TODO
        pass

    @classmethod
    def load(cls, fname):
        """Load settings from file and return the resulting room."""
        if glob.game_file is not None:
            with open(fname, 'r') as f:
                config = json.read(f)

            object_data = config.setdefault("objects", [])
            objects = []

            for obj in object_data:
                cls = obj.setdefault("class", "sge.StellarClass")
                args = obj.setdefault("arguments", [])
                kwargs = obj.setdefault("keyword_arguments", {})
                objects.append(Object(cls, args, kwargs))

            view_data = config.setdefault("views", [])
            views = []

            for view in view_data:
                x = str(view.setdefault("x", 0))
                y = str(view.setdefault("y", 0))
                xport = str(view.setdefault("xport", 0))
                yport = str(view.setdefault("yport", 0))
                width = str(view.setdefault("width"))
                height = str(view.setdefault("height"))
                views.append(View(x, y, xport, yport, width, height))

            width = str(config.setdefault("width"))
            height = str(config.setdefault("height"))
            background = str(config.setdefault("background"))
            background_x = str(config.setdefault("background_x", 0))
            background_y = str(config.setdefault("background_y", 0))

            if sge.game.current_room.empty:
                new_room = sge.game.current_room
                new_room.real_objects = objects
                new_room.real_width = width
                new_room.real_height = height
                new_room.real_views = views
                new_room.background = background
                new_room.background_x = background_x
                new_room.background_y = background_y
            else:
                for room in sge.game.rooms:
                    if room.fname == fname:
                        room.opened = True
                        return room

                new_room = Room(objects, width, height, views, background,
                                background_x, background_y)

            new_room.fname = fname
            new_room.cls = cls
            new_room.empty = False
            new_room.opened = True

            return new_room


class RoomSettings(sge.Room):

    """Room used for adjusting room settings."""

    def __init__(self):
        pass


class View(object):

    """Stores the sge.View options, but as strings of Python code."""

    def __init__(self, x, y, xport=0, yport=0, width=None, height=None):
        self.x = x
        self.y = y
        self.xport = xport
        self.yport = yport
        self.width = width
        self.height = height

    def get_x(self):
        return eval(str(self.x), glob.game_globals)

    def get_y(self):
        return eval(str(self.y), glob.game_globals)

    def get_width(self):
        return eval(str(self.width), glob.game_globals)

    def get_height(self):
        return eval(str(self.height), glob.game_globals)


def set_tooltip(text):
    """Set the text of the tooltip.  Set to None for no tooltip."""
    glob.tooltip_sprite.draw_clear()
    if text:
        w, h = glob.tooltip_font.get_size(text)
        w += 4
        h += 4
        glob.tooltip_sprite.width = w
        glob.tooltip_sprite.height = h
        glob.tooltip_sprite.draw_rectangle(0, 0, w, h, "#C8AD7F", "black")
        glob.tooltip_sprite.draw_text(glob.tooltip_font, text, 2, 2)


def load_resources():
    """Load or reload the sprites, backgrounds, and objects."""
    if glob.game_file is not None:
        with open(glob.game_file, 'r') as f:
            config = json.read(f)

        # Read globals (for purpose of evaluation), using the editors
        # globals as a base.
        glob.game_globals = globals()

        constants = config.setdefault("constants", [])
        globalvars = config.setdefault("global_variables", [])

        for var in constants + globalvars:
            name, value = var.split("=")
            name = name.strip()
            game_globals[name] = eval(value, game_globals)
            
        # Load sprites
        glob.sprites = []
        sprites = config.setdefault("sprites", [])

        for sprite in sprites:
            name = eval(str(sprite.setdefault("name")), glob.game_globals)
            id_ = eval(str(sprite.setdefault("id")), glob.game_globals)
            width = eval(str(sprite.setdefault("width")), glob.game_globals)
            height = eval(str(sprite.setdefault("height")), glob.game_globals)
            origin_x = eval(str(sprite.setdefault("origin_x", 0)),
                            glob.game_globals)
            origin_y = eval(str(sprite.setdefault("origin_y", 0)),
                            glob.game_globals)
            transparent = eval(str(sprite.setdefault("transparent", True)),
                               glob.game_globals)
            fps = eval(str(sprite.setdefault("fps", 60)), glob.game_globals)
            bbox_x = eval(str(sprite.setdefault("bbox_x")), glob.game_globals)
            bbox_y = eval(str(sprite.setdefault("bbox_y")), glob.game_globals)
            bbox_width = eval(str(sprite.setdefault("bbox_width")),
                              glob.game_globals)
            bbox_height = eval(str(sprite.setdefault("bbox_height")),
                               glob.game_globals)
            s = sge.Sprite(name, id_, width, height, origin_x, origin_y,
                           transparent, fps, bbox_x, bbox_y, bbox_width,
                           bbox_height)
            glob.sprites.append(s)

        # Load backgrounds
        background_layers = config.setdefault("background_layers", [])

        for layer in background_layers:
            sprite = eval(str(layer.setdefault(
                "sprite", '"stellar_room_editor_no_sprite"')),
                          glob.game_globals)
            x = eval(str(layer.setdefault("x", 0)), glob.game_globals)
            y = eval(str(layer.setdefault("y", 0)), glob.game_globals)
            z = eval(str(layer.setdefault("z", 0)), glob.game_globals)
            id_ = eval(str(layer.setdefault("id")), glob.game_globals)
            xscroll_rate = eval(str(layer.setdefault("xscroll_rate", 1)),
                                glob.game_globals)
            yscroll_rate = eval(str(layer.setdefault("yscroll_rate", 1)),
                                glob.game_globals)
            xrepeat = eval(str(layer.setdefault("xrepeat", True)),
                           glob.game_globals)
            yrepeat = eval(str(layer.setdefault("yrepeat", True)),
                           glob.game_globals)
            sge.BackgroundLayer(sprite, x, y, z, id_, xscroll_rate,
                                yscroll_rate, xrepeat, yrepeat)

        backgrounds = config.setdefault("backgrounds", [])

        for background in backgrounds:
            layers = []
            color = eval(str(background.setdefault("color", '"white"')),
                         glob.game_globals)
            id_ = eval(str(background.setdefault("id")), glob.game_globals)

            for layer in background.setdefault("layers", []):
                layers.append(eval(str(layer), glob.game_globals))

            sge.Background(layers, color, id_)

        # Load class defaults
        glob.defaults = {}
        classes = config.setdefault("classes", {})

        for i in classes:
            glob.defaults[i] = {}
            methods = classes[i].setdefault("methods", [])

            for method in methods:
                if method.setdefault("name") == "__init__":
                    args = method.setdefault("arguments", [])

                    for arg in args:
                        if "=" in arg:
                            name, value = arg.split("=")
                            name = name.strip()
                            value = value.strip()
                            glob.defaults[i][name] = str(value)


def main(*args):
    # Create Game object
    Game(*SCREEN_SIZE, scale=0.5, scale_smooth=True)

    # Load editor resources
    # Sprites
    sge.Sprite('stellar_room_editor_cursor', width=CURSOR_SIZE[0],
               height=CURSOR_SIZE[1], origin_x=CURSOR_ORIGIN[0],
               origin_y=CURSOR_ORIGIN[1])
    sge.Sprite('stellar_room_editor_panel_left', width=SIDE_BAR_SIZE[0],
               height=SIDE_BAR_SIZE[1])
    sge.Sprite('stellar_room_editor_panel_top', width=TOP_BAR_SIZE[0],
               height=TOP_BAR_SIZE[1])
    sge.Sprite('stellar_room_editor_button', width=BUTTON_SIZE[0],
               height=BUTTON_SIZE[1], fps=0)
    sge.Sprite('stellar_room_editor_textbox', width=TEXTBOX_SIZE[0],
               height=TEXTBOX_SIZE[1])
    sge.Sprite('stellar_room_editor_checkbox', width=CHECKBOX_SIZE[0],
               height=CHECKBOX_SIZE[1], fps=0)
    sge.Sprite('stellar_room_editor_unknown', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_active', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_args', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_background', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_close', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_grid', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_grid_isometric', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_image_settings', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_inactive', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_load', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_return_to_room', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_reload_resources', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_room_next', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_room_previous', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_save', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_save_all', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_settings', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_shift', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_solid', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_tool_fill', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_tool_line', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_tool_paintbrush', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_tool_pointer', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_unsolid', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_views', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_zoom_in', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_zoom_out', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    sge.Sprite('stellar_room_editor_icon_zoom_reset', width=ICON_SIZE[0],
               height=ICON_SIZE[1])
    glob.tooltip_sprite = sge.Sprite()

    # Fonts
    glob.text_entry_font = sge.Font('OSP-DIN.ttf', 20)
    glob.tooltip_font = sge.Font('OSP-DIN.ttf', 16)

    # Set mouse cursor
    sge.game.mouse.sprite = 'stellar_room_editor_cursor'

    if len(args) > 1:
        glob.game_file = args[1]

    # Load game resources
    try:
        load_resources()
    except IOError:
        print('"{0}" is not a proper game file. Ignoring.'.format(
            glob.game_file))
        glob.game_file = None

    # Create rooms
    for arg in args[2:]:
        try:
            Room.load(arg)
        except IOError:
            print('"{0}" is not a proper room file. Skipping.'.format(arg))

    if not sge.game.rooms:
        Room()

    sge.game.start()


if __name__ == '__main__':
    main(*sys.argv)
