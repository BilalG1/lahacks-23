<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import vueLogo from '@/assets/logos/vue-logo.svg'
import reactLogo from '@/assets/logos/react-logo.svg'
import svelteLogo from '@/assets/logos/svelte-logo.svg'

const router = useRouter()

const groupDelay = 130
const frontendOptions = [
  { name: 'Vue', logo: vueLogo},
  { name: 'React', logo: reactLogo},
  { name: 'Svelte', logo: svelteLogo},
]
const backendOptions = [
  { name: 'Express', logo: 'https://www.vectorlogo.zone/logos/expressjs/expressjs-icon.svg', whiteBg: true},
  { name: 'Golang', logo: 'https://www.vectorlogo.zone/logos/golang/golang-icon.svg', },
  { name: 'Flask', logo: 'https://www.vectorlogo.zone/logos/pocoo_flask/pocoo_flask-icon.svg', whiteBg: true},
]
const databaseOptions = [
  { name: 'MongoDB', logo: 'https://www.vectorlogo.zone/logos/mongodb/mongodb-icon.svg'},
  { name: 'MySQL', logo: 'https://www.vectorlogo.zone/logos/mysql/mysql-icon.svg'},
  { name: 'PostgreSQL', logo: 'https://www.vectorlogo.zone/logos/postgresql/postgresql-icon.svg'},
]

const frontendChoice = ref('')
const backendChoice = ref('')
const databaseChoice = ref('')

const handleNext = () => {
  localStorage.frontendChoice = frontendChoice.value
  localStorage.backendChoice = backendChoice.value
  localStorage.databaseChoice = databaseChoice.value
  router.push(`/new-prompt`)
}
</script>

<template>
  <div class="px-4 py-8 max-w-screen-md mx-auto">
    <div class="text-2xl font-bold pb-10">New project</div>

    <div :class="`text-xl pb-2 italic ${frontendChoice ? 'text-primary' : ''}`">Frontend</div>
    <div class="flex flex-row gap-2">
      <Transition name="fade-up" v-for="opt, ind in frontendOptions"  appear>
        <div 
          :class="`bg-black rounded-xl grow`"
          :style="`transition-delay: ${ind * groupDelay + 300}ms`"
        >
          <div 
            :class="[
              `border-2 ${ frontendChoice === opt.name ? 'border-gray-300' : 'border-gray-800'}`,
              'hover:border-gray-50 p-8 rounded-xl cursor-pointer'
            ]"
            @click="frontendChoice = opt.name"
          >
            <div class="text-center text-lg pb-4">{{ opt.name}}</div>
            <img :src="opt.logo" class="mx-auto h-20"/>
          </div>
        </div>
      </Transition>
    </div>

    <div :class="`text-xl pb-2 italic pt-10 ${backendChoice ? 'text-primary' : ''}`">Backend</div>
    <div class="flex flex-row gap-2">
      <Transition name="fade-up" v-for="opt, ind in backendOptions"  appear>
        <div 
          :class="`bg-black rounded-xl grow`"
          :style="`transition-delay: ${ind * groupDelay + 800}ms`"
        >
          <div 
            :class="[
              `border-2 ${ backendChoice === opt.name ? 'border-gray-300' : 'border-gray-800'}`,
              'hover:border-gray-50 p-8 rounded-xl cursor-pointer'
            ]"
            @click="backendChoice = opt.name"
          >
            <div class="text-center text-lg pb-4">{{ opt.name}}</div>
            <img :src="opt.logo" :class="`mx-auto h-20 ${opt.whiteBg ? 'bg-white rounded-2xl' : ''}`"/>
          </div>
        </div>
      </Transition>
    </div>

    <div :class="`text-xl pb-2 italic pt-10 ${databaseChoice ? 'text-primary' : ''}`">Database</div>
    <div class="flex flex-row gap-2">
      <Transition name="fade-up" v-for="opt, ind in databaseOptions"  appear>
        <div 
          :class="`bg-black rounded-xl grow`"
          :style="`transition-delay: ${ind * groupDelay + 1300}ms`"
        >
          <div 
            :class="[
              `border-2 ${ databaseChoice === opt.name ? 'border-gray-300' : 'border-gray-800'}`,
              'hover:border-gray-50 p-8 rounded-xl cursor-pointer'
            ]"
            @click="databaseChoice = opt.name"
          >
            <div class="text-center text-lg pb-4">{{ opt.name}}</div>
            <img :src="opt.logo" class="mx-auto h-20"/>
          </div>
        </div>
      </Transition>
    </div>

    <div class="text-center">
      <q-btn label="next" :disabled="!frontendChoice || !backendChoice || !databaseChoice" color="primary" class="mt-10" @click="handleNext"/>
    </div>
  </div>
</template>