#!/usr/bin/env python3

import pdb

import json
import re
import sys
import textwrap

import bs4
import html2text
import requests

def defn_url(word, ix = None, url_base = 'http://unabridged.merriam-webster.com/unabridged'):
    url = '/'.join([url_base, word])
    if ix is not None:
        url = '{}[{}]'.format(url, ix)
    return url

def get_soup(word, ix = None, url_login = 'https://unabridged.merriam-webster.com/subscriber/lapi/1/subscriber/identity/login/ue'):
    from secret import auth
    user, pw = auth()
    
    payload = {
        'email': user,
        'password': pw
    }

    with requests.Session() as sess:
        post = sess.post(url_login,
                         data=payload)
        url = defn_url(word, ix)
        r = sess.get(url)

    soup = bs4.BeautifulSoup(r.content,
                             features='lxml')
    return soup, url

def get_entries(word, soup):
    all_links = soup.select('#results-box-on-desktop li a')

    entries = []
    for entry in all_links:
        if re.search('{}(%.*)*$'.format(word), entry['href']) is None:
            continue
        label, blank, part_of_speech = entry.contents
        ix = label.text.replace(word, '')
        ix = 1 if ix == '' else int(ix)
        part_of_speech = re.sub('[()]', '', part_of_speech.text)
        entries.append((ix, part_of_speech))
    return entries

def split_examples(raw_entry):
    entry = raw_entry
    
    # ix = entry.index('<')
    # defn = entry[:ix-1].strip()
    # ex = re.sub('>$', '', entry[ix+1:-1].strip()).split('> <')
    
    defn = []
    ex = []
    while True:
        entry = entry.strip()
        if '<' not in entry:
            if entry != '':
                defn.append(entry)
            break
        ix1 = entry.index('<')
        if ix1 > 0:
            defn.append(entry[:ix1].strip())
            
        ix2 = entry.index('>')
        piece = entry[ix1+1:ix2]
        ex.append(piece)
        
        entry = entry[ix2+1:].strip()
        
    if len(ex) == 0:
        ex = None
        
    return((defn, ex))

def get_defn(soup):
    defn_body = soup.select_one('#mwEntryData .d')

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_emphasis = True
    h.body_width = 0

    all_defn = []
    blocks = defn_body.select('.sblk')
    if len(blocks) == 0:
        blocks = defn_body.select('.sense-block-one')
    for sense_body in blocks:
        sense = []
        for subsense in sense_body.select('.ssens'):
            entry = h.handle(str(subsense))
            defn, ex = split_examples(entry)
            sense.append({
                'definition': defn,
                'examples': ex
            })
        all_defn.append(sense)

    return all_defn

def print_defn(word, ix, entries, all_defn, url, tabstop = '  ', print_examples = False):
    outlines = ['']

    outlines.append('Entries:')
    for i, entry in entries:
        outlines.append('{indent}{ix}. {word} ({entry})'.format(indent=tabstop,
                                                                ix=i,
                                                                word=word,
                                                                entry=entry))
            
    outlines.append('\n - {} (entry {}) - \n'.format(word.upper(), ix))
    
    outlines.append('More at {}\n'.format(url))

    for i, defn in enumerate(all_defn):
        outlines.append('')
        x = '{}.'.format(i+1)
        outlines.append(x)
        for d in defn:
            for subdefn in d['definition']:
                x = textwrap.fill(subdefn,
                                  initial_indent=tabstop,
                                  subsequent_indent=2*tabstop)
                outlines.append(x)
                
            if d['examples'] is not None:
                x = '\n{}'.format(textwrap.fill('Examples:',
                                                initial_indent=tabstop))
                outlines.append(x)
                for ex in d['examples']:
                    x = textwrap.fill(ex,
                                      initial_indent=2*tabstop,
                                      subsequent_indent=3*tabstop)
                    outlines.append(x)
                outlines.append('')
    
    outlines.append('\nMore at {}'.format(url))
    out = '\n'.join(outlines)
    print(out)
    return out

def main(word, ix=None):
    if ix is None:
        soup, url = get_soup(word)
        ix = 1
    else:
        soup, url = get_soup(word, ix)
    entries = get_entries(word, soup)
    all_defn = get_defn(soup)

    txt = print_defn(word, ix, entries, all_defn, url)

if __name__ == '__main__':
    word = sys.argv[1]
    if len(sys.argv) > 2:
        ix = int(sys.argv[2])
        main(word, ix)
    else:
        main(word)
