<script setup lang="ts">
import { config } from '../../constants/config';

const reset = () => {
  fetch(`${config.apiUrl}/reset-ids`, { method: 'POST' })
}
</script>

<template>
  <div class="absolute inset-0 flex justify-center items-center">
    <q-btn color="primary" label="reset" @click="reset" />
  </div>
</template>