import json
import os
import config.query_string_maker as qsm


def load_terms_list(dict_list):
    terms_list = []
    if not dict_list:
        return terms_list
    for item in dict_list:
        if isinstance(item, dict):
            key = list(item.keys())[0]
            terms_list.append(item.get(key))
        elif isinstance(item, str):
            terms_list.append(item)
    return terms_list


def open_json_matching_data(match_on, matching_type):
    config_file = 'config/matching_terms.json'
    if not os.path.exists(config_file):
        return []
    try:
        with open(config_file, 'r', encoding='utf-8') as mt:
            data = json.load(mt)
            return data.get(match_on, {}).get(matching_type, [])
    except Exception:
        return []


def get_search_params():
    """Extracts structured search parameters from config/default_search_config.json."""
    config_file = 'config/default_search_config.json'
    defaults = {
        'search_title': 'Spanish teacher',
        'location': 'New York',
        'country': 'USA',
        'salary': None,
        'hours_old': None,
        'results_wanted': 25,
        'sort': 'date',
        'base_url': 'https://www.indeed.com/jobs?',
        'view_job_url': 'https://www.indeed.com/viewjob?jk='
    }

    if not os.path.exists(config_file):
        return defaults

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if stored as list under defaultSearch
        search_list = data.get('defaultSearch', [])
        for item in search_list:
            if not isinstance(item, dict):
                continue
            for k, v in item.items():
                if k == 'searchTitle' and v:
                    defaults['search_title'] = str(v).strip()
                elif k == 'jobTitle' and v:
                    # fallback if searchTitle is missing
                    if not defaults['search_title']:
                        defaults['search_title'] = str(v).replace('q=', '').replace('+', ' ').strip()
                elif k == 'location' and v:
                    defaults['location'] = str(v).replace('l=', '').replace('+', ' ').strip()
                elif k == 'country' and v:
                    defaults['country'] = str(v).strip()
                elif k == 'salary' and v:
                    defaults['salary'] = v
                elif k == 'postsSince' and v:
                    # e.g. "fromage=3"
                    val_str = str(v).replace('fromage=', '').strip()
                    if val_str.isdigit():
                        defaults['hours_old'] = int(val_str) * 24
                elif k == 'resultsWanted' and v:
                    defaults['results_wanted'] = int(v)
                elif k == 'baseUrl' and v:
                    defaults['base_url'] = v
                elif k == 'viewJobUrl' and v:
                    defaults['view_job_url'] = v
    except Exception as e:
        print(f"Warning reading search config: {e}")

    return defaults


# Initial module-level variables for backward compatibility
params = get_search_params()
base_url = params['base_url']
view_job_url = params['view_job_url']
search_title = params['search_title']
final_url = f"{base_url}q={search_title.replace(' ', '+')}&l={str(params['location']).replace(' ', '+')}"

# Matching terms
selected_title_list = open_json_matching_data('titleMatching', 'select')
title_selected_terms = load_terms_list(selected_title_list)

discarded_title_list = open_json_matching_data('titleMatching', 'discard')
title_discarded_terms = load_terms_list(discarded_title_list)

selected_description_list = open_json_matching_data('descriptionMatching', 'select')
description_selected_terms = load_terms_list(selected_description_list)

discarded_description_list = open_json_matching_data('descriptionMatching', 'discard')
description_discarded_terms = load_terms_list(discarded_description_list)
