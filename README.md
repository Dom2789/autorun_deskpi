# autorun_deskpi

A Raspberry Pi automation service that reads environmental sensor data, drives an OLED display, controls a WS281x LED strip, and shares data over MQTT and UDP.

## Overview

The project runs as a systemd service on a Raspberry Pi and coordinates five concurrent threads:

| Thread | Role |
|---|---|
| **Display_Routine** | Reads BME280 sensor (I2C), renders temperature/pressure/humidity to a 96×128 OLED |
| **Strip_Routine** | Drives a 120-pixel WS281x LED strip via GPIO; supports wipe, rainbow, chase, and temperature-gradient modes |
| **Mqtt_Publish_Routine** | Publishes climate data to an MQTT broker at a configurable interval |
| **Mqtt_Subscribe_Routine** | Subscribes to an MQTT topic for LED control commands (JSON) |
| **Network_Routine** | UDP server on port 4081; responds to requests from other LAN devices with current climate data |

Data flows through a thread-safe singleton (`Data`) that all routines read and write.

## Hardware

- Raspberry Pi (any model with GPIO and I2C)
- BME280 sensor at I2C address `0x76`
- 96×128 OLED display (SMBus I2C)
- WS281x / NeoPixel LED strip on GPIO 18 (or 10)

## Dependencies

Managed with [uv](https://github.com/astral-sh/uv) / Poetry (`pyproject.toml`):

| Package | Purpose |
|---|---|
| `paho-mqtt >= 2.1.0` | MQTT client |
| `pillow >= 12.0.0` | Font/image rendering for OLED |
| `rpi-gpio >= 0.7.1` | GPIO control |
| `rpi-ws281x >= 5.0.0` | WS281x LED strip driver |
| `smbus >= 1.1` | I2C communication |

**External library**: [`oled96.py`](https://github.com/BLavery/lib_oled96/) — place in the project root.

Python >= 3.12 required.

## Installation

```bash
# Clone and enter the repo
git clone <repo-url> /home/pi/prog/autorun_deskpi
cd /home/pi/prog/autorun_deskpi

# Download the OLED driver
curl -O https://raw.githubusercontent.com/BLavery/lib_oled96/master/oled96.py

# Install dependencies
uv sync
# or: pip install paho-mqtt pillow rpi-gpio rpi-ws281x smbus
```

## Configuration

Create a config file (see `config_autorun.txt` for reference). The production path expected by `autorun.py` is `/home/pi/_config/config_autorun.txt`.

```
PWDprot:      /home/pi/_prot/          // directory for data/protection files
PWDlog:       /home/pi/_prot/          // directory for log files
IPbroker:     192.168.178.100          // MQTT broker IP
TopicPub:     climate/office/2         // topic to publish climate data on
TopicSub:     led/office/1             // topic to receive LED commands on
Sendinterval: 15                       // publish interval in seconds
DEBUG:        False                    // set True for verbose logging
```

Lines starting with `//` are treated as comments.

## Running

### Directly

```bash
python autorun.py
# or for development/testing:
python main.py
```

### As a systemd service

Create `/etc/systemd/system/python-script.service` pointing to a startup script:

```ini
[Unit]
Description=autorun_deskpi
After=network.target

[Service]
ExecStart=/home/pi/prog/startup.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable python-script
sudo systemctl start python-script
```

## MQTT Protocol

### Published (climate data)

**Topic**: value of `TopicPub`

**Payload** (string):
```
[HH:MM:SS] [23.50C] [1013.25hPa] [45.30%]
```

### Subscribed (LED control)

**Topic**: value of `TopicSub`

**Payload** (JSON):
```json
{
  "brightness": 200,
  "mode": "wipe",
  "red": 52,
  "green": 225,
  "blue": 235
}
```

| Field | Range | Notes |
|---|---|---|
| `brightness` | 0–255 | Strip brightness |
| `mode` | `wipe` \| `rainbow` \| `chase` \| `temperature` | Animation mode |
| `red`, `green`, `blue` | 0–255 | Color (ignored in `rainbow` and `temperature` modes) |

In `temperature` mode the strip color is interpolated from blue (≤15 °C) to red (≥30 °C) using the latest sensor reading.

## UDP Network Protocol

**Port**: 4081

Send a plain-text request; the service replies to a fixed IP on port 4080:

| Request | Destination |
|---|---|
| `trigger` | 192.168.178.45 |
| `desktop` | 192.168.178.117 |
| `clock` | 192.168.178.100 |
| `mini` | 192.168.178.128 |

The reply payload is the current climate string (same format as MQTT publish).

## Seasonal LED Colors

When no MQTT command has been received, the strip defaults to a seasonal color:

- **Spring / Summer** (Mar 20 – Sep 22): cyan `(52, 225, 235)`
- **Fall / Winter**: purple `(240, 3, 252)`

## Project Structure

```
autorun_deskpi/
├── autorun.py                  # Production entry point
├── main.py                     # Development entry point
├── config_autorun.txt          # Example configuration
├── pyproject.toml
├── oled96.py                   # External OLED driver (not in repo)
└── src/
    ├── DataExchange.py         # Thread-safe singleton for shared state
    ├── DisplayRoutine.py       # BME280 sensor reading + OLED output
    ├── LedStripRoutine.py      # WS281x LED strip control
    ├── MqttPublishRoutine.py   # MQTT climate publisher
    ├── MqttSubscribeRoutine.py # MQTT LED command subscriber
    ├── NetworkRoutine.py       # UDP listener
    └── _lib/
        ├── Config.py           # Config file parser
        └── logger.py           # Logging setup
```