from pymongo import MongoClient
from tpclustering.repository.wikipageRepository import MongoWikipageRepository
from tpclustering.clustering.clusterer import HighPageRankSeedWriteToDbClusterer
from tpclustering.similarity.similarity_calculator import JaccardSimilarityCalculator

client = MongoClient()
repository = MongoWikipageRepository(client=client)

# clusterer = HighPageRankSeedClusterer(repository=repository, coverageRate=0.01, minSimilarity=0.3,
#                                       similarityCalc=JaccardSimilarityCalculator())
clusterer = HighPageRankSeedWriteToDbClusterer(repository=repository, coverageRate=0.01, minSimilarity=0.3,
                                      similarityCalc=JaccardSimilarityCalculator())
clusterer.computeCluster()


print("Finish clustering")

