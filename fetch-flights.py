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
                        '.json')
    if path[0] == '/':
        path = path[1:]

    return bucket, path


def main():
    args = parse_args()
    bucket_name, path_name = get_bucket_path(args.dest,
                                             datetime.datetime.now().utcnow())
    logger.info("Saving to %s, %s" % (bucket_name, path_name))
    resp = requests.get(URL)
    data = resp.json()

    client = storage.Client(args.project_id)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(path_name)
    blob.upload_from_string(json.dumps(data))


if __name__ == "__main__":
    main()
