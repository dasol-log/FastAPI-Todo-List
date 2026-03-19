from datetime import datetime
import os
import time


# [추가] 로그 파일 저장 함수
# - BackgroundTasks에서 실행할 함수
# - 응답을 먼저 보낸 뒤, 이 함수가 뒤에서 실행됩니다.

def write_todo_log(action: str, username: str, todo_title: str):
    os.makedirs("logs", exist_ok=True)

    log_line = (
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"user={username} | action={action} | title={todo_title}\n"
    )

    with open("logs/todo_log.txt", "a", encoding="utf-8") as f:
        f.write(log_line)


# [추가] 시간이 조금 걸리는 작업을 흉내내는 함수
# - 예: 이메일 발송, 외부 알림 전송, 통계 업데이트
# - 실제 서비스에서는 이런 작업을 Celery/Redis로 넘기기도 합니다.

def fake_send_notification(username: str, message: str):
    time.sleep(3)  # 일부러 3초 대기
    os.makedirs("logs", exist_ok=True)

    with open("logs/notification_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{username}님에게 알림 전송 완료: {message}\n")