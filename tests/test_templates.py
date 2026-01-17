import sys
import os
import unittest

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ass_generator
from templates import TEMPLATES, get_template

class TestASSTemplates(unittest.TestCase):
    def setUp(self):
        self.test_srt = "test_temp.srt"
        with open(self.test_srt, "w") as f:
            f.write("1\n00:00:00,000 --> 00:00:01,000\nHello World\n")
            
    def tearDown(self):
        if os.path.exists(self.test_srt):
            os.remove(self.test_srt)
        # Remove any generated ass files
        for name in TEMPLATES.keys():
            f = f"test_{name}.ass"
            if os.path.exists(f):
                os.remove(f)

    def test_all_templates_generation(self):
        print("\nTesting all templates...")
        for name, config in TEMPLATES.items():
            output_ass = f"test_{name}.ass"
            print(f"  Generating for template: {name}")
            
            # Generate
            ass_generator.generate_ass(self.test_srt, output_ass, config)
            
            self.assertTrue(os.path.exists(output_ass), f"ASS file not created for {name}")
            
            # Read and Verify content matches config
            with open(output_ass, "r") as f:
                content = f.read()
                
            # Check Font Name
            self.assertIn(config.font_name, content, f"Font name {config.font_name} not found in {name} ASS")
            
            # Check Font Size
            self.assertIn(str(config.font_size), content, f"Font size {config.font_size} not found in {name} ASS")
            
            # Check Primary Color (basic check)
            self.assertIn(config.primary_color, content, f"Primary color {config.primary_color} not found in {name} ASS")

            print(f"  [PASS] Template {name} verified.")

if __name__ == "__main__":
    unittest.main()
