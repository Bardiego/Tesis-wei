# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 10:12:03 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import locale
import dateutil
import ssl
import re
import unicodedata
from ast import literal_eval


def try_itr1(itr, *exceptions, **kwargs):
    for elem in itr:
        try:
            link = elem.get('href')
            yield link
        except exceptions:
            pass

def remove_itr_not(itr, exception):
    for elem in itr:
        if exception not in elem[:25]:
            itr.remove(elem)

def funcion_scrap_lagaceta_salta():
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    
    html = requests.get("https://www.lagacetasalta.com.ar/ultimo-momento", verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html5lib')
    mydivs = soup.find('div', {'class':'news'}).find('div', {'class':'row'}).findAll('a')
    
    
    mylinks = list(try_itr1(mydivs, AttributeError))
    remove_itr_not(mylinks, 'https://www.lagacetasalta')
    remove_itr_not(mylinks, 'https://www.lagacetasalta')
    remove_itr_not(mylinks, 'https://www.lagacetasalta')
    mylinks = list(set(mylinks))
    
    
    diario_str = 'https://www.lagacetasalta.com.ar/'
    format = "%Y-%m-%d,%H:%M"
    
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for link  in mylinks:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_hace = parser.find('div', {'class':'info'}).find('span').text.split()[1:3]
            
            if fecha_hace[1] == 'Min':
                tiempo_hace = fecha_hace[0]
                fecha_actual = datetime.now()
                fecha_publicacion = fecha_actual - dateutil.relativedelta.relativedelta(minutes=int(tiempo_hace))
                fecha_publicacion_real = datetime.strptime(str(fecha_publicacion.year)+'-'+str(fecha_publicacion.month)+'-'+str(fecha_publicacion.day)+','+str(fecha_publicacion.hour)+':'+str(fecha_publicacion.minute), format)
            elif fecha_hace[1] == 'Hs':
                tiempo_hace = fecha_hace[0]
                fecha_actual = datetime.now()
                fecha_publicacion = fecha_actual - dateutil.relativedelta.relativedelta(hours=int(tiempo_hace))
                fecha_publicacion_real = datetime.strptime(str(fecha_publicacion.year)+'-'+str(fecha_publicacion.month)+'-'+str(fecha_publicacion.day)+','+str(fecha_publicacion.hour)+':'+str(fecha_publicacion.minute), format)
            else:
                pass
            
            cuerpo_nota = parser.find('div', {'class':'newsBody'})
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
    
    
    df.to_csv('ultimas_noticias_lagaceta_salta_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_lagaceta_salta_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_lagaceta_salta_full.txt', mode = '+w', index = False, header = False)
