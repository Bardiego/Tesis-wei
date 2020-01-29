# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 12:06:53 2019

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


def try_itr1(itr, *exceptions):
    for elem in itr:
        try:
            link = elem.find('a').get('href')
            yield link
        except exceptions:
            pass

def funcion_scrap_ambito():
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    
    html = requests.get("https://www.ambito.com/").text
    soup = BeautifulSoup(html, 'html5lib')
    contenedor = soup.find('main')
    myarticles = contenedor.findAll('article')
    
    links = list(try_itr1(myarticles, AttributeError))
            
    
    diario_str = 'https://www.ambito.com/'
    format = "%d %B %Y - %H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for link in links:
            try:
                html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
                parser = BeautifulSoup(html_p, 'html5lib')
                fecha_publicacion = datetime.strptime(parser.find('time', {'itemprop':'datePublished'}).text, format)       
                cuerpo_nota = parser.find('main').findAll('section', {'class':'body-content'})
                nota = ''
                nota = nota.join(tag.text for tag in cuerpo_nota)        
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
    
    
    
    df.to_csv('ultimas_noticias_ambito_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_ambito_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_ambito_full.txt', mode = '+w', index = False, header = False)
    
    
    
    
    
    
    
