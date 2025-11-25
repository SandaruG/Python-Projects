import graphviz

# Create a new directed graph
dot = graphviz.Digraph(comment='SQL Query Workflow')

# Define nodes
dot.node('user', 'User', shape='oval')
dot.node('input_query', 'Inputs SQL Query', shape='box')
dot.node('phpmyadmin', 'phpMyAdmin', shape='box')
dot.node('database', 'MySQL Database\n(medicare_health_db)', shape='box')
dot.node('tables', 'Tables: Patients,\nPhysicians, etc.', shape='box')
dot.node('processes', 'Processes: Insert,\nSelect, Update', shape='box')
dot.node('output', 'Output: Query Results', shape='box')
dot.node('view_results', 'User Views Results', shape='oval')

# Define edges
dot.edge('user', 'input_query')
dot.edge('input_query', 'phpmyadmin')
dot.edge('phpmyadmin', 'database')
dot.edge('database', 'tables')
dot.edge('tables', 'processes')
dot.edge('processes', 'output')
dot.edge('output', 'view_results')

# Set graph attributes for vertical layout
dot.attr(rankdir='TB')  # Top to Bottom

# Save and render the graph
dot.render('sql_workflow', format='png', cleanup=True)

print("Flowchart generated as 'sql_workflow.png'")