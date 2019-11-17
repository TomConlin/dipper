
-- .read select_query.sql
select -- count(*)
--
species.speciesID,
--
gene.geneId,
--
anatEntity.anatEntityId,
--
summaryQuality,
--
stage.stageId,
--
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
   and summaryQuality = 'GOLD'
--group by summaryQuality, anatEntity.anatEntityId, species.speciesID, stage.stageId
order by species.speciesID, summaryQuality
--
limit 100

;

