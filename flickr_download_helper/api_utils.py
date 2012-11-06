from flickr_download_helper.api import json_request


def method_info(api, token, method_name):
    rsp_json = json_request(api, token, 'flickr.reflection.getMethodInfo',
        "method info for %s", [method_name], method_name=method_name)
    return rsp_json if rsp_json else None


def reflect(api, token):
    rsp_json = json_request(api, token, 'flickr.reflection.getMethods',
        "methods")
    return rsp_json['methods']['method'] if rsp_json else None
