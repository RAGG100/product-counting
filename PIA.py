# Importar funciones de pipeline
from PYCD_RAGG.image_retrieval import get_images, transform_images
from PYCD_RAGG.object_detection import detect_objects, process_guides, process_products
from PYCD_RAGG.image_uploading import get_tracking_info, get_sale_order, upload_image, create_message
from PYCD_RAGG.error_management import move_images_drive
import logging, json

if __name__ == '__main__':
    with open('logging.json') as file:
        logging.config.dictConfig(json.load(file))

    logger = logging.getLogger('base')

    logger.info('Iniciando obtencion de imagenes')    
    imgs_info = transform_images(get_images())

    logger.info('Iniciando deteccion de objetos')    
    imgs_info = detect_objects(imgs_info)
    for info in imgs_info:
        objs = info.pop('objects',[])
        info['n_products'] = process_products([obj for obj in objs if obj['name'] == 'Producto'])
        info['tracking_id'] = process_guides([obj for obj in objs if obj['name'] == 'Guia'], info['path'])

    logger.info('Iniciando carga de imagenes')
    create_message(upload_image(get_sale_order(get_tracking_info(imgs_info))))

    logger.info('Separando imagenes con problemas')
    move_images_drive([info['drive_link'] for info in imgs_info if not info['tracking_id']])

    logger.info('Guardando resultados en /datasets/results.csv')
    with open('./datasets/results.csv', 'w') as file:
        print("Ubicacion,Link de Drive,Numero de rastreo,Numero de orden,Numero de productos", file=file)
        info_row = "{path},{drive_link},{tracking_id},{order_name},{n_products}"
        for info in imgs_info:
            print(info_row.format(**info), file=file)
    logger.info('Proceso terminado')