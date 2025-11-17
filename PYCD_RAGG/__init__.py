import json, logging, logging.config
with open('logging.json') as file:
    logging.config.dictConfig(json.load(file))

logger = logging.getLogger('base')
logger.info("Empezando nueva ejecucion.")
