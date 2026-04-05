<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import ErrorToast from '@/components/ErrorToast.vue'
import { useFormValidation } from '@/composables/useFormValidation'
import { loginSchema } from '@/schemas'
import { useAuthStore } from '@/stores/useAuthStore'

const router = useRouter()
const authStore = useAuthStore()

const showErrorToast = ref(false)

// 使用 Zod 表單驗證
const { form, errors, validateAll, touchField, getFieldError } = useFormValidation(
  loginSchema,
  {
    email: '',
    password: '',
  },
)

async function handleSubmit() {
  // 驗證整個表單
  if (!validateAll()) {
    return
  }

  try {
    await authStore.loginWithPassword(form.email, form.password)
    router.push('/')
  }
  catch {
    showErrorToast.value = true
  }
}
</script>

<template>
  <ErrorToast :visible="showErrorToast" @close="showErrorToast = false" />
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-card__heading">
        歡迎回來
      </h1>
      <p class="auth-card__subheading">
        登入 NCU TLDR 繼續探索課程評價
      </p>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="auth-form__field">
          <label for="login-email" class="auth-form__label">
            電子信箱
          </label>
          <input
            id="login-email"
            v-model="form.email"
            type="email"
            class="auth-form__input"
            :class="{ 'auth-form__input--error': getFieldError('email') }"
            placeholder="11xxxxxxx@cc.ncu.edu.tw"
            autocomplete="email"
            @blur="touchField('email')"
          >
          <p v-if="getFieldError('email')" class="auth-form__field-error">
            {{ getFieldError('email') }}
          </p>
        </div>

        <div class="auth-form__field">
          <label for="login-password" class="auth-form__label">
            密碼
          </label>
          <input
            id="login-password"
            v-model="form.password"
            type="password"
            class="auth-form__input"
            :class="{ 'auth-form__input--error': getFieldError('password') }"
            placeholder="請輸入密碼"
            autocomplete="current-password"
            @blur="touchField('password')"
          >
          <p v-if="getFieldError('password')" class="auth-form__field-error">
            {{ getFieldError('password') }}
          </p>
        </div>

        <div class="auth-form__options">
          <a href="#" class="auth-form__forgot" @click.prevent>
            忘記密碼？
          </a>
        </div>

        <p v-if="errors._form" class="auth-form__error">
          {{ errors._form }}
        </p>

        <button
          type="submit"
          class="auth-form__submit"
          :disabled="authStore.isLoading"
        >
          {{ authStore.isLoading ? '登入中...' : '登入' }}
        </button>
      </form>

      <div class="auth-divider">
        <span class="auth-divider__text">
          或使用以下方式登入
        </span>
      </div>

      <div class="auth-social">
        <button class="auth-social__btn" aria-label="使用 Google 登入" @click.prevent>
          <svg viewBox="0 0 488 512" height="1em" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"
            />
          </svg>
        </button>
        <button class="auth-social__btn" aria-label="使用 Apple 登入" @click.prevent>
          <svg viewBox="0 0 384 512" height="1em" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"
            />
          </svg>
        </button>
      </div>

      <p class="auth-card__footer">
        還沒有帳號？
        <RouterLink to="/register" class="auth-card__link">
          立即註冊
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: var(--spacing-xl);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl) var(--spacing-xl);
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(127, 169, 184, 0.12);
}

.auth-card__heading {
  text-align: center;
  font-weight: 700;
  font-size: var(--font-size-2xl);
  color: var(--color-accent-primary);
  margin-bottom: var(--spacing-xs);
}

.auth-card__subheading {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-xl);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.auth-form__field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.auth-form__label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.auth-form__input {
  width: 100%;
  background: var(--color-background);
  padding: 14px var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1.5px solid transparent;
  box-shadow: var(--shadow-sm);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.auth-form__input::placeholder {
  color: var(--color-text-muted);
}

.auth-form__input:focus {
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 3px rgba(127, 169, 184, 0.15);
}

.auth-form__options {
  display: flex;
  justify-content: flex-end;
}

.auth-form__forgot {
  font-size: var(--font-size-xs);
  color: var(--color-accent-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.auth-form__forgot:hover {
  color: var(--color-text-primary);
}

.auth-form__input--error {
  border-color: var(--color-error, #c0392b) !important;
}

.auth-form__field-error {
  font-size: var(--font-size-xs);
  color: var(--color-error, #c0392b);
  margin-top: 4px;
}

.auth-form__error {
  font-size: var(--font-size-sm);
  color: var(--color-error);
  text-align: center;
  padding: var(--spacing-sm);
  background: rgba(192, 57, 43, 0.06);
  border-radius: var(--radius-sm);
}

.auth-form__submit {
  width: 100%;
  font-weight: 600;
  background: linear-gradient(135deg, var(--color-accent-primary) 0%, var(--color-accent-teal) 100%);
  color: white;
  padding: 14px;
  margin-top: var(--spacing-sm);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 20px rgba(127, 169, 184, 0.35);
  border: none;
  font-size: var(--font-size-base);
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.auth-form__submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(127, 169, 184, 0.4);
}

.auth-form__submit:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(127, 169, 184, 0.3);
}

.auth-form__submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-divider {
  display: flex;
  align-items: center;
  margin: var(--spacing-lg) 0;
  gap: var(--spacing-md);
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-background-alt);
}

.auth-divider__text {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
}

.auth-social {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
}

.auth-social__btn {
  display: grid;
  place-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-background);
  border: 1.5px solid var(--color-background-alt);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.auth-social__btn svg {
  fill: var(--color-text-secondary);
  transition: fill var(--transition-fast);
}

.auth-social__btn:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-md);
  border-color: var(--color-accent-primary);
}

.auth-social__btn:hover svg {
  fill: var(--color-accent-primary);
}

.auth-social__btn:active {
  transform: scale(0.95);
}

.auth-card__footer {
  text-align: center;
  margin-top: var(--spacing-lg);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.auth-card__link {
  color: var(--color-accent-primary);
  font-weight: 600;
  text-decoration: none;
  transition: color var(--transition-fast);
}

.auth-card__link:hover {
  color: var(--color-text-primary);
}

@media (max-width: 480px) {
  .auth-card {
    padding: var(--spacing-xl) var(--spacing-lg);
    border-radius: var(--radius-lg);
  }

  .auth-card__heading {
    font-size: var(--font-size-xl);
  }
}
</style>
