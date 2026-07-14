<template>
  <AppHeader />
  <main>
    <div class="month-nav">
      <button class="link" @click="goToPrevMonth">← 前月</button>
      <span class="calendar-title">{{ displayYear }}年{{ displayMonth }}月</span>
      <button class="link" @click="goToNextMonth">次月 →</button>
    </div>

    <div class="budget-bar">
      <div class="budget-row">
        <span>収入: {{ actualIncome.toLocaleString() }}円 / 目標 {{ (budget?.income_budget ?? 0).toLocaleString() }}円</span>
        <div class="budget-meter">
          <div class="budget-meter-fill income" :style="{ width: incomeRatio + '%' }"></div>
        </div>
      </div>
      <div class="budget-row">
        <span>支出: {{ actualExpense.toLocaleString() }}円 / 目標 {{ (budget?.expense_budget ?? 0).toLocaleString() }}円</span>
        <div class="budget-meter">
          <div class="budget-meter-fill expense" :style="{ width: expenseRatio + '%' }"></div>
        </div>
      </div>
      <button class="secondary" @click="showBudgetModal = true">予算を設定</button>
    </div>

    <div class="toolbar">
      <button @click="openAddSchedule(null)">＋ 予定追加</button>
    </div>
    <table class="calendar-table">
      <thead>
        <tr>
          <th v-for="label in weekLabels" :key="label">{{ label }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(week, wi) in weeks" :key="wi">
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
    :schedule="editingSchedule"
    :default-date="prefilledDate"
    @close="closeScheduleModal"
    @save="handleSaveSchedule"
    @delete="handleDeleteScheduleFromModal"
  />

  <ExpenseModal
    v-if="showExpenseModal"
    :expense="editingExpense"
    :default-date="prefilledDate"
    @close="closeExpenseModal"
    @save="handleSaveExpense"
    @delete="handleDeleteExpenseFromModal"
  />

  <BudgetModal
    v-if="showBudgetModal"
    :budget="budget"
    :year="displayYear"
    :month="displayMonth"
    @close="showBudgetModal = false"
    @save="handleSaveBudget"
  />
</template>

<script setup>
import { computed, ref, watch } from "vue";
import AppHeader from "../components/AppHeader.vue";
import ScheduleModal from "../components/ScheduleModal.vue";
import ExpenseModal from "../components/ExpenseModal.vue";
import DayDetailModal from "../components/DayDetailModal.vue";
import BudgetModal from "../components/BudgetModal.vue";
import { createSchedule, deleteSchedule, listSchedules, updateSchedule } from "../api/schedules";
import { createExpense, deleteExpense, listExpenses, updateExpense } from "../api/expenses";
import { getBudget, upsertBudget } from "../api/budgets";

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

const showDayDetail = computed(() => !!detailDate.value && !showScheduleModal.value && !showExpenseModal.value);
const detailSchedules = computed(() =>
  detailDate.value ? schedules.value.filter((s) => s.start_datetime.slice(0, 10) === detailDate.value) : []
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
const incomeRatio = computed(() => {
  const target = budget.value?.income_budget ?? 0;
  return target > 0 ? Math.min(100, Math.round((actualIncome.value / target) * 100)) : 0;
});
const expenseRatio = computed(() => {
  const target = budget.value?.expense_budget ?? 0;
  return target > 0 ? Math.min(100, Math.round((actualExpense.value / target) * 100)) : 0;
});

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

function dateKey(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function schedulesForDay(day) {
  const key = dateKey(day);
  return schedules.value.filter((s) => s.start_datetime.slice(0, 10) === key);
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
  if (editingSchedule.value) {
    await updateSchedule(editingSchedule.value.id, payload);
  } else {
    await createSchedule(payload);
  }
  await fetchMonthData();
  closeScheduleModal();
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
  if (editingExpense.value) {
    await updateExpense(editingExpense.value.id, payload);
  } else {
    await createExpense(payload);
  }
  await fetchMonthData();
  closeExpenseModal();
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
  const { data } = await upsertBudget({ year: displayYear.value, month: displayMonth.value, ...payload });
  budget.value = data;
  showBudgetModal.value = false;
}

watch([displayYear, displayMonth], fetchMonthData, { immediate: true });
</script>
