import requests

url = "https://dolphin.jump-technology.com:8443/api/v1/asset"

payload = ""
headers = {
    'Content-Type': "application/json",
    'Authorization': ",Basic RVBJVEFfR1JPVVBFNDp2Umt0OUtoUVpUaHM1aFFn",
    'User-Agent': "PostmanRuntime/7.19.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "5a07920d-1756-4e03-ac2b-ce9e4e572979,6bcd6812-5661-4478-a572-d54e4cd21d8c",
    'Host': "dolphin.jump-technology.com:8443",
    'Accept-Encoding': "gzip, deflate",
    'Cookie': "JSESSIONID=GtSmZJYOGPUmI8MZReNkedNcw7U2rA0ScFg3OW2n.win-sdtshov0af5",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

auth = ("EPITA_GROUPE4", "vRkt9KhQZThs5hQg")

response = requests.request("GET", url, data=payload, headers=headers, auth=auth)

print(response.text)
