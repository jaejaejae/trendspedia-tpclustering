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

    @abstractmethod
    def getPagerank(self, id):
        return None

    @abstractmethod
    def addChild(self, root, child):
        return None

    @abstractmethod
    def hasExplored(self, page):
        return None

    @abstractmethod
    def addRootnode(self, page):
        return None

    @abstractmethod
    def updateExplored(self, page):
        return None

class MongoWikipageRepository(WikipageRepository):
    def __init__(self, client):
        wikiDb = client.wiki
        self.keywordCollection = wikiDb['keyword_score_extraction']
        self.pagerankLinkCollection = wikiDb['pagerank_hierarchical_graph']
        self.pagerankCollection = wikiDb['pagerank_result_redirect_merged_graph_namespace_0']
        self.orderTreeCollection = wikiDb['pagerank_sim_graph']
        stat = wikiDb.command('collStats', 'pagerank_result_redirect_merged_graph_namespace_0')
        self.size = stat["count"]

    def getTotalPages(self):
        return self.size

    def getPageWithPageRankOrder(self, pagerankOrder):
        if pagerankOrder >= self.size: return None
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

    def getPagerank(self, id):
        item = self.pagerankCollection.find_one({"_id": id})
        pagerank = item[u'pagerank_score']
        return pagerank

    def addChild(self, root, child):
        rootNode = self.orderTreeCollection.find_one({"_id": root.id})
        if 'children' not in rootNode:
            rootNode['children'] = []
        if child.id not in rootNode['children']:
            rootNode['children'].append(child.id)
            self.orderTreeCollection.update({"_id": root.id}, {"$set": {"children": rootNode["children"]}})
        childNode = self.orderTreeCollection.find_one({"_id": child.id})
        if childNode == None:
            childNode = {"_id": child.id, "explored": False, "parents": [], "children": []}
            self.orderTreeCollection.insert(childNode)
        if 'parents' not in childNode:
            childNode['parents'] = []
        if root.id not in childNode['parents']:
            childNode['parents'].append(root.id)
            self.orderTreeCollection.update({"_id": child.id}, {"$set": {"parents": childNode["parents"]}})

    def hasExplored(self, page):
        node = self.orderTreeCollection.find_one({"_id": page.id})
        print(page.id)
        if node == None: return False
        else: return node['explored']

    def addRootnode(self, page):
        rootNode = self.orderTreeCollection.find_one({"_id": "root"})
        if 'children' not in rootNode:
            rootNode['children'] = []
        if page.id not in rootNode['children']:
            rootNode['children'].append(page.id)
            self.orderTreeCollection.update({"_id": "root"}, {"$set": {"children": rootNode["children"]}})
        childNode = self.orderTreeCollection.find_one({"_id": page.id})
        if childNode == None:
            childNode = {"_id": page.id,"explored": False, "parents": [], "children": []}
            self.orderTreeCollection.insert(childNode)
        if 'parents' not in childNode:
            childNode['parents'] = []
        if "root" not in childNode['parents']:
            childNode['parents'].append("root")
            self.orderTreeCollection.update({"_id": page.id}, {"$set": {"parents": childNode["parents"]}})

    def updateExplored(self, page):
        self.orderTreeCollection.update({"_id": page.id}, {"$set": {'explored': True}})
