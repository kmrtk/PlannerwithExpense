<template>
  <div class="app-layout">
  <AppSidebar />
  <main>
    <div class="month-nav">
      <button class="link" @click="goToPrev">{{ viewMode === "week" ? "← 前週" : "← 前月" }}</button>
      <span class="calendar-title">{{ navTitle }}</span>
      <button class="link" @click="goToNext">{{ viewMode === "week" ? "次週 →" : "次月 →" }}</button>
      <div class="view-mode-toggle">
        <button :class="{ active: viewMode === 'month' }" class="secondary" @click="setViewMode('month')">月</button>
        <button :class="{ active: viewMode === 'week' }" class="secondary" @click="setViewMode('week')">週</button>
      </div>
    </div>

    <div class="budget-bar">
      <div class="budget-summary-row">収入: {{ actualIncome.toLocaleString() }}円</div>
      <div class="budget-summary-row">支出: {{ actualExpense.toLocaleString() }}円</div>
      <div class="budget-summary-row">
        財務状況: {{ actualSavings.toLocaleString() }}円 / 目標 {{ (budget?.savings_target ?? 0).toLocaleString() }}円
        <span class="savings-diff" :class="{ 'savings-negative': savingsDiff < 0 }">
          差分: {{ savingsDiff >= 0 ? "+" : "" }}{{ savingsDiff.toLocaleString() }}円
        </span>
      </div>
      <div class="budget-bar-actions">
        <router-link class="link" :to="{ name: 'yearly-budget', params: { year: displayYear } }">
          {{ displayYear }}年の累計を見る
        </router-link>
        <button class="secondary" @click="showBudgetModal = true">予算を設定</button>
      </div>
    </div>

    <div class="toolbar">
      <button @click="openAddSchedule(null)">＋ 予定追加</button>
      <button @click="openAddExpense(null)">＋ 支出追加</button>
    </div>
    <table class="calendar-table">
      <thead>
        <tr>
          <th v-for="label in weekLabels" :key="label">{{ label }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(week, wi) in rowsToRender" :key="wi">
          <td v-for="(day, di) in week" :key="di" :class="{ 'day-cell': day }" @click="day && handleCellClick(day)">
            <template v-if="day">
              {{ day.getDate() }}
              <span v-if="schedulesForDay(day).length" class="day-badge schedule-badge">予定あり</span>
              <span v-if="expensesForDay(day).some((e) => e.type === 'expense')" class="day-badge expense-badge">支出あり</span>
              <span v-if="expensesForDay(day).some((e) => e.type === 'income')" class="day-badge income-badge">収入あり</span>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </main>
  </div>

  <DayDetailModal
    v-if="showDayDetail"
    :date="detailDate"
    :schedules="detailSchedules"
    :expenses="detailExpenses"
    @close="detailDate = null"
    @add-schedule="openAddSchedule(null)"
    @edit-schedule="openEditSchedule"
    @delete-schedule="handleDeleteSchedule"
    @add-expense="openAddExpense(null)"
    @edit-expense="openEditExpense"
    @delete-expense="handleDeleteExpense"
  />

  <ScheduleModal
    v-if="showScheduleModal"
    ref="scheduleModalRef"
    :schedule="editingSchedule"
    :default-date="prefilledDate"
    @close="closeScheduleModal"
    @save="handleSaveSchedule"
    @delete="handleDeleteScheduleFromModal"
  />

  <ExpenseModal
    v-if="showExpenseModal"
    ref="expenseModalRef"
    :expense="editingExpense"
    :default-date="prefilledDate"
    @close="closeExpenseModal"
    @save="handleSaveExpense"
    @delete="handleDeleteExpenseFromModal"
  />

  <BudgetModal
    v-if="showBudgetModal"
    ref="budgetModalRef"
    :budget="budget"
    :year="displayYear"
    :month="displayMonth"
    @close="showBudgetModal = false"
    @save="handleSaveBudget"
  />
</template>

<script setup>
import { computed, ref, watch } from "vue";
import AppSidebar from "../components/AppSidebar.vue";
import ScheduleModal from "../components/ScheduleModal.vue";
import ExpenseModal from "../components/ExpenseModal.vue";
import DayDetailModal from "../components/DayDetailModal.vue";
import BudgetModal from "../components/BudgetModal.vue";
import { createSchedule, deleteSchedule, listSchedules, updateSchedule } from "../api/schedules";
import { createExpense, deleteExpense, listExpenses, updateExpense } from "../api/expenses";
import { getBudget, upsertBudget } from "../api/budgets";
import { scheduleOccursOnDate } from "../utils/recurrence";

const weekLabels = ["日", "月", "火", "水", "木", "金", "土"];

const today = new Date();
const displayYear = ref(today.getFullYear());
const displayMonth = ref(today.getMonth() + 1);

const schedules = ref([]);
const expenses = ref([]);
const budget = ref(null);

const showScheduleModal = ref(false);
const editingSchedule = ref(null);
const showExpenseModal = ref(false);
const editingExpense = ref(null);
const prefilledDate = ref(null);
const detailDate = ref(null);
const showBudgetModal = ref(false);
const scheduleModalRef = ref(null);
const expenseModalRef = ref(null);
const budgetModalRef = ref(null);

const showDayDetail = computed(() => !!detailDate.value && !showScheduleModal.value && !showExpenseModal.value);
const detailSchedules = computed(() =>
  detailDate.value ? schedules.value.filter((s) => scheduleOccursOnDate(s, detailDate.value)) : []
);
const detailExpenses = computed(() =>
  detailDate.value ? expenses.value.filter((e) => e.date === detailDate.value) : []
);

const actualIncome = computed(() =>
  expenses.value.filter((e) => e.type === "income").reduce((sum, e) => sum + e.amount, 0)
);
const actualExpense = computed(() =>
  expenses.value.filter((e) => e.type === "expense").reduce((sum, e) => sum + e.amount, 0)
);
const actualSavings = computed(() => actualIncome.value - actualExpense.value);
const savingsDiff = computed(() => actualSavings.value - (budget.value?.savings_target ?? 0));

const weeks = computed(() => {
  const firstDay = new Date(displayYear.value, displayMonth.value - 1, 1);
  const lastDay = new Date(displayYear.value, displayMonth.value, 0);
  const startOffset = firstDay.getDay();

  const days = [];
  for (let i = 0; i < startOffset; i++) days.push(null);
  for (let d = 1; d <= lastDay.getDate(); d++) days.push(new Date(displayYear.value, displayMonth.value - 1, d));
  while (days.length % 7 !== 0) days.push(null);

  const result = [];
  for (let i = 0; i < days.length; i += 7) result.push(days.slice(i, i + 7));
  return result;
});

const viewMode = ref("month");
const anchorDate = ref(new Date(today.getFullYear(), today.getMonth(), today.getDate()));

const visibleWeek = computed(() => {
  const start = new Date(anchorDate.value);
  start.setDate(start.getDate() - start.getDay());
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    return d;
  });
});

const rowsToRender = computed(() => (viewMode.value === "week" ? [visibleWeek.value] : weeks.value));

const navTitle = computed(() => {
  if (viewMode.value !== "week") return `${displayYear.value}年${displayMonth.value}月`;
  const week = visibleWeek.value;
  const first = week[0];
  const last = week[6];
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}`;
  return `${fmt(first)} 〜 ${fmt(last)}`;
});

function dateKey(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function schedulesForDay(day) {
  const key = dateKey(day);
  return schedules.value.filter((s) => scheduleOccursOnDate(s, key));
}

function expensesForDay(day) {
  const key = dateKey(day);
  return expenses.value.filter((e) => e.date === key);
}

function goToPrevMonth() {
  if (displayMonth.value === 1) {
    displayYear.value -= 1;
    displayMonth.value = 12;
  } else {
    displayMonth.value -= 1;
  }
}

function goToNextMonth() {
  if (displayMonth.value === 12) {
    displayYear.value += 1;
    displayMonth.value = 1;
  } else {
    displayMonth.value += 1;
  }
}

function syncDisplayMonthToAnchor() {
  if (displayYear.value !== anchorDate.value.getFullYear() || displayMonth.value !== anchorDate.value.getMonth() + 1) {
    displayYear.value = anchorDate.value.getFullYear();
    displayMonth.value = anchorDate.value.getMonth() + 1;
  }
}

function goToPrevWeek() {
  const d = new Date(anchorDate.value);
  d.setDate(d.getDate() - 7);
  anchorDate.value = d;
  syncDisplayMonthToAnchor();
}

function goToNextWeek() {
  const d = new Date(anchorDate.value);
  d.setDate(d.getDate() + 7);
  anchorDate.value = d;
  syncDisplayMonthToAnchor();
}

function goToPrev() {
  if (viewMode.value === "week") {
    goToPrevWeek();
  } else {
    goToPrevMonth();
  }
}

function goToNext() {
  if (viewMode.value === "week") {
    goToNextWeek();
  } else {
    goToNextMonth();
  }
}

function setViewMode(mode) {
  viewMode.value = mode;
  if (mode === "week") {
    if (anchorDate.value.getFullYear() !== displayYear.value || anchorDate.value.getMonth() + 1 !== displayMonth.value) {
      anchorDate.value = new Date(displayYear.value, displayMonth.value - 1, 1);
    }
  }
}

let fetchSequence = 0;

async function fetchMonthData() {
  const requestId = ++fetchSequence;
  const params = { year: displayYear.value, month: displayMonth.value };
  const [schedulesRes, expensesRes, budgetRes] = await Promise.all([
    listSchedules(params),
    listExpenses(params),
    getBudget(params),
  ]);
  if (requestId !== fetchSequence) return; // 古いリクエストの応答は無視(月送り連打時のレースコンディション対策)
  schedules.value = schedulesRes.data;
  expenses.value = expensesRes.data;
  budget.value = budgetRes.data;
}

function handleCellClick(day) {
  const key = dateKey(day);
  if (schedulesForDay(day).length > 0 || expensesForDay(day).length > 0) {
    detailDate.value = key;
  } else {
    openAddSchedule(day);
  }
}

function openAddSchedule(day) {
  editingSchedule.value = null;
  prefilledDate.value = day ? dateKey(day) : detailDate.value;
  showScheduleModal.value = true;
}

function openEditSchedule(schedule) {
  editingSchedule.value = schedule;
  showScheduleModal.value = true;
}

function closeScheduleModal() {
  showScheduleModal.value = false;
  editingSchedule.value = null;
  prefilledDate.value = null;
}

async function handleSaveSchedule(payload) {
  try {
    if (editingSchedule.value) {
      await updateSchedule(editingSchedule.value.id, payload);
    } else {
      await createSchedule(payload);
    }
    await fetchMonthData();
    closeScheduleModal();
  } catch (error) {
    scheduleModalRef.value?.setErrorMessage(error.response?.data?.detail || "保存に失敗しました");
  }
}

async function handleDeleteScheduleFromModal() {
  if (editingSchedule.value) {
    await deleteSchedule(editingSchedule.value.id);
    await fetchMonthData();
  }
  closeScheduleModal();
}

async function handleDeleteSchedule(schedule) {
  if (!window.confirm(`「${schedule.title}」を削除しますか？`)) return;
  await deleteSchedule(schedule.id);
  await fetchMonthData();
}

function openAddExpense(day) {
  editingExpense.value = null;
  prefilledDate.value = day ? dateKey(day) : detailDate.value;
  showExpenseModal.value = true;
}

function openEditExpense(expense) {
  editingExpense.value = expense;
  showExpenseModal.value = true;
}

function closeExpenseModal() {
  showExpenseModal.value = false;
  editingExpense.value = null;
  prefilledDate.value = null;
}

async function handleSaveExpense(payload) {
  try {
    if (editingExpense.value) {
      await updateExpense(editingExpense.value.id, payload);
    } else {
      await createExpense(payload);
    }
    await fetchMonthData();
    closeExpenseModal();
  } catch (error) {
    expenseModalRef.value?.setErrorMessage(error.response?.data?.detail || "保存に失敗しました");
  }
}

async function handleDeleteExpenseFromModal() {
  if (editingExpense.value) {
    await deleteExpense(editingExpense.value.id);
    await fetchMonthData();
  }
  closeExpenseModal();
}

async function handleDeleteExpense(expense) {
  if (!window.confirm(`「${expense.category}」を削除しますか？`)) return;
  await deleteExpense(expense.id);
  await fetchMonthData();
}

async function handleSaveBudget(payload) {
  try {
    const { data } = await upsertBudget({ year: displayYear.value, month: displayMonth.value, ...payload });
    budget.value = data;
    showBudgetModal.value = false;
  } catch (error) {
    budgetModalRef.value?.setErrorMessage(error.response?.data?.detail || "保存に失敗しました");
  }
}

watch([displayYear, displayMonth], fetchMonthData, { immediate: true });
</script>
