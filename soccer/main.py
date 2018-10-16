import os
import sys
import json

import click

from leaagueids import LEAGUE_IDS
from exceptions import IncorrectParametersException
from writers import get_writer
from request_handler import RequestHandler


def load_json(file):
    """Load JSON file at app start"""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, file)) as jfile:
        data = json.load(jfile)
    return data

TEAM_DATA = load_json("teams.json")["teams"]
TEAM_NAMES = {team["code"]: team["id"] for team in TEAM_DATA}



def get_input_key():
    """Input API key and validate"""
    click.secho("No API key found!", fg="yellow", bold=True)
    click.secho("Please visit {0} and get an API token.".format(RequestHandler.BASE_URL),
                fg="yellow", bold=True)
    while True:
        confkey = click.prompt(click.style("Enter API key",
                                           fg="yellow", bold=True))
        if len(confkey) == 32:  # 32 chars
            try:
                int(confkey, 16)  # hexadecimal
            except ValueError:
                click.secho("Invalid API key", fg="red", bold=True)
            else:
                break
        else:
            click.secho("Invalid API key", fg="red", bold=True)
    return confkey


def load_config_key():
    """Load API key from config file, write if needed"""
    global api_token
    try:
        api_token = os.environ['SOCCER_CLI_API_TOKEN']
    except KeyError:
        home = os.path.expanduser("~")
        config = os.path.join(home, ".soccer-cli.ini")
        if not os.path.exists(config):
            with open(config, "w") as cfile:
                key = get_input_key()
                cfile.write(key)
        else:
            with open(config, "r") as cfile:
                key = cfile.read()
        if key:
            api_token = key
        else:
            os.remove(config)  # remove 0-byte file
            click.secho('No API Token detected. '
                        'Please visit {0} and get an API Token, '
                        'which will be used by Soccer CLI '
                        'to get access to the data.'
                        .format(RequestHandler.BASE_URL), fg="red", bold=True)
            sys.exit(1)
    return api_token


def map_team_id(code):
    """Take in team ID, read JSON file to map ID to name"""
    """people need ids to access teams, the current approach requires that the programmers populates a subset
    of known teams with their codes and then save that in a json file from which users can read the team on interest 
    code, however this approach has clear shortcomings . its not robust and requires often manual changes to add
    teams details as they are being added in the api. yet again, the teams.json file held about 250 team records which
    is a very small portion of the teams that we expect the api to serve. My proposed change is to let the api tell
    us what teams it has. my change will include the application recording any new teams inside the json.teams file
    after each request, where the api returns team data that the application has not seen before.
    
    As a result one can look at teams code and add filters such as league, or area."""
    for team in TEAM_DATA:
        if team["code"] == code:
            click.secho(team["name"], fg="green")
            break
    else:
        click.secho("No team found for this code", fg="red", bold=True)


def list_team_codes():
    """List team names in alphabetical order of team ID, per league."""
    # Sort teams by league, then alphabetical by code
    cleanlist = sorted(TEAM_DATA, key=lambda k: (k["league"]["name"], k["code"]))
    # Get league names
    leaguenames = sorted(list(set([team["league"]["name"] for team in cleanlist])))
    for league in leaguenames:
        teams = [team for team in cleanlist if team["league"]["name"] == league]
        click.secho(league, fg="green", bold=True)
        for team in teams:
            if team["code"] != "null":
                click.secho(u"{0}: {1}".format(team["code"], team["name"]), fg="yellow")
        click.secho("")


import click

@click.group()
@click.option('--apikey', default='Some key',
              help="API key to use.")
@click.option('--use12hour', is_flag=True, default=False,
              help="Displays the time using 12 hour format instead of 24 (default).")
@click.option('--stdout', 'output_format', flag_value='stdout', default=True,
              help="Print to stdout.")
@click.option('--csv', 'output_format', flag_value='csv',
              help='Output in CSV format.')
@click.option('--json', 'output_format', flag_value='json',
              help='Output in JSON format.')
@click.option('-o', '--output-file', default=None,
              help="Save output to a file (only if csv or json option is provided).")
def main(apikey, use12hour, output_format, output_file):
    """
    A CLI for live and past football scores from various football leagues.
    resources are given as commands and subresources are options

    Resources:

    \b
    - Competitions
        -match
        -team
        -standings
        -scorers
    - Match
    - Team
        -match
    - Areas
    - Player
        -match
    """
    headers = {'X-Auth-Token': apikey}
    pass


@click.command()
@click.option('--id', '-i', 'competition_id', help='id for the competitions to load, if no id: returns all available competitions')
@click.option('--list', 'listcodes', is_flag=True, help='list codes and names of all available competitions')
@click.option('--teams','-t', help=' list teams for that particular competition')
@click.option('--standings', is_flag=True, help='show standings for particular competition')
@click.option('--matches', '-m', is_flag=True, help='list matches for a particular competition')
# filters
@click.option('--areas', help='[competitions]:: filters competition to particular area')
@click.option('--plan', help='[competitions]:: filters and shows competitions for a particular plan')
@click.option('--season', help='[teams, matches]:: list matches, and teams in a particular competition for given season')
@click.option('--stage', help='[teams, matches]:: filters either teams or matches to given stage')
@click.option('--standingtype', help='[standings]:: show stndings for a particular competition ')
@click.option('--datefrom', help='[matches]:: list matches for competition with given id from given date')
@click.option('--dateto', help='[matches]:: list matches for competition with given id to this given day')
@click.option('--status', help='[matches]:: filter matches for competition with given id to status of play')
@click.option('--matchday', help='for [matches]: filter matches for competition with given id to given matchday')
@click.option('--group', help='for[matches]: filter matches for competition with given id to given group')

def competitions(competition_id, listcodes, teams, standings, matches, areas, plan, season, stage, standingtype,
                 datefrom, dateto, status, matchday, group):
    print(competition_id, listcodes, teams, standings, matches, areas, plan, season, stage, standingtype,
                 datefrom, dateto, status, matchday, group)

@click.command()
@click.option('--id', '-i', 'player_id', help='displays player with this id')
@click.option('--matches', '-m',is_flag=True, help='matches where player with given id played')
@click.option('--from', '-f', 'date_from', help='display matches in which player with given id played from this date')
@click.option('--to', '-t', 'date_to', help='display matches in which player with given id played to this date')
@click.option('--competitions', '-c',  help='display matches in which player with given id played that belong to this competition')
@click.option('--status', '-s', help='display matches in which player with given id played that have this status')
@click.option('--limit', '-l', 'date_from', help='display limit matches in which player with given id played ')
def players(player_id, matches, date_from, date_to, competitions, status, limit):
    pass

@click.command()
@click.option('--id', '-i', 'match_id', help='displays matches with this id | display or',)
@click.option('--from', '-f', 'date_from', help='display matches played from this date')
@click.option('--to', '-t', 'date_to', help='display matches played to this date')
@click.option('--competitions', '-c',  help='display matches with given id that belong to this competition')
@click.option('--status', '-s', help='display matches  that have this status')
def matches(match_id, date_from, date_to, status):
    pass

@click.command()
@click.option('--id', '-i', 'area_id', help='displays area with this id')
def areas(area_id):
    pass

@click.command()
@click.option('--id', '-i', 'team_id', help='displays team with this id')
@click.option('--matches', '-m',is_flag=True, help='matches where team with given id played')
@click.option('--from', '-f', 'date_from', help='display matches in which team with given id played from this date')
@click.option('--to', '-t', 'date_to', help='display matches in which team with given id played to this date')
@click.option('--venue', '-v',  help='display matches in which team with given id played in the given venue')
@click.option('--status', '-s', help='display matches in which team with given id played that have this status')
@click.option('--limit', '-l', 'date_from', help='display limit matches in which team with given id played ')
def teams(team_id,venue, status, limit, matches, date_from, date_to,):
    pass


main.add_command(competitions)
main.add_command(players)
main.add_command(teams)
main.add_command(matches)
main.add_command(areas)


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
