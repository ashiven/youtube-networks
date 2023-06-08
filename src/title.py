import ast

# Load the output.log data
with open('output.log', 'r') as file:
    data = file.read()

# Convert the string representation to a list of dictionaries
data_list = ast.literal_eval(data)

# Extract the titles of YouTube videos
titles = []
for item in data_list:
    for video_id, details in item.items():
        title = details[1]
        titles.append(title)

# Save the titles to titles.log
with open('titles.log', 'w') as file:
    for title in titles:
        file.write(title + '\n')