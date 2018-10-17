import os
import sys
import json
import click

from .validators import validate_standing, validate_limit, validate_competitions, validate_venue, validate_status,\
    validate_season, validate_matchday, validate_plan, validate_date
import subresource as sr

from leaagueids import LEAGUE_IDS
from exceptions import IncorrectParametersException
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


@click.group()
@click.option('--apikey', default=load_config_key,
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
@click.option('--list', 'listcodes', is_flag=True,
              help='list codes and names of all available competitions')
@click.pass_context
def main(ctx, apikey, use12hour, output_format, output_file, list):
    """
    A CLI for live and past football scores from various football leagues.
    resources are given as commands and subresources and their filters as options

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
    ctx.obj['headers'] = headers


@click.group(invoke_without_command=True)
@click.option('--id', '-i', 'competition_id', type=click.INT,
              help='id for the competitions to load, if no id: returns all available competitions')
@click.option('--areas',
              help='filters competition to particular area')
@click.option('--plan', callback=validate_plan,
              help='filters and shows competitions for a particular plan')
@click.pass_context
def competitions(ctx, competition_id, listcodes, areas, plan):
    """Serves as an entry point to the Competitions Resource"""
    url = 'competitions/{}'.format(competition_id) if competition_id else 'competitions/'
    payload = {}  # hold the filters
    if areas:
        payload['areas'] = areas
    if plan:
        payload['plan'] = plan
    if ctx.invoked_subcommand is None:
        # dealing with the resource only, no subresources, add id
        response = RequestHandler._get(url, headers=ctx.obj['headers'], params=payload)
        click.secho(response.json(), fg='blue', bold=True)
        return
    else:
        ctx.obj['url'] = url
        ctx.obj['competition_id'] = competition_id


@click.command()
@click.option('--standingtype',callback=validate_standing,
              help='[standings]:: show standings for a particular competition ')
@click.pass_context
def standings(ctx, standingtype):
    """
    This is the Standings subresource for the competitions resource, only accessed and works
    if a competition id is present
    """
    if not ctx.obj.get('competition_id'):
        click.secho('You have to provide a competition id', fg='red', bold=True)
        return
    else:
        url = ctx.obj['url'] + 'standings'
        payload = {'standingType':standingtype} if standingtype else {}
        RequestHandler._get(url, headers=ctx.obj['headers'], params=payload)


@click.command()
@click.option('--id', '-i', 'player_id', type=click.INT,
              help='displays player info with this id, absent id will return a 404')
@click.option('--matches', '-m',is_flag=True, help='matches where player with given id played')
@click.option('--from', '-f', 'date_from', callback=validate_date,
              help='display matches in which player with given id played from this date')
@click.option('--to', '-t', 'date_to', callback=validate_date,
              help='display matches in which player with given id played to this date')
@click.option('--competitions', '-c', multiple=True, callback=validate_competitions,
              help='display matches in which player with given id played that belong to this competition')
@click.option('--status', '-s', callback=validate_status,
              help='display matches in which player with given id played that have this status')
@click.option('--limit', '-l', callback=validate_limit,
              help='display limit matches in which player with given id played ')
@click.pass_context
def players(ctx, player_id, matches, date_from, date_to, competitions, status, limit):
    url = 'players/{}'.format(player_id) if player_id else 'players/'
    url += 'matches' if matches else ''
    if matches:
        payload = {}
        if date_from:
            payload['dateFrom'] = date_from
        if date_to:
            payload['dateTo'] = date_to
        if competitions:
           payload['competitions'] = competitions
        if status:
            payload['status'] = status
        if limit:
            payload['limit'] = limit
    if any([limit, status, competitions, date_to, date_from]) and not matches:
        click.secho('seems like you forgot to provide the --matches flag, you need that,'
                    'to be able to add filters', fg='red')
    response = RequestHandler._get(url, headers=ctx.obj['headers'], params=payload)
    return response


@click.command()
@click.option('--id', '-i', 'match_id', type=click.INT,
              help='displays matches with this id',)
@click.option('--from', '-f', 'date_from', callback=validate_date,
              help='display matches played from this date')
@click.option('--to', '-t', 'date_to', callback=validate_date,
              help='display matches played to this date')
@click.option('--competitions', '-c', multiple=True, callback=validate_competitions,
              help='display matches that belong to competition with given id')
@click.option('--status', '-s', callback=validate_status,
              help='display matches  that have this status')
@click.pass_context
def matches(ctx, match_id, date_from, date_to, status):
    url = 'matches/{}'.format(match_id) if match_id else 'matches'
    payload = {}
    if date_from:
        payload['dateFrom'] = date_from
    if date_to:
        payload['dateTo'] = date_to
    if competitions:
        payload['competitions'] = competitions
    if status:
        payload['status'] = status
    response = RequestHandler._get(url, headers=ctx.obj['headers'], params=payload)
    return response


@click.command()
@click.option('--id', '-i', 'area_id', type=click.INT,
              help='display area info with this id')
@click.pass_context
def areas(ctx, area_id):
    url = 'areas/{}'.format(area_id) if area_id else 'areas'
    response = RequestHandler._get(url, headers=ctx.obj['headers'])
    return response


@click.command()
@click.option('--id', '-i', 'team_id', type=click.INT,
              help='displays team info with this id')
@click.option('--matches', '-m', is_flag=True, help='matches where team with given id played')
@click.option('--from', '-f', 'date_from', callback=validate_date,
              help='display matches in which team with given id played from this date')
@click.option('--to', '-t', 'date_to', callback=validate_date,
              help='display matches in which team with given id played to this date')
@click.option('--venue', '-v', callback=validate_venue,
              help='display matches in which team with given id played in the given venue')
@click.option('--status', '-s', callback=validate_status,
              help='display matches in which team with given id played that have this status')
@click.option('--limit', '-l', callback=validate_limit,
              help='display limit matches in which team with given id played ')
@click.pass_context
def teams(ctx, team_id, venue, status, limit, matches, date_from, date_to,):
    pass

competitions.add_command(sr.teams)
competitions.add_command(sr.matches)
main.add_command(competitions)
main.add_command(players)
main.add_command(teams)
main.add_command(matches)
main.add_command(areas)


if __name__ == '__main__':
    main(obj={})
