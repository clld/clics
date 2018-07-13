import re
from xml.etree import ElementTree as et
from collections import defaultdict

import requests

OAI_PMH_URL = "https://zenodo.org/oai2d?verb=ListRecords&set=user-clics&metadataPrefix=oai_dc"
ZENODO_DOI_PREFIX = '10.5281/'
TITLE_PATTERN = re.compile('lexibank/(?P<name>[a-z0-9]+):')


def read_oaipmh():
    doc = et.fromstring(requests.get(OAI_PMH_URL).text)

    for rec in doc.findall('.//{http://www.openarchives.org/OAI/2.0/}record'):
        meta = defaultdict(list)
        for e in rec.findall('.//{http://www.openarchives.org/OAI/2.0/oai_dc/}dc/*'):
            meta[e.tag.partition('}')[2]].append(e.text)
        yield meta


def iter_dois():
    for rec in read_oaipmh():
        m = TITLE_PATTERN.match(rec['title'][0])
        if m:
            for id_ in rec['identifier']:
                if id_.startswith(ZENODO_DOI_PREFIX):
                    yield 'lexibank-{0}'.format(m.group('name')), id_
                    break
