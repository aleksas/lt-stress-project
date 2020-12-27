# coding=utf-8
# Copyright 2020 The Tensor2Tensor Authors.
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

"""Query an exported model. Py2 only. Install tensorflow-serving-api."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from oauth2client.client import GoogleCredentials
from six.moves import input  # pylint: disable=redefined-builtin

from tensor2tensor import problems as problems_lib  # pylint: disable=unused-import
from tensor2tensor.serving import serving_utils
from tensor2tensor.utils import hparam
from tensor2tensor.utils import registry
from tensor2tensor.utils import usr_dir
import tensorflow.compat.v1 as tf

from flask import Flask, request, render_template
import json

def make_request_fn():
  request_fn = serving_utils.make_grpc_request_fn(
        servable_name=os.environ['MODEL_NAME'],
        server=os.environ['MODEL_SERVER_ADDRESS'],
        timeout_secs=10)

  return request_fn

print (os.environ)

tf.logging.set_verbosity(tf.logging.INFO)
usr_dir.import_usr_dir(os.environ['PROBLEM_DIR'])
problem = registry.problem(os.environ['PROBLEM_NAME'])
hparams = hparam.HParams(
    data_dir=os.path.expanduser(os.environ['DATA_DIR']))
problem.get_hparams(hparams)
request_fn = make_request_fn()

app = Flask(__name__, template_folder='.')

@app.route('/api/stress', methods=['GET', 'POST'])
def stress():
    payload = request.get_json()
    inputs = payload['input'] if payload else []
    outputs = serving_utils.predict([inputs], problem, request_fn)
    outputs, = outputs
    output, score = outputs
    if len(score.shape) > 0:  # pylint: disable=g-explicit-length-test
      score = [float(s) for s in score]
    else:
      score = float(score)
    result = {'output': output, 'score': score}
    return json.dumps(result), 200, {'ContentType':'application/json'} 

@app.route('/')
def index():
    return render_template('index.html')
