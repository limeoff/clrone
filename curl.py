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
                 'https://api.github.com/search/repositories?q=' + q + '&sort=created&order=desc?page=1&per_page=' + str(
                     num))
    else:
        print("Something wrong!  Check arguments.")

    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    body = buffer.getvalue()
    values = json.loads(body)

    return values


f=codecs.open("template.html", 'r')
html = f.read()
f.close()

for i in html.split("</body>"):
    if "</h1>" in i:
        data = i[i.find("</h1>") + len("</h1>"):]

html = html.replace(data, '\n{placeholder}\n')

search_term = 'arrow'
num = 5
num_commits = 1

repos = curl_request(num, q = search_term)

#print(repos)
fill_html = {'search_term': search_term}

n = 0
for items in repos['items']:
    n += 1
    fill_body = {'num': n,
                 'repository_name': items['name'],
                 'created_at': items['created_at'],
                 'owner_url': items['owner']['html_url'],
                 'avatar_url': items['owner']['avatar_url'],
                 'owner_login': items['owner']['login']}
    #print(fill_body)
    commits = curl_request(num_commits, api_url=items['commits_url'].replace('{/sha}', ''))
    for commit in commits:
        fill_body.update({
            'sha': commit['sha'],
            'commit_message': commit['commit']['message'],
            'commit_author_name': commit['commit']['author']['name'],
        })
        print(fill_body)

fill_html.update({'num': '',
            'repository_name': '',
            'created_at': '',
            'owner_url': '',
            'avatar_url': '',
            'owner_login': '',
            'sha': '',
            'commit_message': '',
            'commit_author_name': '',
            'placeholder': data})

print(fill_html)


body = html.format(**fill_html)

