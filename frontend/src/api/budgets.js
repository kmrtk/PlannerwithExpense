import client from "./client";

export function getBudget(params) {
  return client.get("/budgets", { params });
}

export function getYearlySummary(year) {
  return client.get("/budgets/yearly", { params: { year } });
}

export function upsertBudget(payload) {
  return client.put("/budgets", payload);
}

export function getAllTimeSummary() {
  return client.get("/budgets/all-time-summary");
}
