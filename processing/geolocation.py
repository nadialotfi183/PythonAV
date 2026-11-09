import requests as http

from requests import Response

def geo_location(ip):
    response = http.get("https://ipapi.co/"+ip+"/json/")
    if response.status_code == 200:
        print(response.json())
    if __name__ == "_main_":
        print(geo_location("88.147.152.239"))