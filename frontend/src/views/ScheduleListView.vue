<template>
  <div class="app-layout">
  <AppSidebar />
  <main>
    <div class="month-nav">
      <router-link class="link" :to="prevTarget">← 前月</router-link>
      <span class="calendar-title">{{ year }}年{{ month }}月</span>
      <router-link class="link" :to="nextTarget">次月 →</router-link>
    </div>

    <div class="toolbar">
      <button @click="openAddSchedule">＋ 予定追加</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>日付</th>
          <th>タイトル</th>
          <th>メモ</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in entries" :key="entry.dateKey + '-' + entry.schedule.id">
          <td>{{ entry.dateKey }}</td>
          <td>{{ entry.schedule.title }}</td>
          <td>{{ entry.schedule.memo }}</td>
          <td>
            <button class="secondary" @click="openEditSchedule(entry.schedule)">編集</button>
            <button class="secondary" @click="handleDeleteSchedule(entry.schedule)">削除</button>
          </td>
        </tr>
        <tr v-if="entries.length === 0">
          <td colspan="4" class="day-detail-empty">予定はありません</td>
        </tr>
      </tbody>
    </table>
  </main>
  </div>

  <ScheduleModal
    v-if="showScheduleModal"
    ref="scheduleModalRef"
    :schedule="editingSchedule"
    :default-date="prefilledDate"
    @close="closeScheduleModal"
    @save="handleSaveSchedule"
    @delete="handleDeleteScheduleFromModal"
  />
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import AppSidebar from "../components/AppSidebar.vue";
import ScheduleModal from "../components/ScheduleModal.vue";
import { createSchedule, deleteSchedule, listSchedules, updateSchedule } from "../api/schedules";
import { scheduleOccursOnDate } from "../utils/recurrence";

const route = useRoute();
const year = computed(() => Number(route.params.year));
const month = computed(() => Number(route.params.month));

const schedules = ref([]);
const showScheduleModal = ref(false);
const editingSchedule = ref(null);
const prefilledDate = ref(null);
const scheduleModalRef = ref(null);

function pad(n) {
  return String(n).padStart(2, "0");
}

async function fetchSchedules() {
  // listSchedules()はパラメータを取らず常に全件を返すため、レースコンディションの心配はない
  const { data } = await listSchedules();
  schedules.value = data;
}

const entries = computed(() => {
  const daysInMonth = new Date(year.value, month.value, 0).getDate();
  const result = [];
  for (let d = 1; d <= daysInMonth; d++) {
    const dateKey = `${year.value}-${pad(month.value)}-${pad(d)}`;
    for (const schedule of schedules.value) {
      if (scheduleOccursOnDate(schedule, dateKey)) {
        result.push({ dateKey, schedule });
      }
    }
  }
  return result;
});

const prevTarget = computed(() => {
  let y = year.value;
  let m = month.value - 1;
  if (m === 0) {
    m = 12;
    y -= 1;
  }
  return { name: "schedule-list", params: { year: y, month: m } };
});

const nextTarget = computed(() => {
  let y = year.value;
  let m = month.value + 1;
  if (m === 13) {
    m = 1;
    y += 1;
  }
  return { name: "schedule-list", params: { year: y, month: m } };
});

function openAddSchedule() {
  editingSchedule.value = null;
  prefilledDate.value = `${year.value}-${pad(month.value)}-01`;
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
  try {
    if (editingSchedule.value) {
      await updateSchedule(editingSchedule.value.id, payload);
    } else {
      await createSchedule(payload);
    }
    await fetchSchedules();
    closeScheduleModal();
  } catch (error) {
    scheduleModalRef.value?.setErrorMessage(error.response?.data?.detail || "保存に失敗しました");
  }
}

async function handleDeleteScheduleFromModal() {
  if (editingSchedule.value) {
    await deleteSchedule(editingSchedule.value.id);
    await fetchSchedules();
  }
  closeScheduleModal();
}

async function handleDeleteSchedule(schedule) {
  if (!window.confirm(`「${schedule.title}」を削除しますか？`)) return;
  await deleteSchedule(schedule.id);
  await fetchSchedules();
}

watch([year, month], fetchSchedules, { immediate: true });
</script>
