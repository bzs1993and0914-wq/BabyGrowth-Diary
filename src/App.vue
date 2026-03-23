<template>
  <div id="app-root">
    <AppHeader />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

onMounted(() => {
  settingsStore.fetchSettings()
})
</script>

<style scoped>
#app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s, color 0.3s;
}

.main-content {
  flex: 1;
  padding: 84px 24px 40px;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
