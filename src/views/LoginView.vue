<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const submitting = ref(false)

async function onSubmit() {
  if (!username.value.trim() || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  submitting.value = true
  try {
    await auth.login({
      username: username.value.trim(),
      password: password.value,
    })
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.replace(redirect)
  } catch (e: unknown) {
    const msg =
      (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
      '登录失败'
    ElMessage.error(typeof msg === 'string' ? msg : '登录失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="never">
      <h1 class="title">登录 BabyGrow</h1>
      <p class="hint">本地数据仅保存在本机。若忘记密码，请使用设置中的修改密码功能。</p>
      <el-form label-position="top" @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="password"
            type="password"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="submitting" native-type="submit">
          登录
        </el-button>
        <el-button text type="primary" class="link" @click="router.push('/register')">
          没有账号？去注册
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--bg-secondary);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
}

.title {
  margin: 0 0 8px;
  font-size: 22px;
  color: var(--text-primary);
}

.hint {
  margin: 0 0 20px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.submit {
  width: 100%;
  margin-top: 8px;
}

.link {
  width: 100%;
  margin-top: 12px;
}
</style>
