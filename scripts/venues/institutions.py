"""Normalize raw affiliation strings to one name per institution.

Every alias regex is run over the whole affiliation string (strings are not split on commas or 'and', because
'National University of Singapore, DeepMind' is two institutions while 'School of Computing, National University of
Singapore' is one). A string with no alias hit is kept as-is and flagged normalized=False.

Granularity (design spec §6.3): company research arms roll up to the parent company; separately incorporated companies
stay apart; branch campuses roll up to the main university; UC campuses stay apart; hospitals stay apart from
universities; CAS institutes roll up to CAS while UCAS stays apart.
Seeded from scripts/notable_inst.py's INST (that file is left unchanged)."""
import re

ALIASES = [  # (canonical name, regex) — case-sensitive unless a group says (?i:...)
    # universities — US
    ('Stanford University', r'Stanford(?! (Health|Hospital|Medicine|Children))'),
    ('MIT', r'\bMIT\b|(?i:Massachusetts Institute of Technology)'),
    ('Harvard University', r'Harvard'),
    ('Carnegie Mellon University', r'(?i:Carnegie Mellon)|\bCMU\b'),
    ('UC Berkeley', r'UC Berkeley|(?i:University of California,? Berkeley)|(?<!Lawrence )\bBerkeley\b(?! (Lab|National))'),
    ('Princeton University', r'Princeton University|^Princeton$'),
    ('Caltech', r'Caltech|(?i:California Institute of Technology)'),
    ('Yale University', r'\bYale\b(?! New Haven)'),
    ('Columbia University', r'Columbia University'),
    ('Cornell University', r'Cornell'),
    ('University of Washington', r'(?i:University of Washington)'),
    ('Johns Hopkins University', r'Johns Hopkins(?! (Hospital|Medicine|Health System))'),
    ('Duke University', r'\bDuke\b'),
    ('University of Pennsylvania', r'(?i:University of Pennsylvania)|\bUPenn\b'),
    ('University of Chicago', r'(?i:University of Chicago)'),
    ('UCLA', r'\bUCLA\b|(?i:University of California,? Los Angeles)'),
    ('UC San Diego', r'UC San Diego|(?i:University of California,? San Diego)|\bUCSD\b'),
    ('University of Michigan', r'(?i:University of Michigan)'),
    ('NYU', r'\bNYU\b|(?i:New York University)'),
    # universities — Europe / Canada
    ('University of Oxford', r'(?i:University of Oxford)|Oxford University|^Oxford$'),
    ('University of Cambridge', r'(?i:University of Cambridge)'),
    ('Imperial College London', r'Imperial College'),
    ('UCL', r'(?i:University College London)|\bUCL\b'),
    ('ETH Zurich', r'\bETH\b|ETH Z|Swiss Federal Institute of Technology(?!,? (in )?Lausanne)'),
    ('EPFL', r'\bEPFL\b|Swiss Federal Institute of Technology,? (in )?Lausanne'),
    ('TU Munich', r'(?i:Technical University (of )?Munich)|Technische Universit\w+ M\w+nchen|\bTUM\b'),
    ('LMU Munich', r'Ludwig-Maximilians|\bLMU\b'),
    ('Max Planck Society', r'Max Planck'),
    ('University of Toronto', r'(?i:University of Toronto)'),
    ('Vector Institute', r'Vector Institute'),
    ('Mila', r'\bMila\b'),
    ('McGill University', r'McGill'),
    # universities — Asia
    ('Tsinghua University', r'(?<!National )(?i:Tsinghua)'),
    ('Peking University', r'(?i:Peking University)'),
    ('Shanghai Jiao Tong University', r'(?i:Shanghai Jiao ?Tong)|\bSJTU\b'),
    ('Zhejiang University', r'(?i:Zhejiang University)(?! of)'),
    ('Fudan University', r'Fudan'),
    ('Harbin Institute of Technology', r'(?i:Harbin Institute of Technology)'),
    ('University of Tokyo', r'(?i:University of Tokyo)|The University of Tokyo'),
    ('KAIST', r'\bKAIST\b|(?i:Korea Advanced Institute of Science)'),
    ('Seoul National University', r'(?i:Seoul National University)(?! (Bundang )?Hospital| of)'),
    ('National University of Singapore', r'(?i:National University of Singapore)|\bNUS\b'),
    ('HKUST', r'\bHKUST\b|(?i:Hong ?Kong University of Science)'),
    ('University of Hong Kong', r'(?i:(?<!Chinese )(?<!City )(?<!Education )(?<!Open )University of Hong Kong)|\bHKU\b'),
    ('City University of Hong Kong', r'(?i:City University of Hong Kong)|\bCityU\b'),
    ('CUHK', r'(?i:Chinese University of Hong Kong)|\bCUHK\b'),
    ('Chinese Academy of Sciences', r'(?<!University of )(?<!University of the )(?i:Chinese Academy of Sciences?)|\bCASIA\b|\bCAS\b'),
    ('University of Chinese Academy of Sciences', r'(?i:University of (the )?Chinese Academy of Sciences?)|\bUCAS\b'),
    ('RIKEN', r'\bRIKEN\b'),
    # universities — added in Task 5 from the most frequent unnormalized strings of 2025–2026
    ('UIUC', r'University of Illinois(?:,? at|,)? Urbana[- ]Champaign|\bUIUC\b'),
    ('UT Austin', r'(?i:University of Texas)(?:,| at)? Austin|\bUT[- ]Austin\b'),
    ('University of Wisconsin-Madison', r'University of Wisconsin\s*[-–,]?\s*Madison|\bUW[- ]Madison\b'),
    ('Georgia Tech', r'Georgia Institute of Technology|Georgia Tech\b'),
    ('University of Southern California', r'University of Southern California|\bUSC\b'),
    ('Purdue University', r'Purdue'),
    ('University of Maryland', r'University of Maryland(?!,? Baltimore)|\bUMD\b'),
    ('Northwestern University', r'Northwestern University'),
    ('UNC Chapel Hill', r'University of North Carolina at Chapel Hill|UNC[- ]Chapel Hill'),
    ('Penn State', r'Pennsylvania State University|\bPenn State\b'),
    ('Arizona State University', r'Arizona State University'),
    ('Rutgers University', r'Rutgers'),
    ('University of Virginia', r'University of Virginia'),
    ('University of Central Florida', r'University of Central Florida'),
    ('University of Notre Dame', r'Notre Dame'),
    ('UC Santa Barbara', r'(?i:University of California,? Santa Barbara)|UC Santa Barbara|\bUCSB\b'),
    ('UC Irvine', r'(?i:University of California,? Irvine)|UC Irvine'),
    ('UC Davis', r'(?i:University of California,? Davis)|UC Davis'),
    ('UC Santa Cruz', r'(?i:University of California,? Santa Cruz)|UC Santa Cruz'),
    ('UC Riverside', r'(?i:University of California,? Riverside)|UC Riverside'),
    ('Texas A&M University', r'Texas A&M'),
    ('Michigan State University', r'Michigan State University'),
    ('Ohio State University', r'Ohio State University'),
    ('Rice University', r'Rice University'),
    ('Emory University', r'Emory University'),
    ('Brown University', r'Brown University'),
    ('Boston University', r'Boston University'),
    ('Virginia Tech', r'Virginia Tech|Virginia Polytechnic Institute'),
    ('Dartmouth College', r'Dartmouth'),
    ('UMass Amherst', r'University of Massachusetts,?( at)? Amherst|UMass Amherst'),
    ('University of Illinois Chicago', r'University of Illinois,?( at)? Chicago'),
    ('Stony Brook University', r'Stony Brook'),
    ('Washington University in St. Louis', r'Washington University(,| in) (Saint|St\.?) Louis'),
    ('University of Waterloo', r'University of Waterloo'),
    ('University of British Columbia', r'University of British Columbia'),
    ('University of Alberta', r'University of Alberta'),
    ('Université de Montréal', r'Universit[ée] de Montr[ée]al|University of Montreal'),
    ('University of Edinburgh', r'University of Edinburgh'),
    ("King's College London", r"King's College London"),
    ('University of Amsterdam', r'University of Amsterdam'),
    ('University of Tübingen', r'Universit\w* (?:of )?T(?:ü|ue)bingen|T(?:ü|ue)bingen University|Eberhard[- ]Karls'),
    ('INRIA', r'(?i:\binria\b)'),
    ('Technion', r'Technion'),
    ('Tel Aviv University', r'Tel Aviv University'),
    ('MBZUAI', r'\bMBZUAI\b|Mohamed [Bb]in Zayed University'),
    ('KAUST', r'\bKAUST\b|King Abdullah University of Science and Technology'),
    ('University of Sydney', r'(?<!Technology )University of Sydney'),
    ('University of Technology Sydney', r'University of Technology,? Sydney'),
    ('University of Melbourne', r'University of Melbourne'),
    ('Monash University', r'Monash'),
    ('Australian National University', r'Australian National University'),
    ('UNSW Sydney', r'University of New South Wales|\bUNSW\b'),
    ('Nanyang Technological University', r'Nanyang Technological University'),
    ('Singapore Management University', r'Singapore Management University'),
    ('SUTD', r'Singapore University of Technology and Design'),
    ('A*STAR', r'A\*STAR|Agency for Science, Technology and Research'),
    ('Hong Kong Polytechnic University', r'Hong Kong Polytechnic University|\bPolyU\b'),
    ('Hong Kong Baptist University', r'Hong Kong Baptist University'),
    ('University of Macau', r'(?<!City )University of Macau'),
    ('National Taiwan University', r'National Taiwan University(?! of)'),
    ('Yonsei University', r'Yonsei'),
    ('Korea University', r'(?<![\w-])Korea University(?! of)'),
    ('Sungkyunkwan University', r'Sungkyunkwan|Sung Kyun Kwan|\bSKKU\b'),
    ('POSTECH', r'\bPOSTECH\b|Pohang University of Science and Technology'),
    ('USTC', r'University of Science and Technology of China|\bUSTC\b'),
    ('UESTC', r'University of Electronic Science and Technology of China|\bUESTC\b'),
    ('Nanjing University', r'(?i:Nanjing University)(?! of)'),
    ('Nanjing University of Science and Technology', r'Nanjing University of Science and Technology'),
    ('Nanjing University of Aeronautics and Astronautics', r'Nanjing University of Aeronautics and Astronautics'),
    ('Renmin University of China', r'(?i:Renmin University)'),
    ('Sun Yat-sen University', r'(?i:Sun Yat-?sen)'),
    ('BUPT', r'Beijing University of Posts? and Telecommunications|\bBUPT\b'),
    ('Huazhong University of Science and Technology', r'Huazhong University of Science and Technology|\bHUST\b'),
    ('Wuhan University', r'Wuhan University(?! of)'),
    ('Beihang University', r'Beihang|Beijing University of Aeronautics and Astronautics'),
    ("Xi'an Jiaotong University", r"(?i:Xi'?an Jiao ?tong University)|\bXJTU\b"),
    ('Xidian University', r"Xidian|Xi'an University of Electronic Science and Technology"),
    ('Southeast University', r'Southeast University'),
    ('East China Normal University', r'East China Normal University'),
    ('Tianjin University', r'Tianjin University(?! of)'),
    ('Tongji University', r'Tongji'),
    ('South China University of Technology', r'South China University of Technology'),
    ('Beijing Institute of Technology', r'Beijing Institute of Technology'),
    ('Beijing Jiaotong University', r'Beijing Jiaotong University'),
    ('Beijing Normal University', r'Beijing Normal University'),
    ('Westlake University', r'Westlake University'),
    ('National University of Defense Technology', r'National University of Defense Technology'),
    ('Xiamen University', r'Xiamen University'),
    ('SUSTech', r'Southern University of Science and Technology|\bSUSTech\b'),
    ('Nankai University', r'Nankai'),
    ('Sichuan University', r'Sichuan University(?! of)'),
    ('Shandong University', r'Shandong University(?! of)'),
    ('Shenzhen University', r'\bShenzhen University(?! of)'),
    ('Jilin University', r'Jilin University'),
    ('Central South University', r'Central South University'),
    ('ShanghaiTech University', r'ShanghaiTech'),
    ('Dalian University of Technology', r'Dalian University of Technology'),
    ('Soochow University', r'Soochow University'),
    ('Northwestern Polytechnical University', r'Northwest(?:ern)? Polytechnical University'),
    ('Shanghai University of Finance and Economics', r'Shanghai University of Finance and Economics'),
    ('University of Adelaide', r'University of Adelaide|Adelaide University'),
    ('University of Minnesota', r'University of Minnesota'),
    ('TU Darmstadt', r'TU Darmstadt|Technische Universit(?:ä|ae)t Darmstadt|Technical University of Darmstadt'),
    ('ISTA', r'\bISTA\b|Institute of Science and Technology Austria'),
    ('Shanghai AI Lab', r'Shanghai (?:AI|Artificial Intelligence) Lab(?:oratory)?'),
    # hospitals (kept apart from universities)
    ('Mayo Clinic', r'Mayo Clinic'),
    ('Mass General Brigham', r'Massachusetts General|Mass General|Brigham and Women'),
    ('MD Anderson', r'MD Anderson'),
    ('Memorial Sloan Kettering', r'Memorial Sloan|\bMSK\b'),
    ('UCSF', r'\bUCSF\b|(?i:University of California,? San Francisco)'),
    ('Cleveland Clinic', r'Cleveland Clinic'),
    ('Mount Sinai', r'Mount Sinai'),
    ('Charité', r'Charit'),
    ('Seoul National University Hospital', r'(?i:Seoul National University (Bundang )?Hospital)|\bSNUH\b'),
    # companies and labs
    ('Google', r'Google|DeepMind'),
    ('Microsoft', r'Microsoft'),
    ('Meta', r'\bMeta\b|\bFAIR\b|Facebook'),
    ('OpenAI', r'OpenAI'),
    ('Anthropic', r'Anthropic'),
    ('NVIDIA', r'(?i:NVIDIA)'),
    ('Apple', r'\bApple\b'),
    ('Amazon', r'Amazon|\bAWS\b'),
    ('IBM', r'\bIBM\b|International Business Machines'),
    ('Alibaba', r'Alibaba|\bQwen\b|DAMO Academy'),
    ('Ant Group', r'Ant Group|Ant Financial'),
    ('Tencent', r'Tencent'),
    ('ByteDance', r'(?i:ByteDance|TikTok)'),
    ('Salesforce', r'(?i:Salesforce)'),
    ('Samsung', r'Samsung(?! Medical)'),
    ('Huawei', r'(?i:Huawei)'),
    ('Baidu', r'Baidu'),
    ('Kuaishou', r'(?i:Kuaishou)'),
    ('Meituan', r'(?i:Meituan)'),
    ('Adobe', r'\bAdobe\b'),
    ('Qualcomm', r'Qualcomm'),
    ('SenseTime', r'(?i:SenseTime)'),
    ('Allen Institute for AI', r'Allen Institute for (AI|Artificial Intelligence)|\bAI2\b|\bAi2\b'),
]
_RX = [(n, re.compile(p)) for n, p in ALIASES]
_FIELD = (r'(?:computer|science|sciences|computing|engineering|electrical|electronic|electronics|statistics|data|'
          r'artificial|intelligence|mathematics|information|communication|technology|and|&|cs|ai|eecs)')
DEPT_ONLY = re.compile(rf'(?i)^(?:(?:department|school|faculty|college) of )?(?:{_FIELD}\s*)+(?:department)?$')
JUNK = {'', 'independent researcher', 'independent', 'unaffiliated', 'n/a', 'na', 'none', 'null', 'unknown', '-', '--'}


def canon(affil):
    s = ' '.join((affil or '').replace('\u2019', "'").split())
    hits = sorted((m.start(), n) for n, rx in _RX for m in [rx.search(s)] if m)
    out = []
    for _, n in hits:
        if (n, True) not in out:
            out.append((n, True))
    if out:
        return out
    if s.strip(' .').lower() in JUNK or DEPT_ONLY.match(s.strip(' .')):
        return []
    return [(re.sub(r'(?i)^the\s+', '', s.strip(' ,;')), False)]


def paper_institutions(authors):
    out = []
    for a in authors:
        for x in canon(a.get('affil')):
            if x not in out:
                out.append(x)
    return out


def _key(name):
    return re.sub(r'[^a-z0-9 ]+', ' ', name.lower()).split()


def _close(a, b):
    if a == b:
        return True
    if abs(len(a) - len(b)) > 2:
        return False
    prev = list(range(len(b) + 1))  # Levenshtein, small strings only
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] <= 2


def split_candidates(counts, top=100):
    names = sorted(counts, key=lambda n: -counts[n])[:top]
    keys = {n: _key(n) for n in names}
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ka, kb = keys[a], keys[b]
            if _close(' '.join(ka), ' '.join(kb)) or (len(ka) > 1 and len(kb) > 1 and (set(ka) <= set(kb) or set(kb) <= set(ka))):
                out.append((a, b))
    return out
