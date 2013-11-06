# The SGE Template
# Written in 2012, 2013 by Julian Marchant <onpon4@riseup.net> 
# 
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any
# warranty. 
# 
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

# INSTRUCTIONS FOR DEVELOPING AN IMPLEMENTATION: Replace the notice
# above as well as the notices contained in other source files with your
# own copyright notice.  Recommended free  licenses are the GNU General
# Public License, GNU Lesser General Public License, Expat License, or
# Apache License 2.0.

"""
The Stellar Game Engine (abbreviated "SGE", pronounced as "Sage") is a
free 2-D game engine.  The purpose of the SGE is to make game
development easier, which allows more rapid development by experienced
game developers and also helps less experienced game developers learn
how to develop games.

Official implementations of the SGE are free software (where "free"
refers to freedom, not price; see the `Free Software Definition
<http://gnu.org/philosophy/free-sw.html>`_ for more information), and
the documentation has been (to the extent legally possible) released to
the public domain via the CC0 license.

Even if it isn't required of you, we encourage you to release your
games' code under a free software license, such as the GNU General
Public License, the Expat License (often ambiguously called the "MIT
License"), or the Apache License 2.0.  Doing so is easy, does not
negatively affect you, and is highly appreciated as a contribution to
free software.

SGE Concepts
============

Naming Conventions
------------------

There are many cases where you will want to derive a class from a SGE
class.  Since there can be multiple implementations of the SGE, it can
be easy when doing so to overwrite a special variable used by some
implementations internally, which can be disastrous.  To avoid such
occasions, implementations are expected to never introduce any attribute
names which are not explicitly mentioned in the documentation for a
class unless the new attribute names are preceded by an underscore, as
in the hypothetical attribute name ``_foo``.  This naming convention
will protect users of the SGE from unexpected errors provided that they
do not use such names themselves.

A suggested convention for users of the SGE to use for "private"
attributes in place of the usual leading underscore  is to precede these
attributes with ``v_`` or ``p_``.

Events
------

The SGE uses an event-based system, with events defined by special class
methods with names starting with ``event_``.

Except in certain special cases, the order that events are handled in is
arbitrary; if Event A and Event B happen at the same time, one
implementation might handle Event A first, another might handle Event B
first, and another might handle either Event A or Event B first
depending on the circumstances.  This is particularly important to keep
in mind because, for example, there is no guarantee that the Step Event
will be executed before or after collision detection is applied in a
given frame, so code should not be written with that expectation.

The Mouse
---------

The mouse is handled somewhat unusually by the SGE.  Rather than having
functions or variables report the mouse position relative to the screen,
the mouse position within the room, calculated based on its position on
the screen by the SGE, is recorded in a special :class:`StellarClass`
object which represents the mouse.  This mouse object can be found as
:attr:`sge.game.mouse`, and it has the special object ID, ``"mouse"``.

The mouse object differs from most :class:`StellarClass` objects in a
few ways.  Its speed variables cannot be manually set, and they always
report numbers which correspond to the average motion of the mouse
during the last quarter of a second.  Setting
:attr:`sge.game.mouse.visible` toggles whether or not the mouse cursor
itself is visible, and setting :attr:`sge.game.mouse.sprite` sets the
mouse cursor to the sprite assigned.

In all other ways, the mouse object is exactly the same as all other
:class:`StellarClass` objects.

Colors
------

Colors can be defined for the SGE in a few different ways.

HTML Color Names
~~~~~~~~~~~~~~~~

The sixteen basic HTML colors, provided as strings, are accepted by the
SGE.  These are case-insensitive, so ``"red"`` is interpreted the same
as ``"Red"`` or ``"rEd"``.  The colors are:

- ``"white"``
- ``"silver"``
- ``"gray``
- ``"black"``
- ``"red"``
- ``"maroon"``
- ``"yellow"``
- ``"olive"``
- ``"lime"``
- ``"green"``
- ``"aqua"``
- ``"teal"``
- ``"blue"``
- ``"navy"``
- ``"fuchsia"``
- ``"purple"``

RGB(A) Tuples
~~~~~~~~~~~~~

A tuple containing three or four values is accepted as a color by the
SGE.  Each index represents a component of a color: first red, then
green, then blue, with the values being integers from ``0`` to ``255``.
For example, ``(255, 128, 0)`` indicates a color with full red
intensity, 50% green intensity, and no blue intensity, which is a shade
of orange.  Note that the components are colors of light, not colors of
pigment.

The fourth value of the tuple, if specified, indicates the alpha
transparency of the color, with the possible values again being integers
from ``0`` to ``255``.  ``255`` is fully opaque, ``0`` is fully
transparent, and any value in between indicates the amount of opacity;
for example, 128 is 50% transparent.  If the fourth value is
unspecified, it is assumed that the color is fully opaque.

RGBA tuples are the only way to specify alpha transparency of colors in
SGE.  All other methods for indicating color assume full opacity.

HTML Hex Strings and Integers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HTML hex strings and integers are accepted as colors by the SGE.  HTML
hex strings are in the format ``"#RRGGBB"``, where ``RR``, ``GG``, and
``BB`` are replaced with the red, green, and blue components of the
color, respectively, in hexadecimal form.  ``FF`` (equivalent to 255 in
decimal form) is full intensity of the respective color, and ``00``
(equivalent to 0 in decimal form) is no intensity of the respective
color.  For example, ``"#FF8000"`` is the same as ``(255, 128, 0)``, or
orange.

Integers, treated as hexadecimals, are also accepted.  These are in the
same form as HTML hex strings, but integral.  For example, ``0xFF8000``
is the same as ``"#FF8000"``.

Position
--------

In all cases of positioning for the SGE, it is based on a
two-dimensional graph with each unit being a pixel.  This graph is not
quite like regular graphs; the horizontal direction, normally called
``x``, is the same as the x-axis on a regular graph; ``0`` is the
origin, positive numbers are to the right of the origin, and negative
numbers are to the left of the origin.  However, in the vertical
direction, normally called ``y``, ``0`` is the origin, positive numbers
are below the origin, and negative numbers are above the origin.  While
slightly jarring if you are used to normal graphs, this is in fact
common in 2-D game development and is so how pixels in most image
formats are indexed.

Except where otherwise specified, the origin is always located at the
top-leftmost position of an object.

In addition to integers, position variables are allowed by the SGE to be
floating-point numbers.

Z-Axis
------

The SGE uses a Z-axis to determine where objects are placed in the third
dimension.  Objects with a higher Z value are considered to be closer to
the viewer and thus will be placed over objects which have a lower Z
value.  Note that the Z-axis does not allow 3-D gameplay or effects; it
is only used to tell the SGE what to do with objects that overlap.  For
example, if an object called ``spam`` has a Z value of ``5`` while an
object called ``eggs`` has a Z value of ``2``, ``spam`` will obscure
part or all of ``eggs`` when the two objects overlap.

If two objects with the same Z-axis value overlap, the SGE arbitrarily
chooses which one is considered to be closer to the viewer.  The SGE is
allowed to change this decision, but only while the objects in question
are not overlapping, since changing the decision while the two objects
are overlapping would cause an undesirable flicker effect.

Global Variables and Constants
==============================

.. data:: sge.IMPLEMENTATION

   A string indicating the name of the SGE implementation.

.. data:: sge.ALIGN_LEFT

   Flag indicating horizontal alignment to the left.

.. data:: sge.ALIGN_CENTER

   Flag indicating horizontal alignment to the center.

.. data:: sge.ALIGN_RIGHT

   Flag indicating horizontal alignment to the right.

.. data:: sge.ALIGN_TOP

   Flag indicating vertical alignment to the top

.. data:: sge.ALIGN_MIDDLE

   Flag indicating vertical alignment to the middle.

.. data:: sge.ALIGN_BOTTOM

   Flag indicating vertical alignment to the bottom.

.. data:: sge.game

   Stores the current :class:`sge.Game` object.  If there is no
   :class:`sge.Game` object currently, this variable is set to
   :const:`None`.

.. data:: sge.image_directories

   A list of directories where images can be found.  Default is
   ``./data/images``, ``./data/sprites``, or ``./data/backgrounds``,
   where ``.`` is the program directory.

.. data:: sge.font_directories

   A list of directories where font files can be found.  Default is
   ``./data/fonts``, where ``.`` is the program directory.

.. data:: sge.sound_directories

   A list of directories where sounds can be found.  Default is
   ``./data/sounds``, where ``.`` is the program directory.

.. data:: sge.music_directories

   A list of directories where music files can be found.  Default is
   ``./data/music``, where ``.`` is the program directory.

Information specific to [insert implementation name here]
=========================================================

License
-------

[insert license info here]

Dependencies
------------

- Python [insert Python version here] <http://www.python.org>
- [insert additional dependency here] <[insert dependency link here]>
- [insert additional dependency here] <[insert dependency link here]>
- [...]

[insert other info here]

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__version__ = "0.5.0"

import sys
import os
import math

# Import implementation-specific libraries like Pygame here

from .constants import *
from .Game import Game
from .Sprite import Sprite
from .BackgroundLayer import BackgroundLayer
from .Background import Background
from .Font import Font
from .Sound import Sound
from .Music import Music
from .StellarClass import StellarClass, Mouse
from .Room import Room
from .View import View
from .functions import *


__all__ = [
    # Constants
    'IMPLEMENTATION', 'ALIGN_LEFT', 'ALIGN_CENTER', 'ALIGN_RIGHT', 'ALIGN_TOP',
    'ALIGN_MIDDLE', 'ALIGN_BOTTOM',

    # Classes
    'Game', 'Sprite', 'BackgroundLayer', 'Background', 'Font', 'Sound',
    'Music', 'StellarClass', 'Room', 'View',

    # Functions
    'create_object', 'sound_stop_all', 'music_clear_queue', 'music_stop_all',
    'get_key_pressed', 'get_mouse_button_pressed', 'get_joystick_axis',
    'get_joystick_hat', 'get_joystick_button_pressed', 'get_joysticks',
    'get_joystick_axes', 'get_joystick_hats', 'get_joystick_buttons'
    ]

# Global variables
game = None
image_directories = [os.path.join(PROGRAM_DIR, 'data', 'images'),
                     os.path.join(PROGRAM_DIR, 'data', 'sprites'),
                     os.path.join(PROGRAM_DIR, 'data', 'backgrounds')]
font_directories = [os.path.join(PROGRAM_DIR, 'data', 'fonts')]
sound_directories = [os.path.join(PROGRAM_DIR, 'data', 'sounds')]
music_directories = [os.path.join(PROGRAM_DIR, 'data', 'music')]
