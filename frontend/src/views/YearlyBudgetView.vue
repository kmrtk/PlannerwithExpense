<template>
  <AppHeader />
  <main>
    <div class="month-nav">
      <router-link class="link" :to="{ name: 'yearly-budget', params: { year: year - 1 } }">← 前年</router-link>
      <span class="calendar-title">{{ year }}年</span>
      <router-link class="link" :to="{ name: 'yearly-budget', params: { year: year + 1 } }">次年 →</router-link>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>月</th>
          <th>収入</th>
          <th>支出</th>
          <th>貯蓄実績</th>
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
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import AppHeader from "../components/AppHeader.vue";
import { getYearlySummary } from "../api/budgets";

const route = useRoute();
const year = computed(() => Number(route.params.year));
const summary = ref([]);

async function fetchYearData() {
  const { data } = await getYearlySummary(year.value);
  summary.value = data;
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

watch(year, fetchYearData, { immediate: true });
</script>
