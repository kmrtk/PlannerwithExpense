<template>
  <AppHeader />
  <main>
    <div class="calendar-title">{{ year }}年{{ month }}月</div>
    <div class="toolbar">
      <button @click="openAddModal">＋ 予定追加</button>
    </div>
    <table class="calendar-table">
      <thead>
        <tr>
          <th v-for="label in weekLabels" :key="label">{{ label }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(week, wi) in weeks" :key="wi">
          <td v-for="(day, di) in week" :key="di">
            <template v-if="day">
              {{ day.getDate() }}
              <span
                v-for="schedule in schedulesForDay(day)"
                :key="schedule.id"
                class="schedule-chip"
                @click="openEditModal(schedule)"
              >
                {{ schedule.title }}
              </span>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </main>

  <ScheduleModal
    v-if="showModal"
    :schedule="editingSchedule"
    @close="closeModal"
    @save="handleSave"
    @delete="handleDelete"
  />
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import AppHeader from "../components/AppHeader.vue";
import ScheduleModal from "../components/ScheduleModal.vue";
import { createSchedule, deleteSchedule, listSchedules, updateSchedule } from "../api/schedules";

const weekLabels = ["日", "月", "火", "水", "木", "金", "土"];

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1;

const schedules = ref([]);
const showModal = ref(false);
const editingSchedule = ref(null);

const weeks = computed(() => {
  const firstDay = new Date(year, month - 1, 1);
  const lastDay = new Date(year, month, 0);
  const startOffset = firstDay.getDay();

  const days = [];
  for (let i = 0; i < startOffset; i++) days.push(null);
  for (let d = 1; d <= lastDay.getDate(); d++) days.push(new Date(year, month - 1, d));
  while (days.length % 7 !== 0) days.push(null);

  const result = [];
  for (let i = 0; i < days.length; i += 7) result.push(days.slice(i, i + 7));
  return result;
});

function dateKey(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function schedulesForDay(day) {
  const key = dateKey(day);
  return schedules.value.filter((s) => s.start_datetime.slice(0, 10) === key);
}

async function fetchSchedules() {
  const { data } = await listSchedules();
  schedules.value = data;
}

function openAddModal() {
  editingSchedule.value = null;
  showModal.value = true;
}

function openEditModal(schedule) {
  editingSchedule.value = schedule;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingSchedule.value = null;
}

async function handleSave(payload) {
  if (editingSchedule.value) {
    await updateSchedule(editingSchedule.value.id, payload);
  } else {
    await createSchedule(payload);
  }
  await fetchSchedules();
  closeModal();
}

async function handleDelete() {
  if (editingSchedule.value) {
    await deleteSchedule(editingSchedule.value.id);
    await fetchSchedules();
  }
  closeModal();
}

onMounted(fetchSchedules);
</script>
