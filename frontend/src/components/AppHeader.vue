<template>
  <header class="app-header">
    <span class="app-title">PlannerwithExpense</span>
    <nav>
      <router-link to="/calendar" :class="{ active: $route.name === 'calendar' }">カレンダー</router-link>
      <router-link to="/expenses" :class="{ active: $route.name === 'expenses' }">家計簿</router-link>
      <a href="#" @click.prevent="handleLogout">ログアウト</a>
    </nav>
  </header>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>
