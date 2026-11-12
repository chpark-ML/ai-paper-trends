# 학회 확장 연구 동향 추적 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** NeurIPS·ICML·ICLR·ACL·EMNLP 2025–2026 main 논문을 한 표로 모으고, 키워드를 고르면 학회·연도별 편수와 기관 순위를 보여 주는 `trends.html`을 만든 뒤, 저장소 이름을 `ai-paper-trends`로 바꾼다.

**Architecture:** `scripts/venues/` 아래에 받기(`fetch.py`), 원본 → 공통 행 변환(`parse.py`), 기관 정규화(`institutions.py`), 집계·출력(`build.py`)을 둔다. 출력은 학회·연도별 JSON(`data/venues/`는 감사용 정규화 표, `trends/`는 페이지 데이터)이다. `trends.html`은 손으로 쓴 정적 페이지로, 필요한 학회·연도 JSON만 `fetch()`로 불러온다. 기존 다섯 페이지와 그 데이터는 건드리지 않는다.

**Tech Stack:** Python 3.9.6 표준 라이브러리만 사용(스크립트), pytest 8.4.2(테스트), 정적 HTML/CSS/JS(GitHub Pages), `gh` CLI(이름 변경).

**Spec:** `docs/superpowers/specs/2026-11-12-multi-venue-trends-design.md`

## Global Constraints

- 파이썬은 시스템 `python3`(3.9.6)다. `match` 문과 실행 시점의 `X | Y` 타입을 쓰지 않는다. 타입 힌트가 필요하면 `from __future__ import annotations`를 쓴다. 스크립트에 새 의존성을 넣지 않는다.
- 학회 키: `neurips`, `icml`, `iclr`은 `*.cc` 사이트, `acl`, `emnlp`는 ACL Anthology. 연도는 2025, 2026이다.
- **남기는 트랙**: `Main`, `Evaluations & Datasets`, `Position`, 그리고 정보 없음(`None`). **빼는 트랙**: `Journal`(orals-posters `sourceurl`에 `TMLR`·`J2C`·`journal`이 들어감, 대소문자 무시), `Blog`(`BlogPosts`), `Bridging`(`bridging-the-future`). 스펙 §6.1 "main 논문"을 적용한 결과다. TMLR 등 저널 발표와 블로그 트랙은 그 학회 자체의 논문이 아니다.
- ACL은 Anthology volume `long`과 `short`, EMNLP는 `main`만 쓴다. 둘 다 트랙은 `Main`이다.
- 키워드 주제는 `scripts/topic_trends.py`의 `T`(58개)다. 각 정규식을 `re.I`로 `제목 + ' ' + 초록`에 적용한다. 기존 `topic_trends.py`와 같은 방식이다.
- 키워드를 여러 개 고르면 기본은 AND이고, OR 토글을 둔다.
- 논문 → 기관은 모든 저자의 정규화된 기관 합집합이다. 한 논문은 한 기관에 한 번만 센다.
- 별칭이 걸리지 않은 소속은 공백을 정리한 원문 그대로 두고 `normalized=False`로 표시한다. 같은 원문은 대소문자를 무시하고 하나로 묶으며, 표시 이름은 가장 많이 나온 표기다.
- 기관 단위 규칙은 스펙 §6.3 표를 그대로 따른다. 요약하면 다음과 같다.
  - 기업 연구조직은 모회사로 합친다. 별도 법인 기업은 따로 센다.
  - 분교는 본교로 합친다. 독립 대학인 UC 캠퍼스들은 각각 따로 센다.
  - 병원은 대학과 따로 센다.
  - CAS 산하 연구소는 CAS로 합친다. UCAS는 CAS와 따로 센다.
- 바뀌면 안 되는 기존 파일:
  - `interests.html`, `explorer.html`, `medical_qa.html`, `opsd.html`, `med_datasets.html`
  - `HIGHLIGHTS.md`
  - `data/` 아래 기존 파일 전부
  - `scripts/notable_inst.py`
  - `scripts/topic_trends.py`. 단, 키워드를 추가하는 경우는 예외다.
- UI는 한국어다. `scripts/explorer_template.html`의 `:root` 색 토큰, 다크 모드 블록, 글꼴을 그대로 쓴다. 휴대폰 너비에서 좌우 여백 16px, 가로 스크롤 없음.
- 새 주소는 `https://chpark-ml.github.io/ai-paper-trends`, 새 저장소는 `chpark-ML/ai-paper-trends`다.
- 브랜치는 `feat-multi-venue-trends`다. 커밋 제목은 동사로 시작한다. AI 표기(`Co-Authored-By` 등)는 넣지 않는다.
- 내려받은 원본은 `data/raw/venues/`(이미 `.gitignore`의 `data/raw/`에 포함)에만 둔다. 원본을 읽는 테스트 밖 실행은 `python3 -I`로 한다.
- `python3 -I`는 스크립트 폴더를 `sys.path`에 넣지 않는다. 그래서 `scripts/venues/`의 CLI(`fetch.py`, `build.py`)는 맨 위에서 `sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))`로 `scripts/`를 넣는다. 그런 다음 `venues.parse`, `venues.institutions`, `notable_inst`, `topic_trends`를 import한다(`explorer.py`와 같은 방식). 테스트는 `tests/conftest.py`가 같은 경로를 넣는다.

## Review Focus

1. **원본의 HTML 엔티티**: `*.cc` 저자 문자열에 `CMU &amp; MBZUAI` 같은 엔티티가 있다(`data/papers.json`에서 확인). 제목·이름·소속은 `&`로 풀려서 나와야 한다. → Task 1 `test_cc_unescapes_entities`.
2. **기관이 아닌 소속값**: `Independent Researcher`, `Unaffiliated`, `N/A`, `None`, `-` 같은 값이 기관 순위에 오르면 안 된다. → Task 2 `test_junk_affiliations_dropped`.
3. **소속이 하나도 없는 논문**(ACL·EMNLP에 1–3%): 키워드 편수와 학회 전체 편수에는 들어가야 한다. 소속 확보율에서는 "없음"으로 세고, 빈 이름의 기관으로 나타나면 안 된다. → Task 4 `test_payload_paper_without_affiliation`.
4. **자유 검색에 정규식 특수문자**(`C++`, `(`, `[`) 입력: 페이지가 예외 없이 문자 그대로 찾아야 한다. → Task 6 Step 4 확인 항목.
5. **결과가 0편이거나 학회·연도 파일을 못 불러온 경우**: 빈 화면이 아니라 이유를 말하는 문장이 보여야 한다. → Task 6 Step 4 확인 항목.

---

### Task 0: 브랜치와 문서 커밋

- [ ] **Step 1:** `git switch -c feat-multi-venue-trends`
- [ ] **Step 2:** 스펙과 이 계획을 커밋한다.

```bash
git add docs/superpowers/specs/2026-11-12-multi-venue-trends-design.md docs/superpowers/plans/2026-11-12-multi-venue-trends.md
git commit -m "Add design and plan for multi-venue keyword→institution trends"
```

---

### Task 1: 원본 → 공통 행 변환 (`parse.py`)

**Files:**
- Create: `scripts/venues/__init__.py` (빈 파일), `scripts/venues/parse.py`
- Create: `tests/conftest.py` (`scripts/`를 `sys.path` 앞에 넣는다), `tests/venues/test_parse.py`

**Interfaces:**
- Consumes: `scripts/notable_inst.py`의 `authors_with_affil(s: str) -> list[tuple[str, str]]`
- Produces:
  - `Row` = `dict(venue: str, year: int, id: str, title: str, abstract: str, track: str|None, decision: str|None, url: str, authors: list[dict(name: str, affil: str)])`
  - `parse_cc(posters: list[dict], op: list[dict], venue: str, year: int) -> list[Row]`: 트랙을 거르지 않는다. 모든 행에 트랙 라벨을 붙인다.
  - `parse_anthology(xml_text: str, venue: str, year: int) -> list[Row]`
  - `KEEP_TRACKS: frozenset = frozenset({'Main', 'Evaluations & Datasets', 'Position', None})`

- [ ] **Step 1: 실패하는 테스트를 쓴다** (`tests/venues/test_parse.py`). 픽스처는 테스트 안의 작은 dict와 XML 문자열이다.

```python
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
```

`P(id, title, authors='', host='neurips.cc')`와 `O(id, decision, sourceurl)`은 테스트 파일 안의 작은 생성 함수다.
- `P`는 `virtualsite_url=f'https://{host}/virtual/2026/poster/{id}'`, `name`, `abstract=''`, `speakers/authors`를 채운다.
- `O`는 같은 `virtualsite_url`에 `eventtype='Poster'`, `decision`, `sourceurl`을 채운다.

- [ ] **Step 2:** `python3 -m pytest tests/venues/test_parse.py -q`를 돌려 실패를 확인한다. 예상: `ModuleNotFoundError: venues.parse`.
- [ ] **Step 3:** `scripts/venues/parse.py`를 구현한다.
  - `*.cc`는 `op` 중 `eventtype == 'Poster'`인 항목을 `virtualsite_url`의 마지막 경로 조각(id)으로 잇는다. Task 3의 실측에서 ICML·ICLR 포스터 id는 100% 겹쳤다.
  - 발표 형식은 소문자로 바꿔 판정한다. `oral` 포함 → `Oral`, `spotlight` 포함 → `Spotlight`, `poster`·`regular` 포함 → `Poster`, 그 밖(`accept` 단독, `None`) → `None`.
  - 트랙은 `sourceurl`을 보고 Global Constraints의 규칙대로 정한다.
  - 제목·이름·소속에 `html.unescape`를 적용하고 공백을 하나로 접는다.
  - Anthology는 `xml.etree.ElementTree`로 읽는다. 제목·초록은 `''.join(el.itertext())`로 평문화한다. 이름은 `first + ' ' + last`다.
- [ ] **Step 4:** `python3 -m pytest tests/venues/test_parse.py -q`를 돌린다. 예상: 전부 PASS.
- [ ] **Step 5:** 커밋한다. `git add scripts/venues tests && git commit -m "Add venue parsers for *.cc poster lists and ACL Anthology XML"`

---

### Task 2: 기관 정규화 (`institutions.py`)

**Files:**
- Create: `scripts/venues/institutions.py`, `tests/venues/test_institutions.py`

**Interfaces:**
- Consumes: `Row['authors']` (Task 1)
- Produces:
  - `ALIASES: list[tuple[str, str]]`: (대표 이름, 정규식). 기본은 대소문자를 구분한다. 필요한 항목만 `(?i)`를 쓴다.
  - `canon(affil: str) -> list[tuple[str, bool]]`: 걸린 대표 이름 전부를 `(이름, True)`로 돌려준다. 하나도 안 걸리면 `[(정리된 원문, False)]`, 빈 값이나 기관이 아닌 값이면 `[]`이다.
  - `paper_institutions(authors: list[dict]) -> list[tuple[str, bool]]`: 처음 나온 순서를 지키는 합집합이다.
  - `split_candidates(counts: dict[str, int], top: int = 100) -> list[tuple[str, str]]`: 상위 `top`개 안에서 갈라졌을 가능성이 있는 쌍을 돌려준다.

- [ ] **Step 1: 실패하는 테스트를 쓴다.** 아래 값이 스펙 §5·§6.3에서 온 고정 기대값이다. `names(s)`는 `[n for n, _ in canon(s)]`이다.

```python
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
def test_canon_aliases(affil, expected): assert names(affil) == expected

@pytest.mark.parametrize('affil', ['MITRE Corporation', 'Brigham Young University', 'Lawrence Berkeley National Laboratory'])
def test_known_traps_not_merged(affil):   # must not yield MIT / Mass General Brigham / UC Berkeley
    assert not {'MIT', 'Mass General Brigham', 'UC Berkeley'} & set(names(affil))

def test_unmatched_kept_raw(): assert canon('  Foo   Lab ') == [('Foo Lab', False)]

@pytest.mark.parametrize('affil', ['', 'Independent Researcher', 'Unaffiliated', 'N/A', 'None', '-'])
def test_junk_affiliations_dropped(affil): assert canon(affil) == []

def test_paper_institutions_union_once():
    au = [{'name': 'a', 'affil': 'Google DeepMind'}, {'name': 'b', 'affil': 'Google Research, KAIST'}, {'name': 'c', 'affil': ''}]
    assert paper_institutions(au) == [('Google', True), ('KAIST', True)]

def test_split_candidates():
    got = {frozenset(p) for p in split_candidates({'National University of Singapore': 10, 'national university of singapore': 5})}
    assert got == {frozenset({'National University of Singapore', 'national university of singapore'})}
    assert split_candidates({'Peking University': 10, 'Tsinghua University': 10}) == []
```

- [ ] **Step 2:** `python3 -m pytest tests/venues/test_institutions.py -q`를 돌려 실패를 확인한다.
- [ ] **Step 3:** `scripts/venues/institutions.py`를 구현한다.
  - 시작점은 `scripts/notable_inst.py`의 `INST` 68개 패턴을 복사한 것이다. `notable_inst.py`는 고치지 않는다.
  - 대표 이름은 §6.3 규칙에 맞게 정한다. 예: `Google / DeepMind` → `Google`.
  - 복사한 패턴 중 위 함정에 걸리는 것을 고친다. `Brigham`은 Brigham Young에, `Berkeley`는 Lawrence Berkeley에 걸린다.
  - CAS는 `University of Chinese Academy of Sciences`에 걸리지 않게 lookbehind로 막는다.
  - 기관이 아닌 값은 집합으로 둔다(대소문자 무시, 끝의 마침표 무시).
  - `split_candidates`의 키는 소문자화 → 구두점 제거 → 오타 하나 허용(편집거리 ≤ 2) 또는 토큰 집합 포함 관계다. 경고 전용이라 거짓 양성은 괜찮다. 자동으로 합치지 않는다.
- [ ] **Step 4:** `python3 -m pytest tests/venues -q`를 돌린다. 예상: 전부 PASS.
- [ ] **Step 5:** 커밋한다. `git add scripts/venues/institutions.py tests/venues/test_institutions.py && git commit -m "Add institution alias table and normalization"`

---

### Task 3: 원본 받기 (`fetch.py`)

네트워크 작업이라 단위 테스트를 쓰지 않고, 실제로 받은 편수로 확인한다.

**Files:**
- Create: `scripts/venues/fetch.py`

**Interfaces:**
- Produces:
  - CLI `python3 scripts/venues/fetch.py <venue> <year>`
  - `*.cc` 학회는 `data/raw/venues/{venue}{year}_posters.json`과 `data/raw/venues/{venue}{year}_op.json`을 쓴다.
  - `acl`·`emnlp`는 `data/raw/venues/{venue}{year}.xml`을 쓴다.

- [ ] **Step 1:** `fetch.py`를 구현한다. 표준 라이브러리 `urllib.request`와 `http.cookiejar`만 쓴다.
  - `*.cc`는 `scripts/fetch.sh`의 순서를 그대로 따른다.
    1. 같은 User-Agent로 `GET https://{host}/Downloads/{year}`를 보내 `csrfmiddlewaretoken`을 얻는다.
    2. `POST` 본문 `format=5&posters=on&resource=0&submitaction=Download+Data`(Referer 포함)로 포스터 목록을 받는다.
    3. `https://{host}/static/virtual/data/{venue}-{year}-orals-posters.json`을 받는다.
  - `CC = {'neurips': 'neurips.cc', 'icml': 'icml.cc', 'iclr': 'iclr.cc'}`.
  - Anthology는 `https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/{year}.{venue}.xml`에서 받는다.
  - 타임아웃은 600초다. 2026-11-12 실측으로 ICLR 한 해 다운로드에 1분 이상 걸렸다.
  - orals-posters가 200이 아니면 그 파일은 쓰지 않고 경고만 출력한다. 이 경우 Task 4에서 트랙·발표 형식이 `None`이 된다.
  - 받은 파일이 JSON·XML로 파싱되지 않으면 non-zero로 종료한다.
  - 저장한 뒤 Task 1의 `parse_cc`·`parse_anthology`로 변환해 `{venue} {year}: {N} papers (op: {M} entries|missing)`를 출력한다. 트랙으로 거르기 전 편수다.
- [ ] **Step 2:** 열 개 조합을 모두 받는다.

```bash
for v in neurips icml iclr acl emnlp; do for y in 2025 2026; do python3 -I scripts/venues/fetch.py $v $y || echo "FAIL $v $y"; done; done
```

예상: `FAIL` 줄이 없다.
- [ ] **Step 3:** Step 2가 출력한 `{N} papers`가 스펙 §5와 맞는지 보고 기록한다.
  - 기대값은 트랙으로 거르기 전 기준이다. ICML 3,339 / 6,628, ICLR 3,826 / 5,466, ACL 1,699 / 2,296, EMNLP 1,809 / 2,704. NeurIPS는 10월 스냅샷 기준 5,860 / 9,094였다.
  - 다르면 다시 받은 수를 기준으로 삼고, 차이를 PR 본문에 적는다(스펙 §5).
- [ ] **Step 4:** 커밋한다. `git add scripts/venues/fetch.py && git commit -m "Add venue fetcher for *.cc sites and ACL Anthology"`

---

### Task 4: 집계와 출력 (`build.py`)

**Files:**
- Create: `scripts/venues/build.py`, `tests/venues/test_build.py`
- Output (커밋 대상):
  - `data/venues/{venue}{year}.json`: 감사용 정규화 표.
  - `trends/{venue}{year}.json`, `trends/index.json`: 페이지 데이터.

**Interfaces:**
- Consumes: `parse_cc`, `parse_anthology`, `KEEP_TRACKS` (Task 1). `canon`, `paper_institutions`, `split_candidates` (Task 2). `topic_trends.T`.
- Produces:
  - `topic_hits(text: str) -> list[int]`: `list(T)` 순서의 인덱스.
  - `venue_payload(rows: list[Row], display: dict[str, str]) -> dict`
    - 반환값은 `{"venue", "year", "n", "covered", "inst": [[이름, normalized]], "papers": [[제목, url, 트랙, 발표형식, [inst 인덱스], [topic 인덱스]]]}`.
    - `display`는 정규화 안 된 이름의 소문자 키 → 표시 이름이다.
    - `covered`는 기관을 하나 이상 얻은 논문 수다.
  - `normalized_table(rows: list[Row]) -> list[dict]`: Row에서 `abstract`를 빼고 `"inst": [이름]`을 더한 것이다. 초록은 커밋하지 않는다(스펙 §6.5).
  - CLI `python3 scripts/venues/build.py`:
    1. `data/raw/venues/`에 있는 조합을 모두 처리한다.
    2. `KEEP_TRACKS`로 거른다.
    3. 정규화 안 된 이름의 표시 이름은 전체 조합을 한 번 훑어 정한다.
    4. 파일을 쓴다.
    5. 아래를 출력한다.
       - 조합별 트랙 편수와 뺀 편수.
       - 전체 기관 순위와 조합별 상위 50위.
       - `split_candidates` 경고.
       - `trends/` 총 용량.

- [ ] **Step 1: 실패하는 테스트를 쓴다** (`tests/venues/test_build.py`).

```python
def test_topic_hits_case_insensitive():
    i = list(T).index('Medical / clinical'); assert i in topic_hits('A CLINICAL benchmark')

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
```

`row(id, affils, text)`는 테스트 안의 생성 함수다. `title=text`, `abstract=''`, 저자 한 명당 소속 하나인 Row를 만든다.

- [ ] **Step 2:** `python3 -m pytest tests/venues/test_build.py -q`를 돌려 실패를 확인한다.
- [ ] **Step 3:** `scripts/venues/build.py`를 위 인터페이스대로 구현한다. JSON은 `ensure_ascii=False, separators=(',', ':')`로 쓴다(`explorer.py`와 같은 방식). `trends/index.json`은 `{"topics": list(T), "sets": [{"venue", "year", "n", "covered", "file"}], "built": "YYYY-MM-DD"}`이다.
- [ ] **Step 4:** `python3 -m pytest tests/venues -q`를 돌린다. 예상: 전부 PASS.
- [ ] **Step 5:** 실제 데이터로 `python3 -I scripts/venues/build.py`를 실행한다.
  - 예상: `trends/` 아래에 10개 조합 파일과 `index.json`이 생긴다.
  - 총 용량이 10MB를 넘으면 페이지 데이터를 줄인다. 예: 트랙·발표 형식 문자열을 인덱스로 바꾼다.
  - 출력된 조합별 남긴 편수와 뺀 트랙 편수를 PR 본문용으로 기록한다.
- [ ] **Step 6: NeurIPS 2026 `Medical / clinical` 확인 (스펙 §8).**
  - 아래 두 수가 같아야 한다.
    - `trends/neurips2026.json`에서 그 주제 인덱스를 가진 논문 수.
    - `re.compile(T['Medical / clinical'], re.I)`를 새 원본의 남긴 트랙 논문 `name + ' ' + abstract`에 직접 돌린 수.
  - 10월 집계 438편(`data/topic_trends.json`)과의 차이를 기록한다. 10월 집계는 트랙으로 거르지 않았으므로 차이가 날 수 있다.
- [ ] **Step 7:** 커밋한다. `git add scripts/venues/build.py tests/venues/test_build.py data/venues trends && git commit -m "Build normalized venue tables and trends page data"`

---

### Task 5: 별칭 표를 실제 데이터에 맞추기

이 작업의 결과물은 상위 기관 목록에 갈라짐과 잘못 합쳐짐이 없는 별칭 표다.

**Files:**
- Modify: `scripts/venues/institutions.py`, `tests/venues/test_institutions.py`
- Regenerate: `data/venues/*`, `trends/*`

- [ ] **Step 1:** Task 4 Step 5 출력을 본다.
  - 전체 순위와 조합별 상위 50위를 본다.
  - `split_candidates` 경고와 정규화 안 된 상위 이름을 본다.
  - 같은 기관이 둘로 갈라진 것, §6.3 규칙과 다르게 합쳐지거나 갈라진 것을 목록으로 만든다.
- [ ] **Step 2:** 찾은 것마다 `test_canon_aliases`나 `test_known_traps_not_merged`에 원문 소속 한 줄을 추가한다. 실패를 확인한다(`python3 -m pytest tests/venues/test_institutions.py -q`).
- [ ] **Step 3:** `ALIASES`를 고친다. 다시 `python3 -m pytest tests/venues -q`(PASS), `python3 -I scripts/venues/build.py`를 돌린다.
- [ ] **Step 4:** Step 1–3을 반복한다. 끝나는 조건은 필터 없는 상위 50위(전체와 10개 조합 각각)에 갈라짐·잘못 합쳐짐이 없는 것이다. 마지막 상위 50위 목록은 PR 본문에 붙인다.
- [ ] **Step 5:** 무작위 20편을 검사한다. `random.seed(0)`으로 `data/venues/*.json` 전체에서 20편을 뽑는다. 각 논문의 저자 소속 원문과 `inst`를 나란히 출력해 눈으로 맞춘다. 틀린 것은 Step 2부터 다시 한다.
- [ ] **Step 6:** 커밋한다. `git add scripts/venues/institutions.py tests/venues/test_institutions.py data/venues trends && git commit -m "Extend institution aliases until the top-50 rankings have no splits"`

---

### Task 6: 동향 페이지 (`trends.html`)

**Files:**
- Create: `trends.html` (저장소 루트, 손으로 쓴 정적 파일, 빌드가 덮어쓰지 않음)

**Interfaces:**
- Consumes: `trends/index.json`, `trends/{venue}{year}.json` (Task 4 형식)

- [ ] **Step 1:** 페이지를 만든다.
  - 머리말은 `explorer_template.html`의 `<head>`(글꼴, `:root` 토큰, 다크 모드 블록)를 복사한다.
  - `<title>`은 `학회 연구 동향`이다.
  - 상단 nav에 기존 다섯 페이지 상대 링크를 둔다.
  - 구성은 스펙 §6.4 순서를 따른다.
    1. **필터**
       - 학회·연도 체크박스: `index.json`의 `sets`로 만든다. 기본은 전부 선택이다.
       - 키워드 주제: 58개 중 여러 개를 고른다. AND/OR 토글을 두고 기본은 AND다.
       - 자유 검색: 제목과 기관 이름을 대상으로 하고 대소문자를 무시하는 부분 문자열 검색이다. `RegExp`를 쓰지 않는다.
    2. **동향 표**: 학회 × 연도별 해당 편수와 그 조합 전체(`n`) 대비 %.
    3. **기관 순위**: 상위 50개를 보여 주고 "더 보기"를 둔다. 행마다 총 편수와 조합별 편수를 보인다. 정규화 안 된 이름에는 표시를 단다. 행을 누르면 그 기관의 해당 논문 목록이 펼쳐진다(제목 링크, 학회·연도, 트랙·발표 형식, 다른 기관).
    4. **소속 확보율**: 선택한 조합마다 `covered / n`.
  - 데이터는 선택된 조합만 `fetch()`로 불러오고 메모리에 캐시한다.
  - 필터 상태는 URL 해시에 넣는다. 예: `#k=12,40&op=and&v=acl2026`. 이렇게 하면 링크로 공유할 수 있다.
- [ ] **Step 2:** 로컬에서 띄운다. `python3 -m http.server 8765`를 실행하고 `http://localhost:8765/trends.html`을 연다.
- [ ] **Step 3:** 기능을 확인한다.
  - `Medical / clinical`만 고르고 NeurIPS 2026만 남기면 편수가 Task 4 Step 6의 수와 같다.
  - `Medical / clinical` + `LLM agents / agentic`의 AND 결과가 각 단독 결과보다 작거나 같다. OR로 바꾸면 크거나 같다.
  - 기관 행을 누르면 그 기관의 논문이 펼쳐진다. 펼친 논문 수가 순위의 숫자와 같다.
- [ ] **Step 4:** Review Focus 4·5를 확인한다.
  - 검색창에 `C++`, `(`, `[`를 넣어도 콘솔 오류가 없다.
  - 결과가 0편인 조합(예: 키워드 AND로 아무것도 없는 경우)에서 "조건에 맞는 논문이 없다"는 문장이 보인다.
  - 개발자 도구로 `trends/acl2025.json` 요청을 막고 다시 열면 "ACL 2025 데이터를 불러오지 못했다"는 문장이 보인다.
- [ ] **Step 5:** 휴대폰 너비를 확인한다. 창 너비 390px에서 `document.documentElement.scrollWidth <= document.documentElement.clientWidth`가 `true`이고, 좌우 여백이 16px이다.
- [ ] **Step 6:** 커밋한다. `git add trends.html && git commit -m "Add trends page: keyword → venue trend and institution ranking"`

---

### Task 7: README·REPORT 생성 스크립트와 새 주소

**Files:**
- Modify: `scripts/build.py`
  - 주소: `https://chpark-ml.github.io/neurips2026-medical-llm-rag`가 나오는 모든 줄(2026-11-12 기준 91·279·282·284·288행 부근).
  - README 생성부: 296–341행.
- Regenerate: `README.md`, `REPORT.md`

- [ ] **Step 1: 사전 확인 (스펙 §6.7).**
  - 고치지 않은 상태로 `python3 scripts/build.py`를 돌리고 `git status --short`를 본다.
  - 예상: 출력이 비어 있다.
  - 비어 있지 않으면 **멈추고 사용자에게 보고한다**. 이 스크립트는 `interests.html`, `HIGHLIGHTS.md`, `data/papers.csv`도 다시 쓴다. 바뀐 파일은 `git restore`로 되돌린다.
- [ ] **Step 2:** `scripts/build.py`에서 옛 주소 문자열을 전부 `https://chpark-ml.github.io/ai-paper-trends`로 바꾼다.
- [ ] **Step 3:** README 생성부를 고친다.
  - 제목: `# AI 학회 논문 동향 — NeurIPS·ICML·ICLR·ACL·EMNLP`
  - 첫 문단: 두 문장으로 쓴다. 하나는 다섯 학회 키워드·기관 동향 페이지, 하나는 기존 NeurIPS 2026 의료·RAG 정리를 소개한다.
  - 웹 페이지 표 맨 위에 새 줄을 추가한다. `| [학회 연구 동향]({BASE}/trends.html) | 다섯 학회 2025–2026 main 논문에서 키워드별 학회·연도 편수와 기관 순위 |`. 편수 같은 변하는 숫자는 넣지 않는다.
  - "다섯 페이지는 서로 독립적이다"를 "여섯 페이지는 서로 독립적이다"로 바꾼다.
  - 파일 표에 새 줄을 추가한다.
    - `trends.html`, `trends/`: 동향 페이지와 그 데이터.
    - `data/venues/`: 학회·연도별 정규화 표.
  - '재현' 코드 블록에 새 명령 두 줄을 추가한다.
    - `for v in neurips icml iclr acl emnlp; do for y in 2025 2026; do python3 scripts/venues/fetch.py $v $y; done; done`
    - `python3 scripts/venues/build.py`
  - 그 밖의 줄(숫자로 보기, 주요 관찰 등 NeurIPS 2026 내용)은 그대로 둔다.
- [ ] **Step 4:** `python3 scripts/build.py`를 다시 돌린 뒤 `git status --short`를 본다.
  - 예상: 바뀐 기존 파일은 `scripts/build.py`, `README.md`, `REPORT.md`뿐이다.
  - `git diff REPORT.md`에는 주소만 바뀌어 있다.
- [ ] **Step 5:** `grep -rn "neurips2026-medical-llm-rag" --exclude-dir=.git .`을 돌린다. 예상: `scripts/medqa_bench/`의 User-Agent 4줄과 `docs/superpowers/` 문서만 나온다.
- [ ] **Step 6:** 커밋한다. `git add scripts/build.py README.md REPORT.md && git commit -m "Point README and REPORT at the renamed site and list the trends page"`
- [ ] **Step 7:** PR을 연다(`harness-core:pr-create`).
  - 제목은 `[feat-multi-venue-trends] Add five-venue keyword→institution trends page`다.
  - 본문에 아래를 적는다.
    - Task 3 편수와 §5 표의 차이.
    - Task 4의 뺀 트랙 편수와 Medical / clinical 확인 결과.
    - Task 5의 최종 상위 50위.
    - 머지 직후 저장소 이름을 바꿀 예정이라는 것.
  - 머지는 사용자가 한다.

---

### Task 8: 저장소 이름 변경 (PR 머지 후)

- [ ] **Step 1:** 사용자에게 PR이 머지됐는지 확인하고, 지금 이름을 바꿔도 되는지 **한 번 더 묻는다**. 옛 웹 주소 다섯 개가 이 시점부터 404가 된다.
- [ ] **Step 2:** `gh repo rename ai-paper-trends --yes`를 실행한다. 이어서 `git remote set-url origin https://github.com/chpark-ML/ai-paper-trends.git`을 실행한다.
- [ ] **Step 3:** 저장소 설정을 바꾼다.

```bash
gh repo edit chpark-ML/ai-paper-trends \
  --description "Keyword → institution research trends across NeurIPS, ICML, ICLR, ACL, EMNLP (2025–2026), plus a NeurIPS 2026 medical LLM/RAG deep dive" \
  --homepage https://chpark-ml.github.io/ai-paper-trends/trends.html
```

- [ ] **Step 4:** 확인한다(스펙 §8).
  - `gh repo view --json nameWithOwner`의 결과가 `chpark-ML/ai-paper-trends`다.
  - `git remote -v`가 새 주소다.
  - Pages 재배포를 기다린 뒤 아래 여섯 주소가 모두 200을 돌려준다.

```bash
for p in trends interests explorer medical_qa opsd med_datasets; do curl -s -o /dev/null -w "$p %{http_code}\n" https://chpark-ml.github.io/ai-paper-trends/$p.html; done
```

- [ ] **Step 5:** 프로젝트 메모리 `multi-venue-expansion.md`를 "이름 변경 완료(날짜)"로 고친다.
