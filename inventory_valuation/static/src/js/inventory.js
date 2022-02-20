console.log('test_moduleeeeeeeeeeeeeeeeeeeeee javascript');
odoo.define('inventory_valuation.stock.tree', function (require) {
"use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var QWeb = core.qweb;

    var InventoryController = ListController.extend({
        /**
         * Extends the renderButtons function of ListView by adding a button
         * on the payslip list.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments);
            this.$buttons.append($(QWeb.render("Inventory.print_button", this)));
            var self = this;
            this.$buttons.on('click', '.o_button_print_stock', function () {
                if (self.getSelectedIds().length == 0) {
                    return;
                }
                return self._rpc({
                    model: 'stock.valuation.layer',
                    method: 'action_print_valuation',
                    args: [self.getSelectedIds()],
                }).then(function (results) {
                    self.do_action(results);
                });
            });
        }
    });

    var Inventory = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: InventoryController,
        }),
    });

    viewRegistry.add('inventory_report_list', Inventory);
    return Inventory
});
