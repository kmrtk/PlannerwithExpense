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
          <div class="amount-input-row">
            <input
              id="expense-amount"
              v-model.number="amount"
              type="number"
              min="1"
              :max="MAX_AMOUNT"
              required
            />
            <button
              type="button"
              class="calculator-toggle-btn"
              aria-label="電卓を開く"
              @click="showCalculator = !showCalculator"
            >
              電卓
            </button>
            <CalculatorPopup
              v-if="showCalculator"
              :model-value="amount"
              @update:model-value="amount = $event"
              @close="showCalculator = false"
            />
          </div>
        </div>
        <div class="form-row">
          <label for="expense-date">日付</label>
          <input id="expense-date" v-model="date" type="date" required />
        </div>
        <div class="form-row">
          <label for="expense-category">カテゴリ</label>
          <select id="expense-category" v-model="selectedCategory">
            <option v-for="preset in EXPENSE_CATEGORY_PRESETS" :key="preset" :value="preset">{{ preset }}</option>
            <option :value="CUSTOM_OPTION">その他（自由入力）</option>
          </select>
        </div>
        <div v-if="selectedCategory === CUSTOM_OPTION" class="form-row">
          <label for="expense-category-custom">カテゴリ（自由入力）</label>
          <input
            id="expense-category-custom"
            v-model="customCategory"
            type="text"
            :maxlength="MAX_TEXT_LENGTH"
            required
          />
        </div>
        <div class="form-row">
          <label for="expense-schedule">紐付ける予定（任意）</label>
          <select id="expense-schedule" v-model="scheduleId">
            <option :value="null">なし</option>
            <option v-for="schedule in scheduleOptions" :key="schedule.id" :value="schedule.id">
              {{ schedule.title }}
            </option>
          </select>
        </div>
        <div class="form-row">
          <label for="expense-memo">メモ</label>
          <textarea id="expense-memo" v-model="memo" rows="3" :maxlength="MAX_MEMO_LENGTH"></textarea>
        </div>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
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
import CalculatorPopup from "./CalculatorPopup.vue";
import { EXPENSE_CATEGORY_PRESETS } from "../constants/categories";
import { MAX_AMOUNT, MAX_TEXT_LENGTH, MAX_MEMO_LENGTH, isPositiveAmount, isNonEmptyWithinLength, isWithinLength } from "../utils/validation";

const CUSTOM_OPTION = "__custom__";

const props = defineProps({
  expense: { type: Object, default: null },
  defaultDate: { type: String, default: null },
  scheduleOptions: { type: Array, default: () => [] },
});
const emit = defineEmits(["close", "save", "delete"]);

const isEdit = !!props.expense;
const type = ref(props.expense?.type || "expense");
const amount = ref(props.expense?.amount ?? null);
const date = ref(props.expense?.date || props.defaultDate || "");
const memo = ref(props.expense?.memo || "");
const scheduleId = ref(props.expense?.schedule_id ?? null);
const errorMessage = ref("");
const showCalculator = ref(false);

const existingCategory = props.expense?.category || "";
const isExistingPreset = EXPENSE_CATEGORY_PRESETS.includes(existingCategory);
const selectedCategory = ref(
  existingCategory ? (isExistingPreset ? existingCategory : CUSTOM_OPTION) : EXPENSE_CATEGORY_PRESETS[0]
);
const customCategory = ref(!isExistingPreset ? existingCategory : "");

defineExpose({ setErrorMessage: (message) => (errorMessage.value = message) });

function handleSubmit() {
  const category = selectedCategory.value === CUSTOM_OPTION ? customCategory.value : selectedCategory.value;

  if (!isPositiveAmount(amount.value, MAX_AMOUNT)) {
    errorMessage.value = `金額は1円以上${MAX_AMOUNT.toLocaleString()}円以下で入力してください`;
    return;
  }
  if (!isNonEmptyWithinLength(category, MAX_TEXT_LENGTH)) {
    errorMessage.value = "カテゴリを入力してください";
    return;
  }
  if (!isWithinLength(memo.value, MAX_MEMO_LENGTH)) {
    errorMessage.value = `メモは${MAX_MEMO_LENGTH}文字以内で入力してください`;
    return;
  }

  errorMessage.value = "";
  emit("save", {
    type: type.value,
    amount: amount.value,
    date: date.value,
    category,
    memo: memo.value,
    schedule_id: scheduleId.value || null,
  });
}
</script>
