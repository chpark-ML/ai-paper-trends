import pytest

from venues.institutions import canon, paper_institutions, split_candidates


def names(s):
    return [n for n, _ in canon(s)]


@pytest.mark.parametrize('affil, expected', [
    ('Google DeepMind', ['Google']), ('Google Research', ['Google']),
    ('National University of Singapore, DeepMind', ['National University of Singapore', 'Google']),
    ('School of Computing, National University of Singapore', ['National University of Singapore']),
    ('national university of singaore, National University of Singapore', ['National University of Singapore']),
    ('CASIA', ['Chinese Academy of Sciences']),
    ('Institute of Automation, Chinese Academy of Sciences', ['Chinese Academy of Sciences']),
    ('University of Chinese Academy of Sciences', ['University of Chinese Academy of Sciences']),
    ('Qwen Team, Alibaba Group', ['Alibaba']), ('Ant Group', ['Ant Group']),
    ('Tsinghua Shenzhen International Graduate School', ['Tsinghua University']),
    ('Harbin Institute of Technology, Shenzhen', ['Harbin Institute of Technology']),
    ('UC San Diego', ['UC San Diego']), ('UCLA', ['UCLA']),
    ('Mass General Brigham', ['Mass General Brigham']), ('Harvard Medical School', ['Harvard University']),
    ('Seoul National University Hospital', ['Seoul National University Hospital']),
    ('Seoul National University', ['Seoul National University']),
    ('Meta FAIR', ['Meta']),
])
def test_canon_aliases(affil, expected):
    assert names(affil) == expected


@pytest.mark.parametrize('affil', ['MITRE Corporation', 'Brigham Young University', 'Lawrence Berkeley National Laboratory'])
def test_known_traps_not_merged(affil):   # must not yield MIT / Mass General Brigham / UC Berkeley
    assert not {'MIT', 'Mass General Brigham', 'UC Berkeley'} & set(names(affil))


def test_unmatched_kept_raw():
    assert canon('  Foo   Lab ') == [('Foo Lab', False)]


@pytest.mark.parametrize('affil', ['', 'Independent Researcher', 'Unaffiliated', 'N/A', 'None', '-'])
def test_junk_affiliations_dropped(affil):
    assert canon(affil) == []


def test_paper_institutions_union_once():
    au = [{'name': 'a', 'affil': 'Google DeepMind'}, {'name': 'b', 'affil': 'Google Research, KAIST'}, {'name': 'c', 'affil': ''}]
    assert paper_institutions(au) == [('Google', True), ('KAIST', True)]


def test_split_candidates():
    got = {frozenset(p) for p in split_candidates({'National University of Singapore': 10, 'national university of singapore': 5})}
    assert got == {frozenset({'National University of Singapore', 'national university of singapore'})}
    assert split_candidates({'Peking University': 10, 'Tsinghua University': 10}) == []


def test_uw_madison_is_not_washington():
    assert 'University of Washington' not in names('University of Wisconsin-Madison (UW-Madison)')
