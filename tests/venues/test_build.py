from topic_trends import T
from venues.build import normalized_table, topic_hits, venue_payload


def row(id, affils, text):
    return dict(venue='acl', year=2026, id=id, title=text, abstract='', track='Main', decision=None,
                url=f'https://example.org/{id}', authors=[dict(name=f'a{i}', affil=a) for i, a in enumerate(affils)])


def test_topic_hits_case_insensitive():
    i = list(T).index('Medical / clinical')
    assert i in topic_hits('A CLINICAL benchmark')


def test_payload_counts_and_indices():
    rows = [row('p1', affils=['Google DeepMind', 'KAIST'], text='clinical agent'), row('p2', affils=['Google Research'], text='graph')]
    pl = venue_payload(rows, {})
    assert pl['n'] == 2 and pl['covered'] == 2
    google = [n for n, _ in pl['inst']].index('Google')
    assert google in pl['papers'][0][4] and google in pl['papers'][1][4]   # one shared index, counted once per paper


def test_payload_paper_without_affiliation():
    pl = venue_payload([row('p1', affils=['', ''], text='x')], {})
    assert pl['n'] == 1 and pl['covered'] == 0 and pl['papers'][0][4] == [] and pl['inst'] == []


def test_unnormalized_display_name():
    pl = venue_payload([row('p1', affils=['foo lab'], text='x')], {'foo lab': 'Foo Lab'})
    assert pl['inst'] == [['Foo Lab', False]]


def test_normalized_table_drops_abstract():
    t = normalized_table([row('p1', affils=['KAIST'], text='x')])
    assert 'abstract' not in t[0] and t[0]['inst'] == ['KAIST']


def test_missing_sets_reports_sets_without_raw_files():
    from venues.build import missing_sets
    previous = [{'venue': 'acl', 'year': 2025}, {'venue': 'icml', 'year': 2026}]
    assert missing_sets(previous, {('icml', 2026)}) == [('acl', 2025)]
    assert missing_sets(previous, {('icml', 2026), ('acl', 2025), ('emnlp', 2026)}) == []
