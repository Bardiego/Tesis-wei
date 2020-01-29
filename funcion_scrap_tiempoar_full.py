# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 20:43:00 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
import csv
from datetime import date
import pandas as pd
from datetime import datetime
import locale
import dateutil
import ssl
import re
import unicodedata
from ast import literal_eval

def funcion_scrap_tiempoar():
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    
    html = requests.get("https://www.tiempoar.com.ar/", verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html5lib')
    columnas = soup.findAll('div', {'class':'block-public-container'})
    
    articulos = []
    
    for columna in columnas:
        try:
            for art in columna:
                artic = art.findAll('a')
                for articu in artic:
                    link = articu.get('href')
                    if link not in articulos:
                        articulos.append(link)
        except  AttributeError:
            pass
    
    
    
    diario_str = 'https://www.tiempoar.com.ar/'
    format = "%d de %B de %Y - %H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    
    for link in articulos:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            tiempo= datetime.now()
            horas = tiempo.hour
            minutos = tiempo.minute
            fecha_publicacion_string = parser.find('span', {'class':'release-date'}).text
            if int(fecha_publicacion_string.split()[0]) == tiempo.day:
                fecha_publicacion_string = parser.find('span', {'class':'release-date'}).text+ ' - '+ str(tiempo.hour) +':'+ str(tiempo.minute)
                fecha_hora_publicacion = datetime.strptime(fecha_publicacion_string, format)
                cuerpo_nota = parser.find('div', {'class':'body'})
                nota_tags = cuerpo_nota.findAll('p')
                nota = ''
                nota = nota.join(tag.text for tag in nota_tags)
                nota = unicodedata.normalize("NFKD", nota)
                nota = nota.replace('\n','').replace('u200b', '')
                pakete_dict['fecha-hora'].append(fecha_hora_publicacion)
                pakete_dict['link'].append(link)
                pakete_dict['noticia'].append(nota) 
                
            else:
                pass
        except:
            pass
            
            
    for nota in pakete_dict['noticia']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
        
    df = pd.DataFrame.from_dict(data = pakete_dict)
    
    
    df.to_csv('ultimas_noticias_tiempoar_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_tiempoar_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='first')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_tiempoar_full.txt', mode = '+w', index = False, header = False)
