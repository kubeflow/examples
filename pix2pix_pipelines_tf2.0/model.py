from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

#KFP-BEGIN

LAMBDA = 100          # Coefficient to weight the Generator's multiple losses contribution
OUTPUT_CHANNELS = 3   # RGB images

# ------------------------------
#   Helper Functions to build
#   the Pix2Pix GAN Generator
# ------------------------------
#
# The architecture of generator is a modified U-Net.
# Each block in the encoder is
#     (Conv -> Batchnorm -> Leaky ReLU)
# Each block in the decoder is
#      (Transposed Conv -> Batchnorm -> Dropout(applied to the first 3 blocks) -> ReLU)
# There are skip connections between the encoder and decoder (as in U-Net).


def downsample(filters, size, apply_batchnorm=True):
    '''
    U-Net Encoder Building block composed of
    (Conv -> Batchnorm -> Leaky ReLU)

    Args:
        filters (int) : Number of output filters in the convolution
        size    (int) : Size (height and width) of the 2D convolution window
        apply_batchnorm (bool) : True to add Batch Normalization

    Returns:
        result : a Keras sequential Model
    '''

    initializer = tf.random_normal_initializer(0., 0.02)

    result = tf.keras.Sequential()
    result.add(tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',
                             kernel_initializer=initializer, use_bias=False))

    if apply_batchnorm:
        result.add(tf.keras.layers.BatchNormalization())

    result.add(tf.keras.layers.LeakyReLU())

    return result


def upsample(filters, size, apply_dropout=False):
    '''
    U-Net Decoder Building block composed of
    (Transposed Conv -> Batchnorm -> Dropout(applied to the first 3 blocks) -> ReLU)

    Args:
        filters (int) : Number of output filters in the transposed convolution
        size    (int) : Size (height and width) of the 2D transposed convolution window
        apply_dropout (bool) : True to add Dropout

    Returns:
        result : a Keras sequential Model
    '''

    initializer = tf.random_normal_initializer(0., 0.02)

    result = tf.keras.Sequential()
    result.add(
    tf.keras.layers.Conv2DTranspose(filters, size, strides=2,
                                    padding='same',
                                    kernel_initializer=initializer,
                                    use_bias=False))

    result.add(tf.keras.layers.BatchNormalization())

    if apply_dropout:
        result.add(tf.keras.layers.Dropout(0.5))

    result.add(tf.keras.layers.ReLU())

    return result



def Generator():
    '''
    Build the Pix2PIx Generator

    Returns: a Keras Model

    '''
    down_stack = [
    downsample(64, 4, apply_batchnorm=False), # (bs, 128, 128, 64)
    downsample(128, 4), # (bs, 64, 64, 128)
    downsample(256, 4), # (bs, 32, 32, 256)
    downsample(512, 4), # (bs, 16, 16, 512)
    downsample(512, 4), # (bs, 8, 8, 512)
    downsample(512, 4), # (bs, 4, 4, 512)
    downsample(512, 4), # (bs, 2, 2, 512)
    downsample(512, 4), # (bs, 1, 1, 512)
    ]

    up_stack = [
    upsample(512, 4, apply_dropout=True), # (bs, 2, 2, 1024)
    upsample(512, 4, apply_dropout=True), # (bs, 4, 4, 1024)
    upsample(512, 4, apply_dropout=True), # (bs, 8, 8, 1024)
    upsample(512, 4), # (bs, 16, 16, 1024)
    upsample(256, 4), # (bs, 32, 32, 512)
    upsample(128, 4), # (bs, 64, 64, 256)
    upsample(64, 4), # (bs, 128, 128, 128)
    ]

    initializer = tf.random_normal_initializer(0., 0.02)
    last = tf.keras.layers.Conv2DTranspose(OUTPUT_CHANNELS, 4,
                                           strides=2,
                                           padding='same',
                                           kernel_initializer=initializer,
                                           activation='tanh') # (bs, 256, 256, 3)

    concat = tf.keras.layers.Concatenate()

    inputs = tf.keras.layers.Input(shape=[None,None, OUTPUT_CHANNELS])
    x = inputs

    # Downsampling through the model
    skips = []
    for down in down_stack:
        x = down(x)
        skips.append(x)

    skips = reversed(skips[:-1])

    # Upsampling and establishing the skip connections
    for up, skip in zip(up_stack, skips):
        x = up(x)
        x = concat([x, skip])

    x = last(x)

    return tf.keras.Model(inputs=inputs, outputs=x)



# ------------------------------
#   Helper Function to build
# the Pix2Pix GAN Discriminator
# ------------------------------
#
# The Discriminator is a PatchGAN.
# Each block in the discriminator is (Conv -> BatchNorm -> Leaky ReLU)
# The shape of the output after the last layer is (batch_size, 30, 30, 1)
# Each 30x30 patch of the output classifies a 70x70 portion of the input image
#  (such an architecture is called a PatchGAN).
# Discriminator receives 2 inputs.
#   - Either, Input image and the target image, which it should classify as real.
#   - or, Input image and the generated image (output of generator),
#     which it should classify as fake.
#   - These 2 inputs are concateneted together in the code

def Discriminator():
    '''
    Build the Pix2PIx Discriminator

    Returns: a Keras Model

    '''
    initializer = tf.random_normal_initializer(0., 0.02)

    inp = tf.keras.layers.Input(shape=[None, None, OUTPUT_CHANNELS], name='input_image')
    tar = tf.keras.layers.Input(shape=[None, None, OUTPUT_CHANNELS], name='target_image')

    x = tf.keras.layers.concatenate([inp, tar]) # (bs, 256, 256, channels*2)

    down1 = downsample(64, 4, False)(x) # (bs, 128, 128, 64)
    down2 = downsample(128, 4)(down1) # (bs, 64, 64, 128)
    down3 = downsample(256, 4)(down2) # (bs, 32, 32, 256)

    zero_pad1 = tf.keras.layers.ZeroPadding2D()(down3) # (bs, 34, 34, 256)
    conv = tf.keras.layers.Conv2D(512, 4, strides=1,
                                  kernel_initializer=initializer,
                                  use_bias=False)(zero_pad1) # (bs, 31, 31, 512)

    batchnorm1 = tf.keras.layers.BatchNormalization()(conv)

    leaky_relu = tf.keras.layers.LeakyReLU()(batchnorm1)

    zero_pad2 = tf.keras.layers.ZeroPadding2D()(leaky_relu) # (bs, 33, 33, 512)

    last = tf.keras.layers.Conv2D(1, 4, strides=1,
                                  kernel_initializer=initializer)(zero_pad2) # (bs, 30, 30, 1)

    return tf.keras.Model(inputs=[inp, tar], outputs=last)



# ------------------------------
#  Helper Functions to compute
#   the Discriminator and the
#       Generator losses
# ------------------------------

def discriminator_loss(disc_real_output, disc_generated_output):
    '''
    Compute the Discriminator loss.

    The discriminator loss function takes 2 inputs: real images and generated images

    real_loss is a sigmoid cross entropy loss of the real images
    and an array of ones(since these are the real images)

    generated_loss is a sigmoid cross entropy loss of the generated images
    and an array of zeros(since these are the fake images)

    Then the total_loss is the sum of real_loss and the generated_loss

    Args:
        disc_real_output      : Output of the Discriminator with the real image
        disc_generated_output : Output of the Discriminator with the generated image

    Returns:
        total_disc_loss : Discriminator loss value

    '''

    loss_object = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    real_loss = loss_object(tf.ones_like(disc_real_output), disc_real_output)
    generated_loss = loss_object(tf.zeros_like(disc_generated_output), disc_generated_output)
    total_disc_loss = real_loss + generated_loss

    return total_disc_loss


def generator_loss(disc_generated_output, gen_output, target):
    '''
    Compute the Generator loss.

    It is a sigmoid cross entropy loss of the generated images and an array of ones.

    The paper also includes L1 loss which is MAE (mean absolute error)
    between the generated image and the target image.
    This allows the generated image to become structurally similar to the target image.

    The formula to calculate the total generator loss is
    Generator_loss = gan_loss + LAMBDA * l1_loss, where LAMBDA = 100
    (This value was decided by the authors of the paper.

    Args:
        disc_generated_output : Output of the Discriminator with the generated image
        gen_output            : Generated image
        target                : Target image

    Returns:
        total_gen_loss        : Generator loss value

    '''

    loss_object = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    gan_loss = loss_object(tf.ones_like(disc_generated_output), disc_generated_output)
    l1_loss = tf.reduce_mean(tf.abs(target - gen_output))  # mean absolute error
    total_gen_loss = gan_loss + (LAMBDA * l1_loss)

    return total_gen_loss

#KFP-END