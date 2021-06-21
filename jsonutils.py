import json

def return_as_json(to_return):
    try:
        return json.dumps(to_return, indent=4, sort_keys=True, ensure_ascii=False)
    except TypeError:
        return json.dumps(to_return, indent=4, ensure_ascii=False)