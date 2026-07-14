<template>
  <div class="modal-overlay open">
    <div class="modal-box">
      <h2>{{ year }}年{{ month }}月の予算を設定</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <label for="budget-income">収入目標</label>
          <input id="budget-income" v-model.number="incomeBudget" type="number" required />
        </div>
        <div class="form-row">
          <label for="budget-expense">支出目標</label>
          <input id="budget-expense" v-model.number="expenseBudget" type="number" required />
        </div>
        <div class="modal-actions">
          <div></div>
          <div class="right-actions">
            <button type="button" class="secondary" @click="$emit('close')">キャンセル</button>
            <button type="submit">保存</button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  budget: { type: Object, default: null },
  year: { type: Number, required: true },
  month: { type: Number, required: true },
});
const emit = defineEmits(["close", "save"]);

const incomeBudget = ref(props.budget?.income_budget ?? 0);
const expenseBudget = ref(props.budget?.expense_budget ?? 0);

function handleSubmit() {
  emit("save", {
    income_budget: incomeBudget.value,
    expense_budget: expenseBudget.value,
  });
}
</script>
