"""Validate the terminal score, layout and audio-independent snapshots."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from player import Film, width
from choreography import CUES, CUE_TIMES, EXECUTIONS, cue_at


class TerminalScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.film = Film()

    def test_cues_follow_source_lyrics(self):
        for timestamp in CUE_TIMES:
            if timestamp in (0, 208):
                continue
            self.assertTrue(any(abs(line['time'] - timestamp) < .001
                                for line in self.film.lyrics), timestamp)
        for i in range(1, len(CUES)):
            self.assertEqual(cue_at(CUE_TIMES[i]), i)
            self.assertEqual(cue_at(CUE_TIMES[i] - .001), i - 1)

    def test_ascii_stage_and_caption_bounds_at_all_lyrics(self):
        for w, h in ((64, 24), (128, 44), (200, 65)):
            for line in self.film.lyrics:
                canvas = self.film.render(line['time'] + .05, w, h)
                self.assertEqual(len(canvas.cells), h)
                self.assertTrue(all(len(row) == w for row in canvas.cells))
                stage = canvas.plain().splitlines()[4:h-7]
                self.assertTrue(all(ord(ch) < 128 for row in stage for ch in row),
                                (w, h, line['time']))
                self.assertTrue(all(width(row) == w for row in canvas.plain().splitlines()))
                caption = ''.join(canvas.plain().splitlines()[h-5:h-3])
                self.assertIn(line['en'].split()[0], caption)

    def test_execution_erases_one_world_per_actual_beat(self):
        for index, timestamp in enumerate(EXECUTIONS):
            frame = self.film.render(timestamp + .01, 128, 44).plain()
            self.assertIn(f'EXECUTION {index+1:02d} / 12', frame)
            self.assertIn(f'{11-index:02d} WORLDS REMAIN', frame)
        self.assertIn('TROIS', self.film.render(159.85, 128, 44).plain())

    def test_seek_is_deterministic_and_response_does_not_rewrite_lyrics(self):
        before = self.film.render(38, 128, 44).plain()
        self.film.render(150, 128, 44)
        self.assertEqual(before, self.film.render(38, 128, 44).plain())
        film = Film()
        caption = film.render(114, 128, 44).plain().splitlines()[-6:]
        film.respond(114)
        after = film.render(114, 128, 44).plain()
        self.assertIn('CONNECTION NOT FOUND', after)
        self.assertEqual(caption, after.splitlines()[-6:])
        self.assertEqual(film.response(100), 0)
        self.assertEqual(film.response(116), 0)

    def test_small_terminal_and_help_stay_operable(self):
        self.assertIn('minimum 64 x 24', self.film.render(0, 50, 20).plain())
        self.assertIn('CONTROLS', self.film.render(38, 64, 24, help_on=True).plain())
        self.assertIn('SPACE / ENTER', self.film.render(0, 128, 44, ready=True).plain())


if __name__ == '__main__':
    unittest.main()
