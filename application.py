from urllib.parse import parse_qs
from html import escape
from io import BytesIO
from time import strftime, strptime, mktime
import codecs
import json
import pycurl


def curl_request(num, q='', api_url=''):
    """Sending the CURL request to api.github.com via PycURL
    and returns answer
    Args:
        num (int): The first parameter.
        q (str): The second parameter.
        api_url (str):
    Returns:
        dict: answer from github api, converted to dictionary
    """
    buffer = BytesIO()
    c = pycurl.Curl()
    # requests to  https://api.github.com depending of giving args
    if api_url:
        c.setopt(c.URL, api_url + '?page=1&per_page=' + str(num))
    elif q:
        c.setopt(c.URL,
                 'https://api.github.com/search/repositories?q=' + q + '&per_page=' + str(num))
    else:
        print("Something wrong!  Check arguments.")

    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    response = buffer.getvalue()
    # converting JSON to dict
    values = json.loads(response.decode('utf-8'))

    return values


def application(env, start_response):

    # setting variables
    # searching for 5 repos and 1 commit for each
    search_num = 5
    num_commits = 1
    # string for repos and commits insertion
    body = ''
    # dictionary of values that will be filled to template placeholders
    fill_body = {}

    # parsing GET params dictionary
    d = parse_qs(env['QUERY_STRING'])
    # get only one search_term param
    search_term = d.get('search_term', [''])[0]
    # good practice for security reasons
    search_term = escape(search_term)

    # loading HTML template
    f = codecs.open("template.html", 'r')
    html = f.read()
    f.close()
    # split template to header/footer and body parts
    for key in html.split("</body>"):
        if "</h1>" in key:
            body_temp = key[key.find("</h1>") + len("</h1>"):]
    # put placeholder instead of cut body
    html = html.replace(body_temp, '{placeholder}\n')

    # initiating search request of repos
    repos = curl_request(search_num, q=search_term)

    # filling up fill_body by needed values from each find repository
    for items in repos['items']:
        # convert datetime to desired format from JSON format
        created = strftime('%Y-%m-%d %H:%M:%S', strptime(items['created_at'], '%Y-%m-%dT%H:%M:%SZ'))
        # convert datetime in seconds for easy sort as github API not provide sorting of searched repos
        created_sec = mktime(strptime(items['created_at'], '%Y-%m-%dT%H:%M:%SZ'))

        fill_body[created_sec] = {'repository_name': items['name'],
                                  'created_at': created,
                                  'owner_url': items['owner']['html_url'],
                                  'avatar_url': items['owner']['avatar_url'],
                                  'owner_login': items['owner']['login']}

        # initiating search request of commits
        commits = curl_request(num_commits, api_url=items['commits_url'].replace('{/sha}', ''))
        # filling up fill_body by needed values from each find last commit repository
        for commit in commits:
            fill_body[created_sec].update({'sha': commit['sha'],
                                           'commit_message': commit['commit']['message'],
                                           'commit_author_name': commit['commit']['author']['name']})

    n = 0
    # sorting repositories by creation date and assemble body string
    for key in sorted(fill_body.keys(), reverse=True):
        n += 1
        fill_body[key].update({'num': n})
        body += body_temp.format(**fill_body[key])

    # filling up fill_html
    fill_html = {'search_term': search_term,
                 'placeholder': body}

    # assemble ready html
    html = html.format(**fill_html)

    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html')
    ]
    start_response(status, headers)

    return [html.encode('utf8')]
