"""
Govi Netha — TFLite Micro Irrigation Classifier Training
Trains a small neural network to classify irrigation urgency.
Converts to TFLite with full integer quantization for ESP32.

Inputs:  [moisture_pct, temperature_c, humidity_pct]
Outputs: [prob_ok, prob_irrigate_soon, prob_irrigate_now]
"""

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle

np.random.seed(42)
tf.random.set_seed(42)

# Generate training data
# Simulates real paddy field conditions for southern Sri Lanka.
# Labels: 0=OK, 1=IRRIGATE_SOON, 2=IRRIGATE_NOW

N = 3000
moisture    = np.random.uniform(10, 100, N)
temperature = np.random.uniform(20, 42,  N)
humidity    = np.random.uniform(35, 95,  N)

labels = np.zeros(N, dtype=np.int32)

# IRRIGATE_NOW (class 2) conditions
now_mask = (
    (moisture < 40) |
    ((moisture < 55) & (temperature > 36)) |
    ((moisture < 45) & (humidity < 45))
)
labels[now_mask] = 2

# IRRIGATE_SOON (class 1) conditions — not already class 2
soon_mask = (
    (~now_mask) & (
        (moisture < 60) |
        ((moisture < 70) & (temperature > 33)) |
        ((moisture < 65) & (humidity < 55))
    )
)
labels[soon_mask] = 1

X = np.column_stack([moisture, temperature, humidity]).astype(np.float32)
y = labels

print(f"Training data: {N} samples")
print(f"  Class 0 (OK):             {np.sum(y==0)} samples ({np.sum(y==0)/N*100:.0f}%)")
print(f"  Class 1 (IRRIGATE_SOON):  {np.sum(y==1)} samples ({np.sum(y==1)/N*100:.0f}%)")
print(f"  Class 2 (IRRIGATE_NOW):   {np.sum(y==2)} samples ({np.sum(y==2)/N*100:.0f}%)")

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Build model
# Kept deliberately small to fit in ESP32 RAM.
# 3 inputs → 16 neurons → 8 neurons → 3 outputs
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(3,)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(8,  activation='relu'),
    tf.keras.layers.Dense(3,  activation='softmax'),
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Train
history = model.fit(
    X_train, y_train,
    epochs=80,
    batch_size=32,
    validation_split=0.1,
    verbose=1
)

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\nTest accuracy: {test_acc*100:.1f}%")
print("Target: >95%")

# Save scaler parameters
# We need these to normalise inputs on the ESP32
print("\nScaler parameters (copy these into model_data.h):")
print(f"  mean_moisture    = {scaler.mean_[0]:.4f}")
print(f"  mean_temperature = {scaler.mean_[1]:.4f}")
print(f"  mean_humidity    = {scaler.mean_[2]:.4f}")
print(f"  std_moisture     = {scaler.scale_[0]:.4f}")
print(f"  std_temperature  = {scaler.scale_[1]:.4f}")
print(f"  std_humidity     = {scaler.scale_[2]:.4f}")

# Convert to TFLite with full integer quantization
# This shrinks the model and makes it ESP32-compatible.

def representative_dataset():
    for i in range(200):
        sample = X_train[i:i+1].astype(np.float32)
        yield [sample]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type  = tf.int8
converter.inference_output_type = tf.int8

tflite_model = converter.convert()

with open('irrigation_model.tflite', 'wb') as f:
    f.write(tflite_model)

size_kb = len(tflite_model) / 1024
print(f"\nTFLite model saved: irrigation_model.tflite ({size_kb:.1f} KB)")
print("Target: < 10 KB to fit comfortably in ESP32 RAM")
print("\nNext step: run convert_to_c_array.py")