# -*- coding: utf-8 -*-
"""webscraping_LFEndesa.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kcoQ0dMEwMQOjOZRup84UMHVrhQKjEdR

### **1. Instalación del navegador**

Necesitamos utilizar un navegador, para ello se implementa el siguiente código que nos va a permitir utilizar Chrome como navegador desde Google Colab.
"""

# Instalar dependencias para utilizar Google Chrome
!sudo apt-get update
!sudo apt-get install -y libu2f-udev
!pip install selenium

# Instalar el navegador
!wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!dpkg -i google-chrome-stable_current_amd64.deb
!apt-get install -f
!rm -rf google-chrome-stable_current_amd64.deb

# Descargar el WebDriver 
!wget https://chromedriver.storage.googleapis.com/112.0.5615.49/chromedriver_linux64.zip
!unzip chromedriver_linux64
!rm -rf chromedriver_linux64.zip
!rm -rf LICENSE.chromedriver

"""### **2. Cargamos las librerias que vamos a utilizar**"""

# navegador
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# manejo de lista desplegable
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# manejo de tiempos
import time

# manejo de datos
import pandas as pd

# exportar a csv
import csv

"""### **3. Almacenamiento en Drive**"""

from google.colab import drive
drive.mount('/content/drive/')

"""### **4. Opciones del navegador**"""

def iniciar_chrome():
  """
  Inicia el navegador con los parámetros indicados y nos devuelve el driver
  """
  # Opciones de Chrome
  chrome_options = Options()
  user_agent = "Mozilla/5.0 (Windows NT 10.; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
  chrome_options.add_argument(f"user-agent={user_agent}") # definimos el user agent
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--no-sandbox') # deshabilita el modo sandbox
  chrome_options.add_argument('--start_maximized') # maximizamos la ventana
  chrome_options.add_argument('--disable-web-security') # deshabilita la politica cross origin 
  chrome_options.add_argument('--disable-extensions') # para que no cargue las extensiones
  chrome_options.add_argument('--disable-notifications') # bloquea las notificaciones de chrome
  chrome_options.add_argument('--allow-running-insecure-content') # desactiva el contenido no seguro
  chrome_options.add_argument('--no-default-browser-check') # evitar el aviso de que chrome no es el navegador principal
  chrome_options.add_argument('--no-first-run') # evita que se ejecuten tareas que se realizan por primera vez en el navegador
  chrome_options.add_argument('--no-proxy-server') # usar conexiones directas
  chrome_options.add_argument('--disable-blink-features=AutomationControlled') # evita que selenium sea detectado
  # Ruta del controlador de Chrome
  chrome_driver_path = '/content/chromedriver'

  # Crear un objeto Service para especificar la ruta del controlador
  service = Service(chrome_driver_path)

  # Crear una instancia del navegador Chrome
  driver = webdriver.Chrome(service=service, options=chrome_options)
  return driver

"""### **5. Manejar lista desplegable**"""

def select_context_navigation(temporada, competicion, atributo, nacionalidad):
  """
  Selecciona las opciones en un desplegable y además devuelve el número de 
  páginas por las que hay que navegar una vez se ha hecho la selección
  """
  # selección de la temporada
  dropdownT = Select(driver.find_element('id', '_ctl0_MainContentPlaceHolderMaster_temporadasDropDownList'))
  dropdownT.select_by_visible_text(temporada)
  time.sleep(1) # tiempo de carga
  # selección del tipo de competición
  dropdownC = Select(driver.find_element('id', '_ctl0_MainContentPlaceHolderMaster_gruposDropDownList'))
  dropdownC.select_by_visible_text(competicion)
  time.sleep(1) # tiempo de carga
  # selección de los atributos
  dropdownA = Select(driver.find_element('id', '_ctl0_MainContentPlaceHolderMaster_rankingsDropDownList'))
  dropdownA.select_by_visible_text(atributo)
  time.sleep(1) # tiempo de carga
  # selección de los atributos
  dropdownN = Select(driver.find_element('id', '_ctl0_MainContentPlaceHolderMaster_nacionalDropDownList'))
  dropdownN.select_by_visible_text(nacionalidad)
  time.sleep(1) # tiempo de carga

  # obtenemos el número de páginas del paginador
  pages = len(driver.find_element(By.CLASS_NAME,'tabla-paginador').find_elements(By.TAG_NAME,'a'))

  return pages

"""### **6. Recolección de atributos**"""

def collect_attributes(lim):
  """
  Recopila los datos y los guarda en una lista
  """
  data = []
  page = 2
  while page <= lim + 2:
    time.sleep(2)  
    selection = driver.find_element(By.ID, '_ctl0_MainContentPlaceHolderMaster_rankingAcumuladosDataGrid').find_elements(By.TAG_NAME,'td')
    for sel in selection:
      if sel.text != '' and sel.text != "1 2" and sel.text != "1 2 3":
        data.append(sel.text)
    # Para hacer scroll
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
    # Damos tiempo
    time.sleep(2)
    # Hacemos clic en el siguiente enlace de paginación
    if page < lim + 2:
      button_page = driver.find_element(By.LINK_TEXT, str(page)).click()
    page = page + 1
  return data

"""### **7. Creación de un dataframe con los datos**"""

def create_df (lista, temporada, atributo, nacionalidad):
  """
  Generamos un dataframe con los datos con los datos de los atributos
  """
  if atributo == 'Puntos':
    df = pd.DataFrame(columns=['Temporada','Jugadora', 'Nacionalidad',
                                          'Equipo', atributo, 'Partidos'])  
    for i in range(int(len(lista)/5)):
      dict_fila = {'Temporada': [temporada],
                      'Jugadora': [lista[5*i]],
                      'Nacionalidad': [nacionalidad],
                      'Equipo': [lista[5*i+1]],
                      atributo:[lista[5*i+2]],
                      'Partidos':[lista[5*i+3]]}
      df_fila = pd.DataFrame(dict_fila)
      df = pd.concat([df, df_fila], ignore_index = True)
  else:
    df = pd.DataFrame(columns=['Jugadora', atributo]) 
    for i in range(int(len(lista)/5)):
      dict_fila = {'Jugadora': [lista[5*i]],
                    atributo:[lista[5*i+2]]}
      df_fila = pd.DataFrame(dict_fila)
      df = pd.concat([df, df_fila], ignore_index = True)
  df = df.sort_values('Jugadora')
  # Tratamiento de jugadoras duplicadas que han cambiado de equipo durante la liga
  if df["Jugadora"].duplicated(keep = False).any() == True:
    bool_series = df["Jugadora"].duplicated(keep = False)
    df = df[~bool_series]
  return df

"""### **8. Función que realiza el scraping**"""

def webscraper(seasons, attributes, nationality):
  """
  Función que realiza el raspado web
  """
  for key in seasons:
    df_season = pd.DataFrame(columns=['Jugadora'])
    for att in attributes:
      df_complete = pd.DataFrame()  
      for nat in nationality:
        lista = collect_attributes(select_context_navigation(key, seasons[key], att, nat))
        df_partial = create_df(lista, key, att, nat)
        df_complete = pd.concat([df_complete, df_partial], ignore_index = True)
      df_complete = df_complete.sort_values('Jugadora')
      df_season = pd.merge(df_season, df_complete, on='Jugadora', how='outer')
    df_season.to_csv(r'/content/drive/MyDrive/PR1Datos/data.csv', mode = 'a', header = True, index = False)
  return driver.quit()

"""### **9. Ejecución final**"""

# variaciones que vamos a utilizar para extraer la información
attributes = ['Puntos', 'Rebotes Totales', 'Rebotes Ofensivos', 'Rebotes Defensivos',
             'Asistencias', 'Balones recuperados', 'Balones perdidos', 'Tapones a favor',
             'Tapones en contra', 'Faltas recibidas', 'Faltas cometidas',
             'Valoración', 'Minutos jugados', '% Tiros de 2', '% Tiros de 3', '% Tiros Libres']
seasons = {'2022/2023':'Liga Regular Único',
           '2021/2022':'Liga Regular Único',
           '2020/2021':'Liga Regular Único',
           '2019/2020':'Liga Regular Único',
           '2018/2019':'Liga Regular',
           '2017/2018':'Liga Regular Único',
           '2016/2017':'Liga Regular Único',
           '2015/2016':'Liga Regular Único',
           '2014/2015':'Liga Regular Único',
           '2013/2014':'Liga Regular Grupo Unico',
           '2012/2013':'Liga Regular Único',
           '2011/2012':'LIGA REGULAR Único',
           '2010/2011':'REGULAR ÚNICO',
           '2009/2010':'REGULAR ÚNICO',
           '2008/2009':'REGULAR ÚNICO',
           '2007/2008':'REGULAR ÚNICO',
           '2006/2007':'REGULAR ÚNICO',
           '2005/2006':'REGULAR',
           '2004/2005':'REGULAR',
           '2003/2004':'LIGA REGULAR ÚNICO'
           }
nationality = ['Nacional', 'Extranjero']

# Ruta de la página web
url = 'https://baloncestoenvivo.feb.es/rankings/lfendesa/4/2022'

# Navegar a una página web
driver = iniciar_chrome()
driver.get(url)

# Lanzamos la función
webscraper(seasons, attributes, nationality)