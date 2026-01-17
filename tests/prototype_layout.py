from manim import *

class AlignmentTest(Scene):
    def construct(self):
        # 1. Old Method: Individual Text objects arranged
        words = ["The", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"]
        g_old = VGroup()
        for w in words:
            # Manim's Text by default centers mechanically, messing up baselines for mixed words
            g_old.add(Text(w, font_size=60))
        g_old.arrange(RIGHT, buff=0.1)
        g_old.to_edge(UP)
        
        self.add(g_old)
        self.add(Text("Method 1: VGroup.arrange (Bad Baseline)", font_size=24, color=RED).next_to(g_old, UP))

        # 2. New Method: Single Text Object
        sentence = " ".join(words)
        t_new = Text(sentence, font_size=60)
        t_new.to_edge(DOWN)
        
        self.add(t_new)
        self.add(Text("Method 2: Single Text Object (Correct Baseline)", font_size=24, color=GREEN).next_to(t_new, UP))
        
        # 3. Visualization of baseline
        line_old = Line(g_old.get_left(), g_old.get_right(), color=RED).move_to(g_old.get_bottom(), coor_mask=[0,1,0])
        line_new = Line(t_new.get_left(), t_new.get_right(), color=GREEN).move_to(t_new.get_bottom(), coor_mask=[0,1,0])
        
        self.add(line_old, line_new)

if __name__ == "__main__":
    # This part is just for manual run if needed, but we essentially run via manim command
    pass
