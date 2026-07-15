<template>
  <div class="modal-overlay open">
    <div class="modal-box">
      <h2>{{ isEdit ? "予定を編集" : "予定を追加" }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <label for="schedule-title">タイトル</label>
          <input id="schedule-title" v-model="title" type="text" required />
        </div>
        <div class="form-row">
          <label for="schedule-date">日付</label>
          <input id="schedule-date" v-model="date" type="date" required />
        </div>
        <div class="form-row">
          <label for="schedule-recurrence">繰り返し</label>
          <select id="schedule-recurrence" v-model="recurrenceType">
            <option value="none">なし</option>
            <option value="weekly">毎週</option>
            <option value="monthly">毎月</option>
          </select>
        </div>
        <div v-if="recurrenceType !== 'none'" class="form-row">
          <label for="schedule-recurrence-end">終了日（未指定で無期限）</label>
          <input id="schedule-recurrence-end" v-model="recurrenceEnd" type="date" />
        </div>
        <p v-if="isEdit && props.schedule.recurrence_type !== 'none'" class="recurrence-note">
          繰り返し予定の編集・削除は全体に反映されます。
        </p>
        <div class="form-row">
          <label for="schedule-memo">メモ</label>
          <textarea id="schedule-memo" v-model="memo" rows="3"></textarea>
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

const props = defineProps({
  schedule: { type: Object, default: null },
  defaultDate: { type: String, default: null },
});
const emit = defineEmits(["close", "save", "delete"]);

const isEdit = !!props.schedule;
const title = ref(props.schedule?.title || "");
const date = ref(props.schedule ? props.schedule.start_datetime.slice(0, 10) : props.defaultDate || "");
const memo = ref(props.schedule?.memo || "");
const recurrenceType = ref(props.schedule?.recurrence_type || "none");
const recurrenceEnd = ref(props.schedule?.recurrence_end || "");

function handleSubmit() {
  emit("save", {
    title: title.value,
    start_datetime: `${date.value}T00:00:00`,
    end_datetime: `${date.value}T00:00:00`,
    memo: memo.value,
    recurrence_type: recurrenceType.value,
    recurrence_end: recurrenceType.value === "none" ? null : recurrenceEnd.value || null,
  });
}
</script>
