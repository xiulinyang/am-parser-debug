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
import json
import sys
import itertools
from tqdm import tqdm

def extract_anchor(j):
    return (j["from"], j["to"])

def extract_all_anchors(j):
    if "anchors" in j:
        return [extract_anchor(a) for a in j["anchors"]]
    else:
        return []


companion_filename = sys.argv[1]
mrp_filename = sys.argv[2]

print(f"Comparing tokens in companion file {companion_filename} with MRP file {mrp_filename}")


# collect token ranges in companion data

companion_tokens = {}

with open(companion_filename, "r") as f:
    for line in tqdm(f):
        j = json.loads(line)
        id = j["id"]
        anchors = [[extract_anchor(a) for a in b["anchors"]] for b in j["nodes"]]
        companion_tokens[id] = set(itertools.chain(*anchors))



# collect token ranges in UCCA MRP graphs
ucca_mrp_files = [mrp_filename]
num_missing_tr = 0
num_total_tr = 0

for file in ucca_mrp_files:
    print(f"Analyzing {file}...")

    with open(file, "r") as f:
        for line in tqdm(f):
            j = json.loads(line)
            id = j["id"]
            companion_anchors = companion_tokens[id]

            anchors = [extract_all_anchors(b) for b in j["nodes"]]

            for anch in itertools.chain(*anchors):
                num_total_tr += 1

                if not anch in companion_anchors:
                    print(f"[{id}] mismatched anchor: {anch}")
                    num_missing_tr += 1

print(f"{num_missing_tr} anchors mismatched out of {num_total_tr} ({100*num_missing_tr/num_total_tr:.2f}%)")

