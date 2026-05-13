🎯 TST proves coarse→fine works when coarse levels have direct loss — holographic loss IS that signal

Token-Superposition Training (Peng, Gigant, Quesnelle / Nous Research 2026):
train on bags of contiguous tokens with multi-hot CE first, then recover
to standard next-token prediction. 2.5× training speedup, beats baseline
loss. The coarse phase builds structural foundations the fine phase exploits.

The connection: v11's original coarse→fine descending arm failed because
it lacked direct loss at coarse levels. TST proves the principle works
when you provide it. Holographic loss provides per-pass CE at every
resolution — it IS continuous TST, running at all resolutions simultaneously
rather than phased over time. The architecture (coarse→fine) and the
training signal (holo) must both be present. Either alone fails:

  coarse→fine(arch) + coarse→fine(signal) = works (TST proves)
  coarse→fine(arch) + uniform(signal)     = fails (our experience)
  uniform(arch)     + coarse→fine(signal) = partially works (v11-holo now)
  
The v11-holo-inv run tests case 1. arxiv: 2605.06546
