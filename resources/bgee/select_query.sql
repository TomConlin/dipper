
-- .read select_query.sql
.once species_gene_anatomy_stage_genome.unl
select distinct
    species.speciesID,
    gene.geneId,
    anatEntity.anatEntityId,
    stage.stageId,
    genomeVersion
 from globalExpression
  join globalCond on globalExpression.globalConditionId == globalCond.globalConditionId
  join species on globalCond.speciesId == species.speciesId
  join gene on globalExpression.bgeeGeneId == gene.bgeeGeneId
   and species.speciesId == gene.speciesId
  join anatEntity on globalCond.anatEntityId == anatEntity.anatEntityId
  join stage on globalCond.stageId == stage.stageId
 where species.speciesID in (
    '6239','7227','7955','8364','9031','9258','9365','9593',
    '9597','9598','9606','9615','9685','9796','9823','9913',
    '9986','10090','10116','10141','13616','28377','9544'
 )
   and summaryQuality == 'GOLD'
   -- and globalExpression.propagation == 'self% (doesn't exist yet)
order by species.speciesID
;


-- PR is interested in specificity
-- we do not have access to the variable granularity an ontology provides here
-- but we can begin the process and get lucky sometimes

select species.speciesID,
    gene.geneId,
    count(anatEntity.anatEntityId) specificity
 from globalExpression
  join globalCond on globalExpression.globalConditionId == globalCond.globalConditionId
  join species on globalCond.speciesId == species.speciesId
  join gene on globalExpression.bgeeGeneId == gene.bgeeGeneId
   and species.speciesId == gene.speciesId
  join anatEntity on globalCond.anatEntityId == anatEntity.anatEntityId
  join stage on globalCond.stageId == stage.stageId
 where species.speciesID in (
    '6239','7227','7955','8364','9031','9258','9365','9593',
    '9597','9598','9606','9615','9685','9796','9823','9913',
    '9986','10090','10116','10141','13616','28377','9544'
 )
   and summaryQuality = 'GOLD'
group by anatEntity.anatEntityId
having count(anatEntity.anatEntityId) = 1
--limit 100
;
-- ~90 sec

-- the other side of that coin is how many genes are associated with an anatomy

select species.speciesID,
    anatEntity.anatEntityId,
    count(gene.geneId) gene_density
 from globalExpression
  join globalCond on globalExpression.globalConditionId == globalCond.globalConditionId
  join species on globalCond.speciesId == species.speciesId
  join gene on globalExpression.bgeeGeneId == gene.bgeeGeneId
   and species.speciesId == gene.speciesId
  join anatEntity on globalCond.anatEntityId == anatEntity.anatEntityId
  join stage on globalCond.stageId == stage.stageId
 where species.speciesID in (
    '6239','7227','7955','8364','9031','9258','9365','9593',
    '9597','9598','9606','9615','9685','9796','9823','9913',
    '9986','10090','10116','10141','13616','28377','9544'
 )
   and summaryQuality = 'GOLD'
group by gene.geneId
-- order by 3 asc -- desc
having count(gene.geneId) == 1
-- limit 100
;

-- ~80 sec

--######################################################################################
--######################################################################################

-- post easybege

-- what species do they have which we do not?

select distinct speciesID  from species
where species.speciesID not in (
    '6239','7227','7955','8364','9031','9258','9365','9593',
    '9597','9598','9606','9615','9685','9796','9823','9913',
    '9986','10090','10116','10141','13616','28377','9544'
 );

-- 7217,7230,7237,7240,7244,7245
-- Drosophila species

-- confirm
select distinct speciesID  from species
where species.speciesID not in (
    '7217','7230','7237','7240','7244','7245'
 ) order by 1;

--'6239','7227','7955','8364','9031','9258','9365','9544','9593',
--'9597','9598','9606','9615','9685','9796','9823','9913',
--'9986','10090','10116','10141','13616','28377'
-- okay.

-- ReDo to the first query limiting to "expressed"
-- the anatomy entity is (mostly?) limited to species anyway
-- may need addtional ontology mapping   e.g. EMAPA -> UBERON

/*
    species.speciesID,
    gene.geneId,
    anatEntity.anatEntityId,
    count(anatEntity.anatEntityId) specificity
*/


select
/**/
    species.speciesID,
    --gene.geneId,
    --anatEntity.anatEntityId,
    --count(anatEntity.anatEntityId) specificity,
    --propagationOrigin,
    score
/**/
 from globalExpression
  join globalCond on globalExpression.globalConditionId == globalCond.globalConditionId
  join species on globalCond.speciesId == species.speciesId
  join gene on globalExpression.bgeeGeneId == gene.bgeeGeneId
   and species.speciesId == gene.speciesId
  join anatEntity on globalCond.anatEntityId == anatEntity.anatEntityId
  join stage on globalCond.stageId == stage.stageId
 where callType == 'EXPRESSED'
   --and propagationOrigin = 'self'
   and species.speciesID not in ('7217','7230','7237','7240','7244','7245')
   and summaryQuality = 'GOLD'
--group by anatEntity.anatEntityId --, anatEntity.anatEntityname
--having count(anatEntity.anatEntityId) = 1
order by 2,1
;


6239	60.32744
7227	57.79801
7955	78.11673
8364	62.60591
9031	63.46201
9258	57.26124
9544	34.6632
9593	60.66692
9598	57.96494
9606	26.30684
9615	60.40659
9685	61.74092
9796	63.79633
9823	57.99209
9913	60.49466
9986	57.82752
10090	40.7332
10116	56.25028
10141	64.8792
13616	56.35633
28377	61.41013




