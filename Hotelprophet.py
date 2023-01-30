import random
import numpy as np
import tensorflow as tf
random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

from tensorflow import keras
from keras import layers
import os

def buildmodel(n_features):
    model = keras.Sequential()
    print(n_features.shape)
    model.add(layers.InputLayer(input_shape=[n_features.shape[1],]))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.3))
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(10, activation='softmax'))
    input()
    return model

def getModel(file_name, parameters):

    __location__ = os.path.realpath(os.getcwd())

    reviews = pd.read_csv(file_name)
    data = reviews.to_numpy(copy=True)
    print(reviews.corrwith(reviews.iloc[:, 0]).sort_values(ascending=False))
    print(reviews.isna().any())

    references_plusplus = reviews[parameters].to_numpy(copy=True)
    scores = reviews.iloc[:, 0].to_numpy(copy=True).T
    scores -= 1
    print("scores before one hot")
    print(scores)
    print("shape: ")
    print(scores.shape)
    print("---------------------")
    scores = tf.one_hot(scores, 10)

    print(references_plusplus)
    print(scores)

    print("---------------------")
    print(references_plusplus.shape)
    print(scores.shape)

    model = buildmodel(references_plusplus)
    opt = keras.optimizers.Adam(learning_rate=0.0005)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['mae', 'mse', 'accuracy'])
    print(model.summary())

    split_ratio = 1
    X_train, X_test = references_plusplus[:int(references_plusplus.shape[0] * split_ratio), :], references_plusplus[int(references_plusplus.shape[0] * split_ratio):, :]
    y_train, y_test = scores[:int(scores.shape[0] * split_ratio), :], scores[int(scores.shape[0] * split_ratio):, :]

    print("tests:")
    print(X_test)
    print(y_test)
    print("shape: ")
    print(y_test.shape)

    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)

    model.fit(X_train, y_train, epochs=500, batch_size=7, verbose=1, validation_split=0.2, shuffle=True)

    scorez = model.get_metrics_result()
    print(f"Test loss: {scorez['loss']}, Test accuracy: {scorez['accuracy'] * 100}")
    input()

    return model, reviews.corrwith(reviews.iloc[:, 0]).sort_values(ascending=False), scaler

def main():
    getModel('E:/PythonStuff/HotelProphet/ReviewData.csv')

if __name__ == '__main__':
    main()