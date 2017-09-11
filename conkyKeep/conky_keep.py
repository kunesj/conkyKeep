#!/usr/bin/env python3
# encoding: utf-8

import os, shutil, traceback
import PIL

from .session_google import SessionGoogle
from .note_drawer import NoteDrawer
from .config_manager import CONFIG_MANAGER

# init cache ~/.cache/conkykeep
cache_path = os.path.join(os.path.expanduser("~"), '.cache', 'conkykeep')
os.makedirs(cache_path, exist_ok=True)

def display_note(img_path, vertical_offset):
    im = PIL.Image.open(img_path); w,h = im.size
    print("${image %s -p %i,%i -s %ix%i}" % (img_path, \
        CONFIG_MANAGER.getInt("General", "ConkyWidth")-w, vertical_offset, w, h), end="")
    return vertical_offset+h+CONFIG_MANAGER.getInt("Style", "NoteMargin")

def build_notes():
    note_max_size = tuple([CONFIG_MANAGER.getInt("General", "ConkyWidth"), \
        CONFIG_MANAGER.getInt("Style", "NoteMaxHeight")])
    nd = NoteDrawer(
        note_max_size = note_max_size,
        note_padding = CONFIG_MANAGER.getInt("Style", "NotePadding"),
        note_title_margin = CONFIG_MANAGER.getInt("Style", "NoteTitleMargin"),

        font_name = CONFIG_MANAGER.get("Style", "FontName"),
        font_size = CONFIG_MANAGER.getInt("Style", "FontSize"),
        font_color = tuple(CONFIG_MANAGER.getListInt("Style", "FontColor")),

        font_title_name = CONFIG_MANAGER.get("Style", "FontTitleName"),
        font_title_size = CONFIG_MANAGER.getInt("Style", "FontTitleSize"),
        font_title_color = tuple(CONFIG_MANAGER.getListInt("Style", "FontTitleColor"))
    )

    # remove old warn.png from cache
    warn_path = os.path.join(cache_path, "warn.png")
    if os.path.exists(warn_path): os.remove(warn_path)
    warn_note = None

    # download notes from google
    try:
        session = SessionGoogle(CONFIG_MANAGER.get("Login","Username"), \
            CONFIG_MANAGER.get("Login","Password"))
        notes = session.googleKeep_formatNotes(session.googleKeep_getNotes())
    except Exception:
        exc = traceback.format_exc()
        warn_note = {"color":"RED", "title":"!!!ERROR!!!", \
            "text":"ConkyKeep: Connection to GoogleKeep failed!!!"}
        if CONFIG_MANAGER.getBoolean("General", "ErrorTraceback"):
            warn_note["text"] += "\n%s" % exc
        # convert to warn.png
        warn_img = nd.drawNoteDict(warn_note)
        warn_img.save(warn_path)


    if warn_note is None:
        try:
            # filter notes
            filtered_notes = []
            for note in notes:
                allowed = False
                if CONFIG_MANAGER.getBoolean("Filter", "RemoveAll"):
                    if (note['id'] in CONFIG_MANAGER.getList("Filter", "AllowIds")) or \
                    (note['title'].lower() in \
                        CONFIG_MANAGER.getList("Filter", "AllowTitles", lowercase=True)):
                        allowed = True
                else:
                    if (note['id'] not in CONFIG_MANAGER.getList("Filter", "RemoveIds")) and \
                        (note['title'].lower() not in \
                            CONFIG_MANAGER.getList("Filter", "RemoveTitles", lowercase=True)):
                        allowed = True

                if allowed:
                    filtered_notes.append(note)

            # clear cache # TODO - reuse unchanged images from last run
            shutil.rmtree(cache_path)
            os.makedirs(cache_path, exist_ok=True)

            # convert notes to images (generate note img files 0.png, 1.png, ...)
            for i, note in enumerate(filtered_notes):
                note_img = nd.drawNoteDict(note)
                note_path = os.path.join(cache_path, "%s.png" % i)
                note_img.save(note_path)


        except Exception:
            exc = traceback.format_exc()
            warn_note = {"color":"RED", "title":"!!!ERROR!!!", \
                "text":"ConkyKeep: Something failed!!!"}
            if CONFIG_MANAGER.getBoolean("General", "ErrorTraceback"):
                warn_note["text"] += "\n%s" % exc
            # convert to warn.png
            warn_img = nd.drawNoteDict(warn_note)
            warn_img.save(warn_path)

    # display note images (display warning first)
    vertical_offset = 0
    if os.path.exists(warn_path):
        vertical_offset = display_note(warn_path, vertical_offset)
    i = 0;
    while True:
        note_path = os.path.join(cache_path, "%s.png" % i)
        if os.path.exists(note_path):
            vertical_offset = display_note(note_path, vertical_offset)
        else:
            break
        i = i+1

if __name__ == "__main__":
    build_notes()
