<template>
  <div class="modal-overlay open">
    <div class="modal-box day-detail-box">
      <h2>{{ date }}</h2>

      <section class="day-detail-section">
        <div class="day-detail-header">
          <h3>予定</h3>
          <button class="secondary" @click="$emit('add-schedule')">＋ 予定を追加</button>
        </div>
        <ul class="day-detail-list">
          <li v-for="schedule in schedules" :key="schedule.id">
            <span class="day-detail-item-title" @click="$emit('edit-schedule', schedule)">{{ schedule.title }}</span>
            <button class="secondary" @click="$emit('delete-schedule', schedule)">削除</button>
          </li>
          <li v-if="schedules.length === 0" class="day-detail-empty">予定はありません</li>
        </ul>
      </section>

      <section class="day-detail-section">
        <div class="day-detail-header">
          <h3>家計簿</h3>
          <button class="secondary" @click="$emit('add-expense')">＋ 支出を追加</button>
        </div>
        <ul class="day-detail-list">
          <li v-for="expense in expenses" :key="expense.id">
            <span
              class="day-detail-item-title"
              :class="expense.type === 'income' ? 'amount-income' : 'amount-expense'"
              @click="$emit('edit-expense', expense)"
            >
              {{ expense.category }}
              {{ expense.type === "income" ? "+" : "-" }}{{ expense.amount.toLocaleString() }}円
            </span>
            <button class="secondary" @click="$emit('delete-expense', expense)">削除</button>
          </li>
          <li v-if="expenses.length === 0" class="day-detail-empty">記録はありません</li>
        </ul>
      </section>

      <div class="modal-actions">
        <div></div>
        <div class="right-actions">
          <button type="button" class="secondary" @click="$emit('close')">閉じる</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  date: { type: String, required: true },
  schedules: { type: Array, default: () => [] },
  expenses: { type: Array, default: () => [] },
});
defineEmits([
  "close",
  "add-schedule",
  "edit-schedule",
  "delete-schedule",
  "add-expense",
  "edit-expense",
  "delete-expense",
]);
</script>
