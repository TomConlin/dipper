

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









