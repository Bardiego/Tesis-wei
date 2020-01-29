# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 17:09:27 2020

@author: Diego
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from funcion_scrap_clarin_full import funcion_scrap_clarin
from funcion_scrap_ambito_full import funcion_scrap_ambito
from funcion_scrap_cronica_full import funcion_scrap_cronica
from funcion_scrap_diariopopular_full import funcion_scrap_diariopopular ##Usa funciones
from funcion_scrap_diarioregistrado_full import funcion_scrap_diarioregistrado ##Usa funciones 
from funcion_scrap_eldestapeweb_full import funcion_scrap_eldestapeweb
from funcion_scrap_infobae_full import funcion_scrap_infobae
from funcion_scrap_lacapital_rosario_full import funcion_scrap_lacapital_rosario
from funcion_scrap_lagaceta_salta_full import funcion_scrap_lagaceta_salta
from funcion_scrap_lanacion_full import funcion_scrap_lanacion
from funcion_scrap_lavoz_cordoba_full import funcion_scrap_lavoz_cordoba
from funcion_scrap_minutouno_full import funcion_scrap_minutouno
from funcion_scrap_pagina12_full import funcion_scrap_pagina12
from funcion_scrap_perfil_full import funcion_scrap_perfil
from funcion_scrap_radiomitre_full import funcion_scrap_radiomitre
from funcion_scrap_tiempoar_full import funcion_scrap_tiempoar
from funcion_scrap_tn_full import funcion_scrap_tn
from funcion_scrap_elcronista_full import funcion_scrap_elcronista


funciones_scrap = [funcion_scrap_ambito, funcion_scrap_clarin, funcion_scrap_cronica,
                   funcion_scrap_diariopopular, funcion_scrap_diarioregistrado, 
                   funcion_scrap_elcronista, funcion_scrap_eldestapeweb, 
                   funcion_scrap_infobae, funcion_scrap_lacapital_rosario, 
                   funcion_scrap_lagaceta_salta, funcion_scrap_lanacion, 
                   funcion_scrap_lavoz_cordoba, funcion_scrap_minutouno, 
                   funcion_scrap_pagina12, funcion_scrap_perfil,
                   funcion_scrap_radiomitre, funcion_scrap_tiempoar, funcion_scrap_tn]

executors = {
    'default': ThreadPoolExecutor(25),
    'processpool': ProcessPoolExecutor(25)
    }

scheduler = BackgroundScheduler(executors=executors)

tiempo_inicial = '2020-01-25 16:30:00'
tiempo_final = '2020-02-01 16:30:00'

#horas = 1
minutos = 30

for func in funciones_scrap:
    scheduler.add_job(func, 'interval', minutes = minutos,
                      start_date = tiempo_inicial,
                      end_date = tiempo_final)

scheduler.start()







