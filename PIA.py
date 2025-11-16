# Importar funciones de pipeline
from PYCD_RAGG.image_retrieval import get_images, transform_images

if __name__ == '__main__':
    transform_images(get_images())