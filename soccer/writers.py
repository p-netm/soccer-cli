import click
import csv
import datetime
import json
import io

from abc import ABCMeta, abstractmethod
from itertools import groupby
from collections import namedtuple
from dateutil.relativedelta import relativedelta
from dateutil import parser

try:
    from soccer.leagueproperties import LEAGUE_PROPERTIES
except ImportError as error:
    from leagueproperties import LEAGUE_PROPERTIES


def get_writer(output_format="stdout", output_file=None):
    return globals()[output_format.capitalize()](output_file)


class BaseWriter(object):

    __metaclass__ = ABCMeta

    def __init__(self, output_file):
        self.output_filename = output_file


    # implement the default writes for the respective resources and subresources
    @abstractmethod
    def write_areas(self, areas_dict):
        """
        :param areas_dict: all records of the area as returned by the api
        format:
        """
        pass

    @abstractmethod
    def write_players(self, player_dict):
        pass

    @abstractmethod
    def write_teams(self, teams_dict):
        pass

    @abstractmethod
    def write_matches(self, team_scores, time):
        pass

    @abstractmethod
    def write_scorers(self, scorers_dict):
        pass

    @abstractmethod
    def write_standings(self, league_dict):
        pass




class Stdout(BaseWriter):

    def __init__(self, output_file):
        self.Result = namedtuple("Result", "homeTeam, goalsHomeTeam, awayTeam, goalsAwayTeam")

        enums = dict(
            WIN="red",
            LOSE="black",
            TIE="yellow",
            MISC="green",
            TIME="yellow",
            CL_POSITION="green",
            EL_POSITION="yellow",
            RL_POSITION="red",
            POSITION="blue",
            INFO="cyan",
            TOPIC="red",
            CONT="blue"
        )
        self.colors = type("Enum", (), enums)

    def write_misc(self, _dict):  # make this have conditional echo according to the presence of the key in the dict
        """
        :param _dict:
        Write the secondary informations, i.e. metadata in regards to the requested data, such as
        filters and count of the returned records
        """
        info = ''
        info += "COUNT: {count}\n".format(**_dict) if 'count' in _dict.keys() else ''
        if 'filters' in _dict.keys():
            info += "FILTERS: \n"
            for key, value in _dict["filters"].items():
                info += "\t{key} : {value}\n".format(key=key, value=value)
        if 'competition' in _dict.keys():
            info += 'COMPETITION: \n\tname:{name}\n\tCODE: {code}\n'.format(**_dict['competition'])
        if 'season' in _dict.keys():
            info += "SEASON: {}\n".format(Stdout.parse_season(_dict['season']['startDate'],
                                                            _dict['season']['endDate']))
        click.secho(info, fg=self.colors.INFO, bold=True)

    def write_areas(self, areas_dict):
        """
        :param areas_dict:
        :param listcodes: is_flag, if set to true display minimal info, goal is to retrieve id
        ====
        count :
        filters:
        id  name country-code parent-id parent-area
        """
        self.write_misc(areas_dict)
        click.secho("%-10s %-25s  %-12s     %-10s  %-25s" %
                    ("ID.", "NAME", "COUNTRY-CODE", "PARENT-ID", "PARENT-AREA"), bold=True, fg=self.colors.TOPIC)
        fmt = (u"{id!s:<10} {name!s:<25} {countryCode!s:<12}     {parentAreaId!s:<10}"
               u" {parentArea!s:<25}")
        if 'areas' not in areas_dict.keys():
            click.secho(fmt.format(**areas_dict), fg=self.colors.CONT)
        else:
            for area in areas_dict["areas"]:
                click.secho(fmt.format(**area), fg=self.colors.CONT)

    def write_player(self, player):
        """
        :param player: a single player record
        :return:
        """
        if not player.get('role'):
            player['role'] = 'N/A'
    
        if not player.get('dateOfBirth'):
            player['age'] = Stdout.convert_utc_to_local_time(player['dateOfBirth'], time_diff=True)
        else:
            player['age'] = 'N/A'
    
        fmt = (u"{id!s:<5} {shirtNumber!s:<5} {name!s:<25} {role!s:<10} {position!s:<15} "
               u"{nationality!s:<20} {age!s:<5}")
        click.secho(fmt.format(**player), fg=self.colors.CONT)

    def write_players(self, squad):
        if type(squad) == list:
            players = squad
        else:
            players = []
            players.append(squad)
        click.secho("%-5s %-5s %-25s %-10s %-15s %-20s %-5s" %
                    ("ID.", "S.NO", "NAME", "ROLE", "POSITION", "NATIONALITY", "AGE"),
                    fg=self.colors.TOPIC, bold=True)
        for player in players:
            self.write_player(player)

    def write_competition(self, comp, full=False):
        """
        :param comp:
        :return:
        """
        color = self.colors.CONT if not full else self.colors.TOPIC
        comp['areaName'] = comp['area']['name']
        if comp.get('currentSeason'):
            comp['_season'] = Stdout.parse_season(comp['currentSeason']['startDate'], comp['currentSeason']['endDate'])
        else: comp['_season'] = None
        fmt = (u"{id!s:<5} {areaName!s:<15} {name!s:<30} {code!s:<5} {plan!s:<10} {_season!s:<10}")
        click.secho(fmt.format(**comp), fg=color)
        if full:
            click.secho("\tSeasons: ", fg=self.colors.TOPIC)
            click.secho("\t\t %-5s  %-10s  %-5s  %-30s" % ("ID.", "SEASON", "MATCHDAY", 'WINNER'), fg=self.colors.TOPIC)
            fmt2 = u"\t\t{id!s:<5}   {season!s:<10}   {currentMatchday!s:<5}  {_winner!s:<30}"
            for season in comp['seasons']:
                season['season'] = Stdout.parse_season(season['startDate'], season['endDate'])
                season['_winner'] = season['winner']['name'] if season['winner'] else None
                click.secho(fmt2.format(**season), fg=self.colors.CONT)

    def write_competitions(self, comps):
        """
        :param comps:
        :return:
        """
        self.write_misc(comps)
        click.secho("%-5s  %-15s  %-30s %-5s  %-10s  %-10s" %
                    ("ID.", "AREA", "COMPETITION", "CODE", "PLAN", "SEASON")
                    , fg=self.colors.TOPIC, bold=True)
        if 'competitions' in comps.keys():
            for competition in comps['competitions']:
                self.write_competition(competition)
        else:
            self.write_competition(comps, full=True)

    def write_team(self, team, full=False): # can add a list of active competitions
        """
        :param team:
        :return:
        """
        team['areaName'] = team['area']['name']
        fmt = u"{id!s:<5} {areaName!s:<10} {name!s:<30}  {founded!s:<5} {venue!s:<}"
        click.secho(fmt.format(**team), fg=self.colors.CONT)
        if full:
            click.secho('SQUAD: ', fg=self.colors.TOPIC)
            self.write_players(team['squad'])

    def write_teams(self, teams_dict):  # 000i dont know? should we add stages here
        """
        :param teams_dict:
        :return:
        """
        self.write_misc(teams_dict)
        click.secho('%-5s %-10s %-30s %-5s %s' % ('ID.','AREA NAME', 'TEAM NAME', 'FOUNDED', 'VENUE'))
        if "teams" not in teams_dict.keys():
            self.write_team(teams_dict, full=True)
            return
        for team in teams_dict['teams']:
            self.write_team(team)

    def write_scorers(self, scorers_dict):  # duplicate code
        """
        :param scorers_dict:
        :return:
        """
        self.write_misc(scorers_dict)
        click.secho("%-5s %-25s %-20s %-15s %-3s %-25s %-3s" %
                    ("ID", "NAME", "NATIONALITY", "POSITION", "s.NO", "TEAM", "GOALS"),
                    fg=self.colors.TOPIC, bold=True)
        for _dict in scorers_dict['scorers']:
            res_string = u"{id!s:<5} {name!s:<25} {nationality!s:<20} {position!s:<15} {shirtNumber!s:<3}".format(**_dict['player'])
            res_string += u" {name!s:<25}".format(**_dict['team']) + u" {numberOfGoals!s:<3}".format(**_dict)
            click.secho(res_string, fg=self.colors.CONT)

    def write_standings(self, league_dict):
        """
        :param league_dict:
        :return:
        structure the standings in a more easily human readable format, metadata on relegation,
        promotion to both higher leagues and to participate in cups may not apply to all leagues
        but to only those whose such information is known and/or is easily attainable
        """
        self.write_misc(league_dict)
        standings_list = league_dict['standings']
        click.secho('Type Filter:  {type}'.format(**standings_list[0]), fg=self.colors.INFO)
        for _dict in standings_list:
            if _dict['stage'] == 'GROUP_STAGE':
                click.secho('GROUP: {group}'.format(**_dict), fg=self.colors.INFO)
            else:
                click.secho('STAGE: {stage}'.format(**_dict), fg=self.colors.INFO)
            self.standings(_dict['table'], league_dict['competition']['code'])

    def write_match(self, match, full=False, use_12_hour_format=False):  # assume format as shown in sample on the website for now and maybe add lineups
        """
        :param match: data
        :param full: flag to signify verbosity of response
        id date&time(duration) hometeam-name score - score awayteam-name
        detailed:
        datetime(datetime') hometeam-name score - score awayteam-name
            head 2 head

        """
        match = match['match'] if 'match' in match.keys() else match
        if full:
            fmt = u"{dateandmin!s:<25} {hometeam!s:<30} {hscore!s:^6}  -  {ascore!s:^6} {awayteam!s:<30}"
            click.secho(fmt.format(
                dateandmin=Stdout.convert_utc_to_local_time(match['utcDate'], use_12_hour_format=use_12_hour_format,
                                                      show_datetime=True) + '(' + match['score']['duration'] + "')",
                hometeam=match['homeTeam']['name'],
                awayteam=match['awayTeam']['name'],
                hscore=match['score']['fullTime']['homeTeam'],
                ascore=match['score']['fullTime']['awayTeam']
            ))
            # head 2 head match information
            if match.get('head2head'):
                click.secho(json.dumps(match['head2head'], indent=4, separators=(",", ": "),
                       ensure_ascii=False), fg=self.colors.CONT)
            else:
                click.secho('Head 2 head information absent', fg='yellow')
            return
        fmt = u"{mid!s:<10} {dateandmin!s:<25} {hometeam!s:<30}  {hscore!s:>6}  -  {ascore!s:^6} {awayteam!s:<30}"
        click.secho(fmt.format(
            mid=match['id'],
            dateandmin=Stdout.convert_utc_to_local_time(match['utcDate'], use_12_hour_format=use_12_hour_format,
                                                        show_datetime=True) + '(' + match['score']['duration'] + "')",
            hometeam=match['homeTeam']['name'],
            awayteam=match['awayTeam']['name'],
            hscore=match['score']['fullTime']['homeTeam'],
            ascore=match['score']['fullTime']['awayTeam']
        ), fg=self.colors.CONT)

    def write_matches(self, matches_dicts, use_12_hour_format=False):
        """
        :param matches_dicts: A dictionary containing match response data from the Api
                        as can be obtained from the urls
                        api-football-data.org/v2/matches
                        api-football-data.org/v2/competitions/<id>/matches
        :param time: Boolean flag to dictate if to use 12 hour format to echo time
        
        This will write matches and their scores for fixtures, scheduled, and live matches
        in the case where we have a single match instance parsed in as the matches_dict
        , this function will write more detailed information regarding the match  including
        the goals, scorers and time of the goal, as well as substitutions and the time that
        they happened
        """
        # determining if its a single match instance
        self.write_misc(matches_dicts)
        header = '%-10s  ' % "ID."
        header1 = "%-25s %-30s %-6s   -  %-6s %-30s" % \
                  ("DATE&TIME(min')", "HOME TEAM", "HSCORE", "ASCORE", "AWAY TEAM")
        if 'count' not in matches_dicts.keys():
            click.secho(header1, fg=self.colors.TOPIC)
            self.write_match(matches_dicts, full=True, use_12_hour_format=use_12_hour_format)
        else:
            click.secho(header + header1, fg=self.colors.TOPIC)
            for match in matches_dicts['matches']:
                self.write_match(match)

    def standings(self, table, league='default'):
        """ Prints the league standings in a pretty way
        :param table: a list containing the json data for teams sorted according to the teams
                    respective positions
        :param league: The league code
        """
        league = league if league in LEAGUE_PROPERTIES.keys() else 'default'
        click.secho("%-3s %-29s  %-6s %-3s %-3s %-3s %-5s %-5s %-5s %-5s" %
                    ("POS", "CLUB", "PLAYED", "W", "D", "L", "G.F.", "G.A.", "G.D.", "POINTS"))
        for team in table:
            if team["goalDifference"] >= 0:
                team["goalDifference"] = " " + str(team["goalDifference"])
            team['teamName'] = team['team']['name']
            # Define the upper and lower bounds for Champions League,
            # Europa League and Relegation places.
            # This is so we can highlight them appropriately.
            cl_upper, cl_lower = LEAGUE_PROPERTIES[league]["cl"]
            el_upper, el_lower = LEAGUE_PROPERTIES[league]["el"]
            rl_upper, rl_lower = LEAGUE_PROPERTIES[league]["rl"]

            team_str = (u"{position!s:<3} {teamName!s:<30} {playedGames!s:<7} {won!s:<3} {draw!s:<3}"
                        u"{lost!s:<3} {goalsFor!s:<5} {goalsAgainst!s:<5}"
                        u" {goalDifference!s:<5} {points}").format(**team)
            if cl_upper <= team["position"] <= cl_lower:
                click.secho(team_str, bold=True, fg=self.colors.CL_POSITION)
            elif el_upper <= team["position"] <= el_lower:
                click.secho(team_str, fg=self.colors.EL_POSITION)
            elif rl_upper <= team["position"] <= rl_lower:
                click.secho(team_str, fg=self.colors.RL_POSITION)
            else:
                click.secho(team_str, fg=self.colors.POSITION)

    @staticmethod
    def time_difference(time_str):
        """Get the datetime timezone aware difference in years between two dates"""
        start = parser.parse(time_str)
        if start.tzinfo:
            today = datetime.datetime.now(datetime.timezone.utc)
        else:
            today = datetime.datetime.now()
        diff = relativedelta(start, today).years
        return abs(diff)

    @staticmethod
    def convert_utc_to_local_time(time_str, use_12_hour_format=False, show_datetime=False, time_diff=False):
        """Converts the API UTC time string to the local user time.
        :param time_diff: gets the the time difference in years from time_str to now"""
        today_utc = datetime.datetime.utcnow()
        utc_local_diff = today_utc - datetime.datetime.now()

        utc_datetime = parser.parse(time_str)
        local_time = utc_datetime - utc_local_diff

        if time_diff:
            return Stdout.time_difference(time_str)

        if use_12_hour_format:
            date_format = "%I:%M %p" if not show_datetime else "%x, %I:%M %p"
        else:
            date_format = "%H:%M" if not show_datetime else "%x, %H:%M"

        return datetime.datetime.strftime(local_time, date_format)

    @staticmethod
    def parse_season(start_date, end_date):
        """
        Takes two utc dates and creates a season date in the commonly known format YYYY/YYYY
        i.e. begin_year/ end_year
        """
        start_year = parser.parse(start_date).year
        end_year = parser.parse(end_date).year
        if end_year < start_year:
            end_year, start_year = start_year, end_year
        return '{}/{}'.format(start_year, end_year)


class Json(BaseWriter):

    def generate_output(self, result):
        if not self.output_filename:
            click.echo(json.dumps(result, indent=4, separators=(",", ": "),
                       ensure_ascii=False))
        else:
            with io.open(self.output_filename, "w", encoding="utf-8") as json_file:
                data = json.dumps(result, json_file, indent=4,
                                  separators=(",", ": "), ensure_ascii=False)
                json_file.write(data)

    def write_areas(self, areas_dict):
        self.generate_output(areas_dict)

    def write_players(self, player_dict):
        self.generate_output(player_dict)

    def write_competitions(self, comps):
        self.generate_output(comps)

    def write_teams(self, teams_dict):
        self.generate_output(teams_dict)

    def write_scorers(self, scorers_dict):
        self.generate_output(scorers_dict)

    def write_standings(self, league_dict):
        self.generate_output(league_dict)

    def write_matches(self, match_dict, use_12_hour_format=False):
        self.generate_output(match_dict)