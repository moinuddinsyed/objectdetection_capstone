import tensorflow as tf
import os
import pandas as pd
from PIL import Image

import dataset_util


flags = tf.app.flags
flags.DEFINE_string('output_path', '/home/syed/MLND/capstone_OD/trainprep/data/train.record', 'Path to output TFRecord')
FLAGS = flags.FLAGS


def create_tf_example(image_det, image_path, pdt):
  # TODO(user): Populate the following variables from your example.
    with tf.gfile.Open(image_path) as image_file:
        encoded_image_data = image_file.read()
    with Image.open(image_path) as img:
        width, height = img.size

    filename = os.path.basename(image_path) # Filename of the image. Empty if image is not from file
    image_format = image_path.split('.')[-1] # b'jpeg' or b'png'


    xmins = [] # List of normalized left x coordinates in bounding box (1 per box)
    xmaxs = [] # List of normalized right x coordinates in bounding box  (1 per box)
    ymins = [] # List of normalized top y coordinates in bounding box (1 per box)
    ymaxs = [] # List of normalized bottom y coordinates in bounding box
             # (1 per box)
    classes_text = [] # List of string class name of bounding box (1 per box)
    classes = [] # List of integer class id of bounding box (1 per box)

    for row in image_det.iterrows():
        xmin = row[1]['XMin']
        xmax = row[1]['XMax']
        ymin = row[1]['YMin']
        ymax = row[1]['YMax']
        class_text = row[1]['LabelName']
        class_ = pdt[pdt['labelid']==class_text].id.values[0]
        xmins.append(xmin)
        xmaxs.append(xmax)
        ymins.append(ymin)
        ymaxs.append(ymax)
        classes_text.append(class_text)
        classes.append(class_)

    tf_example = tf.train.Example(features=tf.train.Features(feature={
      'image/height': dataset_util.int64_feature(height),
      'image/width': dataset_util.int64_feature(width),
      'image/filename': dataset_util.bytes_feature(filename),
      'image/source_id': dataset_util.bytes_feature(filename),
      'image/encoded': dataset_util.bytes_feature(encoded_image_data),
      'image/format': dataset_util.bytes_feature(image_format),
      'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
      'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
      'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
      'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
      'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
      'image/object/class/label': dataset_util.int64_list_feature(classes),
  }))
    return tf_example


def main(_):
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)

  # TODO(user): Write code to read in your dataset to examples variable
    path = '/home/syed/MLND/capstone_OD/data/images'
    pdt_bbox = pd.read_csv('/home/syed/MLND/capstone_OD/data/product_bbox.csv')
    pdt = pd.read_csv('/home/syed/MLND/capstone_OD/data/products.csv')
    for image in os.listdir(path):
        imageid = image.split('.')[0]
        image_det = pdt_bbox[pdt_bbox['ImageID'] == imageid]


        tf_example = create_tf_example(image_det,os.path.join(path,image),pdt)
        writer.write(tf_example.SerializeToString())

    writer.close()


if __name__ == '__main__':
  tf.app.run()