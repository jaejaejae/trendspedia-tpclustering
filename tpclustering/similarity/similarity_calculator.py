from abc import ABCMeta, abstractmethod

class SimilarityCalculator(object):
    __metaclass__=ABCMeta

    @abstractmethod
    def computeSimilarity(self, page1, page2):
        return

class JaccardSimilarityCalculator(SimilarityCalculator):
    def computeSimilarity(self, page1, page2):
        setP1 = set(page1.keywords)
        setP2 = set(page2.keywords)
        denom = setP1.union(setP2)
        numer = setP1.intersection(setP2)
        if len(denom) == 0: return 0
        return 1.0*len(numer)/len(denom)