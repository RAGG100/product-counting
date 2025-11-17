# Librerias
## Conexion con ERP
import xmlrpc.client
import json
## Manejo de imagenes
import base64
import os
## Logs
import logging
logger = logging.getLogger("base")

# Parametros
from .config import ODOO_KEYS, TRACK_FILE
with open(ODOO_KEYS) as file:
    DB_INFO = json.load(file)


# Autenticación y conexion con base de datos
logger.info('Establecendo conexion con ERP')
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(DB_INFO['url']))
DB_INFO['uid'] = common.authenticate(DB_INFO['db'], DB_INFO['user'], DB_INFO['password'], {})
MODELS = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(DB_INFO["url"]))


def get_tracking_info(imgs_info: list, tracking_file: str = TRACK_FILE) -> list:
    """
    Funcion que obtiene el numero de orden de asociado a un codigo de rastreo

    Parametros
    ----------
    imgs_info : list[dict]
        Lista de diccionarios con propiedades
            - tracking_id: numero de rastreo del pedido
    tracking_file : 
        Ruta de acceso a archivo con relacion entre codigo de rastreo y numero de orden

    Regresa
    -------
    imgs_info : list[dict]
        Lista con un diccionario de propiedades para cada imagen
    """
    # Generar diccionario de track id - order
    track_order = {}
    with open(tracking_file) as file:
        # Omitir encabezado
        next(file)
        for line in file:
            track_id, order_id = line.strip().split(',')
            track_order[track_id] = order_id
    # Agregar numero de orden a info de imagenes
    logger.info('Obteniendo numeros de rastreo')
    for info in imgs_info:
        info['order_name'] = track_order.get(info['tracking_id'], '')
    return imgs_info

# Obtener id de venta
def get_sale_order(imgs_info: list) -> list:
    """
    Funcion que obtiene el id de orden asociado a cada numero de orden

    Parametros
    ----------
    imgs_info : list[dict]
        Lista de diccionarios con propiedades
            - order_name: numero de rastreo del pedido

    Regresa
    -------
    imgs_info : list[dict]
        Lista con un diccionario de propiedades para cada imagen
    """
    # Peticion de IDs a ERP
    logger.info('Realizando peticion de IDs de orden a ERP')
    fields = ['name']
    order_names = [info['order_name'] for info in imgs_info]
    filters = [[("name", "in", order_names)]]
    order_info = MODELS.execute_kw(DB_INFO["db"], DB_INFO['uid'], DB_INFO['password'], 
                                   'sale.order', 'search_read',
                                   filters, {'fields': fields})

    # Crear diccionario de numero de venta - id
    order_id = {info['name']: info['id'] for info in order_info}

    # Agregar id
    logger.info('Agregando ID de orden')
    for info in imgs_info:
        info['order_id'] = order_id.get(info['order_name'], '')

    return imgs_info

def upload_image(imgs_info: list) -> list:
    """
    Funcion que crea un registro de una imagen en la base de datos

    Parametros
    ----------
    imgs_info : list[dict]
        Lista de diccionarios con propiedades
            - order_id: ID de orden en base de datos
            - path: Ruta de acceso a imagen
    Regresa
    -------
    imgs_info : list[dict]
        Lista con un diccionario de propiedades para cada imagen
    """
    # Preparar lista de archivos a subir
    records = []
    for info in imgs_info:
        if not info['order_id']:
            continue
        vals = {
            'name': os.path.basename(info['path']), # Nombre de archivo
            'res_model': 'sale.order',
            'res_id': info['order_id']
        }
        # Agregar contenido de archivo
        with open(info['path'], "rb") as img:
            vals['datas'] = base64.b64encode(img.read()).decode('utf-8')
        records.append(vals)

    # Crear registros de archivos
    logger.info('Subiendo archivos a ERP')
    records_id = MODELS.execute_kw(DB_INFO["db"], DB_INFO['uid'], DB_INFO['password'],
                                   'ir.attachment', 'create',
                                   [records])
    # IDs de archivo
    files_ids = {}
    for i, record in enumerate(records):
        files_ids[record['name']] = records_id[i]
    # Agregar IDs de archivos a informacion de imagen
    logger.info('Agregando IDs de archivos')
    for info in imgs_info:
        info['file_id'] = files_ids.get(os.path.basename(info['path']),'')
    return imgs_info


def create_message(imgs_info: list) -> None:
    """
    Funcion que crea un mensaje en la orden de venta asociada a una imagen

    Parametros
    ----------
    imgs_info : list[dict]
        Lista de diccionarios con propiedades
            - path: Ruta de acceso a imagen
            - order_id: ID de orden en ERP
            - file_id: ID de imagen en ERP
            - order_name: Numero de orden
            - tracking_id: Numero de rastreo detectado
            - n_products: Cantidad de productos detectados
    Regresa
    -------
    None
    """
    # Preparar lista de mensajes a crear
    msg_template = "<b>Numero de orden:</b> {order_name}<br>" + \
    "<b>Numero de rastreo:</b> {tracking_id}<br>" + \
    "<b>Numero de products:</b> {n_products}"
    records = []
    for info in imgs_info:
        if not info['order_id']:
            continue
        msg = {
            'model': 'sale.order',
            'res_id': info['order_id'],
            'author_id': DB_INFO['uid'],
            'subtype_id': 2,
            'body': msg_template.format(**info),
            'attachment_ids': [info['file_id']]
        }
        records.append(msg)
    # Crear mensajes en ERP
    logger.info('Creando mensajes en ERP')
    MODELS.execute_kw(DB_INFO['db'], DB_INFO['uid'], DB_INFO['password'], 'mail.message', 'create',
                      [records])

