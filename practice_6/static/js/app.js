document.addEventListener('DOMContentLoaded', function() {
    // Set default dates (today and 7 days ago)
    const today = new Date().toISOString().split('T')[0];
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const weekAgoStr = weekAgo.toISOString().split('T')[0];

    document.getElementById('startDate').value = weekAgoStr;
    document.getElementById('endDate').value = today;

    // Helper function to add loading indicator
    function setLoading(button, isLoading) {
        const loadingId = button.id + 'Loading';
        if (isLoading) {
            if (!document.getElementById(loadingId)) {
                const loading = document.createElement('span');
                loading.id = loadingId;
                loading.className = 'loading';
                button.appendChild(loading);
            }
            button.disabled = true;
        } else {
            const loading = document.getElementById(loadingId);
            if (loading) {
                loading.remove();
            }
            button.disabled = false;
        }
    }

    // Helper function to display errors
    function showError(elementId, message) {
        const element = document.getElementById(elementId);
        element.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }

    // Helper function to format date
    function formatDate(dateStr) {
        return new Date(dateStr).toLocaleDateString();
    }

    // Fetch last trading dates
    document.getElementById('fetchDates').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        const limit = document.getElementById('datesLimit').value;
        const resultDiv = document.getElementById('datesResult');

        try {
            const response = await fetch(`/last-trading-dates/?limit=${limit}`);
            if (!response.ok) {
                throw new Error(`Ошибка HTTP! Статус: ${response.status}`);
            }
            const dates = await response.json();

            resultDiv.innerHTML = `
                <h5>Last ${dates.length} trading dates:</h5>
                <ul class="list-group">
                    ${dates.map(date => `<li class="list-group-item">${formatDate(date)}</li>`).join('')}
                </ul>
            `;
        } catch (error) {
            showError('datesResult', `Ошибка отображения дат: ${error.message}`);
        } finally {
            setLoading(button, false);
        }
    });

    // Fetch trading dynamics
    document.getElementById('fetchDynamics').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const oilId = document.getElementById('oilId').value;
        const deliveryType = document.getElementById('deliveryType').value;
        const deliveryBasis = document.getElementById('deliveryBasis').value;
        const resultDiv = document.getElementById('dynamicsResult');

        if (!startDate || !endDate) {
            showError('dynamicsResult', 'Выберите начальную и конечную даты');
            setLoading(button, false);
            return;
        }

        try {
            let url = `/dynamics/?start_date=${startDate}&end_date=${endDate}`;
            if (oilId) url += `&oil_id=${oilId}`;
            if (deliveryType) url += `&delivery_type_id=${deliveryType}`;
            if (deliveryBasis) url += `&delivery_basis_id=${deliveryBasis}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Ошибка HTTP! Статус: ${response.status}`);
            }
            const results = await response.json();

            if (results.length === 0) {
                resultDiv.innerHTML = '<div class="alert alert-info">Не найдено результатов по заданным критериям</div>';
                return;
            }

            resultDiv.innerHTML = `
                <h5>Results (${results.length} records):</h5>
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Oil ID</th>
                            <th>Delivery Type</th>
                            <th>Delivery Basis</th>
                            <th>Volume</th>
                            <th>Total</th>
                            <th>Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(result => `
                            <tr>
                                <td>${formatDate(result.trade_date)}</td>
                                <td>${result.oil_id}</td>
                                <td>${result.delivery_type_id}</td>
                                <td>${result.delivery_basis_id}</td>
                                <td>${result.volume?.toFixed(2) || '-'}</td>
                                <td>${result.total?.toFixed(2) || '-'}</td>
                                <td>${result.count}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            showError('dynamicsResult', `Ошибка отображения данных: ${error.message}`);
        } finally {
            setLoading(button, false);
        }
    });

    // Fetch recent trading results
    document.getElementById('fetchResults').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        const oilId = document.getElementById('resultsOilId').value;
        const deliveryType = document.getElementById('resultsDeliveryType').value;
        const deliveryBasis = document.getElementById('resultsDeliveryBasis').value;
        const limit = document.getElementById('resultsLimit').value;
        const resultDiv = document.getElementById('resultsTable');

        try {
            let url = `/trading-results/?limit=${limit}`;
            if (oilId) url += `&oil_id=${oilId}`;
            if (deliveryType) url += `&delivery_type_id=${deliveryType}`;
            if (deliveryBasis) url += `&delivery_basis_id=${deliveryBasis}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Ошибка HTTP! Статус: ${response.status}`);
            }
            const results = await response.json();

            if (results.length === 0) {
                resultDiv.innerHTML = '<div class="alert alert-info">Не найдено результатов по заданным критериям</div>';
                return;
            }

            resultDiv.innerHTML = `
                <h5>Recent Results (${results.length} records):</h5>
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Oil ID</th>
                            <th>Delivery Type</th>
                            <th>Delivery Basis</th>
                            <th>Volume</th>
                            <th>Total</th>
                            <th>Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(result => `
                            <tr>
                                <td>${formatDate(result.trade_date)}</td>
                                <td>${result.oil_id}</td>
                                <td>${result.delivery_type_id}</td>
                                <td>${result.delivery_basis_id}</td>
                                <td>${result.volume?.toFixed(2) || '-'}</td>
                                <td>${result.total?.toFixed(2) || '-'}</td>
                                <td>${result.count}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            showError('resultsTable', `Ошибка отображения данных: ${error.message}`);
        } finally {
            setLoading(button, false);
        }
    });
});