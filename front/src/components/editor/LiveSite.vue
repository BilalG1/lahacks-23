<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { config } from '../../constants/config';
import { useQuasar } from 'quasar';

const $q = useQuasar()
const show  = ref(false)
const iframe = ref()
const id = ref()

onMounted(() => {
  fetch(`${config.apiUrl}/gen-id`)
    .then(res => res.json())
    .then(curId => {
      id.value = curId
      if (curId === false) {
        $q.notify('Out of users, reset')
      }
      localStorage.id = id.value
    })
})
const handleRefresh = () => {
  // iframe.value.contentWindow.location.reload();
  iframe.value.src = iframe.value.src
}
const openUrl = () => {
  window.open(`https://u${id.value}.bazzled.com/`)
}
</script>

<template>
  <Transition name="fade-up">
    <iframe 
      v-show="show"
      :src="`https://u${id}.bazzled.com/`" 
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