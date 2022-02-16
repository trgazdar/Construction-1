odoo.define('pos_reserve_order_app.pos_reserve_order', function(require) {
    "use strict";

    var config = require('web.config');
    var dom = require('web.dom');
    var field_utils = require('web.field_utils');
    var Pager = require('web.Pager');
    var utils = require('web.utils');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;

    var reserve_amount;
    var pos_order_domain = [];


    screens.PaymentScreenWidget.include({
        show: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            this.$('.reserve').click(function() {
                if ($(this).hasClass('highlight')) {
                    self.reserve_order();
                }
            });
        },

        order_changes: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            if (!order) {
                return
            } else if (order.get_due() == 0 || order.get_due() == order.get_total_with_tax() || order.get_total_paid() >= order.get_total_with_tax()) {
                self.$('.reserve').removeClass('highlight');
            } else {
                self.$('.reserve').addClass('highlight');
            }
        },

        reserve_order: function() {
            var self = this;
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            var paymentlines = order.get_paymentlines();
            var total_paid = order.get_total_paid();
            var total = order.get_total_with_tax();
            var reserve_charge_type = this.pos.config.reserve_charge_type;
            var reserve_charge = this.pos.config.min_reserve_charges;
            if (reserve_charge_type == 'percentage') {
                reserve_amount = (total * reserve_charge) / 100.0
            } else {
                reserve_amount = reserve_charge;
            }
            if (total_paid < reserve_amount) {
                self.gui.show_popup('error', {
                    'title': _t('Reserve Order Amount Error'),
                    'body': _t('Please Pay minimum amount to Reserve Order.'),
                });
                return;
            }
            var partner_id = false
            if (order.get_client() != null)
                partner_id = order.get_client();
            if (!partner_id) {
                self.gui.show_popup('error', {
                    'title': _t('Unknown customer'),
                    'body': _t('You cannot Reserve Order. Select customer first.'),
                });
                return;
            } else if (orderlines.length === 0) {
                self.gui.show_popup('error', {
                    'title': _t('Empty Order'),
                    'body': _t('There must be at least one product in your order before it can be validated.'),
                });
                return;
            } else {
                if (order.get_total_with_tax() !== order.get_total_paid() && order.get_total_paid() != 0) {
                    self.gui.show_popup('select_reserve_date_widget', {});
                }
            }
        },
    });


    var posorder_super = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr, options) {
            this.delivery_date = this.delivery_date || false;
            this.amount_due = this.amount_due || 0;
            this.is_reserved = this.is_reserved || false;
            posorder_super.initialize.call(this, attr, options);
        },

        export_as_JSON: function() {
            var loaded = posorder_super.export_as_JSON.apply(this, arguments);
            loaded.is_reserved = this.is_reserved || false;
            loaded.amount_due = this.amount_due;
            loaded.delivery_date = this.delivery_date;
            return loaded;
        },

    });

    var SelectReserveDateWidget = popups.extend({
        template: 'SelectReserveDateWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var selectedOrder = self.pos.get('selectedOrder');
            var partner_id = false
            if (order.get_client() != null)
                partner_id = order.get_client();

            this.$('#apply_date').click(function() {
                self.create_reserve_order();
            });
        },

        get_current_day: function() {
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth() + 1; //January is 0!
            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd;
            }
            if (mm < 10) {
                mm = '0' + mm;
            }
            today = yyyy + '-' + mm + '-' + dd;
            return today;
        },


        create_reserve_order: function() {
            var self = this;
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            var paymentlines = order.get_paymentlines();
            var total = order.get_total_with_tax();
            var entered_date = $("#entered_date").val();

            var orderLines, paymentLines;
            orderLines = [];
            order.orderlines.each(_.bind(function(item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, order));
            paymentLines = [];
            order.paymentlines.each(_.bind(function(item) {
                return paymentLines.push([0, 0, item.export_as_JSON()]);
            }, order));
            if (!entered_date) {
                alert('Please Select Delivery Date');
            } else {
                var today_date = self.get_current_day();
                var d1 = Date.parse(today_date);
                var d2 = Date.parse(entered_date);
                if (d1 > d2) {
                    alert("Please Select Valid Date");
                } else {
                    // var create_order = {
                    // 	name: order.get_name(),
                    // 	amount_paid: order.get_total_paid(),
                    // 	amount_due: total - order.get_total_paid(),
                    // 	amount_total: total,
                    // 	amount_tax: order.get_total_tax(),
                    // 	amount_return: order.get_change(),
                    // 	lines: orderLines,
                    // 	statement_ids: paymentLines,
                    // 	pos_session_id: order.pos_session_id,
                    // 	pricelist_id: order.pricelist ? order.pricelist.id : false,
                    // 	partner_id: order.get_client() ? order.get_client().id : false,
                    // 	user_id: order.pos.get_cashier().id,
                    // 	uid: order.uid,
                    // 	sequence_number: order.sequence_number,
                    // 	creation_date: order.creation_date,
                    // 	delivery_date : entered_date,
                    // 	is_reserved : true,
                    // 	fiscal_position_id: order.fiscal_position ? order.fiscal_position.id : false
                    // }
                    // order.amount_due = total - order.get_total_paid();
                    // order.delivery_date = entered_date;
                    // self.pos.db.add_order(order.export_as_JSON());
                    // return rpc.query({
                    // 	model: 'pos.order',
                    // 	method: 'create_pos_order',
                    // 	args: [1,create_order],
                    // }).then(function (server_ids) {
                    // 	self.gui.show_screen('receipt');
                    // })

                    order.is_reserved = true;
                    order.amount_due = total - order.get_total_paid();
                    order.delivery_date = entered_date;
                    order.to_invoice = false;
                    order.finalized = false;
                    self.pos.push_order(order);
                    self.gui.show_screen('receipt');

                }

            }
        },

    });
    gui.define_popup({
        name: 'select_reserve_date_widget',
        widget: SelectReserveDateWidget
    });
    // get_bill_orderlines extend here for categorywise receipt generate for full amount only.
    models.Order = models.Order.extend({
        get_bill_orderlines: function() {
            var order_id = this.pos.get_order();
            var bill_categs = []
            if (order_id.amount_due <= 0) {
                _(this.pos.get_order().get_orderlines()).map(function(result) {
                    if (result.product.bill_category != false) {
                        for (var i = 0; i < bill_categs.length; i++) {
                            if (bill_categs[i].name == result.product.bill_category[1]) {
                                bill_categs[i].orderlines.push(result);

                                return;
                            }
                        }
                        bill_categs.push({
                            'name': result.product.bill_category[1],
                            'orderlines': [result]
                        });
                    }
                });
            }
            return bill_categs;
        },
    });
    // Start SeeReservedOrdersButtonWidget

    var SeeReservedOrdersButtonWidget = screens.ActionButtonWidget.extend({
        template: 'SeeReservedOrdersButtonWidget',

        button_click: function() {
            var self = this;
            var params = self.pos.get_order().get_screen_data('params');
            if (params && params['selected_partner_id']) {
                params['selected_partner_id'] = undefined;
            }
            this.gui.show_screen('see_reserve_orders_screen_widget', {});
        },

    });

    screens.define_action_button({
        'name': 'See Reserved Orders Button Widget',
        'widget': SeeReservedOrdersButtonWidget,
        'condition': function() {
            return true;
        },
    });

    // SeeReservedOrdersScreenWidget start

    var SeeReservedOrdersScreenWidget = screens.ScreenWidget.extend({
        template: 'SeeReservedOrdersScreenWidget',
        init: function(parent, options) {
            this._super(parent, options);
            //this.options = {};
        },

        get_selected_partner: function() {
            var self = this;
            if (self.gui)
                return self.gui.get_current_screen_param('selected_partner_id');
            else
                return undefined;
        },

        render_list_orders: function(orders, search_input) {
            var self = this;
            if (orders == undefined) {
                orders = self.pos.get('reserved_orders_list');
            }
            var selected_partner_id = this.get_selected_partner();
            var selected_client_orders = [];
            if (selected_partner_id != undefined) {
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].partner_id[0] == selected_partner_id)
                        selected_client_orders = selected_client_orders.concat(orders[i]);
                }
                orders = selected_client_orders;
            }

            if (search_input != undefined && search_input != '') {
                var selected_search_orders = [];
                var search_text = search_input.toLowerCase()
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].partner_id == '') {
                        orders[i].partner_id = [0, '-'];
                    }
                    if (orders[i].partner_id[1] == false) {
                        if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].state.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1)) {
                            selected_search_orders = selected_search_orders.concat(orders[i]);
                        }
                    } else {
                        if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].state.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].pos_reference.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
                            selected_search_orders = selected_search_orders.concat(orders[i]);
                        }
                    }
                }
                orders = selected_search_orders;
            }

            var content = this.$el[0].querySelector('.orders-list-contents');
            content.innerHTML = "";
            var orders = orders;
            var current_date = null;
            if (orders != undefined) {
                for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                    var order = orders[i];
                    current_date = field_utils.format.datetime(moment(order.date_order), {
                        type: 'datetime'
                    });
                    var ordersline_html = QWeb.render('OrdersLine', {
                        widget: this,
                        order: orders[i],
                        selected_partner_id: orders[i].partner_id[0],
                        current_date: current_date
                    });
                    var ordersline = document.createElement('tbody');
                    ordersline.innerHTML = ordersline_html;
                    ordersline = ordersline.childNodes[1];
                    content.appendChild(ordersline);

                }
            }

        },
        get_orders_domain: function() {
            var self = this;
            var days = self.pos.config.last_days
            var pos_order_domain = [
                ['state', 'in', ['reserved']]
            ];
            if (days > 0) {
                var today = new Date();
                today.setDate(today.getDate() - days);
                var dd = today.getDate();
                var mm = today.getMonth() + 1; //January is 0!
                var yyyy = today.getFullYear();
                if (dd < 10) {
                    dd = '0' + dd;
                }
                if (mm < 10) {
                    mm = '0' + mm;
                }
                var today = yyyy + '-' + mm + '-' + dd + " " + "00" + ":" + "00" + ":" + "00";
                pos_order_domain.push(['date_order', '>=', today])
            }
            return pos_order_domain;
        },

        get_orders_fields: function() {
            var fields = ['name', 'id', 'date_order', 'delivery_date', 'partner_id', 'pos_reference', 'lines', 'amount_total', 'amount_due', 'amount_paid', 'session_id', 'state', 'company_id', 'amount_tax', 'pos_reference'];
            return fields;
        },

        get_pos_orders: function() {
            var self = this;
            var fields = self.get_orders_fields();
            var pos_domain = self.get_orders_domain();
            var load_orders = [];
            var load_orders_line = [];
            var order_ids = [];
            rpc.query({
                model: 'pos.order',
                method: 'search_read',
                args: [pos_domain, fields],
            }, {
                async: false
            }).then(function(output) {
                load_orders = output;
                self.pos.db.get_orders_by_id = {};
                load_orders.forEach(function(order) {
                    order_ids.push(order.id)
                    self.pos.db.get_orders_by_id[order.id] = order;
                });

                var fields_domain = [
                    ['order_id', 'in', order_ids],
                    ['is_cancel_charge_line', '=', false],
                    ['price_unit', '>', 0]
                ];
                rpc.query({
                    model: 'pos.order.line',
                    method: 'search_read',
                    args: [fields_domain],
                }, {
                    async: false
                }).then(function(output1) {
                    self.pos.db.reserved_orders_line_list = output1;
                    load_orders_line = output1;
                    self.pos.set({
                        'reserved_orders_list': load_orders
                    });
                    self.pos.set({
                        'reserved_orders_line_list': output1
                    });
                    self.render_list_orders(load_orders, undefined);
                });
            });
            return [load_orders, load_orders_line]
        },

        display_details: function(o_id) {
            var self = this;
            var orders = self.pos.get('reserved_orders_list');
            var orders_lines = self.pos.get('reserved_orders_line_list');
            var orders1 = [];
            for (var ord = 0; ord < orders.length; ord++) {
                if (orders[ord]['id'] == o_id) {
                    orders1 = orders[ord];
                }
            }
            var current_date = field_utils.format.datetime(moment(orders1.date_order), {
                type: 'datetime'
            });
            var orderline = [];
            for (var n = 0; n < orders_lines.length; n++) {
                if (orders_lines[n]['order_id'][0] == o_id) {
                    orderline.push(orders_lines[n])
                }
            }
            this.gui.show_popup('reserved_order_details_popup_widget', {
                'order': [orders1],
                'orderline': orderline,
                'current_date': current_date
            });
        },

        orderline_click_events: function() {
            var self = this;
            this.$('.orders-list-contents').delegate('.orders-line-name', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.orders-line-ref', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.orders-line-partner', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.orders-line-date', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.orders-line-tot', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.orders-line-state', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.orders-line-amount_due', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.orders-line-amount_paid', 'click', function(event) {
                var o_id = $(this).data('id');
                self.display_details(o_id);
            });

            this.$('.orders-list-contents').delegate('.cancel-order', 'click', function(event) {
                var orders = self.pos.get('reserved_orders_list');
                var orders_lines = self.pos.get('reserved_orders_line_list');
                var order_id = parseInt(this.id);
                var selectedOrder = null;
                for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                    if (orders[i] && orders[i].id == order_id) {
                        selectedOrder = orders[i];
                    }
                }
                var orderlines = [];
                var order_line_data = orders_lines;
                var myNewArray = selectedOrder.lines.filter(function(elem, index, self) {
                    return index === self.indexOf(elem);
                });
                selectedOrder.lines.forEach(function(line_id) {
                    for (var y = 0; y < order_line_data.length; y++) {
                        if (order_line_data[y]['id'] == line_id) {
                            orderlines.push(order_line_data[y]);
                        }
                    }
                });
                self.gui.show_popup('cancel_order_popup_widget', {
                    'orderlines': orderlines,
                    'order': selectedOrder
                });
            });

            this.$('.orders-list-contents').delegate('.change-date', 'click', function(event) {
                var orders = self.pos.get('reserved_orders_list');
                var order_id = parseInt(this.id);
                var selectedOrder = null;
                for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                    if (orders[i] && orders[i].id == order_id) {
                        selectedOrder = orders[i];
                    }
                }
                self.gui.show_popup('change_reserve_date_widget', {
                    'order': selectedOrder
                });
            });

            this.$('.orders-list-contents').delegate('.pay-order', 'click', function(event) {
                var orders = self.pos.get('reserved_orders_list');
                var orders_lines = self.pos.get('reserved_orders_line_list');
                var order_id = parseInt(this.id);
                var selectedOrder = null;
                for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                    if (orders[i] && orders[i].id == order_id) {
                        selectedOrder = orders[i];
                    }
                }
                var orderlines = [];
                var order_line_data = orders_lines;
                selectedOrder.lines.forEach(function(line_id) {
                    for (var y = 0; y < order_line_data.length; y++) {
                        if (order_line_data[y]['id'] == line_id) {
                            orderlines.push(order_line_data[y]);
                        }
                    }
                });
                self.gui.show_popup('pay_reserve_order_popup_widget', {
                    'orderlines': orderlines,
                    'order': selectedOrder,
                    'amount_due': selectedOrder['amount_due']
                });
            });
        },

        show: function(options) {
            var self = this;
            this._super(options);
            this.details_visible = false;
            var a = self.get_pos_orders();
            var orders = self.pos.get('reserved_orders_list');
            var orders_lines = self.pos.get('reserved_orders_line_list');
            $('.search-order input').val('');
            self.render_list_orders(orders, undefined);
            self.orderline_click_events(orders, orders_lines);

            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });
            var current_date = null;

            $('.refresh-order').on('click', function() {
                $('.search-order input').val('');
                var params = self.pos.get_order().get_screen_data('params');
                if (params && params['selected_partner_id']) {
                    params['selected_partner_id'] = undefined;
                }
                self.get_pos_orders();
            });

            //this code is for Search Orders
            this.$('.search-order input').keyup(function() {
                self.render_list_orders(orders, this.value);
            });

        },
    });
    gui.define_screen({
        name: 'see_reserve_orders_screen_widget',
        widget: SeeReservedOrdersScreenWidget
    });


    var ReservedOrderDetailsPopupWidget = popups.extend({
        template: 'ReservedOrderDetailsPopupWidget',

        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },


        show: function(options) {
            var self = this;
            options = options || {};
            this._super(options);
            this.order = options.order || [];
            this.orderline = options.orderline || [];
            this.current_date = options.current_date || [];
        },

        events: {
            'click .button.cancel': 'click_cancel',
        },

        renderElement: function() {
            var self = this;
            this._super();
        },
    });
    gui.define_popup({
        name: 'reserved_order_details_popup_widget',
        widget: ReservedOrderDetailsPopupWidget
    });
    var ReceiptScreenWidget = screens.ReceiptScreenWidget.extend({
        get_receipt_render_env: function() {
            var order = this.pos.get_order();
            var self = this;

            if (self.pos.reserved_order_print != undefined) {
                return {
                    widget: this,
                    pos: this.pos,
                    order: self.pos.print_reserve_order,
                    receipt: self.pos.print_reserve_receipt,
                    orderlines: self.pos.print_reserve_order_lines,
                    paymentlines: self.pos.print_paymentlines,

                };
            } else {
                return {
                    widget: this,
                    pos: this.pos,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                }
            }
        },
        render_receipt: function() {
            var self = this;
            this.$('.pos-receipt-container').html(QWeb.render('OrderReceipt', this.get_receipt_render_env()));
            var data = {};
            var order = self.pos.get_order();
            if (self.pos.reserved_order_print != undefined) {
                self.pos.reserved_order_print = undefined;
                data = {
                    widget: self,
                    order: self.pos.print_reserve_order,
                    receipt: self.pos.print_reserve_receipt,
                    bill_orderlines: self.pos.print_bill_orderlines,
                    orderlines: self.pos.print_reserve_order_lines,
                    paymentlines: self.pos.print_paymentlines,
                }
            } else {
                data = {
                    widget: self,
                    order: order,
                    receipt: order.export_for_printing(),
                    bill_orderlines: order.get_bill_orderlines(),
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                }
            }
            self.$('.pos-bill-categ-receipt-container').html(QWeb.render('PosTicket_Bill_Category', data));

        },

    });
    gui.define_screen({
        name: 'receipt',
        widget: ReceiptScreenWidget
    });

    var PayReserveOrderPopupWidget = popups.extend({
        template: 'PayReserveOrderPopupWidget',

        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        events: {
            'click .button.confirm-pay': 'pay_order',
            'click .button.cancel': 'close_popup_pay',
        },

        close_popup_pay: function() {
            this.gui.close_popup();
        },

        show: function(options) {
            options = options || {};
            var self = this;
            this._super(options);
            this.order = options.order || [];
            this.orderlines = options.orderlines || [];
            this.amount_due = options.amount_due || 0.0;
            $('.reamining-div').hide();
            $('#pay_amount').on('change', function() {
                if (parseFloat($(this).val()) > parseFloat(options.amount_due)) {
                    var remain = parseFloat($(this).val()) - parseFloat(options.amount_due)
                    $('.reamining-div').show();
                    $('.reamining-change').text(remain)
                } else {
                    $('.reamining-div').hide();
                }
            });

        },

        renderElement: function() {
            var self = this;
            this._super();
        },

        pay_order: function() {
            var self = this;
            var orderlines = self.options.orderlines;
            var order = self.options.order;
            var amount_due = self.options.amount_due || 0.0;
            var select_journal_id = $('.select_journal_id').val();
            var pay_amount = $('#pay_amount').val();
            var cash_jrnl_id = false;
            var session_id = self.pos.get_order().pos_session_id;
            if (pay_amount) {
                for (var i = 0; i < self.pos.payment_methods[0].length; i++) {
                    if (self.pos.payment_methods[i]['type'] == 'cash') {
                        cash_jrnl_id = self.pos.payment_methods['id']
                    }
                }
                rpc.query({
                    model: 'pos.order',
                    method: 'pay_reserved_amount',
                    args: [order.id, parseInt(select_journal_id), parseFloat(pay_amount), parseInt(cash_jrnl_id), parseInt(session_id)],

                }).then(function(output) {
                    //alert("You have Paid: "+pay_amount +"Amount");
                    function generate_wrapped_product_name(product) {
                        var MAX_LENGTH = 24; // 40 * line ratio of .6
                        var wrapped = [];
                        var name = product.display_name;
                        var current_line = "";

                        while (name.length > 0) {
                            var space_index = name.indexOf(" ");

                            if (space_index === -1) {
                                space_index = name.length;
                            }

                            if (current_line.length + space_index > MAX_LENGTH) {
                                if (current_line.length) {
                                    wrapped.push(current_line);
                                }
                                current_line = "";
                            }

                            current_line += name.slice(0, space_index + 1);
                            name = name.slice(space_index + 1);
                        }

                        if (current_line.length) {
                            wrapped.push(current_line);
                        }

                        return wrapped;
                    }
                    var order_lines = [];
                    var bill_categs = {};
                    _.each(orderlines, function(line) {
                        var product = self.pos.db.get_product_by_id(line.product_id[0]);
                        var decimals = self.pos.dp['Product Unit of Measure'];

                        function get_product() {
                            return product;
                        }

                        function get_quantity_str_with_unit() {
                            var unit = self.pos.units_by_id[product.uom_id[0]];
                            var quantityStr = field_utils.format.float(line.qty, {
                                digits: [69, decimals]
                            });
                            if (unit && !unit.is_pos_groupable) {
                                return quantityStr + ' ' + unit.name;
                            } else {
                                return quantityStr;
                            }
                        }

                        function get_display_price() {
                            if (self.pos.config.iface_tax_included === 'total') {
                                return line.price_subtotal_incl
                            } else {
                                return line.price_subtotal
                            }
                        }
                        var l = {
                            company: line.company_id[1],
                            quantity: line.qty,
                            name: line.name,
                            unit_name: line.product_uom_id[1],
                            price: line.qty * line.price_unit,
                            discount: line.discount || 0,
                            product_name: product.display_name,
                            product_name_wrapped: generate_wrapped_product_name(product),
                            price_lst: line.price_unit,
                            //display_discount_policy:    this.display_discount_policy(),
                            price_display_one: line.qty * line.price_unit,
                            price_display: line.qty * line.price_unit,
                            price_with_tax: line.price_subtotal_incl,
                            price_without_tax: line.price_subtotal,
                            price_with_tax_before_discount: line.qty * line.price_unit,
                            tax: 0,
                            product_description: false,
                            product_description_sale: false,
                            product_description: line.product_id[1], //      this.get_product().description,
                            product_description_sale: line.product_id[1], //this.get_product().description_sale,

                        };
                        var cat_line = {
                            get_product: get_product,
                            get_quantity_str_with_unit: get_quantity_str_with_unit,
                            get_display_price: get_display_price,
                        }
                        cat_line = Object.assign({}, cat_line, l)
                        order_lines.push(l);
                        if (product.bill_category != false) {
                            var existing_cat = _.filter(Object.keys(bill_categs), function(cat) {
                                return cat == product.bill_category[1];
                            });
                            if (existing_cat.length) {
                                bill_categs[product.bill_category[1]].push(cat_line);
                            } else {
                                bill_categs[product.bill_category[1]] = [cat_line];
                            }
                        }
                    })
                    var cashier = self.pos.get_cashier();
                    var company = self.pos.company;
                    var date = new Date();

                    function get_amount() {
                        return order.amount;
                    }

                    function get_amount_str() {
                        return field_utils.format.float(order.amount, {
                            digits: [69, self.pos.currency.decimals]
                        });
                    }

                    function get_curr_amount() {
                        return pay_amount;
                    }

                    function get_curr_amount_str() {
                        return field_utils.format.float(pay_amount, {
                            digits: [69, self.pos.currency.decimals]
                        });
                    }
                    function get_client(){
                        return self.pos.db.get_partner_by_id(order.partner_id[0])
                    }
                    var payment_method = _.filter(self.pos.payment_methods, function(pay_method) {

                        return pay_method.id == select_journal_id;
                    });
                    order.get_client = get_client;
                    order.amount_paid = order.amount_paid;
                    var payment_line = [{
                        payment_method: payment_method[0],
                        name: payment_method[0].name,
                        amount: order.amount_total,
                        get_amount: get_amount,
                        get_amount_str: get_amount_str
                    }];
                    var curr_payment_line = [{
                        payment_method: payment_method[0],
                        name: payment_method[0].name,
                        amount: pay_amount,
                        get_amount: get_curr_amount,
                        get_amount_str: get_curr_amount_str
                    }];
                    var final_bill_categs = [];
                    _.each(bill_categs, function(i, j) {
                        final_bill_categs.push({
                            name: j,
                            'orderlines': i
                        })
                    })

                    order.amount_due = amount_due - pay_amount
                    self.pos.reserved_order_print = true;
                    self.pos.print_reserve_order = order
                    self.pos.print_reserve_order_lines = orderlines;
                    self.pos.print_paymentlines = curr_payment_line;
                    if (order.amount_due > 0) {
                        self.pos.print_bill_orderlines = [];
                    } else {
                        self.pos.print_bill_orderlines = final_bill_categs;
                    }

                    self.pos.print_reserve_receipt = {
                        orderlines: order_lines,
                        paymentlines: payment_line,
                        subtotal: order.amount_total,
                        total_with_tax: order.amount_total, //(order.amount_total - order.total_tax) + order.total_tax,
                        total_rounded: order.amount_total,
                        total_without_tax: order.amount_total,
                        total_paid: order.amount_total - pay_amount,
                        total_tax: order.amount_tax,
                        total_discount: 0,
                        amount_paid: order.amount_paid,
                        change: 0,
                        tax_details: [],
                        name: order.pos_reference,
                        client: order.partner_id[1],
                        invoice_id: null,
                        cashier: cashier ? cashier.name : null,
                        precision: {
                            price: 2,
                            money: 2,
                            quantity: 3,
                        },
                        date: {
                            year: date.getFullYear(),
                            month: date.getMonth(),
                            date: date.getDate(), // day of the month
                            day: date.getDay(), // day of the week
                            hour: date.getHours(),
                            minute: date.getMinutes(),
                            isostring: date.toISOString(),
                            localestring: date.toLocaleString(),
                        },
                        company: {
                            email: company.email,
                            website: company.website,
                            company_registry: company.company_registry,
                            contact_address: company.partner_id[1],
                            vat: company.vat,
                            vat_label: company.country && company.country.vat_label || '',
                            name: company.name,
                            phone: company.phone,
                            logo: self.pos.company_logo_base64,
                        },
                        currency: self.pos.currency,
                    };
                    self.gui.show_screen('receipt');
                });
            } else {
                alert("Please Enter Amount To Done Order")
            }

        },

    });

    gui.define_popup({
        name: 'pay_reserve_order_popup_widget',
        widget: PayReserveOrderPopupWidget
    });

    var CancelOrderPopupWidget = popups.extend({
        template: 'CancelOrderPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        //
        show: function(options) {
            options = options || {};
            var self = this;
            this._super(options);
            this.orderlines = options.orderlines || [];
        },
        //
        renderElement: function() {
            var self = this;
            this._super();
            var selectedOrder = this.pos.get_order();
            var orderlines = self.options.orderlines;
            var order = self.options.order;
            var removedline = [];


            $('#delete_whole').click(function() {
                if ($('#delete_whole').is(':checked')) {
                    $('.div-container').hide();
                } else {
                    $('.div-container').show();
                }
            });

            $('.entered_item_qty').change(function(ev) {
                var entered_item_qty = $('#entered_item_qty');
                var line_id = parseFloat(entered_item_qty.attr('line-id'));
                var qty_id = parseFloat(entered_item_qty.attr('qty-id'));
                var entered_qty = parseFloat(entered_item_qty.val());
                if (qty_id < entered_qty) {
                    alert("You can not increase ordered quantity")
                    entered_item_qty.val(qty_id);
                }

            });

            $('.remove-line').click(function() {

                for (var i = 0; i < orderlines.length; i++) {
                    if (orderlines[i]) {
                        if (orderlines[i]['id'] == $(this).attr('line-id')) {
                            removedline.push($(this).attr('line-id'))
                            orderlines.splice(i, 1);
                        }
                    }
                }
                $(this).closest('tr').remove();
                if (orderlines.length === 0) {
                    $('#delete_whole').prop('checked', true);
                    $('.div-container').hide();
                }

            });

            this.$('#apply_order').click(function() {
                self.cancel_order_or_product(order, orderlines, removedline)
            });
        },

        cancel_order_or_product: function(order, orderlines, removedline) {
            var self = this;
            var entered_code = $("#entered_item_qty").val();
            var list_of_qty = $('.entered_item_qty');
            var cancelorder_products = {};
            var orders_lines = self.pos.get('reserved_orders_line_list');
            var cancel_charges_product = this.pos.config.cancel_charges_product;
            var cancel_charge_type = this.pos.config.cancel_charge_type;
            var cancel_charges = this.pos.config.cancel_charges;
            var orders = self.pos.get('reserved_orders_list');
            var selectedOrder = this.pos.get_order();
            var cancellation_charge;
            var temp_charge;
            var partner_id = false;
            var client = false;
            var is_del_all = false;
            if (order && order.partner_id != null)
                partner_id = order.partner_id[0];
            client = this.pos.db.get_partner_by_id(partner_id);

            if ($('#delete_whole').is(':checked')) {
                for (var i = 0; i < orders_lines.length; i++) {
                    for (var j = 0; j < orderlines.length; j++) {
                        if (orders_lines[i]['order_id'][1] == orderlines[j]['order_id'][1]) {
                            orders_lines.splice(i, 1);
                        }
                    }
                }
                is_del_all = true;

            } else {
                $.each(list_of_qty, function(index, value) {
                    var entered_item_qty = $(value).find('input');
                    var line_id = parseFloat(entered_item_qty.attr('line-id'));
                    var qty_id = parseFloat(entered_item_qty.attr('qty-id'));
                    var entered_qty = parseFloat(entered_item_qty.val());
                    cancelorder_products[line_id] = entered_qty;
                });
            }
            for (var i = 0; i < orders_lines.length; i++) {
                for (var j = 0; j < orderlines.length; j++) {
                    if (orders_lines[i]['order_id'][1] == orderlines[j]['order_id'][1]) {
                        if (orders_lines[i]['id'] != orderlines[j]['id']) {
                            orders_lines.splice(i, 1);
                        }
                    }
                }
            }
            rpc.query({
                model: 'pos.order',
                method: 'change_or_remove_product',
                args: [order.id, cancelorder_products, removedline, self.pos.config.id, is_del_all],
            })
            this.gui.show_screen('see_reserve_orders_screen_widget', {});


        },

    });

    gui.define_popup({
        name: 'cancel_order_popup_widget',
        widget: CancelOrderPopupWidget
    });

    var ChangeReserveDateWidget = popups.extend({
        template: 'ChangeReserveDateWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },

        renderElement: function() {
            var self = this;
            this._super();
            var order = self.options.order;
            this.$('#change_date').click(function() {
                self.change_reserve_order_date();
            });
        },

        get_today_date: function() {
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth() + 1; //January is 0!
            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd;
            }
            if (mm < 10) {
                mm = '0' + mm;
            }
            var date = yyyy + "-" + mm + "-" + dd;
            return date
        },


        change_reserve_order_date: function() {
            var self = this;
            var order = self.options.order;
            var changed_date = $("#changed_date").val();
            var orders = self.pos.get('reserved_orders_list');
            var orders_lines = self.pos.get('reserved_orders_line_list');
            if (!changed_date) {
                alert('Please Select Delivery Date');
            } else {
                var today_date = self.get_today_date();
                var d1 = Date.parse(today_date);
                var d2 = Date.parse(changed_date);
                if (d1 > d2) {
                    alert("Please Select Valid Date");
                } else {
                    return rpc.query({
                        model: 'pos.order',
                        method: 'change_reserve_date',
                        args: [order.id, changed_date],
                    })
                }

            }
        },

    });
    gui.define_popup({
        name: 'change_reserve_date_widget',
        widget: ChangeReserveDateWidget
    });

    // Start ClientListScreenWidget
    gui.Gui.prototype.screen_classes.filter(function(el) {
        return el.name == 'clientlist'
    })[0].widget.include({
        show: function() {
            this._super();
            var self = this;
            this.$('.view-orders').click(function() {
                self.gui.show_screen('see_reserve_orders_screen_widget', {});
            });
            $('.selected-client-orders').on("click", function() {
                self.gui.show_screen('see_reserve_orders_screen_widget', {
                    'selected_partner_id': this.id
                });
            });
        },
    });


    var ReservedLinesButtonWidget = screens.ActionButtonWidget.extend({
        template: 'ReservedLinesButtonWidget',
        button_click: function() {
            var self = this;
            this.gui.show_screen('reserve_lines_screen_widget', {});
        },

    });

    screens.define_action_button({
        'name': 'See Reserved Orders Button Widget',
        'widget': ReservedLinesButtonWidget,
        'condition': function() {
            return true;
        },
    });

    var ReservedLinesScreenWidget = screens.ScreenWidget.extend({
        template: 'ReservedLinesScreenWidget',
        init: function(parent, options) {
            this._super(parent, options);
        },
        render_list_orders: function(orders, search_input) {
            var self = this;
            if (orders == undefined) {
                orders = self.pos.get('reserved_line_list');
            }
            if (search_input != undefined && search_input != '') {
                var selected_search_orders = [];
                var search_text = search_input.toLowerCase()
                for (var i = 0; i < orders.length; i++) {
                    if (((orders[i].product.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].order_id.toLowerCase()).indexOf(search_text) != -1)) {
                        selected_search_orders = selected_search_orders.concat(orders[i]);
                    }
                }
                orders = selected_search_orders;
            }
            var content = this.$el[0].querySelector('.lines-list-contents');
            content.innerHTML = "";
            var orders = orders;
            var current_date = null;
            if (orders != undefined) {
                for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                    var order = orders[i];
                    current_date = field_utils.format.datetime(moment(order.date_order), {
                        type: 'datetime'
                    });
                    var ordersline_html = QWeb.render('ReservedOrdersLine', {
                        widget: this,
                        line: orders[i]
                    });
                    var ordersline = document.createElement('tbody');
                    ordersline.innerHTML = ordersline_html;
                    ordersline = ordersline.childNodes[1];
                    content.appendChild(ordersline);
                }
            }

        },
        get_reserved_lines: function() {
            var self = this;
            rpc.query({
                model: 'pos.order',
                method: 'get_reserved_lines',
                args: [1],
            }, {
                async: false
            }).then(function(output1) {
                self.pos.set({
                    'reserved_line_list': output1
                });
                self.render_list_orders(output1, undefined);
            });
        },
        show: function(options) {
            var self = this;
            this._super(options);
            this.details_visible = false;
            $('.search-order input').val('');
            self.get_reserved_lines();
            var orders_lines = self.pos.get('reserved_line_list');
            this.$('.back').click(function() {
                self.gui.show_screen('products');
            });
            $('.refresh-line').on('click', function() {
                $('.search-order input').val('');
                self.get_reserved_lines();
            });
            this.$('.search-order input').keyup(function() {
                self.render_list_orders(orders_lines, this.value);
            });
        },
    });
    gui.define_screen({
        name: 'reserve_lines_screen_widget',
        widget: ReservedLinesScreenWidget
    });
});
