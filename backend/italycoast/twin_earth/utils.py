import datetime
import requests
import re
import xml.etree.ElementTree as ET

from twin_earth.copernicus_marine_services import utils as cmems_utils
from twin_earth.copernicus_land_service import utils as clms_utils

#Function to separate generic time intervals
def format_time_intervals(time_list):
    complete_list = []
    for element in time_list:
        split_interval = element.strip().split("/")
        if len(split_interval) > 1:
            interval_list = []
            first_date = None
            end_date = None
            format_suffix = ""
            try:
                #Extract dates with timezone as it comes from the service -- Format: 2021-10-28T23:30:00.000Z
                first_date = datetime.datetime.strptime(split_interval[0], "%Y-%m-%dT%H:%M:%S.000Z")
                end_date = datetime.datetime.strptime(split_interval[1], "%Y-%m-%dT%H:%M:%S.000Z")
                format_suffix = "00.000Z"
            except Exception as ex:
                #Some services have different formats... Format: 2021-10-28T23:30:00Z
                first_date = datetime.datetime.strptime(split_interval[0], "%Y-%m-%dT%H:%M:%SZ")
                end_date = datetime.datetime.strptime(split_interval[1], "%Y-%m-%dT%H:%M:%SZ")
                format_suffix = "00Z"
            
            if first_date is None or end_date is None:
                raise ValueError("Date format incorrect")
            
            interval = str(split_interval[2])
            #Define the interval step
            #"PXDTXHXM"
            if "P" in interval:
                #remove the P
                interval = interval[1:]
                interval_days = 0
                interval_hours = 0
                interval_minutes = 0
                if "T" in interval and not "D" in interval:
                    interval_parts = interval.split("T")
                    interval_time = interval_parts[1]
                    if "H" in interval_time: #hours present
                        interval_hours = interval_time.split("H")[0]
                        if "M" in interval_time: #hours and minutes
                            interval_minutes = interval_time.split("M")[1]
                    else: #only minutes
                        interval_minutes = interval_time.split("M")[0]

                elif "T" in interval and "D" in interval: #days and time
                    interval_parts = interval.split("T")
                    interval_date = interval_parts[0]
                    interval_time = interval_parts[1]

                    interval_days = interval_date.split("D")[0]
                    if "H" in interval_time: #hours present
                        interval_hours = interval_time.split("H")[0]
                        if "M" in interval_time: #hours and minutes
                            interval_minutes = interval_time.split("M")[1]
                    else: #only minutes
                        interval_minutes = interval_time.split("M")[0]
                    
                
                else: #only days
                    interval_days = interval.split("D")[0]

            interval_days = int(interval_days)
            interval_hours = int(interval_hours)
            interval_minutes = int(interval_minutes)

            while first_date <= end_date: 
                month = f'0{first_date.month}' if len(str(first_date.month)) == 1 else f'{first_date.month}'
                day = f'0{first_date.day}' if len(str(first_date.day)) == 1 else f'{first_date.day}'
                hours = f'0{first_date.hour}' if len(str(first_date.hour)) == 1 else f'{first_date.hour}'
                minutes = f'0{first_date.minute}' if len(str(first_date.minute)) == 1 else f'{first_date.minute}'
                date_to_add = f'{first_date.year}-{month}-{day}T{hours}:{minutes}:{format_suffix}'
                interval_list.append(date_to_add)
                first_date = first_date + datetime.timedelta(hours=(interval_days*24)+interval_hours, minutes=interval_minutes)

            complete_list += interval_list 
        else: 
            complete_list.append(element)  

    return complete_list


def build_wms_get_feature_info_url(service_url, params):
    url = service_url + "?"
    url += "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&"
    for param in params:
        url += param["key"] + "=" + param["value"] + "&"

#params -> {bbox: [min_lat, min_lng, max_lat, max_lng], dimensions: {dim1: value, dim2: value}}
def build_layer_feature_info_url(layer, params):
    try:
        url = ""

        if layer.source == "Copernicus Marine Services":
            url = cmems_utils.build_copernicus_marine_service_url(layer, params)

        elif layer.source == "Copernicus Land Service":
            url = clms_utils.build_copernicus_land_service_url(layer, params)
        else:
            return None

        #&QUERY_LAYERS=chl&LAYERS=chl&BBOX=1252344.271424327%2C5205055.8781073615%2C1291480.0299063374%2C5244191.636589372&CRS=EPSG%3A3857&time=2020-04-01T12%3A00%3A00.000Z&elevation=-3625.703857421875&INFO_FORMAT=text%2Fxml&I=39&J=154&WIDTH=256&HEIGHT=256&STYLES=
        return url
    except Exception as ex:
        return None