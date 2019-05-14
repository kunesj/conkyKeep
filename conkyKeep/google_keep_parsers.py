#!/usr/bin/env python3
# encoding: utf-8

import sys
import os
import copy
import json

import requests
from bs4 import BeautifulSoup

import gkeepapi
from .session_google import SessionGoogle


class ParserGkeepapi(object):

    NOTES_CACHEFILE = 'notes.cache'

    def __init__(self, login, pwd, cache_path=None, **kwargs):
        self.keep = gkeepapi.Keep()
        self.keep.login(login, pwd)

        if cache_path is not None:
            cachefile_path = os.path.join(cache_path, self.NOTES_CACHEFILE)
            # restore dat from cache
            if os.path.exists(cachefile_path):
                with open(cachefile_path, 'r') as fh:
                    self.keep.restore(json.load(fh))
            # update data
            try:
                self.keep.sync()
            except gkeepapi.exception.ResyncRequiredException:
                self.keep = gkeepapi.Keep()
                self.keep.login(login, pwd)
                self.keep.sync()
            # save updated data to cache
            with open(cachefile_path, 'w') as fh:
                json.dump(self.keep.dump(), fh)
        else:
            self.keep.sync()

    def getNotes(self):
        return self.keep.dump()['nodes']


class ParserSoup(object):

    def __init__(self, login, pwd, **kwargs):
        self.session = SessionGoogle(login, pwd)

    def getNotes(self):
        html = self.session.get("https://keep.google.com/")

        # get part of html with notes data
        bs = BeautifulSoup(html, "lxml")

        # find correct script: "<script type="text/javascript">preloadUserInfo(JSON.parse("
        script = None
        for s in bs.body.findAll('script', attrs={'type': 'text/javascript'}):
            if s.text.strip().startswith("preloadUserInfo(JSON.parse("):
                script = s; continue
        if script is None:
            raise Exception("Couldn't find correct <script> tag!")

        # find section with json data
        script_loadChunk = script.text.split(";loadChunk(JSON.parse('")[-1]
        data = "'), ".join(script_loadChunk.split("'), ")[:-1])

        # convert \x?? charcters
        while data.find('\\x') != -1:
            index = data.find('\\x')
            hex_str = data[index:index+4]
            val = int(data[index+2:index+4], 16)
            data = data.replace(hex_str, chr(val))

        # remove redundant \
        data = data.replace('\\\\','\\')

        # decode json string
        return json.loads(data) # encodes string to utf-8 ?
