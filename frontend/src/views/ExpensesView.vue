<template>
  <div class="app-layout">
  <AppSidebar />
  <main>
    <div class="month-nav">
      <template v-if="displayMode === 'week'">
        <button class="link" @click="goToPrevWeek">← 前週</button>
        <span class="calendar-title">{{ weekRangeLabel }}の家計簿</span>
        <button class="link" @click="goToNextWeek">次週 →</button>
      </template>
      <template v-else-if="isFiltered">
        <span class="calendar-title">{{ filterYear }}年{{ filterMonth }}月の家計簿</span>
        <router-link class="link" :to="{ name: 'expenses' }">全期間を見る</router-link>
      </template>
      <div class="view-mode-toggle">
        <button :class="{ active: displayMode === 'month' }" class="secondary" @click="displayMode = 'month'">月</button>
        <button :class="{ active: displayMode === 'week' }" class="secondary" @click="displayMode = 'week'">週</button>
      </div>
    </div>
    <div class="toolbar">
      <button @click="openAddModal">＋ 支出追加</button>
      <select v-model="sortOrder">
        <option value="date_desc">日付が新しい順</option>
        <option value="date_asc">日付が古い順</option>
        <option value="income_only">黒字のみ抽出</option>
        <option value="expense_only">赤字のみ抽出</option>
      </select>
      <button class="secondary" @click="resetSort">並び替えをリセット</button>
      <button class="secondary" :disabled="loading" @click="exportCsv">CSVエクスポート</button>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>日付</th>
          <th>区分</th>
          <th>カテゴリ</th>
          <th>金額</th>
          <th>メモ</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="expense in sortedExpenses" :key="expense.id">
          <td>{{ expense.date }}</td>
          <td>
            <span :class="['type-badge', expense.type]">{{ expense.type === "income" ? "収入" : "支出" }}</span>
          </td>
          <td>{{ expense.category }}</td>
          <td :class="expense.type === 'income' ? 'amount-income' : 'amount-expense'">
            {{ expense.type === "income" ? "+" : "-" }}{{ expense.amount.toLocaleString() }}円
          </td>
          <td>{{ expense.memo }}</td>
          <td>
            <button class="secondary" @click="openEditModal(expense)">編集</button>
            <button class="secondary" @click="handleDelete(expense)">削除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </main>
  </div>

  <ExpenseModal
    v-if="showModal"
    ref="expenseModalRef"
    :expense="editingExpense"
    @close="closeModal"
    @save="handleSave"
    @delete="handleDeleteFromModal"
  />
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import AppSidebar from "../components/AppSidebar.vue";
import ExpenseModal from "../components/ExpenseModal.vue";
import { createExpense, deleteExpense, listExpenses, updateExpense } from "../api/expenses";
import { dateKey, getWeekDates } from "../utils/date";

const route = useRoute();
const filterYear = computed(() => (route.params.year ? Number(route.params.year) : null));
const filterMonth = computed(() => (route.params.month ? Number(route.params.month) : null));
const isFiltered = computed(() => filterYear.value !== null && filterMonth.value !== null);

const expenses = ref([]);
const showModal = ref(false);
const editingExpense = ref(null);
const loading = ref(true);
const expenseModalRef = ref(null);
const sortOrder = ref("date_desc");
const displayMode = ref("month");

function defaultWeekAnchor() {
  return isFiltered.value ? new Date(filterYear.value, filterMonth.value - 1, 1) : new Date();
}

const weekAnchor = ref(defaultWeekAnchor());

const weekDates = computed(() => getWeekDates(weekAnchor.value));
const weekRangeLabel = computed(() => {
  const [first, last] = [weekDates.value[0], weekDates.value[6]];
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}`;
  return `${fmt(first)} 〜 ${fmt(last)}`;
});

const weekFilteredExpenses = computed(() => {
  if (displayMode.value !== "week") return expenses.value;
  const startKey = dateKey(weekDates.value[0]);
  const endKey = dateKey(weekDates.value[6]);
  return expenses.value.filter((e) => e.date >= startKey && e.date <= endKey);
});

const sortedExpenses = computed(() => {
  const list = [...weekFilteredExpenses.value];
  switch (sortOrder.value) {
    case "date_asc":
      return list.sort((a, b) => a.date.localeCompare(b.date));
    case "income_only":
      return list.filter((e) => e.type === "income").sort((a, b) => b.date.localeCompare(a.date));
    case "expense_only":
      return list.filter((e) => e.type === "expense").sort((a, b) => b.date.localeCompare(a.date));
    case "date_desc":
    default:
      return list.sort((a, b) => b.date.localeCompare(a.date));
  }
});

function resetSort() {
  sortOrder.value = "date_desc";
}

function goToPrevWeek() {
  const d = new Date(weekAnchor.value);
  d.setDate(d.getDate() - 7);
  weekAnchor.value = d;
}

function goToNextWeek() {
  const d = new Date(weekAnchor.value);
  d.setDate(d.getDate() + 7);
  weekAnchor.value = d;
}

let fetchSequence = 0;

async function fetchExpenses() {
  const requestId = ++fetchSequence;
  const params = isFiltered.value ? { year: filterYear.value, month: filterMonth.value } : {};
  const { data } = await listExpenses(params);
  if (requestId !== fetchSequence) return; // 古いリクエストの応答は無視(月切り替え連打時のレースコンディション対策)
  expenses.value = data;
  loading.value = false;
}

function openAddModal() {
  editingExpense.value = null;
  showModal.value = true;
}

function openEditModal(expense) {
  editingExpense.value = expense;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingExpense.value = null;
}

async function handleSave(payload) {
  try {
    if (editingExpense.value) {
      await updateExpense(editingExpense.value.id, payload);
    } else {
      await createExpense(payload);
    }
    await fetchExpenses();
    closeModal();
  } catch (error) {
    expenseModalRef.value?.setErrorMessage(error.response?.data?.detail || "保存に失敗しました");
  }
}

async function handleDelete(expense) {
  await deleteExpense(expense.id);
  await fetchExpenses();
}

async function handleDeleteFromModal() {
  if (editingExpense.value) {
    await deleteExpense(editingExpense.value.id);
    await fetchExpenses();
  }
  closeModal();
}

function csvEscape(value) {
  const str = String(value ?? "");
  return /[",\n]/.test(str) ? `"${str.replace(/"/g, '""')}"` : str;
}

function exportCsv() {
  const header = ["日付", "区分", "カテゴリ", "金額", "メモ"];
  const rows = expenses.value.map((expense) => [
    expense.date,
    expense.type === "income" ? "収入" : "支出",
    expense.category,
    expense.amount,
    expense.memo,
  ]);
  const csv = [header, ...rows].map((row) => row.map(csvEscape).join(",")).join("\r\n");
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  link.href = url;
  link.download = `expenses_${today}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

watch([filterYear, filterMonth], () => {
  displayMode.value = "month";
  weekAnchor.value = defaultWeekAnchor();
  fetchExpenses();
}, { immediate: true });
</script>
