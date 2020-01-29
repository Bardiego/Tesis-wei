# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 23:32:09 2019

@author: Diego
"""


from bs4 import BeautifulSoup
import requests
from requests.models import MissingSchema
from requests.sessions import InvalidSchema
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
            link = elem.find('a').get('href')
            yield link
        except exceptions:
            pass
            
def new_itr(itr, diario_str, string):
    for elem in itr:
        if string in elem[:10]:
            yield diario_str+elem


def funcion_scrap_perfil():
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    
    html = requests.get("https://www.perfil.com/").text
    soup = BeautifulSoup(html, 'html5lib')
    myarticles = soup.findAll('article')
    
    
    diario_str = "https://www.perfil.com"      
    
    
    mylinks = list(try_itr1(myarticles, AttributeError))        
    mylinks = list(new_itr(mylinks, diario_str, '/noticias/'))
    
    
    format = "%Y-%m-%d,%H:%M"
    
    pakete_dict = {'fecha-hora':[], 'link':[], 'noticia':[], 'citas':[]}
    
    for link in mylinks:
        try:
            html_p = requests.get(link, verify = False, headers = {"User-Agent":'Mozilla/5.0'}).text
            parser = BeautifulSoup(html_p, 'html5lib')
            fecha_publicacion = parser.find('div', {'class':'articuloDateTime'}).text.strip()
            fecha_publicacion_split = parser.find('div', {'class':'articuloDateTime'}).text.split()
            hoy = datetime.now()
            cuerpo_nota = parser.find('section', {'class':'cuerpoNoticia'})
            nota_tags = cuerpo_nota.findAll('p')
            nota = ''
            nota = nota.join(tag.text for tag in nota_tags) 
            nota = unicodedata.normalize("NFKD", nota)
            nota = nota.replace('\n','').replace('u200b', '')
            if fecha_publicacion_split[0] == 'Hoy':
                if fecha_publicacion_split[-1] == 'AM':
                    fecha_publicacion_real = datetime.strptime(str(hoy.year)+'-'+str(hoy.month)+'-'+str(hoy.day)+','+fecha_publicacion_split[-2],
                                                      "%Y-%m-%d,%I:%M")
                    pakete_dict['fecha-hora'].append(fecha_publicacion_real)
                    pakete_dict['link'].append(link)
                    pakete_dict['noticia'].append(nota)
                    
                if fecha_publicacion_split[-1] == 'PM':
                    if int(fecha_publicacion_split[-2].split(':')[0]) != 12:
                        fecha_publicacion_real = datetime.strptime(str(hoy.year)+'-'+str(hoy.month)+'-'+str(hoy.day)+','+fecha_publicacion_split[-2],
                                                          format)
                        fecha_publicacion_real = fecha_publicacion_real + dateutil.relativedelta.relativedelta(hours=12)
                        pakete_dict['fecha-hora'].append(fecha_publicacion_real)
                        pakete_dict['link'].append(link)
                        pakete_dict['noticia'].append(nota)
                    elif int(fecha_publicacion_split[-2].split(':')[0]) == 12:
                        fecha_publicacion_real = datetime.strptime(str(hoy.year)+'-'+str(hoy.month)+'-'+str(hoy.day)+','+fecha_publicacion_split[-2],
                                                          format)
                        pakete_dict['fecha-hora'].append(fecha_publicacion_real)
                        pakete_dict['link'].append(link)
                        pakete_dict['noticia'].append(nota)
                    
            elif fecha_publicacion_split[0] == 'Ayer':
                ayer = hoy - dateutil.relativedelta.relativedelta(days=1)
                if fecha_publicacion_split[-1] == 'AM':
                    
                    fecha_publicacion_real = datetime.strptime(str(ayer.year)+'-'+str(ayer.month)+'-'+str(ayer.day)+','+fecha_publicacion_split[-2],
                                                      "%Y-%m-%d,%I:%M")
                    pakete_dict['fecha-hora'].append(fecha_publicacion_real)
                    pakete_dict['link'].append(link)
                    pakete_dict['noticia'].append(nota)
                if fecha_publicacion_split[-1] == 'PM':
                    if int(fecha_publicacion_split[-2].split(':')[0]) != 12:
                        fecha_publicacion_real = datetime.strptime(str(ayer.year)+'-'+str(ayer.month)+'-'+str(ayer.day)+','+fecha_publicacion_split[-2],
                                                          format)
                        fecha_publicacion_real = fecha_publicacion_real + dateutil.relativedelta.relativedelta(hours=12)
                        pakete_dict['fecha-hora'].append(fecha_publicacion_real)
                        pakete_dict['link'].append(link)
                        pakete_dict['noticia'].append(nota)
                    elif int(fecha_publicacion_split[-2].split(':')[0]) == 12:
                        fecha_publicacion_real = datetime.strptime(str(ayer.year)+'-'+str(ayer.month)+'-'+str(ayer.day)+','+fecha_publicacion_split[-2],
                                                      format)
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
    
    df.to_csv('ultimas_noticias_perfil_full.txt', mode = 'a', index = False, header = False)
    df = pd.read_csv('ultimas_noticias_perfil_full.txt', header=None)
    df[3] = df[3].apply(literal_eval)
    df = df.drop_duplicates(subset=1, keep='last')
    df = df.sort_values(by = 0, axis=0, ascending=False)
    df.to_csv('ultimas_noticias_perfil_full.txt', mode = '+w', index = False, header = False)    
