from .auth import generate_code, send_code, register, login
from .profile import profile, schools, submit_auth, achievements
from .checkin import daily_topics, checkin, checkin_stats, _normalize_duration, usage_stats, _generate_advice
from .messages import messages_view, reply_message, like_message, notifications_view, create_notification
from .quiz import quiz_questions, quiz_submit, quiz_history, admin_auth_review
