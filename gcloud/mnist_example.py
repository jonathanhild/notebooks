
import tensorflow as tf

(x_train, y_train), (_, _) = tf.keras.datasets.mnist.load_data()

x_train = x_train.reshape((60000, 28 * 28))
x_train = x_train.astype('float32') / 255

model = tf.keras.Sequential([
    tf.keras.layers.Dense(512, activation='relu', input_shape=(28 * 28,)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(loss='sparse_categorical_crossentropy',
              optimizer=tf.keras.optimizers.Adam(),
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=10, batch_size=128)
