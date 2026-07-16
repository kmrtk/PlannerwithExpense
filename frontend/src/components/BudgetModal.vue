<template>
  <div class="modal-overlay open">
    <div class="modal-box">
      <h2>{{ year }}年{{ month }}月の予算を設定</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <label for="budget-savings">貯蓄目標</label>
          <input
            id="budget-savings"
            v-model.number="savingsTarget"
            type="number"
            min="0"
            :max="MAX_AMOUNT"
            required
          />
        </div>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
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
import { MAX_AMOUNT, isNonNegativeAmount } from "../utils/validation";

const props = defineProps({
  budget: { type: Object, default: null },
  year: { type: Number, required: true },
  month: { type: Number, required: true },
});
const emit = defineEmits(["close", "save"]);

const savingsTarget = ref(props.budget?.savings_target ?? 0);
const errorMessage = ref("");

defineExpose({ setErrorMessage: (message) => (errorMessage.value = message) });

function handleSubmit() {
  if (!isNonNegativeAmount(savingsTarget.value, MAX_AMOUNT)) {
    errorMessage.value = `貯蓄目標は0円以上${MAX_AMOUNT.toLocaleString()}円以下で入力してください`;
    return;
  }

  errorMessage.value = "";
  emit("save", {
    savings_target: savingsTarget.value,
  });
}
</script>
