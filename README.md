<p align="center">
  <img src="http://i.imgur.com/F9zuexe.jpg" width="500px" />
</p>

Soccer CLI
=====

[![PyPI version](https://badge.fury.io/py/soccer-cli.svg)](http://badge.fury.io/py/soccer-cli) [![Join the chat at https://gitter.im/architv/soccer-cli](https://badges.gitter.im/architv/soccer-cli.svg)](https://gitter.im/architv/soccer-cli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Soccer for Hackers - a CLI for all the football scores. 

![](http://i.imgur.com/9QbcUrj.gif)

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

<hr>

Usage
====

<details>
  <summary>Competition Resource commands </summary>
  
  #### get specific competition/league info
  
  ```bash
  $ soccer competitions --id 2021 standings # 2021 is the competition id for English Premier League
  ```
  <hr>
</details>

__The content below is not correct for the v2 api and its unedited. I am working on doing so as i port the project to 
the version 2 api__

<details>
<summary> Team resource commands </summary>
  ```bash
  $ soccer teams --id <id> # MUFC is the team code for Manchester United
  ```
  <hr>
</details>

<details>
<summary> Match Resource commands </summary>
  
  #### Get upcoming fixtures
  
  ```bash
  $ soccer
  ```
  <hr>
</details>

<details>
<summary> Player Resource commands </summary>

  #### get specific player info

  ```bash
  $ soccer players --id  <id> # <id> is the id of player of interest
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
 
### Get scores for a particular league

```bash
$ soccer --league=BL # BL is the league code for Bundesliga
$ soccer --league=FL --time=15 # get scores for all the French Ligue games over the past 15 days
```


### Get the output in csv or json

```bash
$ soccer --league PL --standings --csv # prints the output in csv format
$ soccer --league PL --standings --json # prints the output in json format
```

### Store the ouput in a file

```bash
$ soccer --league PL --standings --csv -o 'standings.csv' # stores the ouput in scv format in `standings.csv`
```

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

### Team and team codes

For a full list of supported team and team codes [see this](soccer/teams.json).

### Tests

To run testing suite from root of repo

```bash
$ python -m unittest discover tests
```

To run specific test file (in this case the tests in test_request_handler.py)

```bash
$ python -m unittest tests.test_request_handler
```

Demo
====

### Standings
![standings](http://i.imgur.com/voyWLQE.gif)

### Live scores
![](http://i.imgur.com/EX9GMAM.gif)

### Team scores
![](http://i.imgur.com/QfvH8QL.png)

### Output in json format
![](http://i.imgur.com/jqGhLia.gif)

Todo
====
- [ ] Enable cache
- [ ] Add more test cases
- [ ] Add fixtures for UEFA Champions League
- [ ] Add league filter for live scores
- [ ] Color coding for Europa league and differentiation between straight CL and CL playoff spots, and the same for EL spots
- [ ] Add support for team line up
- [ ] A built in watch feature so you can run once with --live and just leave the program running.

Licence
====
Open sourced under [MIT License](LICENSE)

Support
====
If you like my work, please support the project by donating.

- https://gratipay.com/~architv
