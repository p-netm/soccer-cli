
Soccer CLI
=====

[![PyPI version](https://badge.fury.io/py/soccer-cli.svg)](http://badge.fury.io/py/soccer-cli) [![Join the chat at https://gitter.im/architv/soccer-cli](https://badges.gitter.im/architv/soccer-cli.svg)](https://gitter.im/architv/soccer-cli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Soccer for Hackers - a CLI for all the football scores. 

![](https://github.com/p-netm/imgandvid/blob/master/soccercli/pics/competitionsstandings2021.PNG)
![](https://github.com/p-netm/imgandvid/blob/master/soccercli/pics/competitionsstandings2001.PNG)

Install
=====

An API key from [football-data.org](http://api.football-data.org/) will be required and you can register for one [here](http://api.football-data.org/client/register).

### Using `pip`

```bash
$ pip install soccer-cli
```

Set your API key in an environment variable `SOCCER_CLI_API_TOKEN`

For example:

```bash
export SOCCER_CLI_API_TOKEN="<YOUR_API_TOKEN>"
```

### Build from source

```bash
$ git clone https://github.com/architv/soccer-cli.git
$ cd soccer-cli
$ python setup.py install
```

You can set the API key using an environment variable as shown above or create a file `.soccer-cli.ini` in your home folder (`/home/username/.soccer-cli.ini`) that contains only your API token, such that:

```bash
$ cat /home/username/.soccer-cli.ini
<YOUR_API_TOKEN>
```

#### Note:
Currently supports Linux, Mac OS X, NetBSD, FreeBSD and Windows.

To get colorized terminal output on Windows, make sure to install [ansicon](https://github.com/adoxa/ansicon/releases/latest) and [colorama](https://pypi.org/project/colorama/).

Specifically for the Windows terminal, by default the terminal may be limited in size(width) even when enlarged,
However, this can be dealt with by running the commands
> mode 800
for more info. please check this [stackoverflow post](https://superuser.com/questions/285984/how-do-i-full-screen-my-cmd)

<hr>

Usage
====

<details>
  <summary>Competition Resource commands </summary>
  
  ##### get all competitions
  ```bash
  $ soccer competitions
  ```
  
   filters: areas, and plans
  
  ###### areas
  
  ```bash
  $ soccer competitions --areas 2072 #  2072 is england's area id
  ```
  
  ###### plan(payment pLAN)
  
  usually if you are not subscribed to any premium plans, you'r requests will be automatically handled as TIER_ONE
  
  ```bash
  $soccer competitions --plan TIER_ONE # TIER_ONE has access to 14 competitions
  ``` 
  
  <hr>
  
  ##### get specific competition/league info
  
  ```bash
  $ soccer competitions --id 2021 standings # 2021 is the competition id for English Premier League
  ```
  
  <hr>
  
  ##### get teams in a certain competition(league)
  
  ```bash
  $ soccer competitions --id 2021 teams
  ```
  
  filters: season and stage
  
  ###### season
  
  ```bash
  $ soccer competitions --id 2021 teams --season 2017 # season is the year that the league starts in
  ```
  
  ###### stage
  
  ```bash
  $ soccer competitions --id 2021 teams --stage <stage>
  ```
  
  <hr>
  
  ##### get a specific competition's standings
  
  ```bash
  $ soccer competitions --id 2021 standings
  ```
  
  filters: standingtype
  
  ###### standingtType as standingtype
  
  ```bash
  $ soccer competitions --id 2021 standings --standingtype HOME
  ```
  
  the standing types are case insesitive when fed in through the shell otherwise should be strictly upper.
  
  <hr>
  
  #### get a specific competition's matches
  
  ```bash
  $ soccer competitions --id 2021 matches
  ```
  
  filters : dates(from and to), stage, status, matchday, group, and season
  
  ###### dates 
  
  ```bash
  $ soccer competitions --id 2021 matches --from 2018-10-18 --to 2018-10-20
  ```
  
  ###### status
  
  Can use this to get the live matches within a certain competition
  ```bash
  $ soccer competitions --id 2021 matches --status LIVE
  ```
  
  _hope you get the idea and can comfortably use the other filters and a combination of any
  to specify your query_
  
  <hr>
  
  #### get scorers within a competition
  
  ```bash
  $ soccer competition --id 2021 scorers
  $ soccer competition --id 2021 scorers --limit 20 # to get info on the top 20 scorers of the English premier league
  ```
  
  <hr>
</details>

<details>
<summary> Team resource commands </summary>
     
  #### specific team info
  
  ```bash
  $ soccer teams --id <id> 
  ```
  
  #### Matches subresource
  
  used to get match records on which team of given id participated in
  
  ```bash
  $ soccer teams --id 66 matches  #  66 happens to be Manchester United's team id
  ```
  
  ###### filters : dates(from and to), status, venue, limit
  
  ```bash
  $ soccer teams --id 66 matches --from 2018-09-23 --to 2018-10-01
  $ soccer teams --id 66 matches --status CANCELLED
  $ soccer teams --id 66 matches --venue <venue>
  ```
  
  <hr>
</details>

<details>
<summary> Match Resource commands </summary>
  
  #### Get upcoming fixtures
  
  ```bash
  $ soccer matches --status SCHEDULED
  ```
  
  #### all mathes and specific match
  
  ```bash
  $ soccer matches
  $ soccer matches --id <match_id>
  ```
  
  ##### Match resource fillters : competitions, dates, status
  
  ```bash
  soccer matches --competitions 2000 # world cup matches
  soccer matches --competitions 2021 --competitions 2000 #Request for matches from 2 competitions
  ```
  
  <hr>
</details>

<details>
<summary> Player Resource commands </summary>

  #### get specific player info

  ```bash
  $ soccer players --id  <id> # <id> is the id of player of interest
  ```
  
  #### get matches that player played in
  
  ```bash
  $ soccer players --id <player_id> 
  ```
  
  ###### filters : dates(from and to), status, competitions/leagues, limit
  
  ```bash
  $ soccer players --id 1 --competitions 2021 --status FINISHED 
  ```
  
  <hr>
</details>

<details>
<summary> Areas Resource commands </summary>
  
  #### get area info
  
  ```bash
  $ soccer areas # retrieves info for all areas in api
  $ soccer areas --id 2000 # retrieves info WC whose id is 2000
  ```
  
  <hr>
</details>


### Help
```bash
$ soccer --help
```

### List of supported leagues and their league codes

- Europe:
  - CL: Champions League
- England:
  - PL: Premier League
  - EL1: League One
- France:
  - FL: Ligue 1
  - FL2: Ligue 2
- Germany:
  - BL: Bundesliga
  - BL2: 2. Bundesliga
  - BL3: 3. Liga
- Italy:
  - SA: Serie A 
- Netherlands:
  - DED: Eredivisie
- Portugal:
  - PPL: Primeira Liga
- Spain:
  - LLIGA: La Liga
  - SD: Segunda Division
_And upto 131+ more competitions oferred by the API, supports all competitions offered by the api_ 


### Tests

To run testing suite from root of repo

```bash
$ python -m unittest discover tests
```

To run specific test file (in this case the tests in test_request_handler.py)

```bash
$ python -m unittest tests.test_request_handler
```


Todo
====
- [ ] replace demo sections
- [ ] add how to get ids section
- [ ] integrate the writer with updated code
- [ ] add a developer interface : to use dot notation and direct method calls as opposed to cli
- [ ] id listing
- [ ] predictive analytical statistics
- [ ] Enable cache
- [ ] Add more test cases
- [ ] Add fixtures for UEFA Champions League
- [x] Add league filter for live scores
- [ ] Color coding for Europa league and differentiation between straight CL and CL playoff spots, and the same for EL spots
- [ ] Add support for team line up
- [ ] A built in watch feature so you can run once with --live and just leave the program running.

Licence
====
Open sourced under [MIT License](LICENSE)

Contributions
====
This is one of the simplest projects out here on github and it does require lots of help
so feel free to branch out and send  pull request, or raise any issues that may better the project
in the Issues section. Thanks.

