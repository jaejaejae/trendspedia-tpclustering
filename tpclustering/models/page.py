class Page(object):
    def __init__(self, id, keywords, scores, inlinks, outlinks, pagerank):
        self.id = id
        self.keywords = keywords
        self.scores = scores
        self.inlinks = inlinks
        self.outlinks = outlinks
        self.pagerank = pagerank