

2019 Nov

----------------------------------
```
# existing

time python dipper-etl.py -s bgee

...

INFO:__main__:***** Finished with bgee *****
INFO:__main__:All done.

real	120m17.456s
user	119m29.924s
sys	0m27.303s
```

Two Hours to generate 4,377,842 monarch associations

------------------------------------

There is interest in changing our bgee associations represented.
Key to this may their very involved concept of "rank"
which amounts to multiple levels of "normalizations" of already nebulous numbers.

I like their triage approach they call gold, silver & bronze
which may as well be good, bad and ugly as they
do not even bother distributing the bronze by default.


Download files described here
    https://bgee.org/?page=doc&action=call_files

ftp://ftp.bgee.org/current/sql_lite_dump.tar.gz
------------------------------------------------------------
in `./data/` because I don't like huge data files in git


```
curl -O data/sql_lite_dump.tar.gz ftp://ftp.bgee.org/current/sql_lite_dump.tar.gz
tar -xf sql_lite_dump.tar.gz
```

Despite the name it is a MySql/Mariadb db dump not a sqlite3 db

convert the db dump from mysql to sqlite3
```
../../../scripts/mysql2sqlite sql_lite_dump.sql  > bgee_sqlite3.sql
```

read in the converted ascii db dump and re index into a binary blob


```
sqlite3 bgee.sqlite < bgee_sqlite3.sql
```

Takes about 15 minutes to reconsitute a database from the sql dump
This 15 minute process will need repeating each time they provide a new db dump
which from preusing their news seems to be 14 or less in 7-ish years.
So twice a year maybe.


-- to compress it from ~2.3G to ~660M
-- since it may be downloaded many times (from DipperCache?)

```
gzip -c bgee.sqlite > bgee.sqlite.gz

```

-- Sqlite3 takes no significant time to start the reconsituted database


```
# to unzip w/o an overt copy

mkfifo -m 0666 bgee.sqlite
gzip -d < bgee.sqlite.gz > bgee.sqlite
sqlite3 bgee.sqlite && rm bgee.sqlite
```

While the database is running (type `.quit` to exit) we can
...

```
sqlite> .once ../bgee_sqlite3_schema.ddl
sqlite> .fullschema

```
which saves the isolated schema (data definition language)
as [bgee_sqlite3_schema.ddl](./bgee_sqlite3_schema.ddl)

from which we can extract meaning
```
~/GitHub/SQLiteViz/sqlite_dot.awk bgee_sqlite3_schema.ddl > bgee_sqlite3_schema.gv

dot -T svg  bgee_sqlite3_schema.gv > bgee_sqlite3_schema.svg
```
and we have a handy dandy ER diagram of what BGEE provided
![ER diagram](./bgee_sqlite3_schema.svg)



Note that `stage` is an important component for understanding
what a "count" means in this data model.
Which susgests `stage` information may need to make its way into the front end.

It is also quite unfortunate the README
now says the stage ontology is unmaintained.

--------------------------------------------------------------
```
dot -T plain-ext  bgee_sqlite3_schema.gv |
    awk -F"^graph |^node |^edge |^stop" '/^node / {gsub("\\\n","");split($0,a," ");print a[2];for(i=3;i<length(a);i++)if(match(a[i],"<"))print "\t" substr(a[i],2,length(a[i])-2)}'
```

and a handy plain text list to grab tables & fields from

```
anatEntity
	anatEntityId
	anatEntityName
	anatEntityDescription

gene
	bgeeGeneId
	geneId
	geneName
	geneDescription
	speciesId

species
	speciesId
	genus
	species
	speciesCommonName
	genomeVersion
    genomeSpeciesId

globalCond
	globalConditionId
	anatEntityId
	stageId
	speciesId

stage
	stageId
	stageName
	stageDescription

globalExpression
	globalExpressionId
	bgeeGeneId
	globalConditionId
	summaryQuality

```

localy I might run `xdot bgee_sqlite3_schema.gv` instead of looking at the sgv.

-------------------------------------------------------------

build up a local tt of their `genomeVersion` to `NCBIAssembly:id`

[bgee.yaml](../../translationtable/bgee.yaml)

-------------------------------------------------------------

```
# to get a list of taxon to filter for in a sql query

cut  -f 3 -d ':' translationtable/bgee.yaml | grep "^[0-9]\{3,\}"
6239|nematode
7227|fruit fly
7955|zebrafish
8364|western clawed frog
9031|chicken
9258|platypus
9365|hedgehog not found.  eriEur2 -> GCA 000296755.1
9593|gorilla
959[78]|bonobo/chimpanzee
9606|human
9615|dog
9685|cat
9796|horse
9823|pig
9913|cattle    ???
9986|rabbit
10090|mouse
10116|rat
10141|guinea pig
13616|opossum   note
28377|green anole
9544|macaque
```

reformat & edit
```
cut  -f 3 -d ':' translationtable/bgee.yaml |
    grep "^[0-9]\{3,\}" | sed "s~\([^|]*\)|.*~'\1',~;" | tr -d '\n'

'6239','7227','7955','8364','9031','9258','9365','9593',
'9597','9598','9606','9615','9685','9796','9823','9913',
'9986','10090','10116','10141','13616','28377','9544'
```

to include in a seperate [sql select query file](./select_query.sql)

where we are selecting for
    `speciesID`, `geneId`, `anatEntityId`, `summaryQuality`, `stageId`, `genomeVersion`
e.g
    `6239|WBGene00002059|UBERON:0000465|GOLD|UBERON:0000107|WBcel235`

-----------------------------------------------------------
```
sqlite> .read ../select_query.sql
32,589,067
Run Time: real 181.538 user 72.464747 sys 58.335826
```
Puts together _ALL_ 32M records (monarch associations) in three minutes

---------------------------------------------------
```
sqlite> .read ../select_query.sql
9,825,168
Run Time: real 70.235 user 41.318082 sys 28.917016
```
Puts together 10M _GOLD_ level records (monarch associations) in seventy seconds

---------------------------------------------------------

Start writing a SWAG data model as a Graphviz dot file [bgee_datamodel_swag.gv](bgee_datamodel_swag.gv)
which looks like:



![datamodle](bgee_datamodel_swag.svg)


N.B.  I am currently limiting all sql queries to __GOLD__ level
------------------------------------------------------------
 - this limit doubles the number of associations compared with existing ingest.
 - changes from existing include
    - more than twenty associations in the case of many with high confidance
    - fewer than twenty associations in the case less confidence
 - including __SILVER__ would
    - triple the volume of associations compared with just gold
    - be 8 times the volume of associations compared with existing ingest


-----------------------------------------------------------------------

There is a request to provide some feedback on how specific a gene
is to an anatomical term in a species.

see: https://github.com/monarch-initiative/dipper/issues/865

At ingest is not the place to answer this question at all levels of
granularity a user may intend.
But it is we we can ensure the base information is available
and that it provide guidance for downstream filtering.

note!  BGEE does its own propagating up anatomy and stage ontologies

This means that even with the ontologies it may be difficult to determine
primary observation from infered propatation.
(without the ontologies forget it)

For example the anatomy item with the greatest gene density is
the human multicellular organism with 41,909 distinct genes expressed
during the life cycle stage.  mmm-K

Leaf nodes in the ontology will be the easiest to reason about counting
But that information is not on hand at ingest.

I expect intermediate ontology nodes may be the sum of their children's counts or
also have their own observations added in as well depending
on the granularity of the experiment reported.


At any rate, generating the gene `density` of a anatomy item,
    - _how many distinct genes per anatomy item?_

and the `specificity` of a gene to anatomical items,
    - _in how many anatomy items is this gene expressed?_

for all the species & stages takes about three minutes.


------------------------------------------------------------

Understanding a bit more about the distribution of those counts
per species may shed some light on legitimate uses.


-------------------------------------------------------------

I have had an exchange with folks at BGEE reguarding including
a way to differentiate primary v.s. infered statments of expression.
It seems they may have a new release including this data that allows
more meaningful counts in a month or two.
I will back burner this aspect till then and work on the rest.

--------------------------------------------------------------




2020 June


DipperCache has been pulling and converting their new file (they renamed easybgee)
to indexed and compressed sqlite3 instance since it came out in April.

wget -N https://archive.monarchinitiative.org/DipperCache/bgee/easybgee.sqlite3.gz

--------------------------------------------------------------

it looks as though they are also producing a RDF file.

ftp://ftp.bgee.org/current/rdf_easybgee.zip   (fetching is a slog on my home network)

and they have a tiny covid19  subset file there as well

ftp://ftp.bgee.org/current/rdf_easybgee_covid19_view.zip


# covid diversion while the main ttl file is still downloading)
covid dataset is split up into a file per predicate (~55 files)


although the RDF files have the extention .ttl
they are seem to be mostly valid ntriples. (a -> rdf:type)
but they are not quite valid turtle either  e.g. missing namespaces

cat covid19_ttl/*.ttl > bgee_covid19.ttl
rapper -i turtle -c  bgee_covid19.ttl

rapper: Parsing URI file:///data/Projects/Monarch/dipper/resources/bgee/data/bgee_covid19.ttl with parser turtle
rapper: Error -  - The namespace prefix in "xsd:double" was not declared.
rapper: Error - URI file:///data/Projects/Monarch/dipper/resources/bgee/data/bgee_covid19.ttl:91632 - Failed to convert qname xsd:double to URI
rapper: Error - URI file:///data/Projects/Monarch/dipper/resources/bgee/data/bgee_covid19.ttl:91632 - syntax error, unexpected $end, expecting URI literal or QName
rapper: Failed to parse file bgee_covid19.ttl turtle content
rapper: Parsing returned 137477 triples



########################

back on task
zcat easybgee.sqlite3.gz > bgee


yea... that is not working.

the new mysqldump from bgee has unescaped new lines
(Which I have now deleted)

which then


```
sqlite> .once ./easybgee_sqlite3_schema.ddl
sqlite> .fullschema

```

```
~/GitHub/SQLiteViz/sqlite_dot.awk easybgee_sqlite3_schema.ddl > easybgee_sqlite3_schema.gv

dot -T svg  bgee_sqlite3_schema.gv > bgee_sqlite3_schema.svg
```


the main changes are the addtion od four fields in the globalExpression table.

,  `rank` decimal(9,2)  NOT NULL
,  `score` decimal(9,5)  NOT NULL
,  `propagationOrigin` varchar(20) NOT NULL
,  `callType` varchar(20) NOT NULL


where "propagationOrigin" tells us if the results are inffered

1206369|all
66855858|self
7317246|self and ancestor
24727198|self and descendant

which pointedly does not have **any** which are strictly propagated ... not expected

and "callType" is:

64764646|EXPRESSED
35342025|NOT_EXPRESSED


"rank"
min max average

1|	55062|	20560.409237503

"score"
min max average
0.01|	100|	52.3943358920252




###############################################


playing with the data I have some questions

It seems every record score includes expression of self.
either alone or in combination with up/down stream records.
confirm every score is for an observation (even if it is obfuscated with adgecent scores)

spit out the taxon and score for all the expressed "gold"  quality records

get the list of taxon

cut -f1 -d \| tax_score.unl | sort -un > taxon.list

# partition the scores by species
for t in $(cat taxon.list) ; do
    awk -F'|' -v"tax=$t" '$1==tax{print $2}' tax_score.unl > $t.score;
done


# find a cutoff score per species... relative best of the best score
# Where lower is better.   hmmm. human is best & zebrafish is worse

for t in $(cat taxon.list); do echo -e "$t\t$(uniq -c $t.score | otsu.awk)"; done > taxon_threshold.tsv

# generate queries that filter on the threshold

../generate_threshold_query.awk  taxon_threshold.tsv  > select_filtered.sql

run the queries & save the results

sqlite> .output  bgee_filtered.tsv
sqlite> .read  select_filtered.sql
sqlite> .output  stdout


# chech output volume

wc -l < bgee_filtered.tsv
2,162,464

# (old top 20 of anything resulted in 4,377,842)


# by species
 cut -f1 -d\| bgee_filtered.tsv | sort | uniq -c | sort -nr
 343954 7955
 255959 9606
 230027 7227
 207945 10090
 157336 8364
 144972 9615
 129918 9598
  91843 6239
  89218 13616
  82808 9796
  76543 10116
  65528 9823
  65290 9544
  65213 9986
  33917 9031
  30350 28377
  29481 9913
  25175 9258
  18529 9593
  12742 9685
   5716 10141


----------------------------------------

select count(*) , species.speciesID
 from globalExpression
  join globalCond on globalExpression.globalConditionId == globalCond.globalConditionId
  join species on globalCond.speciesId == species.speciesId
  join gene on globalExpression.bgeeGeneId == gene.bgeeGeneId
   and species.speciesId == gene.speciesId
  join anatEntity on globalCond.anatEntityId == anatEntity.anatEntityId
 where callType == 'EXPRESSED' and summaryQuality = 'GOLD'
 group by species.speciesID order by 1
;


# look as what portiom of available are acccepted.

5716/39050|10141
12742/55120|9685
18529/74530|9593
25175/105998|9258
30350/130284|28377
33917/136230|9031
29481/139241|9913
65213/272402|9986
91843/313309|6239
65528/344058|9823
76543/352386|10116
82808/369100|9796
89218/400773|13616
157336/414173|8364
129918/528441|9598
65290/544929|9544
144972/682701|9615
343954/785715|7955
230027/890622|7227
207945/6558527|10090
255959/9180553|9606

# As percantages  of expressed gold per species ...
awk 'NR==FNR{n[$2]=$1}NR!=FNR{d[$2]=$1}END{for(t in d){if(t in n){printf("%i\t%.2f%%\n",t,n[t]/d[t]*100)}}}' bgee_filtered.count bgee_unfiltered.tsv | sort -k2nr
7955	43.78%
8364	37.99%
6239	29.31%
7227	25.83%
9031	24.90%
9593	24.86%
9598	24.59%
9986	23.94%
9258	23.75%
28377	23.30%
9685	23.12%
9796	22.44%
13616	22.26%
10116	21.72%
9615	21.24%
9913	21.17%
9823	19.05%
10141	14.64%
9544	11.98%
10090	3.17%
9606	2.79%

mostly around the top quarter of the best quality expression.


# loking at the distrtibutions and cutoff in R-Studio 
# I am underwhelmed with the significance.


select count(*), species.speciesID
   ...>  from globalExpression 
   ...>   join globalCond on globalExpression.globalConditionId == globalCond.globalConditionId 
   ...>   join species on globalCond.speciesId == species.speciesId 
   ...>   join gene on globalExpression.bgeeGeneId == gene.bgeeGeneId 
   ...>    and species.speciesId == gene.speciesId 
   ...>   join anatEntity on globalCond.anatEntityId == anatEntity.anatEntityId 
   ...>  where callType == 'EXPRESSED' and summaryQuality = 'GOLD'
   ...>  group by species.speciesID order by 1
   ...> ;
39050|10141
55120|9685
74530|9593
105998|9258
130284|28377
136230|9031
139241|9913
272402|9986
313309|6239
344058|9823
352386|10116
369100|9796
400773|13616
414173|8364
528441|9598
544929|9544
682701|9615
785715|7955
890622|7227
6558527|10090
9180553|9606


22,318,142 total

taking a threshold eliminates ~90% 
It will have to come down to a policy/trust/usefulness choice.



