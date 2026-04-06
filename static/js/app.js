// ================= HELPER =================

function $(id) {
    return document.getElementById(id);
}

function fmt(n) {
    return "$" + Number(n || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function num(n) {
    return Number(n || 0).toLocaleString();
}

function safe(val) {
    return (val === null || val === undefined || val === "null" || val === "None") ? "—" : val;
}

// Chart.js global defaults for dark theme
Chart.defaults.color = '#cccccc';
Chart.defaults.borderColor = '#333333';
Chart.defaults.plugins.legend.labels.color = '#cccccc';
Chart.defaults.plugins.legend.labels.font = { size: 12 };

// Common chart options for proper sizing + readable axes
function getChartOptions(xLabel, yLabel, extraOpts) {
    return Object.assign({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#cccccc', font: { size: 12 } } },
            tooltip: { mode: 'index', intersect: false }
        },
        scales: {
            x: {
                title: { display: true, text: xLabel, color: '#ff6a00', font: { size: 12, weight: 'bold' } },
                ticks: { color: '#aaaaaa', font: { size: 10 }, maxRotation: 45, minRotation: 20, maxTicksLimit: 15 },
                grid: { display: false }
            },
            y: {
                title: { display: true, text: yLabel, color: '#ff6a00', font: { size: 12, weight: 'bold' } },
                ticks: {
                    color: '#aaaaaa',
                    font: { size: 10 },
                    callback: function(value) {
                        if (Math.abs(value) >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M';
                        if (Math.abs(value) >= 1000) return '$' + (value / 1000).toFixed(0) + 'K';
                        return '$' + value;
                    }
                },
                grid: { display: false }
            }
        }
    }, extraOpts || {});
}

function getBarChartOptions(xLabel, yLabel) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#cccccc', font: { size: 12 } } },
            tooltip: { mode: 'index', intersect: false }
        },
        scales: {
            x: {
                title: { display: true, text: xLabel, color: '#ff6a00', font: { size: 12, weight: 'bold' } },
                ticks: { color: '#aaaaaa', font: { size: 10 }, maxRotation: 30 },
                grid: { display: false }
            },
            y: {
                title: { display: true, text: yLabel, color: '#ff6a00', font: { size: 12, weight: 'bold' } },
                ticks: { color: '#aaaaaa', font: { size: 10 } },
                grid: { display: false },
                beginAtZero: true
            }
        }
    };
}


// ================= FILTER & MODAL HELPERS =================

function getFilterParams() {
    const year = $("filterYear") ? $("filterYear").value : "";
    const month = $("filterMonth") ? $("filterMonth").value : "";
    let params = [];
    if (year) params.push(`year=${year}`);
    if (month) params.push(`month=${month}`);
    return params.length > 0 ? "?" + params.join("&") : "";
}

function getCurrentPageKey() {
    const p = window.location.pathname;
    if (p === "/" || p === "/index.html") return "dashboard";
    if (p.includes("daily-revenue")) return "revenue";
    if (p.includes("operating-cost")) return "operating";
    if (p.includes("daily-expense")) return "expense";
    if (p === "/ap") return "payable";
    if (p === "/ar") return "receivable";
    if (p === "/gl") return "ledger";
    if (p.includes("chart-of-accounts")) return "chart";
    if (p === "/pl") return "pl";
    if (p.includes("revenue-recognition")) return "recognition";
    return "dashboard";
}

function hideAddModal() {
    $("addModal").style.display = "none";
}

function showAddModal() {
    const pageKey = getCurrentPageKey();
    const modal = $("addModal");
    const form = $("addForm");
    const title = $("modalTitle");

    modal.style.display = "block";
    form.innerHTML = "";

    if (pageKey === "revenue") {
        title.textContent = "Add Daily Revenue";
        addFormField("date", "Date", "date");
        addFormField("total_revenue", "Total Revenue", "number");
        addFormField("passenger_mainline", "Passenger Mainline", "number");
        addFormField("passenger_regional", "Passenger Regional", "number");
        addFormField("cargo_mail", "Cargo Mail", "number");
    } else if (pageKey === "operating") {
        title.textContent = "Add Operating Cost";
        addFormField("date", "Date", "date");
        addFormField("total_operating_cost", "Total Cost", "number");
        addFormField("fuel_oil", "Fuel & Oil", "number");
        addFormField("salaries_flight_crew", "Flight Crew Salaries", "number");
        addFormField("salaries_ground_staff", "Ground Staff Salaries", "number");
        addFormField("maintenance_repair", "Maintenance", "number");
        addFormField("airport_landing_fees", "Airport Fees", "number");
    } else if (pageKey === "expense") {
        title.textContent = "Add Daily Expense";
        addFormField("date", "Date", "date");
        addFormField("category", "Category", "text");
        addFormField("amount", "Amount", "number");
        addFormField("description", "Description", "text");
        addFormField("department", "Department", "text");
        addFormField("vendor", "Vendor", "text");
    } else if (pageKey === "payable") {
        title.textContent = "Add Account Payable";
        addFormField("vendor_name", "Vendor Name", "text");
        addFormField("invoice_number", "Invoice #", "text");
        addFormField("invoice_date", "Invoice Date", "date");
        addFormField("due_date", "Due Date", "date");
        addFormField("amount", "Amount", "number");
        addFormField("balance", "Balance", "number");
    } else if (pageKey === "receivable") {
        title.textContent = "Add Account Receivable";
        addFormField("customer_name", "Customer Name", "text");
        addFormField("invoice_number", "Invoice #", "text");
        addFormField("invoice_date", "Invoice Date", "date");
        addFormField("due_date", "Due Date", "date");
        addFormField("amount", "Amount", "number");
        addFormField("balance", "Balance", "number");
    } else if (pageKey === "ledger") {
        title.textContent = "Add Ledger Entry";
        addFormField("entry_date", "Entry Date", "date");
        addFormField("posting_date", "Posting Date", "date");
        addFormField("account_code", "Account Code", "text");
        addFormField("account_name", "Account Name", "text");
        addFormField("debit", "Debit", "number");
        addFormField("credit", "Credit", "number");
        addFormField("description", "Description", "text");
    } else if (pageKey === "chart") {
        title.textContent = "Add Chart of Account";
        addFormField("account_code", "Account Code", "text");
        addFormField("account_name", "Account Name", "text");
        addFormField("account_type", "Type (Asset/Liability/Equity/Revenue/Expense)", "text");
    } else if (pageKey === "pl") {
        title.textContent = "Add P&L Statement";
        addFormField("period", "Period (e.g. Q1-2026)", "text");
        addFormField("period_start", "Period Start", "date");
        addFormField("period_end", "Period End", "date");
        addFormField("total_revenue", "Total Revenue", "number");
        addFormField("total_expenses", "Total Expenses", "number");
        addFormField("operating_income", "Operating Income", "number");
        addFormField("pre_tax_income", "Pre-Tax Income", "number");
        addFormField("net_income", "Net Income", "number");
    } else if (pageKey === "recognition") {
        title.textContent = "Add Revenue Recognition";
        addFormField("booking_date", "Booking Date", "date");
        addFormField("service_date", "Service Date", "date");
        addFormField("recognition_date", "Recognition Date", "date");
        addFormField("flight_number", "Flight Number", "text");
        addFormField("route", "Route", "text");
        addFormField("gross_amount", "Gross Amount", "number");
        addFormField("recognized_amount", "Recognized Amount", "number");
        addFormField("deferred_amount", "Deferred Amount", "number");
        addFormField("recognition_method", "Recognition Method", "text");
        addFormField("status", "Status", "text");
    } else {
        title.textContent = "Add Revenue Record";
        addFormField("date", "Date", "date");
        addFormField("total_revenue", "Total Revenue", "number");
    }
}

function addFormField(name, label, type) {
    const div = document.createElement("div");
    div.className = "form-group";
    const isRequired = (type === "date" || name === "total_revenue" || name === "total_operating_cost"
        || name === "amount" || name === "vendor_name" || name === "customer_name"
        || name === "invoice_number" || name === "account_code" || name === "account_name"
        || name === "category" || name === "account_type" || name === "period"
        || name === "balance" || name === "net_income" || name === "operating_income"
        || name === "total_expenses") ? "required" : "";
    div.innerHTML = `
        <label>${label}</label>
        <input type="${type}" id="field_${name}" name="${name}" ${isRequired} step="any">
    `;
    $("addForm").appendChild(div);
}

async function submitNewData() {
    const pageKey = getCurrentPageKey();
    let apiPath = "";

    if (pageKey === "revenue") apiPath = "/api/revenue/";
    else if (pageKey === "operating") apiPath = "/api/operating-cost/";
    else if (pageKey === "expense") apiPath = "/api/daily-expense/";
    else if (pageKey === "payable") apiPath = "/api/accounts-payable/";
    else if (pageKey === "receivable") apiPath = "/api/accounts-receivable/";
    else if (pageKey === "ledger") apiPath = "/api/general-ledger/";
    else if (pageKey === "chart") apiPath = "/api/chart-of-accounts/";
    else if (pageKey === "pl") apiPath = "/api/profit-loss/";
    else if (pageKey === "recognition") apiPath = "/api/revenue-recognition/";
    else apiPath = "/api/revenue/";

    const inputs = $("addForm").querySelectorAll("input");
    const jsonData = {};
    inputs.forEach(input => {
        if (input.value === "") return;
        jsonData[input.name] = input.type === "number" ? parseFloat(input.value) || 0 : input.value;
    });

    try {
        const res = await fetch(apiPath, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(jsonData)
        });

        if (res.ok) {
            alert("Success! Data added.");
            hideAddModal();
            loadAllForCurrentPage(); // Refresh dashboard with new data
        } else {
            const err = await res.json();
            alert("Error: " + JSON.stringify(err.detail));
        }
    } catch (err) {
        alert("Failed to connect to API: " + err.message);
    }
}

function loadAllForCurrentPage() {
    const pageKey = getCurrentPageKey();

    if (pageKey === "dashboard") {
        loadDashboardSummary();
        loadDashboardRevenueChart();
        loadDashboardCostChart();
        loadDashboardProfitChart();
        loadDashboardRevenueTable();
        loadDashboardExpenseSummary();
        loadDashboardExpenseCategoryChart();
        loadDashboardCOASummary();
        loadDashboardCOATypeChart();
    } else if (pageKey === "revenue") {
        loadDailyRevenuePageSummary();
        loadDailyRevenuePageChart();
        loadDailyRevenuePageTable();
    } else if (pageKey === "operating") {
        loadOperatingCostPageSummary();
        loadOperatingCostPageChart();
        loadOperatingCostPageTable();
    } else if (pageKey === "expense") {
        loadDailyExpensePageSummary();
        loadDailyExpensePageChart();
        loadDailyExpensePageTable();
    } else if (pageKey === "payable") {
        loadAccountsPayableSummary();
        loadAccountsPayableAgingChart();
        loadAccountsPayableTable();
    } else if (pageKey === "receivable") {
        loadAccountsReceivableSummary();
        loadAccountsReceivableTable();
    } else if (pageKey === "ledger") {
        loadGeneralLedgerSummary();
        loadGeneralLedgerChart();
        loadGeneralLedgerTable();
    } else if (pageKey === "chart") {
        loadChartOfAccountsPageSummary();
        loadChartOfAccountsPageChart();
        loadChartOfAccountsPageTable();
    } else if (pageKey === "pl") {
        loadProfitLossSummary();
        loadProfitLossChart();
        loadProfitLossTable();
    } else if (pageKey === "recognition") {
        loadRevenueRecognitionSummary();
        loadRevenueRecognitionChart();
        loadRevenueRecognitionTable();
    }
}


// Event Listeners for Slicers (Year and Month dropdowns)
document.addEventListener("DOMContentLoaded", () => {
    if ($("filterYear")) $("filterYear").addEventListener("change", loadAllForCurrentPage);
    if ($("filterMonth")) $("filterMonth").addEventListener("change", loadAllForCurrentPage);
});


// ================= DASHBOARD KPI CARDS =================

async function loadDashboardSummary() {
    const params = getFilterParams();
    try {
        const revRes = await fetch("/api/revenue/summary" + params);
        const revData = await revRes.json();
        if ($("totalRevenue")) $("totalRevenue").textContent = fmt(revData.total_revenue_sum);

        const costRes = await fetch("/api/operating-cost/summary" + params);
        const costData = await costRes.json();
        if ($("totalOperatingCost")) $("totalOperatingCost").textContent = fmt(costData.total_operating_cost_sum);

        const profitRes = await fetch("/api/profit/summary" + params);
        const profitData = await profitRes.json();
        if ($("totalNetIncome")) $("totalNetIncome").textContent = fmt(profitData.total_net_income_sum);
    } catch (err) {
        console.error("Dashboard summary error:", err);
    }
}


// ================= DASHBOARD CHARTS =================

let dashRevenueChart;
async function loadDashboardRevenueChart() {
    const canvas = $("revenueChart");
    if (!canvas) return;

    const res = await fetch("/api/revenue/" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.date);
    const values = data.map(d => Number(d.total_revenue));

    if (dashRevenueChart) dashRevenueChart.destroy();

    dashRevenueChart = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{ label: "Revenue", data: values, borderColor: "#ff6a00", backgroundColor: "rgba(255, 106, 0, 0.15)", fill: true, tension: 0.3 }]
        },
        options: getChartOptions("Date", "Revenue ($)")
    });
}

let dashCostChart;
async function loadDashboardCostChart() {
    const canvas = $("costChart");
    if (!canvas) return;

    const res = await fetch("/api/operating-cost/" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.date);
    const values = data.map(d => Number(d.total_operating_cost));

    if (dashCostChart) dashCostChart.destroy();

    dashCostChart = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{ label: "Operating Cost", data: values, borderColor: "#ef4444", backgroundColor: "rgba(239, 68, 68, 0.15)", fill: true, tension: 0.3 }]
        },
        options: getChartOptions("Date", "Operating Cost ($)")
    });
}


let dashProfitChart;
async function loadDashboardProfitChart() {
    const canvas = $("profitChart");
    if (!canvas) return;

    const res = await fetch("/api/profit/" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.date);
    const values = data.map(d => Number(d.net_income));

    if (dashProfitChart) dashProfitChart.destroy();

    dashProfitChart = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{ label: "Net Income", data: values, borderColor: "#10b981", backgroundColor: "rgba(16, 185, 129, 0.15)", fill: true, tension: 0.3 }]
        },
        options: getChartOptions("Date", "Net Income ($)")
    });
}


// ================= DASHBOARD REVENUE TABLE =================

async function loadDashboardRevenueTable() {
    const tbody = document.querySelector("#revenueTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/revenue/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.date)}</td>
            <td>${fmt(row.total_revenue)}</td>
            <td>${fmt(row.passenger_mainline)}</td>
            <td>${fmt(row.cargo_mail)}</td>
            <td>${Number(row.load_factor || 0).toFixed(1)}%</td>
        `;
        tbody.appendChild(tr);
    });
}


// ================= DASHBOARD EXPENSE SUMMARY =================

async function loadDashboardExpenseSummary() {
    try {
        const res = await fetch("/api/daily-expense/summary" + getFilterParams());
        const data = await res.json();

        if ($("deTotalExpense")) $("deTotalExpense").textContent = fmt(data.total_expense);
        if ($("deTotalRecords")) $("deTotalRecords").textContent = num(data.total_records);
        if ($("deApprovedCount")) $("deApprovedCount").textContent = num(data.approved_count);
        if ($("dePendingCount")) $("dePendingCount").textContent = num(data.pending_count);
    } catch (err) {
        console.error("Dashboard expense summary error:", err);
    }
}


// ================= DASHBOARD EXPENSE CATEGORY CHART =================

let dashExpenseCategoryChart;
async function loadDashboardExpenseCategoryChart() {
    const canvas = $("dailyExpenseCategoryChart");
    if (!canvas) return;

    const res = await fetch("/api/daily-expense/category-summary" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.category);
    const values = data.map(d => Number(d.amount));
    const colors = ['#ff6a00', '#ff8533', '#ffa366', '#cc5500', '#994000', '#12b8a6', '#10b981', '#3b82f6'];

    if (dashExpenseCategoryChart) dashExpenseCategoryChart.destroy();

    dashExpenseCategoryChart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels,
            datasets: [{ data: values, backgroundColor: colors.slice(0, labels.length) }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#cccccc', font: { size: 11 }, padding: 12 } }
            }
        }
    });
}


// ================= DASHBOARD COA SUMMARY =================

async function loadDashboardCOASummary() {
    try {
        const res = await fetch("/api/chart-of-accounts/summary");
        const data = await res.json();

        if ($("coaTotalAccounts")) $("coaTotalAccounts").textContent = num(data.total_accounts);
        if ($("coaActiveAccounts")) $("coaActiveAccounts").textContent = num(data.active_accounts);
        if ($("coaHeaderAccounts")) $("coaHeaderAccounts").textContent = num(data.header_accounts);
        if ($("coaAccountTypes")) $("coaAccountTypes").textContent = num(data.unique_account_types);
    } catch (err) {
        console.error("Dashboard COA summary error:", err);
    }
}


// ================= DASHBOARD COA TYPE CHART =================

let dashCOATypeChart;
async function loadDashboardCOATypeChart() {
    const canvas = $("coaTypeChart");
    if (!canvas) return;

    const res = await fetch("/api/chart-of-accounts/type-summary");
    const data = await res.json();

    const labels = data.map(d => d.account_type);
    const values = data.map(d => Number(d.count));
    const colors = ['#ff6a00', '#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#ec4899'];

    if (dashCOATypeChart) dashCOATypeChart.destroy();

    dashCOATypeChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [{ label: "Accounts by Type", data: values, backgroundColor: colors.slice(0, labels.length) }]
        },
        options: getBarChartOptions("Account Type", "Count")
    });
}


// ================= DAILY REVENUE PAGE =================

async function loadDailyRevenuePageSummary() {
    try {
        const res = await fetch("/api/revenue/" + getFilterParams());
        const data = await res.json();
        if (!data.length) return;

        const totalRevenue = data.reduce((sum, d) => sum + Number(d.total_revenue), 0);
        const avgRevenue = totalRevenue / data.length;
        const topDay = data.reduce((max, d) => Number(d.total_revenue) > Number(max.total_revenue) ? d : max, data[0]);
        const avgLoadFactor = data.reduce((sum, d) => sum + Number(d.load_factor || 0), 0) / data.length;

        if ($("drTotalRevenue")) $("drTotalRevenue").textContent = fmt(totalRevenue);
        if ($("drAvgRevenue")) $("drAvgRevenue").textContent = fmt(avgRevenue);
        if ($("drTopRevenueDay")) $("drTopRevenueDay").textContent = topDay.date + " (" + fmt(topDay.total_revenue) + ")";
        if ($("drAvgLoadFactor")) $("drAvgLoadFactor").textContent = avgLoadFactor.toFixed(2) + "%";
    } catch (err) {
        console.error("Daily revenue page summary error:", err);
    }
}

async function loadDailyRevenuePageTable() {
    const tbody = document.querySelector("#dailyRevenuePageTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/revenue/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.date)}</td>
            <td>${fmt(row.passenger_mainline)}</td>
            <td>${fmt(row.passenger_regional)}</td>
            <td>${fmt(row.cargo_mail)}</td>
            <td>${fmt(row.total_revenue)}</td>
            <td>${Number(row.load_factor || 0).toFixed(1)}%</td>
        `;
        tbody.appendChild(tr);
    });
}

let dailyRevenueChart;
async function loadDailyRevenuePageChart() {
    const canvas = $("dailyRevenuePageChart");
    if (!canvas) return;

    const res = await fetch("/api/revenue/" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.date);
    const values = data.map(d => Number(d.total_revenue));

    if (dailyRevenueChart) dailyRevenueChart.destroy();

    dailyRevenueChart = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{ label: "Revenue", data: values, borderColor: "#ff6a00", backgroundColor: "rgba(255, 106, 0, 0.15)", fill: true, tension: 0.3 }]
        },
        options: getChartOptions("Date", "Revenue ($)")
    });
}


// ================= OPERATING COST PAGE =================

async function loadOperatingCostPageSummary() {
    try {
        const res = await fetch("/api/operating-cost/" + getFilterParams());
        const data = await res.json();
        if (!data.length) return;

        const totalCost = data.reduce((sum, d) => sum + Number(d.total_operating_cost), 0);
        const avgCost = totalCost / data.length;
        const highest = data.reduce((max, d) => Number(d.total_operating_cost) > Number(max.total_operating_cost) ? d : max, data[0]);
        const avgCasm = data.reduce((sum, d) => sum + Number(d.casm || 0), 0) / data.length;

        if ($("ocTotalCost")) $("ocTotalCost").textContent = fmt(totalCost);
        if ($("ocAvgCost")) $("ocAvgCost").textContent = fmt(avgCost);
        if ($("ocHighestCostDay")) $("ocHighestCostDay").textContent = highest.date + " (" + fmt(highest.total_operating_cost) + ")";
        if ($("ocAvgCasm")) $("ocAvgCasm").textContent = avgCasm.toFixed(4);
    } catch (err) {
        console.error("Operating cost page summary error:", err);
    }
}

async function loadOperatingCostPageTable() {
    const tbody = document.querySelector("#operatingCostPageTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/operating-cost/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.date)}</td>
            <td>${fmt(row.fuel_oil)}</td>
            <td>${fmt(row.salaries_flight_crew)}</td>
            <td>${fmt(row.salaries_ground_staff)}</td>
            <td>${fmt(row.maintenance_repair)}</td>
            <td>${fmt(row.airport_landing_fees)}</td>
            <td>${fmt(row.total_operating_cost)}</td>
            <td>${Number(row.casm || 0).toFixed(4)}</td>
        `;
        tbody.appendChild(tr);
    });
}

let operatingCostPageChart;
async function loadOperatingCostPageChart() {
    const canvas = $("operatingCostPageChart");
    if (!canvas) return;

    const res = await fetch("/api/operating-cost/" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.date);
    const values = data.map(d => Number(d.total_operating_cost));

    if (operatingCostPageChart) operatingCostPageChart.destroy();

    operatingCostPageChart = new Chart(canvas, {
        type: "line",
        data: {
            labels,
            datasets: [{ label: "Operating Cost", data: values, borderColor: "#ef4444", backgroundColor: "rgba(239, 68, 68, 0.15)", fill: true, tension: 0.3 }]
        },
        options: getChartOptions("Date", "Operating Cost ($)")
    });
}


// ================= DAILY EXPENSE PAGE =================

async function loadDailyExpensePageSummary() {
    try {
        const res = await fetch("/api/daily-expense/summary" + getFilterParams());
        const data = await res.json();

        if ($("dxTotalExpense")) $("dxTotalExpense").textContent = fmt(data.total_expense);
        if ($("dxTotalRecords")) $("dxTotalRecords").textContent = num(data.total_records);
        if ($("dxApprovedCount")) $("dxApprovedCount").textContent = num(data.approved_count);
        if ($("dxPendingCount")) $("dxPendingCount").textContent = num(data.pending_count);
    } catch (err) {
        console.error("Daily expense page summary error:", err);
    }
}

async function loadDailyExpensePageTable() {
    const tbody = document.querySelector("#dailyExpensePageTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/daily-expense/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.date)}</td>
            <td>${safe(row.category)}</td>
            <td>${safe(row.description)}</td>
            <td>${fmt(row.amount)}</td>
            <td>${safe(row.department)}</td>
            <td>${safe(row.vendor)}</td>
            <td>${safe(row.cost_center)}</td>
            <td>${safe(row.approved_by)}</td>
            <td>${safe(row.status)}</td>
        `;
        tbody.appendChild(tr);
    });
}

let dailyExpensePageChart;
async function loadDailyExpensePageChart() {
    const canvas = $("dailyExpensePageChart");
    if (!canvas) return;

    const res = await fetch("/api/daily-expense/category-summary" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.category);
    const values = data.map(d => Number(d.amount));
    const colors = ['#ff6a00', '#ff8533', '#ffa366', '#cc5500', '#994000', '#12b8a6', '#10b981', '#3b82f6'];

    if (dailyExpensePageChart) dailyExpensePageChart.destroy();

    dailyExpensePageChart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels,
            datasets: [{ data: values, backgroundColor: colors.slice(0, labels.length) }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#cccccc', font: { size: 11 }, padding: 12 } }
            }
        }
    });
}


// ================= ACCOUNTS PAYABLE PAGE =================

async function loadAccountsPayableSummary() {
    try {
        const res = await fetch("/api/accounts-payable/summary" + getFilterParams());
        const data = await res.json();

        if ($("apTotalOutstanding")) $("apTotalOutstanding").textContent = fmt(data.total_outstanding);
        if ($("apTotalPaid")) $("apTotalPaid").textContent = fmt(data.total_paid);
        if ($("apOverdueCount")) $("apOverdueCount").textContent = num(data.overdue_count);
        if ($("apTotalInvoices")) $("apTotalInvoices").textContent = num(data.total_invoices);
    } catch (err) {
        console.error("AP summary error:", err);
    }
}

let apAgingChart;
async function loadAccountsPayableAgingChart() {
    const canvas = $("apAgingChart");
    if (!canvas) return;

    const res = await fetch("/api/accounts-payable/aging" + getFilterParams());
    const data = await res.json();

    const labels = ["Current", "1-30 Days", "31-60 Days", "61-90 Days", "90+ Days"];
    const values = [data.current, data.days_1_30, data.days_31_60, data.days_61_90 || 0, data.days_90_plus];

    if (apAgingChart) apAgingChart.destroy();

    apAgingChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [{ label: "AP Aging ($)", data: values, backgroundColor: ["#ff6a00", "#f59e0b", "#ef4444", "#dc2626", "#991b1b"] }]
        },
        options: getBarChartOptions("Aging Bucket", "Amount ($)")
    });
}

async function loadAccountsPayableTable() {
    const tbody = document.querySelector("#apTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/accounts-payable/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.vendor_name)}</td>
            <td>${safe(row.invoice_number)}</td>
            <td>${fmt(row.amount)}</td>
            <td>${fmt(row.paid_amount)}</td>
            <td>${fmt(row.balance)}</td>
            <td>${safe(row.due_date)}</td>
        `;
        tbody.appendChild(tr);
    });
}


// ================= ACCOUNTS RECEIVABLE PAGE =================

async function loadAccountsReceivableSummary() {
    try {
        const res = await fetch("/api/accounts-receivable/summary" + getFilterParams());
        const data = await res.json();

        if ($("arTotalOutstanding")) $("arTotalOutstanding").textContent = fmt(data.total_outstanding);
        if ($("arTotalReceived")) $("arTotalReceived").textContent = fmt(data.total_received);
        if ($("arOverdueCount")) $("arOverdueCount").textContent = num(data.overdue_count);
        if ($("arTotalInvoices")) $("arTotalInvoices").textContent = num(data.total_invoices);
    } catch (err) {
        console.error("AR summary error:", err);
    }
}

async function loadAccountsReceivableTable() {
    const tbody = document.querySelector("#arTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/accounts-receivable/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.customer_name)}</td>
            <td>${safe(row.invoice_number)}</td>
            <td>${fmt(row.amount)}</td>
            <td>${fmt(row.received_amount)}</td>
            <td>${fmt(row.balance)}</td>
            <td>${safe(row.due_date)}</td>
        `;
        tbody.appendChild(tr);
    });
}


// ================= GENERAL LEDGER PAGE =================

async function loadGeneralLedgerSummary() {
    try {
        const res = await fetch("/api/general-ledger/summary" + getFilterParams());
        const data = await res.json();

        if ($("glTotalDebit")) $("glTotalDebit").textContent = fmt(data.total_debit);
        if ($("glTotalCredit")) $("glTotalCredit").textContent = fmt(data.total_credit);
        if ($("glTotalEntries")) $("glTotalEntries").textContent = num(data.total_entries);
        if ($("glNetBalance")) $("glNetBalance").textContent = fmt(data.net_balance);
    } catch (err) {
        console.error("GL summary error:", err);
    }
}

let generalLedgerChart;
async function loadGeneralLedgerChart() {
    const canvas = $("generalLedgerChart");
    if (!canvas) return;

    const res = await fetch("/api/general-ledger/chart-summary" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.date);
    const debits = data.map(d => Number(d.debit));
    const credits = data.map(d => Number(d.credit));

    if (generalLedgerChart) generalLedgerChart.destroy();

    generalLedgerChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [
                { label: "Debit", data: debits, backgroundColor: "#ff6a00" },
                { label: "Credit", data: credits, backgroundColor: "#12b8a6" }
            ]
        },
        options: getBarChartOptions("Date", "Amount ($)")
    });
}

async function loadGeneralLedgerTable() {
    const tbody = document.querySelector("#generalLedgerTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/general-ledger/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.entry_date)}</td>
            <td>${safe(row.posting_date)}</td>
            <td>${safe(row.account_code)}</td>
            <td>${safe(row.account_name)}</td>
            <td>${fmt(row.debit)}</td>
            <td>${fmt(row.credit)}</td>
            <td>${row.is_reconciled ? "Yes" : "No"}</td>
        `;
        tbody.appendChild(tr);
    });
}


// ================= PROFIT & LOSS PAGE =================

async function loadProfitLossSummary() {
    try {
        const res = await fetch("/api/profit-loss/summary" + getFilterParams());
        const data = await res.json();

        if ($("plTotalRevenue")) $("plTotalRevenue").textContent = fmt(data.total_revenue);
        if ($("plTotalExpenses")) $("plTotalExpenses").textContent = fmt(data.total_expenses);
        if ($("plTotalNetIncome")) $("plTotalNetIncome").textContent = fmt(data.total_net_income);
        if ($("plTotalPeriods")) $("plTotalPeriods").textContent = num(data.total_periods);
    } catch (err) {
        console.error("P&L summary error:", err);
    }
}

let plChart;
async function loadProfitLossChart() {
    const canvas = $("profitLossChart");
    if (!canvas) return;

    const res = await fetch("/api/profit-loss/chart-summary" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.period);
    const revenue = data.map(d => Number(d.revenue));
    const expenses = data.map(d => Number(d.expenses));
    const netIncome = data.map(d => Number(d.net_income));

    if (plChart) plChart.destroy();

    plChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [
                { label: "Revenue", data: revenue, backgroundColor: "#ff6a00" },
                { label: "Expenses", data: expenses, backgroundColor: "#ef4444" },
                { label: "Net Income", data: netIncome, backgroundColor: "#10b981" }
            ]
        },
        options: getBarChartOptions("Period", "Amount ($)")
    });
}

async function loadProfitLossTable() {
    const tbody = document.querySelector("#profitLossTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/profit-loss/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.period)}</td>
            <td>${safe(row.period_start)}</td>
            <td>${safe(row.period_end)}</td>
            <td>${fmt(row.total_revenue)}</td>
            <td>${fmt(row.total_expenses)}</td>
            <td>${fmt(row.operating_income)}</td>
            <td>${fmt(row.pre_tax_income)}</td>
            <td>${fmt(row.net_income)}</td>
        `;
        tbody.appendChild(tr);
    });
}


// ================= CHART OF ACCOUNTS PAGE =================

async function loadChartOfAccountsPageSummary() {
    try {
        const res = await fetch("/api/chart-of-accounts/summary");
        const data = await res.json();

        if ($("caTotalAccounts")) $("caTotalAccounts").textContent = num(data.total_accounts);
        if ($("caActiveAccounts")) $("caActiveAccounts").textContent = num(data.active_accounts);
        if ($("caHeaderAccounts")) $("caHeaderAccounts").textContent = num(data.header_accounts);
        if ($("caUniqueAccountTypes")) $("caUniqueAccountTypes").textContent = num(data.unique_account_types);
    } catch (err) {
        console.error("COA page summary error:", err);
    }
}

let coaPageChart;
async function loadChartOfAccountsPageChart() {
    const canvas = $("chartOfAccountsPageChart");
    if (!canvas) return;

    const res = await fetch("/api/chart-of-accounts/type-summary");
    const data = await res.json();

    const labels = data.map(d => d.account_type);
    const values = data.map(d => Number(d.count));
    const colors = ['#ff6a00', '#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#ec4899'];

    if (coaPageChart) coaPageChart.destroy();

    coaPageChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [{ label: "Accounts by Type", data: values, backgroundColor: colors.slice(0, labels.length) }]
        },
        options: getBarChartOptions("Account Type", "Count")
    });
}

async function loadChartOfAccountsPageTable() {
    const tbody = document.querySelector("#chartOfAccountsPageTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/chart-of-accounts/");
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.account_code)}</td>
            <td>${safe(row.account_name)}</td>
            <td>${safe(row.account_type)}</td>
            <td>${safe(row.sub_type)}</td>
            <td>${safe(row.parent_code)}</td>
            <td>${safe(row.normal_balance)}</td>
            <td>${row.is_active ? "Yes" : "No"}</td>
            <td>${row.is_header ? "Yes" : "No"}</td>
            <td>${safe(row.currency)}</td>
        `;
        tbody.appendChild(tr);
    });
}


// ================= REVENUE RECOGNITION PAGE =================

async function loadRevenueRecognitionSummary() {
    try {
        const res = await fetch("/api/revenue-recognition/summary" + getFilterParams());
        const data = await res.json();

        if ($("rrTotalGross")) $("rrTotalGross").textContent = fmt(data.total_gross);
        if ($("rrTotalRecognized")) $("rrTotalRecognized").textContent = fmt(data.total_recognized);
        if ($("rrTotalDeferred")) $("rrTotalDeferred").textContent = fmt(data.total_deferred);
        if ($("rrTotalTransactions")) $("rrTotalTransactions").textContent = num(data.total_transactions);
    } catch (err) {
        console.error("RR summary error:", err);
    }
}

let rrChart;
async function loadRevenueRecognitionChart() {
    const canvas = $("revenueRecognitionChart");
    if (!canvas) return;

    const res = await fetch("/api/revenue-recognition/chart-summary" + getFilterParams());
    const data = await res.json();

    const labels = data.map(d => d.date);
    const recognized = data.map(d => Number(d.recognized));
    const deferred = data.map(d => Number(d.deferred));

    if (rrChart) rrChart.destroy();

    rrChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [
                { label: "Recognized", data: recognized, backgroundColor: "#10b981" },
                { label: "Deferred", data: deferred, backgroundColor: "#ef4444" }
            ]
        },
        options: getBarChartOptions("Booking Date", "Amount ($)")
    });
}

async function loadRevenueRecognitionTable() {
    const tbody = document.querySelector("#revenueRecognitionTable tbody");
    if (!tbody) return;

    const res = await fetch("/api/revenue-recognition/" + getFilterParams());
    const data = await res.json();

    tbody.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${safe(row.booking_date)}</td>
            <td>${safe(row.service_date)}</td>
            <td>${safe(row.flight_number)}</td>
            <td>${safe(row.route)}</td>
            <td>${fmt(row.gross_amount)}</td>
            <td>${fmt(row.recognized_amount)}</td>
            <td>${fmt(row.deferred_amount)}</td>
            <td>${safe(row.recognition_method)}</td>
            <td>${safe(row.status)}</td>
        `;
        tbody.appendChild(tr);
    });
}


// ================= INIT =================

window.addEventListener("DOMContentLoaded", () => {
    loadAllForCurrentPage();
});