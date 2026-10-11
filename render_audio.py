import numpy as np
import mido
from scipy.io import wavfile

def render_midi_to_wav(midi_file, wav_file, sample_rate=44100):
    print(f"Reading {midi_file} and synthesizing audio...")
    mid = mido.MidiFile(midi_file)

    tempo = 500000
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break

    ticks_per_beat = mid.ticks_per_beat
    seconds_per_tick = mido.tick2second(1, ticks_per_beat, tempo)

    notes = []

    for track in mid.tracks:
        current_time = 0.0
        active_notes = {}

        for msg in track:
            current_time += msg.time * seconds_per_tick

            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[(msg.channel, msg.note)] = (current_time, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active_notes:
                    start_time, vel = active_notes.pop(key)
                    notes.append({
                        'note': msg.note,
                        'start': start_time,
                        'end': current_time,
                        'channel': msg.channel,
                        'velocity': vel
                    })

    if not notes:
        print("No notes found to synthesize.")
        return

    duration = max(n['end'] for n in notes) + 1.0
    total_samples = int(duration * sample_rate)
    audio = np.zeros(total_samples)

    for n in notes:
        freq = 440.0 * (2.0 ** ((n['note'] - 69) / 12.0))
        start_samp = int(n['start'] * sample_rate)
        end_samp = int(n['end'] * sample_rate)

        if end_samp <= start_samp:
            continue

        t = np.arange(end_samp - start_samp) / sample_rate

        attack = min(int(0.03 * sample_rate), len(t) // 2)
        release = min(int(0.06 * sample_rate), len(t) // 2)
        env = np.ones_like(t)
        if attack > 0:
            env[:attack] = np.linspace(0, 1, attack)
        if release > 0:
            env[-release:] = np.linspace(1, 0, release)

        if n['channel'] == 0:
            wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
            vol = 0.25 * (n['velocity'] / 127.0)
        else:
            wave = np.sin(2 * np.pi * freq * t)
            vol = 0.15 * (n['velocity'] / 127.0)

        audio[start_samp:end_samp] += wave * env * vol

    max_peak = np.max(np.abs(audio))
    if max_peak > 0:
        audio = (audio / max_peak) * 0.9

    audio_int16 = np.int16(audio * 32767)
    wavfile.write(wav_file, sample_rate, audio_int16)
    print(f"Audio successfully saved as {wav_file}!")

if __name__ == "__main__":
    render_midi_to_wav("Quantum_Playground_Track.mid", "quantum_audio.wav")