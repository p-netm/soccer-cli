"""
There are a few names that are shared between resources and subresources, and thus to be
able to nest cli commands for such commands i found i had to introduce an additional namespace, that
helps differentiate between a command to a resource and  a command to a subresource
"""

import click
from .validators import *
from .request_handler import RequestHandler

@click.command()
@click.option('--season', callback=validate_season,
              help=' list  teams in a particular competition for given season')
@click.option('--stage',
              help=' filters teams in a competitions with the given id to given stage')
@click.pass_context
def teams(ctx, season, stage):
    """Subresource for teams within competitions """
    # /v2/competitions/{id}/teams
    if not ctx.obj.get('competition_id'):
        click.secho('You have to provide a competition id', fg='red', bold=True)
        return
    else:
        url = ctx.obj['url'] + 'teams'
        payload = {}
        if season:
            payload['season'] = season
            payload['stage'] = stage
        return RequestHandler._get(url, headers=ctx.obj['headers'], params=payload)



@click.command()
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
def matches(ctx, date_from, date_to, status, matchday, group, season, stage):
    if not ctx.obj.get('competition_id'):
        click.secho('You have to provide a competition id', fg='red', bold=True)
        return
    else:
        url =  ctx.obj['url'] + 'matches'
        payload = {}
        if date_from:
            payload['dateFrom'] = date_from
        if date_to:
            payload['dateTo'] = date_to
        if status:
            payload['status'] = status
        if matchday:
            payload['matchday'] = matchday
        if group:
            payload['group'] = group
        if season:
            payload['season'] = season
        if stage:
            payload['stage'] = stage
        return RequestHandler._get(url, headers=ctx.obj['headers'], params=payload)