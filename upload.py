import sys
import os
import string

from bs4 import BeautifulSoup
from internetarchive import get_item


def make_identifier(md):
    s = ''
    legal_chars = string.digits + string.ascii_letters + ' '
    for i, c in enumerate(md['title']):
        if c in legal_chars:
            s += c.lower()
    identifier = 'nslm-{}'.format(s.lower().replace(' ', '-').replace('--', '-'))
    return identifier


if __name__ == '__main__':
    soup = BeautifulSoup(open(sys.argv[-1]).read(), features='html.parser')
    md = dict(
            mediatype='texts',
            collection='national-sporting-library-and-museum-newsletters',
            language='eng',
        )
    pdf_path = None
    for l in soup.find_all('meta'):
        if not l.get('name'):
            continue

        if l['name'] == 'citation_pdf_url':
            pdf_path = l['content'].replace('https://', '')

        if not l['name'].startswith('DC'):
            continue

        if l['name'] == 'DC.creator':
            md['creator'] = l['content']
        elif l['name'] == 'DCTERMS.issued':
            md['date'] = l['content']
        elif l['name'] == 'DC.title':
            md['title'] = l['content']
        elif l['name'] == 'DC.publisher':
            md['publisher'] = l['content']
        elif l['name'] == 'DC.source':
            md['source'] = l['content']
        elif l['name'] == 'DC.contributor':
            md['contributor'] = l['content']
        elif l['name'] == 'DC.rights':
            md['rights'] = l['content']
        elif l['name'] == 'DC.subject':
            md['subject'] = l['content']
        elif l['name'] == 'DCTERMS.spatial':
            md['coverage'] = l['content']
        elif l['name'] == 'DC.identifier':
            md['external-identifier'] = 'urn:sporting-commons:{}'.format(
                    l['content'].replace('http://hdl.handle.net/', ''))

    if not pdf_path or not os.path.isfile(pdf_path):
        print('error: no PDF! - {}'.format(sys.argv[-1]))
        sys.exit(1)

    identifier = make_identifier(md)

    item = get_item(identifier)
    r = item.upload(pdf_path, md, checksum=True, retries=300)
    if not r[0].status_code == 200:
        print('error: failed to upload - {}'.format(item.identifier))
        sys.exit(1)
    print('success: {}'.format(item.identifier))
