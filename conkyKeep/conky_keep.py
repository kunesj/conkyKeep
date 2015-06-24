# ! /usr/bin/python
# coding: utf-8

import os, sys
import argparse

try:
    from BeautifulSoup import BeautifulSoup
except:
    # windows fix
    from bs4 import BeautifulSoup 

from session_google import SessionGoogle

conf_file = 'config.xml'

path = os.path.dirname(os.path.abspath(__file__))
colors_path = os.path.join(path, 'colors')
conf_path = os.path.join(path, '..', conf_file) 

line_height = 16
line_height_title = 18

def getColorPath(color): # TODO - rest of colors
    """
    Returns:
        pathToBackgroundImage
    """
    return_path = os.path.join(colors_path, 'DEFAULT.png')
    if color == 'TEAL':
        return_path = os.path.join(colors_path, 'TEAL.png')
    elif color == 'RED':
        return_path = os.path.join(colors_path, 'RED.png')
    elif color == 'GREEN':
        return_path = os.path.join(colors_path, 'GREEN.png')
    elif color == 'BLUE':
        return_path = os.path.join(colors_path, 'BLUE.png')
    elif color == 'GRAY':
        return_path = os.path.join(colors_path, 'GRAY.png')
    elif color in ['DEFAULT', 'WHITE', None, 'None']:
        return_path = os.path.join(colors_path, 'DEFAULT.png')
    else:
        print "${color black}Unknown color "+str(color)+"${color}",
        
    return return_path

def format_conky_note(note, vertical_offset=0):
    # get path to background color image
    colorPath = getColorPath(note['color'])
    
    # background color height
    background_height = len(note['text'].split('\n'))*line_height
    background_height += line_height # hr
    if note['title'].strip() != '':
        background_height += line_height_title
    
    # background color width
    background_width = 330+10
    
    # add colored background
    print "${image "+colorPath+" -p -5,"+str(vertical_offset)+" -s "+str(background_width)+"x"+str(background_height)+"}",
    print "${color black}",
    
    # add vertical line
    print '${goto 0}${hr 2}'
    
    # add title + text
    if note['title'].strip() != '':
        print '${font Arial:bold:size=12}'+note['title']+'${font}'
    print '${font Arial:size=10}'+note['text']+'${font}'
    
    # reset font + color
    print "${color}${font}",
    
    # return new vertical offset
    return background_height+vertical_offset-1
    
def get_config():
    bs_conf = BeautifulSoup(open(conf_path, "r")).configuration
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

    return conf 
    
def main():
    config = get_config()    
    
    session = SessionGoogle(config['login']['username'], \
        config['login']['password'])
    notes = session.googleKeep_getNotes()
    
    vertical_offset = int(line_height/2)
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
            vertical_offset = format_conky_note(note, vertical_offset)
    
if __name__ == "__main__":
    main()
