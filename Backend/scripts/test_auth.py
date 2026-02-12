import urllib.request

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/api/accounts/me/', timeout=5)
    print('Status:', response.status)
except Exception as e:
    print('Expected auth error:', str(e)[:100])
