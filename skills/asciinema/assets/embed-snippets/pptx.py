"""
pptx embed: insert an animated GIF (converted from asciinema .cast) into a
PowerPoint slide. PowerPoint plays GIFs in slideshow mode, not in normal view.

Prerequisites:
  1. Convert cast to GIF:
       agg demo.cast demo.gif --theme monokai --font-size 18 --cols 100 --rows 30
  2. Install python-pptx:
       pip install python-pptx

This snippet is invoked from generate.py in the pptx skill, but can be used
standalone — drop a slide spec in your deck.yaml like:

    - layout: image
      title: "Terminal demo"
      image: ./demo.gif
      caption: "Recorded with asciinema; converted via agg"

The generator then emits the equivalent of the code below.
"""

from pptx import Presentation
from pptx.util import Inches, Pt


def add_asciinema_slide(
    prs: Presentation,
    title: str,
    gif_path: str,
    caption: str = "",
) -> None:
    """Add a slide with an embedded asciinema-derived GIF."""
    slide_layout = prs.slide_layouts[5]  # Title and Content (no body placeholder)
    slide = prs.slides.add_slide(slide_layout)

    # Title
    slide.shapes.title.text = title

    # GIF placement: centered, ~85 % of slide width
    slide_w = prs.slide_width
    slide_h = prs.slide_height
    gif_w = int(slide_w * 0.85)
    # python-pptx doesn't read GIF dimensions; calculate height assuming 16:9-ish
    # aspect from cols=100 rows=30 font-size=18 -> approx 1800x630
    gif_h = int(gif_w * 630 / 1800)
    left = int((slide_w - gif_w) / 2)
    top = int((slide_h - gif_h) / 2)
    slide.shapes.add_picture(gif_path, left, top, width=gif_w, height=gif_h)

    # Caption (optional)
    if caption:
        from pptx.util import Inches as I
        caption_top = top + gif_h + I(0.2)
        caption_box = slide.shapes.add_textbox(
            left, caption_top, gif_w, I(0.4)
        )
        tf = caption_box.text_frame
        tf.text = caption
        tf.paragraphs[0].font.size = Pt(12)
        tf.paragraphs[0].font.italic = True


if __name__ == "__main__":
    prs = Presentation()
    add_asciinema_slide(
        prs,
        title="Terminal demo",
        gif_path="./demo.gif",
        caption="Recorded with asciinema; converted via agg",
    )
    prs.save("demo-with-cast.pptx")
    print("Wrote demo-with-cast.pptx")
