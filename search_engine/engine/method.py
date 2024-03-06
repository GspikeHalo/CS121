#  .search_engine/engine/method.py

import datetime
import math
import nltk
import json
import numpy as np
from lxml import html
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict


nltk.download('punkt')  # for tokenize
nltk.download('stopwords')  # for stop words
nltk.download('wordnet')  # for lemmatizer


class Method:
    @staticmethod
    def check_time_difference(prev_time_str: str, update_time: int) -> bool:
        """
        Checks if the difference between a previous time and the current time is within a specified limit.

        :param prev_time_str: The previous time as a string in "YYYY-MM-DD" format.
        :param update_time: The maximum number of days allowed between the current date and the previous time.
        :return: True if the time difference is within the specified limit, False otherwise.
        """
        prev_time = datetime.datetime.strptime(prev_time_str, "%Y-%m-%d").date()
        current_date = datetime.datetime.now().date()
        time_difference = abs((current_date - prev_time).days)
        return time_difference <= update_time

    @staticmethod
    def check_num_difference(num01: str | int, num02: str | int) -> bool:
        """
       Checks if two numbers are equal, regardless of whether they're provided as strings or integers.

        :param num01: The first number, can be a string or an integer。
        :param num02: The second number, can be a string or an integer。
        :return: True if the numbers are equal, False otherwise.
        """
        return int(num01) == int(num02)

    @staticmethod
    def preprocess_text(text: str) -> list[str]:
        """
        Preprocesses a text string by tokenizing, removing stopwords, and lemmatizing the words.

        :param text: The text to preprocess.
        :return: A list of preprocessed words.
        """
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        words = word_tokenize(text)
        filtered_words = [lemmatizer.lemmatize(word.lower()) for word in words if
                          word.lower() not in stop_words and word.isalpha()]
        return filtered_words

    @staticmethod
    def calculate_token_weight(html_content: bytes) -> dict:
        """
        Calculates the weight and position of tokens within given HTML content.

        :param html_content: The HTML content as bytes.
        :return: A dictionary with tokens as keys and their weights and positions as values.
        """
        try:
            tree = html.fromstring(html_content)
            token_weights = defaultdict(lambda: {'weight': 0, 'positions': []})
            position_counter = 0

            text_content = tree.text_content()
            tokens = word_tokenize(text_content)
            for token in tokens:
                normalized_token = token.lower()
                token_weights[normalized_token]['weight'] += 1
                token_weights[normalized_token]['positions'].append(position_counter)
                position_counter += 1

            tag_weights = {
                'title': 2.5,
                'h1': 2, 'h2': 1.5, 'h3': 1, 'h4': 0.5, 'h5': 0.5, 'h6': 0.5,
                'b': 1.5, 'strong': 1.5
            }

            for tag, weight in tag_weights.items():
                for element in tree.findall('.//{}'.format(tag)):
                    tokens = word_tokenize(element.text_content())
                    for token in tokens:
                        normalized_token = token.lower()
                        token_weights[normalized_token]['weight'] += weight
                        token_weights[normalized_token]['positions'].append(position_counter)
                        position_counter += 1

            # 处理段落的第一句
            for element in tree.findall('.//p'):
                sentences = sent_tokenize(element.text_content())
                if sentences:
                    first_sentence_tokens = word_tokenize(sentences[0])
                    for token in first_sentence_tokens:
                        token_weights[token.lower()]['weight'] += 1

            stop_words = set(stopwords.words('english'))
            lemmatizer = WordNetLemmatizer()
            filtered_token_positions = {}
            for token, info in token_weights.items():
                if token not in stop_words and token.isalpha():
                    lemmatized_token = lemmatizer.lemmatize(token)
                    if lemmatized_token not in filtered_token_positions:
                        filtered_token_positions[lemmatized_token] = {'weight': info['weight'],
                                                                      'positions': info['positions']}
                    else:
                        filtered_token_positions[lemmatized_token]['weight'] += info['weight']
                        filtered_token_positions[lemmatized_token]['positions'].extend(info['positions'])

            return filtered_token_positions
        except Exception as e:
            print(e)
            return {}

    @staticmethod
    def get_html_general_info(content: bytes) -> tuple:
        """
        Extracts general information from HTML content, such as title, first sentence, and total content length.

        :param content: The HTML content as bytes.
        :return: A tuple containing the title, first sentence, and len of the processed content.
        """
        try:
            tree = html.fromstring(content)
            title = tree.findtext('.//title')
            text_nodes = tree.xpath('//body//text()')
            full_text = ' '.join([text.strip() for text in text_nodes if text.strip()])
            words = full_text.split()
            first_sentence = words[:20]
            first_sentence = ' '.join(first_sentence)

            text = " ".join(tree.xpath('//text()'))
            total_content = Method.preprocess_text(text)
            return title, first_sentence, len(total_content)
        except Exception as e:
            print(e)
            return None, None, None

    @staticmethod
    def get_folder_num_and_file_num(doc_id: str) -> tuple:
        """
        Splits a document ID into folder and file numbers.

        :param doc_id: The document ID in the format "folder_name/file_name".
        :return: A tuple containing the folder name and file name.
        """
        folder_name, file_name = doc_id.split("/")
        return folder_name, file_name

    @staticmethod
    def calculate_tf_idf(f_td, total_words_in_d, n, n_t):
        """
        Calculates the TF-IDF score for a term.

        :param f_td: The frequency of the term in the document.
        :param total_words_in_d: The total number of words in the document.
        :param n: The total number of documents.
        :param n_t: The number of documents containing the term.
        :return: The TF-IDF score for the term, rounded to 8 decimal places.
        """
        tf = f_td / total_words_in_d
        idf = math.log((n + 1) / (n_t + 1)) + 1

        tf_idf = tf * idf
        return round(tf_idf, 8)

    @staticmethod
    def serialize_list_to_json(data_list: list):
        """
        Serializes a list to a JSON string.

        :param data_list: The list to serialize.
        :return: The JSON string representation of the list.
        """
        return json.dumps(data_list)

    @staticmethod
    def deserialize_json_to_list(json_str: str):
        """
        Deserializes a JSON string back into a list.

        :param json_str: The JSON string to deserialize.
        :return: The list represented by the JSON string.
        """
        return json.loads(json_str)

    @staticmethod
    def cosine_similarity(vec1: list, vec2: list) -> float:
        """
        Calculates the cosine similarity between two vectors.

        :param vec1: A list of numbers representing the first vector.
        :param vec2: A list of numbers representing the second vector.
        :return: A float representing the cosine similarity between the two vectors.
        """
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0
        return dot_product / (norm_vec1 * norm_vec2)
