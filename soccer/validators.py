"""provide validator callbacks for filter options"""

#****Pending stages and groupings validator****


import re
from click import BadParameter
from datetime import datetime


def check_in(option, value, enums):
    value = value.upper()
    if value in enums: return value
    else: raise BadParameter('{} values only include [{}]'.format(option, " | ".join(enums)))


def validate_matchday(ctx, param, value):
    """
    format from api: Integer /[1-4]+[0-9]*/
    :param value: [str] matchday
    """
    regex = r'^[1-4]+[0-9]*&'
    try:
        if re.search(regex, value):
            return int(value)
    except ValueError:
        raise BadParameter('unexpected value for matchday')


def validate_season(ctx, param, value):
    """
    format from api: String /YYYY/;
    :param value: [str] season year of play
    :return: str(value) or raise error
    """
    try:
        if int(value) > 1848 and len(value < 5):
            return value
    except ValueError:
        raise BadParameter('unexpected value for season')


def validate_status(ctx, param, value):
    """
    :param value: [str] status of match
    :return: value or error
    api format: 	Enum /[A-Z]+/
    """
    enums = ['SCHEDULED', 'LIVE', 'IN_PLAY', 'PAUSED', 'FINISHED', 'POSTPONED', 'SUSPENDED', 'CANCELED', 'AWARDED']
    return check_in('Status', value, enums)


def validate_venue(ctx, param, value):
    """
    :param value: [str] venue of play
    :return: value or error
    api format: 	Enum /[A-Z]+/
    """
    enums = ['HOME', 'AWAY']
    return check_in('Venue', value, enums)


def validate_date(ctx, param, value):
    """
    :param value: hyphen delimited date values
    :return: str()
    api format: String /YYYY-MM-dd/
    """
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return value
    except ValueError:
        raise BadParameter('unexpected value for range')


def validate_stage(ctx, param, value):
    """
    :param value: [str]
    :return:
    api format: String /[A-Z]+/
    """
    return value


def validate_plan(ctx, param, value):
    """
    :param value: [str]
    :return: one of available plans
    api format: String /[A-Z]+/
    """
    enums = ['TIER_ONE', 'TIER_TWO', 'TIER_THREE', 'TIER_FOUR']
    return check_in('Plan', value, enums)


def validate_competitions(ctx, param, value):
    """
    :param value: [list]
    :return: list
    api format: String /\d+,\d+/
    """
    regex = r'\d+'
    for _id in value:
        if not re.search(regex, _id):
            raise BadParameter('{} : unexpected value for competitions ids'.format(_id))
    return list(value)


def validate_group(ctx, param, value):
    """
    :param value: [str]
    :return:
    competition groupings filter validator
    api format = String /[A-Z]+/
    """
    return value


def validate_limit(ctx, param, value):
    """
    :param value: [str]
    :return: [int(value) or error]
    api format: Integer /\d+/
    """
    try:
        return int(value)
    except ValueError:
        raise BadParameter('Limit can only be integer')


def validate_standing(ctx, param, value):
    """
    :param value: [str]
    :return: value or error
    """
    enums = ['TOTAL', 'HOME', 'AWAY']
    return check_in('StandingType', value, enums)