import sys
import json
from collections import defaultdict, deque

def parse_args():
    args = sys.argv[1:]
    input_file = None
    output_file = None
    for arg in args:
        if arg.startswith('input1='):
            input_file = arg[7:]
        elif arg.startswith('output1='):
            output_file = arg[8:]
    if not input_file:
        input_file = 'output.json'
    if not output_file:
        output_file = 'output.txt'
    return input_file, output_file

def load_graph(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            graph = json.load(f)
            vertices = set(graph['vertices'])
            arcs = graph['arcs']
            return vertices, arcs
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: файл '{input_file}' имеет некорректный формат.")
        sys.exit(1)

def cycle(vertices, arcs):
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
    return has_cycle, sorted_vertices, adjacency_list

def find_root(vertices, arcs):
    outgoing = {arc['from'] for arc in arcs}
    incoming = {arc['to'] for arc in arcs}
    roots = incoming - outgoing
    if len(roots) != 1:
        print("Ошибка: граф должен иметь ровно одну корневую вершину.")
        sys.exit(1)
    return next(iter(roots))

def output(vertices, arcs):
    adjacency_list = defaultdict(list)
    for arc in arcs:
        from_vertex, to_vertex, order = arc['from'], arc['to'], arc['order']
        adjacency_list[to_vertex].append((from_vertex, order))
    for vertex in adjacency_list:
        adjacency_list[vertex].sort(key=lambda x: x[1])
    def build_subtree(vertex):
        if vertex not in adjacency_list or not adjacency_list[vertex]:
            return f"{vertex}()" 
        children = [build_subtree(child[0]) for child in adjacency_list[vertex]]
        return f"{vertex}({', '.join(children)})"
    root = find_root(vertices, arcs)
    return build_subtree(root)

def write_output(output_file, function_representation):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(function_representation)
    except IOError:
        print(f"Ошибка: не удалось записать файл '{output_file}'.")
        sys.exit(1)

def main():
    input_file, output_file = parse_args()
    vertices, arcs = load_graph(input_file)
    has_cycle, _, _ = cycle(vertices, arcs)
    if has_cycle:
        print("Ошибка: граф содержит циклы.")
        sys.exit(1)
    function_representation = output(vertices, arcs)
    write_output(output_file, function_representation)

if __name__ == '__main__':
    main()
