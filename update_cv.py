"""Read cv.pdf and create a plain HTML website in _site/. Needs only pypdf."""
import argparse
import json
import re
import shutil
import unicodedata
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

from pypdf import PdfReader
from pypdf.errors import PyPdfError

ROOT = Path(__file__).resolve().parent
HEADINGS = ('PROFILE', 'RESEARCH', 'EXPERIENCE', 'EDUCATION', 'SKILLS',
            'LANGUAGES', 'PUBLICATIONS', 'CONFERENCES')


def read_pdf(path):
    if path.stat().st_size > 15 * 1024 * 1024:
        raise ValueError('The PDF must be smaller than 15 MB.')
    pdf = PdfReader(path)
    if pdf.is_encrypted or not 1 <= len(pdf.pages) <= 25:
        raise ValueError('Use an unprotected PDF with 1–25 pages.')
    return '\n'.join(page.extract_text() or '' for page in pdf.pages)


def compact(text):
    return ' '.join(text.split())


def split_entries(text, pattern):
    starts = list(re.finditer(pattern, text, re.MULTILINE))
    if not starts or text[:starts[0].start()].strip():
        raise ValueError('An entry could not be recognised. Keep the supplied CV structure.')
    return [text[m.start():starts[i + 1].start() if i + 1 < len(starts) else len(text)].strip()
            for i, m in enumerate(starts)]


def read_career(text):
    entries = []
    for block in split_entries(text, r'^\['):
        lines = block.splitlines()
        match = re.fullmatch(r'\[([^]]+)\]\s+(.+)', lines[0])
        if not match or len(lines) < 3:
            raise ValueError('Each career entry needs [dates] title, institution and description.')
        period, title = match.groups()
        start = re.match(r'(?:(\d{2})/)?((?:19|20)\d{2})\s*[-–—]', period)
        if not start:
            raise ValueError('Use a date range such as [03/2026 - Present].')
        entries.append(dict(period=period, title=title, institution=lines[1],
                            description=compact(' '.join(lines[2:])),
                            order=(int(start[2]), int(start[1] or 1))))
    return sorted(entries, key=lambda e: e['order'], reverse=True)


def read_publications(text):
    entries = []
    for block in split_entries(text, r'^[“"]'):
        title = re.match(r'[“"](.+?)[”"]', block, re.DOTALL)
        if not title:
            raise ValueError('Put each publication title in quotation marks.')
        details = compact(block[title.end():])
        year = re.search(r'\b(?:19|20)\d{2}\b', details)
        doi = re.search(r'\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', details)
        thesis = 'thesis' in details.lower()
        if not year or (not doi and not thesis):
            raise ValueError('Every article needs a year and DOI. A thesis needs the word “thesis”.')
        entries.append(dict(title=compact(title[1]), year=int(year[0]), thesis=thesis,
                            doi=doi[0].rstrip('.;,') if doi else None,
                            details=re.sub(r'\s*DOI:.*$', '', details, flags=re.IGNORECASE)))
    dois = [p['doi'] for p in entries if p['doi']]
    if len(dois) != len(set(dois)):
        raise ValueError('Duplicate DOI found in the CV.')
    return sorted(entries, key=lambda p: p['year'], reverse=True)


def parse_cv(text):
    text = unicodedata.normalize('NFKC', text).replace('\u00ad', '')
    if not re.search(r'Elena\s+Cimmino', text, re.IGNORECASE):
        raise ValueError('Elena Cimmino was not found. Use a PDF with selectable text.')
    sections, current = {}, None
    for raw in text.splitlines():
        line = compact(raw)
        if not line or line == 'Elena Cimmino | Curriculum vitae' or re.fullmatch(r'\d{1,2}', line):
            continue
        if re.search(r'(?i)\b(address|date of birth|telephone|mobile|indirizzo|data di nascita)\s*:', line):
            raise ValueError('Remove private contact details from the PDF before publishing it.')
        if line in HEADINGS:
            if line in sections:
                raise ValueError('Duplicate section: ' + line)
            sections[line], current = [], line
        elif current:
            sections[current].append(line)
    missing = set(HEADINGS) - sections.keys()
    if missing:
        raise ValueError('Missing English CV headings: ' + ', '.join(sorted(missing)))
    sections = {key: '\n'.join(value) for key, value in sections.items()}
    if any(not value for value in sections.values()):
        raise ValueError('An empty section was found. Use “None” for optional sections.')
    data = {key.lower(): value for key, value in sections.items()}
    for key in ('experience', 'education'):
        data[key] = read_career(data[key])
    data['publications'] = read_publications(data['publications'])
    for key in ('skills', 'languages'):
        value = data[key]
        if value == 'None':
            data[key] = []
        elif not value.startswith('•'):
            raise ValueError('Keep bullet points in the skills and languages sections.')
        else:
            data[key] = [compact(item) for item in value.split('•') if item.strip()]
    data['conferences'] = [] if data['conferences'] == 'None' else [compact(e) for e in split_entries(data['conferences'], r'^[“"]')]
    return data


def paragraph(text, css=''):
    return f'<p class="{css}">{escape(compact(text))}</p>'


def career_html(entries):
    return '\n'.join('<article class="career-entry">' + paragraph(e['period'], 'meta')
                     + f'<h3>{escape(e["title"])}</h3>' + paragraph(e['institution'])
                     + paragraph(e['description'], 'muted') + '</article>' for e in entries)


def projects_html(projects):
    if not isinstance(projects, list):
        raise ValueError('projects.json must contain a list.')
    cards = []
    for project in projects:
        if not isinstance(project, dict) or any(not isinstance(project.get(k), str) or not project[k].strip() for k in ('title', 'description', 'url')):
            raise ValueError('Each project needs title, description and url.')
        url = urlsplit(project['url'])
        if url.scheme != 'https' or not url.hostname:
            raise ValueError('Project links must use HTTPS.')
        cards.append(f'<article class="project"><h3><a href="{escape(project["url"], quote=True)}" target="_blank" rel="noopener noreferrer">'
                     + escape(project['title']) + ' ↗</a></h3>'
                     + paragraph(project['description'], 'muted') + '</article>')
    return '\n'.join(cards) or '<p class="empty">No extra projects published yet.</p>'


def render(data, projects, template):
    latest = data['experience'][0]
    papers = []
    for p in data['publications']:
        title = escape(p['title'])
        if p['doi']:
            title = f'<a href="https://doi.org/{escape(p["doi"], quote=True)}" target="_blank" rel="noopener noreferrer">{title} ↗</a>'
        papers.append('<article class="publication">' + paragraph(str(p['year']) + (' · THESIS' if p['thesis'] else ''), 'meta')
                      + f'<h3>{title}</h3>' + paragraph(p['details'], 'muted') + '</article>')
    values = dict(
        latest_title=escape(latest['title']), latest_institution=escape(latest['institution']),
        latest_period=escape(latest['period']),
        latest_description=escape(re.split(r'(?<=[.!?])\s', latest['description'], maxsplit=1)[0]),
        profile=paragraph(data['profile'], 'lead'),
        research=paragraph(data['research'], 'muted') if data['research'] != 'None' else '',
        publications='\n'.join(papers), experience=career_html(data['experience']), education=career_html(data['education']),
        skills='\n'.join(f'<li>{escape(s)}</li>' for s in data['skills']),
        languages='\n'.join(f'<span>{escape(s)}</span>' for s in data['languages']),
        conferences='\n'.join(f'<li>{escape(c)}</li>' for c in data['conferences']) or '<li>No conference presentations listed.</li>',
        projects=projects_html(projects),
    )
    return Template(template).substitute(values)


def build(source=ROOT / 'cv.pdf', output=ROOT / '_site'):
    # Validate everything before replacing the last working page.
    data = parse_cv(read_pdf(source))
    projects = json.loads((ROOT / 'projects.json').read_text(encoding='utf-8'))
    html = render(data, projects, (ROOT / 'template.html').read_text(encoding='utf-8'))
    output.mkdir(parents=True, exist_ok=True)
    for filename in ('style.css', 'favicon.svg'):
        shutil.copyfile(ROOT / filename, output / filename)
    shutil.copyfile(source, output / 'cv.pdf')
    temporary = output / 'index.tmp'
    temporary.write_text(html, encoding='utf-8')
    temporary.replace(output / 'index.html')
    print(f"Site updated: {len(data['experience'])} jobs, {len(data['education'])} qualifications, {len(data['publications'])} publications/theses.")


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--cv', type=Path, default=ROOT / 'cv.pdf')
    cli.add_argument('--output', type=Path, default=ROOT / '_site')
    args = cli.parse_args()
    try:
        build(args.cv, args.output)
    except (ValueError, OSError, KeyError, PyPdfError) as error:
        cli.exit(1, f'Update stopped: {error}\nThe published site has not been changed.\n')
