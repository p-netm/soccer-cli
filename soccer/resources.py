"""
An interface for users who may wish to use object dot notation in traversing and querying the API
all responses will be returned as json unless where the has been specific arguments suggesting
 the use of the writers. this module is an answer to a developer or anyone who may want to make api calls
 inside of his own code

 NB: this module does not cushion users from creating possible erroneous API requests. This will then return
 the resultant error message as it is from the API
"""

import click

try:
    from soccer.request_handler import RequestHandler
    from soccer.exceptions import ApiKeyError, APIErrorException
except ImportError as error:
    from request_handler import RequestHandler
    from exceptions import ApiKeyError, APIErrorException
import os, sys

RH = RequestHandler()


def load_config_key():
    """Load API key from config file"""
    global api_token
    try:
        api_token = os.environ['SOCCER_CLI_API_TOKEN']
    except KeyError:
        home = os.path.expanduser("~")
        config = os.path.join(home, ".soccer-cli.ini")
        key = ''
        if os.path.exists(config):
            with open(config, "r") as cfile:
                key = cfile.read()
        if key:
            api_token = key
        else:
            os.remove(config)  # remove 0-byte file
            raise ApiKeyError('No API Token detected. '
                        'Please visit {0} and get an API Token, '
                        'make sure your key is exported into your environ using the key'
                        '<SOCCER_CLI_API_TOKEN>'
                        .format(RequestHandler.BASE_URL))
    return api_token

class Query(object):
    """Manage filtering and the actual sending of http commands"""
    def __init__(self, url=''):
        self.url = url
        self.headers = {}
        self.headers['X-Auth-Token'] = load_config_key()
        self.payload = {}

    def filter(self, payload):
        self.payload = payload
        return self

    def get(self):
        return RH._get(self.url, headers=self.headers, params=self.payload)

    def click_get(self):
        """To be used by the command line interface such that it will write the error minus
        the stack trace whan an error is thrown"""
        try:
            return RH._get(self.url, headers=self.headers, params=self.payload)
        except ConnectionError:
            click.secho('Seems like there is a problem with your connection', fg='red', bold=True)
            return
        except APIErrorException as error:
            click.secho(str(error), fg='red', bold=True)
            return
        except Exception as err:
            click.secho(err.args[0], fg='red', bold=True)
            return


class Competitions(object):
    """Manages the competitions resource endpoint
    Sample Commands:
        >>>from soccer.resources import Competitions
        >>>data = competitions().query.filter(areas=2072, plan=TIER_ONE).get()
        >>>data
        >>> # get the competitions with id 2021
        >>>Competitions(2021).query.get()
        """
    def __init__(self, _id):
        self.query_uri = 'competitions/{}'.format(_id) if _id else 'competitions'
        self.query = Query(self.query_uri)

    @property
    def standings(self):
        """
        get the home standings of any particular competition eg epl whose id is 2021
        >>>Competitions(2021).standings.query.filter(standingType='HOME').get()
        """
        self.query.url = self.query_uri + '/' + 'standings'
        return self

    @property
    def scorers(self):
        """
        represents the scorers subresource within the competitions resource
        sample commands:
        >>> Competitions(2021).scorers.query.get()
        >>> Competitions(2021).scorers.query.filter(limit=20).get()
        """
        self.query.url =self.query_uri + '/' + 'scorers'
        return self

    @property
    def matches(self):
        """
        represents the matches subresource within the Competitions resource
        :Sample:
        >>> Competitions(2021).matches.query.get()
        You can also add filters to the matches query, refer to the api documentation
        https://www.football-data.org for available filter options
        """
        self.query.url = self.query_uri + '/' + 'matches'
        return self

    @property
    def teams(self):
        """
        Represents the teams subresouce within the Competitions resource
        :sample:
        >>> Competitions.teams.query.filter(season=2017).get()
        """
        self.query.url = self.query_uri + '/' + 'teams'
        return self

class Matches(object):
    """Matches Resource Endpoint
    >>> from soccer.resources import Matches
    >>> Matches().query.get()  # gets a bunch of random matches
    >>> Matches(57).query.get()  # gets the match with the id 57
    """
    def __init__(self, _id):
        self.query_uri = 'matches/{}'.format(_id) if _id else 'matches'
        self.query = Query(self.query_uri)

class Players(object):
    """
    Resource : players
    :sample code:
    >>> from soccer.resources import Players
    >>> Players(1).query.get() # get the player with id 1
    """
    def __init__(self, _id):
        self.query_uri = 'players/{}'.format(_id) if _id else 'players'
        self.query = Query(self.query_uri)

    @property
    def matches(self):
        """
        Subresource: Players.matches
        queries the matches endpoint subjective to the presence of certain player
        :sample code:
        >>> Players(1).matches.query.filter(status='CANCELLED').get()
        """
        self.query.url = self.query_uri + '/' + 'matches'
        return self

class Areas(object):
    """
    Resource : Areas endpoint
    :sample code:
    >>> from soccer.resources import Areas
    >>> Areas().query.get()  # gets all the areas
    """
    def __init__(self, _id):
        self.query_uri = 'areas/{}'.format(_id) if _id else 'areas'
        self.query = Query(self.query_uri)

class Teams(object):
    """
    Resource : Teams endpoint
    :sample usage:
    >>> from soccer.resources import Teams
    >>> Teams().query.get()
    """
    def __init__(self, _id):
        self.query_uri = 'teams/{}'.format(_id) if _id else 'teams'
        self.query = Query(self.query_uri)

    @property
    def matches(self):
        """
        Subresource: Teams.matches endpoint
        >>> Teams(1).matches.query.get()
        >>> Teams(1).matches.filter(venue="HOME").get()
        """
        self.query.url = self.query_uri + '/' + 'matches'
        return self



class Soccer(object):
    """
    An abstract factory class for building the required endpoint classes
    The recommended wy of initilising the enpoint query objects i.e
    >>> from soccer.resources import Soccer
    >>> leagues = Soccer.competitions()
    >>> leagues.query.get()
    >>> # or if you would like to filter legues within the england area
    >>> leagues.filter(areas=2072).get()
    """
    def __init__(self):
        pass

    def competitions(self, _id=None):
        return Competitions(_id=_id)

    def matches(self, _id=None):
        return Matches(_id=_id)

    def players(self, _id=None):
        return Players(_id=_id)

    def areas(self, _id):
        return Areas(_id=_id)

    def teams(self, _id=None):
        return Teams(_id=_id)
