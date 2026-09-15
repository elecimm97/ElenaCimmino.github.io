# Elena Cimmino — Research Portfolio

Personal academic portfolio covering bioinformatics, computational biology, publications, professional experience and side projects.

The website uses plain HTML and CSS. A single Python script reads the public English CV and generates the pages for GitHub Pages. Its only external Python dependency is `pypdf`.

## How it works

1. Update the English CV and upload it as `cv.pdf` to the repository root.
2. Commit the change to `main`.
3. The **Update portfolio from CV** workflow reads the PDF, runs the checks and publishes the updated website.

The profile, research, experience, education, skills, languages, publications and conference presentations come from the PDF. Side projects are maintained separately in `projects.json`. Navigation, introductory copy and contact links are defined in `template.html`.

If the workflow fails, the previously published website remains online. Check the failed run in the **Actions** tab for details.

## Project files

| File | Purpose |
| --- | --- |
| `template.html` | Page structure, fixed text and contact links |
| `style.css` | Light/dark colours, typography, portrait styling and responsive layout |
| `theme.js` | Small theme switcher with a saved visitor preference |
| `update_cv.py` | PDF reader and static website generator |
| `cv.pdf` | Public English CV used as the content source |
| `CV-English.txt` | Editable starting text for the English CV |
| `projects.json` | Independent side-project entries |
| `favicon.svg` | Website icon |
| `requirements.txt` | Python dependency |
| `tests/test_update.py` | Automated checks |
| `.github/workflows/publish.yml` | GitHub Pages publishing workflow |

Generated files are written to `_site/`: `index.html`, `style.css`, `theme.js`, `favicon.svg`, `cv.pdf` and the optional portrait. Content and links work without JavaScript; the theme switcher uses `theme.js`. No application server is required.

## Adding a portrait

Upload your portrait to the repository root as `photo.jpg`, `photo.jpeg`, `photo.png` or `photo.webp` (lowercase filenames). Keep only one of these files. On the next successful workflow run, it appears above the latest experience in the introduction. The image is optional: the page remains complete when no photo is present.

The image is displayed in a circular crop. Adjust `--photo-size`, `--photo-radius` and `--photo-position` at the top of `style.css` to change its size, shape and crop position. For example, use `--photo-radius: 12px` for rounded corners instead of a circle. Upload only a photo you want to make public.

## Light and dark modes

The page initially follows the visitor’s device preference. The **Dark mode / Light mode** button overrides it and remembers the choice in the browser. If browser storage is unavailable, switching still works for the current page.

Customise the light palette in `:root` and the dark palette in `:root[data-theme="dark"]` at the top of `style.css`. Shared font, page-width and portrait settings are in the same area. Change other CSS rules to adjust spacing and layout. Commit changes to `style.css` on `main` to republish them automatically.

## Updating the CV

Use a PDF with selectable text and keep the structure of the supplied English CV. This reader is tailored to that template; scanned documents and substantially different layouts require changes to the reader. Content is not automatically translated.

Keep each of these section headings on a separate line:

```text
PROFILE
RESEARCH
EXPERIENCE
EDUCATION
SKILLS
LANGUAGES
PUBLICATIONS
CONFERENCES
```

For experience and education, use this structure:

```text
[03/2026 - Present] Postdoctoral Researcher
Institution name
Description in English.
```

Keep the date range and role or degree title on the same line, followed by the institution on its own line and then the description.

- **Skills and languages:** use bullet points (`•`).
- **Publications:** begin each entry with the title in quotation marks, followed by authors, publication details, year and DOI. A thesis entry must include the word `thesis` and does not require a DOI.
- **Conferences:** begin each entry with the presentation title in quotation marks.
- **Optional sections:** keep the heading and write `None` if there are no entries for research, skills, languages or conferences.

`CV-English.txt` can be copied into a document editor and exported as a PDF. The website reads only `cv.pdf`: editing the text file alone does not update it.

Upload only information intended for public release. Both the PDF and repository contents are publicly accessible. The reader's checks for selected personal-data labels are not a general anonymisation system.

## Adding side projects

Edit `projects.json` and add entries in this format:

```json
[
  {
    "title": "Project title",
    "description": "A short description in English.",
    "url": "https://example.org/your-project"
  }
]
```

Replace the example URL with a real HTTPS link. Projects may link to repositories, websites or applications hosted elsewhere. Add more objects separated by commas, or use `[]` for an empty list. Updating the CV never overwrites this file.

## Publishing with GitHub Pages

1. Place the project files in the root of your public portfolio repository, including `.github/workflows/publish.yml`.
2. Open **Settings → Pages** and select **GitHub Actions** under **Build and deployment → Source**.
3. Open **Actions → Update portfolio from CV → Run workflow** and select `main` to start the first deployment.
4. Wait for the workflow to complete successfully.

Once deployed, open the public URL shown in the successful **publish** job or in **Settings → Pages**. Subsequent commits to `main` trigger updates automatically.

## Local use

With Python 3.12 installed, run these commands from the project directory:

```sh
python3 -m pip install -r requirements.txt
python3 update_cv.py
```

Open `_site/index.html` in a browser to view the generated website. No local web server is required.

To run the automated checks:

```sh
python3 -m unittest discover -s tests
```

The checks cover CV extraction, changed roles, additional experience and publications, missing sections, preservation of the previous output after an invalid PDF, and independent project rendering with HTML escaping and HTTPS link validation.
