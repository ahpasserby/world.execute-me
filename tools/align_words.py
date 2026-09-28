"""Offline authoring tool; the player itself only reads the resulting JSON.

Optional environment: stable-ts==2.19.1, FFmpeg and a Whisper base.en model.
Align inside existing lyric phrase boundaries rather than re-transcribing music.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, default=ROOT/'media/song.mp3')
    parser.add_argument('--model', default='base.en')
    parser.add_argument('--model-cache', default='/private/tmp/world-execute-alignment-models')
    parser.add_argument('--context', action='store_true', help='Align neighboring phrases together, retaining phrase bounds in output')
    parser.add_argument('--output', type=Path, default=ROOT/'word_timings.json')
    args = parser.parse_args()
    import torch
    import stable_whisper
    torch.set_num_threads(4)
    source = json.loads((ROOT/'lyrics.json').read_text())
    model = stable_whisper.load_model(args.model, device='cpu', download_root=args.model_cache)
    segments = [dict(start=line['time'], end=line['end'], text=line['en'])
                for line in source if len(line['en'].split()) > 1]
    if args.context:
        segments=[]
        for line in source:
            if line['time']==16:continue
            if not segments or line['end']-segments[-1]['start']>11 or line['time']-segments[-1]['end']>.3:
                segments.append(dict(start=line['time'],end=line['end'],text=line['en']))
            else:
                segments[-1]['end']=line['end']
                segments[-1]['text']+=' '+line['en']
    aligned = model.align_words(str(args.audio), segments, language='en',
                                suppress_silence=False, verbose=False)
    raw = aligned.to_dict()
    (args.output.parent/(args.output.stem+'.raw.json')).write_text(json.dumps(raw, indent=2))
    iterator = iter(raw['segments'])
    contextual=iter(w for seg in raw['segments'] for w in seg['words'])
    lines = []
    for line in source:
        context_words=None
        if args.context and line['time']!=16:
            context_words=[next(contextual) for _ in line['en'].split()]
            assert ''.join(w['word'].strip() for w in context_words).lower()==''.join(line['en'].split()).lower(), (line,context_words)
        if len(line['en'].split()) == 1:
            words = [{'text': line['en'], 'start': line['time'], 'end': line['end']}]
            method = 'source-cue'
        else:
            segment = {'words':context_words} if args.context else next(iterator)
            words = [{'text': w['word'].strip(),
                      'start': round(max(line['time'], min(line['end'], w['start'])), 3),
                      'end': round(max(line['time'], min(line['end'], w['end'])), 3)}
                     for w in segment['words'] if w['word'].strip()]
            method = 'forced-alignment'
        lines.append(dict(time=line['time'], end=line['end'], text=line['en'],
                          method=method, words=words))
    data = dict(format=1, model=args.model, tool='stable-ts 2.19.1 align_words',
                audio_sha256=hashlib.sha256(args.audio.read_bytes()).hexdigest(),
                note='Phrase-bounded automatic alignment; not a manually verified phonetic transcript.',
                lines=lines)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print(f'Wrote {len(lines)} phrases / {sum(len(x["words"]) for x in lines)} words: {args.output}')


if __name__ == '__main__':
    main()
