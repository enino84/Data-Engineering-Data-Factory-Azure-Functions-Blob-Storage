# Data Engineering - Tech Assessment

By Elías D. Nino-Ruiz - https://enino84.github.io/

## Overview

My solution is built on Microsoft Azure, a cloud computing platform, and it involves several services to manage data in the cloud. The *Storage* account service is used as a data lake and employs *blobs* to store the data. The *Data Factory* service is used to copy the information into the data lake and also to trigger an *Azure Function* for data formatting. The Azure Function formats the data and sends it to a *blob storage* in the form of csv files, which will be consumed by a Copy data service from the Data Factory. Finally, a *SQL Server* is used as a data warehouse to store the data in a relational format, after all JSONs have been processed by the Azure Function. Overall, this solution provides a comprehensive and efficient approach to handling data in the cloud, utilizing a variety of Azure services to achieve a robust and scalable architecture.

## General Structure of the Solution

To facilitate the task at hand, I first created a resource group named "loka" that contains all the required services. Within this resource group, I created three containers:

<img src="images/general_pipeline.png">

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

while the Class diagram of `process_events.py` is shown next:

<img src="images/class_diagram.png">

This `__init__.py` first imports the logging module and the azure.functions module, which provides functionality for creating Azure Functions. The function creates an instance of the `event_handler` class named `p` and then calls two methods on it: `process_blobs()` and `store_processed_blobs()`. The `process_blobs()` method processes JSON data from blob files in the `lokadata` container, and the `store_processed_blobs()` method stores the resulting data in the `lokadataprocessed` container. On the other hand, The `event_handler` class contains several methods that handle different events related to the vehicles and their operating periods. For example, the `vehicle_register` method is called when a new vehicle is registered, and it creates a new row in the `df_vehicles` DataFrame with the vehicle's ID, latitude, longitude, registration date, and event type. Similarly, the `vehicle_update` method is called when a vehicle's location is updated, and it adds a new row to `df_vehicles` with the updated location information.

The `process_event` method is responsible for calling the appropriate method based on the event type. For example, if the event is related to a vehicle, it calls one of the vehicle-related methods (i.e., `vehicle_register`, `vehicle_update`, or `vehicle_deregister`), and if the event is related to an operating period, it calls one of the operating-period-related methods (i.e., `operating_period_create` or `operating_period_delete`).

The `process_blob` method is responsible for processing a single JSON blob. It first downloads the blob's contents as a string, then splits the string into individual JSON objects. Finally, it iterates over each JSON object, evaluates it using the `eval` function (which converts the JSON string into a Python dictionary), and passes the resulting dictionary to the `process_event` method to handle the event.

The `process_blobs` method is responsible for processing all blobs in the `lokadata` container. It first retrieves a list of all blobs in the container using the `list_blobs` method of the container client, then iterates over each blob and calls the `process_blob` method to handle the events contained in that blob.

Finally, the `store_processed_blobs` method is responsible for uploading the processed data to the `lokadataprocessed` container in CSV format. It first creates an in-memory byte stream (`io.BytesIO`) containing the contents of each DataFrame as CSV, then uploads each byte stream as a blob to the appropriate location in the container using the `upload_blob` method of the blob client. This Azure function is responsible for processing incoming JSON data, extracting relevant events, and storing them in a relational database. The use of Pandas DataFrames and Azure Blob Storage makes it easy to manipulate the data in memory before storing it, and the structured event handling makes it easy to modify the function to handle new event types in the future.

### Detailed View

| Item | Description |
| --- | --- |
| Purpose | Processes events from JSON data stored in Azure Blob Storage and stores the results in two CSV files in Azure Blob Storage. |
| Programming Language | Python |
| External Libraries | `pandas`, `numpy`, `io`, `azure.storage.blob` |
| Functions | `operating_period_create()`, `operating_period_delete()`, `vehicle_register()`, `vehicle_update()`, `vehicle_deregister()`, `process_event()`, `process_blob()`, `process_blobs()`, `store_processed_blobs()` |
| Main Function | `main()` |
| Parameters | `req`: an HTTP request object |
| Returns | an HTTP response object |
| Dependencies | Azure Blob Storage connection string and container name |
| Output | Two CSV files in Azure Blob Storage: `vehicle_events.csv` and `operating_events.csv`. |
| Description | This code reads JSON data stored in Azure Blob Storage, extracts relevant events from it, processes the events, and stores the results in two CSV files in Azure Blob Storage. The code defines five functions to process events (`operating_period_create()`, `operating_period_delete()`, `vehicle_register()`, `vehicle_update()`, and `vehicle_deregister()`), one function to process an event (`process_event()`), one function to process a blob (`process_blob()`), one function to process all blobs in a container (`process_blobs()`), and one function to store processed data in CSV files in Azure Blob Storage (`store_processed_blobs()`). The `main()` function calls these functions in sequence and returns an HTTP response object. The code relies on `pandas`, `numpy`, `io`, and `azure.storage.blob` libraries to read and write data in CSV format and to connect to Azure Blob Storage. The code is properly documented with comments and clear variable names. |

## Azure Data Factory

The Data Factory pipeline is named "fetchdatatoblob" and contains several activities that copy data from one location to another and process it.

The first activity is named "Copy - Blob to Blob" and copies JSON data from the "lokadata" container to the "lokadatacopied" container in Azure Blob Storage. This activity uses a JSON source and sink, and a tabular translator to map the JSON fields to columns in the destination dataset.

The second activity is an Azure Function activity named "Azure Function - Process Events". This activity calls an Azure Function named "TimerTriggerProcessEvent" with an HTTP GET method and a "Process" header. This function processes the JSON data that was copied in the previous activity and extracts relevant events from it.

The third activity is named "Copy - Events Vehicles" and copies the extracted vehicle-related events to a SQL Server sink dataset named "DWHLoka". This activity uses a delimited text source, a tabular translator, and enables type conversion to map the data fields to SQL columns.

The fourth activity is named "Copy - Events on Operating Period" and copies the extracted operating-period-related events to another SQL Server sink dataset named "DWHLokaOperating". This activity also uses a delimited text source, a tabular translator, and enables type conversion to map the data fields to SQL columns.

Overall, this pipeline fetches data from the "lokadata" container, processes it using an Azure Function, and stores the results in two SQL Server datasets for further analysis. The pipeline can be modified to match different source and destination locations, as well as different processing functions and data schemas. 

# Advantages vs Disadvantages

## Advantages of my approach:

The advantages of this solution are many. First, it utilizes the power and flexibility of Microsoft Azure, which is a cloud computing platform that offers a wide range of services for data management, storage, processing, and analysis. Azure provides a robust and scalable infrastructure that can handle large volumes of data with ease, and it offers features such as automatic scaling, load balancing, and redundancy that ensure high availability and fault tolerance.

Second, the solution uses a variety of Azure services to achieve a comprehensive and efficient approach to handling data in the cloud. The Storage account service is used as a data lake to store the data, and blobs are used to store the JSON files provided as input. The Data Factory service is used to copy the information into the data lake and to trigger an Azure Function for data formatting. The Azure Function formats the data and sends it to a blob storage in the form of CSV files, which are then consumed by a Copy data service from the Data Factory. Finally, a SQL Server is used as a data warehouse to store the data in a relational format, after all JSONs have been processed by the Azure Function. This end-to-end pipeline ensures that the data is processed efficiently and accurately, and that it is stored in a format that is easy to query and analyze.

Third, the solution is highly modular and customizable. The use of a Class in the Python code allows for easy modification and extension of the functionality to handle different types of events or data sources. Moreover, the use of Pandas DataFrames and Azure Blob Storage makes it easy to manipulate the data in memory before storing it, and the structured event handling makes it easy to modify the function to handle new event types in the future. This modularity and flexibility are essential in a dynamic data environment where new data sources and formats can emerge at any time.

The use of Microsoft Azure services, the end-to-end pipeline architecture, and the modularity and flexibility of the Python code make this solution an efficient and scalable approach to handling data in the cloud.

## Disadvantages

The solution may not be accessible to some users due to the required expertise in Azure services and Python programming. The use of an Azure Function may introduce latency and processing overhead, which could affect system performance. The use of a relational database may limit the system's ability to handle unstructured or semi-structured data.