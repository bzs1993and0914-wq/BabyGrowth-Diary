<template>
  <div id="app-root">
    <AppHeader v-if="!route.meta.hideHeader" />
    <main
      class="main-content"
      :class="{ 'main-content--full': route.meta.hideHeader }"
    >
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElNotification } from 'element-plus'
import AppHeader from '@/components/common/AppHeader.vue'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { startWebDailyRecordNudge } from '@/utils/dailyRecordNudgeWeb'

const route = useRoute()
const settingsStore = useSettingsStore()
const auth = useAuthStore()

onMounted(() => {
  if (auth.isAuthenticated) {
    settingsStore.fetchSettings()
  }

  startWebDailyRecordNudge()

  window.electronAPI?.onDailyRecordNudge?.((message) => {
    ElNotification({
      title: 'BabyGrow',
      message,
      type: 'info',
      duration: 10_000,
    })
  })
})

watch(
  () => auth.isAuthenticated,
  (ok) => {
    if (ok) settingsStore.fetchSettings()
  }
)
</script>

<style scoped>
#app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition:
    background-color 0.3s,
    color 0.3s;
}

.main-content {
  flex: 1;
  padding: 84px 24px 40px;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.main-content--full {
  padding: 0;
  max-width: none;
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
