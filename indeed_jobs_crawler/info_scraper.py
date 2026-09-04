import re
from datetime import datetime, date
import pandas as pd
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests
from jobspy import scrape_jobs
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def format_salary(row):
    """Formats salary from JobSpy row to human-readable string."""
    min_amt = row.get('min_amount')
    max_amt = row.get('max_amount')
    interval = row.get('interval')
    currency = row.get('currency') or '$'
    symbol = '$' if currency in ['USD', '$'] else f'{currency} '

    if pd.notna(min_amt) and pd.notna(max_amt):
        if min_amt == max_amt:
            return f"{symbol}{min_amt:,.0f} {interval or ''}".strip()
        return f"{symbol}{min_amt:,.0f} - {symbol}{max_amt:,.0f} {interval or ''}".strip()
    elif pd.notna(min_amt):
        return f"{symbol}{min_amt:,.0f}+ {interval or ''}".strip()
    elif pd.notna(max_amt):
        return f"Up to {symbol}{max_amt:,.0f} {interval or ''}".strip()
    return 'Not shown'


def format_post_time(date_val):
    """Formats date into relative days string (e.g. 'today', '2 days ago')."""
    if not date_val or pd.isna(date_val):
        return 'recently'
    try:
        if isinstance(date_val, str):
            d = datetime.strptime(date_val, "%Y-%m-%d").date()
        elif isinstance(date_val, datetime):
            d = date_val.date()
        elif isinstance(date_val, date):
            d = date_val
        else:
            return str(date_val)
        delta = (date.today() - d).days
        if delta <= 0:
            return 'today'
        elif delta == 1:
            return '1 day ago'
        elif delta < 7:
            return f'{delta} days ago'
        elif delta < 30:
            weeks = delta // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = delta // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    except Exception:
        return str(date_val)


def scrape_indeed_data(search_title, location=None, country="USA", results_wanted=25, hours_old=None):
    """
    Modern high-speed scraper for Indeed jobs.
    Returns 8 lists: titles, descriptions, locations, companies, salaries, ratings, urls, days
    """
    is_remote = False
    clean_location = location
    if location and str(location).lower().strip() == 'remote':
        is_remote = True
        clean_location = None

    print(f"\n[Scraper] Fetching up to {results_wanted} Indeed jobs for '{search_title}' in '{location or 'Anywhere'}' (Country: {country})...")
    
    try:
        df = scrape_jobs(
            site_name=["indeed"],
            search_term=search_title,
            location=clean_location,
            is_remote=is_remote,
            results_wanted=results_wanted,
            country_indeed=country or "USA",
            hours_old=hours_old
        )
    except Exception as e:
        print(f"[Scraper] Warning: Error during Indeed scrape: {e}")
        df = pd.DataFrame()

    if df is None or df.empty:
        print("[Scraper] No jobs found for the specified query.")
        return [], [], [], [], [], [], [], []

    job_titles = []
    descriptions = []
    jobs_locations = []
    company_names = []
    salaries = []
    jobs_ratings = []
    apply_urls = []
    days = []

    for _, row in df.iterrows():
        title = str(row.get('title') or '').strip()
        desc = str(row.get('description') or '').strip()
        raw_loc = row.get('location')
        if pd.notna(raw_loc) and str(raw_loc).strip():
            loc = str(raw_loc).strip()
        else:
            loc = 'Remote' if is_remote else 'Not specified'
        comp = str(row.get('company') or 'Not specified').strip()
        sal = format_salary(row)
        rating = row.get('company_rating')
        if pd.isna(rating):
            rating = None
        else:
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                rating = None
        
        apply_url = str(row.get('job_url') or row.get('job_url_direct') or '').strip()
        post_time = format_post_time(row.get('date_posted'))

        job_titles.append(title)
        descriptions.append(desc)
        jobs_locations.append(loc)
        company_names.append(comp)
        salaries.append(sal)
        jobs_ratings.append(rating)
        apply_urls.append(apply_url)
        days.append(post_time)

    print(f"[Scraper] Successfully retrieved {len(job_titles)} jobs from Indeed.\n")
    return job_titles, descriptions, jobs_locations, company_names, salaries, jobs_ratings, apply_urls, days


# =====================================================================
# Backward Compatibility Helpers
# =====================================================================

def set_soup_object(url):
    """Uses curl_cffi to bypass Cloudflare anti-bot checks if raw HTML scraping is attempted."""
    try:
        resp = cffi_requests.get(url, impersonate='chrome', timeout=15)
        return BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return BeautifulSoup('', 'html.parser')


def get_jobs_titles(site, titles_list):
    scraped_job_titles = titles_list or []
    for tag in site.find_all(attrs={'data-jk': True}):
        title_el = tag.find(['h2', 'span'], class_=re.compile(r'jobTitle|title', re.I))
        if title_el:
            scraped_job_titles.append(title_el.text.strip())
    return scraped_job_titles


def get_jobs_locations(site, locations_list):
    scraped_job_locations = locations_list or []
    for tag in site.find_all(class_=re.compile(r'company_location|jobsearch-JobInfoHeader-companyLocation', re.I)):
        scraped_job_locations.append(tag.text.strip())
    return scraped_job_locations


def get_company_names(site, companies_list):
    scraped_company_names = companies_list or []
    for tag in site.find_all(attrs={'data-testid': 'company-name'}):
        scraped_company_names.append(tag.text.strip())
    return scraped_company_names


def get_salaries(site, salaries_list):
    return salaries_list or []


def get_jobs_ratings(site, ratings_list):
    return ratings_list or []


def get_apply_url(site, apply_list, view_job_url):
    scraped_apply_urls = apply_list or []
    for tag in site.find_all(attrs={'data-jk': True}):
        jk = tag.get('data-jk')
        if jk:
            scraped_apply_urls.append(f"{view_job_url}{jk}")
    return scraped_apply_urls


def get_days_since_posted(site, days_since_posted_list):
    return days_since_posted_list or []


def get_job_description(url, descriptions_list):
    return descriptions_list or []


def paginate_next(url):
    return None
