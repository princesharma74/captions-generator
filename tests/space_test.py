from manim import *

class SpaceTest(Scene):
    def construct(self):
        t = Text("A B C")
        print(f"DEBUG: Text('A B C') has {len(t)} submobjects")
        for i, sub in enumerate(t):
            print(f"DEBUG: Submobject {i}: {sub}")

        t2 = Text("Hello   World")
        print(f"DEBUG: Text('Hello   World') has {len(t2)} submobjects")

