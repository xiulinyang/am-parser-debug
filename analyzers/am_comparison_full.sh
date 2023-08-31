#!/bin/bash
##
## Copyright (c) 2020 Saarland University.
##
## This file is part of AM Parser
## (see https://github.com/coli-saar/am-parser/).
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##

# usage: bash am_comparison_full.sh file1 file2 outputfolder
# file1 and file2 are the amconll files you want to compare
# for precision/recall, file1 will be treated as gold and file2 as
# outputfolder should be a path to an empty, existing folder ending with a "/"
# Note: run this from the local directory!

#run preparation script
echo 'preparing data'
python3 prepare_visualize.py $1 $2 $3

#get filenames without the path
f1=1_$(basename $1)
f2=2_$(basename $2)

#f-scores
echo 'computing f-score, without IGNORE and ROOT edges'
python3 am_dep_fscore.py $3$f1 $3$f2

# UAS and LAS
echo 'computing UAS and LAS, without IGNORE edges'
java -jar MaltEval.jar -g $3$f1 -s $3$f2 --Metric "LAS;UAS" --ExcludeDeprels "IGNORE"

# match broken down by dependency label
echo 'computing match broken down by dependency relation, without IGNORE edges. This is written directly to the detailed_f.txt file in the output folder'
java -jar MaltEval.jar -g $3$f1 -s $3$f2 --Metric "self" --GroupBy "Deprel" --ExcludeDeprels "IGNORE" --confusion-matrix 1 > $3detailed_f.txt

# visualization (takes a while to load)
echo 'starting visualization... (takes a while to load)'
java -jar MaltEval.jar -g $3$f1 -s $3$f2 -v 1
