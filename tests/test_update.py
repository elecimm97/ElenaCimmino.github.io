import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import update_cv as site

class CVTests(unittest.TestCase):
    def setUp(self):
        self.text = site.read_pdf(ROOT / 'cv.pdf')
        self.template = (ROOT / 'template.html').read_text()

    def test_current_pdf_has_complete_sections(self):
        data = site.parse_cv(self.text)
        for key in ('experience', 'education', 'publications', 'skills'):
            self.assertTrue(data[key])
        self.assertTrue(all(p['doi'] or p['thesis'] for p in data['publications']))

    def test_changed_role_reaches_english_html(self):
        text = self.text.replace('Postdoctoral Researcher', 'Research Scientist')
        data = site.parse_cv(text)
        html = site.render(data, [], self.template)
        self.assertIn('<h2>Research Scientist</h2>', html)
        self.assertIn('lang="en"', html)
        self.assertIn('No extra projects published yet.', html)
        self.assertNotIn('$latest_title', html)

    def test_new_experience_reaches_html(self):
        extra = '[09/2027 - Present] Research Fellow\nExample University\nGenomic data analysis.\n'
        before = site.parse_cv(self.text)
        after = site.parse_cv(self.text.replace('EDUCATION', extra + 'EDUCATION'))
        self.assertEqual(len(after['experience']), len(before['experience']) + 1)
        self.assertEqual(after['experience'][0]['title'], 'Research Fellow')

    def test_new_publication_reaches_html(self):
        extra = '“A new computational study”\nRossi A. Example Journal, 2027.\nDOI: 10.1234/example.2027\n'
        before = site.parse_cv(self.text)
        after = site.parse_cv(self.text.replace('CONFERENCES', extra + 'CONFERENCES'))
        self.assertEqual(len(after['publications']), len(before['publications']) + 1)
        self.assertIn('https://doi.org/10.1234/example.2027', site.render(after, [], self.template))

    def test_missing_section_stops_update(self):
        with self.assertRaises(ValueError):
            site.parse_cv(self.text.replace('PUBLICATIONS', 'LAVORI'))

    def test_bad_pdf_preserves_last_output(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            bad = folder / 'bad.pdf'
            bad.write_text('not a PDF')
            output = folder / '_site'
            output.mkdir()
            (output / 'index.html').write_text('previous version')
            with self.assertRaises(Exception):
                site.build(bad, output)
            self.assertEqual((output / 'index.html').read_text(), 'previous version')

    def test_projects_survive_cv_changes_and_are_escaped(self):
        project = dict(title='A <project>', description='<script>test</script>', url='https://example.org/project')
        data = site.parse_cv(self.text.replace('Postdoctoral Researcher', 'Research Scientist'))
        html = site.render(data, [project], self.template)
        self.assertIn('https://example.org/project', html)
        self.assertIn('A &lt;project&gt;', html)
        self.assertNotIn('<script>test</script>', html)
        with self.assertRaises(ValueError):
            site.projects_html([dict(project, url='javascript:alert(1)')])

if __name__ == '__main__':
    unittest.main()
