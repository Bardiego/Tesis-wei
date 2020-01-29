# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 12:54:16 2019

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

def funcion_scrap_lavoz_cordoba():
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    
    html = requests.get("https://www.lavoz.com.ar/lo-ultimo", verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html5lib')
    mydivs = soup.find('div', {'class':'timeline'}).findAll('article')
    
    
    format = "%Y-%m-%d,%H:%M"
    
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for div  in mydivs:
        try:
            link = div.find('div', {'class':'columns'}).find('h3').find('a').get('href')
            fecha_hace  = div.find('div', {'class':'columns'}).find('time').text.strip().split()[1:3]
            if fecha_hace[1] == 'minutos' or fecha_hace[1] == 'minuto':
                tiempo_hace = fecha_hace[0]
                fecha_actual = datetime.now()
                fecha_publicacion = fecha_actual - dateutil.relativedelta.relativedelta(minutes=int(tiempo_hace))
                fecha_publicacion_real = datetime.strptime(str(fecha_publicacion.year)+'-'+str(fecha_publicacion.month)+'-'+str(fecha_publicacion.day)+','+str(fecha_publicacion.hour)+':'+str(fecha_publicacion.minute), format)
            elif fecha_hace[1] == 'horas' or fecha_hace[1]  == 'hora':
                tiempo_hace = fecha_hace[0]
                fecha_actual = datetime.now()
                fecha_publicacion = fecha_actual - dateutil.relativedelta.relativedelta(hours=int(tiempo_hace))
                fecha_publicacion_real = datetime.strptime(str(fecha_publicacion.year)+'-'+str(fecha_publicacion.month)+'-'+str(fecha_publicacion.day)+','+str(fecha_publicacion.hour)+':'+str(fecha_publicacion.minute), format)
            else:
                pass
            if 'http' in link[:4]:
                html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
                parser = BeautifulSoup(html_p, 'html5lib')            
                cuerpo_nota = parser.find('div', {'class':'body'})
                nota_tags = cuerpo_nota.findAll('p')
                nota = ''
                nota = nota.join(tag.text for tag in nota_tags)
                nota = unicodedata.normalize("NFKD", nota)
                nota = nota.replace('\n','').replace('u200b', '')
                pakete_dict['fecha-hora'].append(fecha_publicacion_real)
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
    
    
    df.to_csv('ultimas_noticias_lavoz_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_lavoz_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_lavoz_full.txt', mode = '+w', index = False, header = False)
