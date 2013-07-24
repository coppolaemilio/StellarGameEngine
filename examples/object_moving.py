#!/usr/bin/env python

# Object Moving Example
# Written in 2012, 2013 by Julian Marchant <onpon4@lavabit.com>
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any
# warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

"""Object Moving example

This is a simple example of a possible game in Stellar Game Engine, just
to give a general idea of how it will be used.

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sge


class Game(sge.Game):
    def event_key_press(self, key, char):
        if key == 'escape':
            self.end()

    def event_close(self):
        self.end()


class Circle(sge.StellarClass):
    def __init__(self, x, y, player=0):
        super(Circle, self).__init__(x, y, 5, sprite='circle', collision_precise=True)
        self.player = player

    def event_create(self):
        self.image_alpha = 200
        self.image_blend = 'blue'

    def event_step(self, time_passed):
        left_key = ['left', 'a', 'j', 'kp_4'][self.player]
        right_key = ['right', 'd', 'l', 'kp_6'][self.player]
        up_key = ['up', 'w', 'i', 'kp_8'][self.player]
        down_key = ['down', 's', 'k', 'kp_5'][self.player]

        self.xvelocity = (sge.get_key_pressed(right_key) -
                          sge.get_key_pressed(left_key))
        self.yvelocity = (sge.get_key_pressed(down_key) -
                          sge.get_key_pressed(up_key))

        # Limit the circles to inside the room.
        if self.bbox_left < 0:
            self.bbox_left = 0
        elif self.bbox_right >= sge.game.current_room.width:
            self.bbox_right = sge.game.current_room.width - 1
        if self.bbox_top < 0:
            self.bbox_top = 0
        elif self.bbox_bottom >= sge.game.current_room.height:
            self.bbox_bottom = sge.game.current_room.height - 1

def main():
    # Create Game object
    game = Game()

    # Load sprites
    circle_sprite = sge.Sprite('circle', width=64, height=64, origin_x=32,
                               origin_y=32)
    fence_sprite = sge.Sprite('fence')

    # Load backgrounds
    layers = (sge.BackgroundLayer(fence_sprite, 0, 380, 0, yrepeat=False),)
    background = sge.Background(layers, 0xffffff)

    # Create objects
    circle = Circle(game.width // 2, game.height // 2)
    objects = [circle]

    # Create view
    views = (sge.View(0, 0),)

    # Create rooms
    room1 = sge.Room(tuple(objects), views=views, background=background)

    game.start()


if __name__ == '__main__':
    main()
