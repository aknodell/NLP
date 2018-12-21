import sys
import getopt
import os
import math
import operator
import random

# import numpy as np

class Perceptron:
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
      self.klass = ''
      self.words = []
      self.featureIndexes = set([])
      self.featureCounts = []


  def __init__(self):
    """Perceptron initialization"""
    #in case you found removing stop words helps.
    self.stopList = set(self.readStopWords('../data/english.stop'))
    self.POS_ONLY = False
    self.numFolds = 10
    
    self.wordIndexes = dict([])
    self.weights = []
    self.bias = 0.0
    # self.bias = []
    # self.biasAverage = 0

  #############################################################################
  # TODO TODO TODO TODO TODO 
  # Implement the Perceptron classifier with
  # the best set of features you found through your experiments with Naive Bayes.

  def classify(self, words):
    """ TODO
      'words' is a list of words to classify. Return 'pos' or 'neg' classification.
    """
    
    # Write code here
    featureCounts = [0]*len(self.weights)
    featureIndexes = set([])

    for word in words:
        if word in self.wordIndexes:
            featureIndex = self.wordIndexes[word]
            featureIndexes.add(featureIndex)
            featureCounts[featureIndex] += 1
                   
    result = sum([self.weights[featureIndex] * featureCounts[featureIndex] for featureIndex in featureIndexes]) + self.bias
    
    return 'pos' if result > 0 else 'neg'
  

  def addExample(self, klass, words):
    """
     * TODO
     * Train your model on an example document with label klass ('pos' or 'neg') and
     * words, a list of strings.
     * You should store whatever data structures you use for your classifier 
     * in the Perceptron class.
     * Returns nothing
    """

    # Write code here
    for word in set(words):
        if word not in self.wordIndexes:
            self.weights.append(0.0);
            self.wordIndexes[word] = len(self.weights) - 1           
    
    pass
  
  def train(self, split, iterations):
    """
    * TODO 
    * iterates through data examples
    * TODO 
    * use weight averages instead of final iteration weights
    """
    for example in split.train:
        words = example.words
        self.addExample(example.klass, words)
        
    runningWeights = self.weights
    runningBias = self.bias
    averageWeights = self.weights
    averageBias = self.bias

    # trainFeatureCounts = []
    # trainFeatureIndexes = []
    count = 1
    

    for iter in range(iterations):
        # exampleIndex = 0
        random.shuffle(split.train)
        for example in split.train:
            words = example.words
            expectedKlass = 1 if example.klass is 'pos' else -1
            
            if iter is 0:
                example.featureCounts = ([0]*len(runningWeights))
                # trainFeatureIndexes.append(set([]))
                for word in words:
                    featureIndex = self.wordIndexes[word]
                    example.featureIndexes.add(featureIndex)
                    example.featureCounts[featureIndex] += 1
                    # trainFeatureIndexes[exampleIndex].add(featureIndex)
                    # trainFeatureCounts[exampleIndex][featureIndex] += 1
            
            result = runningBias
            for featureIndex in example.featureIndexes:
                result += runningWeights[featureIndex] * example.featureCounts[featureIndex]
                        
            if expectedKlass * result <= 0:
                for featureIndex in example.featureIndexes:
                    runningWeights[featureIndex] += expectedKlass * example.featureCounts[featureIndex]
                    averageWeights[featureIndex] += expectedKlass * count * example.featureCounts[featureIndex]
                runningBias += expectedKlass
                averageBias += expectedKlass * count
                    
            count += 1
            # exampleIndex += 1
                    
    for i in range(len(self.weights)):
        self.weights[i] = runningWeights[i] - (averageWeights[i]/count)
        
    self.bias = runningBias - (averageBias/count)
  # END TODO (Modify code beyond here with caution)
  #############################################################################
  
  
  def readStopWords(self, fileName):
    contents = []
    f = open(fileName)
    for line in f:
      contents.append(line)
    f.close()
    result = self.segmentWords('\n'.join(contents))
    
    return result
  
  def readFile(self, fileName, ngram):
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
    
    if self.POS_ONLY:
        for i in range(len(result)):
            result[i] = result[i].split("_")[0] + '_' + result[i].split("_")[1]

    if ngram > 1:
        for i in range(len(result) - (ngram -1)):
            for j in range(1, ngram):
                result[i] += ' ' + result[i+j]
                
    return result

  
  def segmentWords(self, s):
    """
     * Splits lines on whitespace for file reading
    """
    return s.split()

  
  def trainSplit(self, trainDir, ngram):
    """Takes in a trainDir, returns one TrainSplit with train set."""
    split = self.TrainSplit()
    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    for fileName in posTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/pos/%s' % (trainDir, fileName), ngram)
      example.klass = 'pos'
      split.train.append(example)
    for fileName in negTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/neg/%s' % (trainDir, fileName), ngram)
      example.klass = 'neg'
      split.train.append(example)
    return split


  def crossValidationSplits(self, trainDir, ngram):
    """Returns a lsit of TrainSplits corresponding to the cross validation splits."""
    splits = [] 
    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    #for fileName in trainFileNames:
    for fold in range(0, self.numFolds):
      split = self.TrainSplit()
      for fileName in posTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (trainDir, fileName), ngram)
        example.klass = 'pos'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      for fileName in negTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (trainDir, fileName), ngram)
        example.klass = 'neg'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      splits.append(split)
    return splits
  
  
  def filterStopWords(self, words):
    """Filters stop words."""
    filtered = []
    for word in words:
      if not word in self.stopList and word.strip() != '':
        filtered.append(word)
    return filtered

def test10Fold(POS_ONLY, args):
  pt = Perceptron()
  pt.POS_ONLY = POS_ONLY
  
  iterations = int(args[2])
  splits = pt.crossValidationSplits(args[0], int(args[1]))
  avgAccuracy = 0.0
  fold = 0
  for i in range(0, len(splits)):
    classifier = Perceptron()
    accuracy = 0.0
    classifier.train(splits[i],iterations)
  
    for example in splits[i].test:
      words = example.words
      guess = classifier.classify(words)
      if example.klass == guess:
        accuracy += 1.0

    accuracy = accuracy / len(splits[i].test)
    avgAccuracy += accuracy
    print '[INFO]\tFold %d Accuracy: %f' % (fold, accuracy) 
    fold += 1
    splits[i] = None
    
  avgAccuracy = avgAccuracy / fold
  print '[INFO]\tAccuracy: %f' % avgAccuracy
    
    
def classifyDir(trainDir, testDir,iter):
  classifier = Perceptron()
  trainSplit = classifier.trainSplit(trainDir)
  iterations = int(iter)
  classifier.train(trainSplit,iterations)
  testSplit = classifier.trainSplit(testDir)
  #testFile = classifier.readFile(testFilePath)
  accuracy = 0.0
  for example in testSplit.train:
    words = example.words
    guess = classifier.classify(words)
    if example.klass == guess:
      accuracy += 1.0
  accuracy = accuracy / len(testSplit.train)
  print '[INFO]\tAccuracy: %f' % accuracy
    
def main():
  POS_ONLY = False
  (options, args) = getopt.getopt(sys.argv[1:], 'p')

  if ('-p', '') in options:
    POS_ONLY = True
  
  if len(args) == 3:
    test10Fold(POS_ONLY, args)
  else:
    print 'incorrect number of arguments'

if __name__ == "__main__":
    main()
