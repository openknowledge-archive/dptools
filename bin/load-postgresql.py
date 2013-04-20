'''Command line tool to load a Simple Data Format Data Package into Postgresql.
'''
import json
import argparse
import urlparse
import os
import sqlite3
import urllib
import urllib2
import csv


# http://www.sqlite.org/datatype3.html
mappings = {
    'string': 'text',
    'number': 'numeric',
    # integer: integer
    'date': 'date',
    'datetime': 'timestamp',
    # 'boolean': 'boolean'
    }

def load(dpurlOrPath):
    if not dpurlOrPath.split('://')[0] in ['http', 'https', 'ftp']:
        # it's a path
        dpurl = path2url(dpurlOrPath)
    else:
        dpurl = dpurlOrPath
    dpfo = urllib2.urlopen(dpurl)
    out = json.load(dpfo)
    for finfo in out['resources']:
        # normalization so we do not have to handle both alternatives
        if not 'url' in finfo:
            finfo['url'] = urlparse.urljoin(dpurl, finfo['path'])
        process_resource(finfo)

def process_resource(finfo):
    '''Load the resource specified by finfo into the database at dbpath
    '''
    if 'name' in finfo:
        tablename = finfo['name']
    else:
        _fname = urlparse.urlparse(finfo.get('url', ''))[2].split('/')[-1]
        tablename = os.path.splitext(_fname)[0]
    fields = finfo['schema']['fields']
    _columns = ','.join(
            ['\n  "%s" %s' % (field['id'], mappings[field['type']])
                for field in fields]
            )
    sql = 'CREATE TABLE "%s" (%s\n);' % (tablename, _columns)
    print sql
    fpath = finfo['url'].replace('file://', '')
    copysql = '''COPY "%s" FROM '%s' WITH CSV;''' % (tablename, fpath)
    print copysql


def path2url(path):
    return urlparse.urljoin(
        'file:', urllib.pathname2url(path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print SQL to load a data package into postgres.')
    parser.add_argument('datapackage')
    args = parser.parse_args() 
    load(args.datapackage)

