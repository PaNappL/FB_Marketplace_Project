import pandas as pd
import ast
import nltk
import itertools
import re
import numpy as np
import multiprocessing as mp
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from collections import defaultdict

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)
    
np.random.seed(500)

class CleanDF():

    def __init__(self, df):
        self.df = self.reshapeDF(df)
        self.df = self.checkFields(self.df)
        self.df = self.df.reset_index()

    def reshapeDF(self, df):
        interesting_fields = ["URL","Username","UserID","Description","Location","Join_date","Image_Counts","Category"]
        return df[interesting_fields]
    
    def checkFields(self, df):
        for indx,row in df.iterrows():

            if "https://www.facebook.com/" not in str(row['URL']):
                df = df.drop([indx])
                continue

            if row.isnull().values.any() == True:
                df = df.drop([indx])
                continue

            try:
                ast.literal_eval(row['Description'])
            except:
                df = df.drop([indx])

        return df
    
    def getConvertedDF(self):
        return self.df

class DataPreProcessor():
    def processData(self, df):
        cores = mp.cpu_count()
        chunks = np.array_split(df, cores)

        with mp.Pool(cores) as p:
            results = p.map(self.process_chunk, chunks)

        return pd.concat(results)

    def process_chunk(self, chunk):
        chunk['Description'] = chunk['Description'].apply(self.__dict_to_sentence)
        chunk['Description'].dropna(inplace=True)
        chunk['Description'] = chunk['Description'].apply(str.lower)

        chunk['Description'] = chunk['Description'].apply(word_tokenize)
        chunk['text_final'] = chunk['Description'].apply(self.__lemmatization)

        return chunk
    
    def __dict_to_sentence(self,dictVal):
        values = ast.literal_eval(dictVal)
        sent = ""
        for val in values:
            for i in range(values[val]):
                sent += val + " "
        sent = self.__remove_unicode(sent)
        return sent

    def __remove_unicode(self,string):
        # Use a regular expression to find all Unicode code points
        string = re.sub(r'u[0-9a-fA-F]{4}', ' uniChar ' ,string)

        return string
    
    def __lemmatization(self, entry: list):
        tag_map = defaultdict(lambda : wn.NOUN)
        tag_map['J'] = wn.ADJ
        tag_map['V'] = wn.VERB
        tag_map['R'] = wn.ADV

        Final_words = []
        lemmatizer = WordNetLemmatizer()

        stop_words = set(stopwords.words('english'))

        for word, tag in pos_tag(entry):
            if word not in stop_words and word.isalpha():
                word_Final = lemmatizer.lemmatize(word,tag_map[tag[0]])
                Final_words.append(word_Final)

        return str(Final_words)
    
    def get_feature_datasets(self, df: pd.core.frame.DataFrame, features: list):
        feature_sets = features
        if len(features) > 1:
            feature_sets = self.__get_feature_combinations(features)
        datasets = [self.__get_dataset_by_features(feature_set, df) for feature_set in feature_sets]
        return datasets
    
    def __get_feature_combinations(self, features: list):
        feature_sets = []
        for r in range(1, len(features)+1):
            feature_sets += itertools.combinations(features, r)

        return feature_sets

    def __get_dataset_by_features(self, features: list, df: pd.core.frame.DataFrame):
        new_df = df[features[0]].astype(str)
        for feature in features[1:]:
            new_df = new_df.str.cat(df[feature].astype(str), sep=' ')

        return new_df