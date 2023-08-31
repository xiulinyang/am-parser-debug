#CHECKLIST:

# Tasks?
# Main task?
# Freda?
# Evaluate on test?
# Evaluate on the right test corpora?

local num_epochs = 40;
local device = 2;
local pos_dim = 32;
local lemma_dim = 64;
local ner_dim = 16;

local char_dim = 100;
local num_filters = 50;
local filters = [3];
local max_filter = 3; //KEEP IN SYNC WITH filters!

local test_evaluators = import '../../../../configs/test_evaluators.libsonnet';

local data_paths = import '../../../../configs/data_paths.libsonnet';

local eval_commands = import '../../../../configs/eval_commands.libsonnet';

local UD_banks = data_paths["UD_banks"];

local task_models = import '../../../../configs/task_models_wo_eval.libsonnet';

local bert_model = "bert-large-uncased";

local encoder_output_dim = 256; #encoder output dim, per direction, so total will be twice as large

#=========FREDA=========
local use_freda = 0; #0 = no, 1 = yes
#=======================

local final_encoder_output_dim = 2 * encoder_output_dim + use_freda * 2 * encoder_output_dim; #freda again doubles output dimension

#============TASKS==============
local my_tasks = ["AMR-2017"];
local main_task = "AMR-2017"; #what validation metric to pay attention to.
#===============================

local dataset_reader = {
        "type": "amconll",
        "token_indexers": {
            "bert": {
              "type": "bert-pretrained",
              "pretrained_model": bert_model,
            },
            "token_characters" : {
                           "type" : "characters",
                           "min_padding_length" : max_filter
           }
        }
      };

local data_iterator = {
        "type": "same_formalism",
        "batch_size": 32,
        "formalisms" : my_tasks
    };


{
    "dataset_reader": dataset_reader,
    "iterator": data_iterator,
     "vocabulary" : {
            "min_count" : {
            "lemmas" : 7
     }
     },
    "model": {
        "type": "graph_dependency_parser",

        "tasks" : [task_models(task_name,dataset_reader, data_iterator, final_encoder_output_dim, "kg_edges","dm_edge_loss","dm_label_loss") for task_name in my_tasks],

        "input_dropout": 0.3,
        "encoder": {
            "type" : if use_freda == 1 then "freda_split" else "shared_split_encoder",
            "formalisms" : my_tasks,
            "formalisms_without_tagging": UD_banks,
            "task_dropout" : 0.0,
            "encoder": {
                "type": "stacked_bidirectional_lstm",
                "num_layers": 1,
                "recurrent_dropout_probability": 0.4,
                "layer_dropout_probability": 0.3,
                "use_highway": false,
                "hidden_size": encoder_output_dim,
                "input_size": num_filters + 1024 + pos_dim + lemma_dim + ner_dim
            }
        },

        "pos_tag_embedding":  {
           "embedding_dim": pos_dim,
           "vocab_namespace": "pos"
        },
        "lemma_embedding":  {
           "embedding_dim": lemma_dim,
           "vocab_namespace": "lemmas"
        },
         "ne_embedding":  {
           "embedding_dim": ner_dim,
           "vocab_namespace": "ner_labels"
        },

        "text_field_embedder": {
            "type": "basic",
            "allow_unmatched_keys" : true,
            "embedder_to_indexer_map": {
                "bert": ["bert", "bert-offsets"], "token_characters" : ["token_characters"] },
            "token_embedders": {
                "bert" : {
                    "type": "bert-pretrained",
                        "pretrained_model" : bert_model,
                    },

                "token_characters": {
                  "type": "character_encoding",
                      "embedding": {
                        "embedding_dim": char_dim
                      },
                      "encoder": {
                        "type": "cnn",
                        "embedding_dim": char_dim,
                        "num_filters": num_filters,
                        "ngram_filter_sizes": filters
                      }
                }
             }
        },

    },
    "train_data_path": [ [task_name, data_paths["train_data"][task_name]] for task_name in my_tasks],
    "validation_data_path": [ [task_name,data_paths["gold_dev_data"][task_name]] for task_name in my_tasks],


    #=========================EVALUATE ON TEST=================================
    "evaluate_on_test" : false,
    "test_evaluators" : [test_evaluators(dataset_reader, data_iterator)[main_task]], #when training is done, call evaluation on test sets with best model as described here.
    #==========================================================================

    "trainer": {
        "type" : "am-trainer",
        "num_epochs": num_epochs,
        "patience" : 10,
        "cuda_device": device,
        "optimizer": {
            "type": "adam",
        },
        "validation_metric" : "+"+main_task+"_mean_constant_acc_las",
        "num_serialized_models_to_keep" : 1
    }
}

