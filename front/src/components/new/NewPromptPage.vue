<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar'
import { config } from '../../constants/config'

const $q = useQuasar()
const prompt = ref('')
const loading = ref(false)
const filesPlanned = ref<{ file: string, purpose: string }[]>([])
const stage = ref<0 | 1>(0)
const showAddDialog = ref(false)
const shutoff = ref(1)
const addingFilePath = ref('')
const addingPurpose = ref('')

const handleNext = async () => {
  loading.value = true
  const headers = { 'Content-type': 'application/json' }
  const body = JSON.stringify({ objective: prompt.value })
  const data = await fetch(config.apiUrl + '/gen-plan', { method: 'POST', headers, body })
    .then(r => r.json())
    .catch(() => $q.notify({ message: 'Error with request', color: 'red' }))

  try {
    filesPlanned.value = eval(data.replaceAll('```',''))
    stage.value = 1
  } catch {
    $q.notify({ message: 'Error with response. Please try again', color: 'red' })
  }
  loading.value = false
}

const moveItem = (ind: number, way: 'up' | 'down') => {
  shutoff.value = 0
  const isUp = (way === 'up')
  if ((ind === 0 && isUp) || (ind === (filesPlanned.value.length - 1) && !isUp))
    return
  
  const indSwap = ind + (isUp ? -1 : 1)
  const temp = filesPlanned.value[ind]
  filesPlanned.value[ind] = filesPlanned.value[indSwap]
  filesPlanned.value[indSwap] = temp
}
const confirmDelete = (ind: number) => {
  shutoff.value = 0;
  $q.dialog({ message: 'Are you sure you want to remove this file from your plan?', cancel: true })
    .onOk(() => filesPlanned.value.splice(ind, 1))
}
const addItem = () => {
  shutoff.value = 0
  if (!addingFilePath.value || !addingPurpose.value)
    return $q.notify('File path and purpose are required')
  
  showAddDialog.value = false
  const curFile = { file: addingFilePath.value, purpose: addingPurpose.value }
  filesPlanned.value.push(curFile)
}
</script>

<template>
  <div v-if="stage === 0" class="text-center px-4 pt-10">
    <Transition name="fade-up" appear>
      <div class="text-2xl font-bold mb-10 delay-1000f">Enter your website idea here:</div>
    </Transition>
    <q-input
      v-model="prompt"
      type="textarea"
      class="max-w-lg mx-auto"
      :maxlength="300"
      outlined
      autogrow
      dark
    />
    <div class="text-gray-200 mt-1 mb-8">max 300 chars</div>
    <q-btn label="Next" :disabled="!prompt" :loading="loading" color="white" class="text-black" @click="handleNext" />
  </div>

  <div v-else class="mx-auto max-w-screen-md px-4 pt-10">
    <div class="flex flex-row justify-between mb-4">
      <div class="text-xl font-bold">Frontend File Plan:</div>
      <q-btn label="add" color="primary" rounded @click="showAddDialog = true"/>
    </div>
    <TransitionGroup name="group-move">
      <Transition v-for="file, ind in filesPlanned" name="fade-left" :key="file.file" appear>
        <div class="rounded-xl bg-gray-700 mb-2 px-4 py-2 flex flex-row justify-between items-center" :style="`transition-delay: ${100*ind*shutoff}ms`">
          <div>
            <div class="text-primary">{{ ind+1 }}. {{ file.file }}</div>
            <div class="text-gray-200">{{ file.purpose }}</div>
          </div>
          <div>
            <q-icon name="expand_more" class="text-gray-300 hover:text-white cursor-pointer" size="20px" @click="() => moveItem(ind, 'down')" />
            <q-icon name="expand_less" class="text-gray-300 hover:text-white cursor-pointer" size="20px" @click="() => moveItem(ind, 'up')"/>
            <q-icon name="delete" class="cursor-pointer text-red-300 hover:text-white" size="20px" @click="() => confirmDelete(ind)"/>
          </div>
        </div>
      </Transition>
    </TransitionGroup>
    <div class="text-center mt-10">
      <q-btn label="Looks Good" color="primary"  />
    </div>
  </div>

  <q-dialog v-model="showAddDialog">
    <q-card class="px-4" style="min-width: 300px">
      <div class="pt-4 pb-4 font-bold text-xl">Add to Plan</div>
      <q-input label="File Path" v-model="addingFilePath" />
      <q-input class="pb-2" label="Purpose" v-model="addingPurpose" />
      <div class="text-right pb-2 pt-4">
        <q-btn label="add" color="primary" unelevated @click="addItem"/>
      </div>
    </q-card>
  </q-dialog>
</template>