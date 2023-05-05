# Data Engineering - Tech Assessment

By Elías D. Nino-Ruiz - https://enino84.github.io/

## Overview

My solution is built on Microsoft Azure, a cloud computing platform, and it involves several services to manage data in the cloud. The *Storage* account service is used as a data lake and employs *blobs* to store the data. The *Data Factory* service is used to copy the information into the data lake and also to trigger an *Azure Function* for data formatting. The Azure Function formats the data and sends it to a *blob storage*, which will be consumed by a Copy data service from the Data Factory. Finally, a *SQL Server* is used as a data warehouse to store the data in a relational format, after all JSONs have been processed by the Azure Function. Overall, this solution provides a comprehensive and efficient approach to handling data in the cloud, utilizing a variety of Azure services to achieve a robust and scalable architecture.

## General Structure of the solution

<img src="images/general_pipeline.png">