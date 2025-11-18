# Librerias
## Modelo de deteccion de objetos
from ultralytics import YOLO
## Lectura de codigos de barra
from pyzbar.pyzbar import decode
## Manejo de imagenes
from PIL import Image
## Utilidades
import numpy as np
import json
## Logs
import logging
logger = logging.getLogger("base")

# Parametros
from .config import MODEL_PATH
logger.info(f"Cargando modelo en {MODEL_PATH}")
MODEL = YOLO(MODEL_PATH)


def detect_objects(imgs_info: list[dict], model: any = MODEL) -> list[dict]:
    """
    Funcion que aplica un modelo de deteccion a imagenes en una carpeta especifica

    Parametros
    ----------
    imgs_info : list[dict]
        Lista de diccionarios con propiedades
            - path: Ruta de acceso a imagen
    model : 
        Modelo de deteccion de objetos. Requiere metodo predict

    Regresa
    -------
    imgs_info : list[dict]
        Lista con un diccionario de propiedades para cada imagen
    """

    # Obtener predicciones
    logger.info("Detectando objetos.")
    files = [info['path'] for info in imgs_info]
    preds = model.predict(files, verbose=False)
    # Agregar objetos detectados a informacion de imagen
    for i, pred in enumerate(preds):
        imgs_info[i]['objects'] = pred.summary()
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
    # Lista de vectores de esquinas
    corners = [np.array([box[f"x{i}"],box[f"y{i}"]]) for i in range(1,5)]

    # Encontrar esquina superior izquierda
    ## Ordenar por coordenada x
    corners = sorted(corners, key=lambda corner: corner[0])
    ## Entre las dos coordenadas mas a la izquierda, encontrar la mas arriba
    if corners[0][1] > corners[1][1]:
        UL_corner = corners[0][1]
    else:
        UL_corner = corners[1][1]
    ## Ordenar por distancia a la esquina superior izquierda
    corners_sort_dist = sorted(corners, key=lambda corner: np.linalg.norm(UL_corner-corner))
    ## Obtener esquinas en orden: lower left, upper left, upper right, lower right
    new_corners = [corners_sort_dist[i] for i in [2,0,1,3]]

    # Largo y ancho
    width = np.linalg.norm(UL_corner - corners_sort_dist[1])
    height = np.linalg.norm(UL_corner - corners_sort_dist[2])

    # Aplanar lista
    new_corners = [x for tup in new_corners for x in tup]

    # Diccionario con propiedades de la region
    props = {'quad': new_corners, 'width': int(width), 'height': int(height)}
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
    idx = np.argmax([box['width']*box['height'] for box in regions])
    region = regions[idx]

    # Obtener region de la guia
    with Image.open(img_path) as img:
        guide_img = img.transform((region['width'], region['height']), Image.QUAD, region['quad'], Image.Resampling.BICUBIC)

    # Abrir imagen y buscar codigos de barras o QR
    track_id = ''
    for code in decode(guide_img):
        # Procesamiento de codigo de barras
        if code.type == 'CODE128':
            if len(code.data.decode()) == 11:
                track_id = code.data.decode()
                break
        # Procesamiento de codigos QR
        if code.type == 'QRCODE':
            try:
                content = json.loads(code.data.decode())
                if len(content['id']) == 11:
                    track_id = content['id']
                    break
            except:
                continue
    
    return track_id



