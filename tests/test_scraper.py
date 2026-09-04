from datetime import date, timedelta
import pandas as pd
import pytest
from indeed_jobs_crawler.info_scraper import format_salary, format_post_time, scrape_indeed_data


def test_format_salary():
    # Range
    row1 = {'min_amount': 80000, 'max_amount': 120000, 'interval': 'yearly', 'currency': 'USD'}
    assert format_salary(row1) == "$80,000 - $120,000 yearly"

    # Exact
    row2 = {'min_amount': 50, 'max_amount': 50, 'interval': 'hourly', 'currency': 'USD'}
    assert format_salary(row2) == "$50 hourly"

    # None / Missing
    row3 = {'min_amount': None, 'max_amount': None, 'interval': None, 'currency': None}
    assert format_salary(row3) == "Not shown"


def test_format_post_time():
    today = date.today()
    assert format_post_time(today) == "today"
    assert format_post_time(today - timedelta(days=1)) == "1 day ago"
    assert format_post_time(today - timedelta(days=4)) == "4 days ago"
    assert format_post_time(today - timedelta(days=14)) == "2 weeks ago"
    assert format_post_time(today - timedelta(days=60)) == "2 months ago"
    assert format_post_time(None) == "recently"


def test_scrape_indeed_data_live():
    """Verify that scrape_indeed_data successfully queries Indeed and extracts data."""
    titles, descriptions, locations, companies, salaries, ratings, urls, days = scrape_indeed_data(
        search_title="Python",
        location="Remote",
        country="USA",
        results_wanted=3
    )

    assert len(titles) > 0
    assert len(descriptions) == len(titles)
    assert len(locations) == len(titles)
    assert len(companies) == len(titles)
    assert len(urls) == len(titles)
    assert all("indeed.com" in u for u in urls if u)
