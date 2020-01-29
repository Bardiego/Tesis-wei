# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 16:53:57 2020

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

def try_itr1(itr, *exceptions, **kwargs):
    for elem in itr:
        try:
            link = elem.find('a').get('href')
            yield link
        except exceptions:
            pass


def remove_itr(itr, exception):
    for elem in itr:
        if exception not in elem:
            yield elem

def remove_itr1(itr, exception):
    for elem in itr:
        if exception in elem:
            yield elem


def funcion_scrap_minutouno():
    
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    html = requests.get("https://www.minutouno.com/").text
    soup = BeautifulSoup(html, 'html5lib')
    
    articulos = soup.findAll('article')
    diario_str = 'https://www.minutouno.com/'
    format = "%d de %B de %Y %H:%M"
    
    links = list(try_itr1(articulos, AttributeError))
    links = list(filter(None, links))
    links = list(remove_itr(links, 'ratingcero'))
    links = list(remove_itr1(links, '/notas/'))
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    
    
    for link in links:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            try:
                fecha_publicacion = datetime.strptime(parser.find('span', {'class':'date'}).text,format)
            except ValueError:
                fecha_publicacion = datetime.strptime(parser.find('span', {'class':'date'}).text+ ' '+ str(datetime.now().hour) +':'+ str(datetime.now().minute), format)
            cuerpo_nota = parser.find('div', {'class':'reduced-size'})
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags) 
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
    
    df.to_csv('ultimas_noticias_minutouno_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_minutouno_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_minutouno_full.txt', mode = '+w', index = False, header = False)    
