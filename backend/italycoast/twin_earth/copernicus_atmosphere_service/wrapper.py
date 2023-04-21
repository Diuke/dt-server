import requests
import simplejson
import numpy as np
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from twin_earth.copernicus_atmosphere_service import utils as cams_utils
from twin_earth import utils as general_utils
from twin_earth import models as dte_models
from django.contrib.gis.geos import GEOSGeometry

def get_data(layer, params):
    url = cams_utils.build_cams_service_url(layer, params)

    html_query = requests.get(url)
    parsed_html = BeautifulSoup(html_query.content, 'html.parser')

    td_value_element = parsed_html.find('td', text='Value')
    query_value = td_value_element.next_sibling.text
    #remove whitespaces and units
    query_value = [word for word in query_value.split() if word.replace('.','',1).isdigit()]
    resp_body = dict()
    resp_body['value'] = float(query_value[0])
    resp_body['units'] = layer.units

    return resp_body

def get_parameters(layer: dte_models.Layer, parameter: str):
    urlSuffix = "&request=GetCapabilities&service=WMS&VERSION=1.3.0&layer=" + layer.layer_name
    url = layer.service_url + urlSuffix
    print(url)
    namespaces = {
        "opengis": "http://www.opengis.net/wms" 
    }

    xml_GetCapabilities = requests.get(url)
    xml_text = xml_GetCapabilities.text
    xml = ET.fromstring(xml_text)

    example_layer = xml.find(".//opengis:Layer[opengis:Name='" + layer.layer_name + "']", namespaces)
    time_dimension = example_layer.find(f'./opengis:Dimension[@name="{parameter}"]', namespaces)
    
    param_object = {
        "default": time_dimension.attrib.get("default"),
        "units": time_dimension.attrib.get("units"),
        "name": time_dimension.attrib.get("name"),
        "values": time_dimension.text.strip().split(",")
    }
    if param_object["name"] == "time":
        complete_time_list = general_utils.format_time_intervals(param_object["values"])
        param_object["values"] = complete_time_list
        param_object["values"].reverse()
    
    return param_object


def get_time_series(layer, params):
    #start time - end time
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    level = params.get('level')
    bbox = params.get('bbox')

    base_params = { "bbox": bbox }
    base_url = cams_utils.build_cams_service_url(layer, base_params)

    resp_body = {
        "x": [],
        "y": [],
        "units": layer.units 
    }

    url = base_url + '&time=' + str(start_date) + "/" + str(end_date)
    if level:
        url += '&level=' + str(level)
    xml_Query = requests.get(url)
    print(url)
    xml_text = xml_Query.text
    xml = ET.fromstring(xml_text)
    
    feature_infos = xml.findall("FeatureInfo")

    for feature in feature_infos:
        feature_info_time = feature.find("time").text
        feature_info_value = feature.find("value").text
        resp_body['x'].append(feature_info_time)
        resp_body['y'].append(feature_info_value)

    print(resp_body)
    return resp_body


def get_depth_profile(layer, params):
    time = params.get('time')
    bbox = params.get('bbox')

    base_params = { "bbox": bbox }
    base_url = cams_utils.build_cams_service_url(layer, base_params)

    levels = get_parameters(layer, "level")

    resp_body = {
        "x": [],
        "y": [],
        "units": layer.units 
    }
    for level in levels['values']:

            url = base_url + '&'
            url += 'time=' + str(time)
            url += '&level=' + str(level)
            xml_Query = requests.get(url)
            xml_text = xml_Query.text
            xml = ET.fromstring(xml_text)
            
            feature_info = xml.find(f"FeatureInfo/value")
            feature_info_value = feature_info.text
            if feature_info_value == "none": #break if the request produce no values
                break

            resp_body['y'].append(level)
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
    level = params.get("level")
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
    url = layer.service_url + "&"
    url += "SERVICE=WMS&"
    url += "VERSION=1.3.0&"
    url += "REQUEST=GetFeatureInfo&"
    url += "FORMAT=image/png&"
    url += "TRANSPARENT=true&"
    url += "QUERY_LAYERS=" + layer.layer_name + "&"
    url += "TILED=true&"
    url += "LAYERS=" + layer.layer_name + "&"
    url += "BBOX=" + bbox_string + "&"
    url += "CRS=EPSG:3857&"
    url += "INFO_FORMAT=text/html&"
    url += f"WIDTH={str(x_resolution)}&HEIGHT={str(y_resolution)}&STYLES="
    url += "&time=" + time
    if level:
        url += "&level=" + level
    base_url = url
    
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
                request_url = base_url + "&I=" + str(x) + "&J=" + str(y)
                html_query = requests.get(request_url)
                parsed_html = BeautifulSoup(html_query.content, 'html.parser')

                td_value_element = parsed_html.find('td', text='Value')
                query_value = td_value_element.next_sibling.text
                #remove whitespaces and units
                feature_info_value = [word for word in query_value.split() if word.replace('.','',1).isdigit()]
                try:
                    numerical_value = float(feature_info_value[0])
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
    try:
        avg_value = np.nanmean(response_matrix)
    except Exception as ex:
        avg_value = None

    
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
            