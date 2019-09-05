from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags

# -------------------------------------
#   Kubeflow Pipeline Component code
# -------------------------------------
#
#  Note: In order to build a Kubeflow
#  pipeline, we need to specify the
#  input/output types of the python
#  function used to build a Kubeflow
#  pipeline component.
# -------------------------------------
def download_dataset(fname: str, origin: str, cachedir: str = "./", cachesubdir: str = 'datasets') -> str:
  """
  Download Pix2Pix datasets.

  By default the file at the url `origin` is downloaded to the
  cache_dir `./`, placed in the cache_subdir `datasets`,
  and given the filename `fname`. The final location of a file
  `example.txt` would therefore be `./datasets/example.txt`.

  Args:
    fname       (string) : File name of the dataset archive (i.e "maps.tar.gz")
    origin      (string) : Full url to download the dataset archive
    cachedir    (string) : Cache directory to use
    cachesubdir (string) : Cache subdirectory to use

  Returns:
    data_path (string) : path to uncompressed dataset directory
  """

  # ------------------------------
  # In order to be able to convert
  #  a Python Function directly
  #  into a Kubeflow component,
  #   we need to move the python
  #  includes inside that python
  #  function.
  # ------------------------------
  import tensorflow as tf
  import os

  try:
    # Use Keras.utils to download the dataset archive
    data_path = tf.keras.utils.get_file(fname, origin,
                      extract=True,
                      archive_format='auto',
                      cache_dir=cachedir,
                      cache_subdir=cachesubdir)

    data_path = os.path.join(os.path.dirname(data_path), fname[:-len(".tar.gz")])
    print("Path location to the dataset images is {}".format(data_path))
    print("{} contains {}".format(data_path, os.listdir(data_path)))


    # ------------------------------
    #     Write the Output of the
    #   Kubeflow Pipeline Component
    # ------------------------------
    try:
      # This works only inside Docker containers
      with open('/output.txt', 'w') as f:
        f.write(data_path)

    except PermissionError:
      pass

    return data_path

  except ConnectionError:
    print('Failed to download the dataset at url {}'.format(origin))
    return None


# ---------
#   Main
# ---------
def main(argv):
  del argv  # Unused
  download_dataset(FLAGS.fname, FLAGS.origin, FLAGS.cachedir, FLAGS.cachesubdir)


if __name__ == '__main__':

  flags.DEFINE_string('fname', 'facades.tar.gz', 'file name of the dataset archive')
  flags.DEFINE_string('origin',
            'https://people.eecs.berkeley.edu/~tinghuiz/projects/pix2pix/datasets/facades.tar.gz',
            'Full url to download the dataset archive')
  flags.DEFINE_string('cachedir', './', 'Cache directory to use')
  flags.DEFINE_string('cachesubdir', 'datasets', 'Cache subdirectory to use')

  FLAGS = flags.FLAGS

  app.run(main)
  