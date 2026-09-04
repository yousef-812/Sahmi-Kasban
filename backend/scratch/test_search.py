import urllib.request, json, urllib.parse

def test_query(q):
    url = 'https://sahmi-kasban.fly.dev/api/v1/market/instruments?query=' + urllib.parse.quote(q)
    res = json.loads(urllib.request.urlopen(url).read())
    print(q, '->', [item['ticker'] for item in res.get('items', [])])

test_query('kora')
test_query('KORA')
test_query('كورة')
test_query('كورا')
