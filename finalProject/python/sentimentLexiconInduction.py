import sys
import os
import re
import pprint
import math

class SentimentAnalyzer:
    class TrainSplit:
        """Represents a set of training/testing data. self.train is a list of Examples, as is self.test. 
        """
        def __init__(self):
            self.train = []
            self.test = []

    class Example:
        """Represents a document with a label. klass is 'pos' or 'neg' by convention.
           words is a list of strings.
        """
        def __init__(self):
            self.soSum = 0.0
            self.klass = ''
            self.words = []
      
    def __init__(self):
        self.phraseDict = {}
        self.hitsExcellent = 0
        self.hitsPoor = 0
        self.numFolds = 10
        
    def trainReview(self, words):
        for i in range(0, len(words)-2):
            if self.isValidPhrase(words[i], words[i+1], words[i+2]):
                phrase = self.formPhrase(words[i], words[i+1])
                hitsNearExcellent = self.getHitsNear(i, 'excellent', words)
                hitsNearPoor = self.getHitsNear(i, 'terrible', words)
                if (hitsNearExcellent > 0 or hitsNearPoor > 0):
                    self.addOrUpdatePhraseDict(phrase, hitsNearExcellent, hitsNearPoor)
            if (words[i].split('_')[0] == 'excellent'):
                self.hitsExcellent += 1
            if (words[i].split('_')[0] == 'terrible'):
                self.hitsPoor += 1
                
    def classifyReview(self, example):
        soSum = 0.0
        klass = 'unknown'
        words = example.words
        for i in range(0, len(words)-2):
            if self.isValidPhrase(words[i], words[i+1], words[i+2]):
                phrase = self.formPhrase(words[i], words[i+1])
                if phrase in self.phraseDict:
                    soSum += self.phraseDict[phrase]['so']
                    
        example.soSum = soSum
                    
        if soSum < 0:
            klass = 'neg'
        elif soSum > 0:
            klass = 'pos'
                    
        return klass
        
    def isValidPhrase(self, word1, word2, word3):
        phraseValid = False
        word1Pos = word1.split('_')[1]
        word2Pos = word2.split('_')[1]
        word3Pos = word3.split('_')[1]
                
        if word1Pos == 'JJ':
            if word2Pos == 'NN' or word2Pos == 'NNS':
                phraseValid = True
            elif word2Pos == 'JJ':
                if word3Pos != 'NN' and word3Pos != 'NNS':
                    phraseValid = True
        elif word1Pos == 'RB' or word1Pos == 'RBR' or word1Pos == 'RBS':
            if word2Pos == 'JJ':
                if word3Pos != 'NN' and word3Pos != 'NNS':
                    phraseValid = True
            elif word2Pos == 'VB' or word2Pos == 'VBD' or word2Pos == 'VBN' or word2Pos == 'VBG':
                phraseValid = True
        elif word1Pos == 'NN' or word1Pos == 'NNS':
            if word2Pos == 'JJ':
                if word3Pos != 'NN' and word3Pos != 'NNS':
                    phraseValid = True
            
        return phraseValid
        
    def formPhrase(self, word1, word2):
        phrase = word1.split('_')[0] + '_' + word1.split('_')[1] + ' ' + word2.split('_')[0] + '_' + word2.split('_')[1]
        
        return phrase
        
    def getHitsNear(self, index, nearWord, words):
        hits = 0
        lowerbound = 0 if index < 10 else (index - 10)
        upperbound = len(words) if (len(words) - index) < 11 else (index + 11)
        
        for i in range(lowerbound, upperbound):
            if words[i].split('_')[0] == nearWord:
                hits += 1
        
        return hits
        
    def addOrUpdatePhraseDict(self, phrase, hitsNearExcellent, hitsNearPoor):
        if phrase in self.phraseDict:
            self.phraseDict[phrase]['hitsNearExcellent'] += hitsNearExcellent
            self.phraseDict[phrase]['hitsNearPoor'] += hitsNearPoor
        else:
            self.phraseDict[phrase] = {'hitsNearExcellent':hitsNearExcellent, 'hitsNearPoor':hitsNearPoor, 'so':0.0}
        
    def calculateSos(self):
        for phrase in self.phraseDict:
            numerator = (self.phraseDict[phrase]['hitsNearExcellent'] + 0.01) * self.hitsPoor
            denomenator = (self.phraseDict[phrase]['hitsNearPoor'] + 0.01) * self.hitsExcellent
            so = math.log(numerator/denomenator)
            self.phraseDict[phrase]['so'] = so
        
  #############################################################################
  
    def readFile(self, fileName):
        """
        * Code for reading a file.  you probably don't want to modify anything here, 
        * unless you don't like the way we segment files.
        """
        contents = []
        f = open(fileName)
        for line in f:
            contents.append(line)
        f.close()
        result = self.segmentWords('\n'.join(contents)) 
        return result

  
    def segmentWords(self, s):
        """
        * Splits lines on whitespace for file reading
        """
        return s.split()

  
    def trainSplit(self, trainDir):
        """Takes in a trainDir, returns one TrainSplit with train set."""
        split = self.TrainSplit()
        posTrainFileNames = os.listdir('%s/pos/' % trainDir)
        negTrainFileNames = os.listdir('%s/neg/' % trainDir)
        for fileName in posTrainFileNames:
            example = self.Example()
            example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
            example.klass = 'pos'
            split.train.append(example)
        for fileName in negTrainFileNames:
            example = self.Example()
            example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
            example.klass = 'neg'
            split.train.append(example)
        return split

    def train(self, split):
        for example in split.train:
            words = example.words
            self.trainReview(words)


    def crossValidationSplits(self, trainDir):
        """Returns a lsit of TrainSplits corresponding to the cross validation splits."""
        splits = [] 
        posTrainFileNames = os.listdir('%s/pos/' % trainDir)
        negTrainFileNames = os.listdir('%s/neg/' % trainDir)
        #for fileName in trainFileNames:
        for fold in range(0, self.numFolds):
            split = self.TrainSplit()
            for fileName in posTrainFileNames:
                example = self.Example()
                example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
                example.klass = 'pos'
                if fileName[2] == str(fold):
                    split.test.append(example)
                else:
                    split.train.append(example)
            for fileName in negTrainFileNames:
                example = self.Example()
                example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
                example.klass = 'neg'
                if fileName[2] == str(fold):
                    split.test.append(example)
                else:
                    split.train.append(example)
            splits.append(split)
        return splits
  
def test10Fold(trainDir):
    sa = SentimentAnalyzer()
    splits = sa.crossValidationSplits(trainDir)
    totalCorrectlyClassifiedReviews = 0.0
    totalClassifiedReviews = 0
    totalUnclassifiedReviews = 0
    avgAccuracy = 0.0
    fold = 0
    for split in splits:
        classifier = SentimentAnalyzer()
        foldCorrectlyClassifiedReviews = 0.0
        foldClassifiedReviews = 0
        foldUnclassifiedReviews = 0
        accuracy = 0.0
        for example in split.train:
            words = example.words
            classifier.trainReview(words)
  
        classifier.calculateSos()
        
        for example in split.test:
            words = example.words
            guess = classifier.classifyReview(example)
            # print guess
            if guess == 'unknown':
                foldUnclassifiedReviews += 1.0
            else:
                foldClassifiedReviews += 1
                if example.klass == guess:
                    foldCorrectlyClassifiedReviews += 1.0
                # else:
                    # print example.soSum
                    
        totalUnclassifiedReviews += foldUnclassifiedReviews
        totalClassifiedReviews += foldClassifiedReviews
        totalCorrectlyClassifiedReviews += foldCorrectlyClassifiedReviews

        accuracy = foldCorrectlyClassifiedReviews / foldClassifiedReviews
        # avgAccuracy += accuracy
        print '[INFO]\tFold %d Classified %d out of %d reviews with %f accuracy.  %f reviews unclassified' % (fold, foldClassifiedReviews, foldClassifiedReviews+foldUnclassifiedReviews, accuracy, foldUnclassifiedReviews/(foldClassifiedReviews+foldUnclassifiedReviews)) 
        fold += 1
    avgAccuracy = totalCorrectlyClassifiedReviews / totalClassifiedReviews
    print '[INFO]\tClassified total %d out of %d reviews with %f accuracy.  %f total reviews unclassified' % (totalClassifiedReviews, totalClassifiedReviews+totalUnclassifiedReviews, avgAccuracy, totalUnclassifiedReviews/(totalClassifiedReviews+totalUnclassifiedReviews))
    
    
def classifyDir(trainDir, testDir):
    classifier = SentimentAnalyzer()
    trainSplit = classifier.trainSplit(trainDir)
    classifier.train(trainSplit)
    testSplit = classifier.trainSplit(testDir)
    accuracy = 0.0
    for example in testSplit.train:
        words = example.words
        guess = classifier.classifyReview(words)
        if example.klass == guess:
            accuracy += 1.0
    accuracy = accuracy / len(testSplit.train)
    print '[INFO]\tAccuracy: %f' % accuracy
  
def main():
    if (len(sys.argv) == 3):
        classifyDir(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        test10Fold(sys.argv[1])
    else:
        print 'incorrect arguments'

if __name__ == "__main__":
    main()