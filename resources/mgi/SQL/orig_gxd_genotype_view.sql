/*
mgd=> \d+ gxd_genotype_view
                                       View "mgd.gxd_genotype_view"
      Column       |            Type             | Collation | Nullable | Default | Storage  | Description 
-------------------+-----------------------------+-----------+----------+---------+----------+-------------
 _genotype_key     | integer                     |           |          |         | plain    | 
 _strain_key       | integer                     |           |          |         | plain    | 
 isconditional     | smallint                    |           |          |         | plain    | 
 note              | text                        |           |          |         | extended | 
 _existsas_key     | integer                     |           |          |         | plain    | 
 _createdby_key    | integer                     |           |          |         | plain    | 
 _modifiedby_key   | integer                     |           |          |         | plain    | 
 creation_date     | timestamp without time zone |           |          |         | plain    | 
 modification_date | timestamp without time zone |           |          |         | plain    | 
 strain            | text                        |           |          |         | extended | 
 mgiid             | text                        |           |          |         | extended | 
 displayit         | text                        |           |          |         | extended | 
 createdby         | text                        |           |          |         | extended | 
 modifiedby        | text                        |           |          |         | extended | 
 existsas          | text                        |           |          |         | extended | 
View definition:
*/
 SELECT g._genotype_key,
    g._strain_key,
    g.isconditional,
    g.note,
    g._existsas_key,
    g._createdby_key,
    g._modifiedby_key,
    g.creation_date,
    g.modification_date,
    s.strain,
    a.accid AS mgiid,
    (('['::text || a.accid) || '] '::text) || s.strain AS displayit,
    u1.login AS createdby,
    u2.login AS modifiedby,
    vt.term AS existsas
   FROM gxd_genotype g,
    prb_strain s,
    acc_accession a,
    voc_term vt,
    mgi_user u1,
    mgi_user u2
  WHERE g._strain_key = s._strain_key 
    AND g._genotype_key = a._object_key 
    AND a._mgitype_key = 12 
    AND a._logicaldb_key = 1 
    AND a.prefixpart = 'MGI:'::text 
    AND a.preferred = 1 
    AND g._createdby_key = u1._user_key 
    AND g._modifiedby_key = u2._user_key 
    AND g._existsas_key = vt._term_key
 ;
