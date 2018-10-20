"""
There are a few names that are shared between resources and subresources, and thus to be
able to nest cli commands for such commands i found i had to introduce an additional namespace, that
helps differentiate between a command to a resource, and  a command to a subresource
"""

import click
from validators import *
from request_handler import RequestHandler

def create_payload(**kwargs):
    """
    :param kwargs: key value pairs entry's for parameters to be appended into the query string
    :return: payload dictionary
    """
    payload = {}
    payload.update({'dateFrom':kwargs['date_from']}) if kwargs.get('date_from') else payload.update({})
    payload.update({'dateTo':kwargs['date_to']}) if kwargs.get('date_to') else payload.update({})
    payload.update({'status':kwargs['status']}) if kwargs.get('status') else payload.update({})
    payload.update({'matchday':kwargs['matchday']}) if kwargs.get('matchday') else payload.update({})
    payload.update({'group':kwargs['group']}) if kwargs.get('group') else payload.update({})
    payload.update({'season':kwargs['season']}) if kwargs.get('season') else payload.update({})
    payload.update({'stage':kwargs['stage']}) if kwargs.get('stage') else payload.update({})
    payload.update({'limit':kwargs['limit']}) if kwargs.get('limit') else payload.update({})
    payload.update({'competitions':kwargs['competitions']}) if kwargs.get('competitions') else payload.update({})
    payload.update({'venue':kwargs['venue']}) if kwargs.get('venue') else payload.update({})
    return payload

request_handler = RequestHandler()



global_click_option = [
        click.option('--stdout', 'output_format', flag_value='stdout', default=True,
                      help="Print to stdout."),
        click.option('--csv', 'output_format', flag_value='csv',
                      help='Output in CSV format.'),
        click.option('--json', 'output_format', flag_value='json',
                      help='Output in JSON format.'),
        click.option('-o', '--output-file', default=None,
                      help="Save output to a file (only if csv or json option is provided).")
    ]

time_click_option = [
        click.option('--use12hour', is_flag=True, default=False,
                      help="Displays the time using 12 hour format instead of 24 (default).")]

list_click_option = [
        click.option('--list', 'listcodes', is_flag=True,
              help='list codes and names of all available competitions')
    ]

def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options





@click.command()
@add_options(global_click_option)
@click.option('--season', callback=validate_season,
              help=' list  teams in a particular competition for given season')
@click.option('--stage',
              help=' filters teams in a competitions with the given id to given stage')
@click.pass_context
def teams(ctx, season, stage, output_format, output_file,):
    """Subresource for teams within competitions """
    # /v2/competitions/{id}/teams
    if not ctx.obj.get('competition_id'):
        click.secho('You have to provide a competition id', fg='red', bold=True)
        return
    else:
        url = ctx.obj['url'] + 'teams'
        payload = create_payload(season=season, stage=stage)
        response = request_handler.get(url, headers=ctx.obj['headers'], params=payload)
        return response



@click.command()
@add_options(global_click_option)
@add_options(time_click_option)
@click.option('--from', '-f', 'date_from', callback=validate_date,
              help='list matches for competition with given id from given date')
@click.option('--to', '-t', 'date_to', callback=validate_date,
              help='list matches for competition with given id to given date')
@click.option('--status', callback=validate_status,
              help='filter matches for competition with given id to status of play')
@click.option('--matchday', callback=validate_matchday,
              help='filter matches for competition with given id to given matchday')
@click.option('--group',
              help='filter matches for competition with given id to given group')
@click.option('--season', callback=validate_season,
              help='list matches in a particular competition for given season')
@click.option('--stage',
              help='filters matches of given competition id to given stage')
@click.pass_context
def matches(ctx, date_from, date_to, status, matchday, group, season, stage,
            use12hour, output_format, output_file,):
    """subresource of matches within competitions"""
    if not ctx.obj.get('competition_id'):
        click.secho('You have to provide a competition id', fg='red', bold=True)
        return
    else:
        url =  ctx.obj['url'] + 'matches'
        payload = create_payload(date_from=date_from, date_to=date_to, status=status, matchday=matchday, group=group,
                                 season=season, stage=stage)
        response = request_handler.get(url, headers=ctx.obj['headers'], params=payload)
        return response