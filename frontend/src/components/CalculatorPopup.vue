<template>
  <div class="calculator-backdrop" @click="$emit('close')"></div>
  <div class="calculator-popup" @click.stop>
    <div class="calculator-display">{{ display }}</div>
    <div class="calculator-keys">
      <button type="button" class="calculator-key calculator-key-func" @click="clear">C</button>
      <button type="button" class="calculator-key calculator-key-func" @click="backspace">⌫</button>
      <button type="button" class="calculator-key calculator-key-op" @click="pressOperator('/')">÷</button>
      <button type="button" class="calculator-key calculator-key-op" @click="pressOperator('*')">×</button>

      <button type="button" class="calculator-key" @click="pressDigit('7')">7</button>
      <button type="button" class="calculator-key" @click="pressDigit('8')">8</button>
      <button type="button" class="calculator-key" @click="pressDigit('9')">9</button>
      <button type="button" class="calculator-key calculator-key-op" @click="pressOperator('-')">−</button>

      <button type="button" class="calculator-key" @click="pressDigit('4')">4</button>
      <button type="button" class="calculator-key" @click="pressDigit('5')">5</button>
      <button type="button" class="calculator-key" @click="pressDigit('6')">6</button>
      <button type="button" class="calculator-key calculator-key-op" @click="pressOperator('+')">+</button>

      <button type="button" class="calculator-key" @click="pressDigit('1')">1</button>
      <button type="button" class="calculator-key" @click="pressDigit('2')">2</button>
      <button type="button" class="calculator-key" @click="pressDigit('3')">3</button>
      <button type="button" class="calculator-key calculator-key-eq" @click="pressEquals">=</button>

      <button type="button" class="calculator-key calculator-key-zero" @click="pressDigit('0')">0</button>
    </div>
    <button type="button" class="calculator-confirm" @click="confirm">この金額を入力</button>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  modelValue: { type: Number, default: null },
});
const emit = defineEmits(["update:modelValue", "close"]);

const display = ref(props.modelValue != null ? String(props.modelValue) : "0");
const storedValue = ref(null);
const pendingOperator = ref(null);
const overwrite = ref(true);

const MAX_DIGITS = 15;

function pressDigit(digit) {
  if (overwrite.value) {
    display.value = digit;
    overwrite.value = false;
  } else if (display.value.length < MAX_DIGITS) {
    display.value = display.value === "0" ? digit : display.value + digit;
  }
}

function compute() {
  if (pendingOperator.value === null || storedValue.value === null) return;
  const current = Number(display.value);
  let result;
  switch (pendingOperator.value) {
    case "+":
      result = storedValue.value + current;
      break;
    case "-":
      result = storedValue.value - current;
      break;
    case "*":
      result = storedValue.value * current;
      break;
    case "/":
      result = current === 0 ? storedValue.value : storedValue.value / current;
      break;
    default:
      result = current;
  }
  display.value = String(Math.round(result * 100) / 100);
  storedValue.value = result;
}

function pressOperator(operator) {
  if (pendingOperator.value !== null && !overwrite.value) {
    compute();
  } else {
    storedValue.value = Number(display.value);
  }
  pendingOperator.value = operator;
  overwrite.value = true;
}

function pressEquals() {
  compute();
  pendingOperator.value = null;
  overwrite.value = true;
}

function clear() {
  display.value = "0";
  storedValue.value = null;
  pendingOperator.value = null;
  overwrite.value = true;
}

function backspace() {
  if (overwrite.value) return;
  display.value = display.value.length > 1 ? display.value.slice(0, -1) : "0";
  if (display.value === "0") overwrite.value = true;
}

function confirm() {
  if (pendingOperator.value !== null) {
    compute();
  }
  emit("update:modelValue", Math.round(Number(display.value)));
  emit("close");
}
</script>
