# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 13:02:27 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
from datetime import date
import pandas as pd
import datetime
import ssl
import re
import unicodedata
from ast import literal_eval

def try_itr1(itr, diario_str, *exceptions):
    for elem in itr:
        try:
            link = elem.find('a').get('href')
            yield diario_str+link
        except exceptions:
            pass

def new_itr(itr, exception):
    for elem in itr:
        if exception in elem:
            yield elem

def funcion_scrap_pagina12():
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    
    html = requests.get("https://www.pagina12.com.ar/").text
    soup = BeautifulSoup(html, 'html5lib')
    articulos = soup.findAll('article')
    links = list(try_itr1(articulos, ''))
    links = list(new_itr(links, 'pagina12'))
    
    
    diario_str = 'https://www.pagina12.com.ar'
    format = "%Y-%m-%d,%H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for link in links:
        try:        
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            soup = BeautifulSoup(html_p, 'html5lib')
            try:
                fecha_publicacion = datetime.datetime.fromtimestamp(float(soup.select_one('[data-time]')['data-time']))
                fecha_publicacion_real = datetime.datetime.strptime(str(fecha_publicacion.year)+'-'+
                                                           str(fecha_publicacion.month)+'-'+
                                                           str(fecha_publicacion.day)+','+
                                                           str(fecha_publicacion.hour)+':'+
                                                           str(fecha_publicacion.minute), format)
            except:
                if int(soup.find('div', {'class':'time'}).find('span').text.split()[0]) == datetime.datetime.now().day:
                    fecha_publicacion_real = datetime.datetime.strptime(soup.find('div', {'class':'time'}).find('span').text+ ' '+ str(datetime.datetime.now().hour) +':'+ str(datetime.datetime.now().minute), '%d de %B de %Y %H:%M')
                else:
                    pass
            cuerpo_nota = soup.find('div', {'class':'article-text'})
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            pakete_dict['fecha-hora'].append(fecha_publicacion_real)
            pakete_dict['link'].append(link)
            pakete_dict['noticia'].append(nota)
            
        except:
            pass
            
    
    for nota in pakete_dict['noticia']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
    
    df = pd.DataFrame.from_dict(data = pakete_dict)
    
    
    df.to_csv('ultimas_noticias_pagina12_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_pagina12_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_pagina12_full.txt', mode = '+w', index = False, header = False)

