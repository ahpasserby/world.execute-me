"""Word-onset behavior, original scene coverage and terminal layout checks."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from player import Film, width, WHITE, Canvas
from choreography import EXECUTIONS, scripted_time
from word_score import WordScore, score
import scenes


class TerminalScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.film = Film()
        cls.score = score()

    def test_every_source_word_has_an_ordered_nonzero_slot(self):
        self.assertEqual(len(self.score.lines), len(self.film.lyrics))
        count = 0
        for source, line in zip(self.film.lyrics, self.score.lines):
            self.assertAlmostEqual(source['time'], line['time'])
            self.assertEqual(''.join(source['en'].split()),
                             ''.join(w['text'] for w in line['words']))
            previous = line['time']
            for w in line['words']:
                self.assertGreaterEqual(w['start']+.001, previous)
                self.assertGreater(w['end'], w['start'], (line['time'],w))
                self.assertLessEqual(w['end'], line['end']+.001)
                previous=w['end'];count+=1
        self.assertEqual(count,396)

    def test_word_switches_and_active_caption_glyphs(self):
        for word in self.score.words:
            if word['line_time']==16:continue  # Instrumental full-screen title.
            t=(word['start']+word['end'])/2
            self.assertEqual(self.score.at(t)['text'],word['text'])
            canvas=self.film.render(t,128,44)
            caption=canvas.cells[-5:-3]
            lit=''.join(ch for row in caption for ch,ink in row if ink==WHITE)
            self.assertEqual(lit,word['text'],(t,word['text'],lit))

    def test_dc_and_gender_do_not_switch_before_the_sung_word(self):
        dc=self.score.onset(45.85,'DC')
        self.assertLess(scripted_time(dc-.01),45.85)
        self.assertGreater(scripted_time(dc+.01),45.85)
        male=self.score.onset(90.197,'M')
        self.assertLess(scripted_time(male-.01),90.197)
        self.assertGreater(scripted_time(male+.01),90.197)

    def test_give_opens_lines_before_dimension_unfolds_volume(self):
        give=self.score.onset(31.116,'give')
        self.assertIn('1D: LINES',self.film.render(give+.02,128,44).plain())
        self.assertIn('SURFACE -> VOLUME',self.film.render(32.9,128,44).plain())

    def test_original_comparison_bypasses_word_director(self):
        original=Film(original=True)
        with patch('choreography.draw_scene',side_effect=AssertionError('word director leaked into original')):
            frame=original.render(39.5,128,44).plain()
        self.assertIn('/ ORIGINAL',frame)
        self.assertNotIn('/ WORD SCORE',frame)

    def test_departures_follow_all_six_left_words(self):
        for index,line in enumerate((110.9,112.22,113.1,114.18,114.92,115.78)):
            onset=self.score.onset(line,'left')
            before=self.film.render(onset-.01,128,44).plain()
            after=self.film.render(onset+.01,128,44).plain()
            self.assertIn(f'CONNECTION LOSS / {index:02d} OF 06',before)
            self.assertIn(f'CONNECTION LOSS / {index+1:02d} OF 06',after)

    def test_original_varied_scenes_are_still_used(self):
        checks=[(42,'lyric_infinity_limit'),(46,'lyric_ac_dc'),(49,'lyric_dizzy'),
                (54,'lyric_time_travel'),(60,'lyric_stimulation_satisfaction'),
                (68,'lyric_happy_execution'),(72,'lyric_trapped_simulation'),
                (75,'legacy_organic'),(79,'legacy_organic'),(83,'legacy_organic'),
                (86,'lyric_god_existence'),(91,'lyric_identity_rewrite'),
                (94,'lyric_daynight_clock'),(98,'lyric_gender_role_switch'),
                (108,'lyric_vibration_sync'),(123,'lyric_erase_fragments'),
                (132,'lyric_illegal_arguments'),(160,'lyric_multilingual_count'),
                (169,'lyric_only_execution'),(182,'lyric_love_equation'),
                (199,'lyric_outro_wait')]
        for t,name in checks:
            with patch.object(scenes,name,wraps=getattr(scenes,name)) as fn:
                self.film.render(t,128,44)
                self.assertTrue(fn.called,(t,name))
        with patch.object(scenes,'title_takeover',wraps=scenes.title_takeover) as fn:
            self.film.render(23,128,44);self.assertTrue(fn.called)

    def test_execution_has_twelve_distinct_memory_edits(self):
        frames=[]
        for index,t in enumerate(EXECUTIONS):
            frame=self.film.render(t+.3,128,44).plain()
            self.assertIn(f'EXECUTION {index+1:02d} / 12',frame)
            frames.append(frame)
        self.assertEqual(len(set(frames)),12)
        self.assertIn('TROIS',self.film.render(159.85,128,44).plain())

    def test_all_phrase_boundaries_fit_three_terminal_sizes(self):
        for w,h in ((64,24),(128,44),(200,65)):
            for line in self.film.lyrics:
                for t in (line['time']+.01,min(line['end']-.01,line['time']+.4)):
                    canvas=self.film.render(t,w,h)
                    self.assertEqual(len(canvas.cells),h)
                    self.assertTrue(all(len(row)==w for row in canvas.cells))
                    self.assertTrue(all(width(row)==w for row in canvas.plain().splitlines()),(t,w,h))
                    if 15.8<=t<29.709:continue
                    self.assertIn(line['en'].split()[0],''.join(canvas.plain().splitlines()[h-5:h-3]))

    def test_scrubbing_does_not_depend_on_previous_frames(self):
        before=self.film.render(46.8,128,44).plain()
        self.film.render(191,128,44)
        self.assertEqual(before,self.film.render(46.8,128,44).plain())
        film=Film();caption=film.render(114,128,44).plain().splitlines()[-6:]
        film.respond(114)
        after=film.render(114,128,44).plain()
        self.assertIn('ECHO / NO ACK',after)
        self.assertEqual(caption,after.splitlines()[-6:])
        self.assertEqual(film.response(100),0)

    def test_small_terminal_and_help(self):
        self.assertIn('minimum 64 x 24',self.film.render(0,50,20).plain())
        self.assertIn('CONTROLS',self.film.render(38,64,24,help_on=True).plain())


if __name__=='__main__':
    unittest.main()
