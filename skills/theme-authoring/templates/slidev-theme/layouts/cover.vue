<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
  author?: string
  date?: string
}>()
</script>

<template>
  <div class="slidev-layout cover h-full flex flex-col justify-center">
    <slot name="default">
      <h1 v-if="title">{{ title }}</h1>
      <h2 v-if="subtitle">{{ subtitle }}</h2>
    </slot>
    <div class="absolute bottom-12 left-0 right-0 text-center text-sm opacity-70">
      <slot name="footer">
        <span v-if="author">{{ author }}</span>
        <span v-if="author && date"> &middot; </span>
        <span v-if="date">{{ date }}</span>
      </slot>
    </div>
  </div>
</template>
