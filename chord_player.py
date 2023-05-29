from __future__ import annotations
import contextlib
import io
import random
from enum import Enum
import argparse
from pydub import AudioSegment
from pydub.playback import play


class Scale(Enum):
    C = "C"
    Db = "Db"
    D = "D"
    Eb = "Eb"
    E = "E"
    F = "F"
    Gb = "Gb"
    G = "G"
    Ab = "Ab"
    A = "A"
    Bb = "Bb"
    B = "B"


class ChordQuality(Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    AUGMENTED = "AUGMENTED"
    DIMINISHED = "DIMINISHED"


class Inversion(Enum):
    ROOT = "ROOT"
    FIRST = "FIRST"
    SECOND = "SECOND"

class NotePosition(Enum):
    BOTTOM = "BOTTOM"
    MIDDLE = "MIDDLE"
    TOP = "TOP"


NOTES_PATH = "notes/"
STARTING_MILLIS = 1000  # sound doesn't start at the beginning of the files
CHORD_LENGTH_MILLIS = 3000
SINGLE_LENGTH_MILLIS = 1000
SCALE_LENGTH = len(list(Scale))
LOWEST_OCTAVE = 3


class ChordPlayer:
    root_note: str
    chord_quality: ChordQuality
    inversion: Inversion
    notes_sounds: list[AudioSegment]
    note_in_question: NotePosition
    chord: AudioSegment

    def __init__(self, args):
        self.args = args

    def get_notes_sounds(self, notes: str) -> list[AudioSegment]:
        for note in notes:
            yield AudioSegment.from_file(f"{NOTES_PATH}{str(note)}.aiff")[
                STARTING_MILLIS : CHORD_LENGTH_MILLIS + STARTING_MILLIS
            ]
    
    
    def play_chord(self):
        if not self.chord:
            print("Error: no chords played yet! Press p to play a chord.")
            return
        print(f"Sing the {self.note_in_question.value} note.")
        with contextlib.redirect_stdout(io.StringIO()):
            play(self.chord)


    def play_random_chord(self):
        root_note_index = random.randint(0, 11)
        self.root_note = list(Scale)[root_note_index]

        notes = [root_note_index]
        self.chord_quality = random.choice(list(ChordQuality))
        if self.chord_quality == ChordQuality.MAJOR:
            notes.append(root_note_index + 4)
            notes.append(root_note_index + 7)
        elif self.chord_quality == ChordQuality.MINOR:
            notes.append(root_note_index + 3)
            notes.append(root_note_index + 7)
        elif self.chord_quality == ChordQuality.DIMINISHED:
            notes.append(root_note_index + 3)
            notes.append(root_note_index + 6)
        elif self.chord_quality == ChordQuality.AUGMENTED:
            notes.append(root_note_index + 4)
            notes.append(root_note_index + 8)
        for i in range(len(notes)):
            notes[i] %= SCALE_LENGTH

        inversion = random.randint(0, 2)
        if self.args.root_only:
            inversion = 0
        self.inversion = list(Inversion)[inversion]
        for _ in range(inversion):
            notes = notes[1:] + [notes[0]]
        for i in range(1, len(notes)):
            if notes[i] < notes[i - 1]:
                notes[i] += 12

        octave = LOWEST_OCTAVE
        notes_strs = []
        for note in notes:
            if note >= 12 * (octave + 1 - LOWEST_OCTAVE):
                octave += 1
            note -= (octave - LOWEST_OCTAVE) * 12
            notes_strs.append(f"{list(Scale)[note].value}{str(octave)}")
        self.notes_sounds = list(self.get_notes_sounds(notes_strs))
        self.chord = self.notes_sounds[0]
        for note_sound in self.notes_sounds[1:]:
            self.chord = self.chord.overlay(note_sound)
        self.note_in_question = random.choice(list(NotePosition))
        self.play_chord()


    def print_and_play_answer(self):
        if not self.chord:
            print("Error: no chords played yet! Press p to play a chord.")
            return
        print(
            f"{self.root_note.value} {self.chord_quality.value} {self.inversion.value} inversion {self.note_in_question.value} note"
        )
        index = [i for i, position in enumerate(NotePosition) if position == self.note_in_question][0]
        with contextlib.redirect_stdout(io.StringIO()):
            play(self.notes_sounds[index][:SINGLE_LENGTH_MILLIS])


def print_help():
    print(
        "Commands: \n\
    p - play_chord\n\
    r - repeat_chord\n\
    a - print_answer\n\
    h - print_help\n\
    q - quit"
    )


def print_usage():
    print("Invalid input.")
    print_help()


def get_args():
    parser = argparse.ArgumentParser(description='Chord Player')
    parser.add_argument('--root-only', action='store_true', help='Restrict inversions to only allow root inversion')
    return parser.parse_args()

def main():
    args = get_args()
    chord_player = ChordPlayer(args)
    print("Using args:")
    for key, val in vars(args).items():
        print(f"  {key}: {val}")
    while True:
        user_input = input("Enter a command (h for help): ")
        if user_input == "p":
            chord_player.play_random_chord()
        elif user_input == "r":
            chord_player.play_chord()
        elif user_input == "a":
            chord_player.print_and_play_answer()
        elif user_input == "h":
            print_help()
        elif user_input == "q":
            exit()
        else:
            print_usage()


if __name__ == "__main__":
    main()
