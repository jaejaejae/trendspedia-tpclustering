import unittest
from tpclustering.models.page import Page
from tpclustering.similarity.similarity_calculator import JaccardSimilarityCalculator

class TestSimilaity(unittest.TestCase):

    def test_jaccard_similarity(self):
        p1 = Page(keywords = ["a", "b", "c"], similarityCalculator=JaccardSimilarityCalculator(), id=0, scores=0, inlinks=0, outlinks=0,  pagerank=0)
        p2 = Page(keywords = ["d", "c"], similarityCalculator=JaccardSimilarityCalculator(), id=0, scores=0, inlinks=0, outlinks=0,  pagerank=0)
        self.assertTrue(p1.computeSimilarity(p2), 1/4)
        self.assertTrue(p2.computeSimilarity(p1), 1/4)



if __name__ == '__main__':
    unittest.main()