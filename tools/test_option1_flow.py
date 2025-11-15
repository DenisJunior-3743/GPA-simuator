import urllib.parse, urllib.request, time

# Wait a moment for server to start
time.sleep(2)

# Prepare sample form data: 2 courses, A (3 CU) and B (3 CU)
data = {
    'num_courses': '2',
    'grade_1': 'A',
    'cu_1': '3',
    'grade_2': 'B',
    'cu_2': '3'
}

data = urllib.parse.urlencode(data).encode()
req = urllib.request.Request('http://127.0.0.1:5000/option1', data=data, method='POST')

try:
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode('utf-8')
    print('\n--- Response body (truncated to 2000 chars) ---')
    print(body[:2000])
    print('\n--- End response ---')
except Exception as e:
    print('Test failed:', e)
