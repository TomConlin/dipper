import csv
import gzip
import re
import logging
import os

from dipper.sources.Source import Source
from dipper.models.Genotype import Genotype
from dipper.models.Dataset import Dataset
from dipper.models.assoc.G2PAssoc import G2PAssoc
from dipper.utils.GraphUtils import GraphUtils
from dipper import curie_map


logger = logging.getLogger(__name__)


class IMPC(Source):
    """
    From the [IMPC](http://mousephenotype.org) website:
    The IMPC is generating a knockout mouse strain for every protein coding gene by using the
    embryonic stem cell resource generated by the International Knockout Mouse Consortium (IKMC).
    Systematic broad-based phenotyping is performed by each IMPC center using standardized
    procedures found within the International Mouse Phenotyping Resource of Standardised
    Screens (IMPReSS) resource. Gene-to-phenotype associations are made by a versioned
    statistical analysis with all data freely available by this web portal and by several
    data download features.

    Here, we pull the data and model the genotypes using GENO and the genotype-to-phenotype associations
    using the OBAN schema.

    We use all identifiers given by the IMPC with a few exceptions:

    *  For identifiers that IMPC provides, but does not resolve, we instantiate them as BNodes.  Examples include
       things with the pattern of:  EUROALL, EUROCURATE, NULL-*,

    *  We mint three identifiers:
       1.  Intrinsic genotypes not including sex, based on:
         * colony_id (ES cell line + phenotyping center)
         * strain
         * zygosity
       2.  For the Effective genotypes that are attached to the phenotypes:
         * colony_id (ES cell line + phenotyping center)
         * strain
         * zygosity
         * sex
       3.  Associations based on
           effective_genotype_id + phenotype_id + phenotyping_center +
           pipeline_stable_id + procedure_stable_id + parameter_stable_id

    We DO NOT yet add the assays as evidence for the G2P associations here.  (To be added in the future.)

    """

    # TODO change to ALL_genotype_phenotype.csv.gz
    files = {
        # 'impc': {'file': 'IMPC_genotype_phenotype.csv.gz',
        #          'url': 'ftp://ftp.ebi.ac.uk/pub/databases/impc/latest/csv/IMPC_genotype_phenotype.csv.gz'},
        # 'euro': {'file': 'EuroPhenome_genotype_phenotype.csv.gz',
        #          'url': 'ftp://ftp.ebi.ac.uk/pub/databases/impc/latest/csv/EuroPhenome_genotype_phenotype.csv.gz'},
        # 'mgd': {'file': 'MGP_genotype_phenotype.csv.gz',
        #         'url': 'ftp://ftp.ebi.ac.uk/pub/databases/impc/latest/csv/MGP_genotype_phenotype.csv.gz'},
        # '3i': {'file': '3I_genotype_phenotype.csv.gz',
        #         'url': 'ftp://ftp.ebi.ac.uk/pub/databases/impc/latest/csv/3I_genotype_phenotype.csv.gz'},
        'all': {'file': 'ALL_genotype_phenotype.csv.gz',
                'url': 'ftp://ftp.ebi.ac.uk/pub/databases/impc/latest/csv/ALL_genotype_phenotype.csv.gz'},
        'checksum': {'file': 'checksum.md5',
                     'url': 'ftp://ftp.ebi.ac.uk/pub/databases/impc/latest/csv/checksum.md5'},
    }

    # TODO move these into the conf.json
    # the following are gene ids for testing
    test_ids = ["MGI:109380", "MGI:1347004", "MGI:1353495", "MGI:1913840", "MGI:2144157",
                "MGI:2182928", "MGI:88456", "MGI:96704", "MGI:1913649", "MGI:95639", "MGI:1341847",
                "MGI:104848", "MGI:2442444", "MGI:2444584", "MGI:1916948", "MGI:107403", "MGI:1860086",
                "MGI:1919305", "MGI:2384936", "MGI:88135", "MGI:1913367", "MGI:1916571", "MGI:2152453"]

    def __init__(self):
        Source.__init__(self, 'impc')

        # update the dataset object with details about this resource
        self.dataset = Dataset('impc', 'IMPC', 'http://www.mousephenotype.org', None,
                               'https://raw.githubusercontent.com/mpi2/PhenotypeArchive/master/LICENSE')

        # TODO add a citation for impc dataset as a whole
        # :impc cito:citesAsAuthority PMID:24194600

        return

    def fetch(self, is_dl_forced=False):
        self.get_files(is_dl_forced)
        logger.info("Verifying checksums...")
        if self.compare_checksums():
            logger.debug('Files have same checksum as reference')
        else:
            raise Exception('Reference checksums do not match disk')
        return

    def parse(self, limit=None):
        """
        IMPC data is delivered in three separate csv files, which we process iteratively and write out as
        one large graph.

        :param limit:
        :return:
        """
        if limit is not None:
            logger.info("Only parsing first %s rows fo each file", str(limit))

        logger.info("Parsing files...")

        if self.testOnly:
            self.testMode = True

        # for f in ['impc', 'euro', 'mgd', '3i']:
        for f in ['all']:
            file = '/'.join((self.rawdir, self.files[f]['file']))
            self._process_data(file, limit)

        logger.info("Finished parsing")

        self.load_bindings()

        logger.info("Found %d nodes", len(self.graph))
        return

    def _process_data(self, raw, limit=None):
        logger.info("Processing Data from %s", raw)
        gu = GraphUtils(curie_map.get())

        if self.testMode:
            g = self.testgraph
        else:
            g = self.graph

        geno = Genotype(g)
        line_counter = 0
        gu.loadAllProperties(g)
        gu.loadObjectProperties(g, geno.object_properties)

        # with open(raw, 'r', encoding="utf8") as csvfile:
        with gzip.open(raw, 'rt') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='\"')
            next(filereader, None)  # skip the header row
            for row in filereader:
                line_counter += 1

                (marker_accession_id, marker_symbol, phenotyping_center, colony, sex, zygosity, allele_accession_id,
                 allele_symbol, allele_name, strain_accession_id, strain_name, project_name, project_fullname,
                 pipeline_name, pipeline_stable_id, procedure_stable_id, procedure_name,
                 parameter_stable_id, parameter_name,
                 top_level_mp_term_id, top_level_mp_term_name, mp_term_id, mp_term_name,
                 p_value, percentage_change, effect_size, statistical_method, resource_name) = row

                if self.testMode and marker_accession_id not in self.test_ids:
                    continue

                ###### cleanup some of the identifiers ######
                zygosity_id = self._map_zygosity(zygosity)

                # colony ids sometimes have <> in them, and break our system; replace these with underscores
                colony_id = '_'+re.sub('[<>\s]', '_', colony)
                if self.nobnodes:
                    colony_id = ':'+colony_id

                if not re.match('MGI', allele_accession_id):
                    allele_accession_id = '_IMPC-'+re.sub(':', '', allele_accession_id)
                    if self.nobnodes:
                        allele_accession_id = ':'+allele_accession_id
                if re.search('EUROCURATE', strain_accession_id):
                    strain_accession_id = '_'+strain_accession_id   # the eurocurate links don't resolve at IMPC
                    if self.nobnodes:
                        strain_accession_id = ':'+strain_accession_id
                elif not re.match('MGI', strain_accession_id):
                    logger.info("Found a strange strain accession...%s", strain_accession_id)
                    strain_accession_id = 'IMPC:'+strain_accession_id

                ##############    BUILD THE COLONY    #############
                # first, let's describe the colony that the animals come from
                # The Colony ID refers to the ES cell clone used to generate a mouse strain.
                # Terry sez: we use this clone ID to track ES cell -> mouse strain -> mouse phenotyping.
                # The same ES clone maybe used at multiple centers, so we have to concatenate the two to have a
                # unique ID.
                # some useful reading about generating mice from ES cells:
                # http://ki.mit.edu/sbc/escell/services/details

                # here, we'll make a genotype that derives from an ES cell with a given allele.  the strain is not
                # really attached to the colony.

                # the colony/clone is reflective of the allele, with unknown zygosity
                stem_cell_class = 'CL:0000034'
                gu.addIndividualToGraph(g, colony_id, colony, stem_cell_class)

                # vslc of the colony has unknown zygosity
                # note that we will define the allele (and it's relationship to the marker, etc.) later
                vslc_colony = '_'+allele_accession_id+geno.zygosity['indeterminate']
                vslc_colony = re.sub(':', '', vslc_colony)
                if self.nobnodes:
                    vslc_colony = ':'+vslc_colony
                vslc_colony_label = allele_symbol+'/<?>'
                gu.addIndividualToGraph(g, vslc_colony, vslc_colony_label,
                                        geno.genoparts['variant_single_locus_complement'])
                geno.addPartsToVSLC(vslc_colony, allele_accession_id, None, geno.zygosity['indeterminate'],
                                    geno.object_properties['has_alternate_part'])
                gu.addTriple(g, colony_id, geno.object_properties['has_genotype'], vslc_colony)

                ##############    BUILD THE ANNOTATED GENOTYPE    #############
                # now, we'll build the genotype of the individual that derives from the colony/clone
                # genotype that is attached to phenotype = colony_id + strain + zygosity + sex
                # (and is derived from a colony)

                genotype_id = self.make_id((colony_id+phenotyping_center+zygosity+strain_accession_id))
                geno.addDerivesFrom(genotype_id, colony_id)

                # as with MGI, the allele is the variant locus.  IF the marker is not known, we will call it a
                # sequence alteration.  otherwise, we will create a BNode for the sequence alteration.
                sequence_alteration_id = variant_locus_id = variant_locus_name = sequence_alteration_name = None

                # extract out what's within the <> to get the symbol
                if re.match('.*<.*>', allele_symbol):
                    sequence_alteration_name = re.match('.*<(.*)>', allele_symbol).group(1)
                else:
                    sequence_alteration_name = allele_symbol

                if marker_accession_id is not None and marker_accession_id != '':
                    variant_locus_id = allele_accession_id
                    variant_locus_name = allele_symbol
                    variant_locus_type = geno.genoparts['variant_locus']
                    geno.addGene(marker_accession_id, marker_symbol, geno.genoparts['gene'])
                    geno.addAllele(variant_locus_id, variant_locus_name, variant_locus_type, None)
                    geno.addAlleleOfGene(variant_locus_id, marker_accession_id)

                    sequence_alteration_id = '_seqalt'+re.sub(':', '', allele_accession_id)
                    if self.nobnodes:
                        sequence_alteration_id = ':'+sequence_alteration_id
                    geno.addSequenceAlterationToVariantLocus(sequence_alteration_id, variant_locus_id)

                else:
                    sequence_alteration_id = allele_accession_id

                # IMPC contains targeted mutations with either gene traps, knockouts, insertion/intragenic deletions.
                geno.addSequenceAlteration(sequence_alteration_id, sequence_alteration_name,
                                           geno.genoparts['insertion'])

                allele1_id = variant_locus_id
                allele2_id = allele2_rel = None
                # Making VSLC labels from the various parts, can change later if desired.
                if zygosity == 'heterozygote':
                    vslc_name = variant_locus_name+'/'+re.sub('<.*', '<+>', variant_locus_name)
                    allele2_id = None
                elif zygosity == 'homozygote':
                    vslc_name = variant_locus_name+'/'+variant_locus_name
                    allele2_id = allele_accession_id
                    allele2_rel = geno.object_properties['has_alternate_part']
                elif zygosity == 'hemizygote':
                    vslc_name = variant_locus_name+'/'+re.sub('<.*', '<0>', variant_locus_name)
                    allele2_id = None
                elif zygosity == 'not_applicable':
                    vslc_name = variant_locus_name+'/'+re.sub('<.*', '<?>', variant_locus_name)
                    allele2_id = None
                else:
                    logger.warn("found unknown zygosity %s", zygosity)
                    break

                # Add the VSLC
                vslc_id = '_' + '-'.join((marker_accession_id, allele_accession_id, zygosity))
                vslc_id = re.sub(':', '', vslc_id)
                if self.nobnodes:
                    vslc_id = ':'+vslc_id
                gu.addIndividualToGraph(g, vslc_id, vslc_name, geno.genoparts['variant_single_locus_complement'])
                geno.addPartsToVSLC(vslc_id, allele1_id, allele2_id, zygosity_id,
                                    geno.object_properties['has_alternate_part'], allele2_rel)

                # add vslc to genotype
                geno.addVSLCtoParent(vslc_id, genotype_id)

                # Add the genomic background
                # create the genomic background id and name
                if strain_accession_id != '':
                    genomic_background_id = strain_accession_id
                else:
                    genomic_background_id = None

                genotype_name = vslc_name
                if genomic_background_id is not None:
                    geno.addGenotype(genomic_background_id, strain_name, geno.genoparts['genomic_background'])

                    # make a phenotyping-center-specific strain to use as the background
                    pheno_center_strain_label = strain_name+'/'+phenotyping_center
                    pheno_center_strain_id = '-'.join((re.sub(':', '', genomic_background_id),
                                                           re.sub('\s', '_', phenotyping_center)))
                    if not re.match('^_', pheno_center_strain_id):
                        pheno_center_strain_id = '_'+pheno_center_strain_id
                    if self.nobnodes:
                        pheno_center_strain_id = ':'+pheno_center_strain_id
                    geno.addGenotype(pheno_center_strain_id, pheno_center_strain_label,
                                     geno.genoparts['genomic_background'])
                    geno.addDerivesFrom(pheno_center_strain_id, genomic_background_id)

                    # Making genotype labels from the various parts, can change later if desired.
                    # since the genotype is reflective of the place it got made, should put that in to disambiguate
                    genotype_name = genotype_name+' ['+pheno_center_strain_label+']'
                    geno.addGenomicBackgroundToGenotype(pheno_center_strain_id, genotype_id)

                geno.addGenotype(genotype_id, genotype_name)

                # Add the effective genotype, which is currently the genotype + sex
                effective_genotype_id = self.make_id((allele_accession_id+zygosity+strain_accession_id+sex))
                effective_genotype_label = genotype_name+' ('+sex+')'
                geno.addGenotype(effective_genotype_id, effective_genotype_label, geno.genoparts['effective_genotype'])
                geno.addParts(genotype_id, effective_genotype_id, geno.object_properties['has_alternate_part'])
                geno.addDerivesFrom(effective_genotype_id, colony_id)  # this is redundant, but i'll keep in in for now

                # Add the taxon as a class
                taxon_id = 'NCBITaxon:10090'  # map to Mus musculus
                gu.addClassToGraph(g, taxon_id, None)

                if genomic_background_id is not None and genomic_background_id != '':
                    # Add the taxon to the genomic_background_id
                    geno.addTaxon(taxon_id, genomic_background_id)
                else:
                    # add it as the genomic background
                    geno.addTaxon(taxon_id, genotype_id)

                ##############    BUILD THE G2P ASSOC    #############
                # from an old email dated July 23 2014:
                # Phenotypes associations are made to imits colony_id+center+zygosity+gender

                phenotype_id = mp_term_id

                eco_id = "ECO:0000059"  # experimental_phenotypic_evidence This was used in ZFIN

                # the association comes as a result of a g2p from a procedure in a pipeline at a center
                # and parameter tested
                # assoc_id = self.make_id((effective_genotype_id + phenotype_id + phenotyping_center +
                #                          pipeline_stable_id + procedure_stable_id + parameter_stable_id))

                assoc = G2PAssoc(self.name, effective_genotype_id, phenotype_id)
                assoc.add_evidence(eco_id)
                assoc.set_score(float(p_value))

                # TODO add evidence instance using pipeline_stable_id + procedure_stable_id + parameter_stable_id

                assoc.add_association_to_graph(g)
                assoc_id = assoc.get_association_id()

                # add a free-text description
                description = ' '.join((mp_term_name, 'phenotype determined by', phenotyping_center, 'in an',
                                        procedure_name, 'assay where', parameter_name.strip(),
                                        'was measured with an effect_size of', str(round(float(effect_size), 5)),
                                         '(p =', "{:.4e}".format(float(p_value)), ').'))

                gu.addDescription(g, assoc_id, description)

                # TODO add provenance information
                # resource_id = resource_name
                # assoc.addSource(g, assoc_id, resource_id)

                if not self.testMode and limit is not None and line_counter > limit:
                    break

        return

    def _map_zygosity(self, zygosity):
        geno = Genotype(self.graph)
        typeid = geno.zygosity['indeterminate']
        type_map = {
            'heterozygote': geno.zygosity['simple_heterozygous'],
            'homozygote': geno.zygosity['homozygous'],
            'hemizygote': geno.zygosity['hemizygous'],
            'not_applicable': geno.zygosity['indeterminate']
        }
        if zygosity.strip() in type_map:
            typeid = type_map.get(zygosity)
        else:
            logger.warn("Zygosity type not mapped: %s", zygosity)
        return typeid

    def parse_checksum_file(self, file):
        """
        :param file
        :return dict
        """
        checksums = dict()
        file_path = '/'.join((self.rawdir, file))
        with open(file_path, 'rt') as tsvfile:
            reader = csv.reader(tsvfile, delimiter=' ')
            for row in reader:
                (checksum, whitespace, file_name) = row
                checksums[checksum] = file_name

        return checksums

    def compare_checksums(self):
        """
        test to see if fetched file matches checksum from ebi
        :return: True or False
        """
        is_match = True
        reference_checksums = self.parse_checksum_file(
            self.files['checksum']['file'])
        for md5, file in reference_checksums.items():
            if os.path.isfile('/'.join((self.rawdir, file))):
                if self.get_file_md5(self.rawdir, file) != md5:
                    is_match = False
                    logger.warn('%s was not downloaded completely', file)
                    return is_match

        return is_match

    def getTestSuite(self):
        import unittest
        from tests.test_impc import IMPCTestCase
        # TODO test genotypes

        test_suite = unittest.TestLoader().loadTestsFromTestCase(IMPCTestCase)

        return test_suite
