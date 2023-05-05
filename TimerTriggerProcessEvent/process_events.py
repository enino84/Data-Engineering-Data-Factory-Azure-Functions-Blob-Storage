import pandas as pd
import numpy as np
import io
from azure.storage.blob import BlobServiceClient


class event_handler:

    def __init__(self) -> None:
        connection_string = "DefaultEndpointsProtocol=https;AccountName=lokas3;AccountKey=U9uju7/K+uYBuThv1Ptq9WF4ysdoh1fiLYZJh4r6WXp54WwhvTouahYJwz5hqov7veVzgZRKNhaC+AStRYnMMA==;EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = "lokadata"
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

        self.df_vehicles = pd.DataFrame()
        self.df_operating = pd.DataFrame()


    def operating_period_create(self, event):
        event_ = event['data']

        df_ = pd.DataFrame({'id':     [event_['id']], 
                            'start':    [event_['start']], 
                            'finish':    [event_['finish']], 
                            'event':  'create'})
        
        if self.df_vehicles.empty:
            self.df_operating = df_
        else:
            self.df_operating = pd.concat((self.df_operating, df_))


    def operating_period_delete(self, event):
        event_ = event['data']

        df_ = pd.DataFrame({'id':     [event_['id']], 
                            'start':    [event_['start']], 
                            'finish':    [event_['finish']], 
                            'event':  'delete'})
        
        if self.df_vehicles.empty:
            self.df_operating = df_
        else:
            self.df_operating = pd.concat((self.df_operating, df_))


    def vehicle_register(self, event):
        event_ = event['data']

        df_ = pd.DataFrame({'id':     [event_['id']], 
                            'lat':    [np.nan], 
                            'lon':    [np.nan], 
                            'date':   [event['at']],
                            'event':  'register'})
        
        if self.df_vehicles.empty:
            self.df_vehicles = df_
        else:
            self.df_vehicles = pd.concat((self.df_vehicles, df_))

    def vehicle_update(self, event):
        event_ = event['data']
        locat_ = event_['location']

        df_ = pd.DataFrame({'id':     [event_['id']], 
                            'lat':    [locat_['lat']], 
                            'lon':    [locat_['lng']], 
                            'date':   [locat_['at']],
                            'event':  'update'})
        
        if self.df_vehicles.empty:
            self.df_vehicles = df_
        else:
            self.df_vehicles = pd.concat((self.df_vehicles, df_))


    def vehicle_deregister(self, event):
        event_ = event['data']

        df_ = pd.DataFrame({'id':     [event_['id']], 
                            'lat':    [np.nan], 
                            'lon':    [np.nan], 
                            'date':   [event['at']],
                            'event':  'deregister'})
        
        if self.df_vehicles.empty:
            self.df_vehicles = df_
        else:
            self.df_vehicles = pd.concat((self.df_vehicles, df_))


    def process_event(self, event):
        if event['on']=='vehicle':
            if event['event']=='register':   self.vehicle_register(event)
            if event['event']=='update':     self.vehicle_update(event)
            if event['event']=='deregister': self.vehicle_deregister(event)
        elif event['on']=='operating_period':
            if event['event']=='create':     self.operating_period_create(event)
            if event['event']=='delete':     self.operating_period_delete(event)
        else:
            pass

    def process_blob(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_contents = blob_client.download_blob().readall()
        data = blob_contents.decode('utf-8')
        jsons = data.split('\n')

        for json_ in jsons[:-1]:
            self.process_event(eval(json_))


    def process_blobs(self):
        blob_list = self.container_client.list_blobs()

        for blob in blob_list:
            self.process_blob(blob.name)
       

    def store_processed_blobs(self):
        csv_ =  io.BytesIO(self.df_vehicles.to_csv(index=False).encode('utf-8'))
        blob_client = self.blob_service_client.get_blob_client('lokadataprocessed', 'vehicle_events.csv')
        blob_client.upload_blob(csv_, overwrite=True)

        csv_ =  io.BytesIO(self.df_operating.to_csv(index=False).encode('utf-8'))
        blob_client = self.blob_service_client.get_blob_client('lokadataprocessed', 'operating_events.csv')
        blob_client.upload_blob(csv_, overwrite=True)

