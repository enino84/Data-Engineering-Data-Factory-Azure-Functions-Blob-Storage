import logging
import azure.functions as func

from .process_events import event_handler


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    p = event_handler()
    p.process_blobs()
    p.store_processed_blobs()
    return func.HttpResponse("* Data processed.", status_code=200)
