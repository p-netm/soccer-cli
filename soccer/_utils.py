"""holds more esoteric function tools that encapsulate more advanced click oopertions"""
import click
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



global_click_option = [
        click.option('--stdout', 'output_format', flag_value='stdout', default=True,
                      help="Print to stdout."),
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


class CustomMultiGroup(click.Group):

    def group(self, *args, **kwargs):
        """Behaves the same as `click.Group.group()` except if passed
        a list of names, all after the first will be aliases for the first.
        """
        def decorator(f):
            aliased_group = []
            if isinstance(args[0], list):
                # we have a list so create group aliases
                _args = [args[0][0]] + list(args[1:])
                for alias in args[0][1:]:
                    grp = super(CustomMultiGroup, self).group(
                        alias, *args[1:], **kwargs)(f)
                    grp.short_help = "Alias for '{}'".format(_args[0])
                    aliased_group.append(grp)
            else:
                _args = args

            # create the main group
            grp = super(CustomMultiGroup, self).group(*_args, **kwargs)(f)

            # for all of the aliased groups, share the main group commands
            for aliased in aliased_group:
                aliased.commands = grp.commands

            return grp

        return decorator