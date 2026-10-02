document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert-close").forEach((button) => {
    button.addEventListener("click", () => button.closest(".alert")?.remove());
  });

  const menuButton = document.getElementById("menuButton");
  menuButton?.addEventListener("click", () => document.getElementById("sidebar")?.classList.toggle("sidebar-open"));

  document.querySelectorAll(".status-choice input[type=radio]").forEach((radio) => {
    radio.addEventListener("change", () => {
      document.querySelectorAll(`input[name="${CSS.escape(radio.name)}"]`).forEach((input) => {
        input.closest(".status-choice")?.classList.toggle("selected", input.checked);
      });
    });
  });

  document.querySelectorAll(".bulk-chip").forEach((button) => {
    button.addEventListener("click", () => {
      const status = button.dataset.status;
      document.querySelectorAll(`.status-options input[value="${CSS.escape(status)}"]`).forEach((radio) => {
        radio.checked = true;
        radio.dispatchEvent(new Event("change", { bubbles: true }));
      });
    });
  });

  document.getElementById("attendanceForm")?.addEventListener("submit", (event) => {
    const submitter = event.submitter;
    if (submitter?.value !== "save") return;
    const form = event.currentTarget;
    const loaded = ["loaded_subject", "loaded_date", "loaded_session"].map((name) => form.querySelector(`[name="${name}"]`)?.value || "");
    const selector = document.querySelector(".selector-form");
    const current = ["subject_id", "date", "session"].map((name) => selector?.querySelector(`[name="${name}"]`)?.value || "");
    if (loaded.some((value, index) => value !== current[index])) {
      event.preventDefault();
      window.alert("The class, date, or session changed. Choose Load roster before saving attendance.");
    }
  });
});
