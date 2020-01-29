# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 19:15:59 2020

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
import dateutil
        
def new_itr(itr, exception, diario_str):
    for elem in itr:
        if exception in elem:
            yield(diario_str+elem)
            
def try_itr1(itr, diario_str, *exceptions):
    for elem in itr:
        try:
            link = elem.find('a').get('href')
            yield diario_str+link
        except exceptions:
            pass

def funcion_scrap_eldestapeweb():
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    diario_str = 'https://www.eldestapeweb.com'
    html = requests.get("https://www.eldestapeweb.com/").text
    soup = BeautifulSoup(html, 'html5lib')
    articulos = soup.findAll('article')
    links = list(try_itr1(articulos, '' ,AttributeError))
    links = list(new_itr(links, '/nota/', diario_str))
    
    format = "%Y-%m-%d,%H:%M"
    format1 = "%d de %B, %Y-%H.%M"
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    
    
    for link in links:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_hace = parser.find('div', {'class':'fecha'}).span.text
            if fecha_hace.split()[2] == 'horas' or fecha_hace[1]  == 'hora':
                tiempo_hace = fecha_hace.split()[1]
                fecha_actual = datetime.now()
                fecha_publicacion = fecha_actual - dateutil.relativedelta.relativedelta(hours=int(tiempo_hace))
                fecha_publicacion_real = datetime.strptime(str(fecha_publicacion.year)+'-'+str(fecha_publicacion.month)+'-'+str(fecha_publicacion.day)+','+str(fecha_publicacion.hour)+':'+str(fecha_publicacion.minute), format)
            elif fecha_hace.split()[2] == 'minutos' or fecha_hace[1]  == 'minuto':
                tiempo_hace = fecha_hace.split()[1]
                fecha_actual = datetime.now()
                fecha_publicacion = fecha_actual - dateutil.relativedelta.relativedelta(minutes=int(tiempo_hace))
                fecha_publicacion_real = datetime.strptime(str(fecha_publicacion.year)+'-'+str(fecha_publicacion.month)+'-'+str(fecha_publicacion.day)+','+str(fecha_publicacion.hour)+':'+str(fecha_publicacion.minute), format)
            else:
                fecha_publicacion_real = datetime.strptime(fecha_hace+'-'+parser.find('div', {'class':'fecha'}).find('span', {'class':'hora'}).text.split('|')[1].strip(), "%d de %B, %Y-%H.%M")
            nota_tags = parser.find('div', {'itemprop':'articleBody'}).findAll('p')
            nota = str()
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
    
    df.to_csv('ultimas_noticias_eldestapeweb_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_eldestapeweb_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_eldestapeweb_full.txt', mode = '+w', index = False, header = False)
