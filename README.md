# doi2bib:  DOI to BibTeX Citation Fetcher

A Python utility that reads DOI identifiers from a text file, retrieves BibTeX citations through DOI content negotiation, and saves the results to a `.bib` file.

The program supports both DOI-only files and files that contain local citation keys.

## Features

* Accepts DOI URLs such as `https://doi.org/10.xxxx/xxxxx`.
* Accepts bare DOI identifiers such as `10.xxxx/xxxxx`.
* Accepts `doi:10.xxxx/xxxxx`.
* Supports optional local citation keys.
* Retrieves BibTeX metadata through DOI content negotiation.
* Preserves the publisher's BibTeX key when no local key is provided.
* Replaces the publisher's BibTeX key when a local citation key is provided.
* Reports successful and failed DOI requests.
* Does not guess missing bibliographic information.
* Adds a short delay between requests.

## Requirements

* Python 3.8 or newer
* `requests`

Install `requests` with:

```bash
pip install requests
```

## Input Formats

The program supports three common formats.

### 1. Citation key + DOI

```text
baker2015structjumper https://doi.org/10.1145/2702123.2702589
baltes2022sampling https://doi.org/10.1007/s10664-021-10072-8
bonaker2022nomon https://doi.org/10.1145/3491102.3517738
```

The citation key is preserved in the generated BibTeX.

For example:

```bibtex
@inproceedings{baker2015structjumper,
  ...
}
```

### 2. DOI URL only

```text
https://doi.org/10.1145/2702123.2702589
https://doi.org/10.1007/s10664-021-10072-8
https://doi.org/10.1145/3491102.3517738
```

When no local key is provided, the publisher's BibTeX key is preserved.

### 3. Bare DOI only

```text
10.1145/2702123.2702589
10.1007/s10664-021-10072-8
10.1145/3491102.3517738
```

The program automatically recognizes the DOI and retrieves the citation.

### Mixed input

The formats can also be mixed in the same file:

```text
baker2015structjumper https://doi.org/10.1145/2702123.2702589
https://doi.org/10.1007/s10664-021-10072-8
10.1145/3491102.3517738
doi:10.1038/s41467-024-53873-3
```

## Usage

Place the Python script and input file in the same directory:

```text
project/
├── get_citations.py
└── doi.txt
```

Run:

```bash
python get_citations.py
```

The program reads:

```text
doi.txt
```

and creates:

```text
citations.bib
```

The resulting directory will look like:

```text
project/
├── get_citations.py
├── doi.txt
└── citations.bib
```

## Citation Keys

If the input contains a local citation key:

```text
baker2015structjumper https://doi.org/10.1145/2702123.2702589
```

the program replaces the publisher's BibTeX key with:

```text
baker2015structjumper
```

For example:

```bibtex
@inproceedings{baker2015structjumper,
  ...
}
```

If the input contains only a DOI:

```text
10.1145/2702123.2702589
```

the program does not modify the publisher's BibTeX key.

This behavior is useful when the DOI list comes from an existing bibliography where citation keys need to be preserved.

## Output

Successfully retrieved citations are written to:

```text
citations.bib
```

For example:

```bibtex
@inproceedings{baker2015structjumper,
  author = {...},
  title = {...},
  year = {...},
  pages = {...},
  doi = {10.1145/2702123.2702589}
}
```

The exact fields depend on the metadata returned by the DOI provider and publisher.

## Failed Requests

The program reports failed requests during execution.

For example:

```text
[3/20] example2024paper
  DOI: 10.1145/example
  ERROR: HTTP 403
  FAILED
```

At the end, it reports a summary:

```text
============================================================
Successfully retrieved: 18
Failed:                2

Failed entries:
  example2024paper: 10.1145/example
  another2023paper: 10.1007/example

BibTeX written to: citations.bib
```

Failed entries should be checked manually through the publisher or DOI landing page.

## How It Retrieves BibTeX

The program sends a request to the DOI resolver with the following HTTP header:

```text
Accept: application/x-bibtex
```

This requests the citation in BibTeX format through DOI content negotiation.

The program then verifies that the response begins with a BibTeX entry such as:

```text
@article{
```

or:

```text
@inproceedings{
```

before writing it to the output file.

## Limitations

DOI content negotiation does not guarantee that every publisher will return complete BibTeX metadata.

Possible issues include:

* HTTP `403` responses
* HTTP `503` responses
* Missing page ranges
* Missing `numpages`
* Missing `articleno`
* Incomplete metadata
* Publisher-specific BibTeX formatting
* DOI providers that do not return BibTeX

Therefore, a successful retrieval does not necessarily mean that every bibliographic field is complete.

In particular, **page information should not be guessed**. If a page range is missing, verify it using the publisher or another authoritative source before adding it to a research paper.

## Verification

The generated `citations.bib` file should be reviewed before being used in a final paper.

Important fields to verify include:

* Authors
* Title
* Venue
* Publication year
* DOI
* Pages
* Article number
* Volume
* Issue

The program is a citation retrieval tool and is **not a complete bibliography validation system**.

## Request Rate

The program waits one second between DOI requests:

```python
time.sleep(1)
```

This reduces the rate of requests and is intended to avoid unnecessarily sending requests in rapid succession.

