# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 13:02:27 2019

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

def funcion_scrap_clarin():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    html = requests.get("https://www.clarin.com/ultimas-noticias/").text
    soup = BeautifulSoup(html, 'html5lib')
    
    articulos = soup.findAll('article')
    diario_str = 'https://www.clarin.com'
    format = "\n\n%d/%m/%Y - %H:%M\n"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    
    
    for articulo in articulos:
        try:
            link = str(diario_str)+articulo.find('a').get('href')
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_hora = parser.find('div', {'class','breadcrumb col-lg-6 col-md-12 col-sm-12 col-xs-12'}).find('span').text
            fecha_hora_publicacion = datetime.strptime(fecha_hora, format)
            cuerpo_nota = parser.findAll('div', {'class':'body-nota'})[0]
            nota_tags = cuerpo_nota.findAll('p')
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
    
    df.to_csv('ultimas_noticias_clarin_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_clarin_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_clarin_full.txt', mode = '+w', index = False, header = False)
    
    