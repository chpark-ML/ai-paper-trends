from venues.parse import parse_anthology, parse_cc


def P(id, title, authors='', host='neurips.cc'):
    return {'virtualsite_url': f'https://{host}/virtual/2026/poster/{id}', 'name': title, 'abstract': '',
            'speakers/authors': authors}


def O(id, decision, sourceurl, host='neurips.cc'):
    return {'virtualsite_url': f'https://{host}/virtual/2026/poster/{id}', 'eventtype': 'Poster',
            'decision': decision, 'sourceurl': sourceurl}


def test_cc_track_and_decision():
    posters = [P('1', 'A'), P('2', 'B'), P('3', 'C'), P('4', 'D'), P('5', 'E')]
    op = [O('1', 'Accept (spotlight poster)', '.../Conference'), O('2', 'Accept (regular)', '.../Evaluations_and_Datasets_Track'),
          O('3', 'Accept (Oral)', '.../Position_Paper_Track'), O('4', 'Accept (poster)', '.../2026-TMLR-J2C-Spreadsheet'),
          O('5', None, '.../BlogPosts')]
    rows = {r['id']: r for r in parse_cc(posters, op, 'icml', 2026)}
    assert (rows['icml2026-1']['track'], rows['icml2026-1']['decision']) == ('Main', 'Spotlight')
    assert (rows['icml2026-2']['track'], rows['icml2026-2']['decision']) == ('Evaluations & Datasets', 'Poster')
    assert (rows['icml2026-3']['track'], rows['icml2026-3']['decision']) == ('Position', 'Oral')
    assert rows['icml2026-4']['track'] == 'Journal' and rows['icml2026-5']['track'] == 'Blog'


def test_cc_missing_op_entry_gives_none():   # poster with no orals-posters match
    r = parse_cc([P('9', 'X')], [], 'iclr', 2025)[0]
    assert (r['track'], r['decision']) == (None, None)


def test_cc_authors_and_url():
    r = parse_cc([P('64869', 'T', authors='Ann Lee (Seoul National University), Bo Kim (Google DeepMind (London))', host='ICML.cc')],
                 [], 'icml', 2026)[0]
    assert r['authors'] == [{'name': 'Ann Lee', 'affil': 'Seoul National University'},
                            {'name': 'Bo Kim', 'affil': 'Google DeepMind (London)'}]
    assert (r['id'], r['url']) == ('icml2026-64869', 'https://icml.cc/virtual/2026/poster/64869')


def test_cc_unescapes_entities():
    r = parse_cc([P('1', 'Q&amp;A with $\\chi$-Bench', authors='Kun Zhang (CMU &amp; MBZUAI)')], [], 'neurips', 2026)[0]
    assert r['title'] == 'Q&A with \\chi-Bench'          # '$' removed, as explorer.py does
    assert r['authors'][0]['affil'] == 'CMU & MBZUAI'


XML_ACL = '''<collection id="2025.acl">
 <volume id="long"><paper id="1"><title><fixed-case>E</fixed-case>com Bench</title>
   <author><first>Wei</first><last>Wang</last><affiliation>Amazon</affiliation></author>
   <author><first>Li</first><last>Cui</last></author><abstract>A b.</abstract></paper>
  <paper id="2"><title>Two</title></paper></volume>
 <volume id="short"><paper id="1"><title>Short</title></paper></volume>
 <volume id="demo"><paper id="1"><title>Demo</title></paper></volume></collection>'''


def test_anthology_volumes_and_fields():
    rows = parse_anthology(XML_ACL, 'acl', 2025)
    assert [r['id'] for r in rows] == ['2025.acl-long.1', '2025.acl-long.2', '2025.acl-short.1']   # demo dropped
    assert rows[0]['title'] == 'Ecom Bench'
    assert rows[0]['authors'] == [{'name': 'Wei Wang', 'affil': 'Amazon'}, {'name': 'Li Cui', 'affil': ''}]
    assert rows[0]['url'] == 'https://aclanthology.org/2025.acl-long.1/'
    assert (rows[0]['track'], rows[0]['decision']) == ('Main', None)


def test_anthology_emnlp_uses_main_volume():
    xml = '<collection id="2026.emnlp"><volume id="main"><paper id="1"><title>M</title></paper></volume>' \
          '<volume id="industry"><paper id="1"><title>I</title></paper></volume></collection>'
    assert [r['id'] for r in parse_anthology(xml, 'emnlp', 2026)] == ['2026.emnlp-main.1']


def test_cc_track_variants_seen_in_2025_2026_data():
    srcs = {'1': 'https://openreview.net/group?id=NeurIPS.cc/2025/Datasets_and_Benchmarks_Track',
            '2': 'https://api.github.com/repos/JmlrOrg/v25',
            '3': 'journal-track/NeurIPS_2026-Posters_JMLR.xlsx',
            '4': 'https://projecteuclid.org/journals/annals-of-statistics/volume-53/issue-4',
            '5': 'ANN-STATS-2026',
            '6': 'https://imstat.org/journals-and-publications/annals-of-statistics/annals-of-statistics-future-papers/'}
    rows = {r['id']: r['track'] for r in parse_cc([P(k, k) for k in srcs], [O(k, 'Accept (poster)', s) for k, s in srcs.items()],
                                                  'neurips', 2025)}
    assert rows == {'neurips2025-1': 'Evaluations & Datasets', 'neurips2025-2': 'Journal', 'neurips2025-3': 'Journal',
                    'neurips2025-4': 'Journal', 'neurips2025-5': 'Journal', 'neurips2025-6': 'Journal'}
