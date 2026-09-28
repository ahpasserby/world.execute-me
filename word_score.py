"""Word-level vocal cues, independent of rendering and wall-clock time."""
import bisect
import functools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def normalized(word):
    return re.sub(r'[^a-z0-9]', '', word.lower())


class WordScore:
    def __init__(self, path=None):
        self.data = json.loads((path or ROOT/'word_timings.json').read_text())
        self.lines = self.data['lines']
        self.line_times = [line['time'] for line in self.lines]
        self.words = []
        for line in self.lines:
            offset = 0
            for i, raw in enumerate(line['words']):
                word = dict(raw, line_time=line['time'], line_end=line['end'],
                            index=i, count=len(line['words']), key=normalized(raw['text']))
                found = line['text'].lower().find(raw['text'].lower(), offset)
                word['char_start'] = max(offset, found)
                word['char_end'] = word['char_start'] + len(raw['text'])
                offset = word['char_end']
                self.words.append(word)
        self.starts = [word['start'] for word in self.words]

    def at(self, t):
        i = bisect.bisect_right(self.starts, t) - 1
        if i < 0: return None
        word = self.words[i]
        return word if t < word['line_end'] else None

    def in_line(self, start):
        return [w for w in self.words if abs(w['line_time'] - start) < .002]

    def onset(self, line, word, occurrence=0):
        matches = [w['start'] for w in self.in_line(line) if w['key'] == normalized(word)]
        return matches[occurrence] if len(matches) > occurrence else line

    def end(self, line, word, occurrence=0):
        matches = [w['end'] for w in self.in_line(line) if w['key'] == normalized(word)]
        return matches[occurrence] if len(matches) > occurrence else line

    def phase(self, t, line, word, duration=.35, occurrence=0):
        return max(0., min(1., (t-self.onset(line, word, occurrence))/max(.01, duration)))


@functools.lru_cache(maxsize=1)
def score():
    return WordScore()
