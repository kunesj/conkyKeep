#!/usr/bin/env python3
# encoding: utf-8

import PIL
from PIL import ImageFont, ImageDraw
import numpy as np

class NoteDrawer(object):
    COLORS = {"RED":"#ff8a80", "GREEN":"#ccff90", "BLUE":"#80d8ff", "WHITE":"#fafafa",
        "ORANGE":"#ffd180", "YELLOW":"#ffff8d", "GRAY":"#cfd8dc", "TEAL":"#a7ffeb" }
    COLORS["DEFAULT"] = COLORS["WHITE"]
    COLORS[None] = COLORS["DEFAULT"]; COLORS["None"] = COLORS["DEFAULT"]

    def __init__(self, note_max_size=(1900,1000), note_padding=10, note_title_margin=10, \
        note_border=1, note_border_color=(0,0,0), \
        font_name="arial.ttf", font_size=12, font_color=(0,0,0), \
        font_title_name="arialbd.ttf", font_title_size=14, font_title_color=(0,0,0) ):
        self.note_max_size = note_max_size
        self.note_padding = note_padding
        self.note_title_margin = note_title_margin
        self.note_border = note_border
        self.note_border_color = note_border_color

        self.font_name = font_name
        self.font_size = font_size
        self.font = ImageFont.truetype(self.font_name, self.font_size)
        self.font_color = font_color

        self.font_title_name = font_title_name
        self.font_title_size = font_title_size
        self.font_title = ImageFont.truetype(self.font_title_name, self.font_title_size)
        self.font_title_color = font_title_color


    def getNoteSize(self, title, text):
        """ Computes required note size (with padding), and title height (with padding) """
        used_size = (self.note_max_size[0]-2*self.note_padding, self.note_max_size[1]-2*self.note_padding)

        # get title_h
        bg = PIL.Image.new("L", used_size) # grayscale image
        draw = ImageDraw.Draw(bg)
        draw.text((0, 0), title, (255,), font=self.font_title)
        draw = ImageDraw.Draw(bg)
        bgarr = np.array(bg)
        title_h = np.max(np.nonzero(np.sum(bgarr, axis=1))) # without padding

        # get note_w, note_h
        bg = PIL.Image.new("L", used_size)
        note_img = self.drawText(bg, title, title_h, text, padding=0, \
            font_color=(255,), font_title_color=(255,))

        # compute note size without padding
        imgarr = np.array(note_img)
        note_w = np.max(np.nonzero(np.sum(imgarr, axis=0)))
        note_h = np.max(np.nonzero(np.sum(imgarr, axis=1)))

        # add padding to computed size
        note_w = (note_w+1)+2*self.note_padding # +1 because indexing starts at 0
        note_h = (note_h+1)+2*self.note_padding
        title_h = title_h+self.note_padding

        return note_w, note_h, title_h

    def drawText(self, bg, title, title_h, text, padding=0, \
            font_color=(0,0,0), font_title_color=(0,0,0)):
        """
        Draws text on given background
        title_h - height of title text (without padding)
        """
        draw = ImageDraw.Draw(bg)

        # title
        draw.text((0+padding, 0+padding), title, font_title_color, font=self.font_title)
        draw = ImageDraw.Draw(bg)

        # text
        draw.text((0+padding, title_h+self.note_title_margin), text, font_color, font=self.font)
        draw = ImageDraw.Draw(bg)

        return bg

    def drawBackground(self, size, color): # TODO - decorated borders
        bg = PIL.Image.new("RGBA", size, self.COLORS[color])

        # draw border
        if self.note_border >= 1:
            draw = ImageDraw.Draw(bg)
            draw.rectangle(((0, 0), (size[0]-1, self.note_border)), fill=self.note_border_color)
            draw.rectangle(((0, 0), (self.note_border, size[1]-1)), fill=self.note_border_color)
            draw.rectangle(((size[0]-1, 0), (size[0]-1-self.note_border, size[1]-1)), fill=self.note_border_color)
            draw.rectangle(((0, size[1]-1), (size[0]-1, size[1]-1-self.note_border)), fill=self.note_border_color)
            draw = ImageDraw.Draw(bg)

        return bg

    def drawNote(self, title, text, color):
        note_w, note_h, title_h = self.getNoteSize(title, text)
        bg = self.drawBackground((note_w, note_h), color)
        note_img = self.drawText(bg, title, title_h, text, padding=self.note_padding, \
            font_color=self.font_color, font_title_color=self.font_title_color)
        return note_img

    def drawNoteDict(self, note):
        return self.drawNote(note["title"], note["text"], note["color"])

if __name__ == "__main__":
    nd = NoteDrawer()
    title = "Test Text"
    text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit
anim id est laborum."""

    img = nd.drawNote(title, text, "RED")
    img.save('out.png')



