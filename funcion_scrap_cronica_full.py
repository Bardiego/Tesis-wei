# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 14:20:58 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import ssl
from requests.adapters import SSLError
import re
import unicodedata
from ast import literal_eval


def funcion_scrap_cronica():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    
    
    html = requests.get("https://www.cronica.com.ar/").text
    soup = BeautifulSoup(html, 'html5lib')
    mydivs = soup.findAll('div', {'class':'site-content'})
    mylinks = mydivs[0].findAll('a', {'class':'cover-link'})
    
    
    diario_str = 'https://www.cronica.com.ar'
    
    
    mylinks_filtered = []
    for link in mylinks:
        if 'cronica' not in link.get('href'):
            if '.com' not in link.get('href'):
                mylinks_filtered.append(diario_str+link.get('href'))
        else:
            mylinks_filtered.append(link.get('href'))
    
    
    format = "%d-%m-%Y %H:%M"
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    
    for link_fecha in mylinks_filtered:
        try:
            html_p = requests.get(link_fecha, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            contenido = parser.find('div', {'class':'site-content'})
            fecha = contenido.find('time').text
            fecha_hora_publicacion = datetime.strptime(fecha, format)
            cuerpo_nota =  parser.findAll('div', {'itemprop':'articleBody'})[0]
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags)
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            pakete_dict['fecha-hora'].append(fecha_hora_publicacion)
            pakete_dict['link'].append(link_fecha)
            pakete_dict['noticia'].append(nota)
        except:
            pass
        
        
    for nota in pakete_dict['noticia']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
        
    df = pd.DataFrame.from_dict(data = pakete_dict)
    
    
    
    df.to_csv('ultimas_noticias_cronica_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_cronica_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_cronica_full.txt', mode = '+w', index = False, header = False)
