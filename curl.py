import pycurl
import json
from io import BytesIO
import codecs


def curl_request(num, q='', api_url=''):

    buffer = BytesIO()
    c = pycurl.Curl()
    if api_url:
        c.setopt(c.URL,api_url + '?page=1&per_page=' + str(num))
    elif q:
        c.setopt(c.URL,
                 'https://api.github.com/search/repositories?q=' + q + '&per_page=' + str(num))
    else:
        print("Something wrong!  Check arguments.")

    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    response = buffer.getvalue()
    values = json.loads(response.decode('utf-8'))

    return values


f=codecs.open("template.html", 'r')
html = f.read()
f.close()

for i in html.split("</body>"):
    if "</h1>" in i:
        body_temp = i[i.find("</h1>") + len("</h1>"):]

html = html.replace(body_temp, '\n{placeholder}\n')

search_term = 'arrow'
num = 5
num_commits = 1
body = ''

repos = curl_request(num, q = search_term)
#print(repos)

n = 0
for items in repos['items']:
    fill_body = {'repository_name': items['name'],
                 'created_at': items['created_at'],
                 'owner_url': items['owner']['html_url'],
                 'avatar_url': items['owner']['avatar_url'],
                 'owner_login': items['owner']['login']}
    #print(fill_body)
    commits = curl_request(num_commits, api_url=items['commits_url'].replace('{/sha}', ''))
    for commit in commits:
        n = n + 1
        fill_body.update({'num': n,
            'sha': commit['sha'],
            'commit_message': commit['commit']['message'],
            'commit_author_name': commit['commit']['author']['name'],
        })
        #print(fill_body)
        body = body_temp.format(**fill_body) + body
        #print(body)


fill_html = {'search_term': search_term,
             'placeholder': body}

#print(fill_html)


html = html.format(**fill_html)
print(html)

