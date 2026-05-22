from flask import Blueprint, jsonify, g, send_file
from services.reports_service import ReportsService
from middleware.auth_middleware import token_required

report_bp = Blueprint('reports', __name__)


@report_bp.route('/api/reports/export/excel', methods=['GET'])
@token_required
def export_excel():
    output, error = ReportsService.export_excel(g.current_user_id, g.current_role_name)
    if error:
        return jsonify({'message': error, 'success': False}), 500
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='TaskFlow_Report.xlsx'
    )


@report_bp.route('/api/reports/export/pdf', methods=['GET'])
@token_required
def export_pdf():
    output, error = ReportsService.export_pdf(g.current_user_id, g.current_role_name)
    if error:
        return jsonify({'message': error, 'success': False}), 500
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='TaskFlow_Report.pdf'
    )
