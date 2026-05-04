document.addEventListener('DOMContentLoaded', () => {
    // Only run if on a dashboard page
    if (!document.getElementById('dashboard-stats-container')) return;

    let previousData = null;

    function updateDashboard() {
        fetch('/api/dashboard_data')
            .then(response => response.json())
            .then(data => {
                if (!previousData) {
                    previousData = data;
                    return;
                }

                // Check if anything changed
                let hasChanges = false;
                
                // Update stats
                ['total', 'open', 'progress', 'resolved', 'closed', 'attention'].forEach(key => {
                    const el = document.getElementById(`stat-${key}`);
                    if (el && parseInt(el.textContent) !== data.stats[key]) {
                        el.textContent = data.stats[key];
                        // Add a little highlight animation
                        el.classList.add('text-primary');
                        setTimeout(() => el.classList.remove('text-primary'), 1000);
                        hasChanges = true;
                    }
                });

                // Check for new tickets or status changes
                if (data.tickets.length > previousData.tickets.length) {
                    showToast('New ticket arrived!', 'success');
                    hasChanges = true;
                } else {
                    // check if status changed on any ticket
                    data.tickets.forEach(ticket => {
                        const prev = previousData.tickets.find(t => t.id === ticket.id);
                        if (prev && prev.status !== ticket.status) {
                            showToast(`Ticket #${ticket.id} status changed to ${ticket.status}`, 'info');
                            hasChanges = true;
                        }
                    });
                }

                // If changes, re-render the table body
                if (hasChanges) {
                    const tbody = document.getElementById('tickets-table-body');
                    if (tbody) {
                        tbody.innerHTML = '';
                        const isAdmin = window.location.pathname.includes('/admin');
                        data.tickets.forEach(t => {
                            const dateStr = new Date(t.created_at).toLocaleString(undefined, {
                                year: 'numeric', month: 'short', day: 'numeric',
                                hour: '2-digit', minute: '2-digit'
                            });
                            
                            const tr = document.createElement('tr');
                            tr.className = 'align-middle slide-in';
                            
                            if (isAdmin) {
                                tr.innerHTML = `
                                    <td class="ps-4"><span class="badge bg-light text-dark border">#${t.id}</span></td>
                                    <td><div class="fw-medium text-dark">${t.username}</div></td>
                                    <td class="fw-bold">${t.title}</td>
                                    <td><span class="badge rounded-pill ${getPriorityBadgeClass(t.priority)}">${t.priority}</span></td>
                                    <td><span class="badge rounded-pill ${getStatusBadgeClass(t.status)}">${t.status}</span></td>
                                    <td class="text-muted small">${dateStr}</td>
                                    <td class="text-end pe-4">
                                        <a href="/tickets/${t.id}" class="btn btn-sm btn-outline-primary">Manage</a>
                                    </td>
                                `;
                            } else {
                                tr.innerHTML = `
                                    <td class="ps-4"><span class="badge bg-light text-dark border">#${t.id}</span></td>
                                    <td class="fw-bold">${t.title}</td>
                                    <td><span class="badge rounded-pill ${getPriorityBadgeClass(t.priority)}">${t.priority}</span></td>
                                    <td><span class="badge rounded-pill ${getStatusBadgeClass(t.status)}">${t.status}</span></td>
                                    <td class="text-muted small">${dateStr}</td>
                                    <td class="text-end pe-4">
                                        <a href="/tickets/${t.id}" class="btn btn-sm btn-outline-primary">View</a>
                                    </td>
                                `;
                            }
                            tbody.appendChild(tr);
                        });
                    }
                }
                
                previousData = data;
            })
            .catch(err => console.error("Error fetching live updates:", err));
    }

    // Polling every 5 seconds
    setInterval(updateDashboard, 5000);
});

function getPriorityBadgeClass(prio) {
    if (prio === 'Critical') return 'bg-danger';
    if (prio === 'High') return 'bg-warning text-dark';
    if (prio === 'Medium') return 'bg-info text-dark';
    return 'bg-secondary';
}

function getStatusBadgeClass(status) {
    if (status === 'Open') return 'bg-primary';
    if (status === 'In Progress') return 'bg-warning text-dark';
    if (status === 'Resolved') return 'bg-success';
    return 'bg-secondary';
}

// Simple Toast Notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}
