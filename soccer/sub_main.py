"""
There are a few names that are shared between resources and subresources, and thus to be
able to nest cli commands for such commands i found i had to introduce an additional namespace, that
helps differentiate between a command to a resource, and  a command to a subresource
"""

import click, json
try:
    from soccer.validators import *
    from soccer.request_handler import RequestHandler
    from soccer.writers import get_writer
    from soccer._utils import *
    from soccer.resources import Soccer
except ImportError as error:
    from validators import *
    from request_handler import RequestHandler
    from writers import get_writer
    from _utils import *
    from resources import Soccer


request_handler = RequestHandler()
soccer = Soccer()


@click.command()
@add_options(global_click_option)
@click.option('--season', callback=validate_season,
              help=' list  teams in a particular competition for given season')
@click.option('--stage',
              help=' filters teams in a competitions with the given id to given stage')
@click.pass_context
def teams(ctx, season, stage, output_format, output_file):
    """Subresource for teams within competitions """
    # /v2/competitions/{id}/teams
    comp_id = ctx.obj.get('competition_id')
    if not comp_id:
        click.secho('Aborted!, You have to provide a competitions id', fg='red', bold=True)
        return
    else:
        payload = create_payload(season=season, stage=stage)
        response = soccer.competitions(comp_id).teams.query.filter(payload).click_get()
        writer = get_writer(output_format, output_file)
        if response: writer.write_teams(response)
        return



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
            use12hour, output_format, output_file):
    """subresource of matches within competitions"""
    comp_id = ctx.obj.get('competition_id')
    if not comp_id:
        click.secho('Aborted!, You have to provide a competition id', fg='red', bold=True)
        return
    else:
        payload = create_payload(date_from=date_from, date_to=date_to, status=status, matchday=matchday, group=group,
                                 season=season, stage=stage)
        response = soccer.competitions(comp_id).matches.query.filter(payload).click_get()
        writer = get_writer(output_format, output_file)
        if response: writer.write_matches(response, use_12_hour_format=use12hour)
