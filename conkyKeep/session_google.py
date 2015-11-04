#!/usr/bin/python2
# coding: utf-8

import sys

import requests
from BeautifulSoup import BeautifulSoup

# for JavaScript variables compatibility
false = False
true = True

class SessionGoogle:
    """
    Google Login code is based on http://stackoverflow.com/a/24881998
    
    googleKeep_data - Notes from GoogleKeep    
    googleKeep_data['id']       - id of note
    googleKeep_data['parentId'] - id of parent "note"
    googleKeep_data['title']    - title of note
    googleKeep_data['text']     - text inside of note
    googleKeep_data['color']    - color of note 
    data['serverId']
    data['timestamps']
    data['labelIds']
    data['baseVersion']
    data['abuseFeedback']
    data['errorStatus']
    data['kind'] 
    data['checked']  
    data['type'] 
    data['shareRequests'] 
    data['nodeSettings']   
    data['reminders'] 
    data['sortValue'] 
    data['roleInfo'] 
    data['parentServerId'] 
    data['isArchived']
    +other
    """
    
    googleKeep_data_raw = []
    googleKeep_data = []
    
    def __init__(self, login, pwd, url_login="https://accounts.google.com/ServiceLogin", url_auth="https://accounts.google.com/ServiceLoginAuth"):
        self.ses = requests.session()
        login_html = unicode(self.ses.get(url_login).text)
        soup_login = BeautifulSoup(login_html).find('form').findAll('input')
        dico = {}
        for u in soup_login:
            if u.get('value') is not None:
                dico[u['name']] = u['value']
        # override the inputs with out login and pwd:
        dico['Email'] = login
        dico['Passwd'] = pwd
        self.ses.post(url_auth, data=dico)

    def get(self, URL):
        return self.ses.get(URL).text
        
    def googleKeep_getNotes(self):
        html = self.get("https://keep.google.com/")
        bs = BeautifulSoup(unicode(html))
        script = bs.body.findAll('script')[1].text
        script_loadChunk = script.split(';')[0]
        
        # fill self.googleKeep_data_raw
        data = script_loadChunk.split('loadChunk(')[1]
        data = ", ".join(data.split(', ')[:-1])
        self.googleKeep_data_raw = eval(data)
        
        self.googleKeep_data = []
        notes_info = []
        for data in self.googleKeep_data_raw:
            # ignore trashed (removed) notes
            trashed = data['timestamps']['trashed']
            if trashed != '1970-01-01T00:00:00.000Z':
                continue
            
            if 'title' in data: # note settings
                notes_info.append(data)
            else:
                # set default not settings values
                if 'title' not in data:
                    data['title'] = ''
                if 'color' not in data:
                    data['color'] = 'DEFAULT'

                self.googleKeep_data.append(data)
            
        for info in notes_info: 
            for data in self.googleKeep_data:                
                if data['parentId'] == info['id']:
                    if 'color' in info:
                        data['color'] = info['color']
                    data['title'] = info['title'].strip()
        
        return self.googleKeep_data
        
    def googleKeep_formatNotes(self, notes=None, short=False):
        if notes is None:
            notes = self.googleKeep_data
        
        formated_notes = []
        for note in notes:
            s = ""
            
            if short is True:
                s = "id: "+str(note['id']) +"\n"+ \
                    "color: "+str(note['color']) +"\n"+ \
                    "title: "+str(note['title']) +"\n"+ \
                    "text: "+str(note['text'])
            else:
                for key in note:
                    s += str(key)+": "+str(note[key])+"\n"
            
            s = s.strip()
            formated_notes.append(s)
        
        return formated_notes

if __name__ == "__main__":
    print "USAGE: python2 session_google.py USERNAME PASSWORD"
    if len(sys.argv)!=3:
        print "ERROR: Bad number of arguments"
        sys.exit(2)
            
    session = SessionGoogle(str(sys.argv[1]), str(sys.argv[2]))
    notes = session.googleKeep_getNotes()
    f_notes = session.googleKeep_formatNotes(notes, False)

    for note in f_notes:
        print "------------------------------"
        print note
