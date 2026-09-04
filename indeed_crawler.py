import os
import sys
import argparse
import pandas as pd
import indeed_jobs_crawler.data_matcher as dm
import config.config_setup as cs
import config.url_builder as ub
import config.set_matching_data as smd
import indeed_jobs_crawler.info_scraper as scrape


def parse_args():
    parser = argparse.ArgumentParser(description="Indeed Jobs Scraper - Modernized Job Search Automation")
    parser.add_argument("-y", "--yes", action="store_true", help="Use default search configuration without prompting")
    parser.add_argument("-s", "--search", type=str, default=None, help="Job title / search query (e.g. 'Python Developer')")
    parser.add_argument("-l", "--location", type=str, default=None, help="Location or 'Remote'")
    parser.add_argument("-c", "--country", type=str, default=None, help="Country (e.g. 'USA', 'UK', 'Spain', 'Canada')")
    parser.add_argument("-n", "--results", type=int, default=None, help="Number of job results wanted (e.g. 25)")
    parser.add_argument("--days", type=int, default=None, help="Filter jobs posted within the last N days")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 65)
    print("           INDEED JOBS SCRAPER (Modernized)")
    print("=" * 65)

    # 1. Determine Search Parameters
    if args.search or args.location or args.country or args.results:
        # CLI argument mode
        search_title = args.search or "Python Developer"
        location = args.location
        country = args.country or "USA"
        results_wanted = args.results or 25
        hours_old = (args.days * 24) if args.days else None

        # Build and persist configuration
        builder = ub.BuildUrl()
        builder.make_search_data(
            country_input=country,
            title_input=search_title,
            location_input=location,
            date_input=args.days,
            results_wanted=results_wanted,
            interactive=False
        )
    else:
        # Interactive mode or --yes flag
        if args.yes:
            config_type = 'yes'
        else:
            try:
                config_type = input('\nDo you wish to scrape Indeed with the default search config? (yes/no): ').strip().lower()
                while config_type not in ['yes', 'no']:
                    config_type = input('Please enter "yes" or "no": ').strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nDefaulting to 'yes' config.")
                config_type = 'yes'

        url_builder = ub.BuildUrl(config_type)
        if config_type == 'no':
            url_builder.make_search_data()
            smd.MatchingData.make_matching_data()

        # Reload updated configuration
        search_params = cs.get_search_params()
        search_title = search_params.get('search_title', 'Spanish teacher')
        location = search_params.get('location', 'New York')
        country = search_params.get('country', 'USA')
        results_wanted = search_params.get('results_wanted', 25)
        hours_old = search_params.get('hours_old')

    print(f"\n[Config] Active Search Settings:")
    print(f"  - Title:   {search_title}")
    print(f"  - Location:{location or 'Any'}")
    print(f"  - Country: {country}")
    print(f"  - Limit:   {results_wanted}")
    if hours_old:
        print(f"  - Recency: within {hours_old // 24} days")

    # 2. Start Scraping
    print("\n" + "=" * 65)
    print("                    START CRAWLING")
    print("=" * 65)

    job_titles, descriptions, jobs_locations, company_names, salaries, jobs_ratings, apply_urls, days = (
        scrape.scrape_indeed_data(
            search_title=search_title,
            location=location,
            country=country,
            results_wanted=results_wanted,
            hours_old=hours_old
        )
    )

    if not job_titles:
        print("\nNo jobs were retrieved. Please check your search parameters and try again.\n")
        return

    # 3. Filter Results via Matching Keywords
    # Reload matching terms from config
    title_select = cs.load_terms_list(cs.open_json_matching_data('titleMatching', 'select'))
    title_disc = cs.load_terms_list(cs.open_json_matching_data('titleMatching', 'discard'))
    desc_select = cs.load_terms_list(cs.open_json_matching_data('descriptionMatching', 'select'))
    desc_disc = cs.load_terms_list(cs.open_json_matching_data('descriptionMatching', 'discard'))

    data_match = dm.MatchJob(
        job_titles, descriptions, jobs_locations, company_names, salaries, jobs_ratings, apply_urls,
        days, title_disc, desc_disc, title_select, desc_select
    )

    (
        final_titles, final_descriptions, final_locations, final_companies, final_salaries,
        final_ratings, final_urls, final_days
    ) = data_match.get_targeted_jobs_data()

    print(f"[Matching] Total raw jobs: {len(job_titles)} | Jobs after keyword filtering: {len(final_titles)}")

    if not final_titles:
        print("All jobs were filtered out by your keyword matching rules.")
        return

    # 4. Save to CSV
    os.makedirs('results', exist_ok=True)
    jobs_df = pd.DataFrame({
        "Job Title": final_titles,
        "Location": final_locations,
        "Salary": final_salaries,
        "Company": final_companies,
        "Job Rating": final_ratings,
        "Post time": final_days,
        "Description": final_descriptions,
        "Apply url": final_urls
    })

    file_id = search_title.lower().replace(' ', '_').replace('/', '_')
    csv_path = os.path.join('results', f'job_search_{file_id}.csv')
    jobs_df.to_csv(csv_path, index=False, encoding='utf-8')

    # 5. Output Summary
    print("\n" + "=" * 65)
    print("                     RESULTS SUMMARY")
    print("=" * 65)
    preview_count = min(5, len(final_titles))
    for i in range(preview_count):
        print(f"\n[{i + 1}] {final_titles[i]}")
        print(f"    Company:  {final_companies[i]}")
        print(f"    Location: {final_locations[i]}")
        print(f"    Salary:   {final_salaries[i]}")
        print(f"    Posted:   {final_days[i]}")
        print(f"    URL:      {final_urls[i]}")

    print("\n" + "=" * 65)
    print(f"Congratulations! You've successfully scraped Indeed.")
    print(f"Exported {len(final_titles)} jobs to: {csv_path}")
    print("=" * 65 + "\n")


if __name__ == '__main__':
    main()
