<template>
  <div class="px-4 min-h-screen max-w-screen-lg mx-auto flex justify-center align-middle content-center">
    <div>
      <Transition name="fade-up" appear>
        <div class="text-6xl font-extrabold text-center">Collaborative Web Development With AI</div>
      </Transition>
      <div class="text-center">
        <Transition name="fade-up-delay" appear>
          <div>
            <div><RouterLink to="/new">
                <q-btn label="New Project" color="primary" size="lg" style="padding-left: 30px; padding-right: 30px;" class="mt-10" rounded/>
            </RouterLink></div>
            <div><RouterLink to="/editor">
                <q-btn label="Open Editor" color="primary" size="lg" style="padding-left: 30px; padding-right: 30px;" class="mt-10" rounded/>
            </RouterLink></div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>
