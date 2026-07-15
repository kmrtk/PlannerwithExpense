<template>
  <div class="modal-overlay open">
    <div class="modal-box">
      <h2>{{ isEdit ? "支出を編集" : "支出を追加" }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <label>区分</label>
          <div class="radio-group">
            <label><input v-model="type" type="radio" value="expense" /> 支出</label>
            <label><input v-model="type" type="radio" value="income" /> 収入</label>
          </div>
        </div>
        <div class="form-row">
          <label for="expense-amount">金額</label>
          <input id="expense-amount" v-model.number="amount" type="number" required />
        </div>
        <div class="form-row">
          <label for="expense-date">日付</label>
          <input id="expense-date" v-model="date" type="date" required />
        </div>
        <div class="form-row">
          <label for="expense-category">カテゴリ</label>
          <input id="expense-category" v-model="category" type="text" list="expense-category-presets" required />
          <datalist id="expense-category-presets">
            <option v-for="preset in EXPENSE_CATEGORY_PRESETS" :key="preset" :value="preset" />
          </datalist>
        </div>
        <div class="form-row">
          <label for="expense-memo">メモ</label>
          <textarea id="expense-memo" v-model="memo" rows="3"></textarea>
        </div>
        <div class="modal-actions">
          <button v-if="isEdit" type="button" class="secondary" @click="$emit('delete')">削除</button>
          <div v-else></div>
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
import { EXPENSE_CATEGORY_PRESETS } from "../constants/categories";

const props = defineProps({
  expense: { type: Object, default: null },
  defaultDate: { type: String, default: null },
});
const emit = defineEmits(["close", "save", "delete"]);

const isEdit = !!props.expense;
const type = ref(props.expense?.type || "expense");
const amount = ref(props.expense?.amount ?? null);
const date = ref(props.expense?.date || props.defaultDate || "");
const category = ref(props.expense?.category || "");
const memo = ref(props.expense?.memo || "");

function handleSubmit() {
  emit("save", {
    type: type.value,
    amount: amount.value,
    date: date.value,
    category: category.value,
    memo: memo.value,
  });
}
</script>
