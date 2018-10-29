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
from soccer.leagueproperties import LEAGUE_PROPERTIES



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
                info += "\t\t{key} : {value}\n".format(key=key, value=value)
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
        click.secho("%-10s %-25s  %-10s     %-10s  %-25s" %
                    ("ID.", "NAME", "COUNTRY-CODE", "PARENT-ID", "PARENT-AREA"), bold=True, fg=self.colors.TOPIC)
        fmt = (u"{id!s:<10} {name!s:<25} {countryCode!s:<10} {parentAreaId!s:<10}"
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
        try:
            if not player.get('dateOfBirth'):
                player['age'] = Stdout.convert_utc_to_local_time(player['dateOfBirth'], time_diff=True)
            else:
                player['age'] = 'N/A'
        except KeyError:
            import pdb; pdb.set_trace()
        fmt = (u"{id!s:<5} {shirtNumber!s:<5} {name!s:<25} {role!s:<10} {position!s:<15} "
               u"{nationality!s:<20} {age!s:<5}")
        click.secho(fmt.format(**player), fg=self.colors.CONT)

    def write_players(self, squad):
        squad = list(squad)
        click.secho("%-5s %-5s %-25s %-10s %-15s %-20s %-5s" %
                    ("ID.", "S.NO", "NAME", "ROLE", "POSITION", "NATIONALITY", "AGE"),
                    fg=self.colors.TOPIC, bold=True)
        for player in squad:
            self.write_player(player)

    def write_competition(self, comp, full=False):
        """
        :param comp:
        :return:
        """
        comp['area'] = comp['area']['name']
        comp['season'] = Stdout.parse_season(comp['currentSeson']['startDate'], comp['currentSeason']['endDate'])
        fmt = (u"{id!s:<5} {area!s:<15} {name!s:<30} {code!s:<5} {plan!s:<10} {season!s:<10}")
        click.secho(fmt.format(**comp), fg=self.colors.TOPIC)
        if full:
            click.secho("\tSeasons: ", fg=self.colors.TOPIC)
            click.secho("\t\t %-5s  %-15s  %-5s  %-30s" % ("ID.", "SEASON", "MATCHDAY", 'WINNER'), fg=self.colors.TOPIC)
            fmt2 = u"{id!s:<5}   {season!s:<10}   {currentMatchday!s:<5}  {winner!s:<30}"
            for season in comp['seasons']:
                season['season'] = Stdout.parse_season(season['startDate'], season['endDate'])
                fmt2.format(season, fg=self.colors.CONT)


    def write_competitions(self, comps):
        """
        :param comps:
        :return:
        """
        self.write_misc(comps)
        click.secho("%-5s  %-15s  %-30s %-5s  %-10s  %-10s" %
                    ("ID.", "AREA", "COMPETITION", "CODE", "PLAN", "SEASON")
                    , fg=self.colors.TOPIC, bold=True)
        for competition in comps:
            self.write_competition(competition)

    def write_team(self, team, full=False): # can add a list of active competitions
        """
        :param team:
        :return:
        """
        team['areaName'] = team['area']['name']
        fmt = u"{id!s:<5} {areaName!s:<10} {name!s:<30}  {website!s:<20} {founded!s:<5} {venue}"
        click.secho(fmt.format(**team), fg=self.colors.CONT)
        if full:
            click.secho('SQUAD: ', fg=self.colors.TOPIC)
            self.write_players(team['squad'])

    def write_teams(self, teams_dict):  # 000i dont know? should we add stages here
        """
        :param teams_dict:
        :return:
        """
        if "teams" not in teams_dict.keys():
            self.write_team(teams_dict, full=True)
            return
        self.write_misc(teams_dict)
        for team in teams_dict['teams']:
            self.write_team(team)

    def write_scorers(self, scorers_dict):  # duplicate code
        """
        :param scorers_dict:
        :return:
        """
        self.write_misc(scorers_dict)
        click.secho("COMPETITION: \n\tname:{competition}\n\tPLAN: {plan}".format(scorers_dict['competition']),
                    fg=self.colors.INFO)
        click.secho("SEASON: {}".format(Stdout.parse_season(scorers_dict['season']['startDate'],
                                                            scorers_dict['season']['endDate'])))
        click.echo()
        click.secho("%-5s %-25s %-25s %-15s %-3s %-15s %-3s" %
                    ("ID", "NAME", "NATIONALITY", "POSITION", "s.NO", "TEAM", "GOALS"),
                    fg=self.colors.TOPIC, bold=True)
        for _dict in scorers_dict['scorers']:
            res_string = u"{id!s:<5} {name!s:<25} {nationality!s:<25} {position!s:<15} {shirtNumber!s:<3}".format(_dict['player'])
            res_string += u"{name!s:<15}".format(_dict['team']) + u"{numberOfGoals!s:<3}".format(_dict)
            click.secho(res_string, fg=self.colors.CONT)

    def write_standings(self, league_dict):
        """
        :param league_dict:
        :return:
        structure the standings in a more easily human readable format, metadata on relegation,
        promotion to both higher leagues and to participate in cups may not apply to all leagues
        but to only those whose such information is known and is easily attainable
        """
        self.write_misc(league_dict)
        click.secho("COMPETITION: \n\tname:{competition}\n\tPLAN: {plan}".format(league_dict['competition']),
                    fg=self.colors.INFO)
        click.secho("SEASON: {}".format(Stdout.parse_season(league_dict['season']['startDate'],
                                                            league_dict['season']['endDate'])))
        # use a default filter of total and use that to curate the standing objects that you
        # require then for each such object you can run the echo code below
        standings_list = league_dict['standings']
        res = league_dict['filters'].get('standingType')
        type = res if res else 'TOTAL'
        for _dict in standings_list:
            if _dict['type'] == type:
                click.secho('STAGE: {stage}'.format(_dict), fg=self.colors.INFO)
                self.standings(_dict['table'], league_dict['competition']['code'])

    def aggregate_match_data(self, bookings, substitutions, goals):
        """
        :param bookings:
        :param substitutions:
        :param goals:
        puts together the bookings, substitutions, and goals data into a single
        list ordered accordings to the time of the respective event
        """
        bookings.extend(substitutions)
        bookings.extend(goals)
        sall = sorted(bookings, key=lambda x: x['minute'])
        return sall

    def write_match(self, match, full=False, use_12_hour_format=False):  # assume format as shown in sample on the website for now and maybe add lineups
        """
        :param match: data
        :param full: flag to signify verbosity of response
        id date&time(duration) hometeam-name score - score awayteam-name
        detailed:
        datetime(datetime') hometeam-name score - score awayteam-name
            minute' [GOAL] scorer(assist)<-color coded red
            minute' [CARD] player- <-color coded according to card
            minute' [SUB] [player in <=(green)][=> player out(red)]
            minute' [GOAL] scorer(assist)

        """
        if full:
            fmt = u"{{date!s:<15}({min!s:<3}) {hometeam!s:<30} {hscore!s:<2}  -  {ascore!s:<2} {awayteam}!s:<30}"
            click.secho(fmt.format(
                date=Stdout.convert_utc_to_local_time(match['utcDate'], use_12_hour_format=use_12_hour_format,
                                                      show_datetime=True),
                min=match['score']['duration'],
                hometeam=match['homeTeam']['name'],
                awayteam=match['awayTeam']['name'],
                hscore=match['score']['fullTime']['homeTeam'],
                ascore=match['score']['fullTime']['awayTeam']
            ))
            recs = self.aggregate_match_data(match['bookings'], match['substitutions'], match['goals'])
            goals_fmt = u"{minute!s:<3}[GOAl]({team!s:<20}) {scorer}({assist})"
            card_fmt = u"{minute!s:<3}[CARD]({team!s:<20}) {player}"
            sub_fmt = u"{minute!s:<3}[SUB]({team!s:<20}) "
            sub_fmt1 = u"\t\t<=={playerIn}"
            sub_fmt2 = u"\t\t==>{playerOut}"
            for rec in recs:
                if 'playerIn' in rec.keys():
                    click.secho(sub_fmt.format(
                        minute = rec['minute'],
                        team = rec['team']['name']
                    ))
                    click.secho(sub_fmt1.format(playerIn=rec['playerIn']['name']),
                                fg='green')
                    click.secho(sub_fmt2.format(playerOut=rec['playerOut']['name']),
                                fg='red')
                elif 'card' in rec.keys():
                    color = 'yellow' if rec['card'] == 'YELLOW_CARD' else 'red'
                    click.secho(card_fmt.format(
                        minute=rec['minute'],
                        team=rec['team']['name'],
                        player = rec['player']['name']
                    ), fg=color)
                else:
                    click.secho(goals_fmt.format(
                        miinute=rec['minute'],
                        team=rec['team']['name'],
                        scorer=rec['scorer']['name'],
                        assist=rec['assist']['name']
                    ), fg='red')
            return
        fmt = u"{id!s:<10} {date!s:<15}({min!s:<3}) {hometeam!s:<30} {hscore!s:<2}  -  {ascore!s:<2} {awayteam}!s:<30}"
        click.secho(fmt.format(
            id=match['id'],
            date=Stdout.convert_utc_to_local_time(match['utcDate'], use_12_hour_format=use_12_hour_format,
                                                  show_datetime=True),
            min=match['score']['duration'],
            hometeam=match['homeTeam']['name'],
            awayteam=match['awayTeam']['name'],
            hscore=match['score']['fullTime']['homeTeam'],
            ascore=match['score']['fullTime']['awayTeam']
        ))

    def write_matches(self, matches_dicts, time):
        """
        :param matches_dicts: A dictionary containing match response data from the Api
                        as can be obtained from the urls
                        api-football-data.org/v2/matches
                        api-football-data.org/v2/competitions/<id>/matches
        :param time: Boolean flag to dictate if to use 24 hour format to echo time
        This will write matches and their scores for fixtures, scheduled, and live matches
        in the case where we have a single match instance parsed in as the matches_dict
        , this function will write more detailed informatiion regarding the match  including
        the goals, scorers and time of the goal, as well as substitutions and the time that
        they happened
        """
        # determining if its a single match instance
        self.write_misc(matches_dicts)
        header = '%-10s  ' % "ID."
        header1 = "%-20s(%-3s') %-30s %-2s   -  %-2s %-30s" % \
                  ("DATE&TIME", "MIN'", "HOME TEAM", "SCORE", "SCORE", "AWAY TEAM")
        if 'count' not in matches_dicts.keys():
            click.secho(header1, fg=self.colors.TOPIC)
            self.write_match(matches_dicts, full=True, use_12_hour_format=time)
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
        click.secho("%-6s %-30s  %-5s %-3s %-3s %-3s  %-5s %-5s %-5s %-5s" %
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

            team_str = (u"{position!s:<7} {teamName!s:<33} {playedGames!s:<5} {won!s:<3} {draw!s:<3}"
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
    def convert_utc_to_local_time(time_str, use_12_hour_format=False, show_datetime=False, time_diff=False):
        """Converts the API UTC time string to the local user time.
        :param time_diff: gets the the time difference in years from time_str to now"""
        if not (time_str.endswith(" UTC") or time_str.endswith("Z")):
           return time_str

        today_utc = datetime.datetime.utcnow()
        utc_local_diff = today_utc - datetime.datetime.now()

        if time_str.endswith(" UTC"):
            time_str, _ = time_str.split(" UTC")
            utc_time = datetime.datetime.strptime(time_str, "%I:%M %p")
            utc_datetime = datetime.datetime(today_utc.year, today_utc.month, today_utc.day,
                                             utc_time.hour, utc_time.minute)
        else:
            utc_datetime = datetime.datetime.strptime(time_str, "%Y-%m-%sT%H:%M:%SZ")

        local_time = utc_datetime - utc_local_diff

        if time_diff:
            return relativedelta(today_utc,utc_datetime).years
            # use to calculate age of squad members, or teams

        if use_12_hour_format:
            date_format = "%I:%M %p" if not show_datetime else "%a %s, %I:%M %p"
        else:
            date_format = "%H:%M" if not show_datetime else "%a %s, %H:%M"

        return datetime.datetime.strftime(local_time, date_format)

    @staticmethod
    def parse_season(start_date, end_date):
        """
        Takes two utc dates and creates a season date in the commonly known format YYYY/YYYY
        i.e. begin_year/ end_year
        """
        start_year = parser.parse(start_date).year
        end_year = parser.parse(end_date).year
        return '{}/{}'.format(start_date, end_date)


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
