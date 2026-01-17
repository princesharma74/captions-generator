import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ass_generator import generate_ass

def test_ass_generation():
    input_srt = "tests/data/test_raw.srt"
    output_ass = "tests/data/test_raw.ass"
    
    if os.path.exists(output_ass):
        os.remove(output_ass)
        
    print(f"Generating ASS from {input_srt}...")
    generate_ass(input_srt, output_ass)
    
    if not os.path.exists(output_ass):
        print("ERROR: Output ASS file not created.")
        exit(1)
        
    with open(output_ass, "r") as f:
        content = f.read()
        
    print("ASS Content Preview:")
    print(content[:500])
    
    # Check for karaoke tags
    if "{\\k" in content:
        print("SUCCESS: Karaoke tags found.")
    else:
        print("FAILURE: No karaoke tags found.")
        exit(1)
        
    # Check for expected duration (50cs for 0.5s)
    if "{\\k50}" in content:
        print("SUCCESS: Found expected duration tag {\\k50}.")
    else:
        print("FAILURE: Did not find expected duration tag {\\k50}.")

if __name__ == "__main__":
    test_ass_generation()
