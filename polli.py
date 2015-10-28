#!/usr/bin/env python3.4

""" POLLI (Practically Organic Language Learning Instrument) is a command-line
language acquisition simulator. The more input it receives, the better
conversation it makes.

In its current form, it does not acquire the rules of syntax but of discourse.
Once a large enough corpus of utterances has accumulated, it should be possible
for such a system to generalize syntactic rules, but that is beyond the scope
of this project.

This code is the original work of Cliff Jones (http://CliffJonesJr.com). It may
be modified for personal use, but it should not be used commercially, and
modified versions may not be distributed without accreditation and the author's
express consent. (Polli is my baby, and I want her taken care of.)
"""

import random
import os
import json
import re

# How many statements should be used to determine responses? (1 or more.)
TALK_LEVEL_COUNT = 4


# Reduce an utterance to a sequence of the letters it contains.
def smooth(text):
    text = text.lower()
    text = re.sub(r"[^a-z]", "", text)
    letter_list = list(set(text))
    letter_list.sort()
    text = "".join(letter_list)
    return text

# Come up with a file name for a given talk level.
def get_talk_file_name(talk_level):
    if talk_level < 1:
        return "talk.txt"
    return "talk_" + str(talk_level + 1) + ".txt"

# Try to read in talk map data from the disk.
def get_talk_maps():
    # Read in talk map data files of increasing depth.
    talk_maps = []
    for i in range(TALK_LEVEL_COUNT):
        talk_maps.append({})
        try:
            with open(get_talk_file_name(i)) as in_file:
                talk_maps[i] = json.loads(in_file.read())
        except Exception:
            pass
    return talk_maps

# Save the response history as JSON data.
def store_talk_maps(talk_maps):
    for i in range(TALK_LEVEL_COUNT):
        talk_json = json.dumps(talk_maps[i])
        with open(get_talk_file_name(i), "w") as out_file:
            out_file.write(talk_json)


# This array holds a history of statements and responses.
talk_maps = get_talk_maps()

# Enter an endless loop of talking back and forth.
talk_keys = [""]*TALK_LEVEL_COUNT
line_hist = [""]*TALK_LEVEL_COUNT
line_entered = ""
while True:
    # Choose a talk line to draw a response from.
    if talk_maps[0]:
        # Build a simplified talk history for each level to be used as a key.
        talk_keys[0] = smooth(line_entered)
        for i in range(TALK_LEVEL_COUNT - 1):
            prev_line_hist = talk_keys[i]
            talk_keys[i + 1] = smooth(line_hist[i]) + " " + prev_line_hist
        
        # Check each level for a recognized sequence, longest to shortest.
        response_choices = None
        for i in range(TALK_LEVEL_COUNT - 1, 0, -1):
            if talk_keys[i] in talk_maps[i].keys():
                talk_keys[0] = talk_keys[i]
                response_choices = talk_maps[i][talk_keys[0]]
                break
        if response_choices is None:
            # If we can't find an exact match, just guess.
            if not talk_keys[0] in talk_maps[0].keys():
                talk_keys[0] = random.choice(list(talk_maps[0].keys()))
            response_choices = talk_maps[0][talk_keys[0]]

        # Push the talk history back two levels for the system and the user.
        for i in range(TALK_LEVEL_COUNT - 1, 1, -1):
            line_hist[i] = line_hist[i - 2]
        
        # Make a random selection from the chosen list of responses.
        line_hist[0] = random.choice(response_choices)

    # Say something to the user and read in a response.
    line_hist[1] = line_entered
    line_entered = input(line_hist[0] + "\n> ")

    # Exit when the user enters a blank response.
    if not line_entered:
        break

    # On the very first run, teach the computer how to begin a session.
    if not talk_maps[0]:
        talk_maps[0] = {"": [line_entered]}
    
    # Add the user's response to the talk maps.
    prev_talk_key = ""
    for i in range(TALK_LEVEL_COUNT):
        talk_keys[i] = smooth(line_hist[i]) + prev_talk_key
        if talk_keys[i] in talk_maps[i].keys():
            talk_maps[i][talk_keys[i]].append(line_entered)
        else:
            talk_maps[i][talk_keys[i]] = [line_entered]
        prev_talk_key = " " + talk_keys[i]

# Save progress when the user exits normally.
store_talk_maps(talk_maps)