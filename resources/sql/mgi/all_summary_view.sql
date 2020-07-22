-- http://www.informatics.jax.org/schema_pg/tables/all_summary_view.html
-- _object_key,
-- preferred,
-- mgiid,
-- description,
-- short_description

--  count  821,818  (2020-04)
--_mgitype_key ->  acc_mgitype.name mgitype_name,  -- Allele (constant)

SELECT  -- count(*)
    accid,
    _object_key,
    mgiid,
    description,
    short_description,

    subtype

FROM all_summary_view

    join acc_mgitype on all_summary_view._mgitype_key =  acc_mgitype._mgitype_key
    join all_allele on all_allele._marker_key = 
where all_summary_view.preferred = 1
  and all_summary_view.private != 1




   --join mgi_organism on acc_logicaldb._organism_key = mgi_organism._organism_key



--             subtype              | count
------------------------------------+--------
-- Other                            |     13
-- Chemically and radiation induced |     64
-- Transposon induced               |     64
-- Chemically induced (other)       |    149
-- Radiation induced                |    487
-- Spontaneous                      |   2180
-- Chemically induced (ENU)         |   4285
-- Endonuclease-mediated            |   5543
-- Transgenic                       |   9258
-- QTL                              |  13023
-- Not Applicable                   |  24058
-- Not Specified                    |  37748
-- Targeted                         |  64371
-- Gene trapped                     | 660575
