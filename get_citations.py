import re
import time
import requests

INPUT_FILE = "doi.txt"
OUTPUT_FILE = "citations.bib"

DOI_PATTERN = re.compile(
    r"(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?"
    r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)",
    re.IGNORECASE,
)

def get_bibtex(doi):
    """Retrieve a BibTeX citation from DOI content negotiation."""
    url = f"https://doi.org/{doi}"

    headers = {
        "Accept": "application/x-bibtex",
        "User-Agent": "BibTeXFetcher/1.0",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
            allow_redirects=True,
        )

        if response.status_code == 200:
            bibtex = response.text.strip()

            if bibtex.startswith("@"):
                return bibtex

        print(f"  ERROR: HTTP {response.status_code}")

    except requests.RequestException as e:
        print(f"  ERROR: {e}")

    return None


def extract_dois(filename):
    """
    Extract DOI entries from a text file.

    Supported formats:

        citation_key https://doi.org/10.xxxx/xxxxx
        https://doi.org/10.xxxx/xxxxx
        10.xxxx/xxxxx
        doi:10.xxxx/xxxxx

    Returns:
        List of (citation_key, doi) tuples.

        citation_key is None when no local key is provided.
    """
    entries = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            match = DOI_PATTERN.search(line)

            if not match:
                continue

            doi = match.group(1).rstrip(".,;)")

            # Text before the DOI.
            prefix = line[:match.start()].strip()

            # If the DOI is a URL or starts with "doi:",
            # there should normally be no citation key in the prefix.
            if prefix:
                key = prefix
            else:
                key = None

            entries.append((key, doi))

    return entries


def replace_bibtex_key(bibtex, key):
    """Replace the publisher's BibTeX key with the local citation key."""
    return re.sub(
        r"^(@\w+\s*\{\s*)[^,]+",
        rf"\1{key}",
        bibtex,
        count=1,
    )


def main():
    entries = extract_dois(INPUT_FILE)

    print(f"Found {len(entries)} DOI entries.\n")

    successful = []
    failed = []

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for i, (key, doi) in enumerate(entries, 1):

            display_key = key if key else "(publisher key)"

            print(f"[{i}/{len(entries)}] {display_key}")
            print(f"  DOI: {doi}")

            bibtex = get_bibtex(doi)

            if bibtex:

                # Only replace the BibTeX key when the input
                # contains a local citation key.
                if key:
                    bibtex = replace_bibtex_key(bibtex, key)

                out.write(bibtex)
                out.write("\n\n")

                successful.append((key, doi))
                print("  OK")

            else:
                failed.append((key, doi))
                print("  FAILED")

            # Be polite to DOI/publisher servers.
            time.sleep(1)

    print("\n" + "=" * 60)
    print(f"Successfully retrieved: {len(successful)}")
    print(f"Failed:                {len(failed)}")

    if failed:
        print("\nFailed entries:")

        for key, doi in failed:
            if key:
                print(f"  {key}: {doi}")
            else:
                print(f"  {doi}")

    print(f"\nBibTeX written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
