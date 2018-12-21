import sys
import os
import re
import pprint

atPattern = '\W?(?:@|[\W][Aa][Tt][\W]|&#(?:x40|64);|[\W][Ww][Hh][Ee][Rr][Ee][\W])\W?'
dotPattern = '\W?(?:\.|[\W][Dd][Oo][TtMm][\W]|;|&#(?:46|x2[Ee]|59|x3[Bb]);)\W?'
delimPattern = '((?:\w\W)+\w?(?:' + dotPattern + '\W?(?:\w\W)+)*\w?)' + atPattern + '(\W?(?:\w\W)+\w?' + dotPattern + '\w?(?:\W\w)+)'
emailPattern = '([\w]+(?:' + dotPattern + '[\w]+)*)' + atPattern + '((?:[\w]+' + dotPattern + ')+[A-Za-z]{3})(?! [Pp]ort|:|[\w])'
obPattern = 'obfuscate\(\'((?:[\w]+' + dotPattern + ')+[A-Za-z]{3})\',\s*\'([\w]+(?:' + dotPattern + '[\w]+)*)\'\)'

htmlCharsPattern = '(?:&(?:thin|nb|en|em)sp;|&#(?:30|x20|45|x2[Dd]|46|x2[Ee]|160|x[Aa]0);)'
#(?:[^0-9]+\s?|[^0-9]+[1][\s][\(]?|^)
phonePattern = ('(?:^|(?:[\W][1])?(?:[\(\s\.-^]|' + htmlCharsPattern + '|&#(?:40|x28);)+)'
        '([0-9]{3})(?:[\)\s\.-]|' + htmlCharsPattern + '|&#(?:41|x29);)+([0-9]{3})(?:[\s\.-]|' + htmlCharsPattern + ')+([0-9]{4})(?:[^0-9]|$)')

""" 
TODO
This function takes in a filename along with the file object (actually
a StringIO object) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""
def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        obMatches = re.findall(obPattern, line)
        for om in obMatches:
            email = om[1] + '@' + om[0]
            res.append((name, 'e', email))
        delimMatches = re.findall(delimPattern,line)
        for dm in delimMatches:
            delimMatch = '%s@%s' % dm
            delimMatch = re.sub(dotPattern, '.', delimMatch)
            delimMatch = re.sub('[^\w^@^\.]' , '', delimMatch)
            if re.compile(emailPattern).match(delimMatch):
                res.append((name, 'e', delimMatch))
        emailMatches = re.findall(emailPattern,line)
        for em in emailMatches:
            email = '%s@%s' % em
            email = re.sub(dotPattern, '.', email)
            res.append((name, 'e', email))
            
        phoneMatches = re.findall(phonePattern, line)
        for pm in phoneMatches:
            phone = '%s-%s-%s' % pm
            res.append((name, 'p', phone))
            
    return res

"""
You should not need to edit this function, nor should you alter
its interface
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print('True Positives (%d): ' % len(tp))
    pp.pprint(tp)
    print('False Positives (%d): ' % len(fp))
    pp.pprint(fp)
    print('False Negatives (%d): ' % len(fn))
    pp.pprint(fn)
    print('Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn)))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('usage:\tSpamLord.py <data_dir> <gold_file>')
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
