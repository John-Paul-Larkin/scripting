import requests
import pygal  # type: ignore
from pygal.style import Style  # type: ignore
import json
# Define the URL for the API
BASE_URL = "https://api.fbi.gov/wanted/v1/list"

# Fetch the data from the API
def fetch_data():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
    else:
        print(response.status_code)
        print("Failed to fetch data")
        exit()
    return data
    
def loop_through_all(num_pages):
    # Initialize an empty list to store all items
    all_wanted = []

    # Calculate total pages needed
    page = 1
    response = requests.get(f"{BASE_URL}?page={page}")
    data = response.json()
    total_records = data['total']

    print(f"Starting to fetch {total_records} records across {num_pages} pages...")

    # Fetch data from all pages
    for page in range(1, num_pages):
        print(f"Fetching page {page} of {num_pages}...")
        response = requests.get(f"{BASE_URL}?page={page}")

        if response.status_code == 200:
            page_data = response.json()
            all_wanted.extend(page_data['items'])
        else:
            print(f"Failed to fetch page {page}")
            continue


    print(f"\nFetched a total of {len(all_wanted)} wanted individuals") 
        # Save the data to a JSON file
    with open('wanted_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_wanted, f, indent=2)
    return all_wanted
 
# print the top 20 wanted individuals
def print_top_20(data):
    # Print the top 20 wanted individuals
    print("\nTop 20 Wanted Individuals:")
    for i in range(20):
        if i < len(data['items']):
            item = data['items'][i]
            print(f"{i+1}. {item['title']}")


# print the keys available for each wanted individual
def print_item_keys(data):
    print("\nKeys available for each wanted individual:")
    if len(data['items']) > 0:
        print(json.dumps(list(data['items'][0].keys()), indent=2))
 
# print the details of the first 100 persons 
def print_item_details(item_type, data): 
    for i in range(100):
        print(data['items'][i][item_type]) 
 
# count the number of cases per sex
def parse_all_wanted_by_sex(all_wanted):
    sex_count = {}
    
    for item in all_wanted:
        sex_count[item['sex']] = sex_count.get(item['sex'], 0) + 1
    print(sex_count)
    return sex_count

# count the number of occupations per person
def parse_all_wanted_by_occupation(all_wanted):
    occupation_count = {}
    for item in all_wanted:
        if item['occupations'] is not None:
            for occupation in item['occupations']:
                occupation_count[occupation] = occupation_count.get(occupation, 0) + 1
            else:
                occupation_count['No occupation'] = occupation_count.get('No occupation', 0) + 1
    print(occupation_count)
    return occupation_count
 
# count the number of subjects per person
def parse_all_wanted_by_subjects(all_wanted):
    subjects_count = {}
    for item in all_wanted:
        if item['subjects'] is not None:
            for subject in item['subjects']:
                subjects_count[subject] = subjects_count.get(subject, 0) + 1
    print(subjects_count)
    return subjects_count

# count the number of aliases per person
def parse_all_wanted_by_aliases(all_wanted):
    # Initialise counters in a dictionary
    alias_counts = {
        "no_aliases": 0,
        "one_alias": 0,
        "two_aliases": 0,
        "three_aliases": 0,
        "four_or_more_aliases": 0
    }
    
    # Iterate through the data
    for item in all_wanted:
        aliases = item.get("aliases")
        if aliases:  # Check if aliases is not None or empty
            if len(aliases) == 0:
                alias_counts["no_aliases"] += 1
            elif len(aliases) == 1:
                alias_counts["one_alias"] += 1
            elif len(aliases) == 2:
                alias_counts["two_aliases"] += 1
            elif len(aliases) == 3:
                alias_counts["three_aliases"] += 1
            else:
                alias_counts["four_or_more_aliases"] += 1
      
           
    
    print(alias_counts)
    return alias_counts

# Parse the subjects and count the number of cases by sex
def parse_subjects_by_sex(all_wanted):
    
    subjects_by_sex = {}
    
    for item in all_wanted:
        # Normalize sex field - if it is None or empty, set it to Unknown
        sex = item.get('sex', 'Unknown') or 'Unknown'
        subjects = item.get('subjects', [])
        
        for subject in subjects:
            # Initialise subject entry if it doesn't exist
            if subject not in subjects_by_sex:
                subjects_by_sex[subject] = {'Male': 0, 'Female': 0, 'Unknown': 0}
            
            # Increment the count for the normalised sex
            subjects_by_sex[subject][sex] += 1

    print(subjects_by_sex)
    return subjects_by_sex


    
    
def create_subjects_bar_chart(data):
    # Create a bar chart
    bar_chart = pygal.Bar()
    bar_chart.title = 'Count of FBI Cases by Subject'
    bar_chart.x_title = 'Subjects'
    bar_chart.y_title = 'Count'

    # For each category in the data, add it to the chart
    for category, count in data.items():
        bar_chart.add(category, count)

    # Render the chart to a file
    bar_chart.render_to_file('fbi_cases_by_subject.svg')
    
    
def create_sex_pie_chart(sex_count):
    # just playing with some styling
    custom_style = Style(
        background='white',
        plot_background='#f5f5f5',
        foreground='#333',
        foreground_strong='#000',
        foreground_subtle='#666',
        opacity='.8',
        opacity_hover='.9',
        transition='400ms ease-in',
        colors=('#3498db', '#e74c3c', '#95a5a6')  
    )

    pie_chart = pygal.Pie(style=custom_style)
    pie_chart.title = 'Count of FBI Cases by Sex'
    pie_chart.legend_at_bottom = True
    # Format the value to show the number of cases
    pie_chart.value_formatter = lambda x: f'{x} cases'

    male_count = sex_count.get('Male', 0)
    female_count = sex_count.get('Female', 0)
    # Combine None and empty string counts
    none_count = sex_count.get(None, 0) + sex_count.get('', 0)  

    # Explode Male slice for emphasis
    pie_chart.add('Male', male_count, explode=10)  
    pie_chart.add('Female', female_count)
    pie_chart.add('None/Unknown', none_count)

    # render the chart to a file
    pie_chart.render_to_file('fbi_cases_by_sex.svg')
 
def create_aliases_bar_chart(data):
    bar_chart = pygal.Bar()
    bar_chart.title = 'Count of FBI Cases by Aliases'
    bar_chart.x_title = 'Aliases'
    bar_chart.y_title = 'Count'

    # For each category in the data, add it to the chart
    for category, count in data.items():
        bar_chart.add(category, count)

    # render the chart to a file
    bar_chart.render_to_file('fbi_cases_by_aliases.svg')

def create_subjects_by_sex_chart(subjects_by_sex):
    bar_chart = pygal.Bar()
    bar_chart.title = 'FBI Cases by Subject and Sex'
    bar_chart.x_title = 'Subjects'
    bar_chart.y_title = 'Count'
    # Rotate x-axis labels to vertical for easier r
    bar_chart.x_label_rotation = 270  

    # Extract data for the chart
    subjects = list(subjects_by_sex.keys())
    # Get the counts for each sex 
    male_counts = [subjects_by_sex[subject].get('Male', 0) for subject in subjects]
    female_counts = [subjects_by_sex[subject].get('Female', 0) for subject in subjects]
    unknown_counts = [subjects_by_sex[subject].get('Unknown', 0) for subject in subjects]

    bar_chart.x_labels = subjects
    bar_chart.add('Male', male_counts)
    bar_chart.add('Female', female_counts)
    bar_chart.add('Unknown', unknown_counts)

    # Render the chart to a file
    bar_chart.render_to_file('fbi_cases_by_subject_and_sex.svg')

def main():  
    # all_wanted = loop_through_all(20)
    # Load the data from the json file
    # Instead of calling the APi since i hit HTTP 429 - Too many requests
    all_wanted = json.load(open('wanted_data.json'))
    
    # Create a dictionary to store the data
    # Each funciton will add to the dictionary
    data = {}
    data['all_wanted'] = all_wanted
    data['total_wanted'] = len(all_wanted)
    data['sex_count'] = parse_all_wanted_by_sex(all_wanted)
    data['subjects_count'] = parse_all_wanted_by_subjects(all_wanted)
    data['aliases_count'] = parse_all_wanted_by_aliases(all_wanted)
    data['subjects_by_sex'] = parse_subjects_by_sex(all_wanted)
    
    # Create the charts
    create_subjects_bar_chart(data['subjects_count'])
    create_sex_pie_chart(data['sex_count'])
    create_aliases_bar_chart(data['aliases_count'])
    create_subjects_by_sex_chart(data['subjects_by_sex'])


if __name__ == "__main__":  
    main() 