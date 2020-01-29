# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 15:17:48 2019

@author: Diego
"""

from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateutil
import pandas as pd
import ssl
import re
import unicodedata
from ast import literal_eval


def funcion_scrap_infobae():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    
    html = requests.get("https://www.infobae.com/ultimas-noticias/").text
    soup = BeautifulSoup(html, 'html5lib')
    mysects = soup.findAll('div', {'class':'generic-results-list-main-wrapper'})[0]
    mydivs = mysects.findAll('article')
    
    
    diario_str = 'https://www.infobae.com'
    format = "%Y-%m-%d,%H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for divs in mydivs:
        try:
            link_casi = divs.find('a').get('href')
            link = diario_str+link_casi
            fecha_hace = divs.find('time').text.strip().split()
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
        except:
            pass
        html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
        parser = BeautifulSoup(html_p, 'html5lib')
        cuerpo_nota = parser.findAll('div', {'id':'article-content'})[0]
        nota_tags = cuerpo_nota.findAll('div',{'class':'pb-content-type-text'})
        nota = ''
        nota = nota.join(tag.text for tag in nota_tags)    
        nota = unicodedata.normalize("NFKD", nota)
        nota = nota.replace('\n','').replace('u200b', '')
        pakete_dict['fecha-hora'].append(fecha_publicacion_real)
        pakete_dict['link'].append(link)
        pakete_dict['noticia'].append(nota)
        
    
    for nota in pakete_dict['noticia']:
        citas = re.findall(r'"[^"”“]*"|“[^“”"]*”|”[^“”"]*“|"[^“”"]*“|”[^“”"]*"|"[^“”"]*”|“[^“”"]*"', nota)
        citas1 = [cita.strip('"“”') for cita in citas]
        pakete_dict['citas'].append(citas1)
     
    df = pd.DataFrame.from_dict(data = pakete_dict)
    
    
    df.to_csv('ultimas_noticias_infobae_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_infobae_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_infobae_full.txt', mode = '+w', index = False, header = False)
