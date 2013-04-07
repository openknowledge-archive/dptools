# Create a datapackage.json file
import csv
import json
import collections

def extract(fileobj):
    reader = csv.reader(fileobj)
    headers = reader.next()
    fields = [ {'id': h, 'type': 'string'} for h in headers ]
    dp = collections.OrderedDict({
        'name': '',
        'license': [{
            'name': 'Public Domain Dedication and License',
            'url': 'http://opendatacommons.org/licenses/pddl/1.0/'
        }]
    })
    dp['files'] = [
            {
                'schema': { 'fields': fields }
            }
        ]
    out = json.dumps(dp, indent=2)
    print out

import sys
if __name__ == '__main__':
    url =  sys.argv[1]
    extract(open(url))

