#
# Copyright (c) 2020 Saarland University.
#
# This file is part of AM Parser
# (see https://github.com/coli-saar/am-parser/).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from tempfile import TemporaryDirectory
from typing import Dict, Any
import logging
import json

from allennlp.common.checks import ConfigurationError
from allennlp.common.util import prepare_environment

from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.iterators import DataIterator
from allennlp.models.archival import load_archive
from allennlp.common import Params

from graph_dependency_parser.components.dataset_readers.amconll_tools import from_raw_text
from graph_dependency_parser.components.evaluation.predictors import AMconllPredictor
from graph_dependency_parser.components.spacy_interface import spacy_tokenize
from graph_dependency_parser.graph_dependency_parser import GraphDependencyParser

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


import graph_dependency_parser.graph_dependency_parser
import graph_dependency_parser.important_imports
import argparse

parser = argparse.ArgumentParser(description="Run the am-parser on a text file in order to annotate it with parses"
                                             "in amconll format, doesn't perform tokenization (assumes spaces to"
                                             "separate tokens) or other preprocessing (POS tagging, lemmatization)."
                                             "Instead relies on just BERT for performance.")

parser.add_argument('archive_file', type=str, help='path to an archived trained model')
parser.add_argument('formalism', type=str, help='name of formalism (must be included in the model)')
parser.add_argument('input_file', type=str, help='path to the file containing the evaluation data')
parser.add_argument('output_file', type=str, help='path to where output shall be written')

parser.add_argument('-k',
                       type=int,
                       default=6,
                       help='number of supertags to be used')
parser.add_argument('-t',"--threads",
                       type=int,
                       default=4,
                       help='number of threads')

parser.add_argument('--give_up',
                       type=float,
                       default=60*60,
                       help='number of seconds until fixed-tree decoder backs off to k-1')

parser.add_argument('--tokenize',
                       action='store_true',
                       default=False,
                       help="Assume untokenized sentences and tokenize using spacy.")

parser.add_argument('-v',
                       action='store_true',
                       default=False,
                       help='verbose logging')

cuda_device = parser.add_mutually_exclusive_group(required=False)
cuda_device.add_argument('--cuda-device',
                         type=int,
                         default=-1,
                         help='id of GPU to use (if any)')

parser.add_argument('--weights-file',
                       type=str,
                       help='a path that overrides which weights file to use')

parser.add_argument('-o', '--overrides',
                       type=str,
                       default="",
                       help='a JSON structure used to override the experiment configuration')

parser.add_argument('--batch-weight-key',
                       type=str,
                       default="",
                       help='If non-empty, name of metric used to weight the loss on a per-batch basis.')

parser.add_argument('--extend-vocab',
                       action='store_true',
                       default=False,
                       help='if specified, we will use the instances in your new dataset to '
                            'extend your vocabulary. If pretrained-file was used to initialize '
                            'embedding layers, you may also need to pass --embedding-sources-mapping.')

parser.add_argument('--embedding-sources-mapping',
                       type=str,
                       default="",
                       help='a JSON dict defining mapping from embedding module path to embedding'
                       'pretrained-file used during training. If not passed, and embedding needs to be '
                       'extended, we will try to use the original file paths used during training. If '
                       'they are not available we will use random vectors for embedding extension.')

args = parser.parse_args()
if args.v:
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        level=logging.INFO)  # turn on logging.
    # Disable some of the more verbose logging statements
    logging.getLogger('allennlp.common.params').disabled = True
    logging.getLogger('allennlp.nn.initializers').disabled = True
    logging.getLogger('allennlp.modules.token_embedders.embedding').setLevel(logging.INFO)

# Load from archive
archive = load_archive(args.archive_file, args.cuda_device, args.overrides, args.weights_file)
config = archive.config
prepare_environment(config)
model = archive.model
model.eval()
if not isinstance(model, GraphDependencyParser):
    raise ConfigurationError("The loaded model seems not to be an am-parser (GraphDependencyParser)")
if not args.formalism in model.tasks:
    raise ConfigurationError(f"The model at hand was not trained on {args.formalism} but on {list(model.tasks.keys())}")

# Load the evaluation data

# Try to use the validation dataset reader if there is one - otherwise fall back
# to the default dataset_reader used for both training and validation.
validation_dataset_reader_params = config.pop('validation_dataset_reader', None)
if validation_dataset_reader_params is not None:
    dataset_reader = DatasetReader.from_params(validation_dataset_reader_params)
else:
    dataset_reader = DatasetReader.from_params(config.pop('dataset_reader'))
evaluation_data_path = args.input_file

embedding_sources: Dict[str, str] = (json.loads(args.embedding_sources_mapping)
                                     if args.embedding_sources_mapping else {})
if args.extend_vocab:
    logger.info("Vocabulary is being extended with test instances.")
    logger.info("Reading evaluation data from %s", evaluation_data_path)
    instances = dataset_reader.read(evaluation_data_path)
    model.vocab.extend_from_instances(Params({}), instances=instances)
    model.extend_embedder_vocab(embedding_sources)


predictor = AMconllPredictor(dataset_reader,args.k,args.give_up, args.threads, model=model)

requires_art_root = {"DM" : True, "PAS": True, "PSD": True, "EDS" : False, "AMR-2015": False, "AMR-2017": False}
requires_ne_merging = {"DM" : False, "PAS": False, "PSD": False, "EDS" : False, "AMR-2015": True, "AMR-2017": True}

sentences = []
with open(args.input_file) as f:
    for sentence in f:
        sentence = sentence.rstrip("\n")
        if args.tokenize:
            words = spacy_tokenize(sentence)
        else:
            words = [word.strip() for word in sentence.rstrip("\n").split(" ") if word.strip()]
        sentences.append(from_raw_text(sentence.rstrip("\n"),words,requires_art_root[args.formalism], dict(),requires_ne_merging[args.formalism]))

with TemporaryDirectory() as direc:
    temp_path =  direc+"/sentences.amconll"
    with open(temp_path,"w") as f:
        for sentence in sentences:
            f.write(str(sentence))
            f.write("\n\n")
    predictor.parse_and_save(args.formalism, temp_path, args.output_file)

logger.info("Finished parsing.")
