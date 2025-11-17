# Librerias
## Modelo de deteccion de objetos
from ultralytics import YOLO
## Lectura de codigos de barra
from pyzbar.pyzbar import decode
## Manejo de imagenes
import os
from PIL import Image
## Utilidades
from numpy import argmax

# Parametros
from .config import MODEL_PATH
#ORIGIN_FOLDER = './datasets/downloaded_images/'
MODEL = YOLO(MODEL_PATH)


def detect_objects(origin_folder: str, model: any = MODEL):
    """
    Funcion que aplica un modelo de deteccion a imagenes en una carpeta especifica

    Parametros
    ----------
    origin_folder : str
        Ruta de carpeta donde se encuentran las imagenes
    model : 
        Modelo de deteccion de objetos. Requiere metodo predict

    Regresa
    -------
    imgs_info : list[dict]
        Lista con un diccionario de propiedades para cada imagen
    """

    # Obtener predicciones
    preds = model.predict(origin_folder, verbose=False)
    # Generar informacion de cada imagen
    imgs_info = []
    for pred in preds:
        imgs_info.append({
            'path': pred.path,
            'objects': pred.summary()
        })
    return imgs_info

def region_properties(box: list|tuple) -> dict:
    """
    Funcion que obtiene las propiedades de una region rectangular

    Parametros
    ----------
    box : list|tuple
        Vertices de region en formato (x1,y1,x2,y2,x3,y3,x4,y4)

    Regresa
    -------
    imgs_info : dict
        Diccionario con propiedades
            - quad: Vertices de la region
            - width: Ancho de la region
            - height: Alto de la region
    """
    # Esquinas de la region
    quad = (box['x4'], box['y4'], box['x1'], box['y1'], box['x2'], box['y2'], box['x3'], box['y3'])
    # Largo y ancho
    width = ((box['x1']-box['x2'])**2 + (box['y1']-box['y2'])**2)**0.5
    height = ((box['x3']-box['x2'])**2 + (box['y3']-box['y2'])**2)**0.5
    if width > height:
        width, height = height, width
    # Diccionario con propiedades de la region
    props = {'quad': quad, 'width': int(width), 'height': int(height)}
    return props

def process_products(products: list) -> int:
    """
    Funcion que procesa los productos detectados

    Parametros
    ----------
    products : list
        Lista de regiones donde se detectaron productos

    Regresa
    -------
    n : int
        Numero de productos detectados
    """

    # Por el momento solo regresa el numero de productos que pase cierto umbral
    treeshold = 0.7
    # Cantidad de productos con seguridad mayor al treeshold
    n = len([product for product in products if product['confidence']>treeshold])
    return n


def process_guides(guides: list, img_path: str) -> str:
    """
    Funcion que procesa las guias detectadas

    Parametros
    ----------
    guides : list
        Lista de regiones donde se detecto una guia
    img_path : str
        Ruta de imagen original
        
    Regresa
    -------
    track_id : str
        Codigo de rastreo detectado
    """
    # Filtrar guia con area mas grande
    regions = [region_properties(guide['box']) for guide in guides]
    idx = argmax([box['width']*box['height'] for box in regions])
    region = regions[idx]

    # Obtener region de la guia
    with Image.open(img_path) as img:
        guide_img = img.transform((region['width'], region['height']), Image.QUAD, region['quad'])

    # Abrir imagen y buscar codigo de barras
    code_list = [code.data.decode() for code in decode(guide_img) if code.type=='CODE128']
    track_ids = [code for code in code_list if len(code)==11]
    track_id = track_ids[0] if track_ids else ''
    return track_id



