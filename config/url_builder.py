import json
import os
import config.query_string_maker as qsm


class BuildUrl:
    def __init__(self, process='yes'):
        self.sort = 'sort=date'
        self.process = process

    def make_search_data(self, country_input=None, title_input=None, location_input=None,
                         salary_input=None, date_input=None, results_wanted=25, interactive=True):
        # 1. Country
        if country_input is not None:
            country = str(country_input).strip() or "USA"
        elif interactive:
            user_in = input(
                '\nEnter the country in which you want to search (e.g. USA, UK, Spain, Canada, India)\n'
                'Hit enter to default to "USA": '
            ).strip()
            country = user_in if user_in else "USA"
        else:
            country = "USA"

        base_url = 'https://www.indeed.com/jobs?'
        view_job_url = 'https://www.indeed.com/viewjob?jk='

        # 2. Job Title
        if title_input is not None:
            search_title = str(title_input).strip() or "Software Engineer"
        elif interactive:
            user_in = input('\nEnter job title (e.g. Software Engineer): ').strip()
            search_title = user_in if user_in else "Software Engineer"
        else:
            search_title = "Software Engineer"

        job_keywords = search_title.split()
        job_title = 'q=' + qsm.make_query_param(job_keywords).lower()

        # 3. Location
        if location_input is not None:
            location_raw = str(location_input).strip()
        elif interactive:
            location_raw = input(
                "\nLooking for something remote?\n"
                "\tIf yes, enter \"yes\" or \"remote\"\n"
                "\tIf not, enter your preferred location (city, state)\n"
                "\tTo omit location, hit enter: "
            ).strip()
        else:
            location_raw = ""

        if len(location_raw) < 1:
            location = None
        elif location_raw.lower() in ['yes', 'remote']:
            location = 'l=Remote'
        else:
            location = 'l=' + qsm.make_query_param(location_raw.split()).lower()

        # 4. Salary
        if salary_input is not None:
            salary_raw = str(salary_input).strip()
        elif interactive:
            salary_raw = input(
                "\nWhat's your preferred base salary? (in thousands, e.g. 80 for $80k)\n"
                "\tHit enter to omit salary: "
            ).strip()
        else:
            salary_raw = ""

        if salary_raw and salary_raw.isdigit():
            salary = qsm.make_salary_query_str(salary_raw)
        else:
            salary = None

        # 5. Date / Recency
        if date_input is not None:
            date_raw = str(date_input).strip()
        elif interactive:
            date_raw = input(
                "\nHow recent do you want the job posts? (in days, e.g. 7)\n"
                "\tHit enter to omit: "
            ).strip()
        else:
            date_raw = ""

        if date_raw and date_raw.isdigit():
            job_posted_since = 'fromage=' + date_raw
        else:
            job_posted_since = None

        # Assemble JSON config
        search_data = {
            'defaultSearch': [
                {'baseUrl': base_url},
                {'jobTitle': job_title},
                {'location': location},
                {'salary': salary},
                {'postsSince': job_posted_since},
                {'sort': self.sort},
                {'viewJobUrl': view_job_url},
                {'searchTitle': search_title},
                {'country': country},
                {'resultsWanted': results_wanted}
            ]
        }

        os.makedirs('config', exist_ok=True)
        with open('config/default_search_config.json', 'w', encoding='utf-8') as dsc:
            json.dump(search_data, dsc, ensure_ascii=False, indent=4)

        query_items = [job_title, location, salary, job_posted_since, self.sort]
        query_str = qsm.make_full_query_str(query_items)
        final_url = base_url + query_str

        return [final_url, view_job_url]
