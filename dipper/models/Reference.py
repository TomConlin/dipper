import logging
from dipper.graph.Graph import Graph
from dipper.models.Model import Model

__author__ = 'nlw'

LOG = logging.getLogger(__name__)


class Reference:
    """
    To model references for associations
        (such as journal articles, books, etc.).

    By default, references will be typed as "documents",
        unless if the type is set otherwise.

    If a short_citation is set, this will be used for the individual's label.
        We may wish to subclass this later.

    """

    def __init__(self, graph, ref_id=None, ref_type=None):
        if isinstance(graph, Graph):
            self.graph = graph
        else:
            raise ValueError("%s is not a graph", graph)

        # assert ref_id is not None

        self.ref_id = ref_id
        self.ref_url = None
        self.title = None
        self.year = None
        self.author_list = None
        self.short_citation = None

        self.model = Model(self.graph)
        self.globaltt = self.graph.globaltt
        self.globaltcid = self.graph.globaltcid
        self.curie_map = self.graph.curie_map

        if ref_type is None:
            self.ref_type = self.globaltt['document']
        else:
            self.ref_type = ref_type
            if ref_type[:4] not in ('IAO:', 'SIO:'):
                LOG.warning("Got Pub ref type of:  %s", ref_type)

        if ref_id is not None and ref_id[:4] == 'http':
            self.ref_url = ref_id

    def setTitle(self, title):
        self.title = title

    def setYear(self, year):
        self.year = year

    def setType(self, reference_type):
        self.ref_type = reference_type

    def setAuthorList(self, author_list):
        """

        :param author_list: Array of authors
        :return:
        """

        self.author_list = author_list

    def addAuthor(self, author):
        self.author_list += [author]

    def setShortCitation(self, citation):
        self.short_citation = citation

    def addPage(
            self, subject_id, page_url, subject_category=None, page_category=None
    ):
        self.graph.addTriple(
            subject_id,
            self.globaltt['page'],   # foaf:page  not  <sio:web page>
            page_url,
            object_is_literal=False,    # URL is not a literal
            subject_category=subject_category,
            object_category=page_category
        )

    def addTitle(self, subject_id, title):
        if title is not None and title != '':
            self.graph.addTriple(
                subject_id, self.globaltt['title (dce)'], title, object_is_literal=True
            )

    def addRefToGraph(self):

        cite = self.short_citation
        if cite is None and self.title is not None:
            cite = self.title

        if self.ref_url is not None:
            if self.title is not None:
                self.addTitle(self.ref_url, self.title)
            self.model.addType(self.ref_url, self.ref_type)
            if cite is not None:
                self.model.addLabel(self.ref_url, cite)
        elif self.ref_id is not None:
            self.model.addIndividualToGraph(self.ref_id, cite, self.ref_type)
            if self.title is not None:
                self.addTitle(self.ref_id, self.title)
        else:
            # should never be true
            LOG.error("You are missing an identifier for a reference.")

        # TODO what is the property here to add the date?
        # if self.year is not None:
        #    gu.addTriple()

        # if self.author_list is not None:
        #    for auth in self.author_list:
        #        gu.addTriple(
        #           graph, self.ref_id, self.props['has_author'], auth, True)
