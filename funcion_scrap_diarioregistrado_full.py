# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 17:46:04 2020

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
import ssl
import pandas as pd
from datetime import datetime
import re
import unicodedata
from ast import literal_eval
import locale
def try_itrr(itr, diario_str, *exceptions):
    for elem in itr:
        try:
            link = elem.get('href')
            yield link
        except exceptions:
            pass
        
def new_itr(itr, exception, diario_str):
    for elem in itr:
        if exception not in elem:
            yield(diario_str+elem)

def funcion_scrap_diarioregistrado():
    
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    diario_str = 'https://www.diarioregistrado.com'
    html = requests.get("https://www.diarioregistrado.com/").text
    soup = BeautifulSoup(html, 'html5lib')
    links = soup.findAll('a')
    links = list(try_itrr(links, '' ,AttributeError))
    links = list(new_itr(links, 'diarioregistrado', diario_str))
    
    format = "%A %d de %B de %Y %H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    
    
    for link in links:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_hora_publicacion = datetime.strptime(parser.find('time').text, format)
            nota_tags = parser.find('div', {'class', 'article-body'}).findAll('p')
            nota = str()
            nota = nota.join(tag.text for tag in nota_tags)  
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
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
    
    df.to_csv('ultimas_noticias_diarioregistrado_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_diarioregistrado_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_diarioregistrado_full.txt', mode = '+w', index = False, header = False)
