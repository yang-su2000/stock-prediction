import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.utils import np_utils, normalize
from keras.layers import Dense, Conv1D, Flatten
from keras.activations import tanh
import tensorflow as tf
import glob

# python "scripts/pyspark_cnn_train.py"
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

path = 'data/data_processed_0412/'
all_files = glob.glob(path + "/*.csv")
li = []
for filename in all_files:
	df = pd.read_csv(filename, index_col=None, header=0, keep_default_na=False)
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

labels = train.values[:,-1].astype('float32')
labels2 = test.values[:,-1].astype('float32')
feature_list = [2,3,4,5,7,8,9,17,18]
hashtag_list = range(19,130)
feature_list.extend(hashtag_list)
X_train = train.values[:,feature_list].astype('float32') # change this when we add more features
X_test = test.values[:,feature_list].astype('float32')

y_train = np_utils.to_categorical(labels)
y_test = np_utils.to_categorical(labels2)

input_dim = X_train.shape[1]
input_dim_2 = X_test.shape[1]
nb_classes = y_train.shape[1]
X_train = X_train.reshape(-1, input_dim, 1)
X_test = X_test.reshape(-1, input_dim_2, 1)
assert not np.any(np.isnan(X_train))

model = Sequential()
model.add(Conv1D(64, 1, activation='relu', input_shape=(input_dim, 1)))
model.add(Conv1D(128, 1))
model.add(Conv1D(64, 1))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dense(nb_classes, activation='softmax'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
model.summary()

checkpoint_path = "stock_cnn/cp.ckpt"
# load weight after at least one epoch is trained to restore the trained model
# model.load_weights("stock_cnn/cp.ckpt")
cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=0)

print("Training...")
history = model.fit(X_train, y_train, validation_split=0.2, epochs=50, batch_size=128, callbacks=[cp_callback])
model.test_on_batch(X_test, y_test)
# print("Evaluating...")
# loss, accuracy = model.evaluate(X_test, y_test)
# print('Accuracy: %f' % (accuracy * 100))

# print("Generating test predictions...")
# preds = np.argmax(model.predict(X_test), axis=-1)

# def write_preds(preds, fname):
#     pd.DataFrame({"id": list(range(0,len(preds))), "label": preds}).to_csv(fname, index=False, header=True)

# write_preds(preds, "data/data_prediction/predict_cnn.csv")

from matplotlib import pyplot as plt
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['val', 'train'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['val', 'train'], loc='upper left')
plt.show()