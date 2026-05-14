<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
}>()
</script>

<template>
  <div class="slidev-layout section h-full flex flex-col justify-center">
    <slot name="default">
      <h1 v-if="title">{{ title }}</h1>
      <h2 v-if="subtitle">{{ subtitle }}</h2>
    </slot>
  </div>
</template>
