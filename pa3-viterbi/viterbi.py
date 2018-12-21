import sys
import os
import re
import pprint
from decimal import *

class Viterbi:
    def __init__(self):
        getcontext().prec = 10
        self.partsOfSpeechForReadingFile = ('noun', 'verb', 'inf', 'prep', 'phi', 'fin')
        self.partsOfSpeech = ('noun', 'verb', 'inf', 'prep')
        self.lexicalProbs = {}
        self.bigramProbs = {'noun':{}, 'verb':{}, 'inf':{}, 'prep':{}, 'phi':{}, 'fin':{}}
        # initialize the bigram probabilities to 0.0001
        # in case they are not included in the probabilities file
        for pos in self.partsOfSpeechForReadingFile:
            for posTrans in self.partsOfSpeechForReadingFile:
                self.bigramProbs[pos][posTrans] = 0.0001
        self.sentences = []

    def getLexicalProbs(self, word, pos):
        prob = 0.0001
        try:
            prob = self.lexicalProbs[word][pos]
        except KeyError, e:
            prob = 0.0001
        return prob
        
    def viterbiNetwork(self, sent):
        print '\nPROCESSING SENTENCE: ' + sent
        sentence = sent.split()
        
        piTable = [{}]
        for pos in self.partsOfSpeech:
            piTable[0][pos] = {'prob':self.bigramProbs[pos]['phi'] * self.getLexicalProbs(sentence[0], pos), 'bkptr':None}
        for k in range(1, len(sentence)):
            piTable.append({})
            for pos in self.partsOfSpeech:
                maxTrProb = max(piTable[k-1][prev]['prob'] * self.bigramProbs[pos][prev] for prev in self.partsOfSpeech);
                for prev in self.partsOfSpeech:
                    if piTable[k-1][prev]['prob'] * self.bigramProbs[pos][prev] == maxTrProb:
                        maxProb = maxTrProb * self.getLexicalProbs(sentence[k], pos)
                        piTable[k][pos] = {'prob': maxProb, 'bkptr':prev}
                        
        maxFinalState = {'prob':0, 'bkptr':None}
        for pos in piTable[-1]:
            finalStateProb = piTable[-1][pos]['prob'] * self.bigramProbs['fin'][pos]
            if finalStateProb > maxFinalState['prob']:
                maxFinalState = {'prob':finalStateProb, 'bkptr':pos}
        
        piTable.append({'fin':maxFinalState})
                        
        tagSequence = [{'word':None, 'pos':maxFinalState['bkptr']}]
        prevPos = piTable[-1]['fin']['bkptr']
        for i in range(2, len(piTable)+1):
            tagSequence.append({'word': sentence[len(piTable) - i], 'pos':prevPos})
            prevPos = piTable[len(piTable) - i][prevPos]['bkptr']
            
        print 'FINAL VITERBI NETWORK'
        for i in range(0,len(sentence)):
            for pos in self.partsOfSpeech:
                print 'P(' + sentence[i] + '=' + pos + ') = %.10f' % piTable[i][pos]['prob']
                
        print '\nFINAL BACKPTR NETWORK'
        for i in range(1,len(sentence)):
            for pos in self.partsOfSpeech:
                print 'Backptr(' + sentence[i] + '=' + pos + ') = ' + str(piTable[i][pos]['bkptr'])
                
        print '\nBEST TAG SEQUENCE HAS PROBABILITY = %.10f' % piTable[-1]['fin']['prob']
        for i in range(1, len(tagSequence)):
            print tagSequence[i]['word'] + ' -> ' + tagSequence[i]['pos']
                    
    def forwardAlgorithm(self, sent):
        sentence = sent.split()
        
        piTable = [{}]
        for pos in self.partsOfSpeech:
            piTable[0][pos] = self.bigramProbs[pos]['phi'] * self.getLexicalProbs(sentence[0], pos)
        for k in range(1, len(sentence)):
            piTable.append({})
            for pos in self.partsOfSpeech:
                piTable[k][pos] = 0
                # maxTrProb = max(piTable[k-1][prev] * self.bigramProbs[pos][prev] for prev in self.partsOfSpeech);
                for prev in self.partsOfSpeech:
                    # if piTable[k-1][prev] * self.bigramProbs[pos][prev] == maxTrProb:
                    prob = piTable[k-1][prev] * self.bigramProbs[pos][prev] * self.getLexicalProbs(sentence[k], pos)
                    piTable[k][pos] += prob

        print '\nFORWARD ALGORITHM RESULTS'
        for i in range(0,len(sentence)):
            for pos in self.partsOfSpeech:
                print 'P(' + sentence[i] + '=' + pos + ') = %.10f' % piTable[i][pos]

    def readProbs(self, probsPath):
        f = open(probsPath)
        for line in f:
            content = line.lower().split()
            if content[0] in self.partsOfSpeechForReadingFile:
                self.bigramProbs[content[0]][content[1]] = float(content[2])
            else:
                if content[0] not in self.lexicalProbs:
                    self.lexicalProbs[content[0]] = {}
                    # initialize the lexical probabilities to 0.0001
                    # in case they are not included in the probabilities file
                    for pos in self.partsOfSpeechForReadingFile:
                        self.lexicalProbs[content[0]][pos] = 0.0001
                self.lexicalProbs[content[0]][content[1]] = float(content[2])
        # print('Word probabilities')
        # for i in self.lexicalProbs:
            # print(i)
            # print(self.lexicalProbs[i])
        # print('\nTransition probabilities')
        # for i in self.bigramProbs:
            # print(i)
            # print(self.bigramProbs[i])
    
    def readSents(self, sentsPath):
        f = open(sentsPath)
        for line in f:
            self.sentences.append(line.lower())
        # print('\nSentences')
        # for i in self.sentences:
            # print(i)
            # for j in range(0, len(i)):
                # print(j)
    
def main(probsPath, sentsPath):
    viterbi = Viterbi()
    viterbi.readProbs(probsPath)
    viterbi.readSents(sentsPath)
    # viterbi.viterbiNetwork(viterbi.sentences[0])
    for i in viterbi.sentences:
        viterbi.viterbiNetwork(i)
        viterbi.forwardAlgorithm(i)
    
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('incorrect arguments')
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])