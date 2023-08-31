
#============TRAINING PARAMETERS==============
local batch_size = 32; # adjust this to fit the memory capacity of your machine (mostly GPU memory is relevant)
local num_epochs = 100; # we recommend 40-100 epochs on real datasets and 200 epochs for toy datasets, but your optimal parameters may differ
local patience = 10; # this is per default set to 1000 to turn off early stopping.
local evaluate_on_test = false; # Whether to evaluate on the test set.


#============FILEPATHS==============
local train_zip_path = "/local/xiulyang/am-parser/output/train.zip";  
local dev_zip_path = "/local/xiulyang/am-parser/output/dev.zip";
local validation_amconll_path = "/local/xiulyang/am-parser/output/drt_evaluation.amconll";
local validation_gold_path = "/local/xiulyang/am-parser/output/dev_gold.txt";
#local test_triples_amconll_gold_suffix = [["ENTERPATH/test.amconll", "ENTERPATH/test_gold.txt", ""]];  # each triple consists of (a) path to amconll input for test set; (b) path to gold output for test set; (c) a suffix to be attached to the names of the evaluation metrics. Use multiple triples to evaluate on multiple test sets. In the regular case of just using one test set, use just one triple and the suffix can be the empty string.


#=============IMPORTING MODEL AND FORMALISM CONFIGS==================
local formalism_config = import '/local/xiulyang/am-parser/jsonnets/drs.libsonnet';

local raw_model_config = import '/local/xiulyang/am-parser/jsonnets/unsupervised2020/formalisms/models/default2021.libsonnet';





#==================PUTTING IT ALL TOGETHER (DO NOT MODIFY) ===================
# This puts everything above together. You should not need to modify anything below this line

# Putting the parameters of this file and the formalism config into the model config file (this is necessary due to how the jsonnet structures are organized/nested)
local model_config = raw_model_config(batch_size, num_epochs, patience, formalism_config['task'], formalism_config['evaluation_command'], formalism_config['validation_metric'], validation_amconll_path, validation_gold_path, test_triples_amconll_gold_suffix);

# Now we can write down all of the actual config entries
{
	"dataset_reader": model_config['dataset_reader'],
    "iterator": model_config['iterator'],
    "vocabulary" : model_config['vocabulary'],
    "model":  model_config['model'],
	
    "train_data_path": [ [formalism_config['task'], train_zip_path]],
    "validation_data_path": [ [formalism_config['task'], dev_zip_path]],


    #=========================EVALUATE ON TEST=================================
    "evaluate_on_test" : evaluate_on_test,
    "test_evaluators" : model_config['test_evaluators'],
    #==========================================================================

    "trainer" : model_config['trainer'],
}

