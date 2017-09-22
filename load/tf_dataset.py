import tensorflow as tf
import random
import logging
from load.ndat_header import NdatHeader
from google.cloud import storage


def get_example_parser(header):
	def parse_example(example_raw):
		features_raw = tf.substr(example_raw, 0, header.feature_bytes)
		labels_raw = tf.substr(example_raw, header.feature_bytes, header.label_bytes)

		features = tf.decode_raw(features_raw, header.feature_type)
		labels = tf.decode_raw(labels_raw, header.label_type)

		return tf.reshape(features, [header.feature_width, header.feature_channels]), tf.reshape(labels, [header.label_width])

	return parse_example


def from_filenames(filenames):
	random.shuffle(filenames)
	num_files = len(filenames)

	if num_files == 0:
		raise ValueError('No files found')

	header = NdatHeader.from_file(filenames[0])

	dataset = tf.contrib.data.FixedLengthRecordDataset(filenames, header.example_bytes, header_bytes=NdatHeader.HEADER_SIZE)
	dataset = dataset.map(get_example_parser(header), num_threads=8, output_buffer_size=50000)
	return dataset


storage_client = storage.Client(project='transient-finder-training')


def from_bucket(bucket_name, prefix=None):
	data_bucket = storage.bucket.Bucket(storage_client, bucket_name)

	filenames = []
	blobs = []

	for blob in data_bucket.list_blobs(prefix=prefix):
		if blob.name.endswith('/'):
			continue

		blobs.append(blob)
		path = 'gs://' + data_bucket.name + '/' + blob.name
		filenames.append(path)

	num_files = len(filenames)

	if num_files == 0:
		raise ValueError('No files found')

	logging.info('Found ' + str(num_files) + ' files.')

	header = NdatHeader.from_blob(blobs[0])

	dataset = tf.contrib.data.FixedLengthRecordDataset(filenames, header.example_bytes, header_bytes=NdatHeader.HEADER_SIZE)
	dataset = dataset.map(get_example_parser(header), num_threads=8, output_buffer_size=50000)
	return dataset