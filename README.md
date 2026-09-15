# Portfolio di Elena Cimmino

Sito interamente in inglese, con HTML e CSS standard. Un solo script Python legge il CV PDF e aggiorna i contenuti prima della pubblicazione su GitHub Pages. L'unica libreria richiesta è **pypdf**. Non servono Node.js, React, servizi di intelligenza artificiale o chiavi API.

## I file principali

| File | A cosa serve |
| --- | --- |
| `template.html` | Struttura della pagina, testi fissi e contatti |
| `style.css` | Colori, caratteri e disposizione della pagina |
| `update_cv.py` | Lettura del PDF e generazione del sito |
| `cv.pdf` | Il CV pubblico in inglese da sostituire agli aggiornamenti |
| `projects.json` | I progetti extra, indipendenti dal CV |

Ci sono inoltre l'icona, l'elenco dell'unica dipendenza, alcuni controlli automatici e `.github/workflows/publish.yml`, che attiva tutto su GitHub. Il sito generato contiene solamente `index.html`, `style.css`, `favicon.svg` e `cv.pdf`. La pagina funziona anche senza JavaScript.

## Aggiornare il CV

1. Aggiorna il CV **in inglese** e salva un PDF con testo selezionabile, chiamato **cv.pdf**.
2. Nel repository GitHub usa **Add file → Upload files** e sostituisci `cv.pdf` nella cartella principale.
3. Conferma il caricamento sul ramo **main**.
4. Nella scheda **Actions**, l'automazione **Update portfolio from CV** legge il PDF e ripubblica il sito.

Si aggiornano profilo, ricerca, esperienze, formazione, competenze, lingue, pubblicazioni e congressi. I progetti extra e i testi fissi della pagina rimangono indipendenti. Se la lettura del CV fallisce, GitHub interrompe l'esecuzione e conserva il sito già pubblicato.

**Il file va caricato su GitHub:** modificarlo soltanto sul computer non aggiorna il sito.

## Il formato del CV

Per mantenere il lettore semplice, questa versione usa **il modello inglese incluso**. Il vecchio CV italiano e il modello AlmaLaurea non sono più ingressi supportati. Non c'è una traduzione automatica durante gli aggiornamenti: traduci i nuovi contenuti prima di caricare il PDF.

La copia inglese conserva i contenuti professionali della precedente versione italiana: 2 esperienze, 3 titoli di studio, 5 articoli, una tesi e 4 comunicazioni a congresso. Il testo modificabile è disponibile anche nel file `CV-English.txt` consegnato insieme al sito; puoi copiarlo nel programma che usi per scrivere il CV ed esportarlo in PDF.

Mantieni questi titoli di sezione, ciascuno su una riga:

```
PROFILE
RESEARCH
EXPERIENCE
EDUCATION
SKILLS
LANGUAGES
PUBLICATIONS
CONFERENCES
```

Le voci di esperienza e formazione seguono questo schema:

```
[03/2026 - Present] Postdoctoral Researcher
Nome dell'istituzione
Descrizione in inglese.
```

Mantieni titolo e date sulla stessa riga, e l'istituzione su una riga separata. Competenze e lingue usano punti elenco `•`. Ogni pubblicazione inizia con il titolo tra virgolette, seguito da autori, rivista, anno e DOI; per la tesi usa le parole **PhD thesis**, senza obbligo di DOI. Ogni comunicazione a congresso inizia con il titolo tra virgolette. Per sezioni facoltative prive di contenuti, conserva il titolo e scrivi `None`.

Puoi aggiungere e rimuovere voci, ma cambiamenti importanti nell'impaginazione possono richiedere un adattamento del lettore. I nomi ufficiali italiani degli enti sono mantenuti dove appropriato; il resto del sito è in inglese.

Il CV incluso non contiene indirizzo di casa, telefono o data di nascita. **Carica solo informazioni che vuoi rendere pubbliche:** il PDF sarà visibile anche nel repository. Il controllo di alcune etichette personali non è un sistema universale di anonimizzazione.

## Aggiungere progetti extra

Modifica `projects.json`. Al momento contiene `[]`, in attesa dei tuoi progetti. Esempio di struttura:

```json
[
  {
    "title": "Project title",
    "description": "A short description in English.",
    "url": "https://example.org/your-project"
  }
]
```

Sostituisci il link di esempio con quello reale. Se aggiungi altri progetti, separa gli oggetti con una virgola. Puoi collegare repository, siti e altri materiali HTTPS. Caricare un nuovo CV non modifica questo file.

## Prima pubblicazione su GitHub Pages

La pubblicazione sul tuo account **non è ancora stata attivata**.

1. Accedi a GitHub come **EleCimm** e crea un repository pubblico chiamato **EleCimm.github.io**, se non esiste già.
2. Scompatta l'archivio e carica **il contenuto** nella cartella principale del repository, senza caricare lo ZIP o una cartella aggiuntiva. Includi la cartella nascosta **.github**: sul Mac puoi mostrarla con **⌘ ⇧ .**.
3. In **Settings → Pages → Source** scegli **GitHub Actions**.
4. In **Actions → Update portfolio from CV → Run workflow** avvia la prima pubblicazione.
5. Quando l'esecuzione termina con successo, il sito sarà su **https://elecimm.github.io/**.

## Lavorare sul sito dal computer

Con Python 3.12 installato, dalla cartella del progetto:

```sh
python3 -m pip install -r requirements.txt
python3 update_cv.py
```

Apri `_site/index.html` nel browser: è un sito statico completo, che puoi aprire direttamente anche senza avviare un server.

Per eseguire i controlli:

```sh
python3 -m unittest discover -s tests
```

I controlli verificano lettura, aggiornamenti di ruoli e pubblicazioni, conservazione dell'ultima versione in caso di errore e gestione separata dei progetti. Sono stati controllati anche i contenuti del sito generato, i collegamenti interni e tutte le pagine del PDF inglese. Non sono stati eseguiti test visivi del sito nel browser né una pubblicazione reale su GitHub.
