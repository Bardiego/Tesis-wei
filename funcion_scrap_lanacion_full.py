# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 13:25:49 2019

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

def funcion_scrap_lanacion():
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    
    html = requests.get("https://www.lanacion.com.ar/ultimas-noticias", verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html5lib')
    mydivs = soup.find('section', {'class':'cuerpo'})
    myarts = mydivs.findAll('article')
    
    
    diario_str = 'https://www.lanacion.com.ar/'
    format = "%d-%B-%Y-%H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for articulo  in myarts:
        link = diario_str+articulo.find('a').get('href')
        hora = articulo.find('div', {'class':'hora'}).text
        html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
        parser = BeautifulSoup(html_p, 'html5lib')
        try:
            fecha = parser.find('section', {'class':'fecha'}).text.split()[0:5]
            
            fecha_hora_publicacion = datetime.strptime(fecha[0]+'-'+fecha[2]+'-'+fecha[-1]+'-'+hora, format)
            cuerpo_nota = parser.findAll('section', {'id':'cuerpo'})[0]
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
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
    
    
    df.to_csv('ultimas_noticias_lanacion_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_lanacion_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_lanacion_full.txt', mode = '+w', index = False, header = False)
