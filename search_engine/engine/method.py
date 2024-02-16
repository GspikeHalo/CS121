#  .search_engine/engine/method.py

import datetime
import math
import nltk
from lxml import html
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize


nltk.download('punkt')  # for tokenize
nltk.download('stopwords')  # for stop words
nltk.download('wordnet')  # for lemmatizer




class Method:
    @staticmethod
    def check_time_difference(prev_time_str: str, update_time: int) -> bool:
        prev_time = datetime.datetime.strptime(prev_time_str, "%Y-%m-%d").date()
        current_date = datetime.datetime.now().date()
        time_difference = abs((current_date - prev_time).days)
        return time_difference <= update_time

    @staticmethod
    def check_num_difference(num01: str | int, num02: str | int) -> bool:
        return int(num01) == int(num02)

    @staticmethod
    def preprocess_text(text: str) -> list[str]:
        """预处理文本：去除停用词，词形还原，分词"""
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        words = word_tokenize(text)
        filtered_words = [lemmatizer.lemmatize(word.lower()) for word in words if
                          word.lower() not in stop_words and word.isalpha()]
        return filtered_words

    @staticmethod
    def calculate_token_weight(html_content: bytes) -> dict:
        try:
            tree = html.fromstring(html_content)
            token_weights = {}

            # 添加或更新 token 权重
            def add_weight(token, weight):
                if token in token_weights:
                    token_weights[token] += weight
                else:
                    token_weights[token] = weight

            # 处理标题
            title = tree.find('.//title')
            if title is not None and title.text:
                for token in Method.preprocess_text(title.text):
                    add_weight(token, 10)
            # 处理 H 标签 和 每段首句
            for h_tag in tree.xpath('//h1|//h2|//h3|//h4|//h5|//h6|//p'):
                text_content = h_tag.text_content()
                sentences = sent_tokenize(text_content)
                first_sentence = True
                for sentence in sentences:
                    tokens = Method.preprocess_text(sentence)
                    if not tokens:
                        continue
                    if first_sentence or h_tag.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        weight = 5 if h_tag.tag == 'p' and first_sentence else 5
                        for token in tokens:
                            add_weight(token, weight)
                    first_sentence = False
            # 处理加粗或斜体文本
            for tag in tree.xpath('//b|//strong|//i|//em'):
                for token in Method.preprocess_text(tag.text_content()):
                    add_weight(token, 1)
            return token_weights
        except Exception as e:
            print(e)
            return {}

    # 添加tf-idf的计算

    @staticmethod
    def get_html_general_info(content: bytes) -> tuple:
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
        folder_name, file_name = doc_id.split("/")
        return folder_name, file_name

    @staticmethod
    def calculate_tf_idf(f_td, total_words_in_d, n, n_t):
        tf = f_td / total_words_in_d
        idf = math.log((n + 1) / (n_t + 1)) + 1

        tf_idf = tf * idf
        return round(tf_idf, 8)
