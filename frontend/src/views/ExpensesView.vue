<template>
  <div class="app-layout">
  <AppSidebar />
  <main>
    <div class="toolbar">
      <button @click="openAddModal">＋ 支出追加</button>
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
        <tr v-for="expense in expenses" :key="expense.id">
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
    :expense="editingExpense"
    @close="closeModal"
    @save="handleSave"
    @delete="handleDeleteFromModal"
  />
</template>

<script setup>
import { onMounted, ref } from "vue";
import AppSidebar from "../components/AppSidebar.vue";
import ExpenseModal from "../components/ExpenseModal.vue";
import { createExpense, deleteExpense, listExpenses, updateExpense } from "../api/expenses";

const expenses = ref([]);
const showModal = ref(false);
const editingExpense = ref(null);
const loading = ref(true);

async function fetchExpenses() {
  const { data } = await listExpenses();
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
  if (editingExpense.value) {
    await updateExpense(editingExpense.value.id, payload);
  } else {
    await createExpense(payload);
  }
  await fetchExpenses();
  closeModal();
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

onMounted(fetchExpenses);
</script>
