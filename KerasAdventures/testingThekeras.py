import tensorflow as tf

print(tf.__version__)

import numpy as np
import pandas as pd

import  matplotlib.pyplot as plt

from subprocess import check_output


def get_features_labels(df):
    features = df.values[:,1:]/255

    labels = df["label"].values

    return features, labels


data_train_file = r"data/fashion-mnist_train.csv"
data_test_file = r"data/fashion-mnist_test.csv"

df_train = pd.read_csv(data_train_file)
df_test = pd.read_csv(data_test_file)

train_features, train_labels = get_features_labels(df_train)
test_features, test_labels = get_features_labels(df_test)

print(train_features.shape)
print(train_labels.shape)

train_labels = tf.keras.utils.to_categorical(train_labels)
test_labels = tf.keras.utils.to_categorical(test_labels)

print(train_labels.shape)


model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(30,activation=tf.nn.relu,input_shape=(784,)))
model.add(tf.keras.layers.Dense(20,activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(10,activation=tf.nn.softmax))

model.compile(loss='categorical_crossentropy',
              optimizer="rmsprop",
              metrics=['accuracy'])

model.summary()

EPOCHS = 2
BATCH_SIZE = 128

model.fit(train_features,train_labels,epochs=EPOCHS,batch_size=BATCH_SIZE)

test_loss,test_acc = model.evaluate(test_features,test_labels)


print(f"test_acc: {test_acc}")

