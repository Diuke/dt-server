import requests
import xml.etree.ElementTree as ET
import numpy as np
import simplejson

from twin_earth.copernicus_marine_services import utils as cmems_utils
from twin_earth import utils as general_utils
from django.contrib.gis.geos import GEOSGeometry

def get_parameters(layer, parameter):
    urlSuffix = "?request=GetCapabilities&service=WMS&VERSION=1.3.0&layer=" + layer.layer_name
    url = layer.service_url + urlSuffix
    namespaces = {
        "opengis": "http://www.opengis.net/wms" 
    }

    xml_GetCapabilities = requests.get(url)
    xml_text = xml_GetCapabilities.text
    xml = ET.fromstring(xml_text)

    #["WMS_Capabilities"]["Capability"][0]["Layer"][0]["Layer"][0]["Layer"][0]["Dimension"]
    parameter_values = xml.findall(f"opengis:Capability/opengis:Layer/opengis:Layer/opengis:Layer/opengis:Dimension[@name='{parameter}']", namespaces=namespaces)
    
    param_object = {
        "default": parameter_values[0].get("default"),
        "units": parameter_values[0].get("units"),
        "name": parameter_values[0].get("name"),
        "values": parameter_values[0].text.strip().split(",")
    }
    if param_object["name"] == "time":
        complete_time_list = general_utils.format_time_intervals(param_object["values"])
        param_object["values"] = complete_time_list
        param_object["values"].reverse()
    
    return param_object


def get_data(layer, params):
    url = cmems_utils.build_copernicus_marine_service_url(layer, params)
    xml_Query = requests.get(url)
    xml_text = xml_Query.text
    xml = ET.fromstring(xml_text)
    resp_body = dict()
    feature_info = xml.find(f"FeatureInfo/value")
    try:
        feature_value = float(feature_info.text)
        feature_value = round(feature_value, 4)
    except Exception as ex:
        feature_value = 0
    
    resp_body['value'] = feature_value
    resp_body['units'] = layer.units
    return resp_body

def get_time_series(layer, params):
    #start time - end time
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    elevation = params.get('elevation')
    bbox = params.get('bbox')

    base_params = { "bbox": bbox }
    base_url = cmems_utils.build_copernicus_marine_service_url(layer, base_params)

    resp_body = {
        "x": [],
        "y": [],
        "units": layer.units 
    }

    url = base_url + '&time=' + str(start_date) + "/" + str(end_date)
    if elevation:
        url += '&elevation=' + str(elevation)
    xml_Query = requests.get(url)
    xml_text = xml_Query.text
    xml = ET.fromstring(xml_text)
    
    feature_infos = xml.findall("FeatureInfo")

    for feature in feature_infos:
        feature_info_time = feature.find("time").text
        feature_info_value = feature.find("value").text
        resp_body['x'].append(feature_info_time)
        resp_body['y'].append(feature_info_value)

    return resp_body


def get_depth_profile(layer, params):
    time = params.get('time')
    bbox = params.get('bbox')

    base_params = { "bbox": bbox }
    base_url = cmems_utils.build_copernicus_marine_service_url(layer, base_params)

    elevations = get_parameters(layer, "elevation")

    resp_body = {
        "x": [],
        "y": [],
        "units": layer.units 
    }
    for elevation in elevations['values']:

            url = base_url + '&'
            url += 'time=' + str(time)
            url += '&elevation=' + str(elevation)
            xml_Query = requests.get(url)
            xml_text = xml_Query.text
            xml = ET.fromstring(xml_text)
            
            feature_info = xml.find(f"FeatureInfo/value")
            feature_info_value = feature_info.text
            if feature_info_value == "none": #break if the request produce no values
                break

            resp_body['y'].append(elevation)
            resp_body['x'].append(feature_info_value)            

    return resp_body


def get_area_statistics(layer, params):
    #default resolution
    x_resolution = 20
    y_resolution = 20
    bbox_string = params.get("bbox")
    bbox = bbox_string.split(",") # [min_x, min_y, max_x, max_y]
    time = params.get("time")
    histogram_classes = params.get("classes")
    elevation = params.get("elevation")
    polygon_geojson = simplejson.loads(params.get("polygon"))
    polygon_geometry = polygon_geojson["features"][0]["geometry"]
    polygon_geometry["crs"] = {
        "type": "name",
        "properties": {
            "name": "EPSG:3857"
        }
    }
    
    #Create a geometry to only request pixels where they intersect with the AOI
    geojson = simplejson.dumps(polygon_geometry)
    polygon_feature = GEOSGeometry(geojson)

    resolution = params.get("resolution")
    if resolution == "high":
        x_resolution = 20
        y_resolution = 20
    elif resolution == "low":
        x_resolution = 10
        y_resolution = 10
    else:
        x_resolution = 10
        y_resolution = 10

    start_x = float(bbox[0])
    end_x = float(bbox[2])
    start_y = float(bbox[1])
    end_y = float(bbox[3])

    x_len = abs(end_x - start_x)
    y_len = abs(end_y - start_y)
    x_step = x_len / x_resolution
    y_step = y_len / y_resolution

    #Build base url
    base_url = layer.service_url + "?" + "SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&INFO_FORMAT=text/xml&SRS=EPSG:3857"
    base_url += "&HEIGHT=" + str(y_resolution) + "&WIDTH=" + str(x_resolution)
    base_url += "&BBOX=" + bbox_string
    base_url += "&QUERY_LAYERS=" + layer.layer_name
    base_url += "&time=" + time
    if elevation:
        base_url += "&elevation=" + elevation
    
    response_matrix = np.zeros((x_resolution, y_resolution))
    list_data = []
    cells_with_values = 0
    
    for x in range(x_resolution):
        for y in range(y_resolution):
            x_min = start_x + (x * x_step)
            x_max = x_min + x_step
            y_min = start_y + (y * y_step)
            y_max = y_min + y_step
            cell_geometry = f"SRID=3857;POLYGON (({x_min} {y_min}, {x_min} {y_max}, {x_max} {y_max}, {x_max} {y_min}, {x_min} {y_min}))"
            cell_polygon = GEOSGeometry(cell_geometry)
            
            if cell_polygon.intersects(polygon_feature):
                request_url = base_url + "&X=" + str(x) + "&Y=" + str(y)

                xml_Query = requests.get(request_url)
                xml_text = xml_Query.text
                xml = ET.fromstring(xml_text)
                
                feature_info = xml.find(f"FeatureInfo/value")
                feature_info_value = feature_info.text
                try:
                    numerical_value = float(feature_info_value)
                    cells_with_values += 1
                    list_data.append(numerical_value)

                except Exception as ex:
                    numerical_value = np.NaN

                response_matrix[x, y] = numerical_value
            else:
                response_matrix[x, y] = np.NaN

    median = np.nanmedian(response_matrix)
    stdev = np.nanstd(response_matrix)
    min_value = np.nanmin(response_matrix)
    max_value = np.nanmax(response_matrix)
    avg_value = np.nanmean(response_matrix)

    
    resp = {
        "sampling": simplejson.dumps(response_matrix.tolist(), ignore_nan=True),
        "histogram": np.histogram(list_data, histogram_classes),
        "min": min_value,
        "max": max_value,
        "median": median,
        "standard_deviation": stdev,
        "average": avg_value,
        "total_samples_with_value": cells_with_values
    }
    
    return resp
            