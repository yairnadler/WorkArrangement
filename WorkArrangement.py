from collections import defaultdict, deque

# MaxFlow Implementation
class MaxFlow:
    def __init__(self, graph):
        self.graph = graph
        self.residual_graph = defaultdict(dict)
        for u in graph:
            for v in graph[u]:
                self.residual_graph[u][v] = graph[u][v]
                self.residual_graph[v][u] = 0

    def bfs(self, source, sink, parent):
        visited = set()
        queue = deque([source])
        visited.add(source)

        while queue:
            u = queue.popleft()
            for v in self.residual_graph[u]:
                if v not in visited and self.residual_graph[u][v] > 0:
                    queue.append(v)
                    visited.add(v)
                    parent[v] = u
                    if v == sink:
                        return True
        return False

    def edmonds_karp(self, source, sink):
        parent = {}
        max_flow = 0

        while self.bfs(source, sink, parent):
            path_flow = float('Inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, self.residual_graph[parent[s]][s])
                s = parent[s]

            max_flow += path_flow
            v = sink
            while v != source:
                u = parent[v]
                self.residual_graph[u][v] -= path_flow
                self.residual_graph[v][u] += path_flow
                v = parent[v]

        return max_flow

# Generate all shifts for the week
def generate_weekly_shifts():
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    shift_types = ["day", "night"]

    shifts = []
    shift_id = 1
    for day in days_of_week:
        for shift_type in shift_types:
            shifts.append({
                "id": f"Shift{shift_id}",
                "day": day,
                "type": shift_type
            })
            shift_id += 1
    
    return shifts

# Build the flow network graph
def build_graph(employees, shifts):
    graph = defaultdict(dict)

    for employee in employees:
        graph['S'][employee['name']] = employee['max_shifts']
        for shift in shifts:
            if shift['day'] not in employee['unavailability'] or shift['type'] not in employee['unavailability'].get(shift['day'], []):
                graph[employee['name']][shift['id']] = 1

    for shift in shifts:
        graph[shift['id']]['T'] = 1

    return graph

def violates_rules(assignments, employee_name, new_shift):
    employee = next(emp for emp in employees if emp['name'] == employee_name)
    
    # Check unavailability
    if new_shift['day'] in employee['unavailability'] and new_shift['type'] in employee['unavailability'].get(new_shift['day'], []):
        return True
    
    # Check overlap
    if any(shift['day'] == new_shift['day'] for shift in assignments[employee_name]):
        return True
    
    # Check night shift limit
    night_shifts = sum(1 for shift in assignments[employee_name] if shift['type'] == 'night')
    if new_shift['type'] == 'night' and night_shifts >= 3:
        return True
    
    # Check consecutive shifts
    assigned_shifts = sorted(assignments[employee_name] + [new_shift], key=lambda x: shifts.index(x))
    for i in range(len(assigned_shifts) - 2):
        if all(shift['type'] == 'night' for shift in assigned_shifts[i:i+3]) or \
           all(shift['type'] == 'day' for shift in assigned_shifts[i:i+3]):
            return True
    
    return False

# Example Employees
employees = [
    {"name": "Alice", "unavailability": {"Thursday": ["day", "night"], "Sunday": ["day", "night"]}, "max_shifts": 4},
    {"name": "Bob", "unavailability": {"Monday": ["day", "night"], "Friday": ["day", "night"], "Sunday": ["day", "night"]}, "max_shifts": 3},
    {"name": "Charlie", "unavailability": {"Tuesday": ["day", "night"], "Wednesday": ["day", "night"], "Friday": ["day", "night"], "Saturday": ["day", "night"]}, "max_shifts": 2},
    {"name": "Diana", "unavailability": {"Monday": ["day", "night"], "Wednesday": ["day", "night"], "Thursday": ["day", "night"], "Saturday": ["day", "night"]}, "max_shifts": 4},
    {"name": "Eve", "unavailability": {"Wednesday": ["day", "night"], "Friday": ["day", "night"], "Saturday": ["day", "night"], "Sunday": ["day"]}, "max_shifts": 3},
]

# Generate weekly shifts
shifts = generate_weekly_shifts()

# Build the graph
graph = build_graph(employees, shifts)

# Apply the max-flow algorithm
max_flow_solver = MaxFlow(graph)
max_flow = max_flow_solver.edmonds_karp('S', 'T')
print(f"Max Flow (Total Assignments): {max_flow}")

# Initialize assignments
assignments = defaultdict(list)

# Function to find the best employee for a shift
def find_best_employee(shift):
    available_employees = [
        emp for emp in employees 
        if len(assignments[emp['name']]) < emp['max_shifts'] and not violates_rules(assignments, emp['name'], shift)
    ]
    if available_employees:
        return min(available_employees, key=lambda x: len(assignments[x['name']]))
    return None

# Assign shifts
for shift in shifts:
    best_employee = find_best_employee(shift)
    if best_employee:
        assignments[best_employee['name']].append(shift)
    else:
        print(f"Warning: Could not assign {shift['day']} {shift['type']} shift")

# Print the final assignments
print("\nAssignments:")
for emp, assigned_shifts in assignments.items():
    shift_details = [(shift['day'], shift['type']) for shift in assigned_shifts]
    print(f"{emp}: {shift_details}")

# Print unassigned shifts
unassigned = [shift for shift in shifts if all(shift not in assignments[emp['name']] for emp in employees)]
if unassigned:
    print("\nUnassigned shifts:")
    for shift in unassigned:
        print(f"{shift['day']} {shift['type']}")
else:
    print("\nAll shifts assigned successfully!")