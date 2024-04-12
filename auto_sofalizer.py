import os
import sys
import subprocess
import re

# Check if correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage: python main.py \"path/to/input/folder\" \"path/to/output/folder\"")
    sys.exit(1)

input_folder = sys.argv[1]
output_folder = sys.argv[2]

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Function to extract max_volume from ffmpeg output
def get_max_volume(input_file):
    command = [
        './ffmpeg',
        '-i', input_file,
        '-af', 'volumedetect',
        '-vn',
        '-sn',
        '-dn',
        '-f', 'null',
        '-'
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    max_volume_matches = re.search(r"max_volume: ([\-\d\.]+) dB", result.stderr)
    if max_volume_matches:
        return float(max_volume_matches.group(1))
    else:
        return 0

# Process each file in the input directory
for filename in os.listdir(input_folder):
    if filename.endswith(".m4a"):
        # Check if the output file already exists
        final_output_file = os.path.join(output_folder, filename.replace('.m4a', '.flac'))
        if os.path.exists(final_output_file):
            print(f"File {final_output_file} already exists. Skipping processing.")
            continue

        # Construct the full paths for input and output files
        input_file = os.path.join(input_folder, filename)
        temp_output_file = os.path.join(output_folder, filename.replace('.m4a', '_temp.flac'))

         # ... [rest of the script] ...
        
        # Apply the sofalizer filter
        sofalizer_command = [
            './ffmpeg',
            '-i', input_file,
            '-af', 'sofalizer=sofa=/root/irc_1003.sofa:type=freq:radius=1',
            '-c:a', 'flac',
            temp_output_file
        ]
        subprocess.run(sofalizer_command)
        
        # Check if the temporary file was created successfully
        if os.path.exists(temp_output_file):
            # Get the max_volume from the output file
            max_volume = get_max_volume(temp_output_file)
        
            # Calculate the adjustment needed (if max_volume is negative)
            volume_adjustment = '+{}dB'.format(-max_volume) if max_volume < 0 else '+0dB'
        
            # Apply the volume gain
            gain_command = [
                './ffmpeg',
                '-i', temp_output_file,
                '-af', 'volume={}'.format(volume_adjustment),
                '-c:a', 'flac',
                final_output_file
            ]
            subprocess.run(gain_command)
            print(gain_command)
        
            # Remove the temporary file
            os.remove(temp_output_file)
        else:
            print(f"Error: The file {temp_output_file} was not created.")
        
        # ... [rest of the script] ...

print("Processing complete.")
