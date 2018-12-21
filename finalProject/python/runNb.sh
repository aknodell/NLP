python NaiveBayes.py ../data/untaggedReviews 2 > ../outputs/nb_untagged_2.out
python NaiveBayes.py -b ../data/untaggedReviews 2 > ../outputs/nb_untagged_2_b.out
python NaiveBayes.py -f ../data/untaggedReviews 2 > ../outputs/nb_untagged_2_f.out
python NaiveBayes.py -b -f ../data/untaggedReviews 2 > ../outputs/nb_untagged_2_b_f.out
python NaiveBayes.py -p ../data/taggedReviews 2 > ../outputs/nb_posTag_2.out
python NaiveBayes.py -p -b ../data/taggedReviews 2 > ../outputs/nb_posTag_2_b.out
python NaiveBayes.py -p -f ../data/taggedReviews 2 > ../outputs/nb_posTag_2_f.out
python NaiveBayes.py -p -b -f ../data/taggedReviews 2 > ../outputs/nb_posTag_2_b_f.out
python NaiveBayes.py ../data/taggedReviews 2 > ../outputs/nb_tagged_2.out
python NaiveBayes.py -b ../data/taggedReviews 2 > ../outputs/nb_tagged_2_b.out
python NaiveBayes.py -f ../data/taggedReviews 2 > ../outputs/nb_tagged_2_f.out
python NaiveBayes.py -b -f ../data/taggedReviews 2 > ../outputs/nb_tagged_2_b_f.out