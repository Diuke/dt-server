import twin_earth.models as dte_models

def build_copernicus_marine_service_url(layer: dte_models.Layer, params):
    base_url = layer.service_url
    url = base_url + "?"
    url += "SERVICE=WMS&"
    url += "VERSION=1.3.0&"
    url += "REQUEST=GetFeatureInfo&"
    url += "FORMAT=image/png&"
    url += "TRANSPARENT=true&"
    url += "QUERY_LAYERS=" + layer.layer_name + "&"
    url += "TILED=true&"
    url += "LAYERS=" + layer.layer_name + "&"
    url += "BBOX=" + params["bbox"] + "&"
    url += "CRS=EPSG:3857&"

    #add the dimensions if present
    # dimensions are comma-separated
    for p in layer.parameters.split(","):
        if params.get(p):
            url += str(p) + "=" + str(params[p]) + "&"    

    url += "INFO_FORMAT=text/xml&"
    url += "I=0&J=0&WIDTH=1&HEIGHT=1&STYLES="
    return url
            
