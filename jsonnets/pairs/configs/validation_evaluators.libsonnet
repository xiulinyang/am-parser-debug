local k = 6;
local eval_commands = import 'eval_commands.libsonnet';
local give_up = 15; #15 seconds

local sdp_evaluator(dataset_reader, data_iterator, name, threads, from_epoch) = {
        "type": "standard_evaluator",
        "formalism" : name,
        "system_input" : "data/SemEval/2015/"+name+"/dev/dev.amconll",
        "gold_file": "data/SemEval/2015/"+name+"/dev/dev.sdp",
        "use_from_epoch" : from_epoch,
        "predictor" : {
                "type" : "amconll_predictor",
                "dataset_reader" : dataset_reader, #same dataset_reader as above.
                "data_iterator" : data_iterator, #same bucket iterator also for validation.
                "k" : k,
                "threads" : threads,
                "give_up": give_up,
                "evaluation_command" : eval_commands['commands'][name]
        }

};


#Defines validation evaluators for the formalisms
function (dataset_reader, data_iterator) {
  "AMR-2015" :  {
        "type": "standard_evaluator",
        "formalism" : "AMR-2015",
        "system_input" : "data/AMR/2015/dev/dev.amconll",
        "gold_file": "dev",
        "use_from_epoch" : 25,
        "predictor" : {
                "type" : "amconll_predictor",
                "dataset_reader" : dataset_reader, #same dataset_reader as above.
                "data_iterator" : data_iterator, #same bucket iterator also for validation.
                "k" : k,
                "threads" : 4,
                "give_up": give_up, #try parsing only for 1 second, then retry with smaller k
                "evaluation_command" : eval_commands['commands']['AMR-2015']
        }

  },

    "AMR-2017" :  {
        "type": "standard_evaluator",
        "formalism" : "AMR-2017",
        "system_input" : "data/AMR/2017/dev/dev.amconll",
        "gold_file": "dev",
        "use_from_epoch" : 25,
        "predictor" : {
                "type" : "amconll_predictor",
                "dataset_reader" : dataset_reader, #same dataset_reader as above.
                "data_iterator" : data_iterator, #same bucket iterator also for validation.
                "k" : k,
                "threads" : 4,
                "give_up": give_up, #try parsing only for 1 second, then retry with smaller k
                "evaluation_command" : eval_commands['commands']['AMR-2017']
        }

  },

    "DM" : sdp_evaluator(dataset_reader, data_iterator, "DM",2,15),

    "PAS" :  sdp_evaluator(dataset_reader, data_iterator, "PAS",4,20),

    "PSD" :  sdp_evaluator(dataset_reader, data_iterator, "PSD",2,15),

    "EDS" :  {
        "type": "standard_evaluator",
        "formalism" : "EDS",
        "system_input" : "data/EDS/dev/dev.amconll",
        "gold_file": "data/EDS/dev/dev-gold",
        "use_from_epoch" : 15,
        "predictor" : {
                "type" : "amconll_predictor",
                "dataset_reader" : dataset_reader, #same dataset_reader as above.
                "data_iterator" : data_iterator, #same bucket iterator also for validation.
                "k" : k,
                "threads" : 2,
                "give_up": give_up, #try parsing only for 1 second, then retry with smaller k
                "evaluation_command" : eval_commands['commands']['EDS']
        }
    },
     #UD doesn't need special evaluators.
     "EWT" : { "type" :  "dummy_evaluator" },
     "GUM" : { "type" :  "dummy_evaluator" },
     "LinES" : { "type" :  "dummy_evaluator" },
     "ParTUT" : { "type" :  "dummy_evaluator" }


}
