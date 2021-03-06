import logging
import time
import os
from argparse import ArgumentParser

import tensorflow as tf
import nn

from load import Wave, WaveTF
from predict.model import magnitude_model as model, calc_cost

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

parser = ArgumentParser()

parser.add_argument('--input-file', help="Specify input file path", required=True)
parser.add_argument('--label-file', help="Specify label file path")
parser.add_argument('--job-dir', type=str, default='./tmp/wav_out')
parser.add_argument('--job-name', type=str, default=time.strftime('%Y-%m-%d_%H-%M-%S'))

args = parser.parse_args()

input_filepath = args.input_file
label_filepath = args.label_file
job_dir = args.job_dir
job_name = args.job_name
channels_last = True

logging.info('Loading input file ' + input_filepath + '...')
wav = WaveTF.from_file(input_filepath)
labels = WaveTF.from_file(label_filepath)

labels = labels.get_data()
inputs = wav.get_data()

start = 0
length = 1000000
end = start + length

inputs = inputs[:, start:end]
labels = labels[:, start:end]

if channels_last:
	inputs = tf.transpose(inputs)
	labels = tf.transpose(labels)

raw_outputs = model(inputs, channels_last=channels_last)
predictions = tf.cast(raw_outputs > 0.4, dtype=tf.float32)
cost = calc_cost(predictions, labels, channels_last=channels_last)

init = tf.global_variables_initializer()

with tf.Session(config=tf.ConfigProto(log_device_placement=False)) as sess:
	sess.run(init)
	cost, output = sess.run([cost, tf.transpose(nn.normalize(predictions))])

	logging.info('Total Cost: ' + str(cost))

	wav_out = Wave(output, sample_rate=wav.sample_rate)
	wav_out.to_file(os.path.join(job_dir, job_name + '_out.wav'))
