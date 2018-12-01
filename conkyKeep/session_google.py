#!/usr/bin/env python3
# encoding: utf-8

import requests
from bs4 import BeautifulSoup


class SessionGoogle:
    """
    Google Login code is based on http://stackoverflow.com/a/24881998
    """

    URL_LOGIN='https://accounts.google.com/ServiceLogin'
    URL_AUTH='https://accounts.google.com/ServiceLoginAuth'

    def __init__(self, login, pwd):
        self.ses = requests.session()
        login_html = self.ses.get(self.URL_LOGIN).text
        soup_login = BeautifulSoup(login_html, "lxml").find('form').findAll('input')
        dico = {}
        for u in soup_login:
            if u.get('value') is not None:
                dico[u['name']] = u['value']
        # override the inputs with out login and pwd:
        dico['Email'] = login
        dico['Passwd'] = pwd
        self.ses.post(self.URL_AUTH, data=dico)

    def get(self, URL):
        return self.ses.get(URL).text

    def getFile(self, URL):
        response = self.ses.get(URL)
        if not response.ok:
            raise Exception("Failed to download file from google: %s" % URL)

        filename = None
        for disp in response.headers['Content-Disposition'].split(";"):
            if disp.startswith("filename="):
                filename = disp[10:-1]
                break;

        return filename, response.content
