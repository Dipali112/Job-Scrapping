import os
import json
import pytest
import config.config_setup as cs
import config.url_builder as ub
import config.set_matching_data as smd


@pytest.fixture(autouse=True)
def preserve_config_files():
    """Preserves and restores config files so tests don't leave modified state."""
    search_cfg = 'config/default_search_config.json'
    matching_cfg = 'config/matching_terms.json'

    old_search = None
    old_matching = None
    if os.path.exists(search_cfg):
        with open(search_cfg, 'r', encoding='utf-8') as f:
            old_search = f.read()
    if os.path.exists(matching_cfg):
        with open(matching_cfg, 'r', encoding='utf-8') as f:
            old_matching = f.read()

    yield

    if old_search is not None:
        with open(search_cfg, 'w', encoding='utf-8') as f:
            f.write(old_search)
    if old_matching is not None:
        with open(matching_cfg, 'w', encoding='utf-8') as f:
            f.write(old_matching)


def test_load_terms_list():
    raw_list = [{'term': 'python'}, {'term': 'remote'}, 'fastapi']
    terms = cs.load_terms_list(raw_list)
    assert terms == ['python', 'remote', 'fastapi']
    assert cs.load_terms_list([]) == []
    assert cs.load_terms_list(None) == []


def test_build_url_programmatic():
    builder = ub.BuildUrl()
    urls = builder.make_search_data(
        country_input="USA",
        title_input="Backend Engineer",
        location_input="San Francisco",
        salary_input="150",
        date_input="14",
        results_wanted=30,
        interactive=False
    )
    assert len(urls) == 2
    assert "https://www.indeed.com/jobs?" in urls[0]
    assert "q=backend+engineer" in urls[0]
    assert "l=san+francisco" in urls[0]

    params = cs.get_search_params()
    assert params['search_title'] == "Backend Engineer"
    assert params['location'] == "san francisco"
    assert params['country'] == "USA"
    assert params['results_wanted'] == 30
    assert params['hours_old'] == 14 * 24


def test_matching_data_programmatic():
    smd.MatchingData.make_matching_data(
        title_select=["senior", "lead"],
        title_discard=["junior", "intern"],
        desc_select=["python", "cloud"],
        desc_discard=["unpaid", "volunteer"]
    )
    
    with open('config/matching_terms.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert [item['term'] for item in data['titleMatching']['select']] == ["senior", "lead"]
    assert [item['term'] for item in data['titleMatching']['discard']] == ["junior", "intern"]
    assert [item['term'] for item in data['descriptionMatching']['select']] == ["python", "cloud"]
    assert [item['term'] for item in data['descriptionMatching']['discard']] == ["unpaid", "volunteer"]
