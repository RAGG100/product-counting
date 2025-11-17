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

## Parametros
from .config import DRIVE_KEYS, FOLDER_ID, FOLDER_DEST

CREDENTIALS = service_account.Credentials.from_service_account_file(
   DRIVE_KEYS,
   scopes=['https://www.googleapis.com/auth/drive']
   )

# Obtener imagenes de archivo
def get_images(folder_id: str = FOLDER_ID, dest_folder: str = FOLDER_DEST, credentials: any = CREDENTIALS) -> str:
    """
    Funcion que descarga imagenes dentro de una carpeta de Drive especifica

    Parametros
    ----------
    folder_id : str
        ID de la carpeta de Drive a descargar
    dest_folder : str
        Ruta de carpeta donde se descargaran las imagenes
    credentials : 
        Credenciales de acceso creadas con google.oauth2.service_account

    Regresa
    -------
    dest_folder : str
        Ruta de carpeta con imagenes descargadas
    """
    # Crear cliente
    service = build("drive", "v3", credentials=CREDENTIALS)

    # Obtener lista de archivos
    try:
        response = (service.files()
                    .list(q=f"trashed=false and '{folder_id}' in parents and mimeType = 'image/jpeg'",
                          spaces ='drive',
                          fields='files(id, name)'
                          )
                    .execute()
                    )
    except HttpError as error:
        print(f"Ocurrio un error: {error}")
        response = {}
    
    # Descargar imagenes
    for image in response.get('files', []):
        print(f"Descargando {image['name']}")
        try:
            # Solicitar imagen
            request = service.files().get_media(fileId=image['id'])
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)

            # Esperar a que este lista la descarga
            done = False
            while done is False:
              status, done = downloader.next_chunk()
              print(f"Download {int(status.progress() * 100)}.")

            # Guardar en carpeta
            with open(os.path.join(dest_folder, image['name']), 'wb') as img_file:
              img_file.write(file.getbuffer())
        except HttpError as error:
            print(f"Error al descargar {image['name']}: {error}")
    return dest_folder

# Transformacion de imagenes
def transform_images(origin_folder: str) -> str:
    """
    Funcion que aplica transformaciones a imagenes en una carpeta especifica

    Parametros
    ----------
    origin_folder : str
        Ruta de carpeta donde se encuentran las imagenes a transformar

    Regresa
    -------
    origin_folder : str
        Ruta de carpeta con imagenes transformadas
    """
    for file in os.listdir(origin_folder):
        if not file.endswith('.jpg'):
            continue
        img_path = os.path.join(origin_folder, file)
        with Image.open(img_path).convert('RGB') as img:
            # Rotar imagen para estar en vertical si esta en horizontal
            if img.size[0] < img.size[1]:
                continue
            img = img.rotate(-90, expand=True)
            img.save(img_path)
    return origin_folder
