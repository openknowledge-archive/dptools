'''Command line tool to load a Simple Data Format Data Package into sqlite.

For usage do:

    python load-sqlite.py -h
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
    'number': 'real',
    'float': 'real',
    # integer: integer
    'date': 'string',
    'boolean': 'integer'
    }

def load(dpurlOrPath, sqlitePath):
    if not dpurlOrPath.split('://')[0] in ['http', 'https', 'ftp']:
        # it's a path
        dpurl = path2url(dpurlOrPath)
    else:
        dpurl = dpurlOrPath
    # urljoin makes this work right -
    # http://docs.python.org/2/library/urlparse.html#urlparse.urljoin
    dpurl = urlparse.urljoin(dpurl, 'datapackage.json')
    basepath = dpurlOrPath.rstrip('datapackage.json')
    dpfo = urllib2.urlopen(dpurl)
    out = json.load(dpfo)
    for finfo in out['files']:
        # normalization so we do not have to handle both alternatives
        if not 'url' in finfo:
            finfo['url'] = urlparse.urljoin(dpurl, finfo['path'])
        process_file(finfo, sqlitePath, dpurl)

def process_file(finfo, dbpath, dpurl):
    '''Load the file specified by finfo into the database at dbpath
    '''
    if 'name' in finfo:
        tablename = finfo['name']
    else:
        _fname = urlparse.urlparse(finfo.get('url', ''))[2].split('/')[-1]
        tablename = os.path.splitext(_fname)[0]
    fields = finfo['schema']['fields']
    _columns = ','.join(
            ['"%s" %s' % (field['id'], mappings[field['type']])
                for field in fields]
            )
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    sql = 'CREATE TABLE "%s" (%s)' % (tablename, _columns)
    c.execute(sql)

    _insert_tmpl = 'insert into "%s" values (%s)' % (tablename,
                ','.join(['?']*len(fields)))

    # could do this on but not very robust and will not work on remote urls ...
    # sqlite> .mode csv
    # sqlite> .import <filename> <table>
    reader = csv.reader(urllib2.urlopen(finfo['url']))
    # skip headers
    reader.next()
    for row in reader:
        c.execute(_insert_tmpl, row)
    conn.commit()
    c.close()

def path2url(path):
    return urlparse.urljoin(
        'file:', urllib.pathname2url(path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load a data package into sqlite.')
    parser.add_argument('datapackage',
                       help='an integer for the accumulator')
    parser.add_argument('sqlite',
                       help='path to sqlite db')
    args = parser.parse_args() 
    load(args.datapackage, args.sqlite)

