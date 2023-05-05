# Data Engineering - Tech Assessment

By Elías D. Nino-Ruiz - https://enino84.github.io/

## Overview

My solution is built on Microsoft Azure, a cloud computing platform, and it involves several services to manage data in the cloud. The *Storage* account service is used as a data lake and employs *blobs* to store the data. The *Data Factory* service is used to copy the information into the data lake and also to trigger an *Azure Function* for data formatting. The Azure Function formats the data and sends it to a *blob storage* in the form of csv files, which will be consumed by a Copy data service from the Data Factory. Finally, a *SQL Server* is used as a data warehouse to store the data in a relational format, after all JSONs have been processed by the Azure Function. Overall, this solution provides a comprehensive and efficient approach to handling data in the cloud, utilizing a variety of Azure services to achieve a robust and scalable architecture.

## General Structure of the solution

To facilitate the task at hand, I first created a resource group named "loka" that contains all the required services. Within this resource group, I created three containers:

- `lokadatacopied` is used to emulate the data source and holds the JSON files provided by you from the `s3://de-tech-assessment-2022` endpoint.

- `lokadata` is used to copy the files from the `lokadatacopied` container. This container is filled by the "Copy - Blob to Blob" process, which emulates the process of copying data from a remote host.

- `lokadataprocessed` stores the results of executing an Azure Function named `TimerTriggerProcessEvent`. This function formats the JSON files into a tabular format suitable for storage in a relational database, or data warehouse. The `TimerTriggerProcessEvent` function is based on two Python files: `__init__.py` and `process_events.py`. The `__init__.py` file contains the main function, which is as follows:

```python
import logging
import azure.functions as func

from .process_events import event_handler


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    p = event_handler()
    p.process_blobs()
    p.store_processed_blobs()
    return func.HttpResponse("* Data processed.", status_code=200)
```

This function first imports the logging module and the azure.functions module, which provides functionality for creating Azure Functions. It also imports the `event_handler` class from a module named process_events.

The function creates an instance of the `event_handler` class named `p` and then calls two methods on it: `process_blobs()` and `store_processed_blobs()`. The `process_blobs()` method processes JSON data from blob files in the `lokadata` container, and the `store_processed_blobs()` method stores the resulting data in the `lokadataprocessed` container.


<img src="images/general_pipeline.png">


## Handler Function

<img src="images/class_diagram.png">