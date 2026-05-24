import requests
res = requests.post("http://localhost:8000/monogram", json={"text": "namaskar"})
print(res.status_code)
