import urllib.parse, urllib.request, http.cookiejar, json, time

# Wait briefly
time.sleep(1)

# Create a cookie jar to maintain session
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1) Create a user directly in DB by calling a small endpoint? We don't have that, so try register via vault_manager via HTTP register if available.
# The /login endpoint only needs username present in users table. We'll create a user via direct DB insert by calling an internal helper is not possible here.
# Instead, try to register via /register if exists; otherwise, expect API endpoints to return 401 for guest.

# Try login with username 'testuser' (login route does simple select, user must exist). We'll attempt to register by POSTing to /register if it exists.
register_url = 'http://127.0.0.1:5000/register'
login_url = 'http://127.0.0.1:5000/login'

# Attempt to register
try:
    data = urllib.parse.urlencode({'username':'testuser','password':'guest'}).encode()
    req = urllib.request.Request(register_url, data=data, method='POST')
    resp = opener.open(req, timeout=5)
    print('Register status', resp.status)
except Exception as e:
    print('Register failed or not available:', e)

# Attempt login
try:
    data = urllib.parse.urlencode({'username':'testuser'}).encode()
    req = urllib.request.Request(login_url, data=data, method='POST')
    resp = opener.open(req, timeout=5)
    print('Login status', resp.status)
except Exception as e:
    print('Login failed (likely register not available):', e)

# Call /api/option2 preview
try:
    data = urllib.parse.urlencode({'new_gpa':'4.0','new_cu':'15'}).encode()
    req = urllib.request.Request('http://127.0.0.1:5000/api/option2', data=data, method='POST')
    resp = opener.open(req, timeout=5)
    body = resp.read().decode()
    print('option2 status', resp.status, 'body', body)
except Exception as e:
    print('api/option2 call failed:', e)

# Call /api/save-semester
try:
    data = urllib.parse.urlencode({'academic_year':'2025','semester_num':'1','total_cu':'15','gpa':'4.0'}).encode()
    req = urllib.request.Request('http://127.0.0.1:5000/api/save-semester', data=data, method='POST')
    resp = opener.open(req, timeout=5)
    body = resp.read().decode()
    print('save-semester status', resp.status, 'body', body)
except Exception as e:
    print('api/save-semester call failed:', e)
