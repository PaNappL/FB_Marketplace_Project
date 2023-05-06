from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import naive_bayes, svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score, accuracy_score, recall_score, precision_score
from sklearn.linear_model import LogisticRegression

class Classifiers:
    Naive = naive_bayes.MultinomialNB()
    SVM = svm.SVC(kernel='linear')
    FOREST = RandomForestClassifier() 
    LOG = LogisticRegression(max_iter=2000)
    Train_X = None
    Train_Y = None
    Test_X = None
    Train_Y = None

    def __init__(self, Train_X, Train_Y, Test_X, Test_Y):
        self.Train_Y = Train_Y
        self.Test_Y = Test_Y

        Tfidf_vect = TfidfVectorizer(max_features=5000)
        Tfidf_vect.fit(Train_X)
        self.Train_X = Tfidf_vect.transform(Train_X)
        self.Test_X = Tfidf_vect.transform(Test_X)

    def assign_classif(self, classifiers):
        self.Naive = classifiers['Naive']
        self.SVM = classifiers['SVM']
        self.FOREST = classifiers['FOREST']
        self.LOG = classifiers['LOG']

    # A previous implementation for running classifier training
    # This does not use multiprocessing, therefore became obsolete due to the time loss
    def run_classifiers(self):
        classifiers = {}
        self.Train_NB(classifiers)
        self.Train_SVM(classifiers)
        self.Train_RandomForest(classifiers)
        self.Train_LogReg(classifiers)

        self.Naive = classifiers['Naive']
        self.SVM = classifiers['SVM']
        self.FOREST = classifiers['FOREST']
        self.LOG = classifiers['LOG']

    def Train_NB(self, classifier):
        # Classifier - Algorithm - NB
        # fit the training dataset on the classifier
        classifier['Naive'] = self.Naive.fit(self.Train_X, self.Train_Y)

    def Train_SVM(self, classifier):
        # Classifier - Algorithm - SVM
        # fit the training dataset on the classifier
        classifier['SVM'] = self.SVM.fit(self.Train_X, self.Train_Y)

    def Train_RandomForest(self, classifier):
        # Classifier - Algorithm - Random Forest
        # fit the training dataset on the classifier
        classifier['FOREST'] = self.FOREST.fit(self.Train_X, self.Train_Y)

    def Train_LogReg(self, classifier):
        # Classifier - Algorithm - Logistic Regression
        # fit the training dataset on the classifier
        classifier['LOG'] = self.LOG.fit(self.Train_X, self.Train_Y)

    # # This is the first implementation of the score calculation
    # def calc_score(self, prediction):
    #     scam_f1 = f1_score(self.Test_Y, prediction, pos_label='Scam')
    #     nscam_f1 = f1_score(self.Test_Y, prediction, pos_label='NScam')
    #     acc = accuracy_score(self.Test_Y, prediction)

    #     score = (scam_f1+(nscam_f1*0.8)+acc)/3
    #     score = round(score, 2)

    #     return score

    # This is the second implementation of the score calculation
    # The function collects all the necessary performance metrics scores and calculates a single score representing the total classifier performance
    def calc_score(self, prediction):
        scam_re = recall_score(self.Test_Y, prediction, pos_label='Scam')
        nscam_re = recall_score(self.Test_Y, prediction, pos_label='NScam')
        scam_pr = precision_score(self.Test_Y, prediction, pos_label='Scam')
        nscam_pr = precision_score(self.Test_Y, prediction, pos_label='NScam')
        acc = accuracy_score(self.Test_Y, prediction)

        score = (scam_re*0.21+scam_pr*0.205+nscam_re*0.1925+nscam_pr*0.1925+acc*0.2)
        score = round(score, 2)

        return score

    def get_classifier_scores(self):
        predictions_Naive = self.Naive.predict(self.Test_X)
        predictions_SVM = self.SVM.predict(self.Test_X)
        predictions_FOREST = self.FOREST.predict(self.Test_X)
        predictions_LOG = self.LOG.predict(self.Test_X)

        score_Naive = self.calc_score(predictions_Naive)
        score_SVM = self.calc_score(predictions_SVM)
        score_FOREST = self.calc_score(predictions_FOREST)
        score_LOG = self.calc_score(predictions_LOG)

        class_scores = {"Naive":score_Naive, "SVM":score_SVM, "FOREST":score_FOREST, "LOG":score_LOG}

        return class_scores

    def print_reports(self):

        predictions_NB = self.Naive.predict(self.Test_X)
        print("Naive Bayes Result -> ",classification_report(self.Test_Y, predictions_NB,zero_division=1))

        predictions_SVM = self.SVM.predict(self.Test_X)
        print("SVM Result -> ",classification_report(self.Test_Y, predictions_SVM,zero_division=1))

        predictions_FOREST = self.FOREST.predict(self.Test_X) 
        print("Random Forest Result -> ", classification_report(self.Test_Y, predictions_FOREST,zero_division=1))

        predictions_LOG = self.LOG.predict(self.Test_X)
        print("Logistic Regression Result -> ", classification_report(self.Test_Y, predictions_LOG,zero_division=1))
