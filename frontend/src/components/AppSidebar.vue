<template>
  <aside class="app-sidebar">
    <span class="app-title">PlannerwithExpense</span>
    <nav>
      <router-link to="/calendar" :class="{ active: $route.name === 'calendar' }">カレンダー</router-link>
      <router-link to="/expenses" :class="{ active: $route.name === 'expenses' }">家計簿</router-link>
      <router-link :to="yearlyBudgetLink" :class="{ active: $route.name === 'yearly-budget' }">累計</router-link>
      <a href="#" @click.prevent="handleLogout">ログアウト</a>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const yearlyBudgetLink = computed(() => ({
  name: "yearly-budget",
  params: { year: new Date().getFullYear() },
}));

function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>
