<!--
Slidev embed: Vue component wrapping asciinema-player.

PREREQUISITES (one-time setup per Slidev project):

1. Install the npm package:
     npm install asciinema-player

2. Create `components/AsciinemaPlayer.vue`:

     <script setup lang="ts">
     import { onMounted, ref } from 'vue'
     import * as AsciinemaPlayer from 'asciinema-player'
     import 'asciinema-player/dist/bundle/asciinema-player.css'

     const props = defineProps<{
       src: string
       cols?: number
       rows?: number
       autoplay?: boolean
       loop?: boolean
       theme?: string
     }>()

     const el = ref<HTMLElement | null>(null)

     onMounted(() => {
       if (el.value) {
         AsciinemaPlayer.create(props.src, el.value, {
           cols: props.cols ?? 100,
           rows: props.rows ?? 30,
           autoPlay: props.autoplay ?? false,
           loop: props.loop ?? true,
           theme: props.theme ?? 'monokai',
         })
       }
     })
     </script>

     <template><div ref="el" /></template>

3. Place demo.cast in `public/` so Vite serves it from `/demo.cast`.

USAGE in any slide:
-->

<AsciinemaPlayer
  src="/demo.cast"
  :cols="100"
  :rows="30"
  :autoplay="false"
  :loop="true"
  theme="monokai"
/>

<!--
For PDF export (`slidev export`), the live player renders via Playwright;
the resulting PDF will show the first frame statically. If you need the
PDF to show the demo in motion, also embed a static GIF on the same slide
and conditionally hide one via `v-if="$slidev.nav.exportToPdf"`.
-->
