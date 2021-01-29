import requests
import json


def http_get_size(url):
    headers = {
        'authentication': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0NzA3NiwidHlwZSI6InVzZXIiLCJpc19hZG1pbiI6MCwiaWF0IjoxNjExNTM5MDMyLCJleHAiOjE2MTIxNDM4MzJ9.JDO7ZUSBwLhi19icpcJzNTJbjqfNULkclq5zKTrFrOY'
    }
    response = requests.request("GET", url, headers=headers)
    jdata = json.loads(response.text)
    face_data = jdata["data"]["faces"]  # List
    face_name = ["F", "H", "FR", "FL"]
    output = {}
    for face in face_data:
        if face["name"] in face_name:
            output[face["name"]] = face
    return output


def get_face_size(face):
    face_size = [face["w"], face["h"]]
    return face_size


def get_face_loc(face):
    face_loc = [face["x"], face["y"]]
    return face_loc


if __name__ == '__main__':
    out = http_get_size("https://www.baoxiaohe.com/api/bs/box/project/knifes?bleed=3&dpi=3.7795275591&id=200227")
    print(out)
