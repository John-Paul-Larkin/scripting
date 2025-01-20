import requests
from bs4 import BeautifulSoup

BASE_URL = "https://fbref.com/en/comps/9/Premier-League-Stats"

# Fetch the data from the API
def fetch_data():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print(response.status_code)
        print("Failed to fetch data")
        exit()
    return soup

def bottom_three(stats_table):
    rows = stats_table.find_all('tr')
    ranked_rows = []
    # Iterate through the rows and extract rank and team name
    for row in rows:
        # Find the rank cell and team cell
        rank_cell = row.find('th', {"data-stat": "rank"})
        team_cell = row.find('td', {"data-stat": "team"})
        
        if rank_cell and team_cell:
            # Extract rank and team name text
            rank_value = rank_cell.text.strip()
            if rank_value.isdigit():
                # Get team name from the anchor tag
                team_name = team_cell.find('a').text.strip()  
                ranked_rows.append((int(rank_value), team_name))
    
    # Sort rows by rank (ascending)
    ranked_rows.sort(key=lambda x: x[0])
    
    # Get and return the bottom 3 teams
    bottom_3_teams = ranked_rows[-3:]
    
    for rank, team in bottom_3_teams:
        print(f"Rank {rank}: {team}")
        
def top_five_highest_attendance(stats_table):
    rows = stats_table.find_all('tr')
    ranked_rows = []

    # Iterate through the rows
    for row in rows:
        # Find the attendance cell
        attendance_cell = row.find('td', {"data-stat": "attendance_per_g"})
        if attendance_cell:
            # Extract attendance value
            attendance_value = attendance_cell.text.strip().replace(',', '')
            try:
                attendance_value = int(attendance_value)
            except ValueError:
                continue  # Skip rows with invalid attendance data

            # Find the team name
            team_cell = row.find('td', {"data-stat": "team"})
            if team_cell:
                team_name = team_cell.text.strip()
                ranked_rows.append((team_name, attendance_value))

    # Sort rows by attendance in descending order
    ranked_rows.sort(key=lambda x: x[1], reverse=True)

    # Return the top five teams
    for team, attendance in ranked_rows[:5]:
        print(f"Attendance {attendance:,}: {team}")
    
    return ranked_rows[:5]



def main(): 
    soup = fetch_data()
    ID = 'results2024-202591_overall'
    
    # find the table with the hardcoded ID
    stats_table = soup.find('table', {'id': ID}) 
    
    # Extract table headers
    # headers = [th.text.strip() for th in stats_table.find_all('th')]
    # print("Headers:", headers)
    
    # Get and print bottom three teams
    bottom_three(stats_table)
    
    top_five_highest_attendance(stats_table)
      

if __name__ == "__main__":  
    main() 