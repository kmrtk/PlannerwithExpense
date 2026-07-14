import client from "./client";

export function listExpenses(params = {}) {
  return client.get("/expenses", { params });
}

export function createExpense(payload) {
  return client.post("/expenses", payload);
}

export function updateExpense(id, payload) {
  return client.put(`/expenses/${id}`, payload);
}

export function deleteExpense(id) {
  return client.delete(`/expenses/${id}`);
}
