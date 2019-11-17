
select
    count(distinct geneId) genes,
    anatEntity.anatEntityId,
    species.speciesID,
    summaryQuality,
    stage.stageId,
    genomeSpeciesId
 from globalExpression
  join globalCond on globalExpression.globalConditionId == globalCond.globalConditionId
  join species on globalCond.speciesId == species.speciesId
  join gene on globalExpression.bgeeGeneId == gene.bgeeGeneId
   and species.speciesId == gene.speciesId
  join anatEntity on globalCond.anatEntityId == anatEntity.anatEntityId
  join stage on globalCond.stageId == stage.stageId
 where anatEntity.anatEntityId == "UBERON:0004819"
group by summaryQuality, anatEntity.anatEntityId, species.speciesID, stage.stageId
order by summaryQuality, genes
;

select '"'||genomeVersion||'": "" # NCBITaxon:'||speciesId,speciesCommonName
 from species where speciesCommonName != "";



