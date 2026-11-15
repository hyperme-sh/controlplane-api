"""Read the tagged GHCR inventory; never changes tags or package settings."""
import argparse
import base64
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
import urllib.error

REPOSITORY = os.environ.get('HISTORICAL_REPOSITORY', 'hyperme-sh/controlplane-api/runtime')
if REPOSITORY not in {'hyperme-sh/controlplane-api/runtime'}:
    raise ValueError('Unreviewed GHCR repository')
BASE = 'https://ghcr.io'
DIGEST = re.compile(r'sha256:[0-9a-f]{64}')
ACCEPT = ', '.join(('application/vnd.oci.image.index.v1+json',
    'application/vnd.docker.distribution.manifest.list.v2+json',
    'application/vnd.oci.image.manifest.v1+json',
    'application/vnd.docker.distribution.manifest.v2+json'))


def registry_url(url):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'https' or parsed.netloc != 'ghcr.io'
            or not parsed.path.startswith('/v2/' + REPOSITORY + '/') or parsed.fragment
            or '..' in urllib.parse.unquote(parsed.path).split('/')):
        raise ValueError('Registry pagination escaped the selected repository')
    return url


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Authenticated registry API redirects are refused')


def platform_manifests(document, digest):
    if not DIGEST.fullmatch(digest):
        raise ValueError('Invalid manifest digest')
    if 'manifests' not in document:
        return [digest], []
    selected, omitted = [], []
    for row in document['manifests']:
        if not DIGEST.fullmatch(row['digest']):
            raise ValueError('Invalid child manifest digest')
        platform = row.get('platform', {})
        if platform.get('os') == 'linux' and platform.get('architecture') == 'amd64':
            selected.append(row['digest'])
        else:
            omitted.append({'digest': row['digest'], 'platform': platform})
    return selected, omitted


def inventory(request):
    tags = set()
    url = BASE + '/v2/' + REPOSITORY + '/tags/list?n=100'
    seen = set()
    while url:
        registry_url(url)
        if url in seen:
            raise ValueError('Registry pagination loop')
        seen.add(url)
        document, headers, _ = request(url)
        for tag in document.get('tags') or []:
            if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}', tag):
                raise ValueError('Invalid registry tag')
            tags.add(tag)
        link = headers.get('Link')
        if link:
            match = re.fullmatch(r'<([^>]+)>;\s*rel="?next"?', link)
            if not match:
                raise ValueError('Unsupported registry pagination')
            url = urllib.parse.urljoin(url, match.group(1))
        else:
            url = None
    images, observations, omitted = {}, [], []
    for tag in sorted(tags):
        document, headers, raw = request(BASE + '/v2/' + REPOSITORY + '/manifests/' + tag)
        digest = 'sha256:' + hashlib.sha256(raw).hexdigest()
        if headers.get('Docker-Content-Digest') != digest:
            raise ValueError('Registry manifest bytes differ from advertised digest')
        selected, other = platform_manifests(document, digest)
        observations.append({'tag': tag, 'manifest': digest, 'selected': selected})
        omitted.extend(other)
        for child in selected:
            images.setdefault(child, []).append(tag)
    if len(images) > 256:
        raise ValueError('Actions matrix limit exceeded; split explicitly')
    return {'repository': REPOSITORY, 'tag_observations': observations,
            'images': [{'digest': digest, 'tags': names} for digest, names in sorted(images.items())],
            'omitted_platform_manifests': omitted,
            'scope': 'Retained tagged manifests at collection time; Linux amd64; no untagged/deleted versions or other registries'}


def main(output):
    credentials = base64.b64encode((os.environ['REGISTRY_USER'] + ':' + os.environ['REGISTRY_TOKEN']).encode()).decode()
    url = BASE + '/token?service=ghcr.io&scope=repository:' + REPOSITORY + ':pull'
    opener = urllib.request.build_opener(NoRedirects())
    with opener.open(urllib.request.Request(url, headers={'Authorization': 'Basic ' + credentials}), timeout=30) as response:
        token = json.load(response)['token']
    def request(url):
        req = urllib.request.Request(registry_url(url), headers={'Authorization': 'Bearer ' + token, 'Accept': ACCEPT})
        with opener.open(req, timeout=30) as response:
            raw = response.read(10 * 1024 * 1024 + 1)
            if len(raw) > 10 * 1024 * 1024:
                raise ValueError('Registry response exceeds review limit')
            return json.loads(raw), response.headers, raw
    result = inventory(request)
    print('REGISTRY_REVIEW_INVENTORY=' + json.dumps(result, sort_keys=True))
    with open(output, 'a') as stream:
        stream.write('review-needed=' + ('true' if result['images'] else 'false') + '\n')
        stream.write('matrix=' + json.dumps({'include': [dict(row, repository=REPOSITORY) for row in result['images']]}) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output')
    args = parser.parse_args()
    try:
        main(args.output)
    except urllib.error.HTTPError as exc:
        if exc.code not in (401, 403, 404):
            raise
        # GHCR can conceal private or absent packages with the same response.
        print('REGISTRY_REVIEW_UNAVAILABLE=' + json.dumps({'http_status': exc.code, 'repository': REPOSITORY, 'publication_cleared': False, 'absence_verified': False}))
        with open(args.output, 'w') as stream:
            stream.write('review-needed=false\nmatrix={"include":[]}\n')
