# Linguistic Analysis
**To be added to the wiki when we publish the paper**

In Section 7 of our paper, we describe some basic linguistic analysis of the parser output. This section explains how to replicate the analysis or to do your own analysis of amconll files of data. 

We automatically created subcorpora based on information in the amconll files, and then visualised sampled sentences from those subcorpora. In this way we got some counts of certain patterns, and could sample the sentences with those patterns. The subcorpora are written to new amconll files, which you can then read in with a visualiser. Summaries of the sizes of the subcorpora are written to text files. Below, we first explain how to get the subcorpora and then [how to visualise the samples](https://github.com/coli-saar/am-parser/blob/unsupervised2020/graph_dependency_parser/inside_maximization/linguistic_analysis.md#visualising-examples).

## Requirements

* `am-tools.jar`, which you should have already if you've built `am-parser`. It will be in **TODO path**. If you haven't built the parser, you can build the am-tools jar file separately. Use **TODO branch, commit x**. 

* For visualisation, you need the requirements listed [here](https://github.com/coli-saar/am-parser/wiki/Error-analysis:-visualization-of-AM-dependency-trees#2-the-own-gui-approach)


## Counting and printing examples of phenomena

### Get all counts and examples with a script

There are three Java scripts that categorise corpus entries, count the entries in each category, and print new amconll files for each category. They count the following, explained in detail below:

 * Supertags: counts supertags by unlabelled graph constant
 * Sources: counts sources by graph edge label
 * Edges: counts AM dep-tree edge labels (AM operations)

There is a script in `am-parser/analyzers/` which will run the three existing counters on all four graphbanks. It's simple and you can edit it if you want it to behave differently. Currently it assumes the corpora are `<path/to/amconll_files/DM.amconll>` etc, and that you have DM, PAS, PSD, and AMR.  To run it, `cd` to the `analyzers/` folder and run:

```bash
bash all_counts.sh <path/to/am-tools jar file> <path/to/amconll_files> <path/to/output_folder>

```
   
It will put the output files in `<output_path>/sources/DM/`, `<output_path>/supertags/AMR/` etc.

### Details of counters

There are three Java scripts that categorise corpus entries, count the entries in each category, and print new amconll files for each category. These are:
  1. `CountEdges`: creates a map from AM operation (= dep tree edge labels) to sentences that use that operation. 
   * Creates a directory called `edges` and a daughter `edges/examples`
   * Prints a summary of the counts to `edges/summary.txt`, e.g. 
   
   > Edges in train-final/DM
   >
   > 0. MOD_S2  ####  308231
   > 1. APP_S0  ####  171516
   > 2. IGNORE  ####  169012
   > 3. APP_S2  ####  73070
   > 4. ROOT  ####  32942
   > 5. MOD_S1  ####  6426
   > 6. APP_S1  ####  5846
   > 7. MOD_S0  ####  2647

   * Prints one amconll file for each operation containing all sentences that use it. Files are named after their edges, e.g. `MOD_S2.amconll` and are located in `examples/`.
   
  2. `CountSources`: creates a map from sources to a map from graph edge labels to sentences containing a word whose graph has that edge label incident to that source. e.g. ARG0 -> S1
   * Creates a directory called `sources` and a daughter `sources/examples`
   * Prints a summary of the counts to `sources/summary.txt`, e.g. 
   
   > Sources by graph edge label in train-final/DM
   > 
   > 0. ARG1  #### 3<br>
   > S2: 19746<br>
   > S0: 12288<br>
   > S1: 3403<br>    
   > ...
      
   * For each (edge, source) pair, prints a file of all sentences containing a word whose supertag has an edge incident to that source. Files are named after the edge and source, e.g. `ARG1_s0` and are located in `examples/`.
    
  3. `CountSupertags`: creates a map from unlabelled graph constants to supertags to sentences containing a word with that supertag
    
   * Creates a directory called `supertags` and a daughter `supertags/examples`
   * Prints a summary of the counts to `supertags/summary.txt`, e.g. 
    
   > 3. [i_4<root>/--LEX-- -ARG1-> i_5]  ####  7<br>
   > (i_4<root> / --LEX--  :ARG1 (i_5<S2>)),(S2()): 88186<br>
   > (i_4<root> / --LEX--  :ARG1 (i_5<S0>)),(S0()): 8502<br>
   > (i_4<root> / --LEX--  :ARG1 (i_5<S0>)),(S0(S2())): 120<br>
   > (i_4<root> / --LEX--  :ARG1 (i_5<S1>)),(S1()): 73<br>
   > (i_4<root> / --LEX--  :ARG1 (i_5<S1>)),(S1(S2())): 30<br>
   > (i_4<root> / --LEX--  :ARG1 (i_5<S2>)),(S2(S1())): 1<br>
   > (i_4<root> / --LEX--  :ARG1 (i_5<S0>)),(S0(S1())): 1
    
   * For each supertag, prints an amconll file of all sentences containing a word that is assigned that supertag. Because supertags are full of weird symbols, files are instead numbered. `<i>_<j>.amconll` where `<i>` is the number printed before the graph constant, e.g. `3` above, and `<j>` is the index of the supertag in the list of supertags under that graph, starting at 0. In the example above, to find the 120 sentences that contain the graph constant `[i_4<root>/--LEX-- -ARG1-> i_5]` with supertag `(i_4<root> / --LEX--  :ARG1 (i_5<S0>)),(S0(S2()))`, look in file `3_2.amconll`.
   
   
### Counting and printing more stuff

You can write new Java scripts to count and print examples of other phenomena. The methods for printing live in `CountSources`. Use the existing scripts as a model. To make it easy to incorporate it into the script `all_counts.sh`, name it `Count<Something>`. 

Note also there is a bug where for each large category we print the number of subcategories instead of the total number of sentences in that large category.


   
 ## Visualising examples
 
We used a script from `am-parser` designed to compare two different analyses, so it will show the AM dep-tree twice. We used the ["own GUI approach"](https://github.com/coli-saar/am-parser/wiki/Error-analysis:-visualization-of-AM-dependency-trees#2-the-own-gui-approach).

You can visualise a random sample of AM dep-trees from the subcorpus amconll files you generated with the Java scripts. To make your life easier, you can use the script `analyzers/visualise_unsupervised.sh` which takes as argument the path to the amconll file you want to visualise samples from. It will filter out sentences shorter than 5 and longer than 15 words, randomise the order, and display the AM dependency trees. 

```bash
bash visualise_unsupervised.sh <path/to/output/amconll_file.amconll>
```

Note it won't show the final graphs; try https://github.com/coli-saar/am-parser/wiki/Error-analysis:-visualization-of-AM-dependency-trees#4-get-pdf-with-graph-for-one-sentence if you want to see the graph for a sentence. 

If you want to change the filtering or seed, see https://github.com/coli-saar/am-parser/wiki/Error-analysis:-visualization-of-AM-dependency-trees#2-the-own-gui-approach. 


## Supertag entropy

You can compare the supertag entropy for the neural and EM outputs.

### Script

There is a bash script `am-parser/analyzers/entropy.sh`. It assumes the amconll files are called `DM.amconll` etc., but it's very simple so you can edit it if needed. It prints to standard output, so you can pipe it to a file in the bash command if you want to keep it. (i.e. append `> path/to/entropy_file.txt` to the bash code below.) 

`cd` to `analyzers/` and run: 

```bash
bash entropy.sh <path/to/am-tools.jar> <path/to/neural/output/> <path/to/EM/output/>
```
