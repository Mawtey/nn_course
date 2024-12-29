import sys
import json
from collections import OrderedDict, defaultdict

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
        input_file1 = 'input.txt'
    if not output_file1:
        output_file1 = 'output.json'
    return input_file1, input_file2, output_file1, output_file2

def read_input_file(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            return lines
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
        sys.exit(1)

def parse_graph(lines):
    graph = {
        'vertices': OrderedDict(), 
        'arcs': []
    }
    seen_arcs = set()
    incoming_orders = defaultdict(set)
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            arcs_str = line.split('), (')
            for arc_str in arcs_str:
                arc_str = arc_str.strip('()')
                a, b, n = arc_str.split(', ')
                a = a.strip()
                b = b.strip()
                n = int(n.strip())
                arc_key = (a, b)
                if arc_key in seen_arcs:
                    print(f"Ошибка: повторяющаяся дуга ({a}, {b}, {n}) на строке {i+1}.")
                    sys.exit(1)
                seen_arcs.add(arc_key)
                if n in incoming_orders[b]:
                    print(f"Ошибка: в вершину '{b}' входит несколько дуг с порядком {n} на строке {i+1}.")
                    sys.exit(1)
                incoming_orders[b].add(n)
                if a not in graph['vertices']:
                    graph['vertices'][a] = True  
                if b not in graph['vertices']:
                    graph['vertices'][b] = True
                graph['arcs'].append({'from': a, 'to': b, 'order': n})
        except ValueError:
            print(f"Ошибка: неверный формат строки {i+1}: '{line}'")
            sys.exit(1)
    return graph

def write_json(graph, output_file):
    graph['arcs'] = sorted(graph['arcs'], key=lambda arc: arc['order'])
    graph_json = {
        'vertices': list(graph['vertices'].keys()),
        'arcs': graph['arcs']
    }
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_json, f, ensure_ascii=False, indent=4)
    except IOError:
        print(f"Ошибка: не удалось записать файл '{output_file}'.")
        sys.exit(1)

def main():
    input_file1, input_file2, output_file1, output_file2 = parse_args()
    lines = read_input_file(input_file1)
    graph = parse_graph(lines)
    write_json(graph, output_file1)

if __name__ == '__main__':
    main()
