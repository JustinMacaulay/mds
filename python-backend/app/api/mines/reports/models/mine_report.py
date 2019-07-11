from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import FetchedValue
from sqlalchemy.ext.associationproxy import association_proxy
from app.api.mines.reports.models.mine_report_submission import MineReportSubmission
from app.api.utils.models_mixins import Base, AuditMixin
from app.extensions import db


class MineReport(AuditMixin, Base):
    __tablename__ = "mine_report"
    mine_report_id = db.Column(db.Integer, primary_key=True, server_default=FetchedValue())
    mine_report_guid = db.Column(UUID(as_uuid=True))
    mine_report_definition_id = db.Column(
        db.Integer, db.ForeignKey('mine_report_definition.mine_report_definition_id'))
    mine_guid = db.Column(UUID(as_uuid=True), db.ForeignKey('mine.mine_guid'))
    permit_id = db.Column(db.Integer, db.ForeignKey('permit.permit_id'))
    received_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime, nullable=False)
    submission_year = db.Column(db.Integer)
    deleted_ind = db.Column(db.Boolean, server_default=FetchedValue(), nullable=False)

    def __repr__(self):
        return '<MineReport %r>' % self.mine_report_guid
