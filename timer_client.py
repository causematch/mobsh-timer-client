"mob.sh timer client"
import argparse
import os
import sys
import uuid

import requests


def load_lineup(filepath):
    with open(filepath) as f:
        return f.read().splitlines()


def save_lineup(filepath, lineup):
    with open(filepath, "w") as f:
        f.write("\n".join(lineup))


def next_up(lineup):
    return lineup[:2]


def rotate(lineup):
    return lineup[1:] + lineup[:1]


def get_endpoint(options):
    return f"{options.site}/{options.room}"


def get_user(driver, navigator):
    return f"D: {driver}, N: {navigator}"


def load_defaults():
    return {
        "site": os.getenv("MOB_TIMER_SITE", "https://timer.mob.sh"),
        "room": os.getenv("MOB_TIMER_ROOM", str(uuid.uuid4())),
        "lineup": os.getenv("MOB_TIMER_LINEUP", "lineup"),
        "time": os.getenv("MOB_TIMER_TIME", "7"),
    }


def start_timer(endpoint, user, timer):
    requests.put(endpoint, json={"user": user, "timer": timer})


def config(options):
    print(f"export MOB_TIMER_SITE={options.site}")
    print(f"export MOB_TIMER_ROOM={options.room}")
    print(f"export MOB_TIMER_LINEUP={options.lineup}")
    print(f"export MOB_TIMER_TIME={options.time}")
    print(f"room url: {get_endpoint(options)}", file=sys.stderr)


def cycle(options):
    lineup = load_lineup(options.lineup)
    driver, navigator = next_up(lineup)
    endpoint = get_endpoint(options)
    user = get_user(driver, navigator)
    timer = options.time
    print(f"{user} up for {timer} minutes")
    start_timer(endpoint=endpoint, user=user, timer=timer)
    save_lineup(options.lineup, rotate(lineup))


commands = {
    "config": config,
    "next": cycle,
}


def parse_args(args, defaults):
    parser = argparse.ArgumentParser(
        description="timer client for https://timer.mob.sh"
    )
    parser.add_argument("--site", default=defaults.get("site"))
    parser.add_argument("--room", default=defaults.get("room"))
    parser.add_argument("--lineup", default=defaults.get("lineup"))
    parser.add_argument("-t", "--time", type=int, default=defaults.get("time"))
    parser.add_argument("command", choices=commands.keys())
    return parser.parse_args(args)


def main(args):
    defaults = load_defaults()
    options = parse_args(args, defaults)
    command = commands.get(options.command)
    if command:
        command(options)


if __name__ == "__main__":
    main(sys.argv[1:])
