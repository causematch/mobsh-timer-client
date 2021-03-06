#!/usr/bin/env python3
"mob.sh timer client"
import argparse
import json
import random
import sys
import uuid

import requests

defaults = {
    "site": "https://timer.mob.sh",
    "room": str(uuid.uuid4()),
    "lineup": "lineup",
    "time": "7",
}


def load_lineup(filepath):
    with open(filepath) as f:
        return f.read().splitlines()


def save_lineup(filepath, lineup):
    with open(filepath, "w") as f:
        f.write("\n".join(lineup))


def next_up(lineup):
    return lineup[:2]


def rotate(lineup, count):
    return lineup[count:] + lineup[:count]


def get_endpoint(options):
    return f"{options.site}/{options.room}"


def get_user(driver, navigator):
    return f"D: {driver}, N: {navigator}"


def start_timer(endpoint, user, timer):
    requests.put(endpoint, json={"user": user, "timer": timer})


def serialize_config(options):
    return {
        "site": options.site,
        "room": options.room,
        "lineup": options.lineup,
        "time": options.time,
    }


def save_config(options):
    with open(options.config, "w") as f:
        json.dump(serialize_config(options), f, indent=2)


def load_config(options):
    try:
        with open(options.config) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def config(options):
    save_config(options)
    print(f"config written to {options.config}")
    print(f"room url: {get_endpoint(options)}")


def shuffle(options):
    lineup = load_lineup(options.lineup)
    random.shuffle(lineup)
    save_lineup(options.lineup, lineup)


def forward(options):
    punch(options, 1)


def restart(options):
    punch(options, 0)


def back(options):
    punch(options, -1)


def punch(options, rotate_count):
    lineup = load_lineup(options.lineup)
    if rotate_count:
        lineup = rotate(lineup, rotate_count)
        save_lineup(options.lineup, lineup)
    navigator, driver = next_up(lineup)
    endpoint = get_endpoint(options)
    user = get_user(driver, navigator)
    timer = options.time
    print(f"{user} up for {timer} minutes")
    start_timer(endpoint=endpoint, user=user, timer=timer)


commands = {
    "config": config,
    "next": forward,
    "restart": restart,
    "back": back,
    "shuffle": shuffle,
}


def merge_options(options, config, default):
    merge = lambda name: getattr(options, name) or config.get(name) or default[name]
    return argparse.Namespace(
        site=merge("site"),
        room=merge("room"),
        lineup=merge("lineup"),
        time=merge("time"),
        config=options.config,
        command=options.command,
    )


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="timer client for https://timer.mob.sh"
    )
    parser.add_argument("--config", default=".mobsh-timerrc")
    parser.add_argument(
        "--new-room",
        dest="room",
        action="store_const",
        const=str(uuid.uuid4()),
    )
    parser.add_argument("--room")
    parser.add_argument("--site")
    parser.add_argument("--lineup")
    parser.add_argument("-t", "--time")
    parser.add_argument("command", choices=commands.keys())
    return parser.parse_args(args)


def get_options(args, default_options):
    cli_options = parse_args(args)
    saved_config = load_config(cli_options)
    return merge_options(cli_options, saved_config, default_options)


def main(args):
    options = get_options(args, defaults)
    command = commands.get(options.command)
    if command:
        command(options)


if __name__ == "__main__":
    main(sys.argv[1:])
