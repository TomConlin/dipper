CREATE TABLE `anatEntity` (
  `anatEntityId` varchar(20) NOT NULL
,  `anatEntityName` varchar(255) NOT NULL
,  `anatEntityDescription` text
,  PRIMARY KEY (`anatEntityId`)
);
CREATE TABLE `gene` (
  `bgeeGeneId` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `geneId` varchar(20) NOT NULL
,  `geneName` varchar(255) NOT NULL DEFAULT ''
,  `geneDescription` text
,  `speciesId` integer  NOT NULL
,  UNIQUE (`geneId`,`speciesId`)
,  CONSTRAINT `gene_ibfk_1` FOREIGN KEY (`speciesId`) REFERENCES `species` (`speciesId`) ON DELETE CASCADE
);
CREATE TABLE `globalCond` (
  `globalConditionId` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `anatEntityId` varchar(20) DEFAULT NULL
,  `stageId` varchar(20) DEFAULT NULL
,  `speciesId` integer  NOT NULL
,  UNIQUE (`anatEntityId`,`stageId`,`speciesId`)
,  CONSTRAINT `globalCond_ibfk_1` FOREIGN KEY (`anatEntityId`) REFERENCES `anatEntity` (`anatEntityId`) ON DELETE CASCADE
,  CONSTRAINT `globalCond_ibfk_2` FOREIGN KEY (`stageId`) REFERENCES `stage` (`stageId`) ON DELETE CASCADE
,  CONSTRAINT `globalCond_ibfk_3` FOREIGN KEY (`speciesId`) REFERENCES `species` (`speciesId`) ON DELETE CASCADE
);
CREATE TABLE `globalExpression` (
  `globalExpressionId` integer  NOT NULL PRIMARY KEY AUTOINCREMENT
,  `bgeeGeneId` integer  NOT NULL
,  `globalConditionId` integer  NOT NULL
,  `summaryQuality` varchar(10) NOT NULL
,  UNIQUE (`globalExpressionId`)
,  CONSTRAINT `globalExpression_ibfk_1` FOREIGN KEY (`bgeeGeneId`) REFERENCES `gene` (`bgeeGeneId`) ON DELETE CASCADE
,  CONSTRAINT `globalExpression_ibfk_2` FOREIGN KEY (`globalConditionId`) REFERENCES `globalCond` (`globalConditionId`) ON DELETE CASCADE
);
CREATE TABLE `species` (
  `speciesId` integer  NOT NULL
,  `genus` varchar(70) NOT NULL
,  `species` varchar(70) NOT NULL
,  `speciesCommonName` varchar(70) NOT NULL
,  `genomeVersion` varchar(50) NOT NULL
,  `genomeSpeciesId` integer  NOT NULL DEFAULT '0'
,  PRIMARY KEY (`speciesId`)
,  UNIQUE (`species`,`genus`)
);
CREATE TABLE `stage` (
  `stageId` varchar(20) NOT NULL
,  `stageName` varchar(255) NOT NULL
,  `stageDescription` text
,  PRIMARY KEY (`stageId`)
);
CREATE INDEX "idx_globalCond_stageId" ON "globalCond" (`stageId`);
CREATE INDEX "idx_globalCond_speciesId" ON "globalCond" (`speciesId`);
CREATE INDEX "idx_gene_speciesId" ON "gene" (`speciesId`);
CREATE INDEX "idx_globalExpression_globalConditionId" ON "globalExpression" (`globalConditionId`);
/* No STAT tables available */
