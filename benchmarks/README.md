# Benchmarks — CPU vs GPU Transcription

Measures Whisper transcription speed across devices using a 87-second Spanish audio file and "medium" model.

## Hardware

- **CPU:** 12-core (8P + 4E)
- **GPU:** 11 GB VRAM

## Run

```bash
python3 benchmarks/benchmark_transcription.py -m medium -a benchmarks/benchmarkTest.wav --runs 5
```

## Results

Check results.txt on /benchmarks
