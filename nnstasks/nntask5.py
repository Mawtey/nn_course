import argparse
import sys
import numpy as np
import re
from math import exp

def sigmoid(x):
    return 1 / (1 + exp(-x))

def forward_pass(layers, inputs):
    for idx, layer in enumerate(layers):
        layer['inputs'] = inputs if idx == 0 else layers[idx - 1]['outputs']
        for i in range(layer['neurons']):
            weighted_sum = sum(layer['weights'][i][j] * layer['inputs'][j] for j in range(layer['inputs_count']))
            layer['outputs'][i] = sigmoid(weighted_sum)
            layer['derivatives'][i] = layer['outputs'][i] * (1 - layer['outputs'][i])
    return layers[-1]['outputs']

def backward_pass(layers, expected):
    total_error = 0
    deltas = [np.zeros(layer['neurons']) for layer in layers]
    last_layer = layers[-1]
    for i in range(len(expected)):
        error = last_layer['outputs'][i] - expected[i]
        deltas[-1][i] = error * last_layer['derivatives'][i]
        total_error += error ** 2 / 2
    for idx in range(len(layers) - 1, 0, -1):
        current_layer = layers[idx]
        for i in range(layers[idx - 1]['neurons']):
            deltas[idx - 1][i] = sum(current_layer['weights'][j][i] * deltas[idx][j] for j in range(current_layer['neurons'])) * layers[idx - 1]['derivatives'][i]
    return total_error, deltas

def update_weights(layers, deltas, learning_rate):
    for layer, delta in zip(layers, deltas):
        for i in range(layer['neurons']):
            for j in range(layer['inputs_count']):
                layer['weights'][i][j] -= learning_rate * delta[i] * layer['inputs'][j]

def train(layers, inputs, outputs, max_epochs, learning_rate, error_threshold):
    history = []
    for epoch in range(max_epochs):
        total_error = 0
        for x, y in zip(inputs, outputs):
            forward_pass(layers, x)
            error, deltas = backward_pass(layers, y)
            total_error += error
            update_weights(layers, deltas, learning_rate)
        mean_error = total_error / len(inputs)
        history.append(mean_error)
        if mean_error <= error_threshold:
            break
    for i in range(len(inputs)):
        print(f'Вход: {inputs[i]}, Ожидаемое значение: {outputs[i]}, Выход: {forward_pass(layers, inputs[i])}')
    return history

def load_matrix_file(filename):
    matrices = {}
    try:
        with open(filename, 'r') as file:
            data = file.read()
        matches = re.findall(r"(\S+)\s*:\s*\[\[(.*?)\]\]", data, re.DOTALL)
        for name, matrix_str in matches:
            matrix_str = matrix_str.replace(" ", "").strip(',')
            rows = matrix_str.split('],[')
            try:
                matrix_data = [list(map(float, row.strip('[]').split(','))) for row in rows]
                matrices[name] = np.array(matrix_data)
            except ValueError as e:
                print(f"Ошибка при обработке матрицы {name}: {matrix_str}. Детали: {e}")
                sys.exit(1)
    except FileNotFoundError:
        print(f"Ошибка, файл не найден: {filename}")
        sys.exit(1)
    except Exception as e:
         print(f"Ошибки при считывании матрицы с файла '{filename}': {e}")
         sys.exit(1)
    return matrices

def load_parameters_file(filename):
    try:
        with open(filename, 'r') as file:
            params = {}
            for line in file:
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    try:
                        params[key] = float(value) if '.' in value else int(value)
                    except ValueError:
                         print(f"Ошибка, неверный формат параметра в файле '{filename}'. Параметр '{key}' имеет значение '{value}'")
                         sys.exit(1)
                else:
                    print(f"Ошибка, неверный формат параметра с файла '{filename}': {line.strip()}")
                    sys.exit(1)
            return params
    except FileNotFoundError:
        print(f"Ошибка, файл не найден: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Не удалось считать параметр с файла '{filename}': {e}")
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Neural Network Training Script")
    parser.add_argument('params', nargs='+', type=lambda param: param.split('='))
    try:
        args = parser.parse_args()
        return {param [0] : param[1] for param in args.params}
    except SystemExit:
         sys.exit(1)

def main():
    args = parse_arguments()
    if not args:
      sys.exit(1)
    if not all(key in args for key in ['input1', 'input2', 'input3', 'output1']):
        print("Error: Missing parameters. Please provide input1, input2, input3, and output1.")
        sys.exit(1)
    weights_file = args['input1']
    data_file = args['input2']
    params_file = args['input3']
    output_file = args['output1']
    try:
       weights = load_matrix_file(weights_file)
       layers = [{'weights': w, 'neurons': w.shape[0], 'inputs_count': w.shape[1], 'inputs': np.zeros(w.shape[1]), 'outputs': np.zeros(w.shape[0]), 'derivatives': np.zeros(w.shape[0])} for w in weights.values()]

       data = load_matrix_file(data_file)
       inputs, outputs = data['x'], data['y']
    except Exception as e:
       print(f"Не удалось считать данные : {e}")
       sys.exit(1)
    if len(inputs) != len(outputs):
        print("Размерность x и y не совпадает.")
        sys.exit(1)
    try:
       params = load_parameters_file(params_file)
    except Exception as e:
        print(f"Не удалось считать параметры: {e}")
        sys.exit(1)
    try:
      history = train(layers, inputs, outputs, params['epoch'], params['alpha'], params['eps'])
    except Exception as e:
      print(f"Ошибка во время обучения: {e}")
      sys.exit(1)
    try:
        with open(output_file, 'w') as file:
            file.write("\n".join(map(str, history)))
        print(f"Результат сохранен в файл {output_file}")
    except Exception as e:
      print(f"Не удалось записать вывод в '{output_file}': {e}")
      sys.exit(1)

if __name__ == "__main__":
    main()
