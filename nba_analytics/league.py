class match:
	def __init__(self, date, home, away, home_score, away_score):
		self.home = home
		self.away = away
		self.home_score = home_score
		self.away_score = away_score
		self.date = date

	def get_winner(self):
		if self.home_score > self.away_score:
			return self.home
		else:
			return self.away

	def get_loser(self):
		if self.home_score < self.away_score:
			return self.home
		else:
			return self.away

	def get_opponent(self, team):
		if self.home == team:
			return self.away
		else:
			return self.home

	def get_match_diff(self, team):
		if self.home == team:
			return self.home_score - self.away_score
		else:
			return self.away_score - self.home_score

class league:
	def __init__(self, teams, division, conference):
		self.team_names = teams
		self.division = division
		self.conference = conference
		self.wins = [0] * len(self.team_names)
		self.losses = [0] * len(self.team_names)
		self.win_perc = [0] * len(self.team_names)
		self.matches = []

	def get_ix(self, team):
		return [i for i in range(len(self.team_names)) if self.team_names[i] == team][0]

	def add_win(self, team):
		team_id = self.get_ix(team)
		self.wins[team_id] += 1
		self.win_perc[team_id] = self.wins[team_id] / float(self.get_games_played(team))
		return None

	def add_loss(self, team):
		team_id = self.get_ix(team)
		self.losses[team_id] += 1
		self.win_perc[team_id] = self.wins[team_id] / float(self.get_games_played(team))
		return None

	def add_match(self, date, home_team, away_team, home_score, away_score):
		new_match = match(date, home_team, away_team, home_score, away_score)
		self.add_win(new_match.get_winner())
		self.add_loss(new_match.get_loser())
		self.matches.append(new_match)

		return None

	def get_wins(self, team):
		team_id = self.get_ix(team)
		return self.wins[team_id]

	def get_losses(self, team):
		team_id = self.get_ix(team)
		return self.losses[team_id]

	def get_games_played(self, team):
		return self.get_wins(team) + self.get_losses(team)

	def get_win_perc(self, team):
		team_id = self.get_ix(team)
		return self.win_perc[team_id]

	def get_team_matches(self, team):
		match_list = []
		for match in self.matches:
			if match.home == team or match.away == team:
				match_list.append(match)
		return match_list

	def get_matchup(self, teamA, teamB):
		match_list = []
		for match in self.matches:
			if (match.home == teamA and match.away == teamB) or (match.home == teamB and match.away == teamA):
				match_list.append(match)
		return match_list

	def get_matchup_wins(self, teamA, teamB):
		teamA_wins = 0
		teamB_wins = 0
		for match in self.get_matchup(teamA, teamB):
			if match.get_winner() == teamA:
				teamA_wins += 1
			else:
				teamB_wins += 1
		return teamA_wins, teamB_wins

	def get_division(self, team):
		for division, member in self.division.iteritems():
			if team in member:
				return division

	def get_conference(self, team):
		for conference, member in self.conference.iteritems():
			if team in member:
				return conference

	def is_division_winner(self, team):
		division = self.get_division(team)
		best_team = None
		best_winc = 0
		for i in self.division[division]:
			if self.get_win_perc(i) > best_winc:
				best_team = i
				best_winc = self.get_win_perc(i)
		if best_team == None:
			return True
		else:
			return False

	def get_division_win_perc(self, team):
		division = self.get_division(team)
		all_matches = self.get_team_matches(team)
		division_matches = []
		for match in all_matches:
			if match.get_opponent(team) in self.division[division]:
				division_matches.append(match)
		division_wins = sum(1 for i in division_matches if i.get_winner() == team)
		return division_wins / float(len(division_matches))

	def same_division(self, teamA, teamB):
		teamA_div = self.get_division(teamA)
		teamB_div = self.get_division(teamB)
		return teamA_div == teamB_div

	def get_conf_win_perc(self, team):
		conference = self.get_conference(team)
		all_matches = self.get_team_matches(team)
		conf_matches = []
		for match in all_matches:
			if match.get_opponent(team) in self.conference[conference]:
				conf_matches.append(match)
		conf_wins = sum(1 for i in conf_matches if i.get_winner() == team)
		return conf_wins / float(len(conf_matches))

	def get_conference_lb(self, conf):
		win_perc_list = []
		for team in self.conference[conf]:
			win_perc_list.append((team,self.get_win_perc(team)))
		sorted_list = sorted(win_perc_list, key = lambda x: x[1], reverse = True)
		return sorted_list

	def get_rank(self, team):
		conference = self.get_conference(team)
		leaderboard = self.get_conference_lb(conference)
		rank = [i for i in range(len(leaderboard)) if leaderboard[i][0] == team][0]
		return rank+1

	def get_same_div_opp(self, team, rank):
		conference = self.get_conference(team)
		return self.get_conference_lb(conference)[rank-1][0]

	def is_dangerous(self, team):
		num_8 = self.get_same_div_opp(team, 8)
		games_left_me = 82 - self.get_games_played(team)
		if num_8 != team:
			if games_left_me + self.get_wins(team) <= self.get_wins(num_8):
				return True
			else:
				return False

	def get_playoff_win_perc_same_div(self, team):
		conference = self.get_conference(team)
		playoff_teams = self.get_conference_lb(conference)[:9]
		matchup = []
		wins = 0
		for opp in playoff_teams:
			matchup += self.get_matchup(team, opp[0])
		for match in matchup:
			if match.get_winner() == team:
				wins += 1
		return wins / float(len(matchup))

	def get_playoff_win_perc_other_div(self, team):
		conference = self.get_conference(team)
		if conference == 'West':
			conference = 'East'
		else:
			conference = 'West'
		playoff_teams = self.get_conference_lb(conference)[:9]
		matchup = []
		wins = 0
		for opp in playoff_teams:
			matchup += self.get_matchup(team, opp[0])
		for match in matchup:
			if match.get_winner() == team:
				wins += 1
		return wins / float(len(matchup))

	def get_point_diff(self, team):
		diff = 0
		for match in self.get_team_matches(team):
			diff += match.get_match_diff(team)
		return diff

	def tie_breaker(self, teamA, teamB):
		if self.get_win_perc(teamA) > self.get_win_perc(teamB):
			return teamA
		elif self.get_win_perc(teamA) < self.get_win_perc(teamB):
			return teamB
		else:
			teamA_wins, teamB_wins = self.get_matchup_wins(teamA, teamB)
			if teamA_wins > teamB_wins:
				return teamA
			elif teamA_wins < teamB_wins:
				return teamB
			else:
				if self.is_division_winner(teamA) and ~self.is_division_winner(teamB):
					return teamA
				elif ~self.is_division_winner(teamA) and self.is_division_winner(teamB):
					return teamB
				elif self.same_division(teamA, teamB):
					if self.get_division_win_perc(teamA) > self.get_division_win_perc(teamB):
						return teamA
					elif self.get_division_win_perc(teamA) < self.get_division_win_perc(teamB):
						return teamB
				else:
					if self.get_conf_win_perc(teamA) > self.get_conf_win_perc(teamB):
						return teamA
					elif self.get_conf_win_perc(teamA) < self.get_conf_win_perc(teamB):
						return teamB
					else:
						if self.get_playoff_win_perc_same_div(teamA) > self.get_playoff_win_perc_same_div(teamB):
							return teamA
						elif self.get_playoff_win_perc_same_div(teamA) < self.get_playoff_win_perc_same_div(teamB):
							return teamB
						else:
							if self.get_playoff_win_perc_other_div(teamA) > self.get_playoff_win_perc_other_div(teamB):
								return teamA
							elif self.get_playoff_win_perc_other_div(teamA) < self.get_playoff_win_perc_other_div(teamB):
								return teamB
							else:
								if self.get_point_diff(teamA) > self.get_point_diff(teamB):
									return teamA
								elif self.get_point_diff(teamA) < self.get_point_diff(teamB):
									return teamB
								else:
									import random
									dice = random.choice([1,2])
									if dice == 1:
										return teamA
									else:
										return teamB





