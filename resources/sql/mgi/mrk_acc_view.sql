-- http://www.informatics.jax.org/schema_pg/tables/mrk_acc_view.html
-- accid,
-- prefixpart,
-- _logicaldb_key,
-- _object_key,
-- preferred,
-- _organism_key

SELECT
    accid,
    prefixpart,
    _object_key,
    acc_logicaldb.name logicaldb_name
FROM mrk_acc_view
    join acc_logicaldb on mrk_acc_view._logicaldb_key = acc_logicaldb._logicaldb_key

WHERE mrk_acc_view.preferred = 1
  and mrk_acc_view.private != 1
  and _organism_key = 1    -- 1 | mouse, laboratory | Mus musculus/domesticus
  and acc_logicaldb.name in ('MGI', 'Entrez Gene', 'Ensembl Gene Model')

 order by mrk_acc_view._logicaldb_key asc  -- MGI: first to anchor mgi's cliques



