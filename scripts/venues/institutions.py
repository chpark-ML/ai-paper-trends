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
    ('Princeton University', r'Princeton'),
    ('Caltech', r'Caltech|(?i:California Institute of Technology)'),
    ('Yale University', r'\bYale\b'),
    ('Columbia University', r'Columbia University'),
    ('Cornell University', r'Cornell'),
    ('University of Washington', r'(?i:University of Washington)'),
    ('Johns Hopkins University', r'Johns Hopkins'),
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
    ('ETH Zurich', r'\bETH\b|ETH Z'),
    ('EPFL', r'\bEPFL\b'),
    ('TU Munich', r'(?i:Technical University of Munich)|Technische Universit\w+ M\w+nchen|\bTUM\b'),
    ('LMU Munich', r'Ludwig-Maximilians|\bLMU\b'),
    ('Max Planck Society', r'Max Planck'),
    ('University of Toronto', r'(?i:University of Toronto)'),
    ('Vector Institute', r'Vector Institute'),
    ('Mila', r'\bMila\b'),
    ('McGill University', r'McGill'),
    # universities — Asia
    ('Tsinghua University', r'(?i:Tsinghua)'),
    ('Peking University', r'(?i:Peking University)'),
    ('Shanghai Jiao Tong University', r'(?i:Shanghai Jiao ?Tong)|\bSJTU\b'),
    ('Zhejiang University', r'(?i:Zhejiang University)'),
    ('Fudan University', r'Fudan'),
    ('Harbin Institute of Technology', r'(?i:Harbin Institute of Technology)'),
    ('University of Tokyo', r'(?i:University of Tokyo)|The University of Tokyo'),
    ('KAIST', r'\bKAIST\b|(?i:Korea Advanced Institute of Science)'),
    ('Seoul National University', r'(?i:Seoul National University)(?! (Bundang )?Hospital)'),
    ('National University of Singapore', r'(?i:National University of Singapore)|\bNUS\b'),
    ('HKUST', r'\bHKUST\b|(?i:Hong Kong University of Science)'),
    ('University of Hong Kong', r'(?i:(?<!Chinese )University of Hong Kong)|\bHKU\b'),
    ('CUHK', r'(?i:Chinese University of Hong Kong)|\bCUHK\b'),
    ('Chinese Academy of Sciences', r'(?<!University of )(?<!University of the )(?i:Chinese Academy of Sciences)|\bCASIA\b|\bCAS\b'),
    ('University of Chinese Academy of Sciences', r'(?i:University of (the )?Chinese Academy of Sciences)|\bUCAS\b'),
    ('RIKEN', r'\bRIKEN\b'),
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
    ('Meta', r'\bMeta\b|\bFAIR\b'),
    ('OpenAI', r'OpenAI'),
    ('Anthropic', r'Anthropic'),
    ('NVIDIA', r'(?i:NVIDIA)'),
    ('Apple', r'\bApple\b'),
    ('Amazon', r'Amazon|\bAWS\b'),
    ('IBM', r'\bIBM\b'),
    ('Alibaba', r'Alibaba|\bQwen\b|DAMO Academy'),
    ('Ant Group', r'Ant Group|Ant Financial'),
    ('Tencent', r'Tencent'),
    ('ByteDance', r'(?i:ByteDance)'),
    ('Salesforce', r'Salesforce'),
    ('Samsung', r'Samsung'),
    ('Allen Institute for AI', r'Allen Institute|\bAI2\b|\bAi2\b'),
]
_RX = [(n, re.compile(p)) for n, p in ALIASES]
JUNK = {'', 'independent researcher', 'independent', 'unaffiliated', 'n/a', 'na', 'none', 'null', 'unknown', '-', '--'}


def canon(affil):
    s = ' '.join((affil or '').split())
    if s.strip(' .').lower() in JUNK:
        return []
    hits = sorted((m.start(), n) for n, rx in _RX for m in [rx.search(s)] if m)
    out = []
    for _, n in hits:
        if (n, True) not in out:
            out.append((n, True))
    return out or [(s.strip(' ,;'), False)]


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
