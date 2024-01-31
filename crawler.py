import logging
import re
from urllib.parse import urlparse, urljoin
from lxml import html, etree

logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier, corpus):
        self.frontier = frontier
        self.corpus = corpus

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.corpus.fetch_url(url)

            for next_link in self.extract_next_links(url_data):
                if self.is_valid(next_link):
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)

    @staticmethod
    def is_absolute_url(url):
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme and parsed_url.netloc)

    def extract_next_links(self, url_data: dict):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """
        if url_data['content'] is None or not url_data['content'].strip() or url_data['http_code'] != 200:
            return []

        content = url_data['content']
        base_url = url_data['final_url'] if url_data['is_redirected'] else url_data['url']

        try:
            tree = html.fromstring(content)
        except etree.ParserError:
            return []

        links = []
        for element in tree.xpath('//a/@href'):
            link = element.strip()
            if link:
                absolute_url = urljoin(base_url, link)
                links.append(absolute_url)
        return links

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        try:
            if ".ics.uci.edu" not in parsed.hostname:
                return False

            if re.search(r"\.(css|js|bmp|gif|jpeg|jpg|ico|png|tiff|mid|mp2|mp3|mp4"
                         r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                         r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1"
                         r"|thmx|mso|arff|rtf|jar|csv"
                         r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
                return False
        except TypeError:
            print("TypeError for ", parsed)
            return False

        if len(url) > 200:
            return False

        path_segments = parsed.path.split('/')
        if any(path_segments.count(segment) > 1 for segment in path_segments):
            return False

        if len(parsed.query.split('&')) > 10:
            return False

        return True
