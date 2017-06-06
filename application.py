from urllib.parse import parse_qs
from html import escape
import pycurl
from io import BytesIO

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, 'http://pycurl.io/')
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()

curl -H https://api.github.com/search/repositories?q=tetris&sort=created&order=desc?page=1&per_page=5 \
"Accept: application/vnd.github.v3.full+json"

body = buffer.getvalue()
# Body is a byte string.
# We have to know the encoding in order to print it to a text file
# such as standard output.
print(body.decode('iso-8859-1'))

html = """
<html>
<body>
   <form method="get" action="">
        <p>
           Age: <input type="text" name="age" value="%(age)s">
        </p>
        <p>
            Hobbies:
            <input
                name="hobbies" type="checkbox" value="software"
                %(checked-software)s
            > Software
            <input
                name="hobbies" type="checkbox" value="tunning"
                %(checked-tunning)s
            > Auto Tunning
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>
    <p>
        Age: %(age)s<br>
        Hobbies: %(hobbies)s
    </p>
</body>
</html>
"""

def application(env, start_response):
    # Returns a dictionary in which the values are lists
    d = parse_qs(env['QUERY_STRING'])

    # As there can be more than one value for a variable then
    # a list is provided as a default value.
    age = d.get('age', [''])[0]  # Returns the first age value
    hobbies = d.get('hobbies', [])  # Returns a list of hobbies

    # Always escape user input to avoid script injection
    age = escape(age)
    hobbies = [escape(hobby) for hobby in hobbies]

    body = html % {  # Fill the above html template in
        'checked-software': ('', 'checked')['software' in hobbies],
        'checked-tunning': ('', 'checked')['tunning' in hobbies],
        'age': age or 'Empty',
        'hobbies': ', '.join(hobbies or ['No Hobbies?'])
    }

    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html')
    ]
    start_response(status, headers)

    return [body.encode('utf8')]