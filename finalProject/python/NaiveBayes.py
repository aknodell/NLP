import sys
import getopt
import os
import math
import operator

class NaiveBayes:
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
        self.posProb = 0.0
        self.negProb = 0.0
        self.klass = ''
        self.words = []
      
    # def formatWords(self):
        # if len(self.words) > 0:
            # print '%f' % len(self.words[0].split("_"))
            # if len(self.words[0].split("_")) > 1:
                # print self.words[0]
                # for i in range(len(self.words)):
                    # self.words[i] = self.words[i].split("_")[0] + self.words[i].split("_")[1]

  def __init__(self):
    """NaiveBayes initialization"""
    self.FILTER_STOP_WORDS = False
    self.BOOLEAN_NB = False
    self.POS_ONLY = False
    self.posWords = dict([])
    self.negWords = dict([])
    self.allWords = set([])
    self.posOnlyWords = set([])
    self.negOnlyWords = set([])
    self.posWordsCount = 0
    self.negWordsCount = 0
    self.posDocCount = 0
    self.negDocCount = 0
    self.stopList = set(self.readStopWords('../data/english.stop'))
    self.numFolds = 10

  #############################################################################
  # TODO TODO TODO TODO TODO 
  # Implement the Multinomial Naive Bayes classifier and the Naive Bayes Classifier with
  # Boolean (Binarized) features.
  # If the BOOLEAN_NB flag is true, your methods must implement Boolean (Binarized)
  # Naive Bayes (that relies on feature presence/absence) instead of the usual algorithm
  # that relies on feature counts.
  #
  #
  # If any one of the FILTER_STOP_WORDS and BOOLEAN_NB flags is on, the
  # other one is meant to be off.

  def classify(self, example):
    """ TODO
      'words' is a list of words to classify. Return 'pos' or 'neg' classification.
    """
    words = example.words
    if self.FILTER_STOP_WORDS:
      words =  self.filterStopWords(words)

    # Write code here
    # posProb = 0.0
    # negProb = 0.0
    klass = ''
    
    if self.BOOLEAN_NB:
        for word in set(words):
            if word in self.posOnlyWords:
                example.posProb -= math.log10(2.0/(len(self.posOnlyWords) + len(self.allWords) + 1))
            elif word in self.negOnlyWords:
                example.negProb -= math.log10(2.0/(len(self.negOnlyWords) + len(self.allWords) + 1))
            elif word not in self.allWords:
                example.posProb -= math.log10(1.0/(len(self.posOnlyWords) + len(self.allWords) + 1))
                example.negProb -= math.log10(1.0/(len(self.negOnlyWords) + len(self.allWords) + 1))
    else:
        for word in words:
            if word not in self.posWords:
                example.posProb += math.log10(1.0/(self.posWordsCount + len(self.allWords) + 1))
            else:
                example.posProb += math.log10((self.posWords[word]+1.0)/(self.posWordsCount + len(self.allWords) + 1))
            if word not in self.negWords:
                example.negProb += math.log10(1.0/(self.negWordsCount + len(self.allWords) + 1))
            else:
                example.negProb += math.log10((self.negWords[word]+1.0)/(self.negWordsCount + len(self.allWords) + 1))
        
    if example.posProb > example.negProb:
        klass = 'pos'
    else:
        klass = 'neg'
            
    return klass
  

  def addExample(self, klass, words):
    """
     * TODO
     * Train your model on an example document with label klass ('pos' or 'neg') and
     * words, a list of strings.
     * You should store whatever data structures you use for your classifier 
     * in the NaiveBayes class.
     * Returns nothing
    """


    # Write code here
    if (self.BOOLEAN_NB):
        for word in set(words):
            if klass is 'pos':
                if word in self.allWords:
                    if word in self.negOnlyWords:
                        self.negOnlyWords.remove(word)
                else:
                    self.posOnlyWords.add(word)
            if klass is 'neg':
                if word in self.allWords:
                    if word in self.posOnlyWords:
                        self.posOnlyWords.remove(word)
                else:
                    self.negOnlyWords.add(word)
    else:
        for word in words:
            if klass is 'pos':
                if word in self.posWords:
                    self.posWords[word] += 1
                else:
                    self.posWords[word] = 1
                self.posWordsCount += 1
            elif klass is 'neg':
                if word in self.negWords:
                    self.negWords[word] += 1
                else:
                    self.negWords[word] = 1
                self.negWordsCount += 1
                
    self.allWords.update(words)

    pass
      

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

  def train(self, split):
    for example in split.train:
      words = example.words
      if self.FILTER_STOP_WORDS:
        words =  self.filterStopWords(words)
      self.addExample(example.klass, words)


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
        # print example.words
        example.klass = 'pos'
        if fileName[3] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      for fileName in negTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (trainDir, fileName), ngram)
        example.klass = 'neg'
        if fileName[3] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      splits.append(split)
    return splits
  
  def filterStopWords(self, words):
    """Filters stop words."""
    filtered = []
    for word in words:
      werds = word.split()
      for werd in werds:
        if not werd.split("_")[0] in self.stopList and werd.strip() != '':
            filtered.append(word)
    return filtered

def test10Fold(args, FILTER_STOP_WORDS, BOOLEAN_NB, POS_ONLY):
  nb = NaiveBayes()
  nb.POS_ONLY = POS_ONLY
  splits = nb.crossValidationSplits(args[0], int(args[1]))
  avgAccuracy = 0.0
  fold = 0
  for i in range(0, len(splits)):
    classifier = NaiveBayes()
    classifier.FILTER_STOP_WORDS = FILTER_STOP_WORDS
    classifier.BOOLEAN_NB = BOOLEAN_NB
    # classifier.POS_ONLY = POS_ONLY
    accuracy = 0.0
    for example in splits[i].train:
      words = example.words
      # example.formatWords()
      classifier.addExample(example.klass, words)
  
    for example in splits[i].test:
      words = example.words
      guess = classifier.classify(example)
      if example.klass == guess:
        accuracy += 1.0
      # else: 
        # print '%f %f' % (example.posProb, example.negProb)
        

    accuracy = accuracy / len(splits[i].test)
    avgAccuracy += accuracy
    print '[INFO]\tFold %d Accuracy: %f' % (fold, accuracy) 
    fold += 1
    splits[i] = None
  avgAccuracy = avgAccuracy / fold
  print '[INFO]\tAccuracy: %f' % avgAccuracy

def main():
  FILTER_STOP_WORDS = False
  BOOLEAN_NB = False
  POS_ONLY = False
  (options, args) = getopt.getopt(sys.argv[1:], 'fbmp')
  if ('-f','') in options:
    FILTER_STOP_WORDS = True
  if ('-b','') in options:
    BOOLEAN_NB = True
  if ('-p', '') in options:
    POS_ONLY = True
    
  if len(args) == 2:
    test10Fold(args, FILTER_STOP_WORDS, BOOLEAN_NB, POS_ONLY)
  else:
    print 'incorrect number of arguments'

if __name__ == "__main__":
    main()
