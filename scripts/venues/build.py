"""Build normalized venue tables and the trends page data from data/raw/venues/.

Usage: python3 scripts/venues/build.py
Writes data/venues/<venue><year>.json.gz (normalized table, no abstracts) and trends/<venue><year>.json + trends/index.json
(page data), then prints track counts, institution rankings and possible split institutions for review."""
import collections
import datetime
import gzip
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from topic_trends import T  # noqa: E402
from venues.institutions import paper_institutions, split_candidates  # noqa: E402
from venues.parse import KEEP_TRACKS, parse_anthology, parse_cc  # noqa: E402

TOPICS = list(T)
_TRX = [re.compile(T[k], re.I) for k in TOPICS]
RAW, TABLE, PAGE = pathlib.Path('data/raw/venues'), pathlib.Path('data/venues'), pathlib.Path('trends')
ORDER = ['neurips', 'icml', 'iclr', 'acl', 'emnlp']


def _dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def _write_gz(path, text):  # mtime=0 keeps a rebuild with unchanged data byte-identical
    with open(path, 'wb') as f, gzip.GzipFile(fileobj=f, mode='wb', mtime=0) as g:
        g.write(text.encode('utf-8'))


def topic_hits(text):
    return [i for i, rx in enumerate(_TRX) if rx.search(text)]


def _labels(row, display):
    out = []
    for name, norm in paper_institutions(row['authors']):
        label = (name if norm else display.get(name.lower(), name), norm)
        if label not in out:
            out.append(label)
    return out


def venue_payload(rows, display):
    inst, index, papers = [], {}, []
    for r in rows:
        ids = []
        for label in _labels(r, display):
            if label not in index:
                index[label] = len(inst)
                inst.append(list(label))
            ids.append(index[label])
        papers.append([r['title'], r['url'], r['track'], r['decision'], ids, topic_hits(r['title'] + ' ' + r['abstract'])])
    return dict(venue=rows[0]['venue'] if rows else None, year=rows[0]['year'] if rows else None, n=len(rows),
                covered=sum(bool(p[4]) for p in papers), inst=inst, papers=papers)


def normalized_table(rows, display=None):
    return [dict({k: v for k, v in r.items() if k != 'abstract'}, inst=[n for n, _ in _labels(r, display or {})]) for r in rows]


def load_rows(venue, year):
    xml = RAW / f'{venue}{year}.xml'
    if xml.exists():
        return parse_anthology(xml.read_text(), venue, year)
    op = RAW / f'{venue}{year}_op.json'
    return parse_cc(json.loads((RAW / f'{venue}{year}_posters.json').read_text()),
                    json.loads(op.read_text()) if op.exists() else [], venue, year)


def _sets():
    found = {(m.group(1), int(m.group(2))) for f in RAW.glob('*') for m in [re.match(r'([a-z]+)(\d{4})', f.name)] if m}
    return sorted(found, key=lambda s: (ORDER.index(s[0]) if s[0] in ORDER else 99, s[1]))


def main():
    TABLE.mkdir(parents=True, exist_ok=True)
    PAGE.mkdir(exist_ok=True)
    kept = {}
    for v, y in _sets():
        rows = load_rows(v, y)
        tracks = collections.Counter(r['track'] for r in rows)
        kept[(v, y)] = [r for r in rows if r['track'] in KEEP_TRACKS]
        dropped = {t: c for t, c in tracks.items() if t not in KEEP_TRACKS}
        print(f'{v} {y}: {len(rows)} raw, kept {len(kept[(v, y)])}, tracks {dict(tracks)}, dropped {dropped}')
    spell = collections.defaultdict(collections.Counter)
    for rows in kept.values():
        for r in rows:
            for name, norm in paper_institutions(r['authors']):
                if not norm:
                    spell[name.lower()][name] += 1
    display = {k: c.most_common(1)[0][0] for k, c in spell.items()}
    index, overall = [], collections.Counter()
    for (v, y), rows in kept.items():
        pl = venue_payload(rows, display)
        _write_gz(TABLE / f'{v}{y}.json.gz', _dump(normalized_table(rows, display)))
        (PAGE / f'{v}{y}.json').write_text(_dump(pl))
        index.append(dict(venue=v, year=y, n=pl['n'], covered=pl['covered'], file=f'{v}{y}.json'))
        per = collections.Counter(pl['inst'][i][0] + ('' if pl['inst'][i][1] else ' *') for p in pl['papers'] for i in p[4])
        overall.update(per)
        print(f'\n## {v} {y} coverage {pl["covered"]}/{pl["n"]} top 50 (* = not normalized)')
        print('; '.join(f'{n} {c}' for n, c in per.most_common(50)))
    (PAGE / 'index.json').write_text(_dump(dict(topics=TOPICS, sets=index, built=datetime.date.today().isoformat())))
    print('\n## overall top 50 (* = not normalized)')
    print('; '.join(f'{n} {c}' for n, c in overall.most_common(50)))
    print('\n## possible splits in overall top 100')
    for a, b in split_candidates(dict(overall), top=100):
        print(f'  {a}  <->  {b}')
    print(f'\ntrends/ total {sum(f.stat().st_size for f in PAGE.glob("*.json")) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
