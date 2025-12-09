from modules.database import db
from datetime import datetime


class NewsLinkHistory(db.Model):
    """Model historii kliknięć linków wiadomości (tabela oddzielna dla wiadomości)
    Tabela w tej samej bazie SQLite co reszta aplikacji.
    """
    __tablename__ = 'news_link_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    link_url = db.Column(db.String(500), nullable=False)
    link_title = db.Column(db.String(300), nullable=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<NewsLinkHistory {self.user_id} {self.link_url}>'

    @staticmethod
    def log_click(user_id, link_url, link_title=None, source=None):
        entry = NewsLinkHistory(
            user_id=user_id,
            link_url=(link_url or '')[:500],
            link_title=(link_title or '')[:300] if link_title else None,
            source=(source or '')[:50] if source else None
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def get_user_history(user_id, limit=200):
        return NewsLinkHistory.query.filter_by(user_id=user_id).order_by(NewsLinkHistory.clicked_at.desc()).limit(limit).all()

    @staticmethod
    def get_stats_by_source(user_id):
        from sqlalchemy import func
        rows = db.session.query(NewsLinkHistory.source, func.count(NewsLinkHistory.id).label('count')).filter_by(user_id=user_id).group_by(NewsLinkHistory.source).all()
        return [{'source': r[0] or 'unknown', 'count': r[1]} for r in rows]

    @staticmethod
    def clear_user_history(user_id):
        NewsLinkHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    @staticmethod
    def delete_entry(entry_id, user_id):
        entry = NewsLinkHistory.query.filter_by(id=entry_id, user_id=user_id).first()
        if not entry:
            return False
        db.session.delete(entry)
        db.session.commit()
        return True
