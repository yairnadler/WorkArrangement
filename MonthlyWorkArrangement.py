from collections import defaultdict, deque
import calendar
from datetime import datetime, timedelta

# MaxFlow Implementation (unchanged)
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

# Generate all shifts for the month
def generate_monthly_shifts(year, month):
    _, days_in_month = calendar.monthrange(year, month)
    shifts = []
    shift_id = 1
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day)
        for shift_type in ["day", "night"]:
            shifts.append({
                "id": f"Shift{shift_id}",
                "date": date,
                "day": date.strftime("%A"),
                "type": shift_type
            })
            shift_id += 1
    return shifts

# Build the flow network graph
def build_graph(employees, shifts):
    graph = defaultdict(dict)

    for employee in employees:
        graph['S'][employee['name']] = employee['max_shifts_per_week'] * 4  # Assuming 4 weeks in a month
        for shift in shifts:
            if shift['date'] not in employee['unavailability'] or shift['type'] not in employee['unavailability'].get(shift['date'], []):
                graph[employee['name']][shift['id']] = 1

    for shift in shifts:
        graph[shift['id']]['T'] = 1

    return graph

def violates_rules(assignments, employee_name, new_shift):
    employee = next(emp for emp in employees if emp['name'] == employee_name)
    
    # Check unavailability
    if new_shift['date'] in employee['unavailability'] and new_shift['type'] in employee['unavailability'].get(new_shift['date'], []):
        return True
    
    # Check overlap
    if any(shift['date'] == new_shift['date'] for shift in assignments[employee_name]):
        return True
    
    # Check night shift limit (per week)
    week_start = new_shift['date'] - timedelta(days=new_shift['date'].weekday())
    week_end = week_start + timedelta(days=6)
    week_shifts = [shift for shift in assignments[employee_name] + [new_shift] if week_start <= shift['date'] <= week_end]
    night_shifts = sum(1 for shift in week_shifts if shift['type'] == 'night')
    if night_shifts > 3:
        return True
    
    # Check consecutive shifts
    assigned_shifts = sorted(assignments[employee_name] + [new_shift], key=lambda x: x['date'])
    for i in range(len(assigned_shifts) - 2):
        if all(shift['type'] == 'night' for shift in assigned_shifts[i:i+3]) or \
           all(shift['type'] == 'day' for shift in assigned_shifts[i:i+3]):
            return True
    
    return False

# Example Employees
employees = [
    {
        "name": "Wetzler",
        "unavailability": {

        },
        "max_shifts_per_week": 4,
        "min_shifts_per_month": 15
    },
    {
        "name": "Berko",
        "unavailability": {
            datetime(2024, 9, 1): ["day"],
            datetime(2024, 9, 2): ["day", "night"],
            datetime(2024, 9, 3): ["day", "night"],
            datetime(2024, 9, 4): ["day", "night"],
            datetime(2024, 9, 5): ["night"],
            datetime(2024, 9, 6): ["day", "night"],
            datetime(2024, 9, 7): ["day"],
            datetime(2024, 9, 8): ["day", "night"],
            datetime(2024, 9, 9): ["day", "night"],
            datetime(2024, 9, 10): ["day", "night"],
            datetime(2024, 9, 19): ["day", "night"],
            datetime(2024, 9, 20): ["day"]
        },
        "max_shifts_per_week": 4,
        "min_shifts_per_month": 15
    },
    # Add more employees here...
    {
        "name": "Skoop",
        "unavailability": {
            datetime(2024, 9, 2): ["day", "night"],
            datetime(2024, 9, 3): ["day", "night"],
            datetime(2024, 9, 5): ["day", "night"],
            datetime(2024, 9, 10): ["day", "night"],
            datetime(2024, 9, 15): ["day", "night"],
            datetime(2024, 9, 17): ["day", "night"],
            datetime(2024, 9, 22): ["day", "night"],
            datetime(2024, 9, 24): ["day"],
            datetime(2024, 9, 25): ["day"],
            datetime(2024, 9, 26): ["day"],
            datetime(2024, 9, 28): ["day"],
            datetime(2024, 9, 29): ["day", "night"],

        },
        "max_shifts_per_week": 4,
        "min_shifts_per_month": 15
    },
    {
        "name": "Nadler",
        "unavailability": {
            datetime(2024, 9, 2): ["day", "night"],
            datetime(2024, 9, 26): ["day", "night"],
            datetime(2024, 9, 27): ["day"]
        },
        "max_shifts_per_week": 4,
        "min_shifts_per_month": 15
    }
]

# Generate monthly shifts
year, month = 2024, 9  # September 2024
shifts = generate_monthly_shifts(year, month)

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
        if len([s for s in assignments[emp['name']] if s['date'].isocalendar()[1] == shift['date'].isocalendar()[1]]) < emp['max_shifts_per_week'] and 
        not violates_rules(assignments, emp['name'], shift)
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
        print(f"Warning: Could not assign {shift['date'].strftime('%Y-%m-%d')} {shift['type']} shift")

# Check and try to fulfill minimum monthly shifts
for employee in employees:
    while len(assignments[employee['name']]) < employee['min_shifts_per_month']:
        for shift in shifts:
            if shift not in assignments[employee['name']] and not violates_rules(assignments, employee['name'], shift):
                assignments[employee['name']].append(shift)
                break
        else:
            print(f"Warning: Could not fulfill minimum monthly shifts for {employee['name']}")
            break

# Print the final assignments
print("\nAssignments:")
for emp, assigned_shifts in assignments.items():
    shift_details = [(shift['date'].strftime('%Y-%m-%d'), shift['type']) for shift in assigned_shifts]
    print(f"{emp}: {shift_details}")
    print(f"Total shifts: {len(assigned_shifts)}")

# Print unassigned shifts
unassigned = [shift for shift in shifts if all(shift not in assignments[emp['name']] for emp in employees)]
if unassigned:
    print("\nUnassigned shifts:")
    for shift in unassigned:
        print(f"{shift['date'].strftime('%Y-%m-%d')} {shift['type']}")
else:
    print("\nAll shifts assigned successfully!")

# Print weekly breakdown with shift details
print("\nWeekly breakdown:")
for emp in employees:
    print(f"\n{emp['name']}:")
    
    # Create a dictionary to hold shifts by week number
    shifts_by_week = defaultdict(list)
    
    for shift in assignments[emp['name']]:
        week_number = shift['date'].isocalendar()[1]
        shifts_by_week[week_number].append(shift)
    
    # Get all unique week numbers
    weeks = sorted(shifts_by_week.keys())
    
    for week in weeks:
        week_shifts = shifts_by_week[week]
        if week_shifts:
            print(f"  Week {week}:")
            for shift in week_shifts:
                shift_day = shift['date'].strftime('%A')  # Get the day of the week
                shift_type = shift['type']  # Get the type of shift
                print(f"    {shift_day} ({shift['date'].strftime('%Y-%m-%d')}): {shift_type} shift")
        else:
            print(f"  Week {week}: No shifts assigned")

