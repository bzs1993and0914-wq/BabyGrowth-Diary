<template>
  <div id="app-root">
    <AppHeader v-if="!route.meta.hideHeader" />
    <AppNav v-if="showTabBar" />

    <main
      class="main-content"
      :class="{
        'main-content--full': route.meta.hideHeader,
      }"
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
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'
import AppNav from '@/components/common/AppNav.vue'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { useDailyRecordNudge } from '@/composables/useDailyRecordNudge'
import { navRouteNames } from '@/config/nav'

const route = useRoute()
const settingsStore = useSettingsStore()
const auth = useAuthStore()

useDailyRecordNudge()

const showTabBar = computed(() =>
  !route.meta.hideHeader && navRouteNames.has(route.name as string),
)

onMounted(() => {
  if (auth.isAuthenticated) {
    settingsStore.fetchSettings()
  }
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
  padding-top: var(--header-height, 60px);
  transition:
    background-color 0.3s,
    color 0.3s;
}

.main-content {
  flex: 1;
  padding: 20px 24px 40px;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.main-content--full {
  padding: 0;
  max-width: none;
}

@media (max-width: 767px) {
  #app-root {
    padding-top: var(--header-height-mobile, 54px);
  }

  .main-content {
    padding: 16px 14px 28px;
    padding-bottom: max(28px, env(safe-area-inset-bottom, 0px));
    max-width: none;
  }
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
