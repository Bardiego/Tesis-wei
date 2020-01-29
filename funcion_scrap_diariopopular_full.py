# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:43:05 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import locale
import ssl
import re
import unicodedata
from ast import literal_eval

def try_itr1(itr, *exceptions, **kwargs):
    for elem in itr:
        try:
            link = elem.find('a').get('href')
            yield link
        except exceptions:
            pass

def remove_itr_not(itr, exception):
    for elem in itr:
        if exception not in elem[12:25]:
            itr.remove(elem)

def funcion_scrap_diariopopular():
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    

    html = requests.get("https://www.diariopopular.com.ar/", verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html5lib')
    mydivs = soup.findAll('article')
    mylinks = list(try_itr1(mydivs, AttributeError))
    remove_itr_not(mylinks, 'diariopopular')    
    
    format = "%d de %B de %Y - %H:%M"
    
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for link  in mylinks:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')            
            fecha  = parser.find('div', {'class':'fecha-detallenota'}).text.split('\n')[0]
            hora = parser.find('div', {'class':'fecha-detallenota'}).text.split('\n')[1].split()[1]
            fecha_hora_publicacion = datetime.strptime(fecha+' - '+hora, format)
            
            cuerpo_nota = parser.findAll('article', {'id':'article-post'})
            nota_tags = [cuerpo.findAll('p') for cuerpo in cuerpo_nota if cuerpo.findAll('p')!=[]]
            nota = ''
            nota = nota.join(tag.text for tags in nota_tags for tag in tags)
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '').replace('\x93', '"')
            pakete_dict['fecha-hora'].append(fecha_hora_publicacion)
            pakete_dict['link'].append(link)
            pakete_dict['noticia'].append(nota)
        except:
            pass
    
    
    for nota in pakete_dict['noticia']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
    
    df = pd.DataFrame.from_dict(data = pakete_dict)
    
    
    df.to_csv('ultimas_noticias_diariopopular_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_diariopopular_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_diariopopular_full.txt', mode = '+w', index = False, header = False)
