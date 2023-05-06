from PythonFiles.Classifiers import Classifiers
from sklearn.feature_extraction.text import TfidfVectorizer
from PythonFiles.DFPreProcessing import DataPreProcessor
import warnings
import pandas
import numpy as np
import multiprocessing as mp

class OneStepIterClassif:
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
    chunk_size = 500
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

        classif = self.train_classifiers(self.trainData)

        self.check_best(classif)
        self.score_log.append(self.get_best_score(classif))

        predictedBatches = self.predict_Batches(classif)

        scores = []
        best_scores = []
        classifs = []
        classifier_names = ['Naive','SVM','FOREST','LOG']

        for predictedData in predictedBatches:
            classif = self.train_classifiers(predictedData)
            classifs.append(classif)
            scores.extend(list(classif.get_classifier_scores().values()))

        best_classif_one = (int)(np.argmax(scores)/4)
        best_classif_two = (int)(np.argmax(scores)%4)
        if best_classif_one < 0: best_classif_one = 0

        chunk_one_step = self.unknownData[:self.chunk_size].copy(deep=True)
        self.unknownData = self.unknownData[self.chunk_size:].reset_index(drop=True)

        chunk_one_step['label'] = self.predict_one_step(classifs[best_classif_one], best_classif_two, chunk_one_step)
        self.trainData = self.trainData.append(chunk_one_step)

        self.curr_chunk = self.unknownData[:self.chunk_size].copy(deep=True)
        self.best_classifier_log.append(classifier_names[best_classif_one])
        self.best_classifier_log.append(classifier_names[best_classif_two])
        self.iteration += 1

        if len(self.unknownData) == 0:
            self.train_and_classify()
            self.trainData = self.trainData.append(self.curr_chunk)
            self.curr_chunk = None
            self.iteration += 1

    def predict_one_step(self, classif, classifTwoIndex, chunk):
        processedData = DataPreProcessor().get_feature_datasets(chunk.copy(deep=True), self.features_to_be_classified)[0]

        Tfidf_vect = TfidfVectorizer(max_features=5000)
        Tfidf_vect.fit(self.Train_X)
        processedData = Tfidf_vect.transform(processedData)

        if classifTwoIndex == 0:
            labels = classif.Naive.predict(processedData)
        elif classifTwoIndex == 1:
            labels = classif.SVM.predict(processedData)
        elif classifTwoIndex == 2:
            labels = classif.FOREST.predict(processedData)
        elif classifTwoIndex == 3:
            labels = classif.LOG.predict(processedData)

        return labels

    def train_classifiers(self, trainData):
        warnings.filterwarnings('ignore')

        self.Train_X = DataPreProcessor().get_feature_datasets(trainData.copy(deep=True), self.features_to_be_classified)[0]
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

        return classif
    
    def check_best(self, classif):
        best_score = self.get_best_score(classif)
        if best_score > self.best_score:
            self.best_score = best_score
            self.best_classif = classif
    
    def get_best_score(self, classif):
        scores = classif.get_classifier_scores()
        best_score = max(scores.values())

        return best_score
    
    def predict_Batches(self, classif):
        processedData = DataPreProcessor().get_feature_datasets(self.curr_chunk.copy(deep=True), self.features_to_be_classified)[0]

        Tfidf_vect = TfidfVectorizer(max_features=5000)
        Tfidf_vect.fit(self.Train_X)
        processedData = Tfidf_vect.transform(processedData)

        predictedBatches = []

        classifiers = [classif.Naive, classif.SVM, classif.FOREST, classif.LOG]

        for classifier in classifiers:
            labeledChunk = self.curr_chunk
            labeledChunk['label'] = classifier.predict(processedData)
            trainDataCopy = self.trainData.copy(deep=True)
            trainDataCopy.append(labeledChunk)
            predictedBatches.append(trainDataCopy)

        return predictedBatches