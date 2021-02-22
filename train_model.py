"""
A lot of this is inspired by the concise and simple article found here:
https://towardsdatascience.com/generating-pok%C3%A9mon-names-using-rnns-f41003143333
"""

# All the modelling stuff
from keras.callbacks import LambdaCallback
from keras.layers import Dense, LSTM
from keras import Sequential
import numpy as np

# This can be changed to names, greek or latin with the current setup
from generate_data import names as corpus

# Use regex to capitalize roman numerals
import re


def one_hot_encode_dict(text_list: list) -> (dict, dict):
    """
    Takes a list of strings and outputs a dictionary to one hot encode that set for
    the upcoming RNN

    :param text_list: list, a list of strings for one-hot-encoding
    :return: tuple, two dictionaries to perform one-hot-encoding and decoding
    """
    # form the set of all characters in the corpus
    s = set()
    for text in text_list:
        s |= set(text)

    # make the one-hot-encoding
    encoder = {char: i for i, char in enumerate(s)}
    decoder = {encoder[key]: key for key in encoder}
    return encoder, decoder


def encode_corpus(text_list: list) -> (np.array, np.array, dict, dict):
    """
    Take a corpus, create a one-hot-encoding and spit out inputs X, outputs Y,
    and both encoding and decoding dictionaries

    :param text_list: list, the corpus
    :return: (np.array, np.array, dict, dict),
    """
    # For one hot encoding
    encoder, decoder = one_hot_encode_dict(text_list)

    # init inputs X and outputs Y
    X = np.zeros((m, max_char, len(encoder)))
    Y = np.zeros((m, max_char, len(decoder)))

    # Convert corpus into sequential information
    for i in range(m):
        text = list(text_list[i])
        for j in range(len(text)):
            X[i, j, encoder[text[j]]] = 1
            if j < len(text) - 1:
                Y[i, j, encoder[text[j+1]]] = 1

    return X, Y, encoder, decoder


# Some variables we need to be global
m = len(corpus)
max_char = len(max(corpus, key=len))
X, Y, char_to_index, index_to_char = encode_corpus(corpus)
char_dim = len(char_to_index)

### SOMETHING IS JANKY
### THE BELOW CODE JUST CHECKS INPUTS AND OUTPUTS ARE ENCODED AS EXPECTED
# for i in range(m):
#     for j in range(len(X[i,:,0])):
#         print(index_to_char[max(enumerate(X[i,j,:]), key=lambda x:x[1])[0]], end='')
#         if j > 0:
#             print(index_to_char[max(enumerate(Y[i, j-1, :]), key=lambda x: x[1])[0]], end='')
#     print()
#
# print("magic character is: ", index_to_char[0])

# Define model
model = Sequential()
model.add(LSTM(64, input_shape=(max_char, char_dim), return_sequences=True, recurrent_dropout=0.25))
model.add(LSTM(64, input_shape=(max_char, char_dim), return_sequences=True, recurrent_dropout=0.25))
model.add(Dense(char_dim, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')


def make_name(mdl, prompt: str = '') -> str:
    """
    Takes a model mdl and a prompt (default is empty) and returns text generated by the model

    :param mdl: keras.Sequential(), a ML model
    :param prompt: str, a string to prompt the RNN
    :return: str, a string generated by the RNN
    """
    generated_text = []
    x = np.zeros((1, max_char, char_dim))
    end = False
    i = 0

    for char in prompt:
        x[0, i + 1, char_to_index[char]] = 1
        generated_text.append(char)
        i += 1

    while end == False:
        probs = list(mdl.predict(x)[0, i])
        probs = probs / np.sum(probs)
        index = np.random.choice(range(char_dim), p=probs)
        if i == max_char - 2:
            character = '.'
            end = True
        else:
            character = index_to_char[index]
        generated_text.append(character)
        x[0, i + 1, index] = 1
        i += 1
        if character == '.':
            end = True

    print(''.join(generated_text).title())



def generate_name_loop(epoch, _):
    if epoch % 100 == 0:

        print(f'Text generated after epoch {epoch}:')

        for i in range(3):
            make_name(model)

        print()

def generate_loss(epoch, _):
    if epoch % 100 == 0:
        model.fit(X, Y)
        print()


name_generator = LambdaCallback(on_epoch_end=generate_name_loop)
loss = LambdaCallback(on_epoch_end=generate_loss)

if __name__ == "__main__":

    # train model
    model.fit(X, Y, batch_size=64, epochs=6000, callbacks=[name_generator, loss], verbose=0)

    # Save model
    model.save('ByzantineRNN')
