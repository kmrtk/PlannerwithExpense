import client from "./client";

export function listSchedules() {
  return client.get("/schedules");
}

export function createSchedule(payload) {
  return client.post("/schedules", payload);
}

export function updateSchedule(id, payload) {
  return client.put(`/schedules/${id}`, payload);
}

export function deleteSchedule(id) {
  return client.delete(`/schedules/${id}`);
}
