from __future__ import unicode_literals

import logging
import argparse
import datetime
import requests
import json
import urlparse
import os

from google.cloud import storage


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

URL = 'https://opensky-network.org/api/states/all'
PATHNAME = 'opensky'
# going to save to ndjson
# API returns awkward json blob
SUFFIX = '.ndjson'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dest', help='Destination storage path')
    parser.add_argument('-p', '--project_id', help='Target Project')
    return parser.parse_args()


def get_bucket_path(dest, now):
    dst = urlparse.urlparse(dest)
    assert(dst.scheme == 'gs')

    bucket = dst.hostname
    path = os.path.join(dst.path,
                        PATHNAME,
                        now.strftime('%Y'),
                        now.strftime('%m'),
                        now.strftime('%d'),
                        PATHNAME + '-' + now.strftime('%Y%m%d%H%M%S') +
                        SUFFIX)
    if path[0] == '/':
        path = path[1:]

    return bucket, path


def main():
    args = parse_args()
    bucket_name, path_name = get_bucket_path(args.dest,
                                             datetime.datetime.now().utcnow())
    logger.info("Saving to %s, %s" % (bucket_name, path_name))

    # Fetch data from API and convert states into lines of text
    resp = requests.get(URL)
    data = resp.json()
    states = data['states']
    lines = '\n'.join([json.dumps(s) for s in states])

    client = storage.Client(args.project_id)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(path_name)
    blob.upload_from_string(json.dumps(lines))


if __name__ == "__main__":
    main()
