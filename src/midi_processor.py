import mido
import os



def convert_midi_to_mid(file_path):
    if file_path.endswith(".midi"):

        new_file_path = file_path.replace(".midi", ".mid")
        os.rename(file_path, new_file_path)
        print(f"File renamed to {new_file_path}")
        return new_file_path
    else:
        print("The file is not a .midi file")

def load_midi_file(file_path):
    
    midi_file = mido.MidiFile(file_path)
    
    return midi_file

def parse_midi(midi_file):
    notes = []
    current_time = 0
    active_notes = {}
    ticks_per_beat = midi_file.ticks_per_beat

    # Tempo map: [(absolute_time_in_ticks, tempo_in_microseconds_per_beat)]
    tempo_map = [(0, 500000)]  # Default tempo: 120 BPM = 500,000 microseconds per beat

    # First pass: build a global tempo map
    for track in midi_file.tracks:
        current_ticks = 0
        for msg in track:
            current_ticks += msg.time
            if msg.type == 'set_tempo':
                tempo_map.append((current_ticks, msg.tempo))

    # Sort tempo map by time
    tempo_map = sorted(tempo_map, key=lambda x: x[0])

    # Function to convert ticks to seconds, accounting for tempo changes
    def ticks_to_seconds(ticks):
        seconds = 0
        last_tick = 0
        last_tempo = tempo_map[0][1]

        for tick, tempo in tempo_map:
            if ticks <= tick:
                seconds += (ticks - last_tick) * (last_tempo / 1_000_000) / ticks_per_beat
                return seconds
            seconds += (tick - last_tick) * (last_tempo / 1_000_000) / ticks_per_beat
            last_tick = tick
            last_tempo = tempo

        # If ticks exceed the last tempo change
        seconds += (ticks - last_tick) * (last_tempo / 1_000_000) / ticks_per_beat
        return seconds

    # Second pass: process notes
    for track in midi_file.tracks:
        current_ticks = 0
        for msg in track:
            current_ticks += msg.time
            current_time = ticks_to_seconds(current_ticks)

            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = {
                    'note': msg.note,
                    'velocity': msg.velocity,
                    'start_time': current_time + 1, # offset for initializing pygame
                    'track': midi_file.tracks.index(track)
                }
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    note_data = active_notes[msg.note]
                    active_notes.pop(msg.note)
                    note_data['end_time'] = current_time + 1 # offset for initializing pygame
                    note_data['duration'] = note_data['end_time'] - note_data['start_time']
                    note_data['color'] = (0, 0, 155) if note_data['track'] == 0 else (0, 0, 155)

                    notes.append(note_data)

    # Sort notes by start time
    notes = sorted(notes, key=lambda x: x['start_time'])

    return notes

