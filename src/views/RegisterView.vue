<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import BabyBgSvg from '@/components/BabyBgSvg.vue'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const password2 = ref('')
const submitting = ref(false)

async function onSubmit() {
  if (!username.value.trim() || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (password.value.length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  if (password.value !== password2.value) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  submitting.value = true
  try {
    await auth.register({
      username: username.value.trim(),
      password: password.value,
    })
    ElMessage.success('注册成功')
    router.replace('/')
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data
      ?.detail
    ElMessage.error(typeof detail === 'string' ? detail : '注册失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <BabyBgSvg />
    <el-card class="auth-card" shadow="never">
      <h1 class="title">注册账号</h1>
      <p class="hint">账号与成长记录仅保存在本机，请妥善保管密码。</p>
      <el-form label-position="top" @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码（至少 6 位）">
          <el-input
            v-model="password"
            type="password"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="password2"
            type="password"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="submitting" native-type="submit">
          注册并登录
        </el-button>
        <el-button text type="primary" class="link" @click="router.push('/login')">
          已有账号？去登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.auth-page {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f0f5;
  overflow: hidden;
}

.auth-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow:
    0 8px 32px rgba(180, 140, 160, 0.12),
    0 2px 8px rgba(180, 140, 160, 0.06);
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
