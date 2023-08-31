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
from allennlp.common.registrable import Registrable
import torch

from abc import ABC, abstractmethod


class EdgeExistenceLoss(Registrable,ABC):

    def __init__(self, normalize_wrt_seq_len : bool = False):
        super().__init__()
        self.normalize_wrt_seq_len = normalize_wrt_seq_len

    @abstractmethod
    def loss(self, edge_scores: torch.Tensor,
                            head_indices: torch.Tensor,
                            mask: torch.Tensor) -> torch.Tensor:
        """
        Computes the edge loss for a batch with edge_scores given gold heads.

        Parameters
        ----------
        edge_scores : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length, sequence_length) used to generate
            a distribution over attachments of a given word to all other words.
        head_indices : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length).
            The indices of the heads for every word.
        mask : ``torch.Tensor``, required.
            A mask of shape (batch_size, sequence_length), denoting unpadded
            elements in the sequence.

        Returns
        -------
        loss : ``torch.Tensor``, required.
            The edge loss.
        """
        raise NotImplementedError()


class EdgeLabelLoss(Registrable,ABC):

    def __init__(self, normalize_wrt_seq_len : bool = False):
        super().__init__()
        self.normalize_wrt_seq_len = normalize_wrt_seq_len

    @abstractmethod
    def loss(self, edge_label_logits: torch.Tensor, mask: torch.Tensor, head_tags: torch.Tensor) -> torch.Tensor:
        """
        Computes the edge label loss for a sequence and gold edge labels.

        Parameters
        ----------
        edge_label_logits : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length, num_head_tags),
            that contains raw predictions for incoming edge labels
        head_tags : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length).
            The dependency labels of the heads for every word.
        mask : ``torch.Tensor``, required.
            A mask of shape (batch_size, sequence_length), denoting unpadded
            elements in the sequence.

        Returns
        -------
        loss : ``torch.Tensor``, required.
            The edge label loss.
        """
        raise NotImplementedError()


class EdgeLoss(Registrable):
    """
    Interface for edge loss.
    """
    def __init__(self, existence_loss: EdgeExistenceLoss, label_loss: EdgeLabelLoss) -> None:

        super().__init__()
        self.existence = existence_loss
        self.label = label_loss

    def label_loss(self, edge_label_logits: torch.Tensor, mask: torch.Tensor, head_tags: torch.Tensor) -> torch.Tensor:
        """
        Computes the edge label loss for a sequence and gold edge labels.

        Parameters
        ----------
        edge_label_logits : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length, num_head_tags),
            that contains raw predictions for incoming edge labels
        head_tags : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length).
            The dependency labels of the heads for every word.
        mask : ``torch.Tensor``, required.
            A mask of shape (batch_size, sequence_length), denoting unpadded
            elements in the sequence.

        Returns
        -------
        loss : ``torch.Tensor``, required.
            The edge label loss.
        """
        return self.label.loss(edge_label_logits, mask, head_tags)

    def edge_existence_loss(self, edge_scores: torch.Tensor,
                            head_indices: torch.Tensor,
                            mask: torch.Tensor) -> torch.Tensor:
        """
        Computes the edge loss for a sequence given gold heads.

        Parameters
        ----------
        edge_scores : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length, sequence_length) used to generate
            a distribution over attachments of a given word to all other words.
        head_indices : ``torch.Tensor``, required.
            A tensor of shape (batch_size, sequence_length).
            The indices of the heads for every word.
        mask : ``torch.Tensor``, required.
            A mask of shape (batch_size, sequence_length), denoting unpadded
            elements in the sequence.

        Returns
        -------
        loss : ``torch.Tensor``, required.
            The edge loss.
        """
        return self.existence.loss(edge_scores,head_indices,mask)



