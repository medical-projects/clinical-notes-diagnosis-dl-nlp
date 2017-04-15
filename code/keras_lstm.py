from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np
import pandas as pd

from keras.preprocessing.sequence import pad_sequences
import cPickle


if __name__ == "__main__":
    f = open('./data/preprocessing_data.p', 'rb')
    loaded_data = []
    for i in range(5): # [reverse_dictionary, train_sequence, test_sequence, train_label, test_label]:
        loaded_data.append(cPickle.load(f))
    f.close()

    dictionary = loaded_data[0]
    train_sequence = loaded_data[1]
    test_sequence = loaded_data[2]
    train_label = loaded_data[3]
    test_label = loaded_data[4]

    max_sequence_length = 20
    train_sequence = pad_sequences(train_sequence, maxlen=max_sequence_length)
    test_sequence = pad_sequences(test_sequence, maxlen=max_sequence_length)
    f = open('./data/embedding_matrix.p')
    embedding_matrix = cPickle.load(f)
    f.close

    embedding_size = embedding_matrix.shape[1]

    #LSTM with embedding trainable
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Embedding, BatchNormalization
    from keras.layers import LSTM

    vocabulary_size = len(dictionary) + 1
    embedding_dim = embedding_matrix.shape[1]
    category_number = train_label.shape[1]

    print('Build model...')
    model = Sequential()
    model.add(Embedding(vocabulary_size,
                        embedding_dim,
                        weights=[embedding_matrix],
                        input_length=max_sequence_length,
                        trainable=True,
                        input_shape=train_sequence.shape[1:]))

    # from keras import backend as K
    # get_embedding_output = K.function([model.layers[0].input],
    #                                   [model.layers[0].output])

    # get_embedding_output
    model.add(LSTM(256))
    model.add(Dropout(0.5))
    model.add(BatchNormalization())
    model.add(Dense(category_number, activation='sigmoid'))

    model.compile(loss='mse', optimizer='rmsprop', metrics=['mse'])
    model.summary()
    model.fit(train_sequence, train_label, validation_split= 0.2, epochs=2, batch_size=64)

    predict_label = model.predict(test_sequence)
    predict_sum = np.sum(predict_label, axis=1)
    print(predict_sum[:10])
    scores = model.evaluate(test_sequence, test_label, verbose=0)
    print("Accuracy: %.2f%%" % (scores[1]*100))



