import os
import sys
import json
import click

try:
    from soccer.validators import *
    from soccer.sub_main import teams as Teams, matches as Matches
    from soccer._utils import *
    from soccer.request_handler import RequestHandler
    from soccer.writers import get_writer
    from soccer.resources import Soccer
except ImportError as error:
    from validators import *
    from sub_main import teams as Teams, matches as Matches
    from _utils import *
    from request_handler import RequestHandler
    from writers import get_writer
    from resources import Soccer

request_handler = RequestHandler()
soccer = Soccer()

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

@click.group(invoke_without_command=True)
@click.option('--apikey', default=load_config_key,
              help="API key to use.")
@click.pass_context
def main(ctx, apikey):
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
    if ctx.obj is None:
        ctx.obj = {}
    headers = {'X-Auth-Token': apikey}
    ctx.obj['headers'] = headers


@main.group(invoke_without_command=True)
@add_options(global_click_option)
@click.option('--id', '-i', 'competition_id', type=click.INT,
              help='id for the competitions to load, if no id: returns all available competitions')
@click.option('--areas',
              help='filters competition to particular area')
@click.option('--plan', callback=validate_plan,
              help='filters and shows competitions for a particular plan')
@click.pass_context
def competitions(ctx, competition_id, areas, plan, output_format, output_file):
    """Competitions Resource Endpoint"""
    payload = create_payload(areas=areas, plan=plan)
    if ctx.invoked_subcommand is None:
        # dealing with the resource only, no subresources, add id
        response = soccer.competitions(competition_id).query.filter(payload).click_get()
        writer = get_writer(output_format, output_file)
        if response:
            writer.write_competitions(response)
        return
    else:
        ctx.obj['competition_id'] = competition_id


@competitions.command()
@add_options(global_click_option)
@click.option('--standingtype',callback=validate_standing, default='TOTAL',
              help='[standings]:: show standings for a particular competition ')
@click.pass_context
def standings(ctx, standingtype, output_format, output_file):
    """
    Standings subresource for the competitions resource, only accessed and works
    if a competition id is present
    """
    comp_id = ctx.obj.get('competition_id')
    if not comp_id:
        click.secho('Aborted!, You have to provide a competition id', fg='red', bold=True)
        return
    else:
        payload = {'standingType':standingtype} if standingtype else {}
        response = soccer.competitions(comp_id).standings.query.filter(payload).click_get()
        writer = get_writer(output_format, output_file)
        if response:
            writer.write_standings(response)


@competitions.command()
@add_options(global_click_option)
@click.pass_context
@click.option('--limit', '-l', callback=validate_limit,
              help='limit number of records')
def scorers(ctx, limit, output_format, output_file):
    """Scorers subresource for competitions resource"""
    comp_id = ctx.obj.get('competition_id')
    if not comp_id:
        click.secho('Aborted!, You have to provide a competition id', fg='red', bold=True)
        return
    else:
        payload = create_payload(limit=limit)
        response = soccer.competitions(comp_id).scorers.query.filter(payload).click_get()
        writer = get_writer(output_format, output_file)
        if response:
            writer.write_scorers(response)
        return

@main.command()
@add_options(global_click_option)
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
def players(ctx, player_id, matches, date_from, date_to, competitions, status, limit, output_format, output_file):
    """Players Resource Endpoint"""
    if not player_id:
        click.secho("Aborted!, Please provide a specific player's id", fg='red', bold=True)
        return
    writer = get_writer(output_format, output_file)
    writer_func = writer.write_players
    payload = {}
    if any([limit, status, competitions, date_to, date_from]) and not matches:
        click.secho('Aborted!, seems like you forgot to provide the --matches flag, you need that,'
                    'to be able to add filters', fg='red')
        return
    if matches:
        payload = create_payload(date_from=date_from, date_to=date_to, competitions=competitions, status=status,
                                 limit=limit)
        writer_func = writer.write_matches
        response = soccer.players(player_id).matches.query.filter(payload).click_get()
    response = soccer.players(player_id).query.click_get()
    if response:
        writer_func(response)
    return


@main.command()
@add_options(global_click_option)
@add_options(time_click_option)
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
def matches(ctx, match_id, date_from, date_to, status, competitions, use12hour, output_format, output_file):
    """Matches Resource Endpoint"""
    payload = create_payload(date_from=date_from, date_to=date_to, competitions=competitions, status=status)
    response = soccer.matches(match_id).query.filter(payload).click_get()
    writer = get_writer(output_format, output_file)
    if response: writer.write_matches(response, use12hour)
    return


@main.command()
@add_options(global_click_option)
@click.option('--id', '-i', 'area_id', type=click.INT,
              help='display area info with this id')
@click.pass_context
def areas(ctx, area_id, output_format, output_file):
    """Areas Resource Endpoint"""
    response = soccer.areas(area_id).query.click_get()
    writer = get_writer(output_format, output_file)
    if response: writer.write_areas(response)
    return


@main.command()
@add_options(global_click_option)
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
              help='enforce a limit on the number of match records that should be returned for this team')
@click.pass_context
def teams(ctx, team_id, venue, status, limit, matches, date_from, date_to, output_format, output_file):
    """Teams Resource Endpoint"""
    writer = get_writer(output_format, output_file)
    writer_func = writer.write_teams
    payload = {}
    if any([venue, status, limit, date_from, date_to]) and not matches:
        click.secho('Aborted!, seems like you forgot to provide the --matches flag, you need that'
                    ' to be able to add filters', fg='red')
        return
    if matches:
        payload = create_payload(date_from=date_from, date_to=date_to, venue=venue, status=status, limit=limit)
        writer_func = writer.write_matches
        response = soccer.teams(team_id).query.filter(payload).click_get()
    response = soccer.teams(team_id).query.click_get()
    if response: writer_func(response)

competitions.add_command(Teams)
competitions.add_command(Matches)

if __name__ == '__main__':
    main(obj={})
