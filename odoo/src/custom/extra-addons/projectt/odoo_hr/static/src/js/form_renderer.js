odoo.define('odoo_hr.form_renderer', function (require) {
  'use strict';
  const FormRenderer = require('web.FormRenderer');
  FormRenderer.include({
    init(parent, state, params) {
      this._super(...arguments);
    },

    _render: function () {
      if (this.state.model === 'hr.employee' || this.state.model === 'hr.contract' ) {
        if (this.state.data.locked) {
          this.mode = 'readonly';
        }
      }
      return this._super.apply(this, arguments);
    },
  });
});
