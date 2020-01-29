# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 15:17:48 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateutil
import pandas as pd
import ssl
import re
import locale
import unicodedata
from ast import literal_eval

def remove_itr(itr, exception):
    for elem in itr:
        if exception in elem:
            itr.remove(elem)

def remove_itr_not(itr, exception):
    for elem in itr:
        if exception not in elem:
            itr.remove(elem)


def try_itr1(itr, *exceptions, **kwargs):
    for elem in itr:
        try:
            link = elem.find('a').get('href')
            yield link
            if link == None:
                itr.remove(elem)
        except exceptions:
            pass


def funcion_scrap_lacapital_rosario():
    
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    
    
    html = requests.get("https://www.lacapital.com.ar/", verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html5lib')
    myarticles = soup.findAll('article')
    
    mylinks = list(try_itr1(myarticles, AttributeError))
    mylinks = list(try_itr1(myarticles, AttributeError))
    remove_itr_not(mylinks, '.html')
    remove_itr(mylinks, '/video/')
    remove_itr(mylinks, '/video/')
    remove_itr(mylinks, '/video/')
    remove_itr(mylinks, '/secciones/')
    remove_itr(mylinks, '/secciones/')
    
    
    
    diario_str = 'https://www.lacapital.com.ar'
    format = "%H:%M hs - %A %d de %B de %Y"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for link in mylinks:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_string = parser.find('p',{'class':'paragraph-date'}).text
            fecha_publicacion = datetime.strptime(fecha_string, format)
            cuerpo_nota = parser.findAll('div', {'class':'news-body-main'})[0]
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)    
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            pakete_dict['fecha-hora'].append(fecha_publicacion)
            pakete_dict['link'].append(link)
            pakete_dict['noticia'].append(nota)
        except:
            pass
        
    
    for nota in pakete_dict['noticia']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
     
    df = pd.DataFrame.from_dict(data = pakete_dict)
    
    
    df.to_csv('ultimas_noticias_lacapital_rosario_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_lacapital_rosario_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_lacapital_rosario_full.txt', mode = '+w', index = False, header = False)
