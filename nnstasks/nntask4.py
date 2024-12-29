import numpy as np
import json
import sys

def parse_args():
    args = sys.argv[1:]
    input_file1 = None
    input_file2 = None
    output_file1 = None
    output_file2 = None
    for arg in args:
        if arg.startswith('input1='):
            input_file1 = arg[7:]
        elif arg.startswith('input2='):
            input_file2 = arg[7:]
        elif arg.startswith('output1='):
            output_file1 = arg[8:]
        elif arg.startswith('output2='):
            output_file2 = arg[8:]
    if not input_file1:
        input_file1 = 'input1.txt'
    if not input_file2:
        input_file2 = 'input2.txt'
    if not output_file1:
        output_file1 = 'output_vector.txt'
    if not output_file2:
        output_file2 = 'neural_network.json'
    return input_file1, input_file2, output_file1, output_file2

def read_matrices(file_path):
    matrices = []
    try:
        with open(file_path, 'r') as file:
            data = file.read().split("\n")
            for line in data:
                if line.strip():
                    matrix = eval(line.split(":")[1].strip())
                    matrices.append(np.array(matrix))
    except Exception as e:
        raise ValueError(f"Ошибка при чтении матриц: {e}")
    return matrices

def read_input_vector(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
            vector = np.array([float(x) for x in data.split(",")])
    except Exception as e:
        raise ValueError(f"Ошибка при чтении входного вектора: {e}")
    return vector

def network(matrices, input_vector):
    activations = [input_vector]
    for i, matrix in enumerate(matrices):
        if activations[-1].shape[0] != matrix.shape[1]:
            raise ValueError(
                f"Несоответствие размеров: матрица {i+1} ожидает вход {matrix.shape[1]}, а получила {activations[-1].shape[0]}"
            )
        z = np.dot(matrix, activations[-1])
        a = 1 / (1 + np.exp(-z))  
        activations.append(a)
    return activations

def serialize_to_json(matrices, output_file):
    net_data = {"NeuralNetwork": []}
    for i, matrix in enumerate(matrices):
        layer_data = {
            "LayerIndex": i + 1,
            "Weights": matrix.tolist()
        }
        net_data["NeuralNetwork"].append(layer_data)
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(net_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Ошибка при записи JSON: {e}")

def write_output_vector(vector, output_file):
    try:
        with open(output_file, 'w') as file:
            file.write(", ".join(map(str, vector)))
    except Exception as e:
        raise ValueError(f"Ошибка при записи выходного вектора: {e}")

if __name__ == "__main__":
    weight_file, input_file, output_vector_file, output_json = parse_args()
    try:
        matrices = read_matrices(weight_file)
        input_vector = read_input_vector(input_file)
        activations = network(matrices, input_vector)
        serialize_to_json(matrices, output_json)
        write_output_vector(activations[-1], output_vector_file)
        print(f"Результаты сохранены в файлы: {output_json}, {output_vector_file}")

    except ValueError as e:
        print(f"Ошибка: {e}")