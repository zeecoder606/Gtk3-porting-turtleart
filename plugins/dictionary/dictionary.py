#!/usr/bin/env python
#Copyright (c) 2016 Tymon Radzik
#
#This is Python port of Javascript code - https://github.com/walterbender/turtleblocksjs/blob/master/plugins/dictionary.rtp
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gettext import gettext as _

from plugins.plugin import Plugin

import httplib
import json

from TurtleArt.tapalette import make_palette
from TurtleArt.taprimitive import (ArgSlot, Primitive)
from TurtleArt.tatype import TYPE_STRING

class Dictionary(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self._parent = parent
        self.running_sugar = self._parent.running_sugar
        self._result = ""

    def setup(self):
        palette = make_palette('external',
                               colors=["#FF6060", "#A06060"],
                               help_string=_('Palette of blocks using external requests'),
                               position=10)

        palette.add_block('dictquery',
                              style='number-style-1arg',
                              label=_('define'),
                              default="mouse",
                              help_string=\
                                  _('word\'s definition from web dictionary'),
                              prim_name='dictquery')

        self._parent.lc.def_prim(
            'dictquery', 1,
            Primitive(self.prim_dictquery,
                      return_type=TYPE_STRING,
                      arg_descs=[ArgSlot(TYPE_STRING)]))

    def prim_dictquery(self, word):
        try:
            word = ''.join(e for e in word if e.isalnum()) # sanitize an argument
            rqst_conn = httplib.HTTPConnection('api.pearson.com')
            rqst_conn.request('GET', '/v2/dictionaries/entries?headword=' + word)
            response = rqst_conn.getresponse()
            json_data = json.loads(response.read())
            results = json_data['results']
            for row in results:
                if 'senses' in row:
                    for sense in row['senses']:
                        if 'subsenses' in sense:
                           if 'definition' in sense['subsenses'][0]:
                               if isinstance(sense['subsenses'][0]['definition'], list):
                                   return sense['subsenses'][0]['definition'][0]
                               return sense['subsenses'][0]['definition']
                        if 'definition' in sense:
                           if isinstance(sense['definition'], list):
                               return sense['definition'][0]
                           return sense['definition']
            return ''
        except:
            return 'error'
