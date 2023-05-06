from PythonFiles.Classifiers import Classifiers
from sklearn.feature_extraction.text import TfidfVectorizer
from PythonFiles.DFPreProcessing import DataPreProcessor
import warnings
import pandas
import multiprocessing as mp

class Iterative_Classif:
    Train_X = None
    Train_Y = None
    Test_X = None
    Test_Y = None
    classif = None
    trainData = None
    unknownData = None
    curr_chunk = None
    best_score = 0
    best_classif = None
    iteration = 1
    chunk_size = 200
    features_to_be_classified = [['text_final','Location','Image_Counts','year_diff']]
    score_log = []
    best_classifier_log = []

    def __init__(self, trainData, testData):
        processedData = DataPreProcessor().processData(testData.copy(deep=True))
        self.Test_X = DataPreProcessor().get_feature_datasets(processedData, self.features_to_be_classified)[0]
        self.Test_Y = testData['label']

        self.trainData = DataPreProcessor().processData(trainData.copy(deep=True))
        
        self.unknownData = self.trainData.loc[self.trainData['label'] == 'Unknown'].reset_index(drop=True)
        self.trainData = self.trainData.loc[self.trainData['label'] != 'Unknown'].reset_index(drop=True)

        if len(self.unknownData) == 0:
            raise Exception("No Unlabelled Data")
        elif len(self.unknownData) < self.chunk_size:
            self.curr_chunk = self.unknownData
            self.unknownData = None
        else:
            self.curr_chunk = self.unknownData[:self.chunk_size].copy(deep=True)
            self.unknownData = self.unknownData[self.chunk_size:]

    def iterate_Classif_Training(self, iter_count):
        try:
            start_iter = self.iteration
            while self.iteration < start_iter + iter_count and len(self.unknownData) != 0:
                print(f'Iteration: {self.iteration}')
                self.next_iteration()
        except Exception as e:
            print("ERROR")
            print(e)
    
    def next_iteration(self):
        if len(self.unknownData) == 0:
            raise Exception("No more unknown data")

        try:
            self.unknownData = self.unknownData[self.chunk_size:].reset_index(drop=True)
        except:
            self.unknownData = pandas.DataFrame()

        self.train_and_classify()
        self.trainData = self.trainData.append(self.curr_chunk)

        self.curr_chunk = self.unknownData[:self.chunk_size].copy(deep=True)
        self.iteration += 1

        if len(self.unknownData) == 0:
            self.train_and_classify()
            self.trainData = self.trainData.append(self.curr_chunk)
            self.curr_chunk = None
            self.iteration += 1

    def train_and_classify(self):
        warnings.filterwarnings('ignore')

        self.Train_X = DataPreProcessor().get_feature_datasets(self.trainData.copy(deep=True), self.features_to_be_classified)[0]
        self.Train_Y = self.trainData['label']

        classif = Classifiers(self.Train_X, self.Train_Y, self.Test_X, self.Test_Y)

        manager = mp.Manager()
        classifiers = manager.dict()

        p1 = mp.Process(target=classif.Train_NB, args=(classifiers,))
        p2 = mp.Process(target=classif.Train_SVM, args=(classifiers,))
        p3 = mp.Process(target=classif.Train_RandomForest, args=(classifiers,))
        p4 = mp.Process(target=classif.Train_LogReg, args=(classifiers,))

        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()

        classif.assign_classif(classifiers)

        scores = classif.get_classifier_scores()
        self.classify_on_score(classif, scores)

    def classify_on_score(self, classif, scores):
        best_classifier = max(scores, key=scores.get)

        if max(scores.values()) > self.best_score:
            self.best_score = max(scores.values())
            self.best_classif = classif

        processedData = DataPreProcessor().get_feature_datasets(self.curr_chunk.copy(deep=True), self.features_to_be_classified)[0]

        Tfidf_vect = TfidfVectorizer(max_features=5000)
        Tfidf_vect.fit(self.Train_X)
        processedData = Tfidf_vect.transform(processedData)

        if best_classifier == 'Naive':
            labels = classif.Naive.predict(processedData)
        elif best_classifier == 'SVM':
            labels = classif.SVM.predict(processedData)
        elif best_classifier == 'FOREST':
            labels = classif.FOREST.predict(processedData)
        elif best_classifier == 'LOG':
            labels = classif.LOG.predict(processedData)

        self.curr_chunk['label'] = labels
        self.score_log.append(scores[best_classifier])
        self.best_classifier_log.append(best_classifier)