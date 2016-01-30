#!/usr/bin/env python
# -*- coding=utf-8 -*-

import json
import simplejson
import time

__author__ = 'Riky'


class JsonProtocel:

    @staticmethod
    def pack(content, action, nickname='nickname'):
        pack_dict = {
            'nickname': nickname,
            'action': action,
            'content': content
        }
        return json.dumps(pack_dict)

    @staticmethod
    def unpack(json_data):
        dict = simplejson.loads(json_data, 'utf-8')
        return dict
