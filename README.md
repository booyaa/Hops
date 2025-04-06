# 🐇 Hops

Hops is a [Meshtastic](https://meshtastic.org/) bot that responds to dot commands.


## Commands
#### .help
Get information on the bot (sends you here) Synonyms:.info, .?

#### .whoami
Node info as hops sees it

#### .ping
Sends a short ack.

#### .hello
Say hello!
_Synonyms_:.👋🏼

#### .post Your message for the BBS
Add an item to the global BBS

#### .bbs
List the most recent 5 BBS messages

# Building and Running

Start by cloning the repository and setting up a virtual environment:

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Then, install the required packages:

```sh
pip install -r requirements.txt
```

Then, you can run the bot using the following command:

```sh
python main.py --help
```

Tests can be run with:

```sh
python -m unittest discover
```

You can install the bot via

```sh
pip install .
```

and once installed run it via

```sh
hops --help
```

### Running hops

Hops expects to have access via the serial interface or via TCP. It does **not** run via BLE.

To run via the serial interface,

```sh
hops --serial
```

and via TCP,

```sh
hops --tcp <ip_address>
```

By default hops will create a sqlite database `db.sqlite` in the current directory. Alternatively you can specify a different database file with the `--db` option:

```sh
hops --serial --db /path/to/db.sqlite
```