<script setup lang="ts">
import { config } from '../../constants/config';

const reset = () => {
  fetch(`${config.apiUrl}/reset-ids`, { method: 'POST' })
  for (let i = 375; i < 379; i++) {
    fetch(`${config.apiUrl}/containers/${i}`, { method: 'DELETE' })
  }
}
</script>

<template>
  <div class="absolute inset-0 flex justify-center items-center">
    <q-btn color="primary" label="reset" @click="reset" />
  </div>
</template>