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


# Task 5: spellings and traps seen in the 2025–2026 data (raw strings copied from the build output)
@pytest.mark.parametrize('affil, expected', [
    ('Facebook', ['Meta']), ('Facebook AI Research', ['Meta']),
    ('Institute of automation, Chinese academy of science', ['Chinese Academy of Sciences']),
    ('Swiss Federal Institute of Technology', ['ETH Zurich']), ('Swiss Federal Institute of Technology Lausanne', ['EPFL']),
    ('Technical University Munich', ['TU Munich']),
    ('Huawei Technologies Ltd.', ['Huawei']), ("Huawei Noah's Ark Lab", ['Huawei']),
    ('University of Illinois at Urbana-Champaign', ['UIUC']), ('University of Illinois Urbana-Champaign', ['UIUC']),
    ('University of Illinois, Urbana Champaign', ['UIUC']), ('UIUC', ['UIUC']),
    ('University of Texas at Austin', ['UT Austin']), ('The University of Texas at Austin', ['UT Austin']),
    ('University of Texas, Austin', ['UT Austin']), ('UT Austin', ['UT Austin']),
    ('University of Wisconsin - Madison', ['University of Wisconsin-Madison']),
    ('University of Wisconsin, Madison', ['University of Wisconsin-Madison']),
    ('Nanjing University', ['Nanjing University']),
    ('Nanjing University of Science and Technology', ['Nanjing University of Science and Technology']),
    ('University of Science and Technology of China', ['USTC']),
    ('University of Electronic Science and Technology of China', ['UESTC']),
    ('Beijing University of Aeronautics and Astronautics', ['Beihang University']), ('Beihang University', ['Beihang University']),
    ('Beijing University of Post and Telecommunications', ['BUPT']),
    ('SUN YAT-SEN UNIVERSITY', ['Sun Yat-sen University']),
    ('Shanghai Artificial Intelligence Laboratory', ['Shanghai AI Lab']), ('Shanghai AI Lab', ['Shanghai AI Lab']),
    ('Mohamed bin Zayed University of Artificial Intelligence', ['MBZUAI']), ('MBZUAI', ['MBZUAI']),
    ('The Hong Kong Polytechnic University', ['Hong Kong Polytechnic University']),
    ('Kuaishou- 快手科技', ['Kuaishou']), ('Tiktok', ['ByteDance']), ('SalesForce.com', ['Salesforce']),
    ('International Business Machines', ['IBM']), ('Adobe Systems', ['Adobe']),
    ('Pohang University of Science and Technology', ['POSTECH']), ('Sung Kyun Kwan University', ['Sungkyunkwan University']),
    ('Technion - Israel Institute of Technology, Technion', ['Technion']),
    ('Eberhard-Karls-Universität Tübingen', ['University of Tübingen']),
    ('University of Montreal', ['Université de Montréal']),
    ('State University of New York at Stony Brook', ['Stony Brook University']),
])
def test_canon_aliases_from_data(affil, expected):
    assert names(affil) == expected


@pytest.mark.parametrize('affil, wrong', [
    ('Washington University, Saint Louis', 'University of Washington'),
    ('Northwestern Polytechnical University', 'Northwestern University'),
    ("Xi'an Jiaotong-Liverpool University", "Xi'an Jiaotong University"),
    ('University of Illinois Chicago', 'UIUC'),
    ('National Taiwan University', 'Nanyang Technological University'),
    ('University of Technology Sydney', 'University of Sydney'),
    ('University of Maryland, Baltimore County', 'University of Maryland'),
])
def test_known_traps_from_data(affil, wrong):
    assert wrong not in names(affil)


def test_shenzhen_university_after_department():
    assert names('College of Computer Science and Software Engineering, Shenzhen University') == ['Shenzhen University']


@pytest.mark.parametrize('affil, expected', [
    ('nanjing university', ['Nanjing University']),
    ('Adelaide University', ['University of Adelaide']), ('University of Adelaide', ['University of Adelaide']),
    ('University of Minnesota - Twin Cities', ['University of Minnesota']),
    ('TU Darmstadt', ['TU Darmstadt']), ('Technische Universität Darmstadt', ['TU Darmstadt']),
    ('ISTA', ['ISTA']), ('Institute of Science and Technology Austria', ['ISTA']),
])
def test_canon_aliases_round_two(affil, expected):
    assert names(affil) == expected


def test_unmatched_drops_leading_the():
    assert canon('The University of Queensland') == [('University of Queensland', False)]


@pytest.mark.parametrize('affil', ['Department of Computer Science', 'School of Computing', 'Computer Science Department'])
def test_department_only_is_junk(affil):
    assert canon(affil) == []


@pytest.mark.parametrize('affil, expected', [
    ('Xi’an Jiaotong University', ["Xi'an Jiaotong University"]), ('King’s College London', ["King's College London"]),
])
def test_curly_apostrophe(affil, expected):
    assert names(affil) == expected


@pytest.mark.parametrize('affil, expected', [
    ('ETH Zürich and Max Planck Institute for Intelligent Systems, Tübingen', ['ETH Zurich', 'Max Planck Society']),
    ('NEC Laboratories America, Princeton', ['NEC Laboratories America, Princeton']),
    ('Hongkong University of Science and Technology', ['HKUST']), ('HongKong University of Science and Technology', ['HKUST']),
    ('Universität of Tübingen & Ontic Labs', ['University of Tübingen']), ('Princeton University', ['Princeton University']),
])
def test_city_names_and_hongkong_spelling(affil, expected):
    assert names(affil) == expected


@pytest.mark.parametrize('affil, expected', [
    ('Tencent AI Platform Department', [('Tencent', True)]),
    ('Department of Computer Science in UIUC', [('UIUC', True)]),
    ('UCLA CS Department', [('UCLA', True)]),
    ('School of Computer Science of China University of Geosciences', [('School of Computer Science of China University of Geosciences', False)]),
    ('Department of Veterans Affairs', [('Department of Veterans Affairs', False)]),
    ('Electrical Engineering & Computer Science Department', []),
    ('Department of Computer Science and Engineering', []),
])
def test_department_rule_keeps_real_institutions(affil, expected):
    assert canon(affil) == expected
