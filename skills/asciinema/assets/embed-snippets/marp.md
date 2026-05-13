<!--
Marp embed: live asciinema-player web component.
Requires Marp HTML export (PDF/PPTX strip JS). Set `html: true` in
marp.config.js or pass `--html` to marp-cli.

Place demo.cast next to your slides.md or in a sub-directory; the path
in `src` is resolved relative to the rendered HTML, not the markdown.
-->

<script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.7.1/dist/bundle/asciinema-player.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.7.1/dist/bundle/asciinema-player.css" />

<asciinema-player
  src="./demo.cast"
  cols="100"
  rows="30"
  autoplay="false"
  loop="true"
  speed="1.0"
  theme="monokai"
></asciinema-player>

<!--
For PDF/PPTX export from Marp, this player will not render. Use a static
GIF instead:

  agg demo.cast demo.gif --theme monokai

Then embed via standard Markdown image syntax:

  ![demo](./demo.gif)
-->
