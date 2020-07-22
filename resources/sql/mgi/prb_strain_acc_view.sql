-- http://www.informatics.jax.org/schema_pg/tables/prb_strain_acc_view.html
--
-- 'accid'           -- of the probe/strain
-- 'prefixpart'
-- '_logicaldb_key'  -->  acc_logicaldb.name logicaldb_name  (is provenance)
-- '_object_key'      is a clique key (groups of accids)
-- 'preferred'        is a server side filter, no longer relevent client side
-- '_organism_key'    -->  mgi_organism.latinname (of the clique) -- appears constant

SELECT distinct
    prb_strain_acc_view.accid,
    prb_strain_acc_view.prefixpart,
    prb_strain_acc_view._logicaldb_key,   -- redundant w/provenance for sorting
    prb_strain_acc_view._object_key,
    acc_logicaldb.name logicaldb_name

FROM prb_strain_acc_view
    join acc_logicaldb on prb_strain_acc_view._logicaldb_key = acc_logicaldb._logicaldb_key

 where prb_strain_acc_view.preferred = 1
  and prb_strain_acc_view.private != 1
  and acc_logicaldb.name in (
    'MGI', 'JAX Registry', 'EMMA', 'MMRRC', 'ORNL', 'APB', 'NMICE', 'RIKEN BRC', 'MUGEN'
  )
 order by prb_strain_acc_view._logicaldb_key asc  -- MGI: first to anchor mgi's cliques

--;
