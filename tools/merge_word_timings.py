"""Choose the least-degenerate alignment per phrase and flag minimum-slot repairs.

Usage: python3 tools/merge_word_timings.py result1.json result2.json ...
A repaired word is an estimate, not a claim of phonetic accuracy. The raw model
sources should be kept outside the repository; playback needs only the result.
"""
import argparse
import json
from pathlib import Path


def normalize_slots(line):
    words=[dict(w) for w in line['words']]
    if not words:return words
    minimum=min(.06,(line['end']-line['time'])/(len(words)*2))
    starts=[]
    for i,w in enumerate(words):
        lo=line['time']+minimum*i
        hi=line['end']-minimum*(len(words)-i)
        start=max(lo,min(hi,w['start']))
        if starts:start=max(start,starts[-1]+minimum)
        starts.append(start)
    for i,w in enumerate(words):
        end=min(starts[i+1] if i+1<len(words) else line['end'],max(starts[i]+minimum,w['end']))
        if abs(starts[i]-w['start'])>.002 or abs(end-w['end'])>.002:
            w['timing']='minimum-slot-estimate'
        else:w['timing']=line['method']
        w['start']=round(starts[i],3);w['end']=round(end,3)
    return words


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputs',nargs='+',type=Path)
    p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'word_timings.json')
    args=p.parse_args();sources=[json.loads(path.read_text()) for path in args.inputs]
    result=dict(sources[0]);result['lines']=[]
    def quality(line):
        words=line['words'];duration=line['end']-line['time']
        return (sum(w['end']-w['start']<.015 for w in words),
                sum(w['end']-w['start']<.06 for w in words),
                max(0,words[0]['start']-line['time']-.25),
                sum(max(0,w['end']-w['start']-duration*.65) for w in words))
    for alternatives in zip(*(s['lines'] for s in sources)):
        assert len({l['text'] for l in alternatives})==1
        index=min(range(len(alternatives)),key=lambda i:quality(alternatives[i]))
        line=dict(alternatives[index]);line['model']=sources[index]['model']
        line['words']=normalize_slots(line);result['lines'].append(line)
    result['model']='phrase-wise selection: small.en / base.en'
    result['note']='Audio forced alignment inside original phrase bounds. Words flagged minimum-slot-estimate were repaired to remain visible and require listening review; no claim of manually verified phoneme timing.'
    result['estimated_words']=sum(w['timing']=='minimum-slot-estimate' for l in result['lines'] for w in l['words'])
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f"Wrote {sum(len(l['words']) for l in result['lines'])} words; {result['estimated_words']} flagged estimates")


if __name__=='__main__':main()
