import client from "./client";

export function getBudget(params) {
  return client.get("/budgets", { params });
}

export function upsertBudget(payload) {
  return client.put("/budgets", payload);
}
