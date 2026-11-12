"""Turn raw venue downloads into common rows.

Row = dict(venue, year, id, title, abstract, track, decision, url, authors=[dict(name, affil)]).
*.cc sites (NeurIPS, ICML, ICLR): the poster list from /Downloads plus the orals-posters JSON for track and format.
ACL Anthology (ACL, EMNLP): the collection XML; only main-conference volumes are kept."""
import html
import re
import xml.etree.ElementTree as ET

from notable_inst import authors_with_affil

KEEP_TRACKS = frozenset({'Main', 'Evaluations & Datasets', 'Position', None})
ANTHOLOGY_VOLUMES = {'acl': ('long', 'short'), 'emnlp': ('main',)}


def _clean(s):
    return ' '.join(html.unescape(s or '').split())


def _pid(url):
    return url.rstrip('/').rsplit('/', 1)[-1]


def _decision(d):
    d = (d or '').lower()
    if 'oral' in d:
        return 'Oral'
    if 'spotlight' in d:
        return 'Spotlight'
    if 'poster' in d or 'regular' in d:
        return 'Poster'
    return None


def _track(src):
    s = (src or '').rstrip('/').rsplit('/', 1)[-1]
    low = s.lower()
    if s == 'Conference':
        return 'Main'
    if s == 'Evaluations_and_Datasets_Track':
        return 'Evaluations & Datasets'
    if s == 'Position_Paper_Track':
        return 'Position'
    if 'tmlr' in low or 'j2c' in low or 'journal' in low:
        return 'Journal'
    if s == 'BlogPosts':
        return 'Blog'
    if 'bridging-the-future' in low:
        return 'Bridging'
    return None


def parse_cc(posters, op, venue, year):
    if isinstance(op, dict):
        op = op.get('results', [])
    meta = {_pid(x['virtualsite_url']): x for x in op if x.get('eventtype') == 'Poster'}
    rows = []
    for x in posters:
        pid = _pid(x['virtualsite_url'])
        m = meta.get(pid, {})
        url = re.sub(r'^https?://[^/]+', lambda h: h.group(0).lower(), x['virtualsite_url'])
        rows.append(dict(venue=venue, year=year, id=f'{venue}{year}-{pid}', title=_clean(x['name']).replace('$', ''),
                         abstract=_clean(x.get('abstract')), track=_track(m.get('sourceurl')), decision=_decision(m.get('decision')),
                         url=url, authors=[dict(name=_clean(n), affil=_clean(a))
                                           for n, a in authors_with_affil(x.get('speakers/authors') or '')]))
    return rows


def _text(el):
    return ' '.join(''.join(el.itertext()).split()) if el is not None else ''


def parse_anthology(xml_text, venue, year):
    root = ET.fromstring(xml_text)
    coll = root.get('id')
    rows = []
    for vol in root.iter('volume'):
        if vol.get('id') not in ANTHOLOGY_VOLUMES[venue]:
            continue
        for p in vol.iter('paper'):
            aid = f"{coll}-{vol.get('id')}.{p.get('id')}"
            authors = [dict(name=' '.join(filter(None, [_text(a.find('first')), _text(a.find('last'))])),
                            affil=_text(a.find('affiliation'))) for a in p.findall('author')]
            rows.append(dict(venue=venue, year=year, id=aid, title=_text(p.find('title')), abstract=_text(p.find('abstract')),
                             track='Main', decision=None, url=f'https://aclanthology.org/{aid}/', authors=authors))
    return rows
