# -*- coding: utf-8 -*-

import argparse
import sys
import os
import time
import requests
from .Paper import Paper
from .PapersFilters import filterJurnals, filter_min_date, similarStrings
from .Downloader import downloadPapers
from .Scholar import ScholarPapersInfo
from .Crossref import getPapersInfoFromDOIs
from .proxy import proxy
from .__init__ import __version__
from urllib.parse import urljoin

def checkVersion():
    try :
        print("PyPaperBot v" + __version__)
        response = requests.get('https://pypi.org/pypi/pypaperbot/json')
        latest_version = response.json()['info']['version']
        if latest_version != __version__:
            print("NEW VERSION AVAILABLE!\nUpdate with 'pip install PyPaperBot —upgrade' to get the latest features!\n")
    except :
        pass


def start(query, scholar_results, scholar_pages, dwn_dir, proxy, min_date=None, num_limit=None, num_limit_type=None,
          filter_jurnal_file=None, restrict=None, DOIs=None, SciHub_URL=None, chrome_version=None, cites=None,
          use_doi_as_filename=False, SciDB_URL=None, skip_words=None, GoogleScholar_URL="https://sc.panda985.com"):  # Add google_scholar_url parameter

    if SciDB_URL is not None and "/scidb" not in SciDB_URL:
        SciDB_URL = urljoin(SciDB_URL, "/scidb/")
        
    if GoogleScholar_URL == None:
        GoogleScholar_URL = "https://sc.panda985.com"

    to_download = []
    if DOIs is None:
        print("Query: {}".format(query))
        print("Cites: {}".format(cites))
        to_download = ScholarPapersInfo(query, scholar_pages, restrict, min_date, scholar_results, chrome_version, cites, skip_words, GoogleScholar_URL)  # Add GoogleScholar_URL parameter
    else:
        print("Downloading papers from DOIs\n")
        num = 1
        i = 0
        while i < len(DOIs):
            DOI = DOIs[i]
            print("Searching paper {} of {} with DOI {}".format(num, len(DOIs), DOI))
            papersInfo = getPapersInfoFromDOIs(DOI, restrict)
            papersInfo.use_doi_as_filename = use_doi_as_filename
            to_download.append(papersInfo)

            num += 1
            i += 1

    if restrict != 0 and to_download:
        if filter_jurnal_file is not None:
            to_download = filterJurnals(to_download, filter_jurnal_file)

        if min_date is not None:
            to_download = filter_min_date(to_download, min_date)

        if num_limit_type is not None and num_limit_type == 0:
            to_download.sort(key=lambda x: int(x.year) if x.year is not None else 0, reverse=True)

        if num_limit_type is not None and num_limit_type == 1:
            to_download.sort(key=lambda x: int(x.cites_num) if x.cites_num is not None else 0, reverse=True)

        downloadPapers(to_download, dwn_dir, num_limit, SciHub_URL, SciDB_URL)  # Add GoogleScholar_URL parameter

    Paper.generateReport(to_download, dwn_dir + "result.csv")
    Paper.generateBibtex(to_download, dwn_dir + "bibtex.bib")


def main():
    print(
        """PyPaperBot is a Python tool for downloading scientific papers using Google Scholar, Crossref and SciHub.
        -Join the telegram channel to stay updated --> https://t.me/pypaperbotdatawizards <--
        -If you like this project, you can share a cup of coffee at --> https://www.paypal.com/paypalme/ferru97 <-- :)\n""")
    # time.sleep(4)
    parser = argparse.ArgumentParser(
        description='PyPaperBot is python tool to search and dwonload scientific papers using Google Scholar, Crossref and SciHub')
    parser.add_argument('--query', type=str, default=None,
                        help='Query to make on Google Scholar or Google Scholar page link')
    parser.add_argument('--skip-words', type=str, default=None,
                        help='List of comma separated works. Papers from Scholar containing this words on title or summary will be skipped')
    parser.add_argument('--cites', type=str, default=None,
                        help='Paper ID (from scholar address bar when you search citations) if you want get only citations of that paper')
    parser.add_argument('--doi', type=str, default=None,
                        help='DOI of the paper to download (this option uses only SciHub to download)')
    parser.add_argument('--doi-file', type=str, default=None,
                        help='File .txt containing the list of paper\'s DOIs to download')
    parser.add_argument('--scholar-pages', type=str,
                        help='If given in %%d format, the number of pages to download from the beginning. '
                             'If given in %%d-%%d format, the range of pages (starting from 1) to download (the end is included). '
                             'Each page has a maximum of 10 papers (required for --query)')
    parser.add_argument('--dwn-dir', type=str, help='Directory path in which to save the results')
    parser.add_argument('--min-year', default=None, type=int, help='Minimal publication year of the paper to download')
    parser.add_argument('--max-dwn-year', default=None, type=int,
                        help='Maximum number of papers to download sorted by year')
    parser.add_argument('--max-dwn-cites', default=None, type=int,
                        help='Maximum number of papers to download sorted by number of citations')
    parser.add_argument('--journal-filter', default=None, type=str,
                        help='CSV file path of the journal filter (More info on github)')
    parser.add_argument('--restrict', default=None, type=int, choices=[0, 1],
                        help='0:Download only Bibtex - 1:Down load only papers PDF')
    parser.add_argument('--scihub-mirror', default=None, type=str,
                        help='Mirror for downloading papers from sci-hub. If not set, it is selected automatically')
    parser.add_argument('--annas-archive-mirror', default=None, type=str,
                        help='Mirror for downloading papers from Annas Archive (SciDB). If not set, https://annas-archive.se is used')
    parser.add_argument('--scholar-results', default=10, type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        help='Downloads the first x results for each scholar page(default/max=10)')
    parser.add_argument('--proxy', nargs='+', default=[],
                        help='Use proxychains, provide a seperated list of proxies to use.Please specify the argument al the end')
    parser.add_argument('--single-proxy', type=str, default=None,
                        help='Use a single proxy. Recommended if using --proxy gives errors')
    parser.add_argument('--selenium-chrome-version', type=int, default=None,
                        help='First three digits of the chrome version installed on your machine. If provided, selenium will be used for scholar search. It helps avoid bot detection but chrome must be installed.')
    parser.add_argument('--use-doi-as-filename', action='store_true', default=False,
                        help='Use DOIs as output file names')
    parser.add_argument('--scholar-mirror', type=str, default="https://sc.panda985.com",  # Add this line
                        help='Mirror for downloading papers from Google Scholar. If not set, https://sc.panda985.com is used')
    args = parser.parse_args()

    if args.single_proxy is not None:
        os.environ['http_proxy'] = args.single_proxy
        os.environ['HTTP_PROXY'] = args.single_proxy
        os.environ['https_proxy'] = args.single_proxy
        os.environ['HTTPS_PROXY'] = args.single_proxy
        print("Using proxy: ", args.single_proxy)
    else:
        pchain = []
        pchain = args.proxy
        proxy(pchain)

    if args.query is None and args.doi_file is None and args.doi is None and args.cites is None:
        print("Error, provide at least one of the following arguments: --query, --file, or --cites")
        sys.exit()

    if (args.query is not None and args.doi_file is not None) or (args.query is not None and args.doi is not None) or (
            args.doi is not None and args.doi_file is not None):
        print("Error: Only one option between '--query', '--doi-file' and '--doi' can be used")
        sys.exit()

    if args.dwn_dir is None:
        print("Error, provide the directory path in which to save the results")
        sys.exit()

    if args.scholar_results != 10 and args.scholar_pages != 1:
        print("Scholar results best applied along with --scholar-pages=1")

    dwn_dir = args.dwn_dir.replace('\\', '/')
    if dwn_dir[-1] != '/':
        dwn_dir += "/"
    if not os.path.exists(dwn_dir):
        os.makedirs(dwn_dir, exist_ok=True)

    if args.max_dwn_year is not None and args.max_dwn_cites is not None:
        print("Error: Only one option between '--max-dwn-year' and '--max-dwn-cites' can be used ")
        sys.exit()

    if args.query is not None or args.cites is not None:
        if args.scholar_pages:
            try:
                split = args.scholar_pages.split('-')
                if len(split) == 1:
                    scholar_pages = range(1, int(split[0]) + 1)
                elif len(split) == 2:
                    start_page, end_page = [int(x) for x in split]
                    scholar_pages = range(start_page, end_page + 1)
                else:
                    raise ValueError
            except Exception:
                print(
                    r"Error: Invalid format for --scholar-pages option. Expected: %d or %d-%d, got: " + args.scholar_pages)
                sys.exit()
        else:
            print("Error: with --query provide also --scholar-pages")
            sys.exit()
    else:
        scholar_pages = 0

    DOIs = None
    if args.doi_file is not None:
        DOIs = []
        f = args.doi_file.replace('\\', '/')
        with open(f) as file_in:
            for line in file_in:
                if line[-1] == '\n':
                    DOIs.append(line[:-1])
                else:
                    DOIs.append(line)

    if args.doi is not None:
        DOIs = [args.doi]

    max_dwn = None
    max_dwn_type = None
    if args.max_dwn_year is not None:
        max_dwn = args.max_dwn_year
        max_dwn_type = 0
    if args.max_dwn_cites is not None:
        max_dwn = args.max_dwn_cites
        max_dwn_type = 1


    start(args.query, args.scholar_results, scholar_pages, dwn_dir, proxy, args.min_year , max_dwn, max_dwn_type ,
          args.journal_filter, args.restrict, DOIs, args.scihub_mirror, args.selenium_chrome_version, args.cites,
          args.use_doi_as_filename, args.annas_archive_mirror, args.skip_words, args.scholar_mirror)  # Add args.scholar_mirror parameter   

if __name__ == "__main__":
    checkVersion()
    main()
    print(
        """\nWork completed!
        -Join the telegram channel to stay updated --> https://t.me/pypaperbotdatawizards <--
        -If you like this project, you can share a cup of coffee at --> https://www.paypal.com/paypalme/ferru97 <-- :)\n""")
