from abc import ABCMeta, abstractmethod
from tpclustering.models.page import Page


class WikipageRepository(object):
    __metaclass__ = ABCMeta

    def getPage(self, pagerankOrder=None, id=None):
        if pagerankOrder != None:
            return self.getPageWithPageRankOrder(pagerankOrder)
        elif id != None:
            return self.getPageWithId(id)
        else:
            return None

    @abstractmethod
    def getPageWithPageRankOrder(self, pagerankOrder):
        return None

    @abstractmethod
    def getPageWithId(self, id):
        return None

    @abstractmethod
    def getTotalPages(self):
        return None


class MongoWikipageRepository(WikipageRepository):
    def __init__(self, client):
        wikiDb = client.wiki
        self.keywordCollection = wikiDb['keyword_score_extraction']
        self.pagerankLinkCollection = wikiDb['pagerank_hierarchical_graph']
        self.pagerankCollection = wikiDb['pagerank_result_redirect_merged_graph_namespace_0']
        stat = wikiDb.command('collStats', 'pagerank_result_redirect_merged_graph_namespace_0')
        self.size = stat["count"]

    def getTotalPages(self):
        return self.size

    def getPageWithPageRankOrder(self, pagerankOrder):
        result = self.pagerankCollection.find().sort("pagerank_score", -1).skip(pagerankOrder).limit(1)[0]
        id = result[u'_id']
        return self.getPageWithId(id)

    def getPageWithId(self, id):
        keywordScore = self.keywordCollection.find_one({"_id": id})
        keywords = keywordScore["keywords"] if keywordScore != None else list()
        scores = keywordScore["scores"] if keywordScore != None else list()
        pagerankLink = self.pagerankLinkCollection.find_one({"_id": id})
        inlinks = pagerankLink["in_hierarchy_links"]
        outlinks = pagerankLink["out_hierarchy_links"]
        pagerank = self.pagerankCollection.find_one({"_id": id})
        page = Page(id=id, keywords=keywords, scores=scores, inlinks=inlinks, outlinks=outlinks, pagerank=pagerank)
        return page