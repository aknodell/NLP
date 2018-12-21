import sys
import os
import re
import pprint
import math

class SentimentAnalyzer:
    class TrainSplit:
        def __init__(self):
            self.train = []
            self.test = []
       
    class Review:
        def __init__(self):
            self.klass = ''
            self.taggedWords = []
            self.bigrams = []
            self.soSum = 0.0
            self.soAverage = 0.0
            self.posProb = 0.0
            self.negProb = 0.0
            self.nbGuess = ''
            self.pmiGuess = ''

    def __init__(self):
        self.phraseDict = {}
        self.hitsExcellent = 0
        self.hitsPoor = 0
        self.posBigrams = dict([])
        self.negBigrams = dict([])
        self.allBigrams = set([])
        self.posBigramsCount = 0
        self.negBigramsCount = 0
        
    ##################################
    ##         Train Review         ##
    ##################################
        
    def trainExampleReview(self, review):
        self.trainNb(review.klass, review.bigrams)
        self.trainPmi(review.taggedWords)
        
    def trainNb(self, klass, bigrams):
        for bigram in bigrams:
            if klass is 'pos':
                if bigram in self.posBigrams:
                    self.posBigrams[bigram] += 1
                else:
                    self.posBigrams[bigram] = 1
                self.posBigramsCount += 1
            elif klass is 'neg':
                if bigram in self.negBigrams:
                    self.negBigrams[bigram] += 1
                else:
                    self.negBigrams[bigram] = 1
                self.negBigramsCount += 1
                
        self.allBigrams.update(bigrams)
        
    def trainPmi(self, taggedWords):
        for i in range(0, len(taggedWords)-2):
            if self.isValidPhrase(taggedWords[i], taggedWords[i+1], taggedWords[i+2]):
                phrase = self.formPhrase(taggedWords[i], taggedWords[i+1])
                hitsNearExcellent = self.getHitsNear(i, 'great', taggedWords)
                hitsNearPoor = self.getHitsNear(i, 'bad', taggedWords)
                if hitsNearExcellent+hitsNearPoor > 2:
                    self.addOrUpdatePhraseDict(phrase, hitsNearExcellent, hitsNearPoor)
            if taggedWords[i].split('_')[0] == 'great':
                self.hitsExcellent += 1
            if taggedWords[i].split('_')[0] == 'bad':
                self.hitsPoor += 1
                
    ##################################
    ##       Classifiy Review       ##
    ##################################    
        
    def classify(self, review):
        guess = 'unknown'
        pmiGuess = self.calculateSoSum(review)
        nbGuess = self.calculateProbs(review)
        
        if pmiGuess == nbGuess:
            guess = pmiGuess
        elif pmiGuess == 'unknown':
            guess = nbGuess
        elif nbGuess == 'unknown':
            guess = pmiGuess
        else:
            if abs(review.soAverage) > 1.7543 and abs((review.posProb - review.negProb)/(review.posProb + review.negProb)) < 0.0009:
                guess = pmiGuess
            else:
                guess = nbGuess
            
        return guess    
        
    def calculateSoSum(self, review):
        guess = 'unknown'
        phraseCount = 0
        for i in range(0, len(review.taggedWords)-2):
            if self.isValidPhrase(review.taggedWords[i], review.taggedWords[i+1], review.taggedWords[i+2]):
                phrase = self.formPhrase(review.taggedWords[i], review.taggedWords[i+1])
                if phrase in self.phraseDict:
                    phraseCount += 1
                    review.soSum += self.phraseDict[phrase]['so']
                    
        if phraseCount > 0:
            review.soAverage = review.soSum / phraseCount
              
        if review.soSum > 0:
            guess = 'pos'
        elif review.soSum < 0:
            guess = 'neg'
			
        review.pmiGuess = guess
            
        return guess
                    
    def calculateProbs(self, review):
        guess = 'unknown'
        for bigram in review.bigrams:
            if bigram not in self.posBigrams:
                review.posProb += math.log10(1.0/(self.posBigramsCount + len(self.allBigrams) + 1))
            else:
                review.posProb += math.log10((self.posBigrams[bigram]+1.0)/(self.posBigramsCount + len(self.allBigrams) + 1))
            if bigram not in self.negBigrams:
                review.negProb += math.log10(1.0/(self.negBigramsCount + len(self.allBigrams) + 1))
            else:
                review.negProb += math.log10((self.negBigrams[bigram]+1.0)/(self.negBigramsCount + len(self.allBigrams) + 1))
                
        if review.posProb > review.negProb:
            guess = 'pos'
        elif review.posProb < review.negProb:
            guess = 'neg'
            
        review.nbGuess = guess
		
        return guess
        
    
        
    ##################################
    ##        Misc Functions        ##
    ##################################    
        
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

    ##################################
    ##         File Reading         ##
    ##################################
    
    def getBigrams(self, taggedWords):
        bigrams = []
		
        # for i in range(len(taggedWords)):
            # taggedWords[i] = taggedWords[i].split("_")[0] + '_' + taggedWords[i].split("_")[1]

		
        for i in range(len(taggedWords) - 1):
            word1 = taggedWords[i].split('_')[0] + '_' + taggedWords[i].split('_')[1]
            word2 = taggedWords[i+1].split('_')[0] + '_' + taggedWords[i+1].split('_')[1]
            bigrams.append(word1 + ' ' + word2)
            
        return bigrams
        
    def readFile(self, fileName):
        contents = []
        f = open(fileName)
        for line in f:
            contents.append(line)
        f.close()
        result = self.segmentWords('\n'.join(contents)) 
        
        return result

    def segmentWords(self, s):
        return s.split()
        
    def crossValidationSplits(self, trainDir, numFolds):
        splits = [] 
        posTrainFileNames = os.listdir('%s/pos/' % trainDir)
        negTrainFileNames = os.listdir('%s/neg/' % trainDir)

        for fold in range(0, numFolds):
            split = self.TrainSplit()
            for fileName in posTrainFileNames:
                review = self.Review()
                review.taggedWords = self.readFile('%s/pos/%s' % (trainDir, fileName))
                review.bigrams = self.getBigrams(review.taggedWords)
                # print review.taggedWords
                # print review.bigrams
                review.klass = 'pos'
                if fileName[3] == str(fold):
                    split.test.append(review)
                else:
                    split.train.append(review)
            for fileName in negTrainFileNames:
                review = self.Review()
                review.taggedWords = self.readFile('%s/neg/%s' % (trainDir, fileName))
                review.bigrams = self.getBigrams(review.taggedWords)
                review.klass = 'neg'
                if fileName[3] == str(fold):
                    split.test.append(review)
                else:
                    split.train.append(review)
            splits.append(split)
        return splits        
            
def test10Fold(trainDir):
    sa = SentimentAnalyzer()
    splits = sa.crossValidationSplits(trainDir, 10)
    totalReviews = 0
    totalCorrectClassifications = 0.0
    
    for i in range(len(splits)):
        classifier = SentimentAnalyzer()
        foldReviews = 0
        foldCorrectClassifications = 0.0
        
        for review in splits[i].train:
            classifier.trainExampleReview(review)
            
        classifier.calculateSos()
        
        for review in splits[i].test:
            foldReviews += 1
            guess = classifier.classify(review)
			
            # if review.pmiGuess != review.klass and review.nbGuess != review.klass:
                # print '%f %f' % (abs((review.posProb-review.negProb)/(review.posProb+review.negProb)), abs(review.soAverage))
                        
            if guess == review.klass:
                foldCorrectClassifications += 1.0
                
        totalReviews += foldReviews
        totalCorrectClassifications += foldCorrectClassifications
                
        print 'Fold %d Accuracy: %f' % (i, foldCorrectClassifications/foldReviews)
        
    print 'Total Accuracy: %f' % (totalCorrectClassifications/totalReviews)

def main():
    if len(sys.argv) == 2:
        test10Fold(sys.argv[1])
    else:
        print 'incorrect arguments'

if __name__ == "__main__":
    main()