import json
import os


class MatchingData:

    @staticmethod
    def make_matching_data(title_select=None, title_discard=None, desc_select=None, desc_discard=None):
        """
        Sets keyword inclusion and exclusion criteria for title and description.
        If arguments are provided, uses them; otherwise prompts interactively.
        """
        title_selected_keywords = []
        title_discarded_keywords = []
        description_selected_keywords = []
        description_discarded_keywords = []

        if title_select is not None:
            title_selected_keywords = [str(t).lower().strip() for t in title_select if str(t).strip()]
        else:
            print("\nTERMS MATCHING: Let's refine your search keywords!")
            print("Specify terms you want or do not want in job titles and descriptions.")
            while True:
                term = input('\nEnter a term you WANT in the job title (hit enter to finish): ').strip().lower()
                if not term:
                    break
                title_selected_keywords.append(term)

        if title_discard is not None:
            title_discarded_keywords = [str(t).lower().strip() for t in title_discard if str(t).strip()]
        else:
            while True:
                term = input('\nEnter a term you DO NOT want in the job title (hit enter to finish): ').strip().lower()
                if not term:
                    break
                title_discarded_keywords.append(term)

        if desc_select is not None:
            description_selected_keywords = [str(t).lower().strip() for t in desc_select if str(t).strip()]
        else:
            while True:
                term = input('\nEnter a term you WANT in the job description (hit enter to finish): ').strip().lower()
                if not term:
                    break
                description_selected_keywords.append(term)

        if desc_discard is not None:
            description_discarded_keywords = [str(t).lower().strip() for t in desc_discard if str(t).strip()]
        else:
            while True:
                term = input('\nEnter a term you DO NOT want in the job description (hit enter to finish): ').strip().lower()
                if not term:
                    break
                description_discarded_keywords.append(term)

        matching_data = {
            'titleMatching': {
                'select': [{'term': t} for t in title_selected_keywords],
                'discard': [{'term': t} for t in title_discarded_keywords]
            },
            'descriptionMatching': {
                'select': [{'term': t} for t in description_selected_keywords],
                'discard': [{'term': t} for t in description_discarded_keywords]
            }
        }

        os.makedirs('config', exist_ok=True)
        with open('config/matching_terms.json', 'w', encoding='utf-8') as mt:
            json.dump(matching_data, mt, ensure_ascii=False, indent=4)

        return matching_data
