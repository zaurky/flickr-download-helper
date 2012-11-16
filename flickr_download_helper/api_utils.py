"""
Module that expose 2 methods to reflect flickr api
"""

from flickr_download_helper.api import json_request


def method_info(api, token, method_name):
    """ get information on a given flick api method """
    rsp_json = json_request(api, token, 'flickr.reflection.getMethodInfo',
        "method info for %s", [method_name], method_name=method_name)
    return rsp_json if rsp_json else None


def reflect(api, token):
    """ get the list of flickr api methods """
    rsp_json = json_request(api, token, 'flickr.reflection.getMethods',
        "methods")
    return rsp_json['methods']['method'] if rsp_json else None
