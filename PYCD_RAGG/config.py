# Librerias
import json
import logging
logger = logging.getLogger("base")

with open('config.json') as file:
    logger.info("Carga de archivo de configuracion.")
    _config = json.load(file)

# Parametros
## Obtencion de imagenes
img_retrieval_parms = _config.get('img_retrieval', {})
DRIVE_KEYS = img_retrieval_parms.get('drive_api_keys')
FOLDER_ID = img_retrieval_parms.get('folder_id')
FOLDER_DEST = img_retrieval_parms.get('folder_dest')

## Deteccion de objetos
obj_detection_parms = _config.get('obj_detection', {})
MODEL_PATH = obj_detection_parms.get('model')

## Carga de imagenes
img_uploading = _config.get('img_uploading', {})
ODOO_KEYS = img_uploading.get('odoo_api_keys')
TRACK_FILE = img_uploading.get('track_file')

## Manejo de errores
error_management = _config.get('error_management', {})
ERROR_FOLDER_ID = error_management.get('folder_id')
ERROR_ORIGIN_FOLDER = error_management.get('origin_folder')