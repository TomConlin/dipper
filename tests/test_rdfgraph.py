#!/usr/bin/env python3

import os
import unittest
import logging
from rdflib import URIRef
from dipper import curie_map
from dipper.graph.RDFGraph import RDFGraph
from dipper.utils.CurieUtil import CurieUtil

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RDFGraphTestCase(unittest.TestCase):

    def setUp(self):
        self.graph = RDFGraph()

        this_curie_map = curie_map.get()
        self.cutil = CurieUtil(this_curie_map)

        # stuff to make test triples
        self.test_cat_subj = "http://www.google.com"
        self.test_cat_default_pred = self.cutil.get_uri("biolink:category")
        self.test_cat_nondefault_pred = self.cutil.get_uri("rdf:type")
        self.test_cat_default_category = self.cutil.get_uri("biolink:NamedThing")
        self.test_cat_nondefault_category = self.cutil.get_uri("biolink:Gene")
        self.test_cat_type = self.cutil.get_uri("rdf:type")
        self.test_cat_class = self.cutil.get_uri("rdf:class")

    def tearDown(self):
        self.graph = None

    def test_add_triple_makes_triple(self):
        """
        test that addTriple() makes at least one triple
        """
        self.graph.addTriple(subject_id=self.test_cat_subj,
                             predicate_id="rdf:type",
                             obj="rdf:class")
        self.assertTrue(len(self.graph) > 0, "addTriples() didn't make >=1 triple")

    def test_add_triple_subject_category_assignment(self):
        """
        test that addTriple() correctly assigns subject category
        """
        self.graph.addTriple(subject_id=self.test_cat_subj,
                             predicate_id="rdf:comment",
                             obj="website",
                             subject_category=self.test_cat_nondefault_category)
        triples = list(self.graph.triples((URIRef(self.test_cat_subj),
                                          URIRef(self.test_cat_default_pred),
                                          None)))
        self.assertEqual(len(triples), 1,
                         "addTriples() didn't make exactly one triple subject category")
        self.assertEqual(triples[0][2], URIRef(self.test_cat_nondefault_category),
                         "addTriples() didn't assign the right triple subject category")

    def test_add_triple_object_category_assignment(self):
        """
        test that addTriple() correctly assigns object category
        """
        self.graph.addTriple(subject_id=self.test_cat_subj,
                             predicate_id=self.test_cat_type,
                             obj=self.test_cat_class,
                             object_category=self.test_cat_nondefault_category)
        triples = list(self.graph.triples((URIRef(self.test_cat_class),
                                           URIRef(self.test_cat_default_pred),
                                           None)))
        self.assertEqual(len(triples), 1,
                         "addTriples() didn't make exactly one triple object category")
        self.assertEqual(triples[0][2], URIRef(self.test_cat_nondefault_category),
                         "addTriples() didn't assign the right triple object category")

    def read_graph_from_turtle_file(self, f):
        """
        This will read the specified file into a graph.  A simple parsing test.
        :param f:
        :return:

        """
        vg = RDFGraph()
        p = os.path.abspath(f)
        logger.info("Testing reading turtle file from %s", p)
        vg.parse(f, format="turtle")
        logger.info('Found %s graph nodes in %s', len(vg), p)
        self.assertTrue(len(vg) > 0, "No nodes found in "+p)

        return

    def read_graph_into_owl(self, f):
        """
        test if the ttl can be parsed by owlparser
        this expects owltools to be accessible from commandline
        :param f: file of ttl
        :return:
        """

        import subprocess
        from subprocess import check_call

        status = check_call(["owltools", f], stderr=subprocess.STDOUT)
        # returns zero is success!
        if status != 0:
            logger.error(
                'finished verifying with owltools with status %s', status)
        self.assertTrue(status == 0)

        return

    def test_make_category_triple_default(self):
        """
        test that method adds category triple to graph correctly (default pred and obj)
        """
        self.graph._make_category_triple(self.test_cat_subj)

        triples = list(self.graph.triples((None, None, None)))
        self.assertEqual(len(triples), 1, "method didn't make exactly one triple")
        self.assertEqual(triples[0][0], URIRef(self.test_cat_subj),
                         "didn't assign correct subject")
        self.assertEqual(triples[0][1], URIRef(self.test_cat_default_pred),
                         "didn't assign correct predicate")
        self.assertEqual(triples[0][2], URIRef(self.test_cat_default_category),
                         "didn't assign correct category")

    def test_make_category_triple_non_default_category(self):
        """
        test that method adds category triple to graph correctly
        """
        self.graph._make_category_triple(self.test_cat_subj,
                                         self.test_cat_nondefault_category)
        triples = list(self.graph.triples((None, None, None)))

        self.assertEqual(len(triples), 1, "method didn't make exactly one triple")
        self.assertEqual(URIRef(self.test_cat_nondefault_category),
                         triples[0][2],
                         "didn't assign correct (non-default) category")

    def test_make_category_triple_non_default_pred(self):
        """
        test that method adds category triple to graph correctly (non default pred)
        """
        self.graph._make_category_triple(self.test_cat_subj,
                                         self.test_cat_default_category,
                                         predicate=self.test_cat_nondefault_pred)
        triples = list(self.graph.triples((None, None, None)))
        self.assertEqual(len(triples), 1, "method didn't make exactly one triple")
        self.assertEqual(URIRef(self.test_cat_nondefault_pred),
                         triples[0][1],
                         "didn't assign correct (non-default) category")

    def test_make_category_triple_category_none_should_emit_named_thing(self):
        """
        test that method adds category triple to graph correctly (default pred and obj)
        """
        self.graph._make_category_triple(self.test_cat_subj, category=None)
        triples = list(self.graph.triples((None, None, None)))
        self.assertEqual(len(triples), 1, "method didn't make exactly one triple")
        self.assertEqual(URIRef(self.test_cat_default_category),
                         triples[0][2],
                         "didn't assign correct default category")

    def test_is_literal(self):
        """
        test that method infers type (either literal or CURIE) correctly
        """
        self.assertTrue(self.graph._is_literal("1"))
        self.assertTrue(not self.graph._is_literal("foo:bar"))
        self.assertTrue(not self.graph._is_literal("http://www.zombo.com/"))
        self.assertTrue(not self.graph._is_literal("https://www.zombo.com/"))
        self.assertTrue(not self.graph._is_literal("ftp://ftp.1000genomes.ebi.ac.uk/"))


if __name__ == '__main__':
    unittest.main()