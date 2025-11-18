# Librerias
## Acceso a Drive API
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.cloud import storage

## Logs
import logging
logger = logging.getLogger("base")

## Parametros
from .config import DRIVE_KEYS, ERROR_FOLDER_ID

logger.info(f"Crear cliente de Drive API con claves en {DRIVE_KEYS}")
CREDENTIALS = service_account.Credentials.from_service_account_file(
    DRIVE_KEYS,
    scopes=['https://www.googleapis.com/auth/drive']
    )
SERVICE = build("drive", "v3", credentials=CREDENTIALS)

def move_images_drive(drive_links: list[str], dest_id: str = ERROR_FOLDER_ID) -> str:
    """
    Funcion que mueve imagenes de una carpeta de Drive especifica a otra

    Parametros
    ----------
    drive_links : list[str]
        Lista de links de archivos a mover
    dest_id : str
        ID de carpeta de destino

    Regresa
    -------
    None
    """
    # Obtener lista de archivos
    logger.info(f"Moviendo archivos a {dest_id}")
    drive_ids = [link.split('/')[-1] for link in drive_links]
    for file_id in drive_ids:
        try:
            logger.debug(f"Moviendo archivo {file_id}")
            # Obtener carpeta actual
            file = SERVICE.files().get(fileId=file_id, fields="parents").execute()
            previous_parents = ",".join(file.get("parents"))
            # Cambiar carpeta
            (SERVICE.files()
             .update(
                 fileId=file_id,
                 addParents=dest_id,
                 removeParents=previous_parents
                 )
                .execute()
            )
        except HttpError as error:
            print(f"Error al mover archivo {file_id}: {error}")
