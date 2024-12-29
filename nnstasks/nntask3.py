import sys
import math
from collections import defaultdict, deque

def parse_args():
    args = sys.argv[1:]
    input_file1 = None
    input_file2 = None
    output_file = None
    for arg in args:
        if arg.startswith('input1='):
            input_file1 = arg[7:]
        elif arg.startswith('input2='):
            input_file2 = arg[7:]
        elif arg.startswith('output='):
            output_file = arg[7:]
    if not input_file1:
        input_file1 = 'input.txt'
    if not input_file2:
        input_file2 = 'operations.txt'
    if not output_file:
        output_file = 'output.txt'
    return input_file1, input_file2, output_file

def parse_graph(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.read().strip()
            arcs = []
            vertices = set()
            for item in lines.split('), ('):
                item = item.strip('()')
                a, b, n = item.split(', ')
                a, b, n = a.strip(), b.strip(), int(n)
                arcs.append({'from': a, 'to': b, 'order': n})
                vertices.add(a)
                vertices.add(b)
            return vertices, arcs
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
        sys.exit(1)
    except ValueError:
        print(f"Ошибка: неверный формат входного файла '{input_file}'.")
        sys.exit(1)

def load_operations(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            operations = {}
            lines = f.readlines()
            for line in lines[1:-1]: 
                line = line.strip()
                if ':' in line:  
                    key, value = map(str.strip, line.split(':', 1))
                    operations[key] = value
                else:
                    raise ValueError(f"Неверный формат строки: {line}")
            return operations
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

def detect_cycles(vertices, arcs):
    in_degree = {v: 0 for v in vertices}
    adjacency_list = defaultdict(list)
    for arc in arcs:
        from_vertex, to_vertex = arc['from'], arc['to']
        adjacency_list[from_vertex].append(to_vertex)
        in_degree[to_vertex] += 1
    queue = deque([v for v in vertices if in_degree[v] == 0])
    sorted_vertices = []
    while queue:
        vertex = queue.popleft()
        sorted_vertices.append(vertex)
        for neighbor in adjacency_list[vertex]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    has_cycle = len(sorted_vertices) != len(vertices)
    return has_cycle, sorted_vertices

def find_sink(vertices, arcs):
    outgoing = {arc['from'] for arc in arcs}
    sink_candidates = vertices - outgoing
    if len(sink_candidates) != 1:
        print("Ошибка: граф должен иметь ровно одну стоковую вершину.")
        sys.exit(1)
    return next(iter(sink_candidates))

def evaluate_function(vertices, arcs, operations):
    adjacency_list = defaultdict(list)
    for arc in arcs:
        from_vertex, to_vertex, order = arc['from'], arc['to'], arc['order']
        adjacency_list[to_vertex].append((from_vertex, order))
    for vertex in adjacency_list:
        adjacency_list[vertex].sort(key=lambda x: x[1])
    computed_values = {}
    def evaluate(vertex):
        if vertex in computed_values:
            return computed_values[vertex]
        if vertex not in adjacency_list or not adjacency_list[vertex]:
            operation = operations.get(vertex, None)
            if operation is None:
                print(f"Ошибка: операция для вершины '{vertex}' не найдена.")
                sys.exit(1)
            try:
                value = float(operation) if operation.replace('.', '', 1).isdigit() else None
                computed_values[vertex] = value
                return value
            except ValueError:
                print(f"Ошибка: некорректная операция '{operation}' для вершины '{vertex}'.")
                sys.exit(1)

        children_values = [evaluate(child[0]) for child in adjacency_list[vertex]]
        if None in children_values:
            print(f"Ошибка: не удалось вычислить значение для вершины '{vertex}'.")
            sys.exit(1)

        operation = operations.get(vertex, None)
        if operation is None:
            print(f"Ошибка: операция для вершины '{vertex}' не найдена.")
            sys.exit(1)
        try:
            if operation == '+':
                result = sum(children_values)
            elif operation == '*':
                result = math.prod(children_values)
            elif operation == 'exp':
                if len(children_values) != 1:
                    print(f"Ошибка: операция 'exp' ожидает ровно одно входное значение для вершины '{vertex}'.")
                    sys.exit(1)
                result = math.exp(children_values[0])
            else:
                result = float(operation)
            computed_values[vertex] = result
            return result
        except Exception as e:
            print(f"Ошибка: некорректная операция '{operation}' для вершины '{vertex}': {e}")
            sys.exit(1)

    root = find_sink(vertices, arcs)
    return evaluate(root)

def write_output(output_file, result):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(result))
    except IOError:
        print(f"Ошибка: не удалось записать файл '{output_file}'.")
        sys.exit(1)

def main():
    input_file1, input_file2, output_file = parse_args()
    vertices, arcs = parse_graph(input_file1)
    operations = load_operations(input_file2)
    has_cycle, _ = detect_cycles(vertices, arcs)
    if has_cycle:
        print("Ошибка: граф содержит циклы.")
        sys.exit(1)
    result = evaluate_function(vertices, arcs, operations)
    write_output(output_file, result)
    print(f"Результат сохранён в '{output_file}'")

if __name__ == '__main__':
    main()