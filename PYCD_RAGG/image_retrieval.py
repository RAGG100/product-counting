# Librerias
## Acceso a Drive API
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
## Manejo de imagenes
import io
import os
from PIL import Image
## Logs
import logging
logger = logging.getLogger("base")

## Parametros
from .config import DRIVE_KEYS, FOLDER_ID, FOLDER_DEST

logger.info(f"Crear cliente de Drive API con claves en {DRIVE_KEYS}")
CREDENTIALS = service_account.Credentials.from_service_account_file(
   DRIVE_KEYS,
   scopes=['https://www.googleapis.com/auth/drive']
   )
SERVICE = build("drive", "v3", credentials=CREDENTIALS)

# Obtener imagenes de archivo
def get_images(folder_id: str = FOLDER_ID, dest_folder: str = FOLDER_DEST) -> list[dict]:
    """
    Funcion que descarga imagenes dentro de una carpeta de Drive especifica

    Parametros
    ----------
    folder_id : str
        ID de la carpeta de Drive a descargar
    dest_folder : str
        Ruta de carpeta donde se descargaran las imagenes

    Regresa
    -------
    imgs_info : list[dict]
        Lista con un diccionario de propiedades para cada imagen
    """
    # Obtener lista de archivos
    try:
        logger.info(f"Obteniendo lista de imagenes de {folder_id}")
        response = (SERVICE.files()
                    .list(q=f"trashed=false and '{folder_id}' in parents and mimeType = 'image/jpeg'",
                          spaces ='drive',
                          fields='files(id, name)'
                          )
                    .execute()
                    )
    except HttpError as error:
        logger.error(f"Error: {error}")
        response = {}
    
    # Descargar imagenes
    logger.info(f"Descargando imagenes")
    imgs_info = []
    for image in response.get('files', []):
        logger.debug(f"Descargando {image['name']}")
        try:
            # Solicitar imagen
            request = SERVICE.files().get_media(fileId=image['id'])
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)

            # Esperar a que este lista la descarga
            done = False
            while done is False:
              status, done = downloader.next_chunk()
              logger.debug(f"Progeso: {int(status.progress() * 100)}.")

            # Guardar en carpeta
            with open(os.path.join(dest_folder, image['name']), 'wb') as img_file:
              img_file.write(file.getbuffer())
    
            imgs_info.append({'drive_link': 'https://drive.google.com/file/d/'+image['id'], 
                             'path': os.path.join(dest_folder, image['name'])})
        except HttpError as error:
            logger.error(f"Error al descargar {image['name']}: {error}")
        
    logger.info(f"Imagenes descargadas en {dest_folder}")
    return imgs_info

# Transformacion de imagenes
def transform_images(imgs_info: list[dict]) -> list[dict]:
    """
    Funcion que aplica transformaciones a imagenes en una carpeta especifica

    Parametros
    ----------
    imgs_info : list[dict]
        Lista de diccionarios con propiedades
            - path: Ruta de acceso a imagen

    Regresa
    -------
    img_info : list[dict]
        Lista con un diccionario de propiedades para cada imagen
    """
    logger.info('Transformando imagenes')
    files = [info['path'] for info in imgs_info]
    for file in files:
        if not file.endswith('.jpg'):
            continue
        logger.debug(f"Transformando imagen {file}")
        with Image.open(file).convert('RGB') as img:
            # Rotar imagen para estar en vertical si esta en horizontal
            if img.size[0] < img.size[1]:
                continue
            img = img.rotate(-90, expand=True)
            img.save(file)
    logger.info(f"Imagenes transformadas.")
    return imgs_info
