import urllib.parse, urllib.request, json, time

# Wait briefly for server to be ready
time.sleep(1)

data = {
    'num_courses': '2',
    'grade_1': 'A',
    'cu_1': '3',
    'grade_2': 'B',
    'cu_2': '3'
}

data = urllib.parse.urlencode(data).encode()
req = urllib.request.Request('http://127.0.0.1:5000/api/option1', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

try:
    resp = urllib.request.urlopen(req, timeout=10)
    body = resp.read().decode('utf-8')
    print('Status:', resp.status)
    j = json.loads(body)
    print('JSON:', j)
    assert 'result' in j, 'Missing result in JSON'
    print('Test OK — GPA =', j['result'])
except Exception as e:
    print('Test failed:', e)
