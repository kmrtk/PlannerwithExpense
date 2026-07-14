import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
  { path: "/", redirect: "/calendar" },
  { path: "/login", name: "login", component: () => import("../views/LoginView.vue") },
  { path: "/register", name: "register", component: () => import("../views/RegisterView.vue") },
  {
    path: "/calendar",
    name: "calendar",
    component: () => import("../views/CalendarView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/expenses",
    name: "expenses",
    component: () => import("../views/ExpensesView.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login" };
  }

  if ((to.name === "login" || to.name === "register") && auth.isAuthenticated) {
    return { name: "calendar" };
  }

  return true;
});

export default router;
