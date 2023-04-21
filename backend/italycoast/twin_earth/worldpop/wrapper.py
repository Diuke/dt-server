import requests
import xml.etree.ElementTree as ET

from twin_earth.worldpop import utils as worlpop_utils

def get_data(layer, params):
    url = worlpop_utils.build_worldpop_service_url(layer, params)
    
    if not layer:
        return None

    try:
        namespaces = {
            "wfs": "http://www.opengis.net/wfs",
            "gml": "http://www.opengis.net/gml",
            "wpGlobal": "wpGlobal" 
        }

        xml_Query = requests.get(url)
        worldpop_version = xml_Query.headers.get("QUERY_LAYERS")
        xml_text = xml_Query.text
        xml = ET.fromstring(xml_text)
        resp_body = dict()
        if "ppp_2015" in url: worldpop_version = "ppp_2015"
        elif "ppp_2016" in url: worldpop_version = "ppp_2016"
        elif "ppp_2017" in url: worldpop_version = "ppp_2017"
        elif "ppp_2018" in url: worldpop_version = "ppp_2018"
        elif "ppp_2019" in url: worldpop_version = "ppp_2019"
        elif "ppp_2020" in url: worldpop_version = "ppp_2020"

        feature_info = xml.find(f"gml:featureMember/wpGlobal:" + str(worldpop_version) + "/wpGlobal:People_Per_Pixel", namespaces=namespaces)
        numerical_value = float(feature_info.text)
        numerical_value = 0 if numerical_value == -99999 else numerical_value
        numerical_value = round(numerical_value, 4)

        resp_body['value'] = numerical_value
        resp_body['units'] = layer.units

        return resp_body
    except Exception as ex:
        return None
