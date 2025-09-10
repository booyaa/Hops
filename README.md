# 🐇 Hops plus Tools

Hops is a [Meshtastic](https://meshtastic.org/) bot that responds to dot commands.

> [!INFO]
> This is a fork to add some command line tools to manage the database.

## WIP: Tools

### List BBS messages

```sh
barley bbs list

id|timestamp|from_id|from_short_name|from_long_name|message
1|2025-07-29T17:40:47.122722|nnn|😀|George|Welcome to the East Anglian Notice Board
2|2025-07-29T17:41:13.002919|nnn|😀|George|Now was your hands
```

### Post BBS message

```sh
barley bbs post "your message"

Post added (id: 3)
```

### Delete BBS message

```sh
barley bbs delete 3

Post deleted
```

### Search Nodes

```sh
barley nodedb search "needle" # will search for "needle" in longname, shortname and hardware
```

### Last Seen Node

```sh
barley nodedb lastseen 12345 # search for node by node number
```

### List Nodes

```sh
barley nodedb list # list nodes compactly
```

## Bot commands

#### .help
Get information on the bot (sends you here) Synonyms:.info, .?

#### .whoami
Node info as hops sees it

#### .ping
Sends a short ack.

#### .hello
Say hello!
_Synonyms_:.👋🏼

#### .message <user> <message>
Send a message to a user. The user can be specified by their short or long name.

#### .mail
Retrieve your most recent 5 mail messages.

#### .post Your message for the BBS
Add an item to the global BBS

#### .bbs
List the most recent 5 BBS messages

# Building and Running

Start by cloning the repository and setting up a virtual environment:

```sh
uv venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

Then, install the required packages:

```sh
uv pip install -r requirements.txt
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
uv pip install .
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

### WIP: Install as a service

- cp hops.service.template hop.service.template
- update the new service file FIXME: create install script
  - Service: user, group, working directory
  - Set HOPS_ADMIN_ID to your own node id (hex, not integer)

```sh
sudo cp hops.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hops.service
sudo systemctl start hops.service
```

If this fails troublshoot by checking

```sh
sudo systemctl status hops.service

# alternatively tail service logs
journalctl -fxeu hops.service
```

If you need to fix the service and have made updates to your local service file


```sh
sudo systemctl disable hops.service # stop service and remove syslink
sudo cp hops.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hops.service
sudo systemctl start hops.service
```

- Borrowed service and launch script from SudGunMan's excellent [meshing-around](https://github.com/SpudGunMan/meshing-around/).
