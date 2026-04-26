import requests, sqlite3

# Register test user
r = requests.post('http://localhost:8000/api/auth/register', json={
    'email': 'monitor_test@example.com',
    'password': 'test123456',
    'nickname': 'Monitor Test'
}, timeout=5)
print('Register:', r.status_code, r.text[:200])

token = None
if r.status_code in (200, 201):
    token = r.json().get('access_token')
elif r.status_code == 400:
    # User exists, try login with same password
    r = requests.post('http://localhost:8000/api/auth/login', json={
        'email': 'monitor_test@example.com',
        'password': 'test123456'
    }, timeout=5)
    print('Login:', r.status_code)
    if r.status_code == 200:
        token = r.json().get('access_token')

if token:
    headers = {'Authorization': 'Bearer ' + token}
    
    r2 = requests.get('http://localhost:8000/api/monitor/keywords', headers=headers, timeout=5)
    print('GET /keywords:', r2.status_code, r2.text[:200])
    
    r3 = requests.post('http://localhost:8000/api/monitor/keywords', headers=headers, json={'name': 'GPT-5', 'value': 'GPT-5', 'is_active': True}, timeout=5)
    print('POST /keywords:', r3.status_code)
    if r3.status_code != 201:
        print('  Error:', r3.text[:300])
    
    r4 = requests.post('http://localhost:8000/api/monitor/accounts', headers=headers, json={'name': 'karpathy', 'value': 'karpathy', 'is_active': True}, timeout=5)
    print('POST /accounts:', r4.status_code)
    if r4.status_code != 201:
        print('  Error:', r4.text[:300])
    
    # Test GET accounts
    r5 = requests.get('http://localhost:8000/api/monitor/accounts', headers=headers, timeout=5)
    print('GET /accounts:', r5.status_code, r5.text[:300])
    
    # Test GET sources (all including monitor types)
    r6 = requests.get('http://localhost:8000/api/sources/?monitor_type=keyword', headers=headers, timeout=5)
    print('GET /sources/?monitor_type=keyword:', r6.status_code, r6.text[:200])
else:
    print('Could not authenticate')
