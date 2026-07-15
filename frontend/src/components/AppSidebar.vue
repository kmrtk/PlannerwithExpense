<template>
  <aside class="app-sidebar" :class="{ collapsed: !sidebar.isOpen }">
    <button class="sidebar-toggle" @click="sidebar.toggle()">{{ sidebar.isOpen ? "‹" : "›" }}</button>
    <template v-if="sidebar.isOpen">
      <span class="app-title">PlannerwithExpense</span>
      <nav>
        <div class="nav-item">
          <router-link to="/calendar" :class="{ active: $route.name === 'calendar' }">カレンダー</router-link>
          <button class="chevron" @click="toggleSection('calendar')">
            {{ expandedSection === "calendar" ? "▾" : "▸" }}
          </button>
        </div>
        <div v-if="expandedSection === 'calendar'" class="nav-tree">
          <div v-for="y in years" :key="y" class="nav-tree-year">
            <button class="year-label" @click="toggleYear(y)">{{ y }}年</button>
            <div v-if="expandedYear === y" class="nav-tree-months">
              <router-link
                v-for="m in months"
                :key="m"
                :to="{ name: 'schedule-list', params: { year: y, month: m } }"
                class="month-link"
              >
                {{ m }}月
              </router-link>
            </div>
          </div>
        </div>

        <div class="nav-item">
          <router-link to="/expenses" :class="{ active: $route.name === 'expenses' }">家計簿</router-link>
          <button class="chevron" @click="toggleSection('expenses')">
            {{ expandedSection === "expenses" ? "▾" : "▸" }}
          </button>
        </div>
        <div v-if="expandedSection === 'expenses'" class="nav-tree">
          <div v-for="y in years" :key="y" class="nav-tree-year">
            <button class="year-label" @click="toggleYear(y)">{{ y }}年</button>
            <div v-if="expandedYear === y" class="nav-tree-months">
              <router-link
                v-for="m in months"
                :key="m"
                :to="{ name: 'expenses-month', params: { year: y, month: m } }"
                class="month-link"
              >
                {{ m }}月
              </router-link>
            </div>
          </div>
        </div>

        <router-link :to="yearlyBudgetLink" :class="{ active: $route.name === 'yearly-budget' }">累計</router-link>
        <a href="#" @click.prevent="handleLogout">ログアウト</a>
      </nav>
    </template>
  </aside>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useSidebarStore } from "../stores/sidebar";

const router = useRouter();
const auth = useAuthStore();
const sidebar = useSidebarStore();

const expandedSection = ref(null);
const expandedYear = ref(null);

const years = computed(() => {
  const currentYear = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, i) => currentYear - 3 + i);
});
const months = Array.from({ length: 12 }, (_, i) => i + 1);

const yearlyBudgetLink = computed(() => ({
  name: "yearly-budget",
  params: { year: new Date().getFullYear() },
}));

function toggleSection(section) {
  if (expandedSection.value === section) {
    expandedSection.value = null;
    expandedYear.value = null;
  } else {
    expandedSection.value = section;
    expandedYear.value = null;
  }
}

function toggleYear(year) {
  expandedYear.value = expandedYear.value === year ? null : year;
}

function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>
