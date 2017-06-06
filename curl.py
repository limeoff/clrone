import pycurl
import json
from io import BytesIO

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, 'https://api.github.com/search/repositories?q=tetris&sort=created&order=desc?page=1&per_page=5')
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()

body = buffer.getvalue().decode('iso-8859-1')
values = json.loads(body)
# Body is a byte string.
# We have to know the encoding in order to print it to a text file
# such as standard output.
print(values['total_count'])