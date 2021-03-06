from abc import ABCMeta, abstractmethod
from collections import deque
from tpclustering.models.cluster import Cluster
from tpclustering.repository.wikipageRepository import MongoWikipageRepository
from pymongo import MongoClient


class Clusterer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def computeCluster(self):
        return


class HighPageRankSeedClusterer(Clusterer):
    def __init__(self, repository, coverageRate, minSimilarity, similarityCalc):
        self.repository = repository
        self.coverageRate = coverageRate
        self.minSimilarity = minSimilarity
        self.similarityCalc = similarityCalc
        self.sortedRoots = []

    def computeCluster(self):
        currentPagerankOrder = 0
        currentCoveredNodes = set()
        exploredNodes = set()
        desiredCoveredNodeSize = self.coverageRate * self.repository.getTotalPages()
        print(desiredCoveredNodeSize)
        print(self.repository.getTotalPages())
        # while(len(currentCoveredNodes) < desiredCoveredNodeSize):
        # page = self.repository.getPage(pagerankOrder = currentPagerankOrder)
        #     while(page.id in currentCoveredNodes): page = self.repository.getPage(pagerankOrder = currentPagerankOrder)
        queue = deque()
        pageClusters = dict()
        clusters = list()
        firstPage = self.repository.getPage(pagerankOrder=currentPagerankOrder)
        queue.append(firstPage)
        self.sortedRoots.append(firstPage)
        while (len(currentCoveredNodes) < desiredCoveredNodeSize):
            # print(">>>>>>>>>>>>>>>>" + str(len(currentCoveredNodes)) + "\t" +  str(len(currentCoveredNodes)/desiredCoveredNodeSize))
            page = None
            if len(queue) > 0:
                page = queue.popleft()
            else:
                while page == None or page in exploredNodes:
                    page = self.repository.getPage(pagerankOrder=currentPagerankOrder)
                    currentPagerankOrder = currentPagerankOrder + 1
                self.sortedRoots.append(page)
            if page.id not in exploredNodes:
                exploredNodes.add(page.id)
                if page.id in pageClusters:
                    cluster = pageClusters[page.id]
                else:
                    # print("a new cluster")
                    cluster = Cluster(page)
                    clusters.append(cluster)
                # cluster = pageClusters[page.id] if page.id in pageClusters else Cluster(page)
                pageClusters[page.id] = cluster
                currentCoveredNodes.add(page.id)
                exploredNodes.add(page.id)
                self.addNodesToCluster(pageClusters, currentCoveredNodes, page, queue, cluster, page.inlinks)
                self.addNodesToCluster(pageClusters, currentCoveredNodes, page, queue, cluster, page.outlinks)
                # print(len(cluster.elements))
                # print(str(map(lambda x: str(x.id), cluster.elements)))

        for cluster in clusters:
            print("=============================")
            print(len(cluster.elements))
            print(str(cluster.seed.id))
            print(str(map(lambda x: str(x.id), cluster.elements)))

    def addNodesToCluster(self, pageClusters, currentCoveredNodes, page, queue, cluster, children):
        for inId in children:
            inPage = self.repository.getPage(id=inId)
            similarity = self.similarityCalc.computeSimilarity(page, inPage)
            # print(similarity)
            if (similarity >= self.minSimilarity):
                cluster.addElements(inPage)
                pageClusters[inId] = cluster
                currentCoveredNodes.add(inId)
                queue.append(inPage)


class HighPageRankSeedWriteToDbClusterer(Clusterer):
    def __init__(self, repository, coverageRate, minSimilarity, similarityCalc):
        self.repository = repository
        self.coverageRate = coverageRate
        self.minSimilarity = minSimilarity
        self.similarityCalc = similarityCalc
        self.sortedRoots = []
        self.pagerankCount = 0
        self.processingQueue = deque()
        self.client = MongoClient()

    def resetConnection(self):
        self.client.close()
        self.repository = MongoWikipageRepository()

    def computeCluster(self):
        page = self.getNextHighestPagerank()
        self.repository.addRootnode(page)
        self.processingQueue.append(page)
        while True:
            if len(self.processingQueue) == 0:
                page = self.getNextHighestPagerank()
                self.repository.addRootnode(page)
                if page!= None:
                    self.processingQueue.append(page)
                else:
                    break
            page = self.processingQueue.popleft()
            self.constructPartialOrderTree(page, map(lambda x: self.repository.getPage(id=x), page.inlinks))
            self.constructPartialOrderTree(page, map(lambda x: self.repository.getPage(id=x), page.outlinks))
            self.repository.updateExplored(page)

    def constructPartialOrderTree(self, root, potentialChildren):
        for potentialChild in potentialChildren:
            if potentialChild.pagerank < root.pagerank and \
                            self.similarityCalc.computeSimilarity(root,potentialChild) >= self.minSimilarity:
                print "add: %d %d" % (root.id, potentialChild.id)
                self.repository.addChild(root, potentialChild)
                self.processingQueue.append(potentialChild)

    def getNextHighestPagerank(self):
        page = None
        while page == None or self.repository.hasExplored(page):
            page = self.repository.getPage(pagerankOrder=self.pagerankCount)
            self.pagerankCount = self.pagerankCount + 1
            if page == None: return None
        return page