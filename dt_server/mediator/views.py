import simplejson
import xml.etree.ElementTree as ET
import requests

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_api_key.permissions import HasAPIKey
from api.models import Layer
from rest_framework.response import Response
from rest_framework import status as http_status
from wrappers.copernicus_marine_service import wrapper as cmems_wrapper
from wrappers.copernicus_land_service import wrapper as clms_wrapper
from wrappers.worldpop import wrapper as worldpop_wrapper
#from wrappers.geoportale_nazionale import wrapper as geoportale_wrapper
from wrappers.copernicus_atmosphere_service import wrapper as cams_wrapper
from wrappers import utils as general_utils

POINT_REQUEST_TYPE = "point"
DEPTH_REQUEST_TYPE = "depth_profile"
AREA_REQUEST_TYPE = "area"
TIME_SERIES_REQUEST_TYPE = "time_series"
VISUALIZE = "visualize"

@api_view(['GET'])
@permission_classes([HasAPIKey])
def get_list_of_parameter_values(request, layer_id, parameter):
    try:
        layer = Layer.objects.get(id=int(layer_id))
    except Exception as ex:
        return Response(http_status.HTTP_404_NOT_FOUND)

    params = {}
    #route the request to the specific wrapper
    if layer.source == "Copernicus Marine Service":
        params = cmems_wrapper.get_parameters(layer, parameter)

    elif layer.source == "Copernicus Land Monitoring Service":
        return Response("Incorrect Source", http_status.HTTP_400_BAD_REQUEST)

    elif layer.source == "WorldPop":
        return Response("Incorrect Source", http_status.HTTP_400_BAD_REQUEST)

    elif layer.source == "Geoportale Nazionale":
        return Response("Incorrect Source", http_status.HTTP_400_BAD_REQUEST)

    elif layer.source == "Copernicus Atmosphere Monitoring Service":
        params = cams_wrapper.get_parameters(layer, parameter)
    
    else:
        return Response("Incorrect Layer", http_status.HTTP_400_BAD_REQUEST)

    return Response(params, http_status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasAPIKey])
def get_data(request):
    try:
        data = simplejson.loads(request.body)
        params = data["params"]
        #params example
        # "params": {
        #     "bbox": [978393.9620502554,5518141.945963444,988177.9016707579,5527925.8855839465],
        #     "elevation": -1.0182366371154785,
        #     "time": "2022-10-01T00:00:00.000Z"
        # }
        data_request_type = data["type"] # point, area, time_series, depth_profile
        layer_id = int(data["layer_id"])
        layer = Layer.objects.get(id=layer_id)

        #route the request to the specific wrapper
        if layer.source == "Copernicus Marine Service":
            if data_request_type == POINT_REQUEST_TYPE:
                response_data = cmems_wrapper.get_data(layer, params)

            elif data_request_type == AREA_REQUEST_TYPE:
                response_data = cmems_wrapper.get_area_statistics(layer, params)
                
            elif data_request_type == DEPTH_REQUEST_TYPE:
                response_data = cmems_wrapper.get_depth_profile(layer, params)

            elif data_request_type == TIME_SERIES_REQUEST_TYPE:
                response_data = cmems_wrapper.get_time_series(layer, params)
                
            else:
                return Response("Incorrect Request Type", http_status.HTTP_400_BAD_REQUEST)

        elif layer.source == "Copernicus Land Monitoring Service":
            if data_request_type == POINT_REQUEST_TYPE:
                response_data = clms_wrapper.get_data(layer, params)
                
            else:
                return Response("Incorrect Request Type", http_status.HTTP_400_BAD_REQUEST)

        elif layer.source == "WorldPop":
            if data_request_type == POINT_REQUEST_TYPE:
                response_data = worldpop_wrapper.get_data(layer, params)
            else:
                return Response("Not supported", http_status.HTTP_400_BAD_REQUEST)
        elif layer.source == "Geoportale Nazionale":
            if data_request_type == POINT_REQUEST_TYPE:
                return Response("Not yet supported", http_status.HTTP_400_BAD_REQUEST)
                #response_data = geoportale_wrapper.get_data(layer, params)

            else:
                return Response("Incorrect Request Type", http_status.HTTP_400_BAD_REQUEST)

        elif layer.source == "Copernicus Atmosphere Monitoring Service":
            if data_request_type == POINT_REQUEST_TYPE:
                response_data = cams_wrapper.get_data(layer, params)
            elif data_request_type == AREA_REQUEST_TYPE:
                response_data = cams_wrapper.get_area_statistics(layer, params)
                
            # elif data_request_type == DEPTH_REQUEST_TYPE:
            #     response_data = cams_wrapper.get_depth_profile(layer, params)

            # elif data_request_type == TIME_SERIES_REQUEST_TYPE:
            #     response_data = cams_wrapper.get_time_series(layer, params)

            else:
                return Response("Incorrect Request Type", http_status.HTTP_400_BAD_REQUEST)

        else:
            return Response("Incorrect Layer", http_status.HTTP_400_BAD_REQUEST)

        if response_data:
            return Response(response_data, http_status.HTTP_200_OK)
        else:
            return Response("No Data", http_status.HTTP_400_BAD_REQUEST)

    except Exception as ex:
        print(ex.with_traceback())
        return Response("error", http_status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasAPIKey])
def update_layers(request):
    db_layers = Layer.objects.all()
    response_text = "Updated: "

    for layer in db_layers:
        if layer.type == Layer.LayerType.WMS:
            if layer.enabled:
                if layer.source == 'Copernicus Marine Service' or layer.source == 'Copernicus Atmosphere Monitoring Service':
                    # Define the namespace
                    namespace = {'opengis': 'http://www.opengis.net/wms'}
                    url = ""
                    if "?" in layer.service_url:
                        url = layer.service_url + "&service=WMS&request=GetCapabilities"
                    else:
                        url = layer.service_url + "?service=WMS&request=GetCapabilities"

                    layer_name = layer.layer_name 
                    print(f'Layer url: {url}')
                    print(f'Layer name: {layer_name}')

                    response = requests.get(url)
                    root = ET.fromstring(response.content)

                    # Get the name of the "example" layer
                    example_layer = root.find(".//opengis:Layer[opengis:Name='" + layer_name + "']",namespace)
                    if example_layer is not None:

                        print()
                        print(layer.pk)
                        # get the name of the layer
                        example_layer_name = example_layer.find('opengis:Name',namespace).text

                        # get the abstract of the layer
                        example_layer_abstract = example_layer.find('opengis:Abstract',namespace).text
                        layer.description = example_layer_abstract

                        # get the legend url of the layer
                        example_layer_legend_url = example_layer.find('./opengis:Style/opengis:LegendURL/opengis:OnlineResource',namespace).attrib['{http://www.w3.org/1999/xlink}href']
                        layer.legend_url = example_layer_legend_url

                        #Dimensions
                        # get the time dimension
                        if "time" in layer.parameters:
                            time_dimension = example_layer.find('./opengis:Dimension[@name="time"]', namespace)
                            if time_dimension is not None:
                                #extract the text of the xml element
                                time_dimension_xml = time_dimension
                                time_dimension = time_dimension.text
                                time_dimension = time_dimension.strip().split(",")

                                #get the list of times, start date, and end date
                                complete_time_list = general_utils.format_time_intervals(time_dimension)
                                start_time = complete_time_list[0].split("T")[0]
                                end_time = complete_time_list[len(complete_time_list)-1].split("T")[0]
                                layer.initial_time_range = start_time
                                layer.final_time_range = end_time

                        # if "elevation" in layer.parameters:
                        #     # get the elevation dimension
                        #     elevation_dimension = example_layer.find('./opengis:Dimension[@name="elevation"]', namespace)
                        #     if elevation_dimension is not None:
                        #         #extract the text of the xml element
                        #         elevation_dimension_xml = elevation_dimension
                        #         elevation_dimension = elevation_dimension.text
                        #         #remove whitespaces
                        #         elevation_dimension = "".join(elevation_dimension.split())

                        # if "level" in layer.parameters:
                        #     # get the elevation dimension
                        #     level_dimension = example_layer.find('./opengis:Dimension[@name="level"]', namespace)
                        #     if level_dimension is not None:
                        #         #extract the text of the xml element
                        #         level_dimension_xml = level_dimension
                        #         level_dimension = level_dimension.text
                        #         #remove whitespaces
                        #         level_dimension = "".join(level_dimension.split())
                                
                    layer.save()
                    response_text += ("layer " + str(layer.pk) + ", ")
                
    return Response(response_text, http_status.HTTP_200_OK)