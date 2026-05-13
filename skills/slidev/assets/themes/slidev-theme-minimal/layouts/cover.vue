<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
  author?: string
  date?: string
}>()
</script>

<template>
  <div class="slidev-layout cover h-full flex flex-col items-center justify-center text-center">
    <div class="flex-1 flex flex-col items-center justify-center gap-4">
      <slot name="default">
        <h1 v-if="title">{{ title }}</h1>
        <h2 v-if="subtitle">{{ subtitle }}</h2>
      </slot>
    </div>
    <div class="pb-12 text-sm opacity-70">
      <slot name="footer">
        <span v-if="author">{{ author }}</span>
        <span v-if="author && date"> &middot; </span>
        <span v-if="date">{{ date }}</span>
      </slot>
    </div>
  </div>
</template>
