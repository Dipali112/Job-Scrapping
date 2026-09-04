# Indeed Jobs Scraper (Modernized)

A fast, reliable Python tool to automate job searches on Indeed across 60+ countries, extract full job descriptions and salaries, filter by keywords, and export clean structured data into CSV.

---

## Key Improvements (v2.0)

- **Cloudflare & Anti-Bot Bypass**: Bypasses modern anti-scraping protections and Cloudflare WAF challenges without requiring external browser installations or obsolete binaries.
- **Zero Driver Overhead**: Removed legacy bundled ChromeDriver binaries (Chrome v84) that failed on modern operating systems and Apple Silicon (`arm64`).
- **Rich Data Extraction**: Extracts Job Title, Company, Formatted Location, Salary/Compensation (hourly, daily, yearly), Job Rating, Post Recency, Full Markdown Descriptions, and Direct Apply URLs.
- **Interactive & CLI Automation**: Run interactively or supply one-line CLI arguments (`--search`, `--location`, `--country`, `--results`, `--days`).
- **Keyword Inclusion & Exclusion**: Customizable matching rules to include or discard jobs based on keywords in titles and descriptions.
- **Automated Test Suite**: Includes comprehensive tests covering matching logic, config persistence, and scraping pipelines.

---

## Requirements

- **Python 3.8+** (Tested on Python 3.8, 3.10, 3.12, 3.14)
- Works across macOS (Intel and Apple Silicon), Linux, and Windows.

---

## Setup & Installation

### Option 1: Standard Virtual Environment (`venv` + `pip`)

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

### Option 2: Using `uv` (Fastest)

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Option 3: Using `pipenv`

```bash
pipenv install
pipenv shell
```

---

## Usage

### 1. Interactive Mode

Run the crawler and follow the guided prompts:

```bash
python indeed_crawler.py
```

- When prompted: `Do you wish to scrape Indeed with the default search config? (yes/no)`
  - Enter **`yes`** to run with saved default settings (defaults to *Spanish teacher* in *New York*).
  - Enter **`no`** to configure a new search:
    - **Country**: (e.g. `USA`, `UK`, `Canada`, `Spain`, `Germany`, `India`)
    - **Job Title**: (e.g. `Machine Learning Engineer`)
    - **Location**: (e.g. `Remote`, `San Francisco, CA`, `London`)
    - **Base Salary**: (in thousands, e.g. `120`)
    - **Recency**: (days since posted, e.g. `7`)
    - **Keyword Matching Terms**: Specify words you want or do not want in the title or description.

### 2. Fast CLI Mode (Non-Interactive)

Run directly with command-line arguments:

```bash
# Run default configuration
python indeed_crawler.py --yes

# Search for Python Developer jobs in Remote
python indeed_crawler.py -s "Python Developer" -l "Remote" -c "USA" -n 20

# Search for Data Analyst jobs in London posted within the last 7 days
python indeed_crawler.py -s "Data Analyst" -l "London" -c "UK" -n 15 --days 7
```

#### Available CLI Arguments

| Flag | Full Option | Description | Example |
| :--- | :--- | :--- | :--- |
| `-y` | `--yes` | Run with saved default search config | `python indeed_crawler.py -y` |
| `-s` | `--search` | Job title or keyword search term | `-s "Backend Engineer"` |
| `-l` | `--location` | Target location or `Remote` | `-l "New York, NY"` |
| `-c` | `--country` | Country for the Indeed domain | `-c "Canada"` (default: `USA`) |
| `-n` | `--results` | Maximum number of job posts to retrieve | `-n 50` (default: `25`) |
| | `--days` | Filter to jobs posted within the last N days | `--days 3` |

---

## Output Data

All scraped results are saved into a CSV file in the `results/` folder:
`results/job_search_<job_title>.csv`

Each record contains:
1. **Job Title**: Title of the position.
2. **Location**: City, state, country, or Remote.
3. **Salary**: Parsed salary range with interval (e.g. `$120,000 - $160,000 yearly`, `$45 hourly`, or `Not shown`).
4. **Company**: Hiring employer name.
5. **Job Rating**: Company rating on Indeed (if available).
6. **Post time**: Relative posting date (`today`, `1 day ago`, `2 weeks ago`).
7. **Description**: Full job description in clean markdown formatting.
8. **Apply url**: Direct URL to apply or view on Indeed.

---

## Running Tests

To verify that the crawler, matching engine, and config handlers are operating properly:

```bash
pytest -v
```

---

## Project Structure

```
.
├── config/
│   ├── config_setup.py            # Loads configuration and parameters
│   ├── default_search_config.json # Persisted search settings
│   ├── matching_terms.json        # Persisted keyword matching rules
│   ├── query_string_maker.py      # Query string formatting utility
│   ├── set_matching_data.py       # Matching terms handler
│   ├── top_level_domains.json     # Supported country domains
│   └── url_builder.py             # Search URL & parameter builder
├── indeed_jobs_crawler/
│   ├── data_matcher.py            # Keyword inclusion/exclusion filter engine
│   └── info_scraper.py            # Modern high-performance Indeed scraper
├── results/                       # Generated CSV export directory
├── tests/                         # Automated test suite (pytest)
│   ├── test_config.py
│   ├── test_data_matcher.py
│   └── test_scraper.py
├── indeed_crawler.py              # Main CLI entry point
├── Pipfile                        # Pipenv dependency specification
├── pyproject.toml                 # Package configuration & test setup
├── requirements.txt               # Pip dependency specification
└── README.md
```
