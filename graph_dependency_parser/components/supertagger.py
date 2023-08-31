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
from typing import Optional

import torch
from allennlp.common.checks import check_dimensions_match
from allennlp.data import Vocabulary
from allennlp.models import Model
from allennlp.modules import FeedForward
from allennlp.nn import RegularizerApplicator


class Supertagger(Model):
    """
    A supertagger, mainly consisting of a MLP.
    """
    def __init__(self,vocab: Vocabulary,
                 mlp : FeedForward,
                 label_namespace : str,
                 regularizer: Optional[RegularizerApplicator] = None ):

        super().__init__(vocab=vocab, regularizer=regularizer)
        self.mlp = mlp
        self._encoder_dim = mlp.get_input_dim()

        self.output_layer = torch.nn.Linear(mlp.get_output_dim(),vocab.get_vocab_size(label_namespace))

    def compute_logits(self, encoded_text : torch.Tensor) -> torch.Tensor:
        """
        Computes class logits for every word in the sentence in the batch.

        :param encoded_text: a tensor of shape (batch_size, seq_len, encoder_dim)
        :return: a tensor of shape (batch_size, seq_len, num_supertag_labels)
        """
        return self.output_layer(self.mlp(encoded_text))

    @staticmethod
    def top_k_supertags(logits: torch.Tensor, k : int) -> torch.Tensor:
        """
        Finds the top k supertags for every word (and every sentence in the batch).
        Does not include scores for supertags.

        :param logits: tensor of shape (batch_size, seq_len, num_supetag_labels)
        :return: tensor of shape (batch_size, seq_len, k)
        """
        assert k > 0, "Number of supertags must be positive"
        #shape (batch_size, seq_len, k)
        top_k = torch.argsort(logits,descending=True,dim=2)[:,:,:k]
        
        return top_k

    def encoder_dim(self):
        return self._encoder_dim


