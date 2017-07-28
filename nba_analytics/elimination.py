import pandas as pd
import numpy as np
import league

# Load excel sheets
team_info = pd.read_excel('Analytics_Attachment.xlsx', sheetname=0)
schedule = pd.read_excel('Analytics_Attachment.xlsx', sheetname=1, converters={'Date': pd.to_datetime})
elimination = pd.read_excel('Analytics_Attachment.xlsx', sheetname=2)

# Encode strings
all_teams = [i.encode('utf-8') for i in team_info.Team_Name.unique()]
all_divisions = [i.encode('utf-8') for i in team_info.Division_id.unique()]
all_conferences = [i.encode('utf-8') for i in team_info.Conference_id.unique()]

# Load division/conference information
division_dict = {}
for division in all_divisions:
	division_dict[division] = [i.encode('utf-8') for i in list(team_info[team_info.Division_id==division].Team_Name)]
conference_dict = {}
for conference in all_conferences:
	conference_dict[conference] = [i.encode('utf-8') for i in list(team_info[team_info.Conference_id==conference].Team_Name)]

# Begin simulation
nba = league.league(all_teams, division_dict, conference_dict)

def best_scenario(league, schedule, position, team, opp):
	import copy
	dummy_nba = copy.deepcopy(league)
	for i in range(position+1, schedule.shape[0]):
		match = schedule.iloc[i]
		if match['Home Team'] == team and match['Away Team'] == opp:
			dummy_nba.add_match(match['Date'].strftime('%m/%d/%Y'), match['Home Team'], match['Away Team'], 100, 0)
		elif match['Home Team'] == opp and match['Away Team'] == team:
			dummy_nba.add_match(match['Date'].strftime('%m/%d/%Y'), match['Home Team'], match['Away Team'], 0, 100)
		elif match['Home Team'] == team or match['Away Team'] == opp:
			dummy_nba.add_match(match['Date'].strftime('%m/%d/%Y'), match['Home Team'], match['Away Team'], 100, 0)
		elif match['Home Team'] == opp or match['Away Team'] == team:
			dummy_nba.add_match(match['Date'].strftime('%m/%d/%Y'), match['Home Team'], match['Away Team'], 0, 100)
	return dummy_nba

schedule.Date = pd.to_datetime(schedule.Date, format='%Y/%d/%Y')
eliminated = []
elimination.loc[:, 'Date Eliminated'] = 'Playoffs'

for i in range(schedule.shape[0]):
	match = schedule.iloc[i]
	nba.add_match(match['Date'].strftime('%m/%d/%Y'), match['Home Team'], match['Away Team'], match['Home Score'], match['Away Score'])
	for team in all_teams:
		if nba.is_dangerous(team) and team not in eliminated:
			print team + ' is dangerous!'
			opp = nba.get_same_div_opp(team, 8)
			dummy_nba = best_scenario(nba, schedule, i, team, opp)
			if dummy_nba.tie_breaker(team, opp) != team:
				eliminated.append(team)
				elimination.loc[elimination['Team']==team, 'Date Eliminated'] = match['Date'].strftime('%m/%d/%Y')
				print team + ' is eliminated on ' + match['Date'].strftime('%m/%d/%Y') + '\n'

# Output elimination dates
elimination.to_csv('result.csv', index = False)



