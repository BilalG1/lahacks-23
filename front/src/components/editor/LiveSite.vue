<script setup lang="ts">
import { ref } from 'vue';

const show  = ref(false)
const iframe = ref()
const id = Math.floor(Math.random() * 4 + 5)
const url = `https://u37${id}.bazzled.com/`

const handleRefresh = () => {
  // iframe.value.contentWindow.location.reload();
  iframe.value.src = iframe.value.src
}
const openUrl = () => {
  window.open(url)
}
</script>

<template>
  <Transition name="fade-up">
    <iframe 
      v-show="show"
      :src="url" 
      ref="iframe"
      class="border border-white absolute right-0 top-0"
      style="right: 0; top: 0; width: 600px; height: 800px; border-radius: 12px;" 
    />
  </Transition>
  <div class="absolute top-1 right-1">
    <q-btn v-if="show" icon="link" color="primary" class="mr-1" unelevated @click="openUrl" />
    <q-btn v-if="show" icon="refresh" color="primary" class="mr-1" unelevated @click="handleRefresh" />
    <q-btn :label="show ? 'Hide' : 'Show'" color="primary" @click="show = !show" unelevated />
  </div>
</template>