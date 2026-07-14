<template>
  <div class="auth-card">
    <h1>PlannerwithExpense</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-row">
        <label for="email">メールアドレス</label>
        <input id="email" v-model="email" type="email" placeholder="example@mail.com" required />
      </div>
      <div class="form-row">
        <label for="password">パスワード</label>
        <input id="password" v-model="password" type="password" placeholder="********" required />
      </div>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <div class="submit-row">
        <button type="submit">ログイン</button>
      </div>
    </form>
    <div class="switch-link">
      アカウントをお持ちでない方は<br />
      <router-link to="/register">新規登録はこちら</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const email = ref("");
const password = ref("");
const errorMessage = ref("");
const router = useRouter();
const auth = useAuthStore();

async function handleSubmit() {
  errorMessage.value = "";
  try {
    await auth.login(email.value, password.value);
    router.push({ name: "calendar" });
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || "ログインに失敗しました";
  }
}
</script>
