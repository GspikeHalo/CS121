import logging
import re
from urllib.parse import urlparse, urljoin, parse_qs
from lxml import html, etree
from collections import defaultdict

logger = logging.getLogger(__name__)


class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier, corpus):
        self.frontier = frontier
        self.corpus = corpus
        self.counter = AnalyticsContainer()
        self.param_value_history = defaultdict(lambda: defaultdict(list))

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            out_link_count = 0
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched,
                        len(self.frontier))
            url_data = self.corpus.fetch_url(url)

            for next_link in self.extract_next_links(url_data):
                if self.is_valid(next_link):
                    if self.corpus.get_file_name(next_link) is not None:
                        self.frontier.add_url(next_link)
                        out_link_count += 1

            url = url_data['final_url'] if url_data['is_redirected'] else url_data['url']
            subdomain = self.extract_subdomain(url)
            self.counter.update_download_url(url, out_link_count)
            self.counter.update_longest_page(url, self.count_page_length(url_data))
            self.counter.update_subdomain(subdomain)
        self.counter.get_report()

    @staticmethod
    def extract_subdomain(url):
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        parts = hostname.split('.')
        if len(parts) > 2:
            return '.'.join(parts[:-2])
        else:
            return ""

    """helper function"""

    def is_increasing_sequence(self, base_url, param, value):
        try:
            value = int(value)  # check if value is a number
        except ValueError:
            # if not a number just stop and return false
            return False

        history = self.param_value_history[base_url][param]

        if not history or value > history[-1]:
            history.append(value)
            if len(history) > 3:  # if this query happen more than 3 times, and end with a number
                # we check if this number is increasing
                return all(x < y for x, y in zip(history, history[1:]))
        else:
            # if value is not increasing, clear the history
            self.param_value_history[base_url][param] = [value]

        return False

    def count_page_length(self, url_data: dict):
        if url_data['content'] is None or not url_data['content'].strip() or url_data['http_code'] != 200:
            return 0
        content = url_data["content"]

        try:
            tree = html.fromstring(content)
        except etree.ParserError:
            return 0

        text = tree.text_content()
        return self.counter.count_page_length(text)

    def extract_next_links(self, url_data: dict):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """
        # check if "content" in url_data dictionary is empty, contains only spaces, or HTTP status code other than 200
        if url_data['content'] is None or not url_data['content'].strip() or url_data['http_code'] != 200:
            return []

        # if the content exists and the status code is 200, store the content in the variable
        content = url_data['content']

        # choose the base URL based on redirect or not
        base_url = url_data['final_url'] if url_data['is_redirected'] else url_data['url']

        try:
            # try parsing a html tree from content
            tree = html.fromstring(content)
        except etree.ParserError:  # import program robustness
            return []

        links = []
        # Iterate over the href attribute of all <a> tags
        for element in tree.xpath('//a/@href'):
            link = element.strip()
            if link:
                absolute_url = urljoin(base_url, link)  # Convert relative links to absolute links
                links.append(absolute_url)
        return links

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        # Initialize valid flag as True. It will be set to False if any invalidating condition is met.
        valid = True
        # Parse the URL into components.
        parsed = urlparse(url)
        # Retrieve the history of detected traps to avoid revisiting them.
        trap_history = self.counter.get_trap()
        # If the URL is in the trap history, return False immediately.
        if url in trap_history:
            return False

        # Parse the query parameters from the URL
        params = parse_qs(parsed.query)
        # Construct base URL without query parameters.
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # Check for increasing sequence in the parameters which might indicate a trap.
        for param, values in params.items():
            for value in values:
                if self.is_increasing_sequence(base_url, param, value):
                    # Detected a potential trap based on parameter sequence.
                    return False

        # Check if the URL's scheme is either HTTP or HTTPS. Invalidate otherwise.
        if parsed.scheme not in set(["http", "https"]):
            valid = False
        try:
            # Check if the URL's hostname contains '.ics.uci.edu'. Invalidate if not.
            if ".ics.uci.edu" not in parsed.hostname:
                valid = False
            # Invalidate URLs that point to resources with certain file extensions.
            if re.search(r"\.(css|js|bmp|gif|jpeg|jpg|ico|png|tiff|mid|mp2|mp3|mp4"
                         r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                         r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1"
                         r"|thmx|mso|arff|rtf|jar|csv"
                         r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
                valid = False
        except TypeError:
            print("TypeError for ", parsed)
            valid = False

        # Invalidate URLs that are unusually long (over 200 characters).
        if len(url) > 200:
            valid = False

        # Invalidate URLs where a single path segment is repeated (a common trap pattern).
        path_segments = parsed.path.split('/')
        if any(path_segments.count(segment) > 1 for segment in path_segments):
            valid = False

        # Invalidate URLs with too many query parameters, potentially indicating a trap.
        if len(parsed.query.split('&')) > 10:
            valid = False

        # If the URL is found to be invalid, update the trap counter.
        if not valid:
            self.counter.update_trap(url)

        return valid


class AnalyticsContainer:  # container class for analytics
    def __init__(self):
        # initializes containers to track various analytics during crawling
        self._download_url = {}  # tracks the count of downloads per URL
        self._subdomain = {}  # tracks the number of URLs visited per subdomain
        self._max_out_links = {"url": None,
                               "count": 0}  # keeps the URL with the maximum out links and the count
        self._trap = set()  # a set to keep track of identified crawler traps
        self._longest_page = {"url": None,
                              "word_count": 0}  # records the longest page by word count
        self._word_count = {}  # counts occurrences of each word across all pages
        self._stopwords = self.get_stop_words()  # loads a set of stopwords to exclude from word counts

    @staticmethod
    def get_stop_words():
        # loads stopwords from a text file and returns them as a set for filtering
        content = HelperFunction.get_content("stop_words.txt")
        print(HelperFunction.tokenize(content))
        return set(HelperFunction.tokenize(content))

    def update_download_url(self, url, count) -> None:
        # updates the download count for a given URL
        # updates max out links if applicable
        if url not in self._download_url:
            self._download_url[url] = count
            self.update_max_out_links(url, count)

    def update_subdomain(self, url):
        # increments the count of URLs visited for the subdomain of the given URL
        if url not in self._subdomain:
            self._subdomain[url] = 1
        else:
            self._subdomain[url] += 1

    def update_max_out_links(self, url, count) -> None:
        # updates the record of the URL with the most out links if the current count exceeds the maximum
        if self._max_out_links["count"] < count:
            self._max_out_links["url"] = url
            self._max_out_links["count"] = count

    def update_trap(self, url):
        # adds a URL to the set of identified crawler traps
        self._trap.add(url)

    def update_longest_page(self, url, word_count):
        # updates the record of the longest page if the current page's word count exceeds the maximum
        if self._longest_page["word_count"] < word_count:
            self._longest_page["url"] = url
            self._longest_page["word_count"] = word_count

    def update_word_count(self, word):
        # updates the frequency count of a word across all crawled pages
        if word in self._word_count:
            self._word_count[word] += 1
        else:
            self._word_count[word] = 1

    def get_download_url(self):
        # returns the dictionary tracking download counts per URL
        return self._download_url

    def get_max_out_links(self):
        # returns the record of the URL with the most out links
        return self._max_out_links

    def get_trap(self):
        # returns the set of identified crawler traps
        return self._trap

    def get_longest_page(self):
        # returns the record of the longest page by word count
        return self._longest_page

    def get_word_count(self):
        # returns the dictionary of word frequencies across all crawled pages
        return self._word_count

    def count_page_length(self, content):
        # counts the number of words in the given content, excluding stopwords
        content = HelperFunction.tokenize(content)
        for word in content:
            if word not in self._stopwords:
                self.update_word_count(word)
        return len(content)


    def get_report(self):
        with open("AnalysisReport.txt", "w", encoding="UTF-8") as file:
            file.write("SubDomain:\n")
            for subdomain, num in self._subdomain.items():
                file.write(f"{subdomain}\tnum of subdomains:{num}\n")
            file.write("\nMax Out Links:\n")
            file.write(f"URL: {self._max_out_links['url']}, Count: {self._max_out_links['count']}\n")
            file.write("Download URL:\n")
            for download_url, num in self._download_url.items():
                file.write(f"{download_url}\tnum of out links:{num}\n")
            file.write("\nTraps:\n")
            for trap in self._trap:
                file.write(f"{trap}\n")
            file.write("\nLongest Page:\n")
            file.write(f"URL: {self._longest_page['url']}, Word Count: {self._longest_page['word_count']}\n")
            file.write("\n50 Most Common Word Count:\n")

            sorted_word_count = sorted(self._word_count.items(), key=lambda item: (-item[1], item[0]))
            # for i in range(50):
            #     print(f"{sorted_word_count[i][0]}\t{sorted_word_count[i][1]}")
            for i in range(min(50, len(sorted_word_count))):
                word, count = sorted_word_count[i]
                file.write(f"{word}\t{count}\n")


class HelperFunction:
    @staticmethod
    def get_content(name: str) -> str:
        """
        Reads and returns the contents of the specified file as a string.

        This function opens a file with the given name, reads its content line by line,
        and returns the entire content as a single string. Non-UTF-8 characters are replaced
        with a replacement character.

        Time Complexity: O(n)

        :param name: str, the path or name of the file to read.
        :return:str, a string of the file contents.
        """
        content = []
        try:
            if not isinstance(name, str):
                raise TypeError("Input must be a string")

            with open(name, 'r', encoding='utf-8', errors='replace') as file:
                for line in file:
                    content.append(line)

        except FileNotFoundError:
            print(f"Error: File does not exist - '{name}'")
        except PermissionError:
            print(f"Error: Permission denied when reading the file - '{name}'")
        except UnicodeDecodeError:
            print(f"Error: Unicode decode error while reading the file - '{name}'")
        except TypeError as e:
            print(f"Error: {e} - 'get_content' function expects a string input")
        except Exception as e:
            print(f"Error: An unexpected error occurred while reading the file - '{name}': {e}")

        return ''.join(content)

    @staticmethod
    def is_english_alphanumeric(c: str) -> bool:
        """
        Determines whether the given character is an English alphanumeric character.

        An English alphanumeric character is defined as any of the characters:
        a-z, A-Z, or 0-9.

        Time Complexity: O(1)

        :param c: str, a single character to be checked.
        :return:bool, True if the character is an English letter or digit, False otherwise.
        """
        try:
            if not isinstance(c, str) or len(c) != 1:
                raise TypeError("Input must be a single character")

            return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9')

        except TypeError as e:
            print(
                f"Error: {e} - 'is_english_alphanumeric' function expects a string input with length one")
            return False
        except Exception as e:
            print(f"Error: An unexpected error occurred while determine the alphanumeric: {e}")
            return False

    @staticmethod
    def tokenize(str_content: str) -> list:
        """
        Splits a string into words, where each word consists of English letters and digits.

        Each character in the string is checked to see if it's an English alphanumeric character.
        If so, it's added to the current word. If a non-alphanumeric character is encountered,
        the current word is completed and added to the words list.

        Time Complexity: O(n)

        :param str_content: str, the string to be tokenized.
        :return: list, a list of words extracted from the input string.
        """
        words = []
        try:
            if not isinstance(str_content, str):
                raise TypeError("Input must be a string")

            current_word = ''
            for c in str_content:
                if HelperFunction.is_english_alphanumeric(c):
                    current_word += c
                elif current_word:
                    words.append(current_word.lower())
                    current_word = ''
            if current_word:
                words.append(current_word.lower())

        except TypeError as e:
            print(f"Error: {e} - 'tokenize' function expects a string input")
        except Exception as e:
            print(f"Error: An unexpected error occurred while tokenize: {e}")

        return words

    @staticmethod
    def sort_frequency(words_frequency: dict) -> list[tuple]:
        """
        Sorts the given word frequency dictionary first by frequency in descending order
        and then by word in alphabetical order.

        The function uses Python's built-in sorted function to sort the dictionary items,
        which are word-frequency pairs, based on a custom sorting key.

        Time Complexity: O(nlog(n))

        :param words_frequency: dict, a dictionary where keys are words and values are their frequencies.
        :return: list[tuple], a sorted list of tuples, where each tuple is a word-frequency pair.
        """
        try:
            if not isinstance(words_frequency, dict):
                raise TypeError("Input must be a dictionary")

            return sorted(words_frequency.items(), key=lambda item: (-item[1], item[0]))

        except TypeError as e:
            print(f"Error: {e} - 'sort_frequency' function expects a dictionary input")
        except Exception as e:
            print(f"Error: An unexpected error occurred while sort frequency: {e}")

        return []
