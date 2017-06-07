from urllib.parse import parse_qs
from html import escape
from io import BytesIO
import pycurl
import json
import codecs


def curl_request(num, q='', api_url=''):

    buffer = BytesIO()
    c = pycurl.Curl()
    if api_url:
        c.setopt(c.URL, api_url)
    elif q:
        c.setopt(c.URL,
                 'https://api.github.com/search/repositories?q='
                 + q + '&sort=created&order=desc?page=1&per_page='
                 + str(num))
    else:
        print("Something wrong!  Check arguments.")

    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    body = buffer.getvalue()
    values = json.loads(body)

    return values

f = codecs.open("template.html", 'r')
html = f.read()
f.close()


def application(env, start_response):
    # Returns a dictionary in which the values are lists
    d = parse_qs(env['QUERY_STRING'])

    # As there can be more than one value for a variable then
    # a list is provided as a default value.
    search_term = d.get('search_term', [''])[0]  # Returns the first age value

    # prevent script injection by escape
    search_term = escape(search_term)

    #hobbies = [escape(hobby) for hobby in hobbies]

    fill = {'search_term': search_term,
            'num': '',
            'repository_name': '',
            'created_at': '',
            'owner_url': '',
            'avatar_url': '',
            'owner_login': '',
            'sha': '',
            'commit_message': '',
            'commit_author_name': ''}

    for i in html.split("</body>"):
        if "</h1>" in i:
            data = i[i.find("</h1>") + len("</h1>"):]

    html = html.replace(data, '\n{placeholder}\n')

    body = html.format(**fill)

    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html')
    ]
    start_response(status, headers)

    return [body.encode('utf8')]
