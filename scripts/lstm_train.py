import numpy as np
import pandas as pd
import tensorflow as tf
from keras.utils import np_utils
from tensorflow import keras
from tensorflow.keras import layers
from keras.layers import Dense, Conv1D, Flatten
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
import glob

# python "scripts/pyspark_lstm_train.py"
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

path = 'data/data_processed_0412/'
all_files = glob.glob(path + "/*.csv")
li = []
for filename in all_files:
	df = pd.read_csv(filename, index_col=None, header=0)
	li.append(df)
all = pd.concat(li, axis=0, ignore_index=True)

train = None
test = None
split_randomly = True
if split_randomly:
    train = all.sample(frac = 0.7, random_state = 200)
    test = all.drop(train.index)
else:
    train = all.iloc[:5000,:]
    test = all.iloc[5001:,:]

vocab_size = 500
max_length = 50
feature_list = [2,3,4,5,7,8,9,17,18]
feature_list.extend(range(19,130))
meta_shape = len(feature_list)

labels = train.values[:,-1]
X_train = train.values[:,16]
X_train2 = train.values[:,feature_list].astype('float32')
encoded_docs = [one_hot(d, vocab_size) for d in X_train]
padded_docs = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
y_train = np_utils.to_categorical(labels)
nb_classes = y_train.shape[1]

labels2 = test.values[:,-1]
X_test = test.values[:,16]
X_test2 = test.values[:,feature_list].astype('float32')
encoded_docs2 = [one_hot(d, vocab_size) for d in X_test]
padded_docs2 = pad_sequences(encoded_docs2, maxlen=max_length, padding='post')
y_test = np_utils.to_categorical(labels2)

nlp_input = keras.Input(shape=(max_length,), name='nlp_input')
meta_input = keras.Input(shape=(meta_shape,), name='meta_input')
emb = layers.Embedding(output_dim=64, input_dim=vocab_size, input_length=max_length)(nlp_input)
nlp_out = layers.GRU(64, return_sequences=True)(emb)
nlp_out = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(nlp_out)
nlp_out = layers.Bidirectional(layers.LSTM(64))(nlp_out)
x = tf.concat([nlp_out, meta_input], axis=1)
x = layers.Dense(32, activation='relu')(x)
x = layers.Dense(nb_classes, activation='softmax')(x)
model = keras.Model(inputs=[nlp_input, meta_input], outputs=[x])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
model.summary()

checkpoint_path = "stock_lstm/cp.ckpt"
# load weight after at least one epoch is trained to restore the trained model
# model.load_weights("stock_lstm/cp.ckpt")
cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=0)

print("Training...")
history = model.fit([padded_docs, X_train2], y_train, validation_split=0.2, epochs=10, batch_size=128, callbacks=[cp_callback])
model.test_on_batch([padded_docs2, X_test2], y_test)

print("Generating test predictions...")
preds = np.argmax(model.predict([padded_docs2, X_test2]), axis=-1)

def write_preds(preds, fname):
    pd.DataFrame({"id": list(range(0,len(preds))), "label": preds}).to_csv(fname, index=False, header=True)

write_preds(preds, "data/data_prediction/predict_lstm.csv")

from matplotlib import pyplot as plt
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()