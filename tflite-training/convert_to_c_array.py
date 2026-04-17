"""
Converts the .tflite binary file into a C byte array
that can be compiled directly into the ESP32 firmware.
"""

with open('irrigation_model.tflite', 'rb') as f:
    model_bytes = f.read()

# Format as a C array
hex_values = [f'0x{b:02x}' for b in model_bytes]

# Write 12 values per line for readability
lines = []
for i in range(0, len(hex_values), 12):
    lines.append('  ' + ', '.join(hex_values[i:i+12]) + ',')

c_array = "const unsigned char irrigation_model_tflite[] = {\n"
c_array += '\n'.join(lines)
c_array += f"\n}};\nconst unsigned int irrigation_model_tflite_len = {len(model_bytes)};\n"

with open('irrigation_model.h', 'w') as f:
    f.write("#pragma once\n\n")
    f.write(c_array)

print(f"Done. irrigation_model.h created ({len(model_bytes)} bytes = {len(model_bytes)/1024:.1f} KB)")
print("Copy irrigation_model.h to govi-netha-edge/src/")