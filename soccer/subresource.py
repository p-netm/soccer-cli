"""
There are a few names that are shared between resources and subresources, and thus to be
able to nest cli commands for such commands i found i had to introduce an additional namespace, that
helps differentiate between a command to a resource and  a command to a subresource
"""

import click
from .validators import *

@click.command()
@click.option('--season', callback=validate_season,
              help='[teams, matches]:: list matches, and teams in a particular competition for given season')
@click.option('--stage', help='[teams, matches]:: filters either teams or matches to given stage')
def teams(season, stage):
    print(season, stage)


@click.command()
@click.option('--from', '-f', 'date_from', callback=validate_date,
              help='list matches for competition with given id from given date')
@click.option('--to', '-t', 'date_to', callback=validate_date,
              help='list matches for competition with given id to this given day')
@click.option('--status', callback=validate_status,
              help='filter matches for competition with given id to status of play')
@click.option('--matchday', callback=validate_matchday,
              help='filter matches for competition with given id to given matchday')
@click.option('--group',
              help='filter matches for competition with given id to given group')
@click.option('--season', callback=validate_season,
              help='list matches, and teams in a particular competition for given season')
@click.option('--stage', help='[ matches]:: filters either teams or matches to given stage')
def matches(date_from, date_to, status, matchday, group, season, stage):
    pass


