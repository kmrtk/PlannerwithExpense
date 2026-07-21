<template>
  <div class="app-layout">
  <AppSidebar />
  <main>
    <p v-if="loadError" class="error-message">{{ loadError }}</p>
    <p v-if="allTime.start_year" class="financial-summary-line">
      累計財務状況（{{ allTime.start_year }}年〜{{ allTime.end_year }}年）：
      <span class="savings-diff" :class="{ 'savings-negative': allTime.total_savings < 0 }">
        {{ allTime.total_savings >= 0 ? "+" : "" }}{{ allTime.total_savings.toLocaleString() }}円
      </span>
    </p>

    <div class="month-nav">
      <router-link class="link" :to="{ name: 'yearly-budget', params: { year: year - 1 } }">← 前年</router-link>
      <span class="calendar-title">{{ year }}年</span>
      <router-link class="link" :to="{ name: 'yearly-budget', params: { year: year + 1 } }">次年 →</router-link>
    </div>

    <p class="financial-summary-line">
      {{ year }}年度財務状況：
      <span class="savings-diff" :class="{ 'savings-negative': yearlyTotal < 0 }">
        {{ yearlyTotal >= 0 ? "+" : "" }}{{ yearlyTotal.toLocaleString() }}円
      </span>
    </p>

    <table class="data-table">
      <thead>
        <tr>
          <th>月</th>
          <th>収入</th>
          <th>支出</th>
          <th>財務状況</th>
          <th>貯蓄目標</th>
          <th>差分</th>
          <th>累積差分</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.month">
          <td>{{ row.month }}月</td>
          <td>{{ row.actual_income.toLocaleString() }}円</td>
          <td>{{ row.actual_expense.toLocaleString() }}円</td>
          <td>{{ row.actualSavings.toLocaleString() }}円</td>
          <td>{{ row.savings_target.toLocaleString() }}円</td>
          <td class="savings-diff" :class="{ 'savings-negative': row.diff < 0 }">
            {{ row.diff >= 0 ? "+" : "" }}{{ row.diff.toLocaleString() }}円
          </td>
          <td class="savings-diff" :class="{ 'savings-negative': row.cumulative < 0 }">
            {{ row.cumulative >= 0 ? "+" : "" }}{{ row.cumulative.toLocaleString() }}円
          </td>
        </tr>
      </tbody>
    </table>
  </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import AppSidebar from "../components/AppSidebar.vue";
import { getAllTimeSummary, getYearlySummary } from "../api/budgets";

const route = useRoute();
const year = computed(() => Number(route.params.year));
const summary = ref([]);
const allTime = ref({ start_year: null, end_year: null, total_savings: 0 });
const loadError = ref("");

let fetchSequence = 0;

async function fetchYearData() {
  const requestId = ++fetchSequence;
  try {
    const { data } = await getYearlySummary(year.value);
    if (requestId !== fetchSequence) return; // 古いリクエストの応答は無視(年送り連打時のレースコンディション対策)
    summary.value = data;
    loadError.value = "";
  } catch (error) {
    if (requestId !== fetchSequence) return;
    loadError.value = error.response?.data?.detail || "データの取得に失敗しました";
  }
}

async function fetchAllTimeSummary() {
  try {
    const { data } = await getAllTimeSummary();
    allTime.value = data;
    loadError.value = "";
  } catch (error) {
    loadError.value = error.response?.data?.detail || "データの取得に失敗しました";
  }
}

const rows = computed(() => {
  let cumulative = 0;
  return summary.value.map((m) => {
    const actualSavings = m.actual_income - m.actual_expense;
    const diff = actualSavings - m.savings_target;
    cumulative += diff;
    return { ...m, actualSavings, diff, cumulative };
  });
});

const yearlyTotal = computed(() => rows.value.reduce((sum, row) => sum + row.actualSavings, 0));

watch(year, fetchYearData, { immediate: true });
onMounted(fetchAllTimeSummary);
</script>
