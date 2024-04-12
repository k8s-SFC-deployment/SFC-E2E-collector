import json

def load_json_one_depth_v2(json_str, except_keys=[]):
    json_dict = json.loads(json_str)
    for ek in except_keys:
        if ek in json_dict.keys() and json_dict[ek] is not None:
            json_dict[ek] = json.dumps(json_dict[ek])
    return json_dict