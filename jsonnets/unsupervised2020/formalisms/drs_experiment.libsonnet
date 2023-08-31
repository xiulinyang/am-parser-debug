
local ALTO_PATH = "am-tools/build/libs/m-tools.jar";
local tool_dir = "external_eval_tools/";

{
	"task": "DRS",
	"evaluation_command" : {
		"type" : "bash_evaluation_command",
			"command" : "java -cp "+ALTO_PATH+" de.saar.coli.amtools.evaluation.EvaluateAMConll --corpus {system_output} -o {tmp}/ -et EvaluationToolset" + "&& python2 "+tool_dir+"/smatch/smatch.py -f {tmp}/parserOut.txt {gold_file} --pr --significant 4 > {tmp}/metrics.txt && mkdir -p output_parser/{tmp}/ && cat {tmp}/metrics.txt && cp {tmp}/parserOut.txt output_parser/{tmp}/ && cp {tmp}/metrics.txt output_parser/{tmp}/",
			"result_regexes" : {"P" : [0, "Precision: (?P<value>.+)"],
							"R" : [1, "Recall: (?P<value>.+)"],
							"F" : [2, "F-score: (?P<value>.+)"]}
	},
    "validation_metric" : "+DRS_F",
}
