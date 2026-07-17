# Item Finder (Product Search Agent)

A Python tool that takes a spreadsheet of products and automatically finds matching listings for them on Amazon and Flipkart, flagging each match with a confidence score.

## What It Does

You give it an Excel file with a `GeM Title`, `GeM Brand`, and `GeM Model` column per row (the column names come from India's GeM government procurement portal, but any spreadsheet with those headers works). For each row, it:

1. Builds a search query from the brand, model, and title (e.g. `Acer AL15 52 Acer Aspire Lite AL15 amazon OR flipkart`).
2. Runs that query through DuckDuckGo search (via the `ddgs` library) and keeps only results linking to `amazon.in` or `flipkart.com`.
3. Scores each candidate result's title against the target text using `difflib.SequenceMatcher` and keeps the best match.
4. Labels the row based on the similarity score:
   - `>= 0.45` → "Found, no need for human review"
   - `0.20 - 0.45` → "Needs human review"
   - `< 0.20` or no match → "Item not found"
5. Writes a new timestamped Excel file (`search_results_<timestamp>.xlsx`) with the original data plus `Amazon/Flipkart Link`, `Similarity Score`, and `Review Status` columns.

There's a 2-second delay between searches to reduce the chance of getting rate-limited.

Two ways to run it:
- **`app.py`** — a small Flask web app with a drag-and-drop upload page; download the results file when processing finishes.
- **`agent.py`** — a command-line version that prompts for an input file path (defaulting to `sample_products.xlsx`) and writes the results file to the working directory.

## Tech Stack

- **Python 3**
- [pandas](https://pandas.pydata.org/) + [openpyxl](https://openpyxl.readthedocs.io/) — reading/writing `.xlsx` files
- [ddgs](https://pypi.org/project/ddgs/) — DuckDuckGo search client
- [Flask](https://flask.palletsprojects.com/) — web UI (`app.py`)
- `difflib` (standard library) — string similarity scoring

## Setup

```bash
git clone https://github.com/rkaran112/item_finder.git
cd item_finder
pip install -r requirements.txt
```

Dependencies installed: `pandas`, `openpyxl`, `ddgs`, `flask`.

## Usage

**Web UI:**
```bash
python app.py
```
Then open `http://127.0.0.1:5000`, upload an `.xlsx` file, and download the results once processing finishes.

**Command line:**
```bash
python agent.py
```
Press Enter to use the bundled `sample_products.xlsx`, or type the path to your own file.

**Required input columns** (case-sensitive): `GeM Title`, `GeM Brand`, `GeM Model`. Other columns are preserved but ignored for matching.

## Status

Functional prototype — the core search/match/export pipeline works end-to-end for both the CLI and web interfaces. Known rough edges:

- **Generated result files aren't cleaned up**: each processed upload leaves a `search_results_<timestamp>.xlsx` behind in the project root; there's no expiry or deletion logic. (Uploaded files themselves are now removed from `uploads/` right after processing.)
- **Test coverage is partial**: `tests/` covers score classification, required-column validation, the download route, upload cleanup, `search_product`'s link-filtering/best-match selection, and `process_excel`'s end-to-end row loop (all via mocked DDGS/search calls). Live network behavior against DuckDuckGo is untested.
- **Search reliability depends on DuckDuckGo/`ddgs`** and is not resilient to search API changes, CAPTCHAs, or extended rate limiting beyond the fixed 2-second delay.

No packaging (e.g. `setup.py`/`pyproject.toml`) — it's run directly as scripts.
