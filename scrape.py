import os
from urllib.parse import parse_qs

from bs4 import BeautifulSoup
import requests


def get_next_page_params(soup):
    next_page_str = soup.select('.next-page-link')
    try:
        next_page_str = next_page_str[0]['href'].split('?')[1]
    except IndexError:
        return
    p = dict()
    for key, val in parse_qs(next_page_str).items():
        p[key] = val[0]
    return p


def get_links(soup):
    links = list()
    for l in soup.find_all('a'):
        if not l.get('href'):
            continue
        if not l['href'].startswith('/handle/'):
            continue
        links.append(l['href'])
    return set(links)


def get_soup(url, params):
    r = requests.get(url, params=params)
    return BeautifulSoup(r.text, features="html.parser")


def get_all_links():
    url = 'https://commons.nationalsporting.org/browse'
    p = dict(
            rpp='100',
            sort_by='1',
            type='title',
            etal='-1',
            starts_with='0',
            order='ASC',
        )
    all_links = set()
    while True:
        print('getting links... {}'.format(str(p)))
        soup = get_soup(url, p)
        links = get_links(soup)
        all_links.update(links)
        p = get_next_page_params(soup)
        if not p:
            break
    with open('all-links.txt', 'w') as fh:
        for l in all_links:
            fh.write('{}\n'.format(l))
    return all_links


def download_item_html(url):
    pass


if __name__ == '__main__':
    if not os.path.isfile('all-links.txt'):
        get_all_links()

    # download HTML: parallel wget -x 'https://commons.nationalsporting.org{}' :::: all-links.txt
    # get all PDF links: find commons.nationalsporting.org -type f -exec grep 'citation_pdf_url' '{}' \; | cut -d\" -f2 > all-pdfs.txt
    # download PDFs: parallel --joblog download-pdfs.log wget -x :::: all-pdfs.txt
