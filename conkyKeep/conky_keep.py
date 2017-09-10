#!/usr/bin/env python3
# encoding: utf-8

import os, sys, shutil, traceback

from bs4 import BeautifulSoup
import PIL

from conkyKeep.session_google import SessionGoogle
from conkyKeep.note_drawer import NoteDrawer

NOTE_MARGIN = 5
CONKY_WIDTH = 1000 # None -> will compute minimal value
ERROR_TRACEBACK = False

# get path to app dir
path = os.path.dirname(os.path.abspath(__file__))

# get config file path
# config file in same folder has higher priority
conf_file = 'config.xml'
if os.path.isfile(os.path.join(path, conf_file)): # config in same folder as conkyKeep.sh (../)
    conf_path = os.path.join(path, '..', conf_file)
else: # config in ~/.config/conkykeep folder
    try:
        import appdirs
        app_config_dir = appdirs.user_config_dir('conkykeep')
    except:
        app_config_dir = os.path.join(os.path.expanduser("~"), '.config', 'conkykeep')

    conf_path = os.path.join(app_config_dir, conf_file)
if not os.path.isfile(conf_path):
    print("ERROR: config file not found in: %s" % (conf_path,))

# init cache ~/.cache/conkykeep
cache_path = os.path.join(os.path.expanduser("~"), '.cache', 'conkykeep')
os.makedirs(cache_path, exist_ok=True)

def get_config():
    bs_conf = BeautifulSoup(open(conf_path, "r"), "lxml").configuration
    conf = {}

    # login info
    login_conf = {'username': bs_conf.login.username.text.strip(), \
        'password': bs_conf.login.password.text.strip()}
    conf['login'] = login_conf

    # filter
    filter_conf = {'ids':[], 'titles':[], 'removeall':False}

    filt = bs_conf.find('filter')
    if filt.find('removeall') is not None:
        if 'yes' == filt.find('removeall').text.lower().strip():
            filter_conf['removeall'] = True
        else:
            filter_conf['removeall'] = False

    if filter_conf['removeall']:
        ids = filt.findAll('allowid')
        titles = filt.findAll('allowtitle')
    else:
        ids = filt.findAll('removeid')
        titles = filt.findAll('removetitle')

    for a in ids:
        filter_conf['ids'].append(a.text.lower().strip())
    for a in titles:
        filter_conf['titles'].append(a.text.lower().strip())

    conf['filter'] = filter_conf

    # style
    # TODO

    # misc
    # TODO

    return conf

def display_note(img_path, vertical_offset, conky_width):
    im = PIL.Image.open(img_path)
    w,h = im.size
    print("${image %s -p %i,%i -s %ix%i}" % (img_path, conky_width-w, vertical_offset, w, h), end="")
    return vertical_offset+h+NOTE_MARGIN

def main():
    config = get_config()
    nd = NoteDrawer()
    warn_note = None

    # remove warn.png from cache
    warn_path = os.path.join(cache_path, "warn.png")
    if os.path.exists(warn_path): os.remove(warn_path)

    # download notes from google
    try:
        session = SessionGoogle(config['login']['username'], \
            config['login']['password'])
        notes = session.googleKeep_formatNotes(session.googleKeep_getNotes())
    except Exception:
        exc = traceback.format_exc()
        warn_note = {"color":"RED", "title":"!!!ERROR!!!", \
            "text":"ConkyKeep: Connection to GoogleKeep failed!!!"}
        if ERROR_TRACEBACK:
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
                if config['filter']['removeall']:
                    if (note['id'] in config['filter']['ids']) or \
                    (note['title'].lower() in config['filter']['titles']):
                        allowed = True
                else:
                    if (note['id'] not in config['filter']['ids']) and \
                        (note['title'].lower() not in config['filter']['titles']):
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
            if ERROR_TRACEBACK:
                warn_note["text"] += "\n%s" % exc
            # convert to warn.png
            warn_img = nd.drawNoteDict(warn_note)
            warn_img.save(warn_path)

    # compute conky width
    if CONKY_WIDTH is None:
        conky_width = 0
        for item in os.listdir(cache_path):
            if not item.lower().endswith(".png"): continue
            img_path = os.path.join(cache_path, item)
            im = PIL.Image.open(img_path)
            w,h = im.size
            conky_width = max(conky_width, w)
    else:
        conky_width = CONKY_WIDTH

    # display note images (display warning first)
    vertical_offset = 0
    if os.path.exists(warn_path):
        vertical_offset = display_note(warn_path, vertical_offset, conky_width)
    i = 0;
    while True:
        note_path = os.path.join(cache_path, "%s.png" % i)
        if os.path.exists(note_path):
            vertical_offset = display_note(note_path, vertical_offset, conky_width)
        else:
            break
        i = i+1

if __name__ == "__main__":
    main()
