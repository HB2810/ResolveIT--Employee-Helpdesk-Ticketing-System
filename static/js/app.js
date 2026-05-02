document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("page-ready");

    document.querySelectorAll(".toast").forEach((toastNode) => {
        const toast = new bootstrap.Toast(toastNode, { delay: 3800 });
        toast.show();
    });

    const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
    const sidebarClose = document.querySelector("[data-sidebar-close]");

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            document.body.classList.toggle("sidebar-open");
        });
    }

    if (sidebarClose) {
        sidebarClose.addEventListener("click", () => {
            document.body.classList.remove("sidebar-open");
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            document.body.classList.remove("sidebar-open");
        }
    });

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = button.closest(".password-wrap").querySelector("input");
            const icon = button.querySelector("i");
            const isPassword = input.type === "password";
            input.type = isPassword ? "text" : "password";
            icon.classList.toggle("fa-eye", !isPassword);
            icon.classList.toggle("fa-eye-slash", isPassword);
            button.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
        });
    });

    document.querySelectorAll("[data-table-search]").forEach((input) => {
        const table = document.querySelector(input.dataset.tableSearch);
        if (!table) {
            return;
        }

        input.addEventListener("input", () => {
            const query = input.value.trim().toLowerCase();
            table.querySelectorAll("tbody tr").forEach((row) => {
                row.hidden = query && !row.textContent.toLowerCase().includes(query);
            });
        });
    });

    document.querySelectorAll("[data-counter]").forEach((textarea) => {
        const counter = document.getElementById(textarea.dataset.counter);
        if (!counter) {
            return;
        }

        const updateCounter = () => {
            counter.textContent = textarea.value.length;
        };

        textarea.addEventListener("input", updateCounter);
        updateCounter();
    });

    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            const submitButton = form.querySelector("button[type='submit'], input[type='submit']");
            if (!submitButton) {
                return;
            }
            submitButton.classList.add("is-loading");
            if (submitButton.tagName === "BUTTON") {
                submitButton.dataset.originalText = submitButton.innerHTML;
                submitButton.innerHTML = "<span class='spinner-border spinner-border-sm me-2'></span>Processing";
            }
        });
    });

    const statusChart = document.getElementById("statusChart");
    if (statusChart && window.Chart) {
        new Chart(statusChart, {
            type: "doughnut",
            data: {
                labels: ["Open", "In Progress", "Resolved", "Closed"],
                datasets: [{
                    data: [
                        Number(statusChart.dataset.open || 0),
                        Number(statusChart.dataset.progress || 0),
                        Number(statusChart.dataset.resolved || 0),
                        Number(statusChart.dataset.closed || 0),
                    ],
                    backgroundColor: ["#60a5fa", "#f59e0b", "#22c55e", "#94a3b8"],
                    borderColor: "rgba(15, 23, 42, 0.9)",
                    borderWidth: 4,
                    hoverOffset: 8,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: "#cbd5e1",
                            boxWidth: 12,
                            padding: 18,
                            usePointStyle: true,
                        },
                    },
                },
            },
        });
    }
});
