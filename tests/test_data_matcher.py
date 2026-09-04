import pytest
from indeed_jobs_crawler.data_matcher import MatchJob


def test_match_job_no_filters():
    titles = ["Software Engineer", "Data Scientist"]
    descriptions = ["Build python apps", "Analyze big data"]
    locations = ["Remote", "New York"]
    companies = ["Acme", "Beta"]
    salaries = ["$100k", "$120k"]
    ratings = [4.5, 4.0]
    urls = ["http://a.com", "http://b.com"]
    days = ["today", "1 day ago"]

    matcher = MatchJob(
        titles, descriptions, locations, companies, salaries, ratings, urls, days,
        discarded_title_terms=[], discarded_desc_terms=[],
        selected_title_terms=[], selected_description_terms=[]
    )
    t, d, l, c, s, r, u, dy = matcher.get_targeted_jobs_data()
    assert len(t) == 2
    assert t == titles


def test_match_job_selected_title():
    titles = ["Senior Software Engineer", "Junior Data Scientist", "Senior Product Manager"]
    descriptions = ["Python code", "Data analysis", "Product strategy"]
    locations = ["Remote", "NY", "SF"]
    companies = ["A", "B", "C"]
    salaries = ["$100k", "$80k", "$120k"]
    ratings = [4.0, 3.5, 4.2]
    urls = ["u1", "u2", "u3"]
    days = ["today", "today", "today"]

    matcher = MatchJob(
        titles, descriptions, locations, companies, salaries, ratings, urls, days,
        discarded_title_terms=[], discarded_desc_terms=[],
        selected_title_terms=["engineer"], selected_description_terms=[]
    )
    t, d, l, c, s, r, u, dy = matcher.get_targeted_jobs_data()
    assert len(t) == 1
    assert t[0] == "Senior Software Engineer"
    assert c[0] == "A"


def test_match_job_discard_title():
    titles = ["Senior Software Engineer", "Junior Software Engineer", "Lead Engineer"]
    descriptions = ["Desc1", "Desc2", "Desc3"]
    locations = ["Remote", "Remote", "Remote"]
    companies = ["A", "B", "C"]
    salaries = ["$100k", "$70k", "$150k"]
    ratings = [4.0, 4.0, 4.0]
    urls = ["u1", "u2", "u3"]
    days = ["today", "today", "today"]

    matcher = MatchJob(
        titles, descriptions, locations, companies, salaries, ratings, urls, days,
        discarded_title_terms=["senior", "lead"], discarded_desc_terms=[],
        selected_title_terms=[], selected_description_terms=[]
    )
    t, d, l, c, s, r, u, dy = matcher.get_targeted_jobs_data()
    assert len(t) == 1
    assert t[0] == "Junior Software Engineer"


def test_match_job_duplicate_titles_bug_fix():
    """Verify that duplicate job titles at different companies/locations are both preserved."""
    titles = ["Spanish Teacher", "Spanish Teacher"]
    descriptions = ["School in Queens", "School in Brooklyn"]
    locations = ["Queens, NY", "Brooklyn, NY"]
    companies = ["School A", "School B"]
    salaries = ["$60k", "$65k"]
    ratings = [4.0, 4.5]
    urls = ["url_a", "url_b"]
    days = ["today", "1 day ago"]

    matcher = MatchJob(
        titles, descriptions, locations, companies, salaries, ratings, urls, days,
        discarded_title_terms=[], discarded_desc_terms=[],
        selected_title_terms=["teacher"], selected_description_terms=[]
    )
    t, d, l, c, s, r, u, dy = matcher.get_targeted_jobs_data()
    assert len(t) == 2
    assert c == ["School A", "School B"]
    assert l == ["Queens, NY", "Brooklyn, NY"]
    assert u == ["url_a", "url_b"]


def test_match_job_description_selection_and_discard():
    titles = ["Job 1", "Job 2", "Job 3"]
    descriptions = ["Needs Python and Django", "Needs Java and Spring", "Needs Python and Unpaid Internship"]
    locations = ["Loc1", "Loc2", "Loc3"]
    companies = ["Comp1", "Comp2", "Comp3"]
    salaries = ["Not shown", "Not shown", "Not shown"]
    ratings = [None, None, None]
    urls = ["u1", "u2", "u3"]
    days = ["today", "today", "today"]

    matcher = MatchJob(
        titles, descriptions, locations, companies, salaries, ratings, urls, days,
        discarded_title_terms=[], discarded_desc_terms=["unpaid"],
        selected_title_terms=[], selected_description_terms=["python"]
    )
    t, d, l, c, s, r, u, dy = matcher.get_targeted_jobs_data()
    assert len(t) == 1
    assert t[0] == "Job 1"
    assert c[0] == "Comp1"
