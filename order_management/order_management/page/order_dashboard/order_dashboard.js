// NOTE: If your page console throws an undefined error here, switch 'order_dashboard' to 'order-dashboard'
frappe.pages['order-dashboard'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Order Management Dashboard',
        single_column: true
    });

    // 1. Inject Tailwind directly into the head layer cleanly
    if (!document.getElementById('tailwind-cdn')) {
        let script = document.createElement('script');
        script.id = 'tailwind-cdn';
        script.src = 'https://cdn.tailwindcss.com';
        document.head.appendChild(script);
    }

    // 2. Fetch and render your custom HTML file template
    let html_content = frappe.render_template('order_dashboard', {});
    
    // 3. Inject it straight into the active page element wrapper 
    $(wrapper).find('.layout-main-section').html(html_content);

    // Utility Formatters
    const formatCurrency = (value) => `₹${Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
    
    const statusBadge = (status) => {
        const statusMap = {
            'Confirmed': 'bg-emerald-100 text-emerald-800',
            'Draft': 'bg-slate-100 text-slate-700',
            'Cancelled': 'bg-rose-100 text-rose-800',
            'Pending': 'bg-amber-100 text-amber-800'
        };
        const cssClass = statusMap[status] || 'bg-gray-100 text-gray-700';
        return `<span class="px-2 py-0.5 rounded text-xs font-semibold inline-block ${cssClass}">${status || __('Unknown')}</span>`;
    };

    // Master API Execution Call logic wrapper
    function load_dashboard_data() {
        frappe.call({
            method: 'order_management.api.get_dashboard_stats',
            callback: function (r) {
                const d = r.message || {};

                // Bind Metric Stats
                $('#total-orders').text(d.total_orders || 0);
                $('#confirmed-orders').text(d.confirmed_orders || 0);
                $('#draft-orders').text(d.draft_orders || 0);
                $('#revenue').text(formatCurrency(d.revenue));
                $('#avg-order-value').text(formatCurrency(d.avg_order_value));
                $('#open-orders').text(d.open_orders || 0);

                // Populate Recent Orders Stream
                const recentOrdersBody = $('#recent-orders-body').empty();
                if(d.recent_orders && d.recent_orders.length) {
                    d.recent_orders.forEach(order => {
                        recentOrdersBody.append(`
                            <tr class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                <td class="p-3"><a class="font-bold text-blue-600 hover:underline" href="/app/sales-order/${order.name}">${order.name}</a></td>
                                <td class="p-3"><span class="text-gray-700">${order.customer || '-'}</span></td>
                                <td class="p-3">${statusBadge(order.status)}</td>
                                <td class="p-3 text-end font-bold text-gray-900">${formatCurrency(order.total_amount)}</td>
                            </tr>
                        `);
                    });
                } else {
                    recentOrdersBody.append(`<tr><td colspan="4" class="text-center py-6 text-gray-400">${__('No recent orders found')}</td></tr>`);
                }

                // Render High-fidelity Data Distribution Chart Charting
                const labels = [];
                const values = [];
                (d.status_data || []).forEach(row => {
                    labels.push(row.status);
                    values.push(row.count);
                });

                $('#status-chart').empty();
                new frappe.Chart('#status-chart', {
                    title: '',
                    data: { labels, datasets: [{ values }] },
                    type: 'donut', 
                    height: 260,
                    colors: ['#2563eb', '#059669', '#d97706', '#e11d48', '#64748b'],
                    maxLegendPoints: 4,
                    dontRender: 0
                });

                // Top Customers List Population
                const customerBody = $('#top-customers-body').empty();
                if(d.top_customers && d.top_customers.length) {
                    d.top_customers.forEach((customer) => {
                        customerBody.append(`
                            <tr class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                <td class="p-3"><div class="font-medium text-gray-800">${customer.customer || '-'}</div></td>
                                <td class="p-3 text-end text-emerald-600 font-bold">${formatCurrency(customer.revenue)}</td>
                            </tr>
                        `);
                    });
                } else {
                    customerBody.append(`<tr><td colspan="2" class="text-center py-4 text-gray-400">${__('No data available')}</td></tr>`);
                }

                // Inventory Reorder Low Stock Management
                const lowStockBody = $('#low-stock-body').empty();
                if(d.low_stock_items && d.low_stock_items.length) {
                    d.low_stock_items.slice(0, 3).forEach((item) => { 
                        lowStockBody.append(`
                            <tr class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                <td class="p-3"><span class="font-medium text-gray-800">${item.Item_name}</span></td>
                                <td class="p-3"><span class="bg-rose-100 text-rose-800 font-medium text-xs px-2 py-0.5 rounded-full">${item.stock || 0} left</span></td>
                                <td class="p-3 text-end">
                                    <a href="/app/item/${item.Item_name}" class="text-blue-600 font-semibold text-xs hover:underline">${__('Restock')}</a>
                                </td>
                            </tr>
                        `);
                    });
                } else {
                    lowStockBody.append(`<tr><td colspan="3" class="text-center py-4 text-emerald-600 font-medium">✔️ All stock levels optimal</td></tr>`);
                }
            }
        });
    }

    // 4. Run your live backend fetch functions (FIXED: Moved into initialization lifecycle)
    load_dashboard_data();
};