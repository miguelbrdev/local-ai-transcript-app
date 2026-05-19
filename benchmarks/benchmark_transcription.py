#!/usr/bin/env python3
"""
Simple benchmark: faster-whisper CPU vs GPU
Usage: python3 backend/benchmarks/benchmark_transcription.py -m medium -a backend/benchmarks/benchmarkTest.wav --runs 5
"""

import argparse
import statistics
import time


def get_audio_duration(path):
    try:
        import soundfile as sf

        info = sf.info(path)
        if getattr(info, "duration", None):
            return info.duration
        with sf.SoundFile(path) as f:
            return len(f) / f.samplerate
    except Exception:
        try:
            import wave

            with wave.open(path, "rb") as w:
                return w.getnframes() / float(w.getframerate())
        except Exception:
            return None


def run_benchmark(
    model_name, audio, device, compute_type, runs, warmup, language, beam_size
):
    from faster_whisper import WhisperModel

    print(
        f"\nLoading model '{model_name}' on {device} (compute_type={compute_type}) ..."
    )
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    print("Warmup...")
    for _ in range(warmup):
        segments, info = model.transcribe(
            audio,
            language=language,
            beam_size=beam_size,
            condition_on_previous_text=False,
        )
    durations = []
    for i in range(runs):
        t0 = time.perf_counter()
        segments, info = model.transcribe(
            audio,
            language=language,
            beam_size=beam_size,
            condition_on_previous_text=False,
        )
        t1 = time.perf_counter()
        d = t1 - t0
        durations.append(d)
        print(f"{device} run {i+1}/{runs}: {d:.2f}s")
    avg = statistics.mean(durations)
    stdev = statistics.stdev(durations) if len(durations) > 1 else 0.0
    return {
        "device": device,
        "compute_type": compute_type,
        "avg": avg,
        "stdev": stdev,
        "durations": durations,
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark faster-whisper CPU vs GPU")
    parser.add_argument(
        "-m",
        "--model",
        required=True,
        help="Model name or path (same used in your app)",
    )
    parser.add_argument("-a", "--audio", required=True, help="Audio file to transcribe")
    parser.add_argument(
        "--runs", type=int, default=3, help="Number of timed runs (default 3)"
    )
    parser.add_argument(
        "--warmup", type=int, default=1, help="Warmup runs before timing"
    )
    parser.add_argument(
        "--cpu-compute", default="int8", help="Compute type for CPU (default int8)"
    )
    parser.add_argument(
        "--gpu-compute",
        default="float16",
        help="Compute type for GPU (default float16)",
    )
    parser.add_argument(
        "--beam", type=int, default=5, help="Beam size (same as in app)"
    )
    parser.add_argument("--language", default=None, help="Language code (optional)")
    args = parser.parse_args()

    audio_dur = get_audio_duration(args.audio)
    if audio_dur:
        print(f"Audio duration: {audio_dur:.2f}s")

    cpu_res = None
    try:
        cpu_res = run_benchmark(
            args.model,
            args.audio,
            device="cpu",
            compute_type=args.cpu_compute,
            runs=args.runs,
            warmup=args.warmup,
            language=args.language,
            beam_size=args.beam,
        )
    except Exception as e:
        print(f"CPU benchmark failed: {e}")

    gpu_res = None
    try:
        gpu_res = run_benchmark(
            args.model,
            args.audio,
            device="cuda",
            compute_type=args.gpu_compute,
            runs=args.runs,
            warmup=args.warmup,
            language=args.language,
            beam_size=args.beam,
        )
    except Exception as e:
        print(f"GPU benchmark failed / no GPU available: {e}")

    if cpu_res and gpu_res:
        cpu = cpu_res["avg"]
        gpu = gpu_res["avg"]
        speedup = cpu / gpu if gpu > 0 else float("inf")
        improvement_pct = (cpu - gpu) / cpu * 100
        print("\n=== Summary ===")
        print(f"CPU avg: {cpu:.2f}s ±{cpu_res['stdev']:.2f}s")
        print(f"GPU avg: {gpu:.2f}s ±{gpu_res['stdev']:.2f}s")
        print(
            f"Speedup (CPU / GPU): {speedup:.2f}x  => GPU is {improvement_pct:.1f}% faster"
        )
        if audio_dur:
            rtf_cpu = cpu / audio_dur
            rtf_gpu = gpu / audio_dur
            print(
                f"RTF (cpu): {rtf_cpu:.3f}, RTF (gpu): {rtf_gpu:.3f} (lower is better)"
            )
            print(
                f"Acceleration (audio_duration/transcription_time): {(audio_dur/cpu):.2f}x (CPU), {(audio_dur/gpu):.2f}x (GPU)"
            )
    else:
        print("No comparison possible (one or both runs failed).")


if __name__ == "__main__":
    main()
