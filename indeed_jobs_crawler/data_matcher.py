# jobs which titles OR descriptions have selected items shall be kept


class MatchJob:
    def __init__(self, titles, descriptions, locations, companies, salaries, ratings, urls,
                 days, discarded_title_terms, discarded_desc_terms, selected_title_terms, selected_description_terms):

        self.keep_titles = []
        self.keep_description = []
        self.keep_locations = []
        self.keep_companies = []
        self.keep_salaries = []
        self.keep_ratings = []
        self.keep_urls = []
        self.keep_days = []

        self.titles = titles or []
        self.descriptions = descriptions or []
        self.locations = locations or []
        self.companies = companies or []
        self.salaries = salaries or []
        self.ratings = ratings or []
        self.urls = urls or []
        self.days = days or []

        # Filter out empty strings or None and lowercase
        self.discarded_title_items = [str(t).lower().strip() for t in (discarded_title_terms or []) if str(t).strip()]
        self.discarded_desc_terms = [str(t).lower().strip() for t in (discarded_desc_terms or []) if str(t).strip()]
        self.selected_title_terms = [str(t).lower().strip() for t in (selected_title_terms or []) if str(t).strip()]
        self.selected_description_terms = [str(t).lower().strip() for t in (selected_description_terms or []) if str(t).strip()]

    def keep_job_data(self, i):
        self.keep_titles.append(self.titles[i])
        self.keep_description.append(self.descriptions[i])
        self.keep_locations.append(self.locations[i])
        self.keep_companies.append(self.companies[i])
        self.keep_salaries.append(self.salaries[i])
        self.keep_ratings.append(self.ratings[i])
        self.keep_urls.append(self.urls[i])
        self.keep_days.append(self.days[i])

    def check_title_has_selected_terms(self, title):
        if self.selected_title_terms:
            return any(term in title.lower() for term in self.selected_title_terms)
        return False

    def check_description_has_selected_terms(self, description):
        if self.selected_description_terms:
            return any(term in description.lower() for term in self.selected_description_terms)
        return False

    def check_title_has_discarded_terms(self, title):
        if self.discarded_title_items:
            return any(term in title.lower() for term in self.discarded_title_items)
        return False

    def check_description_has_discarded_terms(self, description):
        if self.discarded_desc_terms:
            return any(term in description.lower() for term in self.discarded_desc_terms)
        return False

    def matching(self):
        has_selected = bool(self.selected_title_terms or self.selected_description_terms)

        for idx, (t, d) in enumerate(zip(self.titles, self.descriptions)):
            t_str = str(t) if t else ""
            d_str = str(d) if d else ""

            # Check inclusion rules if specified
            if has_selected:
                title_match = self.check_title_has_selected_terms(t_str)
                desc_match = self.check_description_has_selected_terms(d_str)
                if not (title_match or desc_match):
                    continue

            # Check exclusion rules
            if self.check_title_has_discarded_terms(t_str):
                continue
            if self.check_description_has_discarded_terms(d_str):
                continue

            self.keep_job_data(idx)

    def get_targeted_jobs_data(self):
        if self.selected_title_terms or self.selected_description_terms or self.discarded_title_items or self.discarded_desc_terms:
            self.matching()
            return self.keep_titles, self.keep_description, self.keep_locations, self.keep_companies,\
                self.keep_salaries, self.keep_ratings, self.keep_urls, self.keep_days
        else:
            return self.titles, self.descriptions, self.locations, self.companies, self.salaries, self.ratings, \
                   self.urls, self.days
