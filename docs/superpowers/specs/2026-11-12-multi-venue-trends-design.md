# 학회 확장 연구 동향 추적 — 설계

작성일 2026-11-12. 이 저장소(NeurIPS 2026 정리)를 NeurIPS·ICML·ICLR·ACL·EMNLP의 main 논문으로 넓혀, **키워드를 기준으로 어떤 연구가 어떤 기관에서 진행되는지**를 학회·연도를 가로질러 보는 페이지를 만든다.

## 1. 의도

사용자는 연구 동향을 파악하려고 이 저장소를 연다. 구체적으로는 키워드(예: medical agent, RAG, knowledge distillation)를 하나 정해 두고, **그 주제를 어느 기관들이 하고 있는지** 볼 때다. 지금 저장소는 NeurIPS 2026 한 학회뿐이고, `explorer.html`은 저자 소속을 표시 전에 지운다(`scripts/explorer.py:29`). 그래서 "이 키워드 → 어느 기관"이 바로 보이지 않는다.

새 학회가 나올 때마다 같은 방식으로 추가해 계속 추적하는 것이 목표다.

## 2. 목표

1. **학회 공통 논문 표.** 다섯 학회·두 해의 main 논문을 같은 열(학회, 연도, 트랙, 발표 형식, 제목, 초록, 저자별 소속, 정규화된 기관, 링크)로 모은다.
2. **키워드 → 기관 페이지.** 키워드를 고르면
   - 학회·연도별 해당 논문 수와 그 학회 전체 대비 비율(동향),
   - 해당 논문을 낸 기관 순위(기관별 편수, 학회·연도별 내역),
   - 기관을 누르면 그 기관의 해당 논문 목록
   을 보여 준다.
3. **기관 이름 정규화.** "Google DeepMind", "Google Research", "Google"처럼 표기가 다른 같은 기관을 하나로 센다.
4. **학회 추가가 명령 한두 줄.** 새 학회·연도를 넣을 때 손으로 고치는 단계가 없다.

## 3. 비목표 (v1에서 하지 않는다)

- 새 학회에 대한 LLM 분류(14개 분야, 212개 세부 주제, 관심 분야 216편 같은 판독). 키워드는 정규식으로만 붙인다.
- ACL·EMNLP의 Findings, 그리고 모든 학회의 workshop·demo·industry·SRW·tutorial.
- arXiv 본문 읽기, 인용 수.
- 저자(사람) 단위 추적.
- 외부 DB(OpenAlex 등)로 소속 보충. §6.3에 후속 선택지로만 남긴다.

## 4. 이렇게 되면 실패다 (반목표)

- **기관을 조용히 잘못 센다.** 예: `MIT` 별칭이 `MITRE`에 걸리거나, `Meta`가 다른 단어에 걸림. 잘못 붙이느니 "정규화 안 됨"으로 원문 그대로 두는 편이 낫다.
- **소속 누락을 숨긴다.** ACL·EMNLP는 소속이 비어 있는 저자가 많다(§5). 페이지에 학회·연도별 소속 확보율이 보여야 한다.
- **기존 페이지가 깨진다.** `interests.html`, `explorer.html`, `medical_qa.html`, `opsd.html`, `med_datasets.html`은 내용이 그대로여야 하고, 새 주소(§6.7)에서 열려야 한다. 옛 주소가 끊기는 것은 사용자가 받아들였다(§6.7).
- **휴대폰에서 못 연다.** README가 "휴대폰에서도 열린다"고 약속한다. 새 페이지도 그래야 한다.

## 5. 데이터 원천 (2026-11-12 직접 받아 확인한 값)

| 학회 | 받는 곳 | 2025 편수 | 2026 편수 | 소속 |
|---|---|---:|---:|---|
| NeurIPS | `neurips.cc/Downloads/{year}` POST (현 `scripts/fetch.sh`와 같은 방식) | 5,860 (10월 스냅샷, README) | 9,094 (10월 스냅샷, README) | 저자 문자열 `이름 (소속)` |
| ICML | `icml.cc/Downloads/{year}` POST, 같은 방식 | 3,339 | 6,628 | 저자 문자열에 소속 있는 논문 2025 100%, 2026 6,622/6,628 |
| ICLR | `iclr.cc/Downloads/{year}` POST, 같은 방식 | 3,826 | 5,466 | 저자 문자열에 소속 있는 논문 2025 3,825/3,826, 2026 5,464/5,466 |
| ACL | ACL Anthology XML `github.com/acl-org/acl-anthology` `data/xml/{year}.acl.xml`, volume `long`+`short` | 1,699 | 2,296 | 저자별 `<affiliation>` 태그 |
| EMNLP | 같은 저장소 `data/xml/{year}.emnlp.xml`, volume `main` | 1,809 | 2,704 | 저자별 `<affiliation>` 태그 |

- `*.cc` 세 학회의 발표 형식(Oral/Spotlight/Poster)은 `static/virtual/data/{venue}-{year}-orals-posters.json`에서 온다. 표기가 학회·해마다 다르다(ICML 2025 `Accept (spotlight poster)`, ICML 2026 `Accept (regular)`, ICLR 2025 `Accept` 49편 등). 대소문자를 무시하고 Oral·Spotlight·Poster로 접는다. ICLR 2026 데이터에는 Spotlight 표기가 없다(Poster 5,244, Oral 224). 그래서 학회 간 Spotlight 비율은 비교하지 않는다.
- 같은 기관의 표기가 학회 안에서도 갈린다. 예: ICLR 2026에서 `CASIA`는 13회, `Institute of Automation, Chinese Academy of Sciences`는 61회 나온다.
- `*.cc` 소속 괄호 하나에 여러 기관이 쉼표로 들어가기도 한다. 쉼표는 한 기관 이름 안에도 나와서 쉼표만으로는 나눌 수 없다. ICLR 2025 예: `National University of Singapore, DeepMind`(두 기관), `School of Computing, National University of Singapore`(한 기관), `national university of singaore, National University of Singapore`(오타가 섞인 같은 기관). 그래서 소속 문자열을 쪼개기보다 **문자열 전체에 별칭 정규식을 모두 돌려 걸리는 기관을 전부 붙인다**(§6.3).
- ACL·EMNLP 소속 확보율(같은 XML에서 계산):

  | | 소속이 있는 저자 비율 | 소속 있는 저자가 1명 이상인 논문 | 제1·마지막 저자 모두 소속 있음 |
  |---|---:|---:|---:|
  | ACL 2025 | 61% | 97% | 41% |
  | EMNLP 2025 | 64% | 98% | 42% |
  | ACL 2026 | 57% | 98% | 34% |
  | EMNLP 2026 | 66% | 99% | 45% |

  논문 단위로는 거의 다 기관을 하나 이상 얻지만, 제1·마지막 저자 기준으로는 절반도 안 된다. 그래서 **논문 → 기관은 모든 저자의 기관 합집합**으로 정한다(§6.3).
- ACL 소속 문자열에는 `Google and The University of Melbourne`처럼 한 칸에 두 기관이 들어 있는 경우가 있다.
- **NeurIPS 원본은 이 checkout에 없다**(`ls data/raw` → `No such file or directory`). 그래서 NeurIPS도 다른 학회처럼 새로 받는다. 기존 다섯 페이지는 10월 스냅샷으로 만든 커밋된 `data/`를 그대로 쓰고, 다시 만들지 않는다. *(내 결정)*
- ICML·ICLR·ACL·EMNLP 편수는 2026-11-12에 받아 센 값이다. 받은 파일은 세션 임시 폴더에만 있었으므로 빌더가 다시 받는다. 다시 받은 수가 위 표와 다르면 **다시 받은 수가 기준**이다. 차이는 빌드 로그와 완료 보고에 적는다.

## 6. 결정한 것

### 6.1 범위

- 학회: NeurIPS, ICML, ICLR, ACL, EMNLP. 연도: 2025, 2026. 이후 새 연도를 같은 방식으로 추가한다.
- "main 논문"의 정의:
  - ACL: main conference의 long·short. EMNLP: main. Findings 제외.
  - NeurIPS·ICML·ICLR: 해당 학회 사이트에 올라온 채택 논문 중 그 학회 자체의 논문을 남긴다.
    - 남기는 것: Main, Evaluations & Datasets, Position, 그리고 트랙 정보가 없는 논문. 트랙 열로 구분한다.
    - 빼는 것: TMLR 등 저널 논문의 학회 발표(Journal), ICLR 블로그 트랙(Blog), NeurIPS Bridging the Future 포스터.
    - 이 트랙들은 2026-11-12 orals-posters JSON의 `sourceurl`에서 확인했다. 예: ICML 2026 `TMLR-2026` 61편, ICLR 2025 `BlogPosts` 49편, NeurIPS 2026 `bridging-the-future` 36편. *(내 결정, 계획 단계에서 추가)*

### 6.2 키워드

- 기존 `scripts/topic_trends.py`의 키워드 주제 58개(정규식, 제목+초록 대상)를 그대로 쓴다. 의료(`Medical / clinical`, `Medical QA`), RAG, 에이전트, distillation 등이 이미 있다.
- 키워드를 추가하려면 이 사전에 정규식 한 줄을 넣고 다시 빌드한다.
- 페이지에는 정해진 키워드 외에 자유 검색창도 둔다(제목·기관 대상).
- 키워드를 여러 개 고르면 기본은 **모두 해당(AND)**이다. "의료 × 에이전트"처럼 좁혀 보는 쓰임을 기본으로 둔다. "하나라도 해당(OR)"으로 바꾸는 토글을 함께 둔다. 기존 `explorer.html`은 OR이지만 새 페이지는 별개다. *(내 결정)*
- `topic_trends.py`에 키워드를 추가해도 된다. 기존 페이지는 다시 만들지 않으므로 영향이 없다.

### 6.3 기관

- 저자별 소속 문자열 얻기: `*.cc`는 `scripts/notable_inst.py`의 `authors_with_affil`(중첩 괄호 처리)을 재사용한다. ACL·EMNLP는 XML의 저자별 `<affiliation>`을 쓴다.
- 정규화: 별칭 정규식 표(현 `notable_inst.py`의 68개 기관에서 시작)를 소속 문자열 전체에 돌려, 걸리는 대표 기관을 모두 붙인다. 문자열을 쉼표나 ` and `로 미리 쪼개지 않는다(§5의 예처럼 쪼개기가 모호하다).
- 어디까지를 한 기관으로 보는가. 현 `notable_inst.py`의 관행(Google과 DeepMind는 하나, Max Planck 연구소들은 하나, UC 캠퍼스들은 각각 따로, Mass General Brigham은 Harvard와 따로)을 일반화한 규칙이다. *(내 결정)*

  | 경우 | 규칙 | 예 |
  |---|---|---|
  | 기업의 연구조직·자회사 브랜드 | 모회사로 합친다 | DeepMind → Google, FAIR → Meta, Qwen·DAMO → Alibaba |
  | 별도 법인 기업 | 따로 | Ant Group ≠ Alibaba |
  | 대학의 분교·부설 대학원 | 본교로 합친다 | HIT Shenzhen → HIT, Tsinghua SIGS → Tsinghua |
  | 독립 대학인 캠퍼스 | 따로 | UC Berkeley ≠ UCLA ≠ UCSD ≠ UCSF |
  | 병원·의료원 | 대학과 따로 | Mass General Brigham ≠ Harvard, 서울대병원 ≠ 서울대 |
  | 연구원 산하 연구소 | 연구원으로 합친다 | CASIA·ICT → Chinese Academy of Sciences |
  | 연구원 소속 대학 | 따로 | UCAS ≠ Chinese Academy of Sciences |
- 별칭이 하나도 걸리지 않은 소속은 공백·대소문자만 다듬은 원문 그대로 둔다. 순위에는 나오되 "정규화 안 됨"으로 표시한다.
- 별칭 표는 실제 데이터에서 빈도 상위 기관부터 늘린다. 몇 개까지 늘릴지는 빌더가 정한다.
- **v1 완료 조건:** 키워드 필터 없는 기관 순위(전체, 그리고 학회·연도별)의 상위 50위 안에 같은 기관이 두 이름으로 갈라져 있으면 안 된다. 키워드로 좁힌 화면에는 이 조건을 걸지 않는다. 작은 키워드의 하위권은 정규화 안 된 원문이 섞여도 된다. *(내 결정)*
- **이후 유지:** 빌드는 갈라졌을 가능성이 있는 기관 쌍(예: 정규화 후 이름이 비슷한 상위 100위 안의 쌍)을 경고로 출력만 한다. 빌드를 실패시키지 않고 자동으로 합치지도 않는다. 별칭 추가는 가끔 하는 정비 작업이지, §6.6 갱신 절차의 일부가 아니다. *(내 결정)*
- 논문 → 기관: 모든 저자의 정규화된 기관 집합이다. 한 논문은 한 기관에 한 번만 센다.
- OpenAlex(저자별 기관이 ROR로 정규화돼 있음)는 v1에 쓰지 않는다. ACL 2025 논문 5편으로 확인한 결과, 논문에 따라 저자 12명 중 3명부터 9명 중 9명까지 기관이 붙어 있었다. 보충 효과가 있을지는 표본이 작아 아직 모른다. 후속 선택지로 남긴다.

### 6.4 페이지

- 새 페이지 하나를 만든다. 기존 `explorer.html`은 NeurIPS 2026 전용 LLM 분류에 기대고 있으므로 건드리지 않는다. *(내 결정)*
- 구성(위에서 아래로):
  1. 필터: 학회·연도 선택, 키워드 주제(여러 개 가능), 자유 검색.
  2. 동향: 학회·연도별 해당 편수와 그 학회 전체 대비 비율.
  3. 기관 순위: 기관별 편수(학회·연도 내역 포함). 기관을 누르면 논문 목록이 펼쳐진다.
  4. 소속 확보율: 선택한 학회·연도마다 "기관을 하나 이상 얻은 논문 비율".
- 기존 페이지처럼 한국어 UI, 정적 HTML, GitHub Pages로 배포한다.
- README는 손으로 쓰지 않는다. `scripts/build.py`(341행 `open('README.md', 'w')`)가 통째로 생성한다. 그래서 새 페이지 한 줄은 `scripts/build.py`의 README 생성 부분에 넣는다. 함께 고칠 것은 "다섯 페이지" 문장과 '재현' 명령이다. 이 줄에는 편수 같은 변하는 숫자를 넣지 않는다. 숫자는 새 페이지가 직접 보여 준다. *(내 결정)*

### 6.5 데이터 보관

- 원본 다운로드는 지금처럼 `data/raw/`(git 제외)에 둔다.
- 정규화된 논문 표와 페이지 데이터는 커밋한다. 다만 저장소가 지나치게 커지지 않게 한다. 초록 전문 대신 페이지에 필요한 만큼만 넣는 등 방법은 빌더가 정한다.

### 6.6 갱신 절차

새 학회·연도 추가는 아래 두 단계면 끝나야 한다.

```bash
python3 scripts/venues/fetch.py <venue> <year>   # 원본 받기 → data/raw/
python3 scripts/venues/build.py                  # 정규화 → 페이지 생성
```

명령 이름과 파일 배치는 빌더가 정해도 된다. 지켜야 할 것은 "명령 두 줄, 수작업 없음"이다.

### 6.7 저장소 이름 변경

저장소가 NeurIPS 2026 하나를 넘어서므로 이름을 바꾼다. 아래 둘은 **사용자가 정했다**.

- 새 이름: `chpark-ML/neurips2026-medical-llm-rag` → **`chpark-ML/ai-paper-trends`**. 웹 페이지 주소는 `https://chpark-ml.github.io/ai-paper-trends/`가 된다.
- 옛 웹 페이지 주소는 **그냥 끊는다.** GitHub는 이름을 바꾸면 저장소·git 주소는 자동으로 넘겨 주지만 GitHub Pages 프로젝트 사이트 주소는 넘겨 주지 않는다([GitHub Docs: Renaming a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)). 옛 이름으로 안내용 저장소는 만들지 않는다. 만들면 GitHub의 저장소·git 주소 자동 이동이 끊긴다.

현재 상태(2026-11-12 확인):

- `gh repo view` → 공개 저장소, homepage `https://chpark-ml.github.io/neurips2026-medical-llm-rag/interests.html`, 설명은 NeurIPS 2026 의료·RAG 216편만 언급한다.
- GitHub Pages는 `main` 브랜치 루트에서 배포 중이다(`gh api repos/{owner}/{repo}/pages` → `status: built`).
- 옛 이름이 들어 있는 파일(`grep -rln neurips2026-medical-llm-rag`, `.git`·`docs` 제외):
  - `scripts/build.py`: 288행 `BASE`와 91·279·282행 등 링크.
  - 이 스크립트가 생성하는 `README.md`(5곳), `REPORT.md`(8곳).
  - `scripts/medqa_bench/` 스크립트 4개의 User-Agent 문자열.
  - HTML 다섯 페이지에는 없다(0곳).

할 일:

1. `scripts/build.py`의 옛 주소를 새 주소로 바꾸고 다시 실행해 `README.md`·`REPORT.md`를 다시 만든다.
   - **먼저** 아무것도 고치지 않은 `build.py`를 실행해 git diff가 비는지 확인한다. 이 스크립트는 커밋된 `data/`만 읽지만(`json.load` 대상이 모두 `data/` 아래), 실제로 같은 출력을 내는지는 아직 확인하지 않았다.
   - diff가 비지 않으면 멈추고 보고한다. 이 스크립트는 `interests.html`·`HIGHLIGHTS.md`·`data/papers.csv`도 다시 쓴다.
2. `gh repo rename ai-paper-trends`로 이름을 바꾸고, 로컬 clone의 주소를 `git remote set-url`로 갱신한다.
3. 저장소 설명을 새 범위(다섯 학회 키워드·기관 동향 + NeurIPS 2026 의료 LLM·RAG 정리)로 바꾸고, homepage를 새 동향 페이지 주소로 바꾼다. 문구는 빌더가 정한다. *(homepage를 새 페이지로 바꾸는 것은 내 결정)*
4. 순서: 새 페이지가 동작한 뒤, 주소 변경 커밋과 이름 변경을 한 단계로 한다. 둘 사이에 README 링크가 잠깐 깨지는 것은 괜찮다.

하지 않는 것:

- `scripts/medqa_bench/`의 User-Agent 문자열. 이미 실행이 끝난 수집 스크립트이고, 바꿔도 동작이 달라지지 않는다. *(내 결정)*
- 로컬 폴더 이름(`~/projects/neurips2026-medical-llm-rag`). 바꾸면 이 폴더에 묶인 Claude Code 프로젝트 메모리 경로도 바뀐다. 원하면 사용자가 직접 바꾼다. *(내 결정)*

## 7. 빌더에게 맡기는 것

- 스크립트 구조와 파일 이름.
- 페이지가 휴대폰에서 열리도록 데이터를 나누는 방법. 예: 학회·연도별 파일을 나눠 필요할 때 불러오기, 초록 길이 줄이기.
- 별칭 표의 크기와 작성 방법. 단, §6.3의 상위 50위 조건은 지킨다.
- 자유 검색이 초록까지 볼지 여부(페이지 크기와 맞바꿈).

## 8. 완료 확인

- 학회·연도별 편수가 그날 받은 원본의 편수와 같다. §5 표와의 차이는 보고에 적는다.
- 무작위로 고른 논문 20편의 기관이 원본 소속 문자열과 맞는다.
- 필터 없는 기관 순위 상위 50위(전체와 학회·연도별)를 눈으로 훑었을 때 잘못 합쳐진 것(MIT/MITRE 등)과 갈라진 것이 없다. 합치는 기준은 §6.3 표다.
- 키워드 `Medical / clinical`의 NeurIPS 2026 편수가 같은 정규식을 새로 받은 원본에 직접 돌린 수와 같다. 10월 스냅샷 집계(`data/topic_trends.json`의 438편)와의 차이는 보고에 적는다.
- 기존 다섯 HTML 페이지와 `data/` 아래 기존 파일의 git diff가 비어 있다. 바뀐 기존 파일은 아래뿐이다.
  - `scripts/build.py`: README 생성 부분과 옛 주소.
  - `README.md`
  - `REPORT.md`: 주소만.
  - 키워드를 추가했다면 `scripts/topic_trends.py`.
- 이름 변경 후 확인:
  - `gh repo view`의 이름이 `chpark-ML/ai-paper-trends`다.
  - `git remote -v`가 새 주소다.
  - 새 주소의 여섯 페이지(기존 다섯 + 새 페이지)가 HTTP 200을 돌려준다.
  - 저장소 전체에서 `neurips2026-medical-llm-rag`를 grep하면 `scripts/medqa_bench/`의 User-Agent와 이 설계 문서에만 남아 있다.
- 휴대폰 너비에서 새 페이지가 가로 스크롤 없이 열린다.
