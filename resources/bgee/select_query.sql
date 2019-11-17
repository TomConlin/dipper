
-- .read select_query.sql
select -- count(*)
species.speciesID,
gene.geneId,
anatEntity.anatEntityId,
summaryQuality,
stage.stageId,
genomeVersion, 
count(distinct gene.geneId,anatEntity.anatEntityId) specificty


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
--group by summaryQuality, anatEntity.anatEntityId, species.speciesID, stage.stageId
order by species.speciesID, summaryQuality
--
limit 100

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
limit 100
;

-- ~80 sec

