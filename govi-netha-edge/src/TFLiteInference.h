#pragma once
/**
 * Wraps TensorFlow Lite Micro inference for the ESP32.
 * Loads the irrigation classifier model and runs predictions.
 *
 * Usage:
 *   TFLiteInference::init();                         // call once in setup()
 *   int state = TFLiteInference::predict(m, t, h);   // call each edge read
 *   // Returns: 0=OK, 1=IRRIGATE_SOON, 2=IRRIGATE_NOW
 */

#include <Arduino.h>
#include <TensorFlowLite_ESP32.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include "irrigation_model.h"

// Scaler parameters from training output
// IMPORTANT: Replace these with YOUR values printed by train_irrigation_model.py
static constexpr float MEAN_MOISTURE = 54.9904f;
static constexpr float MEAN_TEMPERATURE = 30.8749f;
static constexpr float MEAN_HUMIDITY = 64.2435f;
static constexpr float STD_MOISTURE = 26.2447f;
static constexpr float STD_TEMPERATURE = 6.3223f;
static constexpr float STD_HUMIDITY = 17.1322f;

// Tensor arena — scratch memory for TFLite Micro operations.
// 8KB is sufficient for this small 3-layer model.
static constexpr int TENSOR_ARENA_SIZE = 8 * 1024;
static uint8_t tensor_arena[TENSOR_ARENA_SIZE];

static const tflite::Model *tfl_model = nullptr;
static tflite::MicroInterpreter *tfl_interpreter = nullptr;
static TfLiteTensor *tfl_input = nullptr;
static TfLiteTensor *tfl_output = nullptr;
static tflite::MicroErrorReporter micro_error_reporter;

class TFLiteInference
{
public:
    static bool init()
    {
        Serial.println("[TFLITE] Initialising TFLite Micro...");

        tfl_model = tflite::GetModel(irrigation_model_tflite);
        if (tfl_model->version() != TFLITE_SCHEMA_VERSION)
        {
            Serial.println("[TFLITE] ERROR: Model schema version mismatch!");
            return false;
        }

        static tflite::AllOpsResolver resolver;
        static tflite::MicroInterpreter interpreter(
            tfl_model, resolver, tensor_arena, TENSOR_ARENA_SIZE, &micro_error_reporter);
        tfl_interpreter = &interpreter;

        if (tfl_interpreter->AllocateTensors() != kTfLiteOk)
        {
            Serial.println("[TFLITE] ERROR: AllocateTensors failed!");
            return false;
        }

        tfl_input = tfl_interpreter->input(0);
        tfl_output = tfl_interpreter->output(0);

        Serial.printf("[TFLITE] Ready. Model: %d bytes, Arena: %d bytes\n",
                      irrigation_model_tflite_len, TENSOR_ARENA_SIZE);
        return true;
    }

    /**
     * Run inference on the three sensor readings.
     * Returns: 0 = OK, 1 = IRRIGATE_SOON, 2 = IRRIGATE_NOW
     */
    static int predict(float moisture, float temp, float humidity)
    {
        if (!tfl_interpreter)
        {
            Serial.println("[TFLITE] Not initialised — returning rule-based fallback");
            return ruleFallback(moisture, temp, humidity);
        }

        // Normalise inputs using scaler parameters from training
        float scaled[3] = {
            (moisture - MEAN_MOISTURE) / STD_MOISTURE,
            (temp - MEAN_TEMPERATURE) / STD_TEMPERATURE,
            (humidity - MEAN_HUMIDITY) / STD_HUMIDITY,
        };

        // Write to input tensor (quantized int8 format)
        float input_scale = tfl_input->params.scale;
        int input_zero_point = tfl_input->params.zero_point;
        for (int i = 0; i < 3; i++)
        {
            tfl_input->data.int8[i] = (int8_t)(scaled[i] / input_scale + input_zero_point);
        }

        // Run inference
        if (tfl_interpreter->Invoke() != kTfLiteOk)
        {
            Serial.println("[TFLITE] ERROR: Invoke failed");
            return ruleFallback(moisture, temp, humidity);
        }

        // Decode output (find class with highest probability)
        float output_scale = tfl_output->params.scale;
        int output_zero_point = tfl_output->params.zero_point;
        float probs[3];
        for (int i = 0; i < 3; i++)
        {
            probs[i] = (tfl_output->data.int8[i] - output_zero_point) * output_scale;
        }

        int predicted_class = 0;
        float max_prob = probs[0];
        for (int i = 1; i < 3; i++)
        {
            if (probs[i] > max_prob)
            {
                max_prob = probs[i];
                predicted_class = i;
            }
        }

        Serial.printf("  [TFLITE] P(OK)=%.2f P(SOON)=%.2f P(NOW)=%.2f → Class %d\n",
                      probs[0], probs[1], probs[2], predicted_class);

        return predicted_class;
    }

private:
    // Rule-based fallback if TFLite fails for any reason
    static int ruleFallback(float moisture, float temp, float humidity)
    {
        if (moisture < 40.0f)
            return 2;
        if (moisture < 60.0f)
            return 1;
        return 0;
    }
};