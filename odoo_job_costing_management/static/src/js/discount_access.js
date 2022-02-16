odoo.define('odoo_job_costing_management.discount_access', function (require) {
    "use strict";

    var dis_btn = require('project.project_kanban');


    dis_btn.KanbanRecord.include({

         _openRecord: function () {
                console.log("Invalid Delta:")
                this._super.apply(this, arguments);
            }
        },


    });











    

});