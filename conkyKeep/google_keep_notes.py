#!/usr/bin/env python3
# encoding: utf-8

import sys
import os
import copy

from .google_keep_parsers import ParserGkeepapi, ParserSoup


class GoogleKeepNotes(object):

    NOTES_CACHEFILE = 'notes.cache'

    def __init__(self, login, pwd, cache_path=None, note_list_hide_checked=False, parser='soup'):
        assert parser in ['soup', 'gkeepapi']

        if parser.lower() == 'soup':
            self.parser = ParserSoup(login, pwd, cache_path=cache_path)
        elif parser.lower() == 'gkeepapi':
            self.parser = ParserGkeepapi(login, pwd, cache_path=cache_path)
        else:
            raise Exception('Invalid parser "{}"!'.format(parser))

        self.note_list_hide_checked = note_list_hide_checked

    def getNotes(self, raw=False):
        notes = self.parser.getNotes()
        if not raw:
            # filter out deleted and trashed notes
            tmp = []
            for n in notes:
                if 'trashed' in n['timestamps']:
                    if not n['timestamps']['trashed'].startswith('1970-01-01'):
                        continue
                if 'deleted' in n['timestamps']:
                    if not n['timestamps']['deleted'].startswith('1970-01-01'):
                        continue
                tmp.append(n)
            notes = tmp

            # init new and missing data fields
            for n in notes:
                n['childNotes'] = []
                n['parentServerId'] = None
                if 'sortValue' not in n:
                    n['sortValue'] = 0

            # build tree
            root_notes = []
            for cn in notes:
                # get root notes
                if cn['parentId'] == 'root':
                    root_notes.append(cn)
                    continue

                # add child notes to parent notes
                for pn in notes:
                    if cn['parentId'] == pn['id']:
                        cn['parentServerId'] = pn['serverId']
                        pn['childNotes'].append(cn)

            notes = root_notes
        return notes

    def formatNotes(self, notes, child=False):
        """
        requires 'childNotes' and 'parentServerId' in note data
        """
        # create copy of notes before modifications
        notes = copy.deepcopy(notes)
        # sort notes (also later sorts children notes in recursive runs)
        notes = sorted(notes, key=lambda k: int(k['sortValue']), reverse=True)

        for rn in notes:
            # recursivelly format child notes
            if 'childNotes' in rn:
                childNotes = self.formatNotes(rn['childNotes'], child=True)
            # create formated text variable
            if 'text' not in rn:
                rn['text'] = ""
            rn['formatedText'] = rn['text']

            ## Root type notes
            if rn['type'] == "NOTE": # if text note (root note type)
                # add formated text from child notes
                for cn in childNotes:
                    if rn['formatedText'] != "":
                        rn['formatedText'] += "\n"
                    rn['formatedText'] += cn['formatedText']

            elif rn['type'] == "LIST": # if List note (root note type)
                for cn in childNotes:
                    if 'checked' in cn:
                        if cn['checked'] and self.note_list_hide_checked:
                            continue

                    if rn['formatedText'] != "":
                        rn['formatedText'] += "\n"

                    if 'checked' in cn:
                        if cn['checked']:
                            rn['formatedText'] += "[*] "
                        else:
                            rn['formatedText'] += "[ ] "

                    rn['formatedText'] += cn['formatedText']

            ## Child type notes
            elif rn['type'] == 'LIST_ITEM': # if text note or list item
                rn['formatedText'] = rn['text']

            elif rn['type'] == 'BLOB': # if image note
                rn['formatedText'] = "[BLOB mime='"+rn['blob']['mimetype']+"' url='https://keep.google.com/media/v2/"+rn['parentServerId']+"/"+rn['serverId']+"?s=0']"
            else:
                print("Unknown NoteType:%s not implemented!", (rn['type'],))

        # remove unneeded values and add missing default values
        if not child:
            formated_notes = []
            for n in notes:
                _note = {
                    'text': n['formatedText'],
                    'color': "DEFAULT",
                    'title': "",
                    'type': "NOTE",
                    'id': 0
                }

                if 'color' in n:
                    _note['color'] = n['color']
                if 'title' in n:
                    _note['title'] = n['title']
                if 'type' in n:
                    _note['type'] = n['type']
                if 'id' in n:
                    _note['id'] = n['id']

                formated_notes.append(_note)
        else:
            formated_notes = notes

        return formated_notes


if __name__ == "__main__":
    print("USAGE: python3 google_keep_notes.py USERNAME PASSWORD")
    if len(sys.argv)!=3:
        print("ERROR: Bad number of arguments")
        sys.exit(2)

    cache_path = os.path.join(os.path.expanduser("~"), '.cache', 'conkykeep')
    os.makedirs(cache_path, exist_ok=True)

    gkn = GoogleKeepNotes(str(sys.argv[1]), str(sys.argv[2]), cache_path=cache_path)
    notes = gkn.getNotes()
    f_notes = gkn.formatNotes(notes)

    for note in f_notes:
        print("---------------------------------------------------------------")
        print(note)
