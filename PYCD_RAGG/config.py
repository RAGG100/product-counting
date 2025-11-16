# Librerias
import json
with open('config.json') as file:
    _config = json.load(file)

# Parametros
img_retrieval_parms = _config.get('img_retrieval')
DRIVE_KEYS = img_retrieval_parms.get('drive_api_keys')
FOLDER_ID = img_retrieval_parms.get('folder_id')
FOLDER_DEST = img_retrieval_parms.get('folder_dest')
