# Importar funciones de pipeline
from PYCD_RAGG.image_retrieval import get_images, transform_images
from PYCD_RAGG.object_detection import detect_objects, process_guides, process_products
from PYCD_RAGG.image_uploading import get_tracking_info, get_sale_order, upload_image, create_message

if __name__ == '__main__':
    folder = transform_images(get_images())
    imgs_info = detect_objects(folder)
    for info in imgs_info:
        objs = info.pop('objects',[])
        info['n_products'] = process_products([obj for obj in objs if obj['name'] == 'Producto'])
        info['tracking_id'] = process_guides([obj for obj in objs if obj['name'] == 'Guia'], info['path'])
    create_message(upload_image(get_sale_order(get_tracking_info(imgs_info))))

    with open('debug.txt', 'w') as file:
        info_row = """path: {path}
Numero de orden: {order_name}
Numero de rastreo: {tracking_id}
Numero de productos: {n_products}
-------------------------------------"""
        for info in imgs_info:
            print(info_row.format(**info), file=file)
