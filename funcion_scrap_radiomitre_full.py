# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 17:06:52 2020

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

def try_itr1(itr, diario_str, *exceptions):
    for elem in itr:
        try:
            link = elem.find('a').get('href')
            yield diario_str+link
        except exceptions:
            pass

def funcion_scrap_radiomitre():
    
    diario_str = 'https://radiomitre.cienradios.com/'
    
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    html = requests.get("https://radiomitre.cienradios.com/").text
    soup = BeautifulSoup(html, 'html5lib')
    
    articulos = soup.findAll('div', {'class':'articles-item'})
    links = list(try_itr1(articulos, '',AttributeError))
    
    format = "%d %B, %Y %H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    
    
    for link in links:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_hora_publicacion = datetime.strptime(parser.find('div', {'class':'article-date'}).text, format)
            nota_tags = parser.find('div', {'class', 'article-content-box'}).findAll('p')
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
    
    df.to_csv('ultimas_noticias_radiomitre_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_radiomitre_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_radiomitre_full.txt', mode = '+w', index = False, header = False)
