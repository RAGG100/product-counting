# Librerias
import json
with open('config.json') as file:
    _config = json.load(file)

# Parametros
## Obtencion de imagenes
img_retrieval_parms = _config.get('img_retrieval')
DRIVE_KEYS = img_retrieval_parms.get('drive_api_keys')
FOLDER_ID = img_retrieval_parms.get('folder_id')
FOLDER_DEST = img_retrieval_parms.get('folder_dest')

## Deteccion de objetos
obj_detection_parms = _config.get('obj_detection')
MODEL_PATH = obj_detection_parms.get('model')

## Deteccion de objetos
img_uploading = _config.get('img_uploading')
ODOO_KEYS = img_uploading.get('odoo_api_keys')
TRACK_FILE = img_uploading.get('track_file')
