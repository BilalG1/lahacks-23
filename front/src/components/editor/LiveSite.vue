<script setup lang="ts">
import { ref } from 'vue';

const show  = ref(false)
const url = `https://u37${Math.floor(Math.random() * 4 + 5)}.bazzled.com/`
</script>

<template>
  <Transition name="fade-up">
    <iframe 
      v-show="show"
      :src="url" 
      class="border border-white absolute right-0 top-0"
      style="right: 0; top: 0; width: 600px; height: 800px; border-radius: 12px;" 
    />
  </Transition>
  <q-btn :label="show ? 'Hide' : 'Show'" class="absolute top-1 right-1" color="primary" @click="show = !show" />
</template>